# DECISIONS.md — the project's memory of *why*

This is an **append-only** log. Add new entries at the bottom. Never delete
or rewrite old entries. Each entry is dated.

It records choices made, why they were made, open questions, and findings.

---

[D1–D12, the founding decisions from initial project planning — project scope, location, data sources, split dates, model type — archived verbatim to DECISIONS-archive.md. Settled and now codified as active SPEC rules (D1→§1, D3→§3.1, D4→§2.1b, D5/D8→§3.2, D7→§4.3/D13, D9→§4.1, D10→§5, D11→§2.2, D12→§4.4). Full text preserved there and in git.]

---

## 2026-08-16 — Parked items (revisit from inside the work, do not act yet)

**P1. Overall project direction (deeper / wider / sideways).** No specific
pull yet. Decide after a couple of locations are working, from inside the
work rather than up front.

**P2. The WeatherNext angle.** Google DeepMind open-sourced WeatherNext 2 (an
AI-native weather model) in 2026. It fits our plan at stage 4 in three ways:
(a) swap it in as the base forecast and correct it the same way we correct
GFS — the open, likely-unpublished question is whether a fresh AI model
carries a learnable local bias like GFS does; (b) blend it with GFS — it is a
promising blend partner because it is built on completely different
principles, so its mistakes may not overlap with GFS's; (c) later, correct
its ensemble spread (a "go deeper" move). All parked until stage 1 passes.
Two things to verify before betting on it: whether its *past* forecasts can be
pulled in bulk (the method needs history), and whether anyone has already
done this local evaluation (probably not, but check before claiming novelty).

**P3. Harder evaluation bars.** Beating operational post-processed forecasts
(a much higher bar than raw GFS), and demanding statistical significance /
multi-season robustness. Known as the honest "ceiling" but the wrong weight
for stage 1. Revisit once stage 1 passes.

---

## 2026-08-16 — Open questions (verify on contact)

**Q1. Does the Previous Runs API actually return history back to 2021 on the
first real pull** (not just recent months)? Current docs say yes; confirm on
contact.

**Q2. Is EGLC's observation record complete enough** over the chosen period?
Confirm on the first pull; apply the drop-count-report rule (D11) to whatever
gaps appear.

---

[F1–F4, session 01's EGLC-only verify-on-contact findings (the archive's apparent start date, later corrected by F11; EGLC's observation record; EGLC's twice-hourly reporting; the forecast variable used) archived verbatim to DECISIONS-archive.md. Settled, and superseded as ongoing precedent by the project-wide findings that followed (F8, F9, D14). Full text preserved there and in git.]

---

## 2026-08-16 — Open questions raised by session 01 (not acted on)

These came up during session 01 and are outside its scope. Logged for the
owner, per CLAUDE.md.

**Q3. How should an observation timed at :50 be lined up with a forecast
valid on the hour?** The forecast series is stamped on the hour (12:00). The
observation is stamped at :50 (11:50 or 12:50). They are 10 minutes apart
either way, so something has to be chosen and written down before the join.
The obvious candidates are "use the :50 report from the same hour" or "use
the nearest report". This needs deciding before any pairing happens.

**Q4. What exactly does "previous_day1" mean in lead-time hours?** It is the
run from one day earlier, but whether every hour of the day is a clean
24 hours ahead, or whether the lead time drifts across the day depending on
which run cycle is used, was not verified in this session. It matters because
SPEC 3.2 and D8 fix stage 1 at a 24-hour lead time. Worth confirming against
Open-Meteo's documentation before training.

**Q5. The model grid point is about 4 km from the airport.** EGLC is at lat
51.505, lon 0.055. The API returned the nearest GFS cell at lat 51.487137,
lon 0.0, elevation 4 m — about 4.3 km away. The station's own record puts it
at lat 51.5053, lon 0.0553, elevation 5 m. The elevations nearly match, so
there is no height mismatch to worry about, and a fixed distance offset is
exactly the kind of steady local error this project is built to learn. Noted
so it is a known fact rather than a surprise later.

**Q6. Should raw data files go into version control?** The repo has no
`.gitignore`. The session 01 pulls are small (126 KB in total), so
committing them is easy and makes the snapshot rule (SPEC 2.3) very concrete.
A full multi-year pull will be much bigger. The owner decides at commit time;
nothing was committed or ignored this session. There is also an untracked
`.DS_Store` file that macOS created.

---

## 2026-08-16 — Session 02 decisions (owner's choices, now locked)

**D13. The train/test split is now a fixed pair of dates.**
- **Training period: 2021-03-24 to 2025-07-31** (inclusive).
- **Test period: 2025-08-01 to 2026-07-31** (inclusive) — held out and
  untouched until the final evaluation. That is a clean 12 months, so the
  result is judged across all four seasons.
- Data after 2025-07-31 that falls outside the test period — that is, anything
  from 2026-08-01 to today — is simply not used. This keeps the test set
  exactly one calendar year.
- Reason it is fixed now: the evaluation bar must be frozen before any model
  runs (SPEC 2.4), and the split date is part of that bar. Fixing it now means
  it cannot be chosen later to flatter the result.

**D14. Observation-to-forecast pairing rule (answers Q3).**
- The routine `:50` report is the hourly truth observation (per F3).
- Each forecast valid at `HH:00` is paired with the observation nearest that
  hour — in practice the `:50` report ten minutes before it.
- If no report exists within 15 minutes of the hour, that hour is dropped and
  counted (SPEC 2.2). Nothing is filled in.
- Reason: ten minutes is a negligible gap for temperature, so this adds no
  meaningful error, and a single written rule stops the pairing being decided
  ad hoc later.

**D15. Raw data is committed to version control (answers Q6).**
- Raw pulls are small for one station and one variable, so they go into the
  repository. That makes the immutable-snapshot rule (SPEC 2.3) concrete and
  the project reproducible from the history alone.
- If the data volume ever grows a lot — many stations, many variables — this
  is revisited.
- A `.gitignore` was added for operating-system and Python clutter. It
  deliberately does **not** ignore `data/raw/`.

---

## 2026-08-16 — Session 02 findings (documentation checks)

Both checks below were done against Open-Meteo's own documentation. F6 also
used a small throwaway request to the live API to test which model names are
accepted; nothing from it was saved to `data/raw/`, and the exact query is
written out below so it can be repeated.

**F5. Q4 answered — `previous_day1` is a *nominal* 24-hour lead, not an exact
one. The real lead runs from about 24 hours up to about 30 hours, and it
cycles through the day.** This matters, so here is the evidence in order.

The Previous Runs API documentation page states the simple version:

> "`_previous_day0` is the current model run (equivalent to the live Forecast
> API). `_previous_day1` is the value that was predicted 24 hours before valid
> time, `_previous_day2` 48 hours before, and so on up to day 7."

and

> "Data from past model runs is aligned to fixed lead-time offsets of 1–7
> days."

But Open-Meteo's own article on the feature explains how the series is
actually built, and it is not one run from 24 hours ago:

> "For **Previous Day 1**, with a forecast lead-time offset of 24 hours, it
> doesn't entail retrieving a single weather model run from 24 hours ago.
> Instead, the initial 24 hours of each weather model run are disregarded. In
> models updating every 3 hours, time steps 24, 25, and 26 are utilized to
> form a continuous time-series."

So each run contributes only the hours it is needed for, starting at its own
hour 24. GFS updates every 6 hours (00Z, 06Z, 12Z, 18Z), so by the same rule
each GFS run contributes its time steps 24 to 29 — meaning the effective lead
time sweeps from 24 hours up to 29 hours and then resets, six hours at a time,
right through the day. Open-Meteo's documentation gives this worked example
for a 3-hourly model only; the 6-hourly case is the same rule applied to GFS,
not a separately published number.

The maintainer confirms the same picture on the project's discussion board,
and adds the processing delay:

> "a 24 hour lead-time is in reality 24 hours + 5:20 for processing"

and describes the stitching directly — for a model of that update cadence,
"hours 0-6 from the 00Z run, hours 6-12 from the 06Z run, and so forth".

**Does this match SPEC's "24-hour lead" framing (SPEC 3.2, D8)?** Mostly, but
not exactly. It matches in the way that matters: every value is a genuine
forecast made at least 24 hours before the hour it describes, so there is no
look-ahead leakage (SPEC 2.1b holds). It does not match the literal reading
that every hour is a clean 24 hours ahead. The honest description is "a
day-ahead forecast at a 24-to-30-hour lead", and this is exactly the dataset
Open-Meteo recommends for training bias-correction models. Whether to reword
SPEC is left to the owner — see Q7.

[F6, the EGLC-only `gfs_seamless`-versus-`gfs_global` equivalence check, archived verbatim to DECISIONS-archive.md. Settled; D16 (pinning `gfs_global`) is the active rule it supports, and the same check was later repeated per airport (F40 at DSM, F52 at Dubbo — see those live entries for the current picture). Full text preserved there and in git.]

**Q5 closed — accepted.** The roughly 4 km gap between the airport and the GFS
grid point (returned again as lat 51.487137, lon 0.0, elevation 4 m in every
successful probe above) is accepted as-is. A steady distance offset is exactly
the kind of repeated local error this project exists to learn, and the
elevations nearly match, so there is no height problem. No action needed.

---

## 2026-08-16 — Open questions raised by session 02 (not acted on)

**Q7. Should SPEC's "24-hour lead" wording be made more precise?** F5 shows
the real lead is 24 to about 30 hours, sweeping through the day. SPEC 3.2 says
"a fixed lead-time offset of 1 day (24 hours ahead)" and D8 says "24 hours
only". Neither is wrong in spirit and neither creates leakage, but a reader
could take them literally. Session 02's authorised SPEC edits did not cover
this, so nothing was changed. The owner decides whether to reword SPEC 3.2,
and whether the varying lead should later become a feature the model can see.

**Q8. Which model string does session 3 pull with — `gfs_global` or
`gfs_seamless`?** F6 recommends `gfs_global` and shows the two are identical
at EGLC today. This needs the owner's word before the full historical pull,
because it is baked into every raw file after that.

**Q9. `.DS_Store` is already tracked, so the new `.gitignore` rule cannot
take effect on it.** Q6 recorded `.DS_Store` as untracked, but it went into
the session 01 commit. The `.gitignore` added this session does match it
(`git check-ignore --no-index` confirms the rule fires), but git ignores
ignore-rules for files it is already tracking, so the file stays in the
history until someone runs `git rm --cached .DS_Store`. That is a version-
control action, which Claude Code never takes (CLAUDE.md), and it is outside
this session's scope. Left for the owner.

---

## 2026-08-16 — Session 03b decisions (owner's choices, now locked)

Session 03 was started and stopped partway. Session 03b re-did the pull on a
corrected basis. The note at the end of this section records what was thrown
away, so the history is honest.

**D16. The forecast model string is pinned to `gfs_global` (answers Q8).**
- Every forecast pull uses the explicit string `gfs_global`, not
  `gfs_seamless`.
- Reason: session 02 (F6) showed the two return identical data at EGLC over
  both a 2026 and a 2021 window, so pinning costs nothing. It makes the claim
  "this is exactly NCEP GFS" true by construction rather than by argument, and
  it stops a future change to Open-Meteo's seamless blending from quietly
  changing the dataset underneath us.
- **Q8 is closed.**

**D17. Stage 1 is temperature-only on the forecast side.**
- The only forecast variable pulled is `temperature_2m` at the
  `previous_day1` offset.
- The four extra candidates tried in the aborted session 03 — cloud cover,
  10 m wind speed, 2 m dew point and surface pressure — are dropped for
  stage 1.
- Reason: they exist only for recent data, not across the archive (F7), and
  they begin exactly where the big forecast gap ends (F8), so including them
  would mean a dataset whose columns start at different dates. Temperature
  covers the whole archive. Stage 1 is meant to be the simplest clean test.
- Kept as a **possible later enhancement, recent period only**. If the extras
  are ever used, the training period for a model using them has to start after
  they begin, and that is a different, shorter dataset.

---

## 2026-08-16 — Session 03b findings (the full historical pull)

The full pull ran for real: 2021-03-24 to 2026-07-31, both sources, six
yearly chunks each, 24 files in `data/raw/` with a `.meta.txt` beside every
one. Nothing was joined, filled, cleaned or modelled.

**F7. The extra forecast variables exist only for recent data.** A small
probe (three days, `gfs_global`, EGLC) was run at each end of the archive
before the pull. Every candidate returns real values recently; only
temperature reaches back to the start:

| variable at `_previous_day1` | 2026-08-10..12 | 2021-03-24..26 |
|------------------------------|----------------|----------------|
| `temperature_2m`             | 72/72 present  | 72/72 present  |
| `cloud_cover`                | 72/72 present  | 0/72 — all null |
| `wind_speed_10m`             | 72/72 present  | 0/72 — all null |
| `dew_point_2m`               | 72/72 present  | 0/72 — all null |
| `surface_pressure`           | 72/72 present  | 0/72 — all null |
| `relative_humidity_2m`       | 72/72 present  | 0/72 — all null |
| `pressure_msl`               | 72/72 present  | 0/72 — all null |

None was rejected; the early ones come back HTTP 200 with null values, the
same pattern F1 found for temperature before 24 March 2021. A coarse scan of
single days showed the extras still absent on 2023-07-01 and present on
2024-07-01. This finding is what D17 rests on.

**F8. There is exactly one sizeable gap in the forecast series, and it
straddles the 2023/2024 year end.** Pinned down exactly:

```
last hour with data       : 2023-12-29 23:00 UTC
first missing hour        : 2023-12-30 00:00 UTC
last missing hour         : 2024-01-19 11:00 UTC
first hour with data again: 2024-01-19 12:00 UTC
length                    : 492 hours (20.5 days)
split across the year end : 48 hours in 2023, 444 hours in 2024
```

The aborted session 03 reported "about 444 null hours in early 2024". That was
the same gap seen from inside the 2024 file only; counting from 30 December
2023 gives the true 492.

It is genuinely one continuous gap, not an artefact of how the requests were
chunked: the 2023 file and the 2024 file were requested separately, and each
holds its own side of it (2023 file: 48 nulls, 2023-12-30 00:00 to 2023-12-31
23:00; 2024 file: 444 nulls, 2024-01-01 00:00 to 2024-01-19 11:00). They join
end to end.

**It is the only gap in the forecast series.** Over the whole period there is
exactly **one** gap run. Every hour was returned as a row — no hour is
missing outright — so all 492 missing hours are rows the API returned with a
null value. Nothing was filled (SPEC 2.2).

Forecast totals for the period:
```
expected hours in period : 46,944
hours with a usable value: 46,452
hours missing            : 492 (1.05% of the period)
  of which no row at all : 0
  of which row but null  : 492
training 2021-03-24..2025-07-31: 38,184 expected, 37,692 usable, 492 missing (1.29%)
test     2025-08-01..2026-07-31:  8,760 expected,  8,760 usable,   0 missing (0.00%)
```
The whole gap falls inside the training window. The test window has no
forecast gap at all.

**F9. The observation record over the full period is very good.** 44 missing
hours out of 46,944 (**0.09%**), spread over 23 short runs. The longest is
8 hours. There is no run of 24 hours or more.

```
reports in files           : 46,919
minute-past-hour spread    : :20 x8, :50 x46,911
reports with no temperature: 10
reports >15 min from any hour, dropped (D14): 8
hours with an observation  : 46,900
training 2021-03-24..2025-07-31: 38,184 expected, 38,146 usable, 38 missing (0.10%)
test     2025-08-01..2026-07-31:  8,760 expected,  8,754 usable,  6 missing (0.07%)
```

Gap runs by length: 16 runs of 1 hour, 5 runs of 2–5 hours, 2 runs of 6–23
hours. The full list of all 23 runs is in
`notes/session-03b-check-output.txt`.

Two small things the pull turned up, both handled by the existing rules:
- Eight reports came in at `:20` rather than `:50`. They sit 20 minutes from
  the nearest hour, so the D14 15-minute rule drops them. That is the whole of
  the "8 dropped" line above.
- Ten reports carry no temperature (marked `M`). They were counted, not
  filled.

This confirms F2's two-week snapshot holds across the whole five years: gaps
are rare and short, so dropping unpaired rows will cost very little data.

**F10. Value-range sanity check, training window only.** The test window was
not looked at (its values stay sealed until the final evaluation).

```
forecast (GFS, training window): n = 37,692   min = -1.7   max = 40.7   mean = 12.67 degC
observed (EGLC, training window): n = 38,146   min = -5.0   max = 39.0   mean = 12.93 degC
```

Both are plainly Celsius — a Kelvin mix-up would read about 250–310 — and
neither carries an absurd value. Nothing here is wrong.

Worth noticing for later, though: the forecast's range is shifted warm at the
cold end (its coldest hour is -1.7 against the station's -5.0) and slightly
warm at the hot end. That is the shape you would expect from a coarse global
grid cell sitting about 4 km away and partly over the Thames (Q5), which
smooths extremes. It is not a fault in the data — it is exactly the kind of
repeatable local bias this project exists to learn. Recorded as an
observation, not acted on. See Q10.

**Note — what the aborted session 03 left behind, and what happened to it.**
Session 03 pulled four forecast chunks (2021–2024) carrying five variables
before it was stopped. Those files were never committed. They were moved out
of `data/raw/` before this session's pull so the dataset would be clean and
uniform, and every forecast chunk was re-pulled temperature-only. Nothing
committed was touched. The `data/raw/` folder now holds the six committed
session 01 sample files plus the 24 new session 03b files (3.7 MB in total).

**Q7 closed.** The owner approved rewording SPEC 3.2, and the edit was made in
the aborted session 03 and confirmed intact at the start of this one. SPEC 3.2
now states the `gfs_global` pin, the nominal-versus-real lead time (24 to about
30 hours, sweeping through the day), and that every value is still a genuine
forecast made at least 24 hours ahead, so 2.1b holds.

**Q8 closed** by D16. **Q9 closed** — `git ls-files` returns nothing for
`.DS_Store`, and `.gitignore` line 8 matches it, so the owner's
`git rm --cached` took effect.

---

## 2026-08-16 — Open questions raised by session 03b (not acted on)

**Q10. Does the 492-hour forecast gap need anything done about it?** It is
1.29% of the training window and falls entirely inside it, in winter
(30 December to 19 January). Dropping those hours is what SPEC 2.2 requires
and is the default. The only thing worth the owner's thought is that the loss
is concentrated in one winter rather than spread out, so the training set
holds slightly less deep-winter data than the raw row count suggests. No
action taken.

**Q11. Should the warm shift in the forecast's value range be looked at
before modelling?** F10 notes the forecast never gets as cold as the station
does. This is expected and is the bias the project targets, so it needs no
fix — but if the owner wants a sanity plot of forecast-minus-observation
before the model is built, that is a training-window-only exercise and would
have to be asked for explicitly. Not done here.

---

## 2026-08-17 — Session 04 decisions (owner's choices, now locked)

**D18. The validation approach — rehearse the evaluation inside the training
period, so the sealed test year is looked at only once.**
- **Inner-training: 2021-03-24 to 2024-07-31.** Everything that is fitted is
  fitted on this and only this — the model, the climatology baseline, the mean
  bias figure.
- **Validation year: 2024-08-01 to 2025-07-31.** A practice stand-in for the
  real test year. It has the same August-to-July shape, so it covers all four
  seasons the same way the real test does.
- **The real test year (2025-08-01 to 2026-07-31, D13) stays sealed** until a
  later session, and is judged exactly once.
- Reason: the frozen bar (SPEC 2.4, 5.3) only means something if the test year
  is looked at once. Every look at it is a chance to adjust the method to suit
  it, which quietly turns a test into a fit. So the whole evaluation — the
  join, the baselines, the model, the comparison — is rehearsed on a year taken
  from inside training first. The single real look happens once the method is
  locked.
- Note this splits the D13 training window in two. D13 is unchanged: the
  training window is still 2021-03-24 to 2025-07-31. Inner-training and the
  validation year are a subdivision *inside* it, used for this rehearsal.

**D19. The stage 1 feature set is deliberately minimal.**
- The features are the **forecast temperature** and the **season**, where
  season is the day of the year encoded as a sine and a cosine pair. The
  sine/cosine encoding makes 31 December and 1 January neighbours instead of
  sitting at opposite ends of a number line.
- **Hour of day is not a feature.** The target hour is fixed at 12:00 UTC
  (SPEC 4.1), so it carries no information.
- **No recent-observation feature.** Nothing like "yesterday's observed
  temperature" or "yesterday's error" is included, even though it would be
  legal under SPEC 2.1d. Reason: it keeps the claim clean — the model is
  correcting *the forecast*, not quietly becoming a persistence model wearing
  a forecast as a feature. It may be revisited later if the correction turns
  out too weak without it.

---

## 2026-08-17 — Session 04 findings (join, bias, and the validation rehearsal)

The join, the bias look and the model all ran for real. **The test year was not
touched**: the two 2026 raw chunk files were never opened, the 2025 chunk was
cut off at 2025-07-31 on load, and the script asserts that no date on or after
2025-08-01 reached any table. Full output in
`notes/session-04-check-output.txt`.

[F11, the correction to F1's superseded continuity claim, archived verbatim to DECISIONS-archive.md alongside F1. Settled; F8 (kept live here) is the finding that actually maps EGLC's forecast gap. Full text preserved there and in git.]

**F12. The join at 12:00 UTC, rows kept and dropped.** One row per day: date,
forecast temperature, observed temperature, and the residual the model learns.

```
                                         days   kept   drop  no fc  null fc  no obs
inner-training 2021-03-24..2024-07-31   1,226  1,205     21      0       20       1
validation     2024-08-01..2025-07-31     365    364      1      0        0       1
```

Every dropped day is accounted for, and nothing was filled (SPEC 2.2):
- **20 of the 21 inner-training drops are the F8 forecast gap** (see Q10
  below).
- **1 inner-training drop is a missing observation**, 2023-06-11.
- **1 validation drop is a missing observation**, 2024-08-14. That same single
  missing observation also costs the persistence baseline the following day,
  2024-08-15, which is why the scored validation set is 363 days rather than
  364.
- Across the whole loaded period, exactly **1** observation report fell more
  than 15 minutes from the hour and was dropped by the D14 rule, and **0**
  reports at 12:00 carried a missing temperature.

**Q10 addressed.** The F8 gap costs **20 days**, not 21: the gap ends at
2024-01-19 11:00 UTC and the series resumes at 12:00 UTC that day, which is
exactly the target hour, so 2024-01-19 survives. Those 20 days were dropped and
counted, as SPEC 2.2 requires. At the 12:00-only daily resolution the loss is
20 days out of 1,226 (1.6%) — and worth remembering, it is 20 consecutive
mid-winter days out of about 250 winter days in inner-training, so it is about
8% of the deep-winter training days rather than 1.6% spread evenly.

**F13. The bias at 12:00 UTC has real structure, and it is at the WARM end,
not the cold end (answers Q11).** Inner-training only.

Overall:
```
bias (observed - forecast), n = 1,205
mean   = -0.108 degC      median = +0.000 degC     st dev = 1.551 degC
min    = -7.0 degC        max    = +5.6 degC
5th pct = -2.78   25th = -1.00   75th = +0.90   95th = +2.10
mean absolute size (= raw GFS MAE in sample) = 1.172 degC
station warmer than the forecast on 587 of 1,205 days (48.7%)
```

The mean bias is almost zero. That is the important part: **there is very
little constant offset to correct at 12:00 UTC.** The structure is all in how
the bias varies.

Against forecast temperature:
```
forecast band (degC)     days  mean bias   st dev  mean |bias|
0 to 5                     47     -0.049    1.557        1.206
5 to 10                   220     +0.361    1.307        0.998
10 to 15                  356     +0.387    1.424        1.118
15 to 20                  276     -0.287    1.678        1.270
20 to 25                  223     -0.746    1.354        1.194
25 to 45                   83     -1.201    1.457        1.466

coldest 10% of forecasts  n=120  forecast  +1.0 to  +7.3 degC  mean bias +0.097
warmest 10% of forecasts  n=120  forecast +23.1 to +39.4 degC  mean bias -1.155
```

This **corrects the expectation set by F10**. F10 looked at all 24 hours and
saw a forecast that never reached the station's cold extremes, and Q11 asked
whether that cold-end shift needed attention. At 12:00 UTC specifically, the
cold end is not the problem — the forecast is essentially unbiased below 10
degC, and there is barely a cold tail at all (over three and a bit years, the
12:00 forecast never once went below 0 degC). The problem is the **warm end**:
on the hottest days GFS runs about **1.2 degC too warm**. That is consistent
with the grid cell sitting about 4 km away and partly over the Thames (Q5) —
water damps a hot afternoon. F10's cold-end observation was presumably driven
by night-time hours, which stage 1 does not target.

By season, the same pattern seen through the calendar:
```
season         days  mean bias   st dev  mean |bias|
winter DJF      251     +0.356    1.340        1.065
spring MAM      345     -0.061    1.624        1.203
summer JJA      336     -0.549    1.755        1.437
autumn SON      273     -0.052    1.194        0.907
```
GFS runs slightly cold in winter and clearly warm in summer, and summer is also
where the error is largest and most variable. The full month-by-month table is
in the notes file.

**F14. The validation rehearsal. The correction beats all four references, but
the margin over a plain constant offset is small.**

Model: LightGBM gradient-boosted trees, fitted on the 1,205 inner-training rows
only, predicting the residual from the D19 features. Settings were fixed before
the run and nothing was tuned, grid-searched or varied:
```
objective=regression (squared error)  n_estimators=300  learning_rate=0.05
num_leaves=15  min_child_samples=40  subsample=1.0  colsample_bytree=1.0
reg_alpha=0.0  reg_lambda=0.0  random_state=42  n_jobs=1  deterministic=True
lightgbm 4.7.0, numpy 2.5.2, python 3.12.2
```
Two consecutive runs produced byte-identical output, so the result is
reproducible.

All five methods scored on the same 363 validation days:
```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.239     -0.278      1.630        4.90
Persistence                2.226     -0.017      2.928       12.00
Climatology                2.865     +0.020      3.656       11.65
Mean-bias reference        1.231     -0.170      1.615        4.79
ML-corrected               1.190     -0.166      1.580        5.76
```

Verdicts:
```
vs Raw GFS              YES   1.190 against 1.239  ->  0.049 degC better (4.0%)
vs Persistence          YES   1.190 against 2.226  ->  1.036 degC better (46.5%)
vs Mean-bias reference  YES   1.190 against 1.231  ->  0.041 degC better (3.3%)
vs Climatology          YES   1.190 against 2.865  ->  1.675 degC better (58.5%)
```

**This is a validation rehearsal, not the frozen bar (SPEC 5.3).** The frozen
bar is judged once, on the sealed test year, in a later session. A good number
here means the method is ready for that single look. It does **not** mean
stage 1 has passed.

Read honestly, the numbers say three things:

1. **The correction does beat raw GFS, and it beats it by learning structure,
   not by shifting everything.** The mean-bias reference — the forecast plus a
   single constant, the inner-training mean bias of -0.108 degC — improves on
   raw GFS by only 0.008 degC. So almost all of the model's 0.049 degC gain is
   structure, which matches F13: there was hardly any constant offset to take.
2. **But the total gain is small: 4.0%, about 0.05 degC.** Raw GFS at 12:00
   UTC is already good (1.24 degC MAE), and the residual left over is mostly
   day-to-day noise rather than repeatable bias. Beating a constant offset by
   3.3% is a real win over the sanity check, but it is a narrow one, and 363
   days is not many.
3. **The win is essentially a summer win, and it is not uniform:**
   ```
   season         days   raw GFS   ML-corr    change
   winter DJF       90     0.972     1.068    +0.096   (worse)
   spring MAM       92     1.337     1.363    +0.026   (worse)
   summer JJA       90     1.498     1.204    -0.294   (better)
   autumn SON       91     1.147     1.121    -0.026   (better)
   ```
   The model helps most exactly where F13 said the bias was largest (summer)
   and slightly hurts in winter and spring. That is coherent — it is the same
   finding twice — but it means the headline average hides a season where the
   correction is a small step backwards. Winter is also the season missing
   20 consecutive training days (Q10), which may be part of it.

Feature importances, as a sanity check that the model used what it was meant
to:
```
feature                      gain  gain share   splits
forecast_temp_c            7056.8       51.8%    1,651
season_sin                 3085.0       22.6%    1,141
season_cos                 3483.1       25.6%    1,408
```
Forecast temperature carries about half the gain and season the other half,
split fairly evenly between its two components. Nothing is ignored and nothing
dominates, which is what F13's picture predicts: the bias depends on both how
warm it is and what time of year it is.

The corrections the model actually applied over the validation year were
modest — mean -0.112 degC, standard deviation 0.820, range -2.4 to +2.1 degC.
It is nudging the forecast, not rewriting it.

For the record, the in-sample figures were raw GFS 1.172 degC against
ML-corrected 0.857 degC on inner-training. That gap between 27% in-sample and
4% on validation is the ordinary sign of a flexible model fitting noise it
cannot generalise. It is recorded only so the number is not a surprise later;
it proves nothing.

**How each reference was built, for the record:**
- **Raw GFS** — the forecast value itself, uncorrected.
- **Persistence** — the previous calendar day's 12:00 UTC observation. Past
  values only (SPEC 2.1d).
- **Climatology** — the seasonal average of the *observed* temperature for that
  position in the year, averaged over every inner-training observation within
  7.5 days of it, measured around the circle so late December and early January
  are neighbours (SPEC 2.1c). Between 30 and 61 inner-training days sit behind
  each value, 49.5 on average.
- **Mean-bias reference** — the forecast plus -0.108 degC, that figure being
  the mean inner-training bias and nothing else.
- **ML-corrected** — the forecast plus the model's predicted residual.

Nothing was fitted on the validation year: not the model, not the climatology,
not the mean bias, not any encoding.

---

## 2026-08-17 — Open questions raised by session 04 (not acted on)

**Q12. Is a 4.0% improvement on raw GFS enough to be worth carrying to the
sealed test?** The rehearsal wins on all four references, so on the frozen bar
as written (SPEC 5.3, beat raw GFS and persistence) the method would pass. But
the margin over raw GFS is 0.049 degC on 363 days, and the correction makes
winter and spring slightly worse. Nothing here was tuned, so there is likely
room to do better — but improving the method means more looks at the validation
year, which is allowed, whereas looking at the test year is not. The owner
decides whether to go straight to the single sealed-test evaluation, or to
spend one more session improving the method against validation first.

**Q13. Should SPEC 5.3 gain a numeric margin before the sealed test?** SPEC 5.3
says a specific figure "may be fixed just before the model is run — but still
before seeing any results". Validation results now exist, which makes this
awkward: any margin chosen now is chosen in the knowledge that validation gave
4.0%. The honest options are to leave the bar qualitative as it stands, or to
write down a margin and record openly that it was set after seeing validation
(but before seeing the test year). The owner decides. Nothing was changed.

**Q14. Should the mean-bias reference join the baselines in SPEC 5.2?** It
turned out to be the most informative comparison of the five — it is what
separates "the model learned something" from "the model found a constant".
SPEC 5.2 currently lists raw GFS, persistence and optional climatology. Adding
it would be a SPEC edit, which this session is not authorised to make.

**Q15. The model objective is squared error while the metric is MAE.** The
model was fitted with LightGBM's default squared-error objective, but judged on
mean absolute error (SPEC 5.1). Fitting with an absolute-error objective would
line the two up and might do better on the metric that counts. Trying it is a
model variant, which this session's scope forbids. Logged for the owner.

**Q16. LightGBM needed an OpenMP library that is not installed on this
machine.** There is no Homebrew here, so `libomp.dylib` was missing and
LightGBM would not import. The workaround used is the copy of that library
that scikit-learn's macOS package already ships: `scripts/session04_model.py`
points the dynamic loader at it and restarts itself once, in a clearly
commented block at the top. It changes nothing about the model, and both runs
were byte-identical. A cleaner fix is to install `libomp` properly. Also
recorded for reproducibility: a `.venv` virtual environment was created at the
project root holding numpy, scipy, scikit-learn and lightgbm. `.gitignore`
already ignores `.venv/`, so nothing about it enters the history — which means
the exact versions used are recorded here (python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0) and nowhere else. The owner may want a `requirements.txt`.

---

## 2026-08-17 — Session 05 decision (the objective fix)

**D20. The model is fitted on absolute error, not squared error (closes
Q15).**
- The LightGBM objective changes from `regression` (squared error, the library
  default used in session 04) to **`regression_l1`** (absolute error).
- The "objective" is the quantity the model tries to make small while it is
  being fitted. Squared error makes one big miss count far more than several
  small ones; absolute error counts every degree of miss the same.
- Reason: SPEC 5.1 measures **mean absolute error**. Session 04 fitted the
  model on one quantity and judged it on another. Lining the two up is a
  correctness fix — the model should be trained on the thing it is measured
  on. It is the right change whether or not the number improves, which is
  exactly why it was allowed while variant-hunting was not.
- **Nothing else changed.** Same D18 split, same D19 features, same tree
  settings (300 trees, learning rate 0.05, 15 leaves, minimum 40 samples per
  leaf), same seed 42, same deterministic run. Nothing was retuned to suit the
  new objective. `scripts/session05_model.py` proves this rather than claiming
  it: it reads `scripts/session04_model.py` and compares the two, setting by
  setting, constant by constant, and function source character by character.
  The printed comparison is at the top of
  `notes/session-05-check-output.txt`.
- The sealed test year was not touched. This is still a rehearsal.

---

## 2026-08-17 — Session 05 finding (the objective fix, measured)

**F15. The absolute-error objective helps a little, and it helps in the place
session 04's model was weakest.** Validation rehearsal only, same 363 days,
same harness.

The proof that only one thing changed, from the script's own comparison:
```
settings that differ between session 04 and session 05: 1
    objective   regression -> regression_l1
every other setting                                    : same
every shared constant (hour, dates, chunks, features)  : same
load_forecast_12z, load_obs_12z, all_days, year_fraction,
features, mae, describe, join, bias_look,
climatology_from_inner                                 : character-identical
model_and_evaluate                                     : one added `return`
                                                         so the comparison
                                                         section can read the
                                                         results; no
                                                         calculation touched
```
Parts A and B of the output — the join, the drop counts, the bias tables — are
character-identical to session 04's output file. Two consecutive runs of the
new script produced identical output apart from the clock time in the header
line, so the result is reproducible.

All five methods, the same 363 validation days:
```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.239     -0.278      1.630        4.90
Persistence                2.226     -0.017      2.928       12.00
Climatology                2.865     +0.020      3.656       11.65
Mean-bias reference        1.231     -0.170      1.615        4.79
ML-corrected (L1)          1.165     -0.221      1.571        5.42
```
The four non-ML rows match session 04 to three decimal places, which is the
cross-check that the harness is unchanged. Only the ML row moved.

Against session 04:
```
session 04, squared-error objective : 1.190 degC
session 05, absolute-error objective: 1.165 degC
change                              : -0.025 degC (-2.1%)
```

It still beats every reference, by wider margins than before:
```
vs                    session 04 margin   session 05 margin
Raw GFS                        +0.049              +0.074   (4.0% -> 6.0%)
Persistence                    +1.036              +1.061
Mean-bias reference            +0.041              +0.066   (3.3% -> 5.3%)
Climatology                    +1.675              +1.700
```

Per season, which is where the interesting part is:
```
season         days   raw GFS   s04 ML   s05 ML   s04 chg   s05 chg
winter DJF       90     0.972    1.068    1.059    +0.096    +0.087
spring MAM       92     1.337    1.363    1.322    +0.026    -0.015
summer JJA       90     1.498    1.204    1.177    -0.294    -0.321
autumn SON       91     1.147    1.121    1.098    -0.026    -0.049
```
("chg" is the corrected MAE minus raw GFS MAE for that season. Negative means
better than raw GFS.) Session 04's picture was "a summer win, with winter and
spring made slightly worse". After the fix, **spring flips from slightly worse
to slightly better**, summer improves further, autumn improves, and winter is
still worse than raw GFS but by less. So the correction now helps in three
seasons out of four instead of two. Winter remains the one season where the
correction is a small step backwards — the same winter that is missing 20
consecutive training days (Q10).

Feature importances, still sane and still using both inputs:
```
feature             s04 gain %  s05 gain %  s04 splits  s05 splits
forecast_temp_c          51.8%       44.3%       1,651       1,614
season_sin               22.6%       26.7%       1,141       1,337
season_cos               25.6%       29.0%       1,408       1,249
```
Gain is on a different scale under an absolute-error objective, so only the
shares and the split counts compare meaningfully. Season now carries slightly
more of the weight than before. Nothing is ignored and nothing dominates.

Two honest notes on the size and shape of this:

1. **The gain is real but small.** 0.025 degC off the corrected MAE, on 363
   days. The win over raw GFS goes from 4.0% to 6.0%, which is still 0.074
   degC — the same order of magnitude as before. The objective fix did not
   change the character of the result; it made a small win slightly less
   small. That was the expected outcome and it is why the change was made on
   principle rather than for the number.
2. **The new model fits its training data less tightly, not more.** In-sample
   MAE on inner-training went from 0.857 (session 04) to 0.879 degC — worse
   in sample, better on validation. That is the ordinary signature of a less
   over-fitted model: absolute error does not chase extreme days the way
   squared error does, so the fitted corrections are more conservative. The
   corrections applied over the validation year bear that out — mean -0.057
   degC, standard deviation 0.720, range -1.8 to +1.8, against session 04's
   mean -0.112, standard deviation 0.820, range -2.4 to +2.1. It nudges the
   forecast even more gently than before.

**This is a validation rehearsal, not the frozen bar (SPEC 5.3).** The bar is
judged once, on the sealed test year, in a later session. Stage 1 has not
passed. The test year was not touched: the two 2026 raw chunk files were never
opened, the 2025 chunk was cut off at 2025-07-31 on load, and the script
asserts that no date on or after 2025-08-01 reached any table.

**Q15 is closed** by D20 and this finding.

---

## 2026-08-17 — Session 06: THE METHOD LOCK

No model was built, run or refitted this session, and the test year was not
touched. This section is the written lock, plus the three SPEC questions the
owner has now answered and the environment pin.

**D21. The method is LOCKED. This entry fully specifies what the sealed-test
session will run.**

The point of writing this down before the test year is opened is simple: every
choice below is made *now*, with the test year still unseen. The test session
executes this record and reports. It decides nothing.

**D21.1 — Target.** The temperature at **12:00 UTC** at **London City airport
(EGLC)**, latitude 51.505, longitude 0.055 (SPEC 4.1). One row per day.

**D21.2 — What the model predicts.** The **residual**: observed minus forecast
(SPEC 4.2). The corrected forecast is the GFS forecast plus the predicted
residual. The model never predicts temperature directly.

**D21.3 — Features.** The D19 minimal set, exactly three:
```
forecast_temp_c   the GFS forecast temperature for that day at 12:00 UTC
season_sin        sin(2 * pi * year_fraction(date))
season_cos        cos(2 * pi * year_fraction(date))
```
where `year_fraction` is `(day_of_year - 1) / 365`, or `/ 366` in a leap year.
No hour-of-day feature (the hour is fixed, so it carries no information). No
recent-observation feature, even though SPEC 2.1d would allow one — see D19 for
why.

**D21.4 — Model and settings.** LightGBM gradient-boosted trees (SPEC 4.4,
D12), with exactly the session 05 settings, unchanged:
```
objective=regression_l1   (absolute error, D20)   n_estimators=300
learning_rate=0.05        num_leaves=15           min_child_samples=40
subsample=1.0             colsample_bytree=1.0    reg_alpha=0.0
reg_lambda=0.0            random_state=42         n_jobs=1
deterministic=True        force_row_wise=True     verbose=-1
```
Nothing is tuned, searched or varied in the test session. Library versions are
pinned in `requirements.txt` (D24): python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0.

**D21.5 — Training data for the test: the FULL D13 training window,
2021-03-24 to 2025-07-31.** That is inner-training **and** the validation year
recombined into one training set.
- Reason: the D18 split existed so the method could be rehearsed without
  touching the test year. The method is now locked, so validation has finished
  its job, and holding a year back would only throw away real training data.
  Refitting on all non-test data before the single test is the standard move.
- Everything fitted is fitted on this window and nothing else: the model, the
  climatology baseline (SPEC 2.1c) and the mean-bias figure.
- **Note the consequence, so it is not a surprise:** the model that is tested
  is not literally the model measured in session 05. It is the same recipe
  fitted on about 20% more data, including one more year of seasons. That is
  expected to help slightly, but it means the test number will not match the
  validation number exactly, and it should not be expected to.

**D21.6 — Test data: 2025-08-01 to 2026-07-31 (D13), and nothing after it.**
The 2026 raw chunk files are opened for the first time. Data after 2026-07-31
is not used, keeping the test set exactly one calendar year.

**D21.7 — Pairing and missing data.** The D14 rule: the routine `:50` report is
the truth observation, each 12:00 forecast is paired with the observation
nearest that hour, and if no report falls within 15 minutes of the hour the day
is dropped and counted. Drop, count, report — nothing filled, ever (SPEC 2.2).
The drop counts for both the training window and the test year are part of the
output.

**D21.8 — The four references. Anything that has to be *fitted* is fitted on
the training window only.** Raw GFS and persistence are fitted on nothing —
they are just values. Climatology and the mean-bias figure are fitted, and both
come from the D13 training window (SPEC 2.1c).
- **Raw GFS** — the forecast value itself, uncorrected. *Part of the bar.*
- **Persistence** — the previous calendar day's 12:00 UTC observation. Past
  values only (SPEC 2.1d). *Part of the bar.* Note that for the first test day,
  2025-08-01, "yesterday" is 2025-07-31, which sits in the training window.
  That is a past observation, so it is legal and it will be used; it is written
  down here so it is not mistaken for leakage later.
- **Climatology** — the seasonal average of the *observed* temperature for that
  position in the year, averaged over every **training-window** observation
  within 7.5 days of it, measured around the circle so late December and early
  January are neighbours (SPEC 2.1c). *Informative only.*
- **Mean-bias reference** — the forecast plus one constant: the mean
  **training-window** bias. *Informative only* (SPEC 5.2, D23).

All five methods — the four above plus the corrected forecast — are scored on
the **same set of days**, the days where every method has a value.

**D21.9 — The metric and the bar.** Mean absolute error in degrees Celsius
(SPEC 5.1). **Stage 1 passes if the corrected forecast has a lower MAE than
both raw GFS and persistence over the test year.** No numeric margin — the bar
is qualitative and stays that way (D22, SPEC 5.3). Climatology and the
mean-bias reference are reported but do not decide pass or fail.

**D21.10 — One look, and the result stands.** The test year is opened once,
this method is run once, and whatever comes out is reported straight — pass or
fail, with the seasonal breakdown and the drop counts. A failure is an honest
finding (SPEC 2.4), not something to fix by trying again. If the result
disappoints, the response is a new decision logged here by the owner, never a
quiet re-run.

**D21.11 — Deviation is a stop signal.** If the test session finds any reason
to depart from this record — a setting that does not fit, a missing file, a
count that will not reconcile, a tempting small improvement — it **stops and
raises it with the owner**. It does not decide on the fly with the test year
open. Any change to the above is a new DECISIONS entry made deliberately, not
an adjustment made mid-run.

---

**D22. The success bar stays qualitative — no numeric margin, ever (closes
Q13).**
- SPEC 5.3 previously left the door open to fixing a numeric figure "just
  before the model is run". That door is now closed, and SPEC 5.3 says so.
- Reason: validation results exist (F14, F15). Any figure chosen now would be
  chosen knowing validation gave a 6.0% win, which is not the clean
  before-the-fact choice rule 2.4 demands. Setting a bar that the known result
  comfortably clears would be self-flattering; setting one it does not clear
  would be equally arbitrary. The honest option is to fix no number at all.
- What survives is the bar as originally frozen: beat raw GFS **and**
  persistence on MAE over the test year. That was written before any model
  existed and it is unchanged.
- The cost of this is worth stating plainly: a win of, say, 0.01 degC would
  count as a pass under a purely qualitative bar. The size of the margin is
  therefore reported prominently alongside the verdict, so a technical pass by
  a hair reads as what it is.
- **SPEC edit made:** section 5.3, authorised by session 06 A-1.

**D23. The mean-bias reference is now a listed baseline, as an informative
check (closes Q14).**
- SPEC 5.2 now lists four references: raw GFS, persistence, climatology and the
  mean-bias reference — the forecast plus GFS's average bias measured on
  training data only.
- Reason: it turned out to be the most informative of the five comparisons
  (F14). It is the simplest correction anyone could apply — one constant, no
  learning — so it separates a model that learned real structure from a model
  that merely found an offset. Session 04's model beat it by 3.3% and session
  05's by 5.3%, which is what makes "it is learning structure" a claim with
  evidence behind it.
- **It is not part of the pass/fail bar.** The bar stays raw GFS and
  persistence (D10, D22). SPEC 5.2 now says this explicitly, because a baseline
  list that does not say which entries decide the verdict invites confusion
  later.
- **SPEC edit made:** section 5.2, authorised by session 06 A-2.

**D24. The environment is pinned in `requirements.txt` (closes Q16).**
- A `requirements.txt` now records the exact versions: python 3.12.2 with
  numpy 2.5.2, lightgbm 4.7.0, scikit-learn 1.9.0, scipy 1.18.0, joblib 1.5.3,
  threadpoolctl 3.6.0, narwhals 2.24.0.
- Only **numpy** and **lightgbm** are imported by the scripts. scipy and
  narwhals are lightgbm's own dependencies. scikit-learn is pinned for one
  reason only: it is the current source of the OpenMP library, below.
- **The OpenMP note, written into the file as a comment.** LightGBM's macOS
  build will not import without `libomp.dylib`, which is a system library, not
  a Python package, so pip cannot supply it. The normal fix is
  `brew install libomp`. This machine has no Homebrew, so the model scripts use
  the copy that scikit-learn's macOS wheel ships: they point the dynamic loader
  at it and restart the interpreter once, in a commented block at the top of
  `session04_model.py` and `session05_model.py`. It changes nothing about the
  model — repeat runs were byte-identical (F14, F15) — and it becomes a no-op
  if `libomp` is ever installed properly.
- **No script behaviour was changed** this session.

**D25. SPEC 3.2 now records the forecast gap.** SPEC 3.2 said the archive was
"confirmed available back to 24 March 2021" and said nothing about the 492-hour
gap, so a reader could infer the archive is continuous — the exact mistake F1
made and F11 corrected. One clause was added naming the gap (2023-12-30 00:00
to 2024-01-19 11:00 UTC, training window only, dropped and counted), pointing
at F8 and F11. This records a fact already established; it changes no decision.
**SPEC edit made:** section 3.2, authorised by session 06 A-3.

---

## 2026-08-17 — Session 06 note (no findings, nothing measured)

This session ran no code against the data and produced no numbers of its own.
There is therefore no F-entry. What it produced is the lock above, three SPEC
edits, and one new file (`requirements.txt`).

**Q13, Q14 and Q16 are closed** by D22, D23 and D24.

**Q12 is also closed, by the lock itself.** Q12 asked whether to spend another
session improving the method against validation, or to go to the sealed test.
The owner chose the second: session 06's whole purpose was to lock and prepare
for the test. D21 is that answer written down. The 6.0% validation win is
carried to the test as it stands, with no further tuning.

Q7, Q8, Q9, Q10, Q11 and Q15 were closed in earlier sessions. **No open
questions remain.**

**One thing noticed and deliberately not acted on.** `.DS_Store` files exist in
the working tree at the project root and in `scripts/`. Q9 confirmed the
tracked one was removed from the index and that `.gitignore` matches the
pattern, so these are untracked clutter, not a problem — recorded only so the
owner is not surprised to see them.


---

## 2026-08-17 — Session 07: THE SEALED-TEST RESULT (stage 1 is decided)

The test year was opened for the first and only time. The method locked in D21
was executed and nothing was decided, tuned, swapped or re-run. This section is
the stage 1 result of record. The script is `scripts/session07_test.py` and the
full real output is `notes/session-07-check-output.txt`.

**F16. STAGE 1 PASSES. The corrected forecast beats both raw GFS and
persistence on the held-out test year.**

The verdict first, because that is what the session was for:

```
                        MAE degC   part of bar?
Raw GFS                    1.242   YES
Persistence                2.096   YES
Climatology                2.972   no  (informative)
Mean-bias reference        1.234   no  (informative)
ML-corrected               1.040   the claim

vs Raw GFS       BEATEN   1.040 against 1.242  ->  0.202 degC better (16.3%)
vs Persistence   BEATEN   1.040 against 2.096  ->  1.056 degC better (50.4%)
```

**Stage 1 passes on the frozen bar (SPEC 5.3, D21.9): the corrected forecast has
a lower MAE than both raw GFS and persistence over 2025-08-01 to 2026-07-31.**
The margin is stated prominently because D22 requires it — this is not a pass by
a hair. It is 0.202 degC, a 16.3% cut in the average error against raw GFS.

The full table, all five methods on the same 363 days:

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.242     -0.369      1.672        6.00
Persistence                2.096     -0.008      2.775       10.00
Climatology                2.972     +0.773      3.865       16.11
Mean-bias reference        1.234     -0.221      1.646        5.85
ML-corrected               1.040     -0.272      1.412        5.86
```

**It beats the mean-bias reference too, by 15.7% (1.040 against 1.234).** That
is the comparison that matters most for the claim (D23): the mean-bias reference
is the forecast plus one constant, with no learning in it. Beating it by that
much means the model found real structure in the bias, not just an offset. The
constant itself is tiny — the mean training-window bias is -0.1479 degC — so
there was almost no offset available to take, exactly as F13 predicted.

**Day by day, not just on average.** The correction was closer to the truth than
raw GFS on **221 of 363 days (60.9%)** and further away on 142 (39.1%). So the
win is spread across the year rather than carried by a handful of days, but it
is far from every day — the model is nudging a good forecast, and about two days
in five it nudges the wrong way.

**Per season, the correction helped in all four:**

```
season         days   raw GFS   ML-corr    change   persistence
winter DJF       90     0.752     0.745    -0.007         1.589
spring MAM       92     1.285     1.219    -0.066         2.576
summer JJA       92     1.870     1.252    -0.618         2.391
autumn SON       89     1.045     0.934    -0.111         1.809
```
("change" is corrected MAE minus raw GFS MAE. Negative means better than raw
GFS.) This is the first time the correction has not made a season worse. Winter
is now a dead heat rather than a loss — 0.745 against 0.752, a difference of
0.007 degC, which is nothing. Summer is the whole result: 0.618 degC better on
92 days.

**The test-year drop count (D21.7).** One day dropped out of 365:

```
test-year calendar days : 365
paired rows kept        : 364
days dropped            : 1
    2025-11-21  (no usable observation)
```
The forecast series had no gap in the test year at all, as F8 said it would not.
Scoring then loses one more day — 2025-11-22 — because persistence needs the
previous day's observation and 2025-11-21 is the day that is missing. So all five
methods are scored on **363 days**. Nothing was filled (SPEC 2.2).

The training-window counts reconcile exactly against the published session 04
and 05 figures, which is the check that the harness has not drifted (D21.11):
1,205 inner-training rows plus 364 validation rows equals the 1,569 rows this
session fitted on, out of 1,591 calendar days.

**The test number against the session 05 validation number.** D21.5 said in
advance that these would differ and should not be expected to match. They do
differ, and by more than expected:

```
method                  s05 valid   s07 test  difference
Raw GFS                     1.239      1.242      +0.003
Persistence                 2.226      2.096      -0.130
Climatology                 2.865      2.972      +0.107
Mean-bias reference         1.231      1.234      +0.003
ML-corrected                1.165      1.040      -0.125
days scored                   363        363

margin over raw GFS:  validation +0.074 (6.0%)   test +0.202 (16.3%)
```

**Read honestly, the test margin is better than validation's for two reasons,
and only one of them is the model.**

1. **The model is fitted on more data.** D21.5 recombined the validation year
   into training, so the tested model saw 1,569 days instead of 1,205 — about
   30% more rows and one more full cycle of seasons. That was expected to help
   slightly.
2. **The test year suited the correction better.** Raw GFS was almost exactly as
   hard overall (1.242 against 1.239), but the difficulty sat in a different
   place. In the test year raw GFS's summer MAE was **1.870**, against 1.498 in
   the validation year — a harder summer for GFS. Summer is precisely where F13
   located the bias and where the correction has always worked best, so a summer
   with more warm-end error to remove flatters the method. Meanwhile test-year
   winter was easy for raw GFS (0.752 against 0.972), so the season where the
   correction used to lose ground had less ground to lose.

So the 16.3% figure is the honest result on the year that was sealed, but it
should not be read as "the method improved by 10 percentage points". A fair
summary is: the method wins on both years, by 6% on one and 16% on the other,
and the gap between those two numbers is mostly what the weather did.

**Two further honest notes.**

- **Climatology ran 0.773 degC cold on the test year**, against +0.020 on the
  validation year. That is not a fault in the baseline — it means the test year
  was warmer at 12:00 UTC than the 2021–2025 training average for the same dates.
  It is worth recording because it says the test year was not a neutral repeat of
  the training period.
- **Nothing about the residual scatter changed.** The corrections applied were
  modest: mean -0.098 degC, standard deviation 0.749, range -1.8 to +1.9 —
  essentially the same gentle nudge as session 05's (mean -0.057, st dev 0.720,
  range -1.8 to +1.8). The model did not start making big swings on unseen data.

**Feature importances, the sanity check that it used what it was meant to:**

```
feature                 gain  gain share   splits   s05 share  s05 splits
forecast_temp_c       5265.2       51.8%    1,844       44.3%       1,614
season_sin            2496.8       24.5%    1,166       26.7%       1,337
season_cos            2411.6       23.7%    1,190       29.0%       1,249
```
Forecast temperature carries about half the gain and season the other half.
Nothing is ignored and nothing dominates — the same picture as sessions 04 and
05, which is what F13 predicts: the bias depends on both how warm it is and
what time of year it is.

For the record, in-sample MAE on the training window was 0.908 degC against raw
GFS's 1.187. A model always looks better on the data it was fitted to; that
figure proves nothing and is here only so it is not a surprise later.

**What this session did not do, on purpose.**
- **The script was run once and not repeated.** D21.10 says the method is run
  once, so no second run was made to confirm byte-identical output, even though
  sessions 04 and 05 both did that. Determinism rests on the fixed seed,
  `deterministic=True`, `n_jobs=1`, the pinned versions in `requirements.txt`
  (D24) and the byte-identical repeat runs already recorded in F14 and F15.
  Re-running the unchanged script would change nothing about the result above,
  but the strict reading of the lock was followed rather than the convenient one.
- **The deeper evaluation stays parked.** Skill scores, statistical
  significance and formal season-by-season testing are SPEC 5.4 items, parked
  until stage 1 passes. Stage 1 has now passed, so they can be opened — but they
  were not opened here. The seasonal table above is context, not a significance
  test.
- **Nothing was committed.**

**No SPEC edit was made this session, and none was authorised.** The bar was
judged as written.

---

## 2026-08-17 — Open questions raised by session 07 (not acted on)

Stage 1 has passed, which opens two choices that are the owner's to make. Both
are recorded here and neither was acted on.

**Q17. Stage 1 has passed — does stage 2 open now, and with what scope?** SPEC
section 6 says stage 2 is the same recipe at a second airport, Charles de Gaulle
(CDG), to prove stage 1 was not a fluke. SPEC deliberately leaves stage 2
unspecified until the owner opens it, and section 6 says a session that fills in
a later stage early is a warning sign. So nothing about stage 2 was written or
started. Two things F6 already flagged for it: CDG is also in Europe so the
`gfs_global` reasoning should carry over, but it must be re-checked rather than
assumed; and the observation record and archive start date at CDG are
verify-on-contact facts, exactly as Q1 and Q2 were for EGLC.

**Q18. Does any of the parked SPEC 5.4 evaluation get done now that stage 1 has
passed?** SPEC 5.4 parks skill scores, statistical significance and formal
season-by-season testing until stage 1 passes. It has now passed, so they are
available. The case for doing some of it first is in F16: the test-year margin
(16.3%) is much larger than the validation margin (6.0%), and F16's own reading
is that most of that gap is what the weather did rather than what the model
learned. A significance check on 363 days would say how much of the win is
solid. The case against is that stage 2 at a second airport is a stronger and
more honest robustness check than any statistic on the same 363 days. The owner
decides which comes first, or whether both do. Nothing was started.

---

## 2026-08-17 — Session 08 decisions (Stage 2 opens)

Stage 1 passed (F16), so the owner has opened Stage 2. These two entries are
the opening decisions, written before any CDG data was pulled.

**D26. Stage 2 is opened: the second airport is Paris Charles de Gaulle
(CDG / ICAO LFPG). This answers Q17.**
- **The job of Stage 2 is to prove the recipe travels.** Stage 1 worked at one
  airport. A method that only works where it was built is not a method, it is a
  fit. Running the same recipe at a genuinely different location is the test of
  that.
- **Target: the temperature at 12:00 UTC at LFPG — the same fixed hour as
  Stage 1.** The hour is kept identical on purpose. Stage 2 changes the
  **location and nothing else**, so if the result differs, the location is the
  only thing that can explain it.
- **Everything else is reused unchanged from Stage 1**, pending verification
  that CDG's data supports it: the model and its settings (D21.4), the minimal
  three-feature set (D19), the train/test split dates (D13), the pairing rule
  (D14), the drop-count-report rule (SPEC 2.2), the four references (D21.8) and
  the frozen qualitative bar (SPEC 5.3, D22).
- **"Pending verification" is the important clause.** Reusing a rule written
  around EGLC's habits only works if CDG has the same habits. That is what this
  session checked, and one of those rules did need a closer look — see F18.

**D27. The target-hour convention for Stage 3, noted now and NOT acted on.**
- When airports are pooled into one model at Stage 3 (SPEC section 6), the
  target hour will switch from a fixed UTC hour to **solar standard noon** —
  each airport's local standard-time noon.
- **Daylight saving is deliberately ignored.** That keeps the target at a fixed
  UTC hour for each airport all year round, so there is no seasonal jump in the
  middle of the data, while the sun still sits at a comparable height across
  airports.
- Why it is written down now rather than later: a pooled model compares
  airports, and comparing 12:00 UTC at London with 12:00 UTC at a location
  several time zones away would be comparing different times of day. Deciding
  the convention while nothing depends on it is cleaner than deciding it under
  pressure when the pooling session needs an answer.
- **This is not applied to Stage 2.** Stage 2 stays on 12:00 UTC at both
  airports (D26). LFPG's local standard time is UTC+1, so its solar standard
  noon would be 11:00 UTC — close to 12:00 UTC but not the same, which is
  exactly why the convention needs to be a deliberate decision rather than a
  detail settled by accident.

---

## 2026-08-17 — Session 08 findings (CDG verified on contact)

This session pulled small samples only. **No full dataset was pulled, nothing
was joined, built, trained or evaluated, and nothing from Stage 1 was touched or
re-run.** Six raw files went into `data/raw/`, each with a `.meta.txt` beside it
recording the pull time and the exact request (SPEC 2.3). The script is
`scripts/session08_checks.py` and the full real output is
`notes/session-08-check-output.txt`.

**F17. The station position used, and the forecast grid point returned.**

The session prompt quoted CDG at approximately 49.010 N, 2.548 E, elevation
~119 m, and asked for IEM's own metadata to be used instead. IEM's record
differs a little:

```
                    IEM metadata      prompt's figure     difference
latitude            49.0153           49.010              +0.59 km
longitude           2.5344            2.548               -0.99 km
elevation           109.0 m           119 m               -10.0 m
                                      the two are 1.15 km apart
```

**IEM's figures were used for every forecast pull**, and the observation file
IEM returns carries the same lat/lon/elevation, so the two IEM sources agree
with each other. The 10 m elevation difference is worth noting but changes
nothing here.

Against Stage 1's airport, LFPG is a genuinely different setting, which is the
point of Stage 2:

```
        latitude   longitude   elevation
EGLC    51.5053    0.0553        5 m
LFPG    49.0153    2.5344      109 m
        328 km apart, 104 m higher
```

The forecast grid point Open-Meteo returned for LFPG:

```
requested        : lat 49.0153,  lon 2.5344
grid point       : lat 49.027008, lon 2.578125, elevation 109 m
distance         : 3.44 km from the airport
height mismatch  : 0.0 m  (grid 109 m, station 109 m)
```

For comparison, EGLC's grid point is 4.33 km away with a 1 m height mismatch
(Q5). So CDG's grid point is slightly closer and, on the numbers, an exact
elevation match. That last point should not be over-read: a GFS cell elevation
is a smoothed average over a wide area, so an exact match to the station figure
is a pleasant coincidence rather than evidence the cell represents the airport.
What it does say is that there is no height problem to worry about at CDG, the
same conclusion Q5 reached for EGLC.

**F18. LFPG reports ON THE HOUR, not at :50 — so the D14 pairing rule applies
as it stands and actually fits CDG better than it fits EGLC. But CDG files
off-hour reports more often, and those cost days.**

This was the key CDG-specific unknown, because D14 was written around EGLC's
habit of reporting at :50.

Recent sample, 1–21 July 2026, routine METARs only:

```
reports in file  : 504
minute-past-hour : :00 x501, :30 x3
rows with no temp: 0
expected hours   : 504
hours covered    : 504
hours MISSING    : 0  (0.00%)
```

Early sample, 18–31 March 2021, routine METARs only:

```
reports in file  : 334
minute-past-hour : :00 x334
rows with no temp: 0
expected hours   : 336
hours covered    : 334
hours MISSING    : 2  (0.60%)  -> 2021-03-20 07:00 and 2021-03-30 16:00 UTC
```

So the on-the-hour habit holds at both ends of the period, five years apart.
Nothing was filled (SPEC 2.2); the two missing hours are whole reports never
filed.

**Does D14 need adapting? No.** D14 says: pair each `HH:00` forecast with the
nearest report, and drop the hour if no report falls within 15 minutes of it.
Written for a station reporting at :50, it produces a 10-minute offset at EGLC.
At LFPG it produces an **exact match, 0 minutes**, because the report is stamped
on the hour already. The rule is unchanged and the pairing it gives is strictly
better. The 10-minute-gap argument D14 rests on does not even need to be made
for CDG.

**But there is a real catch, and it is the one thing this session found that
needs the owner's attention.** Three of the 504 recent routine reports came in
at `:30` rather than `:00`:

```
2026-07-02 17:30 UTC   (dropped by D14 - 30 minutes from the hour)
2026-07-08 12:30 UTC   (dropped by D14)
2026-07-20 00:30 UTC   (dropped by D14)
```

D14 drops all three, correctly — they sit 30 minutes out, twice the tolerance.
Two of them do not matter, because Stage 1's target is 12:00 UTC only. **The
middle one does:** on 2026-07-08 the only routine report in the noon hour was at
12:30, so there is no observation for 12:00 UTC that day and the day is dropped.

Counting what D14 would keep at the target hour, observation side only:

```
recent sample 2026-07-01..2026-07-21   21 calendar days, 20 kept, 1 dropped
                                       (2026-07-08, only report was 12:30)
early sample  2021-03-18..2021-03-31   14 calendar days, 14 kept, 0 dropped
pairing offset on every kept day       : 0 minutes
```

**The rate is what deserves a second look, not the rule.** Over five years at
EGLC, exactly 8 reports out of 46,919 fell more than 15 minutes from an hour
(F9) — about 0.017%. LFPG produced 3 out of 504 in three weeks — about 0.60%,
roughly 35 times higher. If that rate held across the roughly 1,950 days from
2021-03-24 to 2026-07-31, it would cost **about 12 days** at the 12:00 target.

For contrast, over EGLC's training and validation years this cause cost **no
days at all** at 12:00 UTC. F12 found exactly one report in that whole loaded
period more than 15 minutes from an hour, and it was not at noon: every day
lost there went to the forecast gap or to a missing observation, never to a
report filed at an odd minute. (F16 records one day dropped in the test year,
2025-11-21, as "no usable observation" without saying which of the two causes it
was. It is one day either way, so it does not change the comparison, and this
session did not re-open stage 1's data to find out.)

About 12 days out of ~1,950 is still a small number, and the drop-count-report
rule handles it exactly as written. **But three weeks is a small sample, and one
of the three off-hour reports landed on the target hour — which is either bad
luck or a hint that off-hour reports cluster around the middle of the day.** One
in three is far too little to tell those apart. The full pull will settle it, and
the honest thing is to look at the number then rather than guess now. See Q19.

**F19. LFPG files a scheduled half-hourly report at :30, which IEM labels
"special" — the same pattern EGLC shows at :20.**

Pulling the same three weeks with both report types:

```
reports in file  : 1,007
minute-past-hour : :00 x501, :06 x1, :07 x1, :30 x502, :35 x1, :57 x1
```

Subtracting the 504 routine rows leaves 503 "special" rows, of which **499 are
at :30**. So IEM's "special" label does not mean "unscheduled" at LFPG any more
than it did at EGLC (F3): both stations file a second scheduled report each
hour, EGLC at :20 and LFPG at :30. Only 4 rows in three weeks look like genuine
unscheduled reports.

This is recorded, not acted on. Stage 1 used the routine report as the hourly
truth and Stage 2 reuses that unchanged (D26). It is noted because the :30
stream is the obvious place to look if Q19's off-hour drops turn out to matter.

**F20. The forecast archive starts at LFPG on exactly the same hour as it does
at EGLC: 2021-03-24 00:00 UTC.**

Two probes, both `gfs_global`, `temperature_2m_previous_day1`:

```
probe 1, 2021-03-01..2021-03-07 : 168 rows, ALL 168 null
probe 2, 2021-03-18..2021-03-26 : 216 rows, 72 with a value, 144 null
                                  first non-null = 2021-03-24T00:00
                                  value range 4.8 to 16.1 degC
```

The recent sample is complete:

```
2026-07-01..2026-07-21 : 504 rows, 504 with a value, 0 null
                         value range 8.7 to 36.7 degC
```

This is the same behaviour F1 found at EGLC, down to the hour — including the
detail that the API answers HTTP 200 with all-null values for dates before its
archive begins, rather than returning an error. That the two locations share the
exact same first hour says the March 2021 floor is a property of the archive
itself, not of any one place.

**The practical consequence: the D13 split dates carry over to CDG unchanged.**
Training 2021-03-24 to 2025-07-31 and testing 2025-08-01 to 2026-07-31 are as
available at LFPG as at EGLC. No date needs moving for Stage 2.

**F21. Plain first read — yes, CDG's data is usable for Stage 2 the same way
EGLC's was.** Every verify-on-contact check passed:

- the Previous Runs API carries the location, with a grid point 3.44 km away and
  no height problem (F17);
- the archive reaches back to the same 2021-03-24 start, so the fixed split
  dates need no change (F20);
- IEM carries LFPG in the `FR__ASOS` network with a clean, complete-looking
  observation record (F18);
- the pairing rule needs no adapting, and pairs better at CDG than at EGLC
  (F18).

The one qualification worth carrying forward is the off-hour report rate (Q19),
which is a counting question the full pull answers, not a blocker. **Nothing
here justifies changing any Stage 1 decision.**

Two things this session did **not** check, both listed as open questions below:
whether `gfs_global` and `gfs_seamless` return identical data at LFPG the way
F6 proved they do at EGLC (Q20), and whether the 492-hour forecast gap F8 found
at EGLC is present at LFPG too (Q21). Neither could be answered from
three-week samples.

---

## 2026-08-17 — Open questions raised by session 08 (not acted on)

**Q19. Off-hour routine reports at LFPG cost days at the target hour — how many,
and should the `:30` stream be allowed to rescue them?** F18 found 3 routine
reports out of 504 stamped at `:30` instead of `:00`, one of them in the noon
hour, which drops that day. The rate is about 35 times EGLC's, on a three-week
sample. Two questions follow, and both are the owner's:
- **What is the real rate over five years?** Only the full pull can say. The
  session that does the pull should count it explicitly and report the number of
  days lost at 12:00 UTC to this cause, separately from days lost to missing
  reports.
- **If it matters, should D14 be adapted for Stage 2?** The `:30` report exists
  in IEM's "special" stream (F19), so on 2026-07-08 there *was* a real
  observation 30 minutes from the target — D14 simply refuses it, correctly, as
  the rule stands. Widening the tolerance or allowing a fallback would recover
  those days, but it would also mean Stage 2 runs a different pairing rule from
  Stage 1, which weakens the "only the location changed" claim D26 rests on.
  **The default is to change nothing and take the drops**, since a handful of
  days out of ~1,900 is not worth muddying the comparison. Recorded so the
  choice is made deliberately rather than by silence.

**Q20. `gfs_global` versus `gfs_seamless` has not been re-checked at LFPG.** D16
pinned `gfs_global`, and this session used it. But F6 proved the two return
identical data **at EGLC**, and F6's own closing note said the same reasoning
should be re-checked at CDG rather than assumed. It was not re-checked this
session — that was outside the verify-on-contact scope, which was about whether
the data exists at all. The pin holds either way (D16 is a decision about which
string to use, not a claim about equivalence), so nothing is blocked. But if the
project ever wants to say "Stage 2 used exactly NCEP GFS" with the same
by-construction confidence F6 gives for Stage 1, the comparison should be run at
LFPG before the full pull.

**Q21. Is the 492-hour forecast gap present at LFPG too?** F8 found exactly one
sizeable gap in EGLC's forecast series, 2023-12-30 00:00 to 2024-01-19 11:00
UTC, falling entirely inside the training window. Because F20 shows the archive
floor is a property of the archive rather than of a location, the gap is likely
to be there at LFPG as well — but "likely" is not "checked", and F11's lesson is
precisely that spot checks cannot prove what they did not look at. The full pull
maps every hour, exactly as session 03b did, and the answer falls out of that. No
action needed now; recorded so the mapping is not forgotten.

---

## 2026-08-17 — Session 09 decisions (SPEC generalised to many airports)

This session wrote no code, pulled no data, and touched no dataset. It is a
documentation session: SPEC was rewritten so it describes a **per-airport**
project instead of a one-airport one. The three entries below are the choices
behind that edit.

**D28. SPEC is generalised to a multi-airport structure — one set of rules,
parameterised by airport.**
- **What changed in shape.** Everything shared stays stated once: the data
  sources, the method, the split dates, the pairing rule, the missing-data rule,
  the metric, the baselines and the bar. Everything that varies by location
  moves into a small **airport table** (SPEC 3.4) that grows by one row per
  airport: ICAO code, IEM network, the airport's own position, the forecast grid
  point it maps to, and the minute past the hour the station reports at.
- **What did not change.** No rule, no date, no setting and no threshold was
  altered. The bar's **meaning** is untouched — beat raw GFS and persistence on
  MAE over the held-out test year. Only its **scope** is now written down: it is
  judged once **per airport**, on that airport's own test year (SPEC 5.0, 5.3).
  An earlier airport's pass does not excuse a later airport's failure, and a
  later result does not re-open an earlier one.
- **Why now, with only two airports.** Two is the cheapest moment to do it. With
  one airport the general shape cannot be checked against anything; with five it
  is a rewrite of a much larger file, done under pressure. Doing it at two means
  the structure is proved by a real second case (CDG's row is filled from real
  pulls, not invented) while the file is still small. It also sets up stage 3,
  where airports are pooled — a pooled model needs per-airport facts to already
  be separated from shared ones, which is exactly what the table does.
- **The rule the table enforces: a row is filled from real pulls, never from
  memory or a map.** That is why one cell in it is marked unverified — see Q22.
- **SPEC edits made:** sections 1, 3 (3.1, 3.2, 3.3, and the new 3.4), 4.1, 4.3,
  4.5, 5 (new 5.0, and 5.3), 5.4 and 6. All were authorised by the session 09
  prompt as E-1 to E-9. No other part of SPEC was touched.

**D29. The deeper evaluation (SPEC 5.4) is optional and blocks nothing. This
closes Q18.**
- SPEC 5.4 parked the harder checks — skill score, statistical significance,
  formal season-by-season testing — "until stage 1 passes". Stage 1 has passed
  (F16), so that wording was stale: it read as a gate that had quietly opened
  with nobody deciding what came through it.
- **The owner's decision: they stay available but are not required.** No stage
  waits on them. No session has to do them. If they are wanted, they are a
  session of their own.
- Reason: stage 1 passed cleanly rather than by a hair — 1.040 against 1.242 for
  raw GFS, a 16.3% cut — and its season-by-season table already showed the
  correction helping in all four seasons, which is partial robustness evidence
  in itself. The stronger check on whether the method is real is running it at a
  second airport, which is what stage 2 is. A significance test on the same 363
  days would say less than CDG's result will.
- Recorded honestly: this does mean the project has no formal significance
  figure for the stage 1 win, and F16's own reading — that much of the gap
  between the 6.0% validation margin and the 16.3% test margin is what the
  weather did, not what the model learned — stands unquantified.
- **SPEC edit made:** section 5.4, authorised by session 09 E-8.

**D30. At CDG, off-hour reports cost days and the days are taken. The pairing
rule is NOT adapted for one airport. This closes Q19.**
- Q19 asked whether D14's 15-minute tolerance should be widened, or the `:30`
  "special" stream allowed as a fallback, to rescue the days LFPG loses when its
  routine report is filed off the hour (F18, F19).
- **The decision is to change nothing and take the drops.** D14 applies at CDG
  exactly as written at EGLC.
- Reason: stage 2's whole claim is that **only the location changed** (D26). A
  pairing rule that differs between the two airports would break that claim, and
  it would break it in a way that is hard to reason about afterwards — any
  difference in the result could then be the location or the rule, with no way
  to tell which. A handful of days out of about 1,900 is not worth that. The
  drop-count-report rule (SPEC 2.2) already handles them honestly.
- **What the pull session must still do:** count the off-hour reports explicitly
  and report the days lost at 12:00 UTC to that cause **separately** from days
  lost to missing reports. This decision fixes what to do about them; it does
  not excuse anyone from counting them. F18's estimate of about 12 days rests on
  a three-week sample and one off-hour report landing at noon, which is far too
  little to tell bad luck from a midday pattern.
- If the real rate turns out much larger than F18's estimate, that is a finding
  for the owner, not grounds for a quiet change of rule mid-pull.
- **SPEC edit made:** section 4.5, authorised by session 09 E-5.

---

## 2026-08-17 — Session 09 note (nothing measured, one thing found)

No code ran and no data was pulled, so there is no F-entry. What this session
produced is the generalised SPEC, the three entries above, and one open question
below.

**Q18 is closed** by D29. **Q19 is closed** by D30. Q20 and Q21 remain open and
are both answered by the CDG pull rather than by a decision.

**The frozen bar was checked, edit by edit, and its meaning is unchanged.** The
session prompt required this and it is worth writing down. Before: "Stage 1
succeeds if the corrected forecast has a lower MAE than both raw GFS and
persistence, over the held-out test period." After: the same sentence with
"Stage 1" replaced by "An airport" and "the held-out test period" by "the
held-out test period at that airport". The metric (5.1), the baselines (5.2),
the qualitative-no-numeric-margin rule (5.3, D22) and the frozen-before-running
rule (2.4) are all untouched. Nothing was added that a result must now clear,
and nothing was removed that it used to have to clear.

---

## 2026-08-17 — Open question raised by session 09 (not acted on)

**Q22. EGLC's IEM network code has never been verified.** The session 09 prompt
gave EGLC's network as `GB__ASOS` and CDG's as `FR__ASOS`, and asked for the
airport table to be filled "from verified values". CDG's is verified: session 08
pulled IEM's own station metadata for the `FR__ASOS` network and the coordinates
in the table come from that file (F17). EGLC's is not. Every EGLC request in
this project — session 01's samples and session 03b's full pull — was made with
`station=EGLC` and no network parameter at all, so IEM has never told this
project which network EGLC sits in. `GB__ASOS` is very probably right, but
"probably" is not the standard the airport table is meant to hold to, and
CLAUDE.md forbids writing a spec file from memory or assumption.
- It is therefore written into SPEC 3.4 **marked unverified**, rather than left
  out or stated as fact.
- **Nothing depends on it.** The network code is not used by any request, any
  script or any join; the pulls address stations by ICAO code. This is a
  bookkeeping gap, not a data problem.
- Fixing it is one small metadata request — the same call session 08 made for
  France, pointed at the United Kingdom network — which would be a data pull,
  and this session was documentation only. The CDG pull session could fold it in
  for free, or the owner can leave the marker where it is.

---

## 2026-08-17 — Session 10 findings (the full LFPG pull and gap map)

The full stage 2 pull ran for real: 2021-03-24 to 2026-07-31, both sources, six
yearly chunks each, plus one IEM network metadata file. 26 new files went into
`data/raw/`, with a `.meta.txt` beside every one of the 13 data files (SPEC
2.3). **Nothing was joined, filled, cleaned, built, trained or evaluated**, and
no temperature value from the test window was printed. The scripts are
`scripts/session10_pull.py` and `scripts/session10_checks.py`; the full real
output is `notes/session-10-check-output.txt` and `notes/session-10-pull-output.txt`.

**F22. Q21 answered — LFPG has EXACTLY the same 492-hour forecast gap as EGLC,
down to the hour. It is one gap and there are no others.**

```
expected hours in period : 46,944
hours with a usable value: 46,452
hours missing            : 492 (1.05% of the period)
  of which no row at all : 0
  of which row but null  : 492
rows returned outside the period: 0

training 2021-03-24..2025-07-31: 38,184 expected, 37,692 usable, 492 missing (1.29%)
test     2025-08-01..2026-07-31:  8,760 expected,  8,760 usable,   0 missing (0.00%)

GAP MAP: 1 gap run in the whole period
    last hour with data       : 2023-12-29 23:00 UTC
    first missing hour        : 2023-12-30 00:00 UTC
    last missing hour         : 2024-01-19 11:00 UTC
    first hour with data again: 2024-01-19 12:00 UTC
    length                    : 492 hours (20.5 days)
    falls entirely in training: yes
    matches EGLC's F8 gap     : YES - same start, same end, same length
```

Every one of those six totals is **identical to EGLC's** (F8), and so is the
gap's position. That is the answer Q21 wanted and it is stronger than "likely":
the gap is a property of the Open-Meteo archive itself, not of a location, in
exactly the way F20 showed the March 2021 floor is. Nothing was filled (SPEC
2.2).

The practical consequence is the same one F12 recorded at EGLC: the gap ends at
2024-01-19 11:00 UTC and the series resumes at 12:00, which is the target hour,
so **that day survives and the gap should cost 20 days at 12:00 UTC, not 21**.
That is a prediction about the join, which is the next session's job — this
session did not join anything.

The grid point Open-Meteo returned across all six chunks is lat 49.027008, lon
2.578125, elevation 109.0 m — the same point session 08's samples got (F17), so
the full pull is describing the same place the verification did.

**Q20 closed.** All six forecast chunks were requested with `models=gfs_global`
(D16), read back out of the saved `.meta.txt` URLs rather than claimed, with no
`gfs_seamless` anywhere. Nothing looked wrong, so `gfs_seamless` was not
re-probed at LFPG, as the session prompt's A-1 directed. Note honestly what this
does and does not settle: the pin is confirmed as *used*, but F6's
value-by-value equivalence check between the two strings still has not been run
at LFPG. Stage 2 can say "this is exactly the `gfs_global` series" but not "and
`gfs_seamless` would have given the same", which is what F6 proved for stage 1.

**F23. The observation record at LFPG is good, but not as clean as EGLC's, and
the reason is interesting.**

```
reports in files           : 46,903
minute-past-hour spread    : :00 x46,805, :30 x95, :36 x1, :43 x1, :49 x1
reports with no temperature: 1
reports >15 min from any hour, dropped (D14): 97
expected hours in period   : 46,944
hours with an observation  : 46,804
hours missing              : 140 (0.30% of the period)

training 2021-03-24..2025-07-31: 38,184 expected, 38,077 usable, 107 missing (0.28%)
test     2025-08-01..2026-07-31:  8,760 expected,  8,727 usable,  33 missing (0.38%)

gap runs: 85 in total
    1 hour        75 runs      75 hours
    2-5 hours      8 runs      18 hours
    6-23 hours     1 run       15 hours
    1-7 days       1 run       32 hours
longest two: 32 hours  2022-07-22 16:00 -> 2022-07-23 23:00 UTC
             15 hours  2022-07-25 00:00 -> 2022-07-25 14:00 UTC
```

Against EGLC (F9): 140 missing hours against 44, so **0.30% against 0.09%** —
about three times as many holes, and a longest run of 32 hours against 8. Both
are still small. The full list of all 85 runs is in the notes file. Nothing was
filled (SPEC 2.2).

**The two long runs are not missing data at all — they are the station shifting
its reporting minute.** On 2022-07-23 LFPG filed all 24 of its routine reports
at `:30`, and on 2022-07-25 it filed the first 15 that way. The reports exist and
carry temperatures; D14 refuses them at 30 minutes out, so they show up in the
gap map as absent hours. Recorded plainly because a reader of the gap map would
otherwise conclude the station went dark for a day and a half, and it did not.
The rule is still applied as written (D30) — the point is only that "missing
hour" and "no report filed" are not the same thing at this airport.

**F24. Q22 closed — IEM confirms EGLC is in `GB__ASOS`, and the position in
SPEC 3.4 was already right.**

One metadata request, the same call session 08 made for France pointed at the
United Kingdom (`https://mesonet.agron.iastate.edu/geojson/network/GB__ASOS.geojson`,
HTTP 200, 63,682 bytes, 112 stations). What IEM returned for EGLC:

```
sid           = EGLC
sname         = London City
network       = GB__ASOS
coordinates   = lat 51.5053, lon 0.0553
elevation     = 5.0 m
tzname        = Europe/London
archive_begin = 1988-01-29
archive_end   = None   (still reporting)
online        = True
```

The FR__ASOS file was re-read in the same check and still carries LFPG at
49.0153 / 2.5344 / 109.0 m, matching F17.

So the guess carried in from the session 09 prompt was correct — but it is now a
checked fact rather than a probable one, which is the standard SPEC 3.4 is meant
to hold to. **SPEC 3.4 before:** `` `GB__ASOS` (unverified) ``. **After:**
`` `GB__ASOS` ``, and the note beneath the table now records both networks as
verified by real pulls instead of explaining why one was not. Nothing in the
project uses a network code — every request addresses its station by ICAO code —
so this closes a bookkeeping gap, not a data one.

**F25. The D30 count: LFPG loses THREE days at 12:00 UTC to off-hour reporting
across the whole period, not the ~12 F18 estimated.**

D30 decided what to do about these days — nothing, take the drops — but required
this session to count them and to keep them apart from days lost because no
report was filed. Observation side only; nothing was joined. This is a count of
report *timing*, not of temperature values, so it covers the test window too
without opening it.

```
calendar days in the period : 1,956
cause                                days  training   test
kept - usable 12:00 observation      1953      1589    364
LOST: only an off-hour report           3         2      1
LOST: report on the hour, no temp       0         0      0
LOST: no report in the 12:00 hour       0         0      0

total days lost at 12:00 UTC (observation side): 3 of 1,956 (0.15%)
of those, lost to CDG's off-hour reporting (D30) : 3

    2022-07-23  [training]  only report in the noon hour: 12:30
    2022-07-25  [training]  only report in the noon hour: 12:30
    2026-07-08  [test]      only report in the noon hour: 12:30
```

**Every day lost on the observation side is lost to this one cause.** There is
not a single day in five years where LFPG filed nothing at all in the 12:00 hour,
and only one report in 46,903 carries no temperature. On the observation side
CDG's record at the target hour is better than EGLC's, which lost days to missing
reports (F12, F16).

**F18's estimate was four times too high, and the reason is worth keeping.** F18
extrapolated 3 off-hour reports in a three-week sample to a 0.60% rate and about
12 lost days. The real whole-period rate is **97 reports in 46,903, or 0.207%**,
and the lost-day count is 3. Two things went wrong with the extrapolation, in
opposite directions from what was feared:

```
off-hour reports : 97 on 57 days, in 49 episodes
episodes of 5 or more reports: 2
  2022-07-23 .. 2022-07-25   39 reports over 2 days  (the F23 shift to :30)
  2026-03-07 .. 2026-03-11    5 reports over 3 days
the remaining 53 reports are scattered singles across 47 episodes
minute stamps: :30 x95, :36 x1, :43 x1
```

First, **40% of all off-hour reports come from one two-day episode** (F23), so
the rate is not the steady drizzle a three-week sample suggested. Second, and
more importantly, **off-hour reports do not cluster at midday** — that was F18's
open worry, raised because one of its three landed at noon. Spread over 57 days
and 24 hours, only 3 ever hit the noon hour, which is close to what chance alone
would give. So the noon hit in F18's sample was bad luck, not a pattern.

**Against EGLC:** 0.207% off-hour against 0.017% (F9) — still roughly twelve
times the rate, so F18's headline observation was right in direction even though
its size was wrong. But the thing that matters, days lost at the target hour, is
3 against 0. **Nothing here disturbs D30**: the drops are taken, the rule is
unchanged, and three days out of 1,956 is not worth a different pairing rule at
one airport.

**F26. Training-window value ranges, both series — sane, and plainly Celsius.**
The test window's values were not looked at.

```
forecast (GFS, training window) : n = 37,692   min = -8.5   max = 41.2   mean = 12.77 degC
observed (LFPG, training window): n = 38,077   min = -5.0   max = 39.0   mean = 13.14 degC
```

Kelvin would read about 250–310, so neither series has a unit problem, and
neither carries an absurd value. The observed maximum of 39.0 degC is real: it
is the July 2022 European heat, and the raw file shows 2022-07-19 sitting at
39 degC from 13:00 to 17:00 UTC. METAR reports whole degrees, which is why the
extremes land on round numbers.

Worth noticing for later, and **only** as an observation on the training window:
unlike EGLC (F10), the forecast's range here is *wider* than the station's at
both ends rather than narrower — it goes 3.5 degC colder and 2.2 degC warmer
than anything observed. Whether that means anything at 12:00 UTC specifically is
a question for the join session, which is exactly the mistake F13 caught F10
making: an all-hours range says little about one target hour. Not acted on.

**The pull itself, for the record.** No retry fired and no HTTP 429 appeared,
with a 3-second pause between calls (session 08 hit a rate limit at a faster
pace). No IEM network parameter was sent: stage 1 addressed EGLC by station code
alone, and a probe confirmed IEM returns identical rows with and without
`network=FR__ASOS`, so the request shape is deliberately the same as stage 1's —
only the location changed (D26). `data/raw/` now holds 76 files, 7.6 MB.

---

## 2026-08-17 — Session 10 note (what closed, and what is left)

**Q20, Q21 and Q22 are all closed** — by F22 (with the honest limit noted on
Q20), F22 again, and F24. **No open questions remain.**

The three closures needed findings, not decisions: each was a question about what
the data actually is, and the full pull answered all three. D30's required count
is F25.

**Two authorised SPEC edits and no others**, both from the session prompt's B-3:
section 3.2's "whether CDG has a forecast gap is NOT YET KNOWN" marker is
replaced by the verified answer (F22), and section 3.4's EGLC network cell drops
its "(unverified)" tag (F24). The note beneath the table was rewritten to match
the cell, because leaving it saying "EGLC's network code is not verified" would
have made SPEC contradict its own table — flagged here as slightly wider than
"one cell", so the owner can judge it.

**Nothing else changed.** No rule, date, setting, threshold or bar was touched.
Nothing was joined, built, trained or evaluated. **CDG's test year is now on disk
but has never been opened**: only its row presence and gap locations were
counted, never a temperature value, exactly as session 03b held EGLC's.

---

## 2026-08-17 — Session 11 findings (the CDG join, bias look and rehearsal)

The first modelling session for CDG, mirroring sessions 04 and 05 at EGLC. The
join, the bias look and the model all ran for real. **CDG's test year was not
touched**: the two 2026 LFPG raw chunk files were never opened, the 2025 chunk
was cut off at 2025-07-31 on load, and the script asserts that no date on or
after 2025-08-01 reached any table. Nothing was tuned, varied or chosen again —
the locked D21 recipe was applied to the second location and nothing else. The
script is `scripts/session11_model.py` and the full real output is
`notes/session-11-check-output.txt`.

**F27. The join at 12:00 UTC at CDG, and every drop reconciled in advance.**
One row per day: date, forecast temperature, observed temperature, and the
residual the model learns.

```
                                         days   kept   drop  no fc  null fc  no obs
inner-training 2021-03-24..2024-07-31   1,226  1,204     22      0       20       2
validation     2024-08-01..2025-07-31     365    365      0      0        0       0
```

**Session 10's gap map predicted these drops before anything was joined, and it
predicted them exactly.** That is the check this session existed to make, and it
is a stronger check than counting after the fact:

```
cause                                         expected   actual  verdict
the 492-hour forecast gap (F22)                     20       20  MATCHES
off-hour reports, training window (F25)              2        2  MATCHES
anything else                                        0        0  MATCHES
TOTAL days dropped                                  22       22  MATCHES
```

The two off-hour days are named, with the report the station actually filed:

```
2022-07-23  [inner-training]  only report nearest noon was 11:30, temp 25.0
2022-07-25  [inner-training]  only report nearest noon was 11:30, temp 24.0
                              both dropped by D14 (30 minutes out), per D30
```

Both reports exist and carry a temperature. D14 refuses them and D30 says the
drops are taken rather than the rule bent for one airport.

One wording note, so the two records do not look as if they disagree: F25 named
these same two days by the report **inside the 12:00 clock hour** (12:30), while
this entry names them by the report **nearest 12:00 under D14's pairing** (the
one at 11:30). On both days the station filed everything at `:30` — 10:30, 11:30,
12:30, 13:30 — so both descriptions are true of the same day, and the day is lost
either way. Nothing was filled
(SPEC 2.2). **CDG's validation year loses no day at all** — 365 of 365 — where
EGLC's lost one to a missing observation (F12).

Row counts beside EGLC's, for context: inner-training 1,204 against 1,205,
validation 365 against 364. The two airports have almost exactly the same amount
of training data, which is a coincidence worth noticing rather than a designed
result — CDG loses two days to off-hour reporting where EGLC lost one to a
missing observation, and the shared 20-day forecast gap costs both the same.

**F28. CDG's bias at 12:00 UTC is a genuinely different shape from EGLC's: the
same near-zero average, but the structure sits in the CALENDAR rather than in
the temperature.** Inner-training only; the validation year's values were not
explored and the test year not touched.

Overall, beside EGLC (F13):

```
                            EGLC       CDG
days                       1,205     1,204
mean bias degC            -0.108    +0.050
median degC               +0.000    +0.100
st dev degC                1.551     1.654
mean |bias| degC           1.172     1.248
station warmer, %           48.7      51.7
min / max degC        -7.0/+5.6 -7.7/+5.8
```

The headline similarity is real: **at CDG too there is almost no constant offset
to correct** — the mean bias is +0.050 degC, even smaller than EGLC's -0.108.
GFS is slightly harder to beat at CDG in absolute terms (mean |bias| 1.248
against 1.172), which is the first sign that the second airport is a harder
problem than the first.

Against forecast temperature, the picture diverges:

```
forecast band (degC)     days  mean bias   st dev  mean |bias|  EGLC mean bias
-10 to 0                    2     +1.800    0.141        1.800               -
0 to 5                     55     -0.687    1.659        1.422          -0.049
5 to 10                   218     +0.223    1.514        1.092          +0.361
10 to 15                  293     +0.339    1.462        1.122          +0.387
15 to 20                  269     +0.320    1.706        1.312          -0.287
20 to 25                  229     -0.142    1.733        1.314          -0.746
25 to 45                  138     -0.772    1.638        1.452          -1.201

coldest 10%  n=120  forecast  -0.9 to  +7.0 degC  mean bias -0.351 (EGLC +0.097)
warmest 10%  n=120  forecast +25.6 to +39.6 degC  mean bias -0.784 (EGLC -1.155)
```

**The warm-end bias F13 found at EGLC is present at CDG but weaker** — -0.772 in
the top band against EGLC's -1.201, and -0.784 in the warmest tenth against
EGLC's -1.155. **The cold end, which was unbiased at EGLC, is biased at CDG**:
-0.687 in the 0-5 band and -0.351 across the coldest tenth, meaning GFS runs
*too warm* on CDG's coldest days as well as its hottest. That is a plausible
inland effect — a continental site gets colder clear nights and mornings than a
coarse grid cell sitting near a large city does — but this session measured it
and did not test that explanation.

By season, the difference is larger still:

```
season         days  mean bias   st dev  mean |bias|  EGLC bias  EGLC |bias|
winter DJF      251     -0.092    1.595        1.182     +0.356        1.065
spring MAM      345     +0.614    1.433        1.203     -0.061        1.203
summer JJA      335     -0.056    1.940        1.510     -0.549        1.437
autumn SON      273     -0.401    1.379        1.044     -0.052        0.907
```

At EGLC the seasonal signal was small and the temperature signal carried the
bias. **At CDG it is the other way round**: spring runs +0.614 degC (the station
warmer than GFS) and autumn -0.401, a swing of over one degree through the year,
while summer's average is near zero even though summer has by far the widest
spread (st dev 1.940). Month by month the turn is sharp — June +0.704, July
-0.125, August -0.948.

**So the recipe is being asked to learn a different thing at the two airports,
using the same three features.** That is exactly what stage 2 was for, and the
model's own feature importances agree with this reading (F29).

**F29. The rehearsal: the correction beats all four references at CDG, by a
smaller margin than at EGLC, and in a different seasonal pattern.**

Model: the locked D21 recipe, fitted on CDG's 1,204 inner-training rows only.
PART 0 of the output proves the method was reused rather than re-chosen — it
reads `scripts/session05_model.py` and compares it with this session's script:
**0 model settings differ, 0 constants differ**, and `all_days`, `year_fraction`,
`features`, `mae`, `describe` and `climatology_from_inner` are character-
identical. The two loaders differ, and their full diffs are printed: the station
code in the file names, the docstring naming LFPG's on-the-hour reporting, and a
bookkeeping record of report offsets used only by the drop reconciliation. Two
consecutive runs produced identical output apart from the clock time in the
header.

All five methods scored on the same 365 validation days — CDG loses no day at
all, where EGLC scored 363:

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.426     -0.424      1.900        7.20
Persistence                2.523     -0.014      3.278       10.00
Climatology                3.293     -0.298      4.163       13.87
Mean-bias reference        1.435     -0.475      1.912        7.25
ML-corrected               1.377     -0.465      1.863        7.87
```

Verdicts:

```
vs Raw GFS              YES   1.377 against 1.426  ->  0.050 degC better (3.5%)
vs Persistence          YES   1.377 against 2.523  ->  1.147 degC better (45.4%)
vs Mean-bias reference  YES   1.377 against 1.435  ->  0.058 degC better (4.1%)
vs Climatology          YES   1.377 against 3.293  ->  1.916 degC better (58.2%)
```

**This is a validation rehearsal, not the frozen bar (SPEC 5.3, 5.0).** CDG's
bar is judged once, on CDG's own sealed test year, in a later session. A good
number here means the recipe travels well enough to be worth that single look.
**It does not mean stage 2 has passed.**

Four things the numbers say, read honestly:

1. **The recipe travels.** Applied unchanged at a location 328 km away and 104 m
   higher, with a different bias shape, it still beats every reference. Nothing
   about it was adapted for CDG, and nothing needed to be.
2. **The margin over raw GFS is smaller than at EGLC: 3.5% against 6.0%**
   (0.050 degC against 0.074). Both are small wins on a forecast that is already
   good. CDG is the harder problem on every measure — raw GFS 1.426 against
   1.239, persistence 2.523 against 2.226, climatology 3.293 against 2.865 — so
   the correction is working on a noisier target and keeping less of it.
3. **The mean-bias reference is WORSE than raw GFS at CDG (1.435 against
   1.426).** This is new: at EGLC the constant offset helped slightly. At CDG the
   available constant is +0.050 degC and applying it makes things very slightly
   worse, which is what "there is no constant worth taking" looks like in
   practice. It makes the model's 4.1% win over that reference the cleanest
   statement yet that the correction is learning structure — there is no offset
   here for it to be quietly finding instead.
4. **The seasonal pattern is different, and flatter.** At EGLC the win was
   essentially a summer win. At CDG it is spread:

```
season         days   raw GFS   ML-corr   CDG chg   EGLC chg
winter DJF       90     1.512     1.537    +0.025     +0.087
spring MAM       92     1.221     1.164    -0.057     -0.015
summer JJA       92     1.445     1.323    -0.122     -0.321
autumn SON       91     1.531     1.487    -0.044     -0.049
```

   ("chg" is corrected MAE minus raw GFS MAE. Negative is better than raw GFS.)
   The correction helps in **three seasons of four at both airports**, and at
   both the one season it hurts is **winter** — by less at CDG (+0.025) than at
   EGLC (+0.087). Summer still carries the most at CDG but nothing like as much.
   Note that CDG's validation year was hardest for raw GFS in **autumn** (1.531),
   not summer, which is not where the correction is strongest.

Day by day, the correction was closer to the truth than raw GFS on **202 of 365
days (55.3%)**, against 60.9% for EGLC's sealed test (F16). So it nudges the
right way slightly more often than not, and slightly less reliably than at EGLC.

**Feature importances, and they back up F28:**

```
feature             EGLC gain %   CDG gain %  EGLC splits   CDG splits
forecast_temp_c           44.3%        35.9%        1,614        1,558
season_sin                26.7%        39.9%        1,337        1,444
season_cos                29.0%        24.2%        1,249        1,198
```

At EGLC forecast temperature was the single largest source of gain. **At CDG
`season_sin` overtakes it.** The model, given the same three features and no
guidance, leant on the calendar at the airport whose bias lives in the calendar
and on the temperature at the airport whose bias lives in the temperature. That
is a coherent independent confirmation of F28 from a completely different
direction, and it is the most interesting thing in this session.

The corrections applied were modest and slightly warm-leaning: mean +0.041 degC,
standard deviation 0.751, range -1.7 to +2.3 — the same gentle nudge session 05
made at EGLC (mean -0.057, st dev 0.720, range -1.8 to +1.8), pointed the other
way, which follows from CDG's mean bias being positive where EGLC's was
negative.

For the record, in-sample MAE on CDG inner-training was 0.945 degC against raw
GFS's 1.248 (EGLC: 0.879). A model always looks better on the data it was fitted
to; the figure proves nothing and is here only so it is not a surprise later.

**How each reference was built, for the record** — identical to session 05,
fitted on CDG inner-training only:
- **Raw GFS** — the forecast value itself, uncorrected.
- **Persistence** — the previous calendar day's 12:00 UTC observation. Past
  values only (SPEC 2.1d).
- **Climatology** — the seasonal average of the *observed* temperature for that
  position in the year, over every CDG inner-training observation within 7.5
  days of it, measured around the circle (SPEC 2.1c). Between 30 and 61 days sit
  behind each value, 49.5 on average — the same coverage as at EGLC.
- **Mean-bias reference** — the forecast plus +0.0504 degC, that figure being the
  mean CDG inner-training bias and nothing else.
- **ML-corrected** — the forecast plus the model's predicted residual.

Nothing was fitted on the validation year: not the model, not the climatology,
not the mean bias, not any encoding. **No SPEC edit was made and none was
authorised.**

---

## 2026-08-17 — Open question raised by session 11 (not acted on)

**Q23. CDG has no written test lock, and the D21.5 refit question has to be
answered for it.** D21 is written specifically for EGLC — D21.1 names London
City and its coordinates, and D21.5 fixes the refit on the full training window.
D26 says stage 2 reuses everything but the location, so the substance carries
over, but there is no CDG entry anyone can point at that says "this is what the
sealed-test session will run", which is the whole job D21 did for stage 1. Two
things need the owner's word before CDG's test year is opened:
- **Does the lock get written out for CDG**, as a D21-equivalent entry naming
  LFPG, or is D26-plus-D21 considered sufficient on its own? The stage 1 pattern
  was to write it down first and execute it second, precisely so no choice is
  made with the test year open (D21.11).
- **Is CDG's test model refitted on the full D13 training window** (inner-
  training plus the validation year recombined, as D21.5 did for EGLC)? The same
  reasoning applies and the same consequence follows — the tested model would be
  the same recipe on about 20% more data, so the test number will not match the
  1.377 rehearsal figure and should not be expected to. Recorded here so it is
  decided deliberately rather than inherited by silence.

---

## 2026-08-17 — Session 12: THE CDG METHOD LOCK

No model was built, run or refitted this session, no data was loaded, and
**CDG's test year was not touched**. This section is the written lock for stage
2, mirroring what D21 did for stage 1, plus the correspondence check that proves
it is D21 with the location swapped and nothing else.

**D31. CDG's method is LOCKED. This entry fully specifies what CDG's
sealed-test session will run. It closes Q23.**

This is **D21 with the airport swapped and nothing else touched.** Every
methodological choice below — the model, its settings, the features, the target
hour, the pairing rule, the missing-data rule, the references, the bar, and the
one-look rule — is the same choice D21 made, not a new one. That is required by
D26, which says stage 2 changes **only the location**: if CDG's result differs
from EGLC's, the location must be the only thing that can explain it.

Why it is written out separately rather than by pointing at D21: D21 names
London City throughout, so CDG's test session would otherwise have to reach back
to an EGLC-named record and translate it while the test year was open. The whole
value of a lock is that the executing session decides nothing (D21.11). A
translation is a decision. So the translation is done here, now, with CDG's test
year still unseen, and the test session executes this record and reports.

**D31.1 — Target.** The temperature at **12:00 UTC** at **Paris Charles de
Gaulle (IATA CDG, ICAO LFPG)**, the station at latitude 49.0153, longitude
2.5344, elevation 109 m — IEM's own position, per SPEC 3.4 and F17. The forecast
comes from the Open-Meteo grid point that position maps to: latitude 49.027008,
longitude 2.578125, elevation 109 m, 3.44 km from the airport (SPEC 3.4, F17).
One row per day. The hour is 12:00 UTC, the same hour as stage 1, on purpose
(SPEC 4.1, D26).

**D31.2 — What the model predicts.** The **residual**: observed minus forecast
(SPEC 4.2). The corrected forecast is the GFS forecast plus the predicted
residual. The model never predicts temperature directly. Identical to D21.2.

**D31.3 — Features.** The D19 minimal set, exactly three:
```
forecast_temp_c   the GFS forecast temperature for that day at 12:00 UTC
season_sin        sin(2 * pi * year_fraction(date))
season_cos        cos(2 * pi * year_fraction(date))
```
where `year_fraction` is `(day_of_year - 1) / 365`, or `/ 366` in a leap year.
No hour-of-day feature (the hour is fixed, so it carries no information). No
recent-observation feature, even though SPEC 2.1d would allow one — see D19 for
why. Identical to D21.3.

**D31.4 — Model and settings.** LightGBM gradient-boosted trees (SPEC 4.4,
D12), with exactly the session 05 settings, unchanged:
```
objective=regression_l1   (absolute error, D20)   n_estimators=300
learning_rate=0.05        num_leaves=15           min_child_samples=40
subsample=1.0             colsample_bytree=1.0    reg_alpha=0.0
reg_lambda=0.0            random_state=42         n_jobs=1
deterministic=True        force_row_wise=True     verbose=-1
```
Nothing is tuned, searched or varied in the test session. Library versions are
pinned in `requirements.txt` (D24): python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0. Identical to D21.4. Session 11 already ran this exact
configuration at CDG and its PART 0 proved it setting by setting against
`scripts/session05_model.py` — 0 settings differ, 0 constants differ (F29).

**D31.5 — Training data for the test: the FULL D13 training window,
2021-03-24 to 2025-07-31, at LFPG.** That is CDG's inner-training **and** CDG's
validation year recombined into one training set.
- Reason: the same reason D21.5 gave. The D18 split existed so the method could
  be rehearsed without touching the test year. The method is locked, so
  validation has finished its job, and holding a year back would only throw away
  real training data. Refitting on all non-test data before the single test is
  the standard move — and it is what stage 1 did, so doing anything else here
  would be a second difference between the two airports on top of the location.
- Everything fitted is fitted on this window and nothing else: the model, the
  climatology baseline (SPEC 2.1c) and the mean-bias figure.
- **Note the consequence, so it is not a surprise:** the model that is tested is
  **not** the model measured in session 11. It is the same recipe fitted on about
  20% more days, including one more full cycle of seasons. Session 11 fitted
  1,204 inner-training rows; the test model fits those plus CDG's 365 validation
  rows (F27). **The test number will not match session 11's 1.377 rehearsal
  figure and should not be expected to.** At EGLC the equivalent move moved the
  number by 0.125 degC (F16), and most of that was the weather rather than the
  extra data.

**D31.6 — Test data: LFPG, 2025-08-01 to 2026-07-31 (D13), and nothing after
it.** Data after 2026-07-31 is not used, keeping the test set exactly one
calendar year. This is CDG's own test year: the dates are the same as EGLC's but
the data is a different airport's, and it has never been looked at.

What "opened for the first time" means precisely here, because it is not quite
the same sentence D21.6 could write. Two files carry the test year:
```
openmeteo_previousruns_gfs_global_LFPG_2026-01-01_2026-07-31.json  never read
iem_asos_LFPG_2026-01-01_2026-07-31_routine.csv                    never read
openmeteo_previousruns_gfs_global_LFPG_2025-01-01_2025-12-31.json  read, but
iem_asos_LFPG_2025-01-01_2025-12-31_routine.csv                    cut at
                                                                   2025-07-31
```
The two 2026 LFPG chunk files have never been opened by any session. The 2025
chunks have been read, but every session so far cut them off at 2025-07-31 on
load and asserted that no date on or after 2025-08-01 reached any table (F27).
The test session reads them to their end. Session 10 counted row presence, gap
positions and report timing across the whole period including the test window,
but never a temperature value from it (F22, F23, F25) — a structural count, not
a look at the data.

**D31.7 — Pairing and missing data.** The D14 rule, applied exactly as written at
EGLC: the routine report is the truth observation, each 12:00 forecast is paired
with the report nearest that hour, and if no report falls within 15 minutes of
the hour the day is dropped and counted. Drop, count, report — nothing filled,
ever (SPEC 2.2). The drop counts for both the training window and the test year
are part of the output.

The one location fact inside this: **LFPG reports on the hour (`:00`)**, where
EGLC reports at `:50` (SPEC 3.4, F18). So the rule pairs 12:00 with the 12:00
report — an exact match, no offset — where at EGLC it paired 12:00 with the
11:50 report. **The rule is not adapted; it simply fits CDG better.** Where CDG
files its routine report off the hour, the day is dropped and taken, not
rescued: that is D30, which refused to widen the tolerance or fall back to the
`:30` "special" stream for one airport, because a different pairing rule at
stage 2 would break the "only the location changed" claim.

**What the gap map says the test year should cost, written down before the
look.** From session 10, which mapped every hour without reading a value:
```
forecast-gap days in CDG's test year                            0   (F22)
days lost to an off-hour-only report in CDG's test year         1   (F25)
    2026-07-08  -- the only routine report in the noon hour was 12:30
days lost to no report at all in the noon hour                  0   (F25)
days lost to a report on the hour carrying no temperature       0   (F25)
expected paired rows                                          364 of 365
```
Scoring is then expected to lose one further day, 2026-07-09, because
persistence needs the previous day's observation and 2026-07-08 is the day that
is missing — the same arithmetic that took EGLC's test from 364 paired rows to
363 scored days (F16). So **363 scored days is the expectation, not a
requirement.** The test session reports the **actual** counts and reconciles
them against this table. A count that will not reconcile is a D31.11 stop
signal, not something to explain away.

**D31.8 — The four references. Anything that has to be *fitted* is fitted on
CDG's training window only.** Raw GFS and persistence are fitted on nothing —
they are just values. Climatology and the mean-bias figure are fitted, and both
come from LFPG's D13 training window (SPEC 2.1c).
- **Raw GFS** — the forecast value itself, uncorrected. *Part of the bar.*
- **Persistence** — the previous calendar day's 12:00 UTC observation at LFPG.
  Past values only (SPEC 2.1d). *Part of the bar.* Note that for the first test
  day, 2025-08-01, "yesterday" is 2025-07-31, which sits in the training window.
  That is a past observation, so it is legal and it will be used; it is written
  down here so it is not mistaken for leakage later. Identical to D21.8's note.
- **Climatology** — the seasonal average of the *observed* temperature at LFPG
  for that position in the year, averaged over every **CDG training-window**
  observation within 7.5 days of it, measured around the circle so late December
  and early January are neighbours (SPEC 2.1c). *Informative only.*
- **Mean-bias reference** — the forecast plus one constant: the mean **CDG
  training-window** bias. *Informative only* (SPEC 5.2, D23). Worth carrying
  forward from F29: on CDG's validation year this reference was **worse** than
  raw GFS, because the constant available is near zero and applying it hurt
  slightly. If that repeats on the test year it is not a fault — it is what "no
  constant offset worth taking" looks like.

All five methods — the four above plus the corrected forecast — are scored on
the **same set of days**, the days where every method has a value.

**D31.9 — The metric and the bar.** Mean absolute error in degrees Celsius
(SPEC 5.1). **Stage 2 passes if the corrected forecast has a lower MAE than both
raw GFS and persistence over CDG's test year.** No numeric margin — the bar is
qualitative and stays that way (D22, SPEC 5.3). Climatology and the mean-bias
reference are reported but do not decide pass or fail. The margin is reported
prominently alongside the verdict, so a technical pass by a hair reads as what it
is (D22).

**The bar is judged once per airport, on that airport's own data (SPEC 5.0).**
EGLC's pass does not excuse a CDG failure, and a CDG result does not re-open
EGLC's. Stage 1's 16.3% is not a target CDG has to reach and not a number CDG is
measured against; CDG is measured against CDG's own raw GFS and CDG's own
persistence, and nothing else.

**D31.10 — One look, and the result stands.** CDG's test year is opened once,
this method is run once, and whatever comes out is reported straight — pass or
fail, with the seasonal breakdown and the drop counts. A failure is an honest
finding (SPEC 2.4), not something to fix by trying again. If the result
disappoints, the response is a new decision logged here by the owner, never a
quiet re-run. Identical to D21.10.

Read this one plainly, because stage 2 is where it bites hardest. CDG's
rehearsal margin was 3.5% (F29), half of EGLC's 6.0%, on a harder problem. A
smaller margin is easier to lose. **A CDG failure is a real possible outcome of
the next session, and it is an outcome the project reports rather than avoids.**
It would be a finding about how far the recipe travels, which is exactly the
question stage 2 was opened to ask (D26).

**D31.11 — Deviation is a stop signal.** If CDG's test session finds any reason
to depart from this record — a setting that does not fit, a missing file, a count
that will not reconcile against D31.7, a tempting small improvement — it **stops
and raises it with the owner**. It does not decide on the fly with the test year
open. Any change to the above is a new DECISIONS entry made deliberately, not an
adjustment made mid-run. Identical to D21.11.

---

**The D21 ↔ D31 correspondence check.** This is the verification the session
prompt required: every D21 sub-point set beside its D31 counterpart, to show that
the only differences are the location and the facts that follow from it.

```
point  subject                D21 (EGLC)                D31 (LFPG)                differs?
.1     target hour            12:00 UTC                 12:00 UTC                 same
.1     airport                London City / EGLC        Paris CDG / LFPG          LOCATION
.1     station position       51.505 / 0.055            49.0153 / 2.5344 / 109 m  LOCATION
.1     grid point             (not stated in D21)       49.027008 / 2.578125      LOCATION
.1     row granularity        one row per day           one row per day           same
.2     what is predicted      residual = obs - fcst     residual = obs - fcst     same
.2     how corrected is made  fcst + predicted resid    fcst + predicted resid    same
.3     features               3: fcst temp, sin, cos    3: fcst temp, sin, cos    same
.3     year_fraction          (doy-1)/365 or /366       (doy-1)/365 or /366       same
.3     excluded features      no hour, no recent obs    no hour, no recent obs    same
.4     library and model      LightGBM GBDT             LightGBM GBDT             same
.4     objective              regression_l1             regression_l1             same
.4     n_estimators           300                       300                       same
.4     learning_rate          0.05                      0.05                      same
.4     num_leaves             15                        15                        same
.4     min_child_samples      40                        40                        same
.4     subsample              1.0                       1.0                       same
.4     colsample_bytree       1.0                       1.0                       same
.4     reg_alpha / reg_lambda 0.0 / 0.0                 0.0 / 0.0                 same
.4     random_state           42                        42                        same
.4     n_jobs                 1                         1                         same
.4     deterministic          True                      True                      same
.4     force_row_wise         True                      True                      same
.4     verbose                -1                        -1                        same
.4     pinned versions        py 3.12.2, np 2.5.2,      py 3.12.2, np 2.5.2,      same
                              lightgbm 4.7.0            lightgbm 4.7.0
.4     tuning allowed         none                      none                      same
.5     training window        2021-03-24..2025-07-31    2021-03-24..2025-07-31    same
.5     refit on inner+valid   yes                       yes                       same
.5     what else is fitted    model, climatology,       model, climatology,       same
                              mean bias -- all on it    mean bias -- all on it
.5     rows fitted on         1,569 (F16)               1,569 expected (F27:      LOCATION
                                                        1,204 + 365)
.5     mismatch warning       test != validation no.    test != 1.377 rehearsal   LOCATION
.6     test window            2025-08-01..2026-07-31    2025-08-01..2026-07-31    same
.6     nothing used after     2026-07-31                2026-07-31                same
.6     files opened first     the two 2026 EGLC         the two 2026 LFPG         LOCATION
       time                   chunks                    chunks
.7     pairing rule           D14, nearest report,      D14, nearest report,      same
                              15-minute tolerance       15-minute tolerance
.7     report minute          :50 -> 10-min offset      :00 -> exact match        LOCATION
.7     missing data           drop, count, report,      drop, count, report,      same
                              never fill (SPEC 2.2)     never fill (SPEC 2.2)
.7     off-hour reports       dropped by D14            dropped by D14, taken     same rule,
                                                        not rescued (D30)         LOCATION
                                                                                  consequence
.7     expected fcst-gap days 0 in test year (F8)       0 in test year (F22)      same
.7     expected obs-loss days (not predicted in         1: 2026-07-08 (F25)       LOCATION
                              advance; 1 found, F16)
.7     drop counts reported   training and test         training and test         same
.8     reference 1            raw GFS, in the bar       raw GFS, in the bar       same
.8     reference 2            persistence, in the bar   persistence, in the bar   same
.8     persistence's source   previous day's 12:00 obs  previous day's 12:00 obs  same
.8     first-day note         2025-07-31 is training,   2025-07-31 is training,   same
                              legal, will be used       legal, will be used
.8     reference 3            climatology, +-7.5 days   climatology, +-7.5 days   same
                              circular, informative     circular, informative
.8     reference 4            mean-bias, informative    mean-bias, informative    same
.8     what fitted refs use   training window only      training window only      same
                              (SPEC 2.1c)               (SPEC 2.1c)
.8     scoring set            same days for all five    same days for all five    same
.9     metric                 MAE in degC (SPEC 5.1)    MAE in degC (SPEC 5.1)    same
.9     the bar                beat raw GFS AND          beat raw GFS AND          same
                              persistence               persistence
.9     numeric margin         none, qualitative (D22)   none, qualitative (D22)   same
.9     margin reported        yes, prominently          yes, prominently          same
.9     who decides pass/fail  raw GFS + persistence     raw GFS + persistence     same
.10    number of looks        one                       one                       same
.10    number of runs         one                       one                       same
.10    failure handling       reported straight, not    reported straight, not    same
                              re-run
.11    deviation handling     stop and raise with       stop and raise with       same
                              the owner                 the owner
```

**Verdict of the check: no methodological choice differs.** Every row marked
`LOCATION` is one of four things, and nothing else appears in that column:
1. **which airport it is** — its name, ICAO code, station position and grid
   point (D31.1);
2. **which files hold its data** (D31.6);
3. **when the station files its routine report** — `:00` at LFPG against `:50` at
   EGLC — which changes the pairing *offset* the D14 rule produces, not the rule
   (D31.7);
4. **how many rows and drops follow from that airport's own record** — 1,569
   expected training rows, 1 expected test-year drop (D31.5, D31.7).

Every setting, every date, every feature, every reference, the metric, the bar,
the one-look rule and the stop-signal rule are the same in both entries. Nothing
was added to D31 that D21 does not require, and nothing D21 requires was left
out of D31.

**One difference inside the `LOCATION` rows worth naming rather than hiding.**
D21.1 gives EGLC's position as 51.505 / 0.055, which is the approximate figure
stage 1's pulls were made with. D31.1 gives LFPG's as 49.0153 / 2.5344 / 109 m,
which is **IEM's own metadata** (F17), because session 08 pulled that metadata
and used it in preference to the prompt's approximate figure. So the two
coordinates do not come from the same kind of source. This is a difference in
where a number came from, not in method: each airport's pulls were made at the
position that airport's session used, every file records the exact query (SPEC
2.3), and the grid point Open-Meteo returned is fixed and recorded either way. It
changes nothing in D31 and needs no action; it is written down so nobody later
reads "only the location changed" as also meaning "and both positions were
sourced the same way".

Three places where D31 says **more** than D21 did, all of them recording facts
that already exist rather than making choices:
- **D31.7 predicts the test-year drops before the look** (0 forecast-gap days, 1
  off-hour day, 363 scored days expected). D21 could not do this: EGLC's gap map
  came from session 03b, but nobody had computed the day-level consequence for
  the test year in advance, so F16 reported one dropped day after the fact. CDG's
  session 10 gap map makes the prediction possible, and F27 already showed the
  same prediction landing exactly on the training side. **A prediction made
  before the look is a stronger check than a count made after it**, which is why
  it is written here rather than left to the test session.
- **D31.6 spells out what "opened for the first time" means** for the 2025 chunk
  files, which have been read with a cut-off. D21 did not need this sentence
  because it was writing about the same situation without naming it.
- **D31.9 and D31.10 add a plain warning** that CDG's rehearsal margin was half
  EGLC's, so a failure is a real possible outcome. This adds no requirement and
  changes no threshold; it is written so a disappointing result is met with a
  record that expected the possibility, rather than with a search for a reason.

---

## 2026-08-17 — Session 12 note (nothing measured, nothing opened)

This session ran no code, loaded no data and produced no numbers of its own, so
there is no F-entry. What it produced is D31, the correspondence check above,
and the STATUS update.

**Q23 is closed by D31**, and both halves of it are answered:
- **Does the lock get written out for CDG?** Yes. D31 is the D21-equivalent,
  written before the test year is opened, exactly as the stage 1 pattern did.
  D26-plus-D21 was judged not sufficient on its own, because it would leave the
  test session translating an EGLC-named record with the test year open, and
  translation is a decision (D21.11).
- **Is CDG's test model refitted on the full D13 training window?** Yes —
  D31.5, matching D21.5, with the consequence stated in advance: the test number
  will not match session 11's 1.377 and should not be expected to.

**No open questions remain.**

**Nothing was opened.** CDG's test year was not loaded, read, printed, averaged
or fitted on. No model was run, fitted or refitted. No file in `data/raw/` was
read this session at all — the file names in D31.6 come from listing the
directory, not from opening the files. `scripts/` gained nothing: there was
nothing to run.

**No SPEC edit was made and none was authorised.** D31 fixes no rule that SPEC
does not already carry; it names, for one airport, what SPEC already says
per-airport.

**One honest limit carried forward, not a new question.** Q20 is closed, but its
closing note stands and applies to the test session's write-up: `gfs_global` is
confirmed as the string every LFPG chunk was pulled with, while F6's
value-by-value comparison against `gfs_seamless` was never re-run at LFPG. So
stage 2 can say "this is exactly the `gfs_global` series" but not "and
`gfs_seamless` would have given the same", which stage 1 can. Recorded here so
the test session does not accidentally claim the stronger version.

---

## 2026-08-18 — Session 13: THE CDG SEALED-TEST RESULT (stage 2 is decided)

CDG's test year was opened for the first and only time. The method locked in
D31 was executed and nothing was decided, tuned, swapped or re-run. This
section is the stage 2 result of record. The script is
`scripts/session13_test.py` and the full real output is
`notes/session-13-check-output.txt`.

**F30. STAGE 2 PASSES. At CDG the corrected forecast beats both raw GFS and
persistence on the held-out test year. The recipe travels.**

The verdict first, because that is what the session was for:

```
                        MAE degC   part of bar?
Raw GFS                    1.396   YES
Persistence                2.300   YES
Climatology                3.774   no  (informative)
Mean-bias reference        1.389   no  (informative)
ML-corrected               1.208   the claim

vs Raw GFS       BEATEN   1.208 against 1.396  ->  0.188 degC better (13.5%)
vs Persistence   BEATEN   1.208 against 2.300  ->  1.092 degC better (47.5%)
```

**Stage 2 passes on the frozen bar (SPEC 5.3, 5.0, D31.9): the corrected
forecast has a lower MAE than both raw GFS and persistence over 2025-08-01 to
2026-07-31 at LFPG.** The margin is stated prominently because D22 requires it —
this is not a pass by a hair. It is 0.188 degC, a 13.5% cut in the average error
against raw GFS.

The full table, all five methods on the same 363 days:

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.396     -0.517      1.847        8.70
Persistence                2.300     +0.008      3.097       12.00
Climatology                3.774     +0.918      4.822       14.60
Mean-bias reference        1.389     -0.457      1.831        8.64
ML-corrected               1.208     -0.401      1.650        7.60
```

**It beats the mean-bias reference too, by 13.0% (1.208 against 1.389).** That
is the comparison that matters most for the claim (D23): the mean-bias reference
is the forecast plus one constant, with no learning in it. The constant itself is
tiny — the mean training-window bias at CDG is **-0.0600 degC** — so there was
almost no offset available to take, exactly as F28 found on the training side.
Beating it by 13.0% means the model found real structure in CDG's bias, not an
offset.

**Day by day, not just on average.** The correction was closer to the truth than
raw GFS on **213 of 363 days (58.7%)** and further away on 150 (41.3%), with no
day where it made no difference. So the win is spread across the year rather than
carried by a handful of days, but it is far from every day — the model is nudging
a good forecast, and about two days in five it nudges the wrong way. EGLC's
sealed test was 60.9% (F16), so the two airports are close on this.

**Per season, the correction helped in three of the four:**

```
season         days   raw GFS   ML-corr    change   persistence
winter DJF       90     1.188     1.198    +0.010         2.200
spring MAM       92     1.239     1.135    -0.104         2.196
summer JJA       90     1.924     1.397    -0.528         2.767
autumn SON       91     1.238     1.104    -0.134         2.044
```
("change" is corrected MAE minus raw GFS MAE. Negative means better than raw
GFS.) Winter is the one season it makes worse, and by 0.010 degC, which is
nothing — smaller than CDG's own rehearsal loss (+0.025, F29) and much smaller
than EGLC's rehearsal loss (+0.087, F15). Winter has been the losing season at
both airports in every run so far. Summer carries the result: 0.528 degC better
on 90 days.

**The test-year drop count, and the reconciliation D31.7 existed for.** D31.7
wrote the expected drops down in session 12, from session 10's gap map, before
CDG's test year was opened. Every line matched:

```
cause                                            predicted  actual  verdict
forecast-gap days in the test year (F22)                 0       0  MATCHES
days lost to an off-hour-only report (F25)               1       1  MATCHES
days lost to no report at all in the noon hour (F25)     0       0  MATCHES
days lost to a report on the hour with no temp (F25)     0       0  MATCHES
paired rows expected                                   364     364  MATCHES
the off-hour day is the one D31.7 named         2026-07-08  2026-07-08  MATCHES
```

Scoring then loses one more day — 2026-07-09 — because persistence needs the
previous day's observation and 2026-07-08 is the day that is missing. So all five
methods are scored on **363 days**, which is what D31.7 predicted. Nothing was
filled (SPEC 2.2).

**A prediction made before the look landed exactly**, which is a stronger check
than a count made after it. D21 could not make this check for EGLC; CDG's session
10 gap map made it possible, and it has now paid off on both the training side
(F27) and the test side.

The training-window counts reconcile exactly against session 11's published
figures, which is the check that the harness has not drifted (D31.11): 1,204
inner-training rows plus 365 validation rows equals the 1,569 rows this session
fitted on, out of 1,591 calendar days.

**What LFPG actually filed on 2026-07-08, written out because two records
describe it differently.** The station filed at 11:00 and at 12:30 — no report at
all between 11:30 and 12:29:

```
routine report at 12:00-60 min, temp 31.0  -> belongs to the 11:00 hour
routine report at 12:00+30 min, temp 32.0  -> in the noon clock hour but 30
                                              minutes out, dropped by D14
```

So under D14's nearest-hour pairing there was **no** report in the noon bucket,
while under F25's clock-hour framing there **was** one, at 12:30. Both are true
of the same day, the day is lost either way, and the day is counted against
F25's framing because that is the framing D31.7's prediction was built from. This
is the same double description F27 had to reconcile at 2022-07-23 and
2022-07-25, and it is written out again here so nobody later reads the two
entries as disagreeing.

**The test number against session 11's rehearsal number.** D31.5 said in advance
that these would differ and should not be expected to match. They do differ, and
in the same direction the equivalent EGLC comparison moved (F16):

```
method                  s11 valid   s13 test  difference
Raw GFS                     1.426      1.396      -0.030
Persistence                 2.523      2.300      -0.223
Climatology                 3.293      3.774      +0.481
Mean-bias reference         1.435      1.389      -0.046
ML-corrected                1.377      1.208      -0.169
days scored                   365        363

margin over raw GFS:  validation +0.050 (3.5%)   test +0.188 (13.5%)
```

(One small bookkeeping note so the two records do not look as if they disagree:
F29 reported the validation margin as 0.050 degC / 3.5% from unrounded figures,
while session 13's side-by-side recomputes it as 0.049 degC / 3.4% from the
published three-decimal MAEs. It is a rounding artefact of quoting rounded
numbers, not a different measurement.)

**Read honestly, the test margin is bigger than the rehearsal margin for two
reasons, and only one of them is the model. It is the same reading F16 gave for
EGLC, and that similarity is itself the thing worth noticing.**

1. **The model is fitted on more data.** D31.5 recombined the validation year
   into training, so the tested model saw 1,569 days instead of 1,204 — about 30%
   more rows and one more full cycle of seasons. That was expected to help
   slightly.
2. **The test year suited the correction better.** Raw GFS was slightly easier
   overall (1.396 against 1.426), but the difficulty sat in a different place. In
   the test year raw GFS's summer MAE at CDG was **1.924**, against 1.445 in the
   validation year — a much harder summer for GFS — and summer is where the
   correction works best. Meanwhile test-year winter was easier for raw GFS
   (1.188 against 1.512), so the season the correction loses in had less ground
   to lose.

**And here is the caveat that matters most, stated plainly.** That is *exactly*
the pattern F16 described at EGLC: a harder summer and an easier winter in the
test year than in the validation year, both flattering the correction. The two
airports are 328 km apart and were tested on **the same twelve months**, so this
is not two independent pieces of evidence that the method does better than its
rehearsals suggest. It is much more likely one weather year that happened to suit
the method, seen twice. The honest summary is: **the method won at both airports
on both years — by 6.0% and 3.5% on the two rehearsal years, and by 16.3% and
13.5% on one shared test year — and the gap between those two pairs of numbers is
mostly what the weather did.**

**Stage 2 beside stage 1, which is the question stage 2 was opened to ask:**

```
                        EGLC       CDG   difference
Raw GFS                1.242     1.396       +0.154
Persistence            2.096     2.300       +0.204
Climatology            2.972     3.774       +0.802
Mean-bias reference    1.234     1.389       +0.155
ML-corrected           1.040     1.208       +0.168
days scored              363       363

margin over raw GFS   +0.202 (16.3%)   +0.188 (13.5%)
margin over persist.  +1.056 (50.4%)   +1.092 (47.5%)
seasons helped               4 of 4          3 of 4
days closer than raw   221/363 (60.9%)  213/363 (58.7%)
```

**CDG is the harder problem on every reference**, exactly as its rehearsal said
it would be — raw GFS, persistence and climatology are all worse there than at
EGLC. The correction is worse there too, in absolute terms. But **the proportion
of the error it removes is very nearly the same**: 13.5% against 16.3% on raw
GFS, 47.5% against 50.4% on persistence. That is the result stage 2 was for. The
recipe was not rebuilt, retuned or adapted for the second airport — only the
location changed (D26) — and it removed a similar share of a larger error.

**Two further honest notes.**

- **Climatology ran 0.918 degC cold on CDG's test year**, against -0.298 on its
  validation year (F29). As at EGLC (+0.773, F16), that says the test year was
  warmer at 12:00 UTC than the 2021–2025 training average for the same dates. It
  is not a fault in the baseline; it is a fact about the year, and it is the same
  fact at both airports, which fits the "one shared weather year" caveat above.
- **Nothing about the residual scatter changed.** The corrections applied were
  modest: mean -0.117 degC, standard deviation 0.796, range -1.8 to +1.5 —
  essentially the same gentle nudge session 11 made (mean +0.041, st dev 0.751,
  range -1.7 to +2.3), pointed the other way. The model did not start making big
  swings on unseen data.

**Feature importances, the sanity check that it used what it was meant to:**

```
feature                 gain  gain share   splits   s11 share  EGLC test share
forecast_temp_c       3706.8       38.2%    1,659       35.9%            51.8%
season_sin            3381.7       34.9%    1,206       39.9%            24.5%
season_cos            2606.5       26.9%    1,335       24.2%            23.7%
```
Nothing is ignored and nothing dominates. The three shares are much more even at
CDG than at EGLC, which is F28's finding seen again: CDG's bias lives partly in
the calendar where EGLC's lived mostly in the temperature. With one extra year of
training data, forecast temperature edges back ahead of `season_sin` at CDG
(38.2% against 34.9%) where session 11 had it behind (35.9% against 39.9%) — a
small shift, not a change of character, and it is not over-read here.

For the record, in-sample MAE on the training window was 0.989 degC against raw
GFS's 1.290. A model always looks better on the data it was fitted to; that
figure proves nothing and is here only so it is not a surprise later.

**How each reference was built, for the record** — identical to session 07,
fitted on LFPG's D13 training window only (D31.8, SPEC 2.1c):
- **Raw GFS** — the forecast value itself, uncorrected.
- **Persistence** — the previous calendar day's 12:00 UTC observation at LFPG.
  Past values only (SPEC 2.1d). The first scored day, 2025-08-01, took its
  persistence value from the 2025-07-31 12:00 observation (+24.0 degC), which
  sits in the training window — a past observation, legal, and written down in
  D31.8 in advance so it is not mistaken for leakage.
- **Climatology** — the seasonal average of the observed LFPG temperature for
  that position in the year, over every training-window observation within 7.5
  days of it, measured around the circle. Between 45 and 76 training days sit
  behind each value, 64.4 on average.
- **Mean-bias reference** — the forecast plus -0.0600 degC, that figure being the
  mean LFPG training-window bias and nothing else.
- **ML-corrected** — the forecast plus the model's predicted residual.

**The lock was checked before anything ran.** PART 0 of the output does three
checks and all three passed: all 23 values D31 fixes matched what the script used
(0 mismatches); the model settings matched `scripts/session05_model.py` setting
by setting (0 differ); and the script was compared function by function with
`scripts/session07_test.py`, EGLC's sealed test. **Nine functions are
character-identical to EGLC's test script** — `all_days`, `year_fraction`,
`features`, `mae`, `describe`, `_literal`, `top_level`, `func_source` and
`climatology_from_training` — and the three that differ have their full diffs
printed: the two loaders (the station code in the file names, LFPG's on-the-hour
reporting in the docstring, and the near-noon bookkeeping the drop reconciliation
needs) and `fit_on_training` (printed labels only, D21 references becoming D31
references). All fourteen shared constants matched, including the split dates.
So "only the location changed" (D26) is checked in code here, not argued.

**What this session did not do, on purpose.**
- **The script was run once and not repeated.** D31.10 says the method is run
  once, so no second run was made to confirm byte-identical output, exactly as
  session 07 chose. Determinism rests on the fixed seed, `deterministic=True`,
  `n_jobs=1`, the pinned versions in `requirements.txt` (D24) and the
  byte-identical repeat runs already recorded in F14, F15 and F29.
- **The deeper evaluation (SPEC 5.4) stays optional and was not opened.** D29
  made it optional and blocking nothing. The seasonal table above is context, not
  a significance test. The project still has no formal significance figure for
  either airport's win.
- **The `gfs_seamless` equivalence check was not run at LFPG**, and this result
  does not claim it. Stage 2 can say "this is exactly the `gfs_global` series"
  (D16, F22) but not "and `gfs_seamless` would have given the same", which stage
  1 can (F6). Carried forward from Q20's closing note and session 12's warning.
- **Nothing was committed.**

**No SPEC edit was made this session, and none was authorised.** The bar was
judged as written. SPEC 5.0's results table still shows LFPG as "pending — not
yet run", and SPEC 1 and 6 still describe stage 2 as in progress; those are now
out of date and are flagged for the owner in this session's consistency check
rather than changed here.

---

## 2026-08-18 — Open question raised by session 13 (not acted on)

Stage 2 has passed, which opens a choice that is the owner's to make. It is
recorded here and was not acted on. This mirrors Q17, which was raised the same
way when stage 1 passed.

**Q24. Stage 2 has passed — what opens next, and does SPEC need updating to say
so?** Two parts, both the owner's:
- **Which way next?** SPEC section 6 says the roadmap's next stage is **Stage 3 —
  pool airports into one model with location-describing features**, with the
  target hour switching to solar standard noon (D27). But the owner has
  previously said they would rather **add more airports first** before pooling,
  and SPEC 1 leaves that open ("More airports may follow"). Adding an airport
  means a new row in SPEC 3.4 and the same five steps stage 2 just walked:
  verify on contact, pull and map, join and rehearse, lock, test. SPEC 6 is
  explicit that a stage opens only when the owner opens it and that a session
  filling in a later stage early is a warning sign, so **nothing about stage 3
  was written or started**.
- **SPEC now describes stage 2 as unfinished, and it is finished.** Four places
  are out of date, and no session 13 SPEC edit was authorised, so none was made:
  section 1 ("stage 2, **in progress**"), the stage cell in the 3.4 airport table
  ("2 — in progress"), the 5.0 results table ("LFPG | pending — not yet run | —")
  and section 6 ("Stage 2 ... IN PROGRESS"). They are listed here and in session
  13's consistency check so the owner can authorise the edits deliberately, in
  the way session 09 and session 10's SPEC edits were authorised.

One thing worth deciding alongside it, though it needs no separate question:
**both airports' single looks are now spent, and they were spent on the same
twelve months** (F30). Whatever opens next, a result measured on 2025-08-01 to
2026-07-31 is no longer a held-out result for the method, and a third airport
tested on those same dates would not be an independent draw of weather either.

---

## 2026-08-18 — Session 14 decisions (a third airport opens)

Stage 2 passed (F30), and F30's own closing caveat is what these two entries
answer. Both were written before any DSM data was pulled.

**D32. A third airport is opened: Des Moines, Iowa (IEM station `DSM`, network
`IA_ASOS`).**
- **What it is for.** F30 recorded the honest limit on stages 1 and 2: EGLC and
  LFPG are 328 km apart and were tested on **the same twelve months**, so the
  two wins lean on one western-European weather year seen twice, not on two
  independent draws. A third airport in a different weather region is the direct
  attack on that. Des Moines sits in the flat continental interior of the United
  States, where a summer has little to do with a summer in London or Paris.
- **Why Des Moines specifically.** Flat and continental, so the local
  terrain effects are mild; GFS is well behaved over the US interior; and IEM is
  an Iowa institution, so `IA_ASOS` is its home network and its cleanest record.
  The owner's plan is "temperate and well-behaved first, then ramp up
  difficulty", so DSM is the easy off-continent step, taken before harder and
  more independent airports and before any stage 3 pooling.
- **This partially answers Q24**, which asked what opens next now that stage 2
  has passed. The answer is the "more airports first" branch, not stage 3.
  **Stage 3 is not opened and nothing about it was written or started.** Q24's
  second half — the SPEC edits that would stop SPEC describing stage 2 as in
  progress — is still open and is now joined by Q25.
- Everything else is reused unchanged from stages 1 and 2, pending
  verification that DSM's data supports it: the two data sources (SPEC 3.1,
  3.2), the model string pin (D16), temperature only (D17), the split dates
  (D13), the pairing rule (D14), the drop-count-report rule (SPEC 2.2), the
  minimal three features (D19), the model settings (D21.4) and the frozen
  qualitative bar (SPEC 5.3, D22). **One thing is not reused — the target
  hour. See D33.**

**D33. DSM's target hour is local standard noon — 18:00 UTC — not 12:00 UTC.**
- **The problem.** DSM's standard-time offset is UTC−6, so 12:00 UTC is 06:00
  in the morning at Des Moines. That is dawn: the coldest, most stable part of
  the day, and precisely the transition SPEC 4.1 says 12:00 UTC was chosen to
  **avoid** in Europe ("It avoids dawn and dusk, when temperature swings
  quickest"). Testing DSM at 12:00 UTC would change the *time of day* as well
  as the region, so a different result could be either, with no way to tell
  which.
- **The decision.** DSM's target is **12:00 Central Standard Time = 18:00 UTC**,
  with daylight saving deliberately ignored so the target stays a fixed UTC hour
  all year round. At 18:00 UTC the local clock reads 12:00 CST in winter and
  13:00 CDT in summer — midday to early afternoon, which is how 12:00 UTC sat
  at the European airports.
- This is **D27's solar-standard-noon convention brought forward**. D27 wrote
  the convention down for stage 3 and said, in as many words, that deciding it
  while nothing depended on it was cleaner than deciding it under pressure. It
  is now being applied earlier than D27 expected, for a reason D27 did not have
  in front of it: a third airport six time zones away, modelled on its own.
- **The honest consequence, recorded plainly.** DSM changes **both** the
  location and the target hour against EGLC and CDG, so **D26's "only the
  location changed" does not strictly hold for DSM**. That claim was what made
  stage 2's comparison clean, and it is being given up here on purpose. The
  argument for giving it up: for a cross-region test, holding *local midday*
  constant is the more meaningful thing to fix than holding the UTC hour
  constant, because 12:00 UTC is a different time of day at each location and
  the difference is small in Europe and large across an ocean. Anyone reading a
  DSM result must read it knowing two things changed, and DSM's result must not
  be quoted as if it were the same controlled comparison stage 2 was.
- **Chosen on principle, before any DSM data was seen.** Nothing about DSM's
  bias, its record or its numbers was known when this was decided. That matters
  under rule 2.4 in the same way the frozen bar does.
- **It conflicts with SPEC 4.1 as SPEC is written today**, which says the same
  hour 12:00 UTC is used at every airport and that the convention "changes at
  stage 3, and only there". No SPEC edit was authorised this session, so none
  was made. The conflict is real, it is deliberate, and it is raised as **Q25**
  and in this session's consistency check for the owner to settle.

---

## 2026-08-18 — Session 14 findings (DSM verified on contact)

This session pulled small samples only. **No full dataset was pulled, nothing
was joined, built, trained or evaluated, and nothing from stage 1 or stage 2 was
touched or re-run.** Ten raw files went into `data/raw/`, each with a
`.meta.txt` beside it recording the pull time and the exact request (SPEC 2.3).
The scripts are `scripts/session14_pull.py` and `scripts/session14_checks.py`;
the full real output is `notes/session-14-check-output.txt`, and the pull log is
`notes/session-14-pull-output.txt`. Two consecutive runs of the checks script
produced identical output.

**F31. DSM's position, and the forecast grid point it maps to.**

The position comes from IEM's own `IA_ASOS` station listing, pulled first in the
same run so that the forecast requests could use it. Nothing was typed in from
memory or a map — the rule D28 set for the airport table.

```
IEM's entry for DSM, exactly as returned:
  sid           = DSM
  sname         = Des Moines
  network       = IA_ASOS
  state / country = IA / US
  coordinates   = lat 41.534, lon -93.6531
  elevation     = 294.0 m
  tzname        = America/Chicago
  archive_begin = 1928-01-01
  archive_end   = None   (still reporting)
  online        = True
  attributes    = METAR_RESET_MINUTE = 54, HAS1MIN = 1, HASTAF = 1, ...
                  (62 stations in the IA_ASOS listing)
```

The observation CSV carries lat 41.5339 / lon -93.6531 / elevation 294.0 m — the
same place, 11 m apart, because the CSV rounds latitude to four decimals and the
metadata to three. The two IEM sources agree.

Beside the two airports already in the project:

```
        latitude   longitude   elevation
EGLC    51.5053     0.0553         5 m
LFPG    49.0153     2.5344       109 m
DSM     41.534    -93.6531       294 m
DSM is 6,754 km from EGLC and 7,051 km from LFPG, and 289 m / 185 m higher.
EGLC and LFPG are 328 km apart (F17).
```

That distance is the whole point of D32. It also makes DSM the highest and by
far the most continental site in the project.

The forecast grid point Open-Meteo returned for DSM:

```
requested        : lat 41.534, lon -93.6531
grid point       : lat 41.52945, lon -93.63281, elevation 285.0 m
distance         : 1.76 km from the airport
height mismatch  : -9.0 m  (grid 285 m, station 294 m)
```

**This is the closest grid point of the three** — 1.76 km against 3.44 km at
LFPG and 4.33 km at EGLC — and the first with a height mismatch worth naming.
Neither should be over-read. A GFS cell elevation is a smoothed average over a
wide area, so 9 m is well inside the noise, and both facts are exactly the kind
of steady local offset this project exists to learn (Q5, F17).

**F32. The target hour checked, not assumed: local standard noon at DSM really
is 18:00 UTC.**

D33 fixes DSM's target at local standard noon and says that is 18:00 UTC. That
was checked against the timezone database, using the timezone name IEM's own
metadata gives (`America/Chicago`):

```
timezone from IEM metadata     : America/Chicago
mid-winter (standard time)     : 18:00 UTC = 12:00 CST (UTC-6)
mid-summer (daylight saving)   : 18:00 UTC = 13:00 CDT (UTC-5)
standard-time offset           : UTC-6
so local standard noon (12:00) = 18:00 UTC
D33 says                       = 18:00 UTC
VERDICT                        : MATCHES
```

And for contrast, what the European target hour would have been at DSM:

```
mid-winter  : 12:00 UTC = 06:00 CST - dawn
mid-summer  : 12:00 UTC = 07:00 CDT - dawn
```

So the reason D33 gives is not theoretical. 12:00 UTC at Des Moines is the
dawn hour SPEC 4.1 explicitly chose 12:00 UTC to avoid in Europe.

**F33. The forecast archive starts at DSM on exactly the same hour as at EGLC
and LFPG: 2021-03-24 00:00 UTC.**

Two probes, both `gfs_global`, `temperature_2m_previous_day1`, at IEM's DSM
position:

```
probe 1, 2021-03-01..2021-03-07 : 168 rows, ALL 168 null
probe 2, 2021-03-18..2021-03-26 : 216 rows, 72 with a value, 144 null
                                  first non-null = 2021-03-24T00:00
                                  value range 4.8 to 13.0 degC
```

The recent sample is complete:

```
2026-07-01..2026-07-21 : 504 rows, 504 with a value, 0 null
                         value range 17.2 to 36.0 degC
                         timezone in the response: GMT, utc_offset_seconds 0
```

This is the third location to give the same answer, down to the hour, including
the detail that the API answers HTTP 200 with all-null values for dates before
its archive begins rather than returning an error (F1, F20). Two locations
sharing a start hour said the floor was a property of the archive; a third on
another continent makes that about as settled as it can be without reading
Open-Meteo's source.

**The practical consequence: the D13 split dates carry over to DSM unchanged.**
Training 2021-03-24 to 2025-07-31 and testing 2025-08-01 to 2026-07-31 are as
available at DSM as at the two European airports. No date needs moving.

**F34. DSM reports at `:54`, on every single report in both samples — so the
D14 pairing rule applies as written at the 18:00 UTC target, with a 6-minute
offset.**

This is the per-airport fact D14 depends on. EGLC reports at `:50` (F3), LFPG at
`:00` (F18), and DSM turns out to be the most consistent of the three.

```
recent sample 2026-07-01..2026-07-21 : 504 reports, minute-past-hour  :54 x504
early  sample 2021-03-18..2021-03-31 : 336 reports, minute-past-hour  :54 x336
distance from the nearest hour        : 6 min on every report in both samples
within D14's 15-minute window         : 504 of 504, and 336 of 336
outside it, so D14 drops them         : 0, and 0
```

IEM's own station metadata agrees: DSM's `METAR_RESET_MINUTE` attribute is `54`
(F31). So the habit is both measured and declared, and it holds at both ends of
the period, five years apart.

**Does D14 need adapting? No.** D14 pairs each target hour with the nearest
routine report and drops the hour if no report falls within 15 minutes of it.
At DSM the `17:54` report is 6 minutes from 18:00 UTC and the `18:54` report is
54 minutes from it, so the rule picks 17:54 — the same shape of pairing D14
gives at EGLC, where the 11:50 report serves 12:00, and a smaller offset than
EGLC's. The 10-minute argument D14 rests on covers 6 minutes comfortably.

```
pairing offset at the target hour     EGLC   LFPG   DSM
                                      10 min  0 min  6 min
```

What D14 would keep at DSM's own target hour, observation side only:

```
recent sample 2026-07-01..2026-07-21  21 calendar days, 21 kept, 0 dropped
early  sample 2021-03-18..2021-03-31  14 calendar days, 14 kept, 0 dropped
pairing offset on every kept day      : 6 minutes, min and max alike
e.g. 2026-07-01 -> report 17:54 UTC, 30.56 degC
     2021-03-18 -> report 17:54 UTC,  8.89 degC
```

**Not one report in either sample falls outside D14's tolerance**, so on this
evidence DSM loses no day at all to off-hour reporting — the problem that costs
LFPG three days across five years (F25) and EGLC almost nothing (F9). Only the
full pull can say whether that holds over five years; three weeks plus two weeks
is a small sample and F11's lesson is that spot checks prove nothing about the
places they did not look.

**Gap counts, nothing filled (SPEC 2.2).** Both samples are complete except for
one hour each, and that one hour is an artefact of where the request was cut,
not a hole in the record:

```
recent sample : 504 hours expected, 503 covered, 1 missing (2026-07-01 00:00)
early  sample : 336 hours expected, 335 covered, 1 missing (2021-03-18 00:00)
reports with no temperature : 0 in both samples
```

Because DSM reports at `:54`, the report that covers hour `H` is stamped
`(H-1):54`. The first hour of any window therefore needs a report from the day
*before* the request, which was not asked for. **It does not touch the target
hour** — 18:00 is served by 17:54 on the same day — but it will make the full
pull's whole-hours gap map miscount one hour per chunk boundary unless the
mapping allows for it. See Q26.

**F35. The two United States questions answered: DSM needs no new units
handling and no new timezone handling.**

Neither was ever in doubt in Europe, and both would have been large, silent
errors if wrong at a US station. Both were measured rather than assumed.

**Units.** The pipeline reads IEM's `tmpc` field and performs no unit conversion
anywhere — session 08's reader floats the value straight into a Celsius column.
A short window was pulled with Fahrenheit alongside Celsius purely to check
this:

```
file : iem_asos_DSM_2026-07-01_2026-07-04_routine-tmpc-tmpf.csv   72 rows

valid (UTC)        tmpc     tmpf   (tmpf-32)*5/9   difference
2026-07-01 00:54   32.22    90.00          32.22       -0.002
2026-07-01 01:54   30.00    86.00          30.00       +0.000
2026-07-01 03:54   28.89    84.00          28.89       +0.001
2026-07-01 04:54   28.33    83.00          28.33       -0.003

largest disagreement across all 72 rows : 0.0044 degC
tmpc range in this sample               : 18.89 to 32.22 degC
```

`tmpc` is degrees Celsius at DSM, the same field and the same units EGLC and
LFPG use. The sub-hundredth differences are rounding: the METAR carries whole
degrees Celsius, IEM derives Fahrenheit from it, and both are printed to two
decimals.

**Timezone.** Every IEM request in this project sends `tz=UTC`. The same three
days were pulled a second time with `tz=America/Chicago` and the two series
slid past each other to see where the temperatures line up:

```
shift (hours)   rows compared   temperatures equal
          +0              72        3  (4.2%)
          +3              69        9  (13.0%)
          +4              68       17  (25.0%)
          +5              67       67  (100.0%)
          +6              66       17  (25.8%)
          +8              64        4  (6.2%)
```

A single clean 100% at +5 hours, and early July is exactly when
`America/Chicago` is on daylight saving at UTC−5. So the `tz=UTC` request really
is UTC. Open-Meteo labels its own side of the join `timezone=GMT`,
`utc_offset_seconds=0`, so both series are stamped in UTC and neither needs
shifting.

**One wording difference settled while there.** The session 14 prompt describes
the existing request approach as `tz=Etc/UTC`; every request this project has
ever made uses `tz=UTC`. The same three days were pulled the prompt's way and
compared with the first three days of the `tz=UTC` sample — same station, same
fields, same window:

```
tz=UTC file     : iem_asos_DSM_2026-07-01_2026-07-22_routine.csv, first 73 lines
tz=Etc/UTC file : iem_asos_DSM_2026-07-01_2026-07-04_routine-etc-utc.csv
both            : 4,146 bytes
byte-for-byte identical : YES
```

They are the same request under two spellings. The project's `tz=UTC` needs no
change and the prompt's wording and the code agree in substance.

**F36. DSM does NOT file a second scheduled report — its "special" reports are
genuinely unscheduled. That is different from both European airports.**

At EGLC, IEM's "special" (SPECI) stream turned out to be a second scheduled
report at `:20` (F3), and at LFPG one at `:30` (F19). At DSM it is what the name
says:

```
recent window 2026-07-01..2026-07-21, 21 days
  routine rows           : 504  (all at :54)
  routine + special rows : 558
  special rows           :  54
  distinct minutes used  :  38
  busiest minutes        : :07 x4, :31 x3, :01 x2, :13 x2, :22 x2
```

Fifty-four extra reports spread over thirty-eight different minutes, none used
more than four times in three weeks. That is weather-driven, not scheduled.

Recorded, not acted on. Stage 1 and stage 2 use the routine report as the hourly
truth and DSM reuses that unchanged. It is worth writing down for two reasons:
DSM has no `:30`-style fallback stream to argue about the way Q19 did at CDG, so
D30's question cannot even arise here; and a reader comparing the three airports'
report counts should know why DSM's second stream is so much smaller.

**F37. Plain first read — yes, DSM is usable for the recipe the same way EGLC
and CDG were.** Every verify-on-contact check passed:

- the Previous Runs API carries the location, with a grid point 1.76 km away and
  a 9 m height difference (F31);
- the archive reaches back to the same 2021-03-24 00:00 UTC start hour, so the
  fixed D13 split dates need no change (F33);
- IEM carries DSM in `IA_ASOS` with a complete-looking observation record, and
  the position used is IEM's own (F31);
- the pairing rule needs no adapting: DSM reports at `:54`, a steady 6 minutes
  from the target hour, inside D14's tolerance, on every report in both samples
  (F34);
- the units and the timezone need no new handling, and that is measured rather
  than assumed (F35);
- and the one genuinely DSM-specific choice, the target hour, was made on
  principle before any data was seen (D33) and then confirmed against the
  timezone database (F32).

**Nothing found here justifies changing any stage 1 or stage 2 decision.** The
one thing that is not reused — the target hour — was decided in advance and its
cost to D26's "only the location changed" claim is written into D33 rather than
glossed over.

Three things this session did **not** check, all listed as open questions below:
the SPEC edits D33 now requires (Q25), the chunk-boundary effect DSM's `:54`
reporting has on a whole-hours gap map (Q26), and whether `gfs_global` and
`gfs_seamless` return the same data at DSM (Q27) — which matters more in Iowa
than it ever did in Europe.

---

## 2026-08-18 — Open questions raised by session 14 (not acted on)

**Q25. SPEC and D33 now disagree about DSM's target hour, and SPEC also still
describes stage 2 as in progress.** No SPEC edit was authorised this session and
none was made. The places that need the owner's word, so the edits are made
deliberately the way session 09's and session 10's were:
- **SPEC 4.1 says the target hour is 12:00 UTC at every airport**, and says the
  solar-standard-noon convention "changes at stage 3, and only there" and is
  "**not** applied to stage 1 or stage 2". D33 applies it at DSM now. Both
  sentences cannot stand. The natural repair is to make the target hour a
  **per-airport fact in the SPEC 3.4 table** — a new column — with 12:00 UTC for
  EGLC and LFPG and 18:00 UTC for DSM, and to reword 4.1 so it states the
  principle (local midday, daylight saving ignored) rather than one hour. That
  is exactly the move D28 made for the other per-airport facts, and the session
  14 prompt says it belongs to the design/pull session, not this one.
- **SPEC 3.4's table has no DSM row**, and no target-hour column to put in it.
- **The four places Q24 already listed are still out of date**, now with a
  third airport arriving on top of them: section 1 ("stage 2, **in progress**"),
  the stage cell in the 3.4 table, the 5.0 results table ("LFPG | pending — not
  yet run") and section 6 ("Stage 2 ... IN PROGRESS"). Adding DSM raises a
  further question the owner should settle at the same time: **what is a third
  airport called?** SPEC 6's stage list has no slot for it — stage 3 is pooling.
  It may be a continuation of stage 2's "prove the recipe travels", a new stage
  2b, or something else. Nothing was invented here.

**Q26. DSM's `:54` reporting will make a whole-hours gap map miscount one hour
at every chunk boundary.** At a station reporting at `:54`, the report covering
hour `H` is stamped `(H-1):54`, so the first hour of any request window has no
report inside that window — which is why both of this session's samples show
exactly one missing hour, at the very first hour (F34). It is a request-boundary
artefact, not a hole. It **does not touch the target hour**: 18:00 UTC is served
by the 17:54 report from the same day, inside the same chunk. But session 10's
gap-mapping approach counts *every* hour, and run unchanged over six yearly
chunks at DSM it would report six phantom missing hours. The pull session
should either overlap the chunks by a day, or count the boundary hours
separately and say so. Recorded now so it is not discovered as a surprise in the
middle of the pull, and so nobody "fixes" it by filling anything (SPEC 2.2).

**Q27. `gfs_global` versus `gfs_seamless` has never been compared at DSM, and
F6's reason for expecting them to agree does NOT carry to Iowa.** D16 pins
`gfs_global`, and this session used it, so nothing is broken. But the argument
behind F6 was location-specific and it is worth reading again:

> "For the NCEP provider the candidates are GFS (global) and HRRR/NAM/NBM (all
> CONUS-only, that is the United States). HRRR 'data are only available for the
> United States, while for other locations, only GFS is used'. EGLC is in
> London, so no CONUS model can ever apply."

**Des Moines is in CONUS.** So at DSM, `gfs_seamless` is exactly the case F6
ruled out for Europe: a seamless blend that may prefer a higher-resolution
non-GFS model over GFS. Two consequences, neither of them a blocker:
- The **D16 pin protects the project** — pinning `gfs_global` means the series
  is NCEP GFS by construction wherever the airport is, which is precisely the
  reason D16 gave for pinning it. This is the first time that reason has had
  real work to do.
- But if anyone ever reaches for `gfs_seamless` at a US airport, or compares
  DSM's numbers with a `gfs_seamless` series from elsewhere, **it will not be
  the same model**. That is worth a check at the pull session, in the way F6
  checked it at EGLC: a small value-by-value comparison of the two strings over
  a recent and an early window. Q20's note already records that this comparison
  was never re-run at LFPG either. Not acted on here — it is outside a
  verify-on-contact scope, which is about whether the data exists at all.

---

## 2026-08-18 — Session 15 decision (SPEC generalised for per-airport hours)

This session had two jobs: generalise SPEC first, then pull DSM's full history
against the agreed spec. The entry below is the first job. The findings that
follow are the second.

**D34. SPEC now carries a per-airport target hour and an open-ended airport
list. This closes Q25 and the second half of Q24.**

- **What changed in shape.** The **target hour is now a per-airport fact**, in
  exactly the way the minute the station reports at already was. It has its own
  column in the SPEC 3.4 airport table — 12:00 UTC for EGLC, 12:00 UTC for
  LFPG, 18:00 UTC for DSM — and section 4.1 now states the *principle* (one
  fixed hour per airport, chosen to sit at that airport's local midday) instead
  of naming one hour for everybody.
- **Why now.** D33 set DSM's target at local standard noon, 18:00 UTC, and SPEC
  4.1 said the hour was 12:00 UTC at every airport and that the solar-noon
  convention arrived "at stage 3, and only there". Both sentences could not
  stand. This is the same move D28 made when it turned the other per-airport
  facts into a table: the general rule is stated once and the varying part is a
  column. It is done to scale rather than patched, because more airports are
  coming.
- **D27 is folded in honestly rather than quietly overtaken.** SPEC 4.1 now says
  plainly that this *is* D27's solar-standard-noon convention, that D27 had
  planned it for stage 3, and that DSM brought it forward. Stage 3 inherits it
  instead of switching to it (SPEC 6).
- **The cost to D26's claim is written into SPEC, not left in DECISIONS.** SPEC
  4.1 now states that "only the location changed" still holds **within western
  Europe**, between EGLC and LFPG, which ran at the same hour — and does **not**
  hold for DSM, which changes the location and the target hour together. A DSM
  result answers "does the recipe travel to a different region at a comparable
  local time", and must not be quoted as the same controlled comparison. That is
  D33's own wording, promoted into the spec so a reader of SPEC alone cannot
  miss it.
- **Stage 2 is reframed from "the second airport" to "individual airports, two
  or more".** SPEC 6's stage 2 now covers CDG (passed), DSM (in progress) and
  any further airports before pooling, each judged on its own sealed test year.
  That answers the "what is a third airport called?" half of Q25: it is not a
  new stage and not a stage 2b — stage 2 is the *shape* of the work (one airport
  at a time, five steps, one look), and it holds as many airports as the owner
  opens. Stage 3 is still only pooling, and **stage 3 is not opened**.
- **The stale wording Q24 listed is now resolved.** Section 1, the 3.4 stage
  cells, the 5.0 results table and section 6 all said stage 2 was in progress
  and LFPG pending. They now record EGLC and LFPG as **passed**, with F30's
  figures in the results table, and DSM as in progress.

**The frozen bar's meaning is unchanged — only its scope and the hour
convention moved.** This was checked edit by edit, as session 09's prompt
required of D28:
- **Section 5.1, the metric:** untouched. Mean absolute error in degrees
  Celsius.
- **Section 5.2, the references:** untouched. Raw GFS and persistence decide;
  climatology and the mean-bias reference are informative. The sentence naming
  which two decide was inspected and left exactly as it stands.
- **Section 5.3, the bar:** the only change is that "stage 2 is CDG being put to
  the same one" became "stage 2 is each further individual airport put to the
  same bar, one at a time — CDG, then DSM, then any that follow". The
  requirement — beat raw GFS **and** persistence on MAE over that airport's own
  test year, qualitatively, with no numeric margin (D22) — is word for word what
  it was.
- **Section 5.0, the scope:** unchanged in meaning; the results table gained
  LFPG's real figures and a DSM row marked pending, plus a pointer to F30's
  caveat that both spent test years are the same twelve months.
- **Rule 2.4** is untouched. Nothing a result must clear was added, and nothing
  it used to have to clear was removed.

**The authorised edits, and nothing else.** A-1 (section 1), A-2 (section 3.4:
the target-hour column, DSM's two rows, and the notes beneath the table), A-3
(sections 3.2 and 3.3), A-4 (section 4.1), A-5 (section 4.5), A-6 (sections 5.0
and 5.3) and A-7 (section 6). The full before/after of every one is saved in
`notes/session-15-spec-edits.txt`.

**Two things about how the edits were made, recorded so neither looks like a
liberty taken quietly:**

1. **A-3's gap marker was written, then filled in later in the same session.**
   The prompt said to leave a "to be verified in this session's gap map" marker
   in section 3.2 and not to assume DSM shared the 492-hour gap. That marker was
   written during part A, before any DSM history was pulled. Part C then mapped
   every hour and answered the question (F38), so the marker was replaced with
   the verified answer at the end of the session. Leaving SPEC saying "not yet
   known" about something this session measured would have created exactly the
   SPEC-versus-DECISIONS drift CLAUDE.md warns against. The edit stayed inside
   A-3's authorised section and its authorised purpose.
2. **One inaccuracy was flagged rather than fixed, because fixing it was not
   authorised.** See Q28.

---

## 2026-08-18 — Session 15 findings (the full DSM pull and gap map)

The full third-airport pull ran for real: 2021-03-24 to 2026-07-31, both
sources, six yearly chunks each, plus four small files for the Q27 comparison.
32 new files went into `data/raw/` — 16 data files with a `.meta.txt` beside
every one (SPEC 2.3). **Nothing was joined, filled, cleaned, built, trained or
evaluated**, and no temperature value from the test window was printed. The
scripts are `scripts/session15_pull.py` and `scripts/session15_checks.py`; the
full real output is `notes/session-15-check-output.txt` and the pull log is
`notes/session-15-pull-output.txt`.

`data/raw/` now holds **128 files, 11 MB**. No retry fired and no HTTP 429
appeared, with a 3-second pause between calls.

**F38. DSM's forecast series has EXACTLY the same 492-hour gap as EGLC's and
LFPG's, down to the hour. It is one gap and there are no others.**

```
expected hours in period : 46,944
hours with a usable value: 46,452
hours missing            : 492 (1.05% of the period)
  of which no row at all : 0
  of which row but null  : 492
rows returned outside the period: 0

training 2021-03-24..2025-07-31: 38,184 expected, 37,692 usable, 492 missing (1.29%)
test     2025-08-01..2026-07-31:  8,760 expected,  8,760 usable,   0 missing (0.00%)

GAP MAP: 1 gap run in the whole period
    last hour with data       : 2023-12-29 23:00 UTC
    first missing hour        : 2023-12-30 00:00 UTC
    last missing hour         : 2024-01-19 11:00 UTC
    first hour with data again: 2024-01-19 12:00 UTC
    length                    : 492 hours (20.5 days)
    falls entirely in training: yes
    matches the EGLC/LFPG gap : YES - same start, same end, same length
```

**The explicit answer the session asked for: the same window, not a different
one and not none.** Every one of those six headline totals is identical to
EGLC's (F8) and LFPG's (F22), and so is the gap's position. Two airports 328 km
apart sharing it made the gap look like a property of the archive; a third one
6,754 km away on another continent, in a different IEM network and a different
weather region, settles it. It is the archive, not the place. Nothing was filled
(SPEC 2.2).

The practical consequence at DSM is slightly different from Europe's, because
DSM's target hour is 18:00 UTC rather than 12:00. The gap ends at 2024-01-19
11:00 and the series resumes at 12:00, so 2024-01-19 has an 18:00 value and
survives. The gap costs **20 days at 18:00 UTC**, 2023-12-30 to 2024-01-18
inclusive — the same count Europe lost at 12:00, arrived at by different
arithmetic.

The grid point Open-Meteo returned across all six chunks is lat 41.52945, lon
-93.63281, elevation 285.0 m — the same point session 14's samples got (F31), so
the full pull describes the same place the verification did.

All six chunks were requested with `models=gfs_global` (D16), read back out of
the saved `.meta.txt` URLs rather than claimed, with no `gfs_seamless` anywhere.
Unlike at LFPG (Q20's closing note), that pin was **not** taken on trust here —
see F40.

**Value ranges, training window only. The test window's values were not looked
at.**

```
forecast (GFS, training window) : n = 37,692   min = -30.0    max = 44.7   mean = 11.95 degC
observed (DSM, training window) : n = 38,174   min = -27.22   max = 38.33  mean = 12.28 degC
```

Both are plainly Celsius — Kelvin would read about 250-310 — and neither carries
an absurd value for the continental interior. For scale, EGLC ran -1.7 to 40.7
(F10) and LFPG -8.5 to 41.2 (F26), so DSM swings roughly 20 degrees wider at the
cold end than either European airport. That is what "flat continental interior"
means and it is the reason D32 chose the place.

**One thing worth noticing for the join session, recorded as an observation
only.** The forecast's warm end runs well past anything the station observed:
the forecast reaches 44.7 degC (2023-07-28 21:00) and spends 64 hours at or
above 40 degC, while the observed training-window maximum is 38.33. The cold
ends nearly agree (-30.0 against -27.22). Whether that means anything at 18:00
UTC specifically is a question for the join session and not for this one — F13
caught F10 making exactly that mistake, reading an all-hours range as if it said
something about one target hour. Not acted on.

**F39. DSM's observation record is the cleanest of the three airports, and the
Q26 request-boundary artefact is real, tiny and fully accounted for.**

```
reports in files           : 46,938
minute-past-hour spread    : :09 x1, :36 x1, :38 x2, :47 x1, :49 x1, :50 x2,
                             :51 x1, :53 x3, :54 x46,921, :57 x1, :58 x2, :59 x2
reports with no temperature: 1   (2023-06-30 10:50 UTC)
reports >15 min from any hour, dropped (D14): 3
expected hours in period   : 46,944
hours with an observation  : 46,932
hours missing              : 12 (0.03% of the period)
  of which Q26 artefacts   : 1
  real missing hours       : 11 (0.02%)

window                              expected  observed  real gap  Q26
training 2021-03-24..2025-07-31       38,184    38,174         9    1
test     2025-08-01..2026-07-31        8,760     8,758         2    0

gap runs (real): 10 in total
    1 hour     9 runs     9 hours
    2-5 hours  1 run      2 hours
longest: 2 hours  2025-09-24 03:00 -> 2025-09-24 04:00 UTC
```

Against the other two airports: **11 real missing hours (0.02%) against LFPG's
140 (0.30%, F23) and EGLC's 44 (0.09%, F9)**, with a longest run of 2 hours
against 32 and 8. There is no run of even half a day. F34's guess from five
weeks of samples — that DSM's record looked exceptionally tidy — holds across
five years.

**Q26 answered, and it is smaller than feared.** F34 predicted that a
whole-hours gap map would count one phantom missing hour at every chunk
boundary, because DSM reports at `:54` and the report serving hour `H` is
stamped `(H-1):54`, so the first hour of a request window needs a report from
before that window. That is exactly what happens **chunk by chunk** — all six
first hours are uncovered by their own chunk. But the chunks are contiguous and
IEM's end date is exclusive, so chunk *N*'s last report (`:54` on its final day)
serves the first hour of chunk *N+1*. Concatenated, five of the six seams close
themselves:

```
chunk                      first hour           that chunk alone   all chunks joined
2021-03-24..2021-12-31   2021-03-24 00:00     MISSING            MISSING
2022-01-01..2022-12-31   2022-01-01 00:00     MISSING            covered
2023-01-01..2023-12-31   2023-01-01 00:00     MISSING            covered
2024-01-01..2024-12-31   2024-01-01 00:00     MISSING            covered
2025-01-01..2025-12-31   2025-01-01 00:00     MISSING            covered
2026-01-01..2026-07-31   2026-01-01 00:00     MISSING            covered
```

**So there is exactly one artefact hour, 2021-03-24 00:00 UTC** — the first hour
of the whole period, which would need a report from 2021-03-23 23:54 that this
project never requested. It is counted, named and reported separately from the
11 real gaps, and **nothing was filled to cover it** (SPEC 2.2). It touches no
target hour: 18:00 UTC is served by the 17:54 report of the same day, inside the
same chunk. The gap map was not left to inflate by six phantom hours, and it was
not "fixed" by inventing anything. The check is in the script rather than in an
argument — it maps each chunk in isolation, then maps the joined series, and
prints the difference.

**Off-hour reporting is a non-issue at DSM, which is the third distinct answer
from three airports.**

```
off-hour reports (>15 min from any hour): 3 on 3 days, in 3 episodes
minute stamps                           : :36 x1, :38 x2
    EGLC   8 of 46,919 (0.017%, F9)
    LFPG  97 of 46,903 (0.207%, F23)
    DSM    3 of 46,938 (0.006%)
```

Three reports in five years, scattered as singles, none of them near the target
hour. D30's question — whether to widen D14's tolerance or fall back to a second
scheduled stream — cannot even arise here, both because there is nothing to
rescue and because DSM files no second scheduled report at all (F36).

**F40. Q27 answered, and the answer is the one D16 was pinned against: at DSM,
`gfs_seamless` is NOT the same series as `gfs_global`.**

F6 proved the two strings return identical data at EGLC, but its argument was
location-specific — no CONUS-only NCEP model (HRRR, NAM, NBM) can apply in
London, so nothing non-GFS was in the seamless set to mix in. Des Moines is
inside CONUS, so the argument does not carry. The comparison was therefore run
the way F6 ran it, on two windows:

```
-- 2021-03-24 .. 2021-04-05  (early, inside the training window; F6's own
                              early window at EGLC) --
   gfs_global    grid lat 41.52945, lon -93.63281, elev 285.0 m
   gfs_seamless  grid lat 41.53814, lon -93.65474, elev 285.0 m
   same grid point            : NO
   hours compared             : 312   (0 null in either)
   values that DIFFER         : 0

-- 2026-08-05 .. 2026-08-15  (recent) --
   gfs_global    grid lat 41.52945, lon -93.63281, elev 285.0 m
   gfs_seamless  grid lat 41.53814, lon -93.65474, elev 285.0 m
   same grid point            : NO
   hours compared             : 264   (0 null in either)
   values that DIFFER         : 259 of 264
   largest difference         : 12.3 degC
```

**Three things this says, in order of how much they matter:**

1. **On recent data the two strings are plainly different models.** 259 of 264
   hours differ, by up to 12.3 degC — not rounding, not a tenth here and there,
   but a different forecast. `gfs_seamless` also reports a **different grid
   point** at DSM (41.53814 / -93.65474 against 41.52945 / -93.63281, about
   2 km apart), which is what a higher-resolution CONUS model looks like from
   the outside, and it takes far longer to serve (a `generationtime_ms` of 27
   against 0.12), which is what blending looks like. **This is exactly the case
   F6 ruled out for Europe and Q27 warned would not carry to Iowa.**
2. **On the 2021 window the two are identical, 312 hours out of 312**, even
   though the grid point they report still differs. The plain reading is that
   there is no non-GFS series that far back to blend in, so seamless serves GFS
   values under its own grid label. That is worth knowing, because it means a
   comparison run only on old data would have concluded, wrongly, that the two
   strings agree at DSM.
3. **D16's pin has now earned its keep.** D16 chose `gfs_global` over
   `gfs_seamless` in session 03b for a stated reason — that pinning makes "this
   is exactly NCEP GFS" true by construction rather than by argument, and stops
   a change in Open-Meteo's blending from quietly changing the dataset
   underneath us. Every DSM chunk was pulled with `gfs_global` (checked back out
   of the saved URLs), so **DSM's dataset is unaffected**. But had the project
   used `gfs_seamless`, DSM's recent forecasts would not have been GFS at all,
   and stage 2's third airport would have been quietly comparing a different
   model against the other two. That is the first time a decision in this log has
   prevented a real error rather than a hypothetical one.

**One deliberate departure from F6's method, stated plainly.** F6's "recent"
window at EGLC was 1-21 July 2026. At DSM that window now sits **inside the
sealed test year** (2025-08-01 to 2026-07-31), so it was not used. The recent
window here is 2026-08-05 to 2026-08-15, which sits **after the project period
ends on 2026-07-31** and is therefore outside both the training and the test
sets — D13 does not use any data after 2026-07-31. The early window is F6's own.
So the comparison answers Q27 without opening a single hour of DSM's test year.
The four comparison files are saved in `data/raw/` with their provenance, marked
`q27compare` so they cannot be mistaken for part of the dataset.

**F41. Days lost at DSM's 18:00 UTC target, by cause — written down before any
join, the way session 10's gap map was for CDG.**

This is a count of report timing and forecast row presence, not of temperature
values, so it covers the test window without opening it. The two series were
**not** joined; that is the next session's job. These are the numbers that join
must reconcile against.

```
calendar days in the period : 1,956

OBSERVATION SIDE                       days  training   test
kept - usable 18:00 observation        1,956     1,591    365
LOST: only an off-hour report              0         0      0
LOST: report in place, no temperature      0         0      0
LOST: no report near the 18:00 hour        0         0      0
total days lost, observation side          0 of 1,956 (0.00%)

FORECAST SIDE
days with no 18:00 UTC forecast value     20 (training 20, test 0)
    2023-12-30 .. 2024-01-18, the F38 gap, consecutive

BOTH SIDES TOGETHER - what the join should expect to drop
days lost, either side      :    20  (training 20, test 0)
days lost on BOTH sides     :     0
paired rows expected        : 1,936 of 1,956

inner-training 2021-03-24..2024-07-31: 1,226 days, 1,206 expected rows, 20 dropped
validation     2024-08-01..2025-07-31:   365 days,   365 expected rows,  0 dropped
test           2025-08-01..2026-07-31:   365 days,   365 expected rows,  0 dropped
```

**DSM loses no day at all on the observation side, in five years.** Every one of
the 20 expected drops is the shared forecast gap. That is better than both
European airports: EGLC lost days to missing observations (F12, F16) and LFPG
lost three to off-hour reporting (F25).

Two consequences worth carrying to the next sessions:

- **The 18:00 report is where D14's tolerance is tested, and it passes
  everywhere.** The pairing offset is 6 minutes on essentially every day, from
  the `:54` report of the hour before (F34). The one report in five years with
  no temperature is 2023-06-30 10:50 UTC, nowhere near the target.
- **DSM's validation year and test year are both expected to be complete, 365
  rows each.** CDG's validation year was also complete and its test year lost
  one day (F27, F30); EGLC lost one in each. If DSM's join returns anything
  other than 1,206 / 365 / 365, that is a discrepancy to raise, not to explain
  away — the same standard D31.7 set for CDG and F27 and F30 met.

**Nothing was filled anywhere in this session** (SPEC 2.2). Every count above is
of rows that exist or do not exist.

---

## 2026-08-18 — Session 15 note (what closed, and what is open)

**Q24 is now fully closed.** Its first half was answered by D32 (more airports
first, at Des Moines). Its second half — the SPEC edits that still described
stage 2 as in progress — is closed by D34.

**Q25 is closed by D34.** All three of its bullets are answered: SPEC 4.1 no
longer contradicts D33, SPEC 3.4 has a DSM row and a target-hour column, and the
"what is a third airport called?" question is settled — stage 2 is the shape of
the work, not a count of airports, and it holds as many as the owner opens.

**Q26 is closed by F39.** The artefact is real but it is one hour, not six, once
the contiguous chunks are joined. It is counted separately, named, and nothing
was filled.

**Q27 is closed by F40**, and closed with a result rather than a shrug: at DSM
the two model strings return different data on recent dates. D16's pin means
nothing in the project is affected.

**One new open question, Q28**, below.

**Nothing was committed.** The pull, the gap map, the SPEC edits and this log
entry are all prepared for the owner's review.

**Nothing was joined, built, trained or evaluated. DSM's test year is now on
disk but has never been opened**: only its row presence, gap locations and
report timing were counted, never a temperature value, exactly as session 03b
held EGLC's and session 10 held LFPG's.

---

## 2026-08-18 — Open question raised by session 15 (not acted on)

**Q28. SPEC calls the first column of the airport table "ICAO", and DSM's code
is not an ICAO code.** EGLC and LFPG are ICAO codes. `DSM` is IEM's own station
id for Des Moines International, and every request this project makes addresses
the station by whatever code IEM knows it as. **IEM's `IA_ASOS` listing carries
no ICAO code for DSM at all** — checked this session against the saved listing
rather than assumed. Its twenty properties are `archive_begin`, `archive_end`,
`attributes`, `climate_site`, `country`, `county`, `elevation`, `ncdc81`,
`ncei91`, `network`, `online`, `sid`, `sname`, `state`, `synop`, `time_domain`,
`tzname`, `ugc_county`, `ugc_zone` and `wfo`, and the six attributes beneath
them are `GHCNH_ID`, `HAS1MIN`, `HASTAF`, `HAS_PHOUR`, `METAR_RESET_MINUTE` and
`SHEF_6HR_SRC`. No field holds an ICAO code and the string `KDSM` appears
nowhere in the entry. F31 recorded the entry but printed its attribute list
truncated, so this is the full check rather than a re-reading of F31. Two places
now say something that is no longer quite true:
- **SPEC 3.4's column heading, "ICAO"**, which was accurate while every airport
  was European.
- **SPEC 3.1**, which says each airport "is requested by its ICAO code".

Neither is a data problem — nothing in the project resolves a station by ICAO
code as such, and DSM's pulls are provably addressed by the code IEM returned
(SPEC 2.3 meta files). It is a naming problem, and it will get worse as more
non-European airports are added.

**Nothing was changed**, because this session's authorised edits were A-1 to
A-7 and neither the heading nor section 3.1 is among them; the prompt says
another needed SPEC change is logged as an open question rather than acted on.
What *was* done is inside A-2's authorised section: a note beneath the table now
states plainly that the column holds whatever code IEM addresses the station by,
that `DSM` is not an ICAO code, and that the heading and section 3.1 are flagged
here. So SPEC does not assert something false; it carries a heading it corrects
two lines later, which is untidy rather than wrong.

The obvious repair, for the owner to authorise or reject: rename the column to
"station code" and reword section 3.1 to say each airport is requested by its
IEM station code, noting that for the European airports that code is the ICAO
code. That is one heading and one sentence.

---

## 2026-08-18 — Session 16 findings (the DSM join, bias look and rehearsal)

The first modelling session for the third airport, mirroring session 11 at CDG
and sessions 04/05 at EGLC. The join, the bias look and the model all ran for
real. **DSM's test year was not touched**: the two 2026 DSM raw chunk files were
never opened, the 2025 chunk was cut off at 2025-07-31 on load, and the script
asserts that no date on or after 2025-08-01 reached any table. Nothing was
tuned, varied or chosen again — the locked recipe was applied at the third
location and nothing else. The script is `scripts/session16_model.py` and the
full real output is `notes/session-16-check-output.txt`.

**F42. The join at 18:00 UTC at DSM, and every drop reconciled against F41's
advance prediction. All four lines matched.**

One row per day: date, forecast temperature, observed temperature, and the
residual the model learns.

```
                                         days   kept   drop  no fc  null fc  no obs
inner-training 2021-03-24..2024-07-31   1,226  1,206     20      0       20       0
validation     2024-08-01..2025-07-31     365    365      0      0        0       0
```

**Session 15's gap map predicted these drops before anything was joined, and it
predicted them exactly** — the check F41 exists for, and the same check D31.7
and F27/F30 made at CDG:

```
cause                                         expected   actual  verdict
the 492-hour forecast gap (F38, F41)                20       20  MATCHES
observation-side losses, any cause (F41)             0        0  MATCHES
TOTAL days dropped                                  20       20  MATCHES

period rows                                   expected   actual  verdict
inner-training paired rows (F41)                 1,206    1,206  MATCHES
validation paired rows (F41)                       365      365  MATCHES
```

The 20 dropped days are 2023-12-30 to 2024-01-18, consecutive, all of them the
shared archive gap, all in inner-training. The gap ends at 2024-01-19 11:00 UTC
and the series resumes at 12:00, so DSM's 18:00 target has a value on
2024-01-19 and that day survives — 20 days lost, not 21, arrived at by different
arithmetic from Europe's (F38). Nothing was filled (SPEC 2.2).

**DSM loses no day at all on the observation side, in the whole training
window**, exactly as F41 said: 1,591 usable 18:00 observations from 1,591
calendar days, **0** reports more than 15 minutes from the hour and **0**
carrying no temperature at the target hour. Both European airports lost days
here — EGLC to missing observations (F12), LFPG three to off-hour reporting
(F25). **DSM's validation year is complete, 365 of 365**, as CDG's was and
EGLC's was not.

**The pairing offset actually used, day by day.** F34 predicted a steady 6
minutes from DSM's `:54` report, and that is what 1,590 of the 1,591 days gave:

```
-6 minutes from 18:00 UTC : 1,590 days
-2 minutes from 18:00 UTC :     1 day   (2024-06-07, report filed at 17:58)
```

On 2024-06-07 the station filed 16:54, **17:58** and 18:54 — one report in the
tolerance window, two minutes out, so D14 keeps it and no day is lost. The
script counts one more thing worth writing down: **no day in the whole training
window has more than one report inside D14's 15-minute window**, so the pairing
is never ambiguous at DSM and the rule never has to choose between two reports.

**F43. DSM's bias at 18:00 UTC is a third distinct shape — and it is the first
airport that has BOTH structures, each of them larger than either European
airport's.** Inner-training only; the validation year's values were not
explored and the test year not touched.

Overall, beside EGLC (F13) and CDG (F28):

```
                            EGLC       CDG       DSM
days                       1,205     1,204     1,206
mean bias degC            -0.108    +0.050    -0.231
median degC               +0.000    +0.100    -0.200
st dev degC                1.551     1.654     2.550
mean |bias| degC           1.172     1.248     1.973
station warmer, %           48.7      51.7      45.5
min / max degC        -7.0/+5.6 -7.7/+5.8 -10.4/+9.2
```

EGLC and CDG are measured at 12:00 UTC and DSM at 18:00 UTC (D33). What is held
constant across the three is each airport's own local midday, not the UTC hour
(SPEC 4.1).

**GFS is a much harder forecast to beat at DSM.** Mean |bias| 1.973 degC against
1.248 at CDG and 1.172 at EGLC — about 60% larger — and the spread is half as
wide again. That is what a continental interior means, and it was expected from
F38's value ranges. The mean bias is still small (-0.231), so most of the error
is structure and day-to-day noise rather than a constant offset — but unlike at
CDG, the constant here is not quite nothing.

Against forecast temperature, the warm end is much stronger than anywhere yet:

```
forecast band (degC)     days  mean bias   st dev  mean |bias|  EGLC bias   CDG bias
-30 to -20                  1     -1.580      -          1.580          -          -
-20 to -10                 26     -1.179    1.611        1.612          -          -
-10 to 0                   85     -1.087    1.548        1.504          -     +1.800
0 to 5                    130     -0.781    2.026        1.611     -0.049     -0.687
5 to 10                   165     -0.337    2.049        1.543     +0.361     +0.223
10 to 15                  147     +0.465    2.026        1.554     +0.387     +0.339
15 to 20                  130     +1.098    2.579        2.153     -0.287     +0.320
20 to 25                  186     +0.953    2.247        2.006     -0.746     -0.142
25 to 30                  222     -0.147    2.567        2.113          -          -
30 to 45                  114     -3.089    2.795        3.449          -          -

coldest 10%  n=120  forecast -21.7 to  +0.3 degC  mean bias -1.066 (EGLC +0.097, CDG -0.351)
warmest 10%  n=120  forecast +29.8 to +42.7 degC  mean bias -2.993 (EGLC -1.155, CDG -0.784)
```

**The warm-end bias EGLC had is present at DSM at nearly three times the size**
(-2.993 in the warmest tenth against EGLC's -1.155 and CDG's -0.784), and it
strengthens steadily the warmer the forecast gets (see F44). The cold end is
biased the same way EGLC's was not and CDG's was — GFS runs too warm on DSM's
coldest days too, by about a degree.

By season, the calendar swing is also the biggest of the three:

```
season         days  mean bias   st dev  mean |bias|  EGLC bias   CDG bias
winter DJF      251     -0.805    2.051        1.693     +0.356     -0.092
spring MAM      345     +0.923    2.226        1.923     -0.061     +0.614
summer JJA      337     -0.208    3.155        2.519     -0.549     -0.056
autumn SON      273     -1.187    1.862        1.619     -0.052     -0.401
```

Month by month the turn is sharp: May +1.965 and June +1.736, then August
-2.808 and September -2.113 — a swing of nearly five degrees across the year,
against CDG's one and EGLC's much less.

**So DSM is not "EGLC's shape" or "CDG's shape". It is both at once, and
larger.** EGLC's bias lived in the temperature, CDG's in the calendar, and DSM
carries a strong version of each. That is a third distinct answer from three
airports, and it is the finding this part of the session existed to produce.

**F44. The warm-end overshoot F38 flagged IS real at the 18:00 target hour —
this is not F10's mistake repeated.** Inner-training only.

F38 noticed that DSM's forecast warm end runs past anything the station
observed, counting all 24 hours across the whole training window (forecast max
44.7, observed max 38.33, 64 forecast hours at or above 40 degC). F13 caught F10
reading an all-hours range as if it said something about one target hour, so the
question had to be asked of 18:00 specifically. It was, by mapping every hour of
the day on inner-training and then the join rows:

```
hour UTC   fc hours  fc >=40   fc max   obs max
00:00         1,205        2    40.20     35.56
...
15:00         1,206        0    37.50     31.67
16:00         1,206        1    40.20     33.89
17:00         1,206        2    41.20     35.00
18:00         1,206        5    42.70     36.67   <- target hour
19:00         1,206        8    43.50     37.22
20:00         1,206       10    44.30     37.78
21:00         1,206       13    44.70     38.33
22:00         1,206       11    43.80     38.33
23:00         1,206        6    42.70     36.11
all hours together: 58 forecast hours at or above 40 degC (inner-training)
```

**The overshoot peaks at 19:00 to 22:00 UTC — mid to late local afternoon — and
18:00 sits on the rising edge of it, not away from it.** That is the opposite of
F10's cold-end shift, which came from night-time hours the target never sees.
At the target hour itself:

```
join rows (inner-training)                        : 1,206
forecast range at 18:00 UTC                       : -21.70 to +42.70 degC
observed range at 18:00 UTC                       : -23.28 to +36.67 degC
days with forecast at or above 40 degC            : 5
days with forecast above the observed maximum     : 17
```

And the bias grows steadily as the forecast gets hotter — it is a slope, not a
handful of odd days:

```
selection                 days  mean bias  mean |bias|
forecast >= 30 degC        114     -3.089        3.449
forecast >= 32 degC         57     -4.331        4.360
forecast >= 34 degC         37     -4.838        4.838
forecast >= 36 degC         21     -5.818        5.818
forecast >= 38 degC         13     -6.438        6.438
forecast >= 40 degC          5     -7.068        7.068

the cold end, for symmetry:
forecast <= -10 degC        29     -1.209        1.597
forecast <= -15 degC         4     -0.478        1.148
forecast <= -20 degC         1     -1.580        1.580
```

The ten warmest forecast days at 18:00 are all July to September 2022 and 2023,
and GFS is too warm on every one of them, by 4.6 to 10.3 degC. The worst of
them is **2023-07-27: forecast 40.9, observed 30.6, a gap of 10.3 degC** — the
second-largest miss anywhere in inner-training, behind 2021-08-26 (forecast
33.2, observed 22.8, -10.4).

Two things follow, and both are recorded rather than acted on, because the
method is locked (D21.11 applies to the lock, and this session's scope forbids
changes anyway):

1. **This is the largest single piece of learnable structure at DSM**, and it is
   the reason the correction does as well as it does (F45).
2. **It rests on few days.** Only 5 inner-training days reach 40 degC at 18:00
   and only 21 reach 36. A tree model cannot extrapolate past the range it was
   fitted on, so on any future day hotter than its training data it applies the
   correction it learned at the top of that range. That is a property of the
   locked method, stated here so it is not a surprise when DSM's test year is
   opened — not a proposal to change anything.

**F45. The rehearsal: at DSM the correction beats all four references by the
widest margin of the three airports — on much the hardest problem.**

Model: the locked D21/D31 recipe, fitted on DSM's 1,206 inner-training rows
only. PART 0 of the output proves the method was reused rather than re-chosen —
it reads `scripts/session05_model.py` and compares it with this session's
script: **0 model settings differ**, and of the eleven shared constants
**exactly one differs, TARGET_HOUR (12 → 18), which is D33 and nothing else.**
Eight shared functions are character-identical to both session 05's and session
11's; the ninth, `features`, differs by one docstring line naming the fixed hour,
and its executable code with docstrings stripped is identical. The two loaders
differ and their full diffs are printed — the station code in the file names,
DSM's `:54` reporting in the docstring, and the same near-target bookkeeping
session 11 added. Two consecutive runs produced identical output apart from the
clock time in the header line.

All five methods scored on the same 365 validation days — DSM loses no day at
all, so the common set is the whole year:

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.748     -0.407      2.218        7.27
Persistence                4.108     -0.017      5.470       22.22
Climatology                4.772     -0.074      6.143       19.78
Mean-bias reference        1.723     -0.176      2.187        7.42
ML-corrected               1.466     -0.291      1.921        6.99
```

Verdicts:

```
vs Raw GFS              YES   1.466 against 1.748  ->  0.282 degC better (16.1%)
vs Persistence          YES   1.466 against 4.108  ->  2.642 degC better (64.3%)
vs Mean-bias reference  YES   1.466 against 1.723  ->  0.257 degC better (14.9%)
vs Climatology          YES   1.466 against 4.772  ->  3.306 degC better (69.3%)
```

**This is a validation rehearsal, not the frozen bar (SPEC 5.3, 5.0).** DSM's
bar is judged once, on DSM's own sealed test year, in a later session. **A good
number here does not mean DSM has passed.**

Five things the numbers say, read honestly:

1. **The recipe travels to a different continent.** Applied unchanged 6,754 km
   from EGLC, at a different target hour, on a bias with a different shape, it
   beats every reference. Nothing about it was adapted for DSM and nothing
   needed to be.
2. **The margin is the biggest yet — 16.1% against EGLC's 6.0% and CDG's
   3.4% — but so is the error it is working on.** Raw GFS is 1.748 at DSM
   against 1.426 at CDG and 1.239 at EGLC. There is simply more repeatable bias
   to remove at a continental site, and F43 and F44 say where it is. The
   correction removes a larger share of a larger error; it does not make DSM's
   corrected forecast better in absolute terms than Europe's (1.466 against
   1.165 and 1.377).
3. **Persistence and climatology are far worse at DSM** — 4.108 and 4.772,
   roughly double their European figures. Day-to-day temperature swings in the
   US interior are much bigger, so "tomorrow is the same as today" is a much
   weaker guess there. **The consequence for the frozen bar is worth stating in
   advance: at DSM the binding half of the bar will be raw GFS, not
   persistence.**
4. **The mean-bias reference beats raw GFS at DSM (1.723 against 1.748)**, which
   it did at EGLC and did not at CDG. So there is a small constant worth taking
   here — -0.2305 degC. The model beats that reference by 14.9%, so the win is
   still overwhelmingly structure and not the offset.
5. **The seasonal pattern is new: the season it hurts is SUMMER, not winter.**

```
season         days   raw GFS   ML-corr   DSM chg   EGLC chg   CDG chg
winter DJF       90     1.687     1.273    -0.414     +0.087     +0.025
spring MAM       92     1.958     1.774    -0.184     -0.015     -0.057
summer JJA       92     1.532     1.593    +0.061     -0.321     -0.122
autumn SON       91     1.816     1.218    -0.598     -0.049     -0.044
```

   ("chg" is corrected MAE minus raw GFS MAE for that season. Negative means
   better than raw GFS.) The correction helps in **three seasons of four**, the
   same as both European airports — but at EGLC and CDG the losing season was
   winter every time, and here winter is the second-best season and summer is
   the only loss. Autumn carries the result (-0.598). **Winter flipping from
   the worst season to a strong one is the clearest sign that the seasonal
   pattern was a fact about western Europe, not about the method.**

Day by day, the correction was closer to the truth than raw GFS on **203 of 365
days (55.6%)**, almost exactly CDG's 202 of 365 (55.3%). So it nudges the right
way slightly more often than not, and the extra margin at DSM comes from the
size of the nudges, not their frequency.

**Feature importances — and DSM leans on both features, which is F43 seen from
another direction:**

```
feature             EGLC gain %   CDG gain %   DSM gain %   DSM splits
forecast_temp_c           44.3%        35.9%        45.0%        1,850
season_sin                26.7%        39.9%        37.3%        1,366
season_cos                29.0%        24.2%        17.7%          984
```

At EGLC forecast temperature was the largest source of gain, at CDG `season_sin`
overtook it. **At DSM forecast temperature leads and `season_sin` is close
behind**, which is what an airport carrying a strong version of both structures
should look like. Given the same three features and no guidance, the model
matched each airport's bias where that bias actually lives — three times now.

The corrections applied were much larger than at either European airport, as the
larger bias would suggest: mean -0.116 degC, standard deviation 1.607, range
-5.3 to +3.1, against CDG's standard deviation of 0.751 and EGLC's 0.720. It is
still nudging rather than rewriting, but the nudges are twice the size.

For the record, in-sample MAE on DSM inner-training was 1.221 degC against raw
GFS's 1.973 (EGLC 0.879, CDG 0.945). A model always looks better on the data it
was fitted to; the figure proves nothing and is here only so it is not a
surprise later.

**How each reference was built, for the record** — identical to sessions 05 and
11, fitted on DSM inner-training only:
- **Raw GFS** — the forecast value itself, uncorrected.
- **Persistence** — the previous calendar day's 18:00 UTC observation. Past
  values only (SPEC 2.1d). The first validation day, 2024-08-01, takes its value
  from the 2024-07-31 observation, which sits in inner-training — a past
  observation, legal, and written down so it is not mistaken for leakage.
- **Climatology** — the seasonal average of the *observed* temperature at DSM
  for that position in the year, over every DSM inner-training observation
  within 7.5 days of it, measured around the circle (SPEC 2.1c). Between 30 and
  61 days sit behind each value, 49.6 on average — the same coverage as at the
  other two airports.
- **Mean-bias reference** — the forecast plus -0.2305 degC, that figure being
  the mean DSM inner-training bias and nothing else.
- **ML-corrected** — the forecast plus the model's predicted residual.

Nothing was fitted on the validation year: not the model, not the climatology,
not the mean bias, not any encoding. **No SPEC edit was made and none was
authorised.**

**F46. What a DSM rehearsal win does and does not answer.** This is worth
writing down separately, because it is the reason D32 opened DSM at all and it
is easy to over-claim.

F30 recorded the honest limit on stages 1 and 2: EGLC and LFPG are 328 km apart
and were judged on **the same twelve months** in **the same weather region**, so
two wins leant on one western-European weather year seen twice. DSM attacks one
of those two axes and only one:

- **The region axis: answered.** Des Moines is 6,754 km from EGLC, in the
  continental interior, where a summer has nothing to do with a summer in
  London or Paris. The recipe wins there too, on a bias with a different shape
  and a different seasonal pattern. That is genuinely independent evidence that
  the method is not a western-European artefact.
- **The year axis: NOT answered.** DSM's rehearsal year is
  2024-08-01 to 2025-07-31 — **the same twelve months** the EGLC and CDG
  rehearsals used, because D13's dates are shared by every airport. So nothing
  here says what a different year would have done, at any airport.
- **And the comparison is not the controlled one stage 2 made between EGLC and
  CDG.** DSM changes the location **and** the target hour (D33, SPEC 4.1). A DSM
  result answers "does the recipe travel to a different region at a comparable
  local time", and must not be quoted as if only the location had moved.

**Read as: independent region, same year, two things changed.**

---

## 2026-08-18 — Session 16 note (what was and was not done)

**No new open question was raised.** Q28 remains the only open question, and it
is the owner's: SPEC 3.4's first column is headed "ICAO" while `DSM` is IEM's
own station id (session 15). Nothing in this session depends on it — the station
is addressed by the code IEM knows it as, exactly as F31's meta files record.

**Nothing was tuned, varied or re-chosen.** PART 0's comparison against
`scripts/session05_model.py` is in the output: 0 model settings differ, 1
constant differs and it is TARGET_HOUR (D33).

**Nothing was joined, built or evaluated outside inner-training and the
validation year. DSM's test year was not touched**: the two 2026 DSM chunk files
were never opened, the 2025 chunks were cut off at 2025-07-31 on load, and the
script asserts that no date on or after 2025-08-01 reached any table. Only
session 15's structural counts have ever touched the test window, and they
counted rows and report times, never a temperature value.

**The frozen bar was not judged and DSM has not passed.** SPEC 5.0's results
table still reads "DSM | pending — not yet run | —", which is correct and was
left alone.

**No SPEC edit was made and none was authorised.**

**Nothing was committed.**

---

## 2026-08-18 — Session 17: THE DSM METHOD LOCK

No model was built, run or refitted this session, no data was loaded, and
**DSM's test year was not touched**. This section is the written lock for the
third airport, mirroring what D31 did for CDG and D21 did for EGLC, plus the
correspondence check that proves it is D31 with the location and the target
hour swapped and nothing else.

**D35. DSM's method is LOCKED. This entry fully specifies what DSM's
sealed-test session will run.**

This is **D31 with the airport and the target hour swapped and nothing else
touched.** Every methodological choice below — the model, its settings, the
features, what is predicted, the pairing rule, the missing-data rule, the
references, the metric, the bar, and the one-look rule — is the same choice
D31 made, which was the same choice D21 made. Not one of them is new.

**Two things differ from D31, not one.** D31 could say "only the location
changed" (D26). D35 cannot: DSM changes the location **and** the target hour,
because 12:00 UTC at Des Moines is dawn (D33, F32, SPEC 4.1). That cost was
accepted on purpose, in advance, and is written into SPEC 4.1 and D33. It is
repeated here so the test session cannot report a DSM result as though it were
the same controlled comparison EGLC and CDG made between them.

Why it is written out separately rather than by pointing at D31: D31 names
Paris throughout and fixes the target at 12:00 UTC, so DSM's test session would
otherwise have to reach back to a CDG-named record and translate it — twice
over — while the test year was open. The whole value of a lock is that the
executing session decides nothing (D21.11, D31.11). A translation is a
decision. So the translation is done here, now, with DSM's test year still
unopened, and the test session executes this record and reports.

**D35.1 — Target.** The temperature at **18:00 UTC** at **Des Moines, Iowa
(IEM station code `DSM`, IEM network `IA_ASOS`)**, the station at latitude
41.534, longitude -93.6531, elevation 294 m — IEM's own position, per SPEC 3.4
and F31. The forecast comes from the Open-Meteo grid point that position maps
to: latitude 41.52945, longitude -93.63281, elevation 285 m, 1.76 km from the
airport with a -9 m height difference (SPEC 3.4, F31). One row per day.

The hour is **18:00 UTC, not 12:00 UTC**, and that is the one methodological
input this lock does not share with D31. 18:00 UTC is local standard noon at
Des Moines (12:00 CST in winter, 13:00 CDT in summer), which is what SPEC 4.1
asks each airport to target; 12:00 UTC there would be 06:00 local, the dawn
hour SPEC 4.1 exists to avoid. Decided on principle before any DSM data was
seen (D33) and then checked against the timezone database (F32). Daylight
saving is deliberately ignored, so the target stays one fixed UTC hour all
year.

**D35.2 — What the model predicts.** The **residual**: observed minus forecast
(SPEC 4.2). The corrected forecast is the GFS forecast plus the predicted
residual. The model never predicts temperature directly. Identical to D31.2
and D21.2.

**D35.3 — Features.** The D19 minimal set, exactly three:
```
forecast_temp_c   the GFS forecast temperature for that day at 18:00 UTC
season_sin        sin(2 * pi * year_fraction(date))
season_cos        cos(2 * pi * year_fraction(date))
```
where `year_fraction` is `(day_of_year - 1) / 365`, or `/ 366` in a leap year.
No hour-of-day feature — the hour is fixed at 18:00, so it carries no
information, which is D19's reason unchanged. No recent-observation feature,
even though SPEC 2.1d would allow one — see D19 for why. Identical to D31.3
apart from which fixed hour `forecast_temp_c` is read at, which follows from
D35.1.

**D35.4 — Model and settings.** LightGBM gradient-boosted trees (SPEC 4.4,
D12), with exactly the session 05 settings, unchanged:
```
objective=regression_l1   (absolute error, D20)   n_estimators=300
learning_rate=0.05        num_leaves=15           min_child_samples=40
subsample=1.0             colsample_bytree=1.0    reg_alpha=0.0
reg_lambda=0.0            random_state=42         n_jobs=1
deterministic=True        force_row_wise=True     verbose=-1
```
Nothing is tuned, searched or varied in the test session. Library versions are
pinned in `requirements.txt` (D24): python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0. Identical to D31.4 and D21.4. Session 16 already ran this exact
configuration at DSM, and its PART 0 proved it against
`scripts/session05_model.py`: **0 model settings differ, and of the eleven
shared constants exactly one differs — TARGET_HOUR, 12 to 18** (F45). That one
constant is D33 and nothing else.

**D35.5 — Training data for the test: the FULL D13 training window,
2021-03-24 to 2025-07-31, at DSM.** That is DSM's inner-training **and** DSM's
validation year recombined into one training set.
- Reason: the same reason D21.5 and D31.5 gave. The D18 split existed so the
  method could be rehearsed without touching the test year. The method is
  locked, so validation has finished its job, and holding a year back would
  only throw away real training data. Refitting on all non-test data before the
  single test is the standard move — and it is what both earlier airports did,
  so doing anything else here would add a third difference on top of the
  location and the hour.
- Everything fitted is fitted on this window and nothing else: the model, the
  climatology baseline (SPEC 2.1c) and the mean-bias figure.
- **Expected row count, written down before the run.** The window holds 1,591
  calendar days. Session 16 kept 1,206 inner-training rows and 365 validation
  rows (F42), both exactly as F41 predicted, so:
  ```
  inner-training rows (F42)                      1,206
  validation rows      (F42)                       365
  expected training rows for the test refit      1,571 of 1,591 calendar days
  days dropped, all of them the shared forecast gap  20 (2023-12-30..2024-01-18)
  ```
  **1,571, not 1,569.** EGLC and CDG each fitted 1,569 rows because each lost
  22 days; DSM loses only the 20 gap days, because its observation record loses
  no day at all in the training window (F41, F42). A count other than 1,571 is
  a D35.11 stop signal.
- **Note the consequence, so it is not a surprise:** the model that is tested
  is **not** the model measured in session 16. It is the same recipe fitted on
  about 30% more days, including one more full cycle of seasons. **The test
  number will not match session 16's 1.466 rehearsal figure and should not be
  expected to.** At EGLC the equivalent move moved the number by 0.125 degC
  (F16) and at CDG by 0.169 degC (F30), and in both cases most of that was the
  weather rather than the extra data.

**D35.6 — Test data: DSM, 2025-08-01 to 2026-07-31 (D13), and nothing after
it.** Data after 2026-07-31 is not used, keeping the test set exactly one
calendar year. This is DSM's own test year: the dates are the same as EGLC's
and CDG's but the data is a third airport's.

What "opened for the first time" means precisely here. Two yearly chunk files
carry the test year, and the 2025 chunks have been read with a cut-off:
```
openmeteo_previousruns_gfs_global_DSM_2026-01-01_2026-07-31.json   never read
iem_asos_DSM_2026-01-01_2026-07-31_routine.csv                     never read
openmeteo_previousruns_gfs_global_DSM_2025-01-01_2025-12-31.json   read, but
iem_asos_DSM_2025-01-01_2025-12-31_routine.csv                     cut at
                                                                   2025-07-31
```
The two 2026 DSM chunk files have never been opened by any session. The 2025
chunks were read by sessions 15 and 16, which cut them off at 2025-07-31 on
load and asserted that no date on or after 2025-08-01 reached any table (F42).
Session 15 counted row presence, gap positions and report timing across the
whole period including the test window, but never a temperature value from it
(F38, F39, F41) — a structural count, not a look at the data.

**One thing stated plainly rather than left out, because D31.6 did not state
it and it is true at all three airports.** Session 14's verify-on-contact
samples (SPEC 3.3) were pulled from the most recent weeks available, and those
weeks fall **inside** DSM's test year. Six small sample files cover
2026-07-01 to 2026-07-22, and session 14's output printed real values from
them: forecast value ranges for 2026-07-01..21, and three target-hour
observations — 2026-07-01 30.56, 2026-07-02 31.11, 2026-07-03 28.33 degC
(F34, F35). So three of DSM's 365 test days have had an observed value printed
already, and no forecast/observation pair or error figure from the test year
has ever been formed. Nothing was fitted on them, no method choice was made
from them, and the test session reads the yearly chunk files, not these
samples. **The same thing happened at EGLC in session 01 and at LFPG in
session 08**, both of whose recent samples were July 2026, so the three
airports are at least treated alike. It is written here rather than glossed
over, and raised for the owner as **Q29**, because the honest sentence is "the
test year is unopened except for three printed observation values from a
verification sample", not "never touched at all".

**D35.7 — Pairing and missing data.** The D14 rule, applied exactly as written
at EGLC and CDG: the routine report is the truth observation, each target-hour
forecast is paired with the report nearest that hour, and if no report falls
within 15 minutes of the hour the day is dropped and counted. Drop, count,
report — nothing filled, ever (SPEC 2.2). The drop counts for both the training
window and the test year are part of the output.

The location facts inside this: **DSM reports at `:54`** (F34, and IEM's own
`METAR_RESET_MINUTE` attribute says 54), where LFPG reports at `:00` and EGLC
at `:50` (SPEC 3.4). So the rule pairs 18:00 UTC with the **17:54 report — six
minutes earlier**. The next report, 18:54, is 54 minutes out, so the rule picks
17:54 without ambiguity; session 16 confirmed that no day in the whole training
window has more than one report inside the 15-minute window (F42). Six minutes
is a smaller gap than EGLC's ten, so D14's argument covers it comfortably.
**The rule is not adapted; it simply fits DSM well.** DSM also files no second
scheduled report at all (F36), so D30's question — whether to fall back to a
"special" stream — cannot even arise here.

**What the gap map says the test year should cost, written down before the
look.** From session 15, which mapped every hour without reading a value:
```
forecast-gap days in DSM's test year                            0   (F38, F41)
days lost to an off-hour-only report in DSM's test year         0   (F41)
days lost to no report near the 18:00 hour                      0   (F41)
days lost to a report in place carrying no temperature          0   (F41)
expected paired rows                                          365 of 365
expected scored days                                          365
```
**365 scored days, not 364.** Scoring loses a day only when the previous day's
observation is missing, because persistence needs it. DSM's observation record
loses no day anywhere in the five years (F41, F42), so 2025-07-31's 18:00
observation exists and the first test day, 2025-08-01, keeps its persistence
value — which D35.8 declares legal in advance. That is why DSM expects 365
scored days where EGLC and CDG each scored 363: at those airports a day inside
the test year was lost, which cost the following day as well.

This is an **expectation, not a requirement.** The test session reports the
**actual** counts and reconciles them against this table. A count that will not
reconcile is a D35.11 stop signal, not something to explain away.

**D35.8 — The four references. Anything that has to be *fitted* is fitted on
DSM's training window only.** Raw GFS and persistence are fitted on nothing —
they are just values. Climatology and the mean-bias figure are fitted, and both
come from DSM's D13 training window (SPEC 2.1c).
- **Raw GFS** — the forecast value itself, uncorrected. *Part of the bar.*
- **Persistence** — the previous calendar day's 18:00 UTC observation at DSM.
  Past values only (SPEC 2.1d). *Part of the bar.* Note that for the first test
  day, 2025-08-01, "yesterday" is 2025-07-31, which sits in the training
  window. That is a past observation, so it is legal and it will be used; it is
  written down here so it is not mistaken for leakage later. Identical to
  D31.8's and D21.8's note.
- **Climatology** — the seasonal average of the *observed* temperature at DSM
  for that position in the year, averaged over every **DSM training-window**
  observation within 7.5 days of it, measured around the circle so late
  December and early January are neighbours (SPEC 2.1c). *Informative only.*
- **Mean-bias reference** — the forecast plus one constant: the mean **DSM
  training-window** bias. *Informative only* (SPEC 5.2, D23). Worth carrying
  forward from F45: on DSM's validation year this reference **beat** raw GFS
  (1.723 against 1.748), as it did at EGLC and did not at CDG, because the
  constant available at DSM is not quite nothing (-0.2305 degC on
  inner-training; the training-window figure will differ slightly and is
  computed in the test session, not here). The model beat it by 14.9% all the
  same, so a win over it on the test year is the evidence that the correction
  is structure and not an offset.

All five methods — the four above plus the corrected forecast — are scored on
the **same set of days**, the days where every method has a value.

**One thing about the bar that is DSM-specific and is stated in advance (F45).**
Persistence is far weaker at DSM than in Europe — 4.108 degC on the validation
year against 2.523 at CDG and 2.226 at EGLC — because day-to-day swings in the
continental interior are much bigger. **So at DSM the binding half of the bar
will be raw GFS, not persistence.** This changes nothing about the bar, which
is both halves as always; it is written down so the test session reports the
raw-GFS margin as the one that decides the verdict in practice.

**D35.9 — The metric and the bar.** Mean absolute error in degrees Celsius
(SPEC 5.1). **DSM passes if the corrected forecast has a lower MAE than both
raw GFS and persistence over DSM's test year.** No numeric margin — the bar is
qualitative and stays that way (D22, SPEC 5.3). Climatology and the mean-bias
reference are reported but do not decide pass or fail. The margin is reported
prominently alongside the verdict, so a technical pass by a hair reads as what
it is (D22).

**The bar is judged once per airport, on that airport's own data (SPEC 5.0).**
EGLC's and CDG's passes do not excuse a DSM failure, and a DSM result does not
re-open either of theirs. Stage 1's 16.3% and stage 2's 13.5% are not targets
DSM has to reach and not numbers DSM is measured against; DSM is measured
against DSM's own raw GFS and DSM's own persistence, and nothing else.

**D35.10 — One look, and the result stands.** DSM's test year is opened once,
this method is run once, and whatever comes out is reported straight — pass or
fail, with the seasonal breakdown and the drop counts. A failure is an honest
finding (SPEC 2.4), not something to fix by trying again. If the result
disappoints, the response is a new decision logged here by the owner, never a
quiet re-run. Identical to D31.10 and D21.10.

Read plainly, and note that it reads differently here from how it read at CDG.
D31.10 warned that CDG's rehearsal margin was half EGLC's, so a failure was a
real possibility. DSM's rehearsal margin is the widest of the three — 16.1%
(F45) — so a failure is less likely on the face of it. **That is not a reason
to expect a pass.** The rehearsal margin is not the test margin at either
earlier airport, DSM's raw GFS error is much larger and much more variable than
Europe's, and D35.12 names a handful of extreme days that could move a
365-day average on their own. A DSM failure remains an outcome this project
reports rather than avoids.

**D35.11 — Deviation is a stop signal.** If DSM's test session finds any reason
to depart from this record — a setting that does not fit, a missing file, a
count that will not reconcile against D35.5 or D35.7, a tempting small
improvement — it **stops and raises it with the owner**. It does not decide on
the fly with the test year open. Any change to the above is a new DECISIONS
entry made deliberately, not an adjustment made mid-run. Identical to D31.11
and D21.11.

**D35.12 — The warm-end watch-item, recorded before the look and NOT acted
on.** This is inside the lock so that any inspection after the test is honest:
the place to look was named before anyone knew what the result was.

F44 measured, at the 18:00 target hour on inner-training, that DSM's forecast
overshoots badly at the warm extreme, and that the overshoot grows with the
forecast rather than sitting on a few odd days:
```
selection                 days  mean bias  mean |bias|
forecast >= 30 degC        114     -3.089        3.449
forecast >= 34 degC         37     -4.838        4.838
forecast >= 38 degC         13     -6.438        6.438
forecast >= 40 degC          5     -7.068        7.068

forecast range at 18:00 UTC, inner-training : -21.70 to +42.70 degC
observed range at 18:00 UTC, inner-training : -23.28 to +36.67 degC
days with a forecast above the observed maximum : 17
worst single day: 2023-07-27, forecast 40.9, observed 30.6, gap 10.3 degC
```
Two consequences, both recorded and neither acted on:
1. **This is the largest single piece of learnable structure at DSM** and much
   of why the rehearsal did as well as it did (F45).
2. **It rests on very few days.** Only 5 inner-training days reach 40 degC at
   18:00 and only 21 reach 36. A tree model cannot extrapolate past the range
   it was fitted on, so on a test day hotter than anything in training it
   applies the correction it learned at the top of that range.

**This is not a reason to change the method, and the method does not change.**
It is locked. If DSM's test result behaves oddly — a large swing either way, a
summer that does not match the rehearsal, a worst-miss far outside the others —
**this handful of extreme warm days is the first place to look**, and looking
there is a description of what happened, never a licence to re-run or adjust
anything (D35.10, D35.11).

**D35.13 — One data-source fact that is stronger at DSM than at CDG, recorded
so the test session states it correctly.** At LFPG, F6's value-by-value check
of `gfs_global` against `gfs_seamless` was never run (Q20's closing note), so
stage 2's first airport can say "this is exactly the `gfs_global` series" but
not "and `gfs_seamless` would have given the same". At DSM the check **was**
run (F40) and it gave a different answer from EGLC's: on recent dates the two
strings return **different** data, 259 of 264 hours differing by up to
12.3 degC, from a different grid point. Every DSM chunk was pulled with
`gfs_global` (read back out of the saved `.meta.txt` URLs), so DSM's dataset is
exactly NCEP GFS and is unaffected. The test session should say that, and must
**not** say that the two strings agree at DSM — they do not. This is a fact
about the data source, not a methodological difference; it changes nothing in
D35.

---

**The D31 ↔ D35 correspondence check.** Every D31 sub-point set beside its D35
counterpart. Two kinds of intended difference are expected this time, not one:
`LOCATION` (the airport and what follows from it) and `HOUR` (the target hour,
per D33, and what follows from it). Anything else appearing in that column
would be a stop signal.

```
point  subject                D31 (LFPG)                D35 (DSM)                 differs?
.1     target hour            12:00 UTC                 18:00 UTC (D33)           HOUR
.1     why that hour          local midday in Europe    local standard noon       HOUR
.1     airport                Paris CDG / LFPG          Des Moines / DSM          LOCATION
.1     station position       49.0153 / 2.5344 / 109 m  41.534 / -93.6531 / 294 m LOCATION
.1     position source        IEM's own metadata (F17)  IEM's own metadata (F31)  same
.1     grid point             49.027008 / 2.578125      41.52945 / -93.63281      LOCATION
.1     grid distance/height   3.44 km, 0 m              1.76 km, -9 m             LOCATION
.1     row granularity        one row per day           one row per day           same
.2     what is predicted      residual = obs - fcst     residual = obs - fcst     same
.2     how corrected is made  fcst + predicted resid    fcst + predicted resid    same
.3     features               3: fcst temp, sin, cos    3: fcst temp, sin, cos    same
.3     fcst temp read at      12:00 UTC                 18:00 UTC                 HOUR
.3     year_fraction          (doy-1)/365 or /366       (doy-1)/365 or /366       same
.3     excluded features      no hour, no recent obs    no hour, no recent obs    same
.4     library and model      LightGBM GBDT             LightGBM GBDT             same
.4     objective              regression_l1             regression_l1             same
.4     n_estimators           300                       300                       same
.4     learning_rate          0.05                      0.05                      same
.4     num_leaves             15                        15                        same
.4     min_child_samples      40                        40                        same
.4     subsample              1.0                       1.0                       same
.4     colsample_bytree       1.0                       1.0                       same
.4     reg_alpha / reg_lambda 0.0 / 0.0                 0.0 / 0.0                 same
.4     random_state           42                        42                        same
.4     n_jobs                 1                         1                         same
.4     deterministic          True                      True                      same
.4     force_row_wise         True                      True                      same
.4     verbose                -1                        -1                        same
.4     pinned versions        py 3.12.2, np 2.5.2,      py 3.12.2, np 2.5.2,      same
                              lightgbm 4.7.0            lightgbm 4.7.0
.4     tuning allowed         none                      none                      same
.5     training window        2021-03-24..2025-07-31    2021-03-24..2025-07-31    same
.5     refit on inner+valid   yes                       yes                       same
.5     what else is fitted    model, climatology,       model, climatology,       same
                              mean bias -- all on it    mean bias -- all on it
.5     rows fitted on         1,569 (1,204 + 365, F27)  1,571 (1,206 + 365, F42)  LOCATION
.5     calendar days in it    1,591                     1,591                     same
.5     mismatch warning       test != 1.377 rehearsal   test != 1.466 rehearsal   LOCATION
.6     test window            2025-08-01..2026-07-31    2025-08-01..2026-07-31    same
.6     nothing used after     2026-07-31                2026-07-31                same
.6     files opened first     the two 2026 LFPG         the two 2026 DSM          LOCATION
       time                   chunks                    chunks
.6     verification samples   not stated in D31         stated: 3 test-day obs    LOCATION
       inside the test year   (the same is true of      values printed in F34/F35 (see Q29)
                              LFPG, session 08)
.7     pairing rule           D14, nearest report,      D14, nearest report,      same
                              15-minute tolerance       15-minute tolerance
.7     report minute          :00                       :54                       LOCATION
.7     pairing offset         0 min (exact match)       6 min (17:54 -> 18:00)    LOCATION
                                                                                  + HOUR
.7     missing data           drop, count, report,      drop, count, report,      same
                              never fill (SPEC 2.2)     never fill (SPEC 2.2)
.7     second scheduled       :30 "special" exists,     none exists at all        LOCATION
       stream                 refused (D30)             (F36), D30 cannot arise
.7     expected fcst-gap days 0 in test year (F22)      0 in test year (F38)      same
.7     expected obs-loss days 1: 2026-07-08 (F25)       0 (F41)                   LOCATION
.7     expected paired rows   364 of 365                365 of 365                LOCATION
.7     expected scored days   363 (persistence loses    365 (nothing lost, so     LOCATION
                              2026-07-09)               nothing follows)
.7     drop counts reported   training and test         training and test         same
.8     reference 1            raw GFS, in the bar       raw GFS, in the bar       same
.8     reference 2            persistence, in the bar   persistence, in the bar   same
.8     persistence's source   previous day's 12:00 obs  previous day's 18:00 obs  HOUR
.8     first-day note         2025-07-31 is training,   2025-07-31 is training,   same
                              legal, will be used       legal, will be used
.8     reference 3            climatology, +-7.5 days   climatology, +-7.5 days   same
                              circular, informative     circular, informative
.8     reference 4            mean-bias, informative    mean-bias, informative    same
.8     mean-bias note carried worse than raw GFS on     better than raw GFS on    LOCATION
       from the rehearsal     validation (F29)          validation (F45)
.8     which half binds       not stated (both close)   raw GFS, not persistence  LOCATION
                                                        (F45)
.8     what fitted refs use   training window only      training window only      same
                              (SPEC 2.1c)               (SPEC 2.1c)
.8     scoring set            same days for all five    same days for all five    same
.9     metric                 MAE in degC (SPEC 5.1)    MAE in degC (SPEC 5.1)    same
.9     the bar                beat raw GFS AND          beat raw GFS AND          same
                              persistence               persistence
.9     numeric margin         none, qualitative (D22)   none, qualitative (D22)   same
.9     margin reported        yes, prominently          yes, prominently          same
.9     who decides pass/fail  raw GFS + persistence     raw GFS + persistence     same
.9     judged once per        that airport's own data   that airport's own data   same
       airport                (SPEC 5.0)                (SPEC 5.0)
.10    number of looks        one                       one                       same
.10    number of runs         one                       one                       same
.10    failure handling       reported straight, not    reported straight, not    same
                              re-run                    re-run
.11    deviation handling     stop and raise with       stop and raise with       same
                              the owner                 the owner
.12    watch-item             none recorded             warm-end overshoot        LOCATION
                                                        (F44), see below
.13    gfs_seamless check     never run at LFPG         run at DSM, and they      LOCATION
                              (Q20)                     DIFFER (F40)
```

**Verdict of the check: no methodological choice differs.** The `HOUR` rows are
all one decision — D33's target hour — and the three things that follow from
it: which hour the feature is read at, which hour persistence looks back to,
and which report the pairing rule lands on. The `LOCATION` rows are the same
four kinds D31's own check found, plus two new kinds that record facts rather
than choices:

1. **which airport it is** — its name, station code, network, position and grid
   point (D35.1);
2. **which files hold its data** (D35.6);
3. **when the station files its routine report** — `:54` at DSM against `:00`
   at LFPG — which changes the pairing *offset* the D14 rule produces, not the
   rule (D35.7);
4. **how many rows and drops follow from that airport's own record** — 1,571
   expected training rows, 0 expected test-year drops, 365 expected scored days
   (D35.5, D35.7);
5. **what the rehearsal already showed about the references at this airport** —
   the mean-bias reference beats raw GFS here, persistence is far weaker here
   (D35.8). These carry no requirement; they are context so the test session
   reports the right thing as the deciding margin;
6. **two facts about the data and the record** — the warm-end watch-item
   (D35.12) and the `gfs_seamless` result (D35.13). Neither changes a setting,
   a date, a feature, a reference or the bar.

Every setting, every date, every feature, every reference, the metric, the bar,
the one-look rule and the stop-signal rule are the same in D21, D31 and D35.
Nothing was added to D35 that D31 does not require, and nothing D31 requires
was left out of D35.

**The one difference that must not be smoothed over, stated again because it is
the point of the whole check.** D31's correspondence table had no `HOUR`
column, and it could say in one line that only the location changed (D26).
D35's has one. **DSM is the first lock where the target hour is among the
intended differences**, and that is D33's deliberate choice, taken before any
DSM data was seen, with its cost written into SPEC 4.1: a DSM result answers
"does the recipe travel to a different region at a comparable local time", and
must **not** be quoted as if it were the controlled, location-only comparison
EGLC and CDG make between them (D33, F46).

---

## 2026-08-18 — Open question raised by session 17 (not acted on)

**Q29. The verify-on-contact samples sit inside each airport's test year, and
no lock has said so until now.** SPEC 3.3 requires two things to be checked by
pulling real data at every new airport, and the natural sample to pull is the
most recent few weeks. At all three airports that sample landed inside the
sealed test window (2025-08-01 to 2026-07-31):
- **EGLC**, session 01: forecast and observation samples for 1–21 July 2026;
  F2 printed gap counts and F1 the archive's behaviour.
- **LFPG**, session 08: the same three weeks; F18 printed the minute spread and
  F20 the forecast value range 8.7 to 36.7 degC.
- **DSM**, session 14: the same three weeks; F34 printed three target-hour
  observations (2026-07-01 30.56, 2026-07-02 31.11, 2026-07-03 28.33 degC) and
  F35 printed 72 hourly values for 2026-07-01..03 while checking units.

**What this is not.** It is not leakage into any model: nothing was fitted on
those values, no method choice was made from them, no forecast-observation pair
or error figure from a test year has ever been formed, and each test session
reads the yearly chunk files rather than the samples. Nor is it unequal
treatment — all three airports were sampled the same way in the same weeks.

**What it is.** STATUS and several log entries say a test window has been
touched only by structural counts, "never a temperature value". For the
verify-on-contact samples that sentence is slightly too strong: a handful of
values inside the test window were printed at each airport, months before the
look. D35.6 now says so for DSM. D21.6 and D31.6 do not say it for EGLC and
LFPG, and those entries are closed and append-only.

**Two things for the owner, and neither was acted on.** Whether the wording in
STATUS should be corrected to match (this session did not change any claim it
did not write). And whether future airports should take their verify-on-contact
samples from **outside** the D13 period entirely — after 2026-07-31, which D13
does not use at all — the way session 15 already chose to do for F40's recent
window when it noticed the same problem (F40's own note). That would cost
nothing and would remove the question at the next airport.

---

## 2026-08-18 — Session 18: THE DSM SEALED-TEST RESULT (the third airport is decided)

DSM's test year was opened for the first and only time. The method locked in
D35 was executed and nothing was decided, tuned, swapped or re-run. This
section is the third airport's result of record. The script is
`scripts/session18_test.py` and the full real output is
`notes/session-18-check-output.txt`.

**F47. DSM PASSES. At Des Moines the corrected forecast beats both raw GFS and
persistence on the held-out test year. The recipe travels to another
continent — on the narrowest margin of the three airports.**

The verdict first, because that is what the session was for:

```
                        MAE degC   part of bar?
Raw GFS                    1.815   YES
Persistence                4.003   YES
Climatology                5.030   no  (informative)
Mean-bias reference        1.760   no  (informative)
ML-corrected               1.700   the claim

vs Raw GFS       BEATEN   1.700 against 1.815  ->  0.115 degC better (6.3%)
vs Persistence   BEATEN   1.700 against 4.003  ->  2.303 degC better (57.5%)
```

**DSM passes on the frozen bar (SPEC 5.3, 5.0, D35.9): the corrected forecast
has a lower MAE than both raw GFS and persistence over 2025-08-01 to 2026-07-31
at Des Moines.** The margin is stated prominently because D22 requires it. It is
**0.115 degC, a 6.3% cut against raw GFS** — a clear pass, but the smallest
margin any airport has returned on a sealed test year (EGLC 16.3%, CDG 13.5%),
and smaller than DSM's own rehearsal margin. That reading is in F48.

**D35.8 named the deciding half of the bar in advance and it was right.**
Persistence at DSM is 4.003 degC, **2.21 times raw GFS**, because day-to-day
swings in the continental interior are much bigger. So the raw-GFS comparison is
what decides the verdict in practice; the persistence half is met by a wide
margin that says little. Both halves are still required by the bar and both were
met.

The full table, all five methods on the same 365 days:

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.815     -0.641      2.423       10.09
Persistence                4.003     +0.000      5.453       20.56
Climatology                5.030     +0.172      6.393       21.81
Mean-bias reference        1.760     -0.369      2.366        9.82
ML-corrected               1.700     -0.444      2.333       12.44
```

**It beats the mean-bias reference too, but only by 3.4% (1.700 against
1.760), and that is the number to read carefully.** The mean-bias reference is
the forecast plus one constant, with no learning in it — the comparison that
separates "the model learned real structure" from "the model found an offset"
(D23). At EGLC the model beat it by 15.7% and at CDG by 13.0%. At DSM it beats
it by 3.4%.

Two things explain that and both are honest:

- **The constant available at DSM is the largest of the three.** The mean
  training-window bias is **-0.2715 degC**, against -0.1479 at EGLC (F16) and
  -0.0600 at CDG (F30). So more of the correction's win here *is* a constant
  offset than at either European airport — as D35.8 said in advance, the
  mean-bias reference **beats** raw GFS at DSM (1.760 against 1.815), which it
  did at EGLC and did not at CDG.
- **What is left over is still structure, and it is still a win.** 0.060 degC on
  365 days, in the same direction the rehearsal found (14.9%, F45). But the
  claim "the correction learned structure rather than an offset" is on its
  thinnest evidence yet at this airport, and it should be quoted at 3.4%, not at
  stage 1's 15.7%.

**Day by day, not just on average.** The correction was closer to the truth than
raw GFS on **195 of 365 days (53.4%)** and further away on 170 (46.6%), with no
day where it made no difference. That is the lowest of the three airports —
EGLC 60.9% (F16), CDG 58.7% (F30) — so at DSM the correction nudges the right
way barely more often than not, and its margin comes from the *size* of the
nudges rather than their frequency. That is the same shape session 16 saw on the
rehearsal (55.6%, F45).

**Per season, the correction helped in three of the four:**

```
season         days   raw GFS   ML-corr    change   persistence
winter DJF       90     1.652     1.639    -0.013         5.160
spring MAM       92     1.964     2.159    +0.196         5.254
summer JJA       92     1.921     1.590    -0.331         2.360
autumn SON       91     1.718     1.408    -0.310         3.254
```
("change" is corrected MAE minus raw GFS MAE. Negative means better than raw
GFS.) **Spring is the season it makes worse, by 0.196 degC — and that is a
fourth distinct answer.** Winter was the losing season at EGLC and CDG in every
run; summer was DSM's losing season in its rehearsal (F45); spring is DSM's
losing season on the test year. Summer and autumn carry the result, 0.331 and
0.310 degC better. Winter is a dead heat.

**The test-year drop count, and the reconciliation D35.7 existed for. Every
line matched, and DSM is the first airport to lose no test day at all.**

```
cause                                                    predicted  actual  verdict
forecast-gap days in the test year (F38)                         0       0  MATCHES
days lost to an off-hour-only report (F41)                       0       0  MATCHES
days lost to no report near the 18:00 hour (F41)                 0       0  MATCHES
days lost to a report in place carrying no temperature (F41)     0       0  MATCHES
paired rows expected                                           365     365  MATCHES
days scored (nothing lost, so nothing follows)                 365     365  MATCHES
```

D35.7 wrote those numbers down in session 17, from session 15's gap map, before
DSM's test year was opened. **A prediction made before the look is a stronger
check than a count made after it**, and this is the third time it has paid off —
F27 and F30 at CDG, F42 and now F47 at DSM. Nothing was filled (SPEC 2.2).

Scoring loses no further day either. Persistence needs the previous day's
observation, and DSM's observation record loses no day anywhere in five years
(F41), so the first test day 2025-08-01 keeps its persistence value from the
2025-07-31 18:00 observation (+23.9 degC) — a past observation, sitting in the
training window, declared legal in advance by D35.8 so it is not mistaken for
leakage. EGLC and CDG each scored 363 because each lost a day inside its test
year and that cost the following day as well.

**The pairing behaved exactly as F34 and F42 said it would.** Across all 1,956
loaded days the pairing offset is **-6 minutes on 1,955 of them** (DSM's `:54`
report serving 18:00) and -2 minutes on one — 2024-06-07, in training, which F42
already named. **On all 365 test days the offset is -6 minutes.** No day in the
whole loaded period has more than one report inside D14's 15-minute window, so
the pairing is never ambiguous at DSM. Not one report was dropped for being more
than 15 minutes out, and not one carried no temperature.

**The training refit reconciles exactly**, which is the check that the harness
has not drifted (D35.11): **1,571 rows** out of 1,591 calendar days, of which
1,206 are dated on or before 2024-07-31 and 365 on or after 2024-08-01 — session
16's published counts (F42) to the row. That is 1,571 and not the 1,569 both
European airports fitted, exactly as D35.5 predicted, because DSM loses only the
20 shared forecast-gap days.

**The test number against session 16's rehearsal number.** D35.5 said in advance
these would differ and should not be expected to match. They differ — and for
the first time the test margin is **smaller** than the rehearsal margin:

```
method                  s16 valid   s18 test  difference
Raw GFS                     1.748      1.815      +0.067
Persistence                 4.108      4.003      -0.105
Climatology                 4.772      5.030      +0.258
Mean-bias reference         1.723      1.760      +0.037
ML-corrected                1.466      1.700      +0.234
days scored                   365        365

margin over raw GFS:  validation +0.282 (16.1%)   test +0.115 (6.3%)
```

Season by season, that is where it went:

```
season        s16 raw   s16 ML  s16 chg   s18 raw   s18 ML  s18 chg
winter DJF      1.687    1.273   -0.414     1.652    1.639   -0.013
spring MAM      1.958    1.774   -0.184     1.964    2.159   +0.196
summer JJA      1.532    1.593   +0.061     1.921    1.590   -0.331
autumn SON      1.816    1.218   -0.598     1.718    1.408   -0.310
```

**Raw GFS was about equally hard in both years in winter and spring** (1.687
against 1.652, 1.958 against 1.964), so the loss is not the weather being
easier: **the correction simply stopped helping in winter and turned harmful in
spring.** Summer moved the other way — a much harder summer for GFS (1.921
against 1.532) and the correction turned a small loss into its second-best
season. Autumn stayed strong at both. Net, the two gains did not cover the two
losses, and 16.1% became 6.3%.

**Feature importances, the sanity check that it used what it was meant to:**

```
feature                 gain  gain share   splits   s16 share  s16 splits
forecast_temp_c       5694.0       43.4%    1,809       45.0%       1,850
season_sin            4736.8       36.1%    1,400       37.3%       1,366
season_cos            2701.1       20.6%      991         17.7%       984
```
Nothing is ignored and nothing dominates. Forecast temperature leads with
`season_sin` close behind — the same picture session 16 found, and the picture
F43 predicts for an airport carrying a strong version of both bias structures.
Beside the other two sealed tests: EGLC 51.8 / 24.5 / 23.7, CDG 38.2 / 34.9 /
26.9. DSM sits between them, which is what "both structures at once" looks like
from this direction.

**The corrections applied stayed the size the rehearsal made them.** Mean
-0.197 degC, standard deviation 1.658, range -5.2 to +3.0, mean absolute size
1.331 — against session 16's mean -0.116, standard deviation 1.607, range -5.3
to +3.1 (F45). Both are about twice the size of Europe's nudges (standard
deviation 0.720 at EGLC, 0.751 at CDG). The model did not start making bigger
swings on unseen data.

For the record, in-sample MAE on the training window was 1.222 degC against raw
GFS's 1.921 (session 16's inner-training figure was 1.221). A model always looks
better on the data it was fitted to; that figure proves nothing and is here only
so it is not a surprise later.

**Climatology ran 0.172 degC cold on DSM's test year**, against -0.074 on its
validation year (F45). At EGLC the same figure was +0.773 and at CDG +0.918
(F16, F30), both saying their test year was much warmer at the target hour than
the training average for the same dates. **DSM's is close to neutral**, so the
"warm test year" that flattered the two European airports is a western-European
fact, not a fact about 2025-08 to 2026-07 everywhere.

**D35.12's warm-end watch-item, described and NOT acted on.** D35.12 named this
before the look precisely so that any inspection afterwards is honest. The
answer is that the warm end is **not** where this result went wrong — it is
where the correction did its best work:

```
selection                 test days  mean bias   raw MAE   ML MAE   change
forecast >= 30 degC              31     -2.485     2.661    1.554   -1.107
forecast >= 32 degC              13     -4.395     4.395    1.913   -2.483
forecast >= 34 degC              11     -4.774     4.774    2.162   -2.612
forecast >= 36 degC               3     -6.687     6.687    2.322   -4.365
forecast >= 38 degC               2     -7.240     7.240    3.211   -4.029
forecast >= 40 degC               2     -7.240     7.240    3.211   -4.029

test days with a forecast above the training-window maximum (42.70 degC): 0
forecast range at 18:00 UTC, training window : -21.70 to +42.70 degC
observed range at 18:00 UTC, training window : -23.28 to +36.67 degC
```

The overshoot F44 measured on inner-training is present in the test year at
about the same size, and the correction removes most of it — on the two hottest
days it cuts a 7.24 degC error to 3.21. **No test day asked the model to
extrapolate past its training range**, so D35.12's second worry (a tree model
cannot extrapolate) never arose. This is a description of what happened, not a
licence to re-run or adjust anything (D35.10, D35.11).

**The five worst single misses of the test year, for the record:**

```
date          forecast  observed   raw err    ML err  correction
2026-04-02       21.20     11.11     10.09     12.44       +2.35
2026-07-27       40.50     32.22      8.28      4.25       -4.03
2025-08-09       31.20     23.33      7.87      5.77       -2.10
2025-08-18       35.40     27.78      7.62      2.39       -5.23
2026-07-25       34.20     26.67      7.53      3.50       -4.03
```

**The correction's own worst miss is the ML column's 12.44 degC on
2026-04-02** — a spring day where GFS was already 10.09 degC too warm and the
model, reading a spring date, pushed it a further 2.35 degC the wrong way. That
is the same spring loss the season table shows, seen on one day. The other four
are warm-end days and the correction helped on every one of them. This is why
the ML "worst miss" (12.44) is larger than raw GFS's (10.09) even though the ML
average is better.

**The lock was checked before anything ran.** PART 0 does five checks and all
five passed: all 23 values D35 fixes matched what the script used (0
mismatches); the model settings matched `scripts/session05_model.py` setting by
setting (0 differ) and `scripts/session13_test.py` likewise (0 differ); of the
fourteen shared constants **exactly one differs — TARGET_HOUR, 12 to 18** — and
the script asserts that it is the only one, so the shared split dates, chunks,
gap dates, climatology window and feature names are provably identical to CDG's
sealed test; eight functions are character-identical to session 13's
(`all_days`, `year_fraction`, `mae`, `describe`, `_literal`, `top_level`,
`func_source`, `climatology_from_training`); and the four that differ have their
full diffs printed. Those four are `features` (one docstring line naming the
hour), the two loaders (the station code in the file names, the function names,
and DSM's `:54` reporting) and `fit_on_training` (printed labels only). Every
one of them was also compared with its docstring and name stripped out:
`features` and `load_forecast_target_hour` are **identical in executable code**.
So "the airport and the hour changed, and nothing else" is checked in code here,
not argued.

**What this session did not do, on purpose.**
- **The script was run once and not repeated.** D35.10 says the method is run
  once, so no second run was made to confirm byte-identical output, exactly as
  sessions 07 and 13 chose. Determinism rests on the fixed seed,
  `deterministic=True`, `n_jobs=1`, the pinned versions in `requirements.txt`
  (D24) and the byte-identical repeat runs already recorded in F14, F15, F29 and
  F45.
- **Nothing was analysed beyond the locked run.** The spring loss is described
  from the figures the single run printed. No further pass was made over the
  test year to explain it.
- **The deeper evaluation (SPEC 5.4) stays optional and was not opened.** D29
  made it optional and blocking nothing. The seasonal table above is context,
  not a significance test. The project still has no formal significance figure
  for any airport's win — and at 6.3% on 365 days that limit now bites harder
  than it did at 16.3%.
- **Nothing was committed.**

**One data-source fact stated correctly, per D35.13.** Every DSM forecast chunk
was pulled with `models=gfs_global` (D16, F38, read back out of the saved
`.meta.txt` URLs), so **this result is genuine NCEP GFS by construction of the
D16 pin**. At DSM the `gfs_global` versus `gfs_seamless` comparison **was** run
(F40) and the two strings **differ** on recent dates — 259 of 264 hours, by up
to 12.3 degC, from a different grid point, because Des Moines is inside CONUS.
So it must not be said that the two strings agree at DSM; they do not. At LFPG
the comparison was never run at all (Q20), so stage 2's first airport still
cannot make the by-construction claim stage 1 and DSM can.

**No SPEC edit was made this session, and none was authorised.** The bar was
judged as written. SPEC 5.0's results table still reads "DSM | pending — not yet
run | —", and SPEC 1, 3.4 and 6 still describe DSM as in progress; those are now
out of date and are flagged for the owner in this session's consistency check
rather than changed here.

---

**F48. What three passes now establish, and what they still do not. The most
important number in F47 is the one that went DOWN.**

This is written separately because it is easy to over-claim three passes, and
because the direction of DSM's test margin is genuinely new information.

**1. The region axis of F30's caveat is now answered.** F30 recorded that EGLC
and LFPG are 328 km apart in one weather region, so two wins leant on one
western-European weather year seen twice. Des Moines is 6,754 km away in the
continental interior, with a bias of a different shape (F43), a different
seasonal pattern (F45, F47) and roughly double the persistence error. **The same
recipe, unchanged, wins there too.** That is genuinely independent evidence that
the method is not a western-European artefact.

**2. The year axis is still not answered, and cannot be by this result.** D13's
split dates are shared by every airport, so DSM's test year is **the same twelve
months** EGLC's and CDG's were. Three passes on one calendar year are not three
independent draws of weather. F46 wrote this down before the look and it stands
unchanged.

**3. DSM is not the controlled comparison EGLC and CDG make between them.** DSM
changed the location **and** the target hour (D33, SPEC 4.1, D35, F46). A DSM
result answers "does the recipe travel to a different region at a comparable
local time". It must not be quoted as if only the location had moved.

**4. The new information: at DSM the test margin is SMALLER than the rehearsal
margin, and that is the first time.**

```
airport   rehearsal margin over raw GFS   test margin over raw GFS
EGLC              +0.074 degC (6.0%)          +0.202 degC (16.3%)
CDG               +0.050 degC (3.5%)          +0.188 degC (13.5%)
DSM               +0.282 degC (16.1%)         +0.115 degC (6.3%)
```

F16 and F30 both read their rise the same way: most of the gap was the weather,
not the model — the shared test year had a hard summer and an easy winter for
GFS in western Europe, and that flattered a correction that works best in
summer. **DSM is the test of that reading, and it supports it.** The same twelve
months at Des Moines were not a year that suited the correction: winter went
from a 0.414 degC gain to nothing, spring flipped from a gain to a 0.196 degC
loss, and only summer improved. Climatology's near-neutral bias at DSM (+0.172
against +0.773 and +0.918 in Europe) says the same thing from another direction
— that test year was warm in Europe, not everywhere.

**So the honest summary across all three airports is: the method wins on both
years at all three places, by 6.0%, 3.5% and 16.1% on the three rehearsal years
and by 16.3%, 13.5% and 6.3% on the one shared test year — and the spread inside
each of those two groups is mostly what the weather did.** The range across six
airport-years is roughly 3% to 16%. That is the size of win this method
delivers; anyone quoting 16.3% alone is quoting the best of six.

**5. One claim is weaker at DSM than at either European airport.** The margin
over the mean-bias reference — the evidence that the correction learned
structure rather than a constant — is 3.4% at DSM against 15.7% at EGLC and
13.0% at CDG, and DSM has the largest constant available (-0.2715 degC). The
claim still holds in the same direction at all three airports and it held on
DSM's rehearsal by 14.9%. But it is thinner here, and the honest statement is
that at DSM most of the win is the constant plus a modest amount of structure,
where in Europe almost all of it was structure.

**6. Nothing here re-opens EGLC's or CDG's results.** SPEC 5.0 judges each
airport once on its own data. F16 and F30 stand as written; F47 stands beside
them, not above or below them.

---

## 2026-08-18 — Open question raised by session 18 (not acted on)

A third airport has passed, which opens a choice that is the owner's to make. It
is recorded here and was not acted on. This mirrors Q17, raised when stage 1
passed, and Q24, raised when stage 2's first airport passed.

**Q30. Three airports have now passed on the same twelve months — what opens
next?** Three branches, and the owner picks. Nothing about any of them was
written or started.
- **More airports.** Stage 2 is the shape of the work and holds as many airports
  as the owner opens (D34, SPEC 6). D32's plan was "temperate and well-behaved
  first, then ramp up difficulty", and DSM was the easy off-continent step. A
  harder airport — coastal, mountainous, tropical — would test the method where
  it has not been tested. Each one is the same five steps: verify on contact,
  pull and map, join and rehearse, lock, test once.
- **A different test year — the remaining half of the F30 caveat.** F46 and F48
  both record that D13's dates are shared, so all three passes rest on one
  calendar year. Answering that means testing on different twelve months, which
  would need D13 revisited deliberately and a written decision about what a
  second test year means for airports whose single authorised look is already
  spent (D21.10, D31.10, D35.10). **This is the axis no result so far touches**,
  and it is the one F48 names as still open.
- **Stage 3 — pooling.** SPEC 6's next stage combines airports into one model
  with location-describing features. It inherits the solar-standard-noon target
  hour already in use (SPEC 4.1, D27, D33). **Stage 3 is not opened and nothing
  about it has been written or started.**

**Two things worth deciding alongside whichever branch is chosen, neither of
them a separate question.** First, all three airports' single looks are now
spent, so 2025-08-01 to 2026-07-31 is no longer a held-out year for this method
at any of them; anything measured on it from here on is measured on data the
method has been compared against once already. Second, F48's range — 3% to 16%
across six airport-years — is the figure to carry forward, not stage 1's 16.3%.

---

## 2026-08-19 — Session 19 decisions (a fourth airport opens, Southern Hemisphere)

Q30's first branch — more airports — is the one the owner picked. Both entries
below were written before any Australian data was pulled.

**D36. A fourth airport is opened: inland eastern Australia.** Both
Canberra (YSCB) and Dubbo (YSDU) exist in IEM's `AU__ASOS` network with
authoritative coordinates (F49). Dubbo was chosen; see F49 for the comparison
and the reasoning.
- **What it is for.** Every airport so far — EGLC, LFPG, DSM — is in the
  Northern Hemisphere, and F46/F48 both name the axis no result yet touches:
  three passes on **the same twelve months** (D13's shared dates), so nothing
  so far tests whether the recipe travels to a genuinely different weather
  cycle. A Southern Hemisphere airport is the direct attack on that: flipped
  seasons, a different hemisphere's calendar, and — because season-of-year is
  one of the model's three features (D19) — a real stress test of whether the
  `season_sin`/`season_cos` features generalise or were quietly learning
  "Northern Hemisphere summer is warm" rather than "summer is warm".
- **Why inland eastern Australia specifically.** The owner's plan, stated in
  the session 19 prompt, continues D32's "temperate and well-behaved first"
  approach: inland and flat-ish, so GFS stays reliable and local terrain
  effects stay mild, the same reasoning that chose DSM over a harder airport.
  A coastal, mountainous or tropical airport is harder and is deliberately
  left for later (Q30's own "ramp up difficulty" branch).
- **This is the "more airports" branch of Q30.** Stage 3 (pooling) and a
  second test year (the other two Q30 branches) are **not** opened and
  nothing about either was written or started.
- Everything else is reused unchanged from the three airports already in the
  project, pending verification that this airport's data supports it: the two
  data sources (SPEC 3.1, 3.2), the model string pin (D16), temperature only
  (D17), the split dates (D13), the pairing rule (D14), the drop-count-report
  rule (SPEC 2.2), the minimal three features (D19), the model settings
  (D21.4) and the frozen qualitative bar (SPEC 5.3, D22). **One thing is not
  reused — the target hour. See D37.**

**D37. This airport's target hour is local standard noon — 02:00 UTC — not
12:00 or 18:00 UTC.**
- **The problem, stated in the session prompt before any data was pulled.**
  Eastern Australia's standard-time offset is UTC+10. Local standard noon
  (12:00) is therefore 02:00 UTC — a third distinct target hour, after 12:00
  (EGLC, LFPG) and 18:00 (DSM). This is D33's convention applied a second
  time: hold *local midday* constant across airports rather than the UTC
  hour, because the UTC hour is a different time of day at every longitude
  and the difference is small across 328 km and large across an ocean or a
  hemisphere.
- **The decision.** The target is **local standard noon, 02:00 UTC**, with
  daylight saving deliberately ignored so the target stays a fixed UTC hour
  all year, exactly as D33 does for DSM. New South Wales observes daylight
  saving (AEDT, October–April); the **standard** offset (AEST, UTC+10) is
  used regardless, per the session prompt's explicit instruction and D27's
  convention.
- **Checked against the timezone database before being trusted, and it
  matches exactly.** See F50. This is the same discipline F32 applied for
  DSM: state the expected hour on principle first, then confirm it against
  real timezone data rather than assuming.
- **The honest consequence, recorded plainly, exactly as D33 recorded it for
  DSM.** This airport changes **both** the location and the target hour
  against EGLC and LFPG, so D26's "only the location changed" does not hold
  for it either — it is now the second airport of which that is true. Read a
  result from this airport as: independent hemisphere, independent season
  cycle, same shared D13 twelve months, two things changed from the European
  pair (location and target hour) — the same honest reading D33/F46 give DSM.
- **Chosen on principle, before any data from this airport was seen**, in the
  same style rule 2.4 requires for the frozen bar.
- **No SPEC edit was made or authorised this session.** SPEC 4.1 already
  states the local-midday principle generally (D34 generalised it precisely
  so a fourth airport would not need a fresh conflict the way DSM's D33 did
  against the old single-hour wording). Adding this airport to SPEC 3.4's
  table, once the full pull confirms the data, is a later session's job.

---

## 2026-08-19 — Session 19 findings (airport #4 verified on contact)

This session pulled small samples only. **No full dataset was pulled, nothing
was joined, built, trained or evaluated, and nothing from stage 1, CDG or DSM
was touched or re-run.** Twenty-four raw files went into `data/raw/`, each
with a `.meta.txt` beside it recording the pull time and the exact request
(SPEC 2.3). The scripts are `scripts/session19_pull.py` and
`scripts/session19_checks.py`; the full real output is
`notes/session-19-check-output.txt`, and the pull log is
`notes/session-19-pull-output.txt`. Two consecutive runs of the checks script
produced identical output.

**Q29 fix applied from the start.** Session 17 raised Q29 because every
earlier airport's verify-on-contact sample sat inside its own sealed test
year (2025-08-01 to 2026-07-31) — not leakage into any model, but a habit
worth stopping. Every sample this session pulled sits in 2021 (the
archive-start probes, shared with every airport) or 2024 (comfortably inside
training, nowhere near the test year). Nothing here touches 2025-08-01
onward. This is the first airport to get the fix from the start, as Q29
itself suggested.

**F49. The station chosen — Dubbo (YSDU) over Canberra (YSCB) — and the
position it maps to.**

Both candidates come from IEM's own `AU__ASOS` network listing, pulled first
in the same run so the forecast requests could use real coordinates. Nothing
is typed in from memory or a map (D28's rule for the airport table).

```
IEM's entries, exactly as returned:
              sid    sname      elevation   tzname              archive_begin
YSCB          YSCB   Canberra   577.0 m     Australia/Sydney    1939-02-28
YSDU          YSDU   Dubbo      275.0 m     Australia/Sydney    1956-12-31
coordinates:  YSCB  lat -35.3088, lon 149.2003
              YSDU  lat -32.2167, lon 148.5747
attributes:   both  METAR_RESET_MINUTE = 0, HAS_PHOUR = 1
```

A short 7-day comparison sample (2024-06-01 to 2024-06-08, outside the test
year) was pulled for both before choosing:

```
        reports  present  missing  minute-past-hour
YSCB    163      163       0       :00 x160, :30 x2, :44 x1
YSDU    164      164       0       :00 x163, :30 x1
```

Both report hourly, on the hour, essentially complete over a week — either
would likely pass verification. **Dubbo was chosen on the "flat-ish, not
alpine" criterion the session prompt names.** Canberra sits at 577 m, in a
valley ringed by the Brindabella Range, with ski resorts under two hours away
— its climate carries a real elevation and mountain-proximity signature.
Dubbo sits at 275 m on the flat wheat-sheep plains of central-west New South
Wales, with no comparable terrain complication — the closer match to DSM's
294 m flat-continental profile (D32), which this airport is meant to be a
Southern Hemisphere counterpart to.

```
                latitude   longitude   elevation
EGLC            51.5053     0.0553         5 m
LFPG            49.0153     2.5344       109 m
DSM             41.534    -93.6531       294 m
YSDU           -32.2167   148.5747       275 m
YSDU is 16,683 km from EGLC, 16,637 km from LFPG, 14,504 km from DSM.
```

The forecast grid point Open-Meteo returned for YSDU:

```
requested        : lat -32.2167, lon 148.5747
grid point       : lat -32.274643, lon 148.59375, elevation 279.0 m
distance         : 6.69 km from the airport
height mismatch  : +4.0 m  (grid 279 m, station 275 m)
```

**This is the largest grid offset of the four airports** — 6.69 km against
1.76 km at DSM, 3.44 km at LFPG and 4.33 km at EGLC. Still only a few
kilometres, and the same kind of steady local offset the project exists to
learn (Q5, F17) — not a fault, but worth naming honestly rather than glossed
over, the way F31 named DSM's height mismatch.

**F50. The target hour checked, not assumed: local standard noon here really
is 02:00 UTC.**

D37 fixes the target at local standard noon and says that is 02:00 UTC. That
was checked against the timezone database, using the timezone name IEM's own
metadata gives (`Australia/Sydney`):

```
timezone from IEM metadata     : Australia/Sydney
mid-summer (daylight saving)   : 02:00 UTC = 13:00 AEDT (UTC+11)
mid-winter (standard time)     : 02:00 UTC = 12:00 AEST (UTC+10)
standard-time offset           : UTC+10
so local standard noon (12:00) = 02:00 UTC
D37 expects                    = 02:00 UTC
VERDICT                        : MATCHES
```

The standard offset was read from a July date (guaranteed standard time,
outside the October–April daylight-saving window), the same way F32 read
DSM's January date for the opposite hemisphere's winter. New South Wales
does observe daylight saving; D37 (and the session prompt) use the standard
offset regardless, per D27's convention.

**F51. The forecast archive starts here on exactly the same hour as at all
three other airports: 2021-03-24 00:00 UTC.**

```
probe 1, 2021-03-01..2021-03-07 : 168 rows, ALL 168 null
probe 2, 2021-03-18..2021-03-26 : 216 rows, 72 with a value, 144 null
                                  first non-null = 2021-03-24T00:00
                                  value range 13.0 to 24.9 degC

recent sample 2024-06-01..2024-06-21 : 504 rows, 504 with a value, 0 null
                                       value range 2.0 to 17.6 degC
                                       timezone in the response: GMT, utc_offset_seconds 0
```

This is the fourth location, on a fourth continent, to give the same answer
down to the hour — including the detail that the API answers HTTP 200 with
all-null values before its archive begins rather than returning an error
(F1, F20, F33). **The practical consequence: the D13 split dates carry over
here unchanged.** Training 2021-03-24 to 2025-07-31 and testing 2025-08-01 to
2026-07-31 are as available at this airport as at the other three. No date
needs moving.

**F52. `gfs_global` and `gfs_seamless` are IDENTICAL here, in both windows
tested — the Q30-adjacent check the session prompt asked for.**

F6 found the two strings identical at EGLC, reasoning that no CONUS-only NCEP
model (HRRR, NAM, NBM) could apply in Europe so nothing non-GFS was in the
seamless blend to prefer. F40 then found the two strings clearly **different**
at DSM — up to 12.3 degC apart on 259 of 264 recent hours — because Des
Moines sits inside CONUS, where those models can and do get blended in. That
made F6's reasoning location-specific rather than general, so it had to be
measured again here rather than assumed.

```
window 2021-03-24..2021-04-05 (early, inside training)   : 312 hours compared, 0 differ
window 2024-08-05..2024-08-15 (out-of-test-year, Q29 fix) : 264 hours compared, 0 differ
same grid point in every case : YES
```

**This airport sits outside CONUS (and outside the US entirely), so F6's
original reasoning applies again here — but for the right reason, checked
rather than assumed.** Every chunk pulled at this airport used `gfs_global`
regardless (D16), so nothing in the project depends on this result either
way; it is recorded because F40 is exactly the finding that says a
Europe-only argument does not travel automatically, and this confirms it does
travel to a second non-CONUS continent rather than being a fluke of Europe
specifically.

**F53. This station reports on the hour (`:00`), the same shape as LFPG — so
D14's pairing rule applies as written at the 02:00 UTC target, with an EXACT
match, no offset at all.**

```
recent sample 2024-06-01..2024-06-22 : 500 reports, minute-past-hour :00 x498, :30 x1, :59 x1
early  sample 2021-03-18..2021-04-01 : 333 reports, minute-past-hour :00 x333
```

IEM's own station metadata agrees: this station's `METAR_RESET_MINUTE`
attribute is `0` (F49), matching every reading in both samples five years
apart bar two isolated exceptions in the recent sample (one report 30 minutes
off the hour, which D14 correctly drops; one report 1 minute off, which D14
keeps) — the same kind of rare off-hour reporting CDG shows (F18), not a
pattern.

**What D14 keeps at the 02:00 UTC target hour, observation side only:**

```
recent sample 2024-06-01..2024-06-22  21 calendar days, 21 kept, 0 dropped
early  sample 2021-03-18..2021-04-01  14 calendar days, 14 kept, 0 dropped
pairing offset on every kept day      : 0 minutes, min and max alike
```

**Every single day is kept in both samples, with a perfect 0-minute offset
throughout.** DSM was the only airport so far to lose no target-hour day at
all in its own verify-on-contact sample (F34); this airport matches that,
and does it with an exact on-the-hour match rather than DSM's 6-minute
offset. On this evidence D14 needs no adapting here — if anything this is
the easiest pairing case of the four.

**Gap counts, nothing filled (SPEC 2.2).**

```
recent sample : 504 hours expected, 498 covered, 6 missing
                (a 5-hour outage 2024-06-07 03:00-07:00 UTC, and one isolated
                hour 2024-06-17 15:00 UTC — neither touches 02:00 UTC)
early  sample : 336 hours expected, 333 covered, 3 missing
                (2021-03-20 07:00, 2021-03-30 05:00 and 06:00 UTC)
reports with no temperature : 0 in both samples
```

**F54. Both non-European-airport risks — whether "tmpc" needs new units
handling, and whether the "tz=UTC" request really is UTC — were measured
here too, and both need no new handling, more cleanly than at DSM.**

**Units.** Australian METARs are written in whole-degree Celsius natively
(unlike US METARs, written in whole-degree Fahrenheit, which is why DSM's
F35 found a small ~0.004 degC rounding gap against the Fahrenheit field).
Here the Celsius field and the Fahrenheit-converted field agree to the
limits of floating-point:

```
file : iem_asos_YSDU_2024-06-01_2024-06-04_routine-tmpc-tmpf.csv   72 rows

valid (UTC)        tmpc     tmpf   (tmpf-32)*5/9   difference
2024-06-01 00:00   13.00    55.40          13.00       +0.000
2024-06-01 01:00   14.00    57.20          14.00       -0.000
2024-06-01 02:00   15.00    59.00          15.00       +0.000

largest disagreement across all 72 rows : 0.000000 degC
tmpc range in this sample               : 1.0 to 17.0 degC
```

**Timezone.** Every IEM request in this project sends `tz=UTC`. The same
window was pulled a second time with `tz=Australia/Sydney`; June is
southern-hemisphere winter, so that timezone is on **standard** time (AEST,
UTC+10) throughout, unlike DSM's July check which landed inside daylight
saving. Because the two requests use the same date strings under different
timezones, they cover different physical hours at their edges, so the two
series were matched by shifting timestamps and comparing values at matching
physical instants directly, rather than by row position:

```
shift            matching hours   values equal
local -9h              63              18  (28.6%)
local -10h              62              62  (100.0%)
local -11h              61              18  (29.5%)
```

A single clean 100% match at local time minus 10 hours, exactly the AEST
standard offset. So the `tz=UTC` request really is UTC here too. Open-Meteo
labels its own side of the join `timezone=GMT`, `utc_offset_seconds=0`, so
both series are stamped in UTC and neither needs shifting.

**F55. The "special" (SPECI) report stream is a second SCHEDULED
half-hourly report here — like EGLC and LFPG, unlike DSM.**

```
recent window 2024-06-01..2024-06-22, 21 days (504 hours)
  routine rows           : 500  (essentially all at :00)
  routine + special rows : 1,238
  special-only rows      : 738
  of which at :30        : 496  (67.2% of all special-only rows)
  distinct minutes used  : 58
```

At EGLC the "special" stream turned out to be a second scheduled report at
`:20` (F3); at LFPG, at `:30` (F19); at DSM it turned out to be genuinely
unscheduled, spread across 38 minutes with none used more than four times in
three weeks (F36). Here, two-thirds of every special-only report lands at
`:30` — almost one for nearly every hour in the window — which is the shape
of a second scheduled report, not weather-driven noise. **Recorded, not
acted on.** This airport reuses the routine report as the truth observation,
exactly as D30 already settled for the other three; there is no fallback
stream to consider using instead.

**F56. Plain first read — yes, this airport is usable for the recipe the
same way EGLC, CDG and DSM were.** Every verify-on-contact check passed:

- the Previous Runs API carries the location, with a grid point 6.69 km away
  and a 4 m height difference — the largest offset of the four, still small
  (F49);
- the archive reaches back to the same 2021-03-24 00:00 UTC start hour, so
  the fixed D13 split dates need no change (F51);
- `gfs_global` and `gfs_seamless` are identical here, confirming F6's
  original non-CONUS reasoning travels to a second continent (F52);
- IEM carries the station in `AU__ASOS` with a largely complete observation
  record, and the position used is IEM's own (F49);
- the pairing rule needs no adapting: this station reports on the hour, an
  exact match at the target hour, on every report bar two isolated
  exceptions in three weeks (F53);
- the units and the timezone need no new handling, and both are measured
  more cleanly than at DSM because Australian METARs are already whole-degree
  Celsius (F54);
- and the one genuinely airport-specific choice, the target hour, was made
  on principle before any data was seen (D37) and then confirmed against the
  timezone database (F50).

**Nothing found here justifies changing any earlier decision at EGLC, CDG or
DSM.** The one thing that is not reused — the target hour — was decided in
advance and its cost to D26's "only the location changed" claim is written
into D37 rather than glossed over, exactly as D33 did for DSM.

**No new open question is raised this session.** Unlike session 14 (which
left Q25–Q27 open because SPEC still conflicted with DSM's target hour, the
gap-map chunk-boundary effect was untested, and the `gfs_seamless` comparison
had not yet been run), this session's own prompt already built in the fixes
those questions asked for: SPEC's per-airport wording (D34) means no SPEC
conflict is opened by D37 the way D33's was; this station reports on the
hour, so there is no DSM-style chunk-boundary artifact to name; and the
`gfs_seamless` comparison (F52) was run in this same session rather than
deferred to the next one.

---

## 2026-08-19 — Session 20 decision (SPEC housekeeping: DSM's pass recorded,
Dubbo added to SPEC, Q28 and Q29 resolved)

**D38. SPEC is brought up to date with two facts that were already true and
had not yet been written down, plus one new airport row.** Nothing measured
here changes; this entry documents six authorised edits (A-1 to A-6, the
session 20 prompt) and no others, made *before* this session's own pull ran,
exactly as the prompt required ("the SPEC edits are the careful part and come
first, so the pull runs against an agreed spec").

- **A-1 (§5.0 results table).** DSM's row changed from "pending — not yet run"
  to **PASSED (stage 2, 365 test days)**, with its session 18 figures
  (corrected 1.700 vs raw GFS 1.815 vs persistence 4.003, DECISIONS F47). The
  paragraph beneath now says all three airports' single authorised looks are
  spent and fell on the same twelve months, and names the extra caveat that
  applies to DSM alone: it changed both the location and the target hour
  against the European pair, so it is not the same controlled comparison EGLC
  and LFPG make between them.
- **A-2 (§6 build order).** The DSM bullet changed from "IN PROGRESS" to
  **PASSED**, citing its full chain of findings (F31–F37, F38–F41, F42–F46,
  D35, F47), mirroring how the CDG bullet already reads. A new Dubbo bullet was
  added, "IN PROGRESS", citing its verify-on-contact findings (F49–F56).
- **A-3 (§3.4 airport table, both sub-tables).** A YSDU row was added to each
  table, using session 19's own recorded figures (F49, F50, F53) rather than
  the session prompt's summary of them, exactly as the prompt required.
  DSM's stage cell changed from "2 — in progress" to "2 — passed".
- **A-4 (§3.4 notes and §3.1 — closes Q28).** The first column heading in both
  sub-tables changed from **"ICAO"** to **"station code"**, and §3.1's
  wording changed from "requested by its ICAO code" to "requested by its
  station code (the first column of the table)". The note beneath the table
  now explains why the old heading could not survive a fourth airport: YSDU's
  code *is* an ICAO code, unlike DSM's, so the set is genuinely mixed (two
  ICAO codes, one non-ICAO station id, and a third ICAO code) and no single
  word describes every entry. **This closes Q28.**
- **A-5 (§1 airport list).** DSM's bullet now reads "passed" instead of "in
  progress"; a new Dubbo bullet was added, "stage 2, in progress".
- **A-6 (§3.3 verify-on-contact — closes Q29).** A new paragraph states the
  accurate claim plainly: verify-on-contact samples at EGLC, CDG and DSM fell
  inside the sealed test year, which was never leakage (nothing was fitted on
  those values, no method choice came from them), and the accurate claim has
  always been **"no test-year data influenced any model, feature, or
  choice"** — not that no test-year value was ever seen. From Dubbo onward,
  verification samples are drawn from outside the test year on purpose. **This
  closes Q29** as the honest-wording item it always was, not a leakage one.

**What did not change.** Sections 5.1 (the metric), 5.2 (which references
decide the bar) and 5.3 (the qualitative bar itself, D22) are untouched. No
edit here adds anything a result must clear or removes anything it already
had to. The frozen bar's *meaning* is exactly what it was before this session.

**Why this is a decision entry and not just a finding.** Sessions 09 (D28) and
15 (D34) established the pattern: bringing SPEC into line with facts already
established elsewhere in the log is itself the kind of change this project
tracks as a decision, because it is edited under authorisation rather than
discovered by measurement. D38 is that same kind of entry for session 20.

---

## 2026-08-19 — Session 20 findings (the full Dubbo pull and gap map)

This session pulled Dubbo's full history for both sources, 2021-03-24 to
2026-07-31, mirroring session 03b (EGLC), session 10 (LFPG) and session 15
(DSM) file for file. **No data was joined, built, trained or evaluated, and
Dubbo's test year was touched only structurally** — row presence, gap
positions, report timing — never a temperature value. The scripts are
`scripts/session20_pull.py` and `scripts/session20_checks.py`; the full real
output is `notes/session-20-check-output.txt`, and the pull log is
`notes/session-20-pull-output.txt`. Two consecutive runs of the checks script
produced byte-identical output. No retry fired on the pull and no rate limit
was hit; every chunk was written on the first attempt.

**F57. The full pull totals, and the 492-hour gap answer: SAME WINDOW — a
fourth airport on a fourth continent shares it.**

```
Forecast (Open-Meteo Previous Runs, gfs_global, YSDU):
  46,944 hourly rows expected, 46,452 with a usable value, 492 missing (all
  null, 0 "no row at all"). Grid point: lat -32.274643, lon 148.59375,
  elevation 279.0 m — matches session 19's F49 exactly.

Truth (IEM ASOS routine METARs, YSDU):
  46,734 reports across the six chunks. Station position in the files:
  lat -32.2167, lon 148.5747, elevation 275.0 m — matches SPEC 3.4 (F49)
  exactly.
```

The forecast series' single gap is **2023-12-30 00:00 to 2024-01-19 11:00
UTC, 492 hours** — the same start, same end, same length as EGLC (F8), LFPG
(F22) and DSM (F38). Every one of the six headline totals matches. It falls
entirely inside the training window; **the test window has no forecast gap at
all**. Four airports on four continents now share it hour for hour, which is
as close to proof as this project can get that the gap belongs to the
Open-Meteo archive itself, not to any place.

**Training-window value ranges checked and sane, both in Celsius.** Forecast
0.5 to 40.9 degC (mean 17.03); observed -5.0 to 41.0 degC (mean 16.66).
**Dubbo has by far the narrowest cold end of the four airports** — its
forecast series never drops below 0.5 degC across the whole training window,
against EGLC's -1.7 (F10), LFPG's -8.5 (F26) and DSM's -30.0 (F38). Inland
New South Wales plains sit at latitude -32, a good deal closer to the equator
than any of the other three airports are to it, and the training window's
worth of hours reflects that plainly. Nothing here is out of range for the
location; recorded, not acted on.

**F58. The observation record is real, complete enough, and its off-hour
report rate is the highest of the four airports — a correction to F53's
early optimism, not a contradiction of it.**

```
                              reports   no temp   off-hour (>15 min)   rate
EGLC (F9, whole period)       46,919         -              8         0.017%
LFPG (F23, whole period)      46,903         -             97         0.207%
DSM  (F39, whole period)      46,938         1              3         0.006%
YSDU (this session)           46,734         2            235         0.503%
```

**Two reports in five years carry no temperature** (2022-12-12 01:02 UTC,
2025-07-23 17:00 UTC) — dropped and counted, never filled (SPEC 2.2). The
**235 off-hour reports (0.503%)** are the highest rate of any airport so far,
about 2.4 times LFPG's and roughly 80 times DSM's — all 235 are still
`report_type=3` (routine) rows, since that is the only type this pull
requested. Most (177 of 235, 75%) sit at exactly `:30`, on 178 distinct days
in total across all 235; whether a given `:30` row sits alongside a normal
`:00` report that same hour or in its place was not examined this session
(observation-side counting only asks whether *a* report exists near the
target hour, which is unaffected either way). The rest are single scattered
minutes across 121 further episodes, the largest being the 38 reports over the
same 2022-07-23/25 episode session 10 found in LFPG's own record (a genuine
short outage at the station, not something specific to Dubbo's equipment).
**Session 19's F53
sample (500 reports over three weeks, D14 dropping none) undersold this: a
three-week sample is 3.5% of a five-year record, and this is the second time
a short sample has read more cleanly than the full one turned out to be**
(F18 made the same kind of extrapolation error for LFPG, corrected by F25).
Nothing about the pairing rule changes: D14's tolerance and D30's "take the
drops, do not adapt the rule for one airport" both apply exactly as written,
and the pull session's job — as it was for every earlier airport — is to
count the real cost, not to change the rule.

**Real observation gaps: 287 runs, 477 missing hours (1.02% of the whole
period), the largest being 42, 37 and 29 hours (October 2022 and July 2022) —
genuine outages where nothing was filed at all, not an off-hour shift.** This is
higher than DSM's 11 hours (0.02%, the cleanest of the airports so far) and
higher than EGLC's 44 (0.09%), but still comparable to LFPG's 140 (0.30%) in
shape if not in size. There is no request-boundary artefact of the kind DSM's
`:54` reporting created (Q26): Dubbo reports on the hour, so the report
serving hour H is stamped H:00 and always sits inside the chunk that covers
hour H — checked chunk by chunk in this session's script rather than assumed,
and confirmed clean at every one of the five internal chunk boundaries.

**F59. Days lost at the 02:00 UTC target, both sides, written down before any
join — the numbers the next session's join must reconcile against.**

```
                                       days    expected rows   dropped (fc / obs)
inner-training 2021-03-24..2024-07-31  1,226           1,193        21 / 12
validation      2024-08-01..2025-07-31   365             360         0 / 5
test            2025-08-01..2026-07-31   365             356         0 / 9
whole period                           1,956           1,909        21 / 26 (0 overlap)
```

**Observation side: 26 days lost of 1,956 (1.33%)** — 5 to an off-hour-only
report near 02:00 (2022-07-23, 2022-07-25, 2022-10-21, 2025-03-08, 2025-08-30,
all at `:30` or `:31`) and 21 to no report at all near the hour (mostly single
scattered days, with 2022-10-22/23/24 sitting inside the 42+37+19-hour outage
F58 found). **This is the most any airport has lost at its own target hour on
the observation side** — DSM lost 0 (F41), EGLC and LFPG a handful each. **Of
the test window's 9 observation-side losses, 8 are "no report near the hour"
and 1 is the off-hour report on 2025-08-30** — so the test year is not spared
either cause, only spared the bulk of it: 4 of the 5 off-hour losses and 13 of
the 21 "no report" losses fall in training instead. Nothing about this changes
the pairing rule's behaviour; it is a fact about which weeks the outages fell
in.

**Forecast side: 21 days lost, all inside the shared 492-hour gap, all
consecutive, all in inner-training** — 2023-12-30 through 2024-01-19. This is
one more day than EGLC (20, F12), LFPG (20, F22) and DSM (20, F41) lost from
the identical gap. The gap's last missing hour is 2024-01-19 11:00 UTC, so
whether that date's target hour is lost depends only on whether the target
hour falls before or after 11:00: EGLC (12:00), LFPG (12:00) and DSM (18:00)
all fall after it, so 2024-01-19 already has data at their targets and only
2023-12-30 through 2024-01-18 (20 days) is lost. Dubbo's 02:00 target falls
*before* 11:00, so 2024-01-19 is still inside the gap at 02:00 and is lost
too, giving 21 days (2023-12-30 through 2024-01-19) — arithmetic that follows
from the target hour, not a new fact about the gap itself.

**Expected paired rows for the eventual join: 1,909 of 1,956 calendar days
(97.6%).** That is the lowest keep-rate of the four airports — EGLC and LFPG
each kept about 1,933 of 1,956 (98.8%, F12, F27/D31.7) and DSM kept 1,936
(99.0%, F42) — all four losing essentially the same ~20-day shared forecast
gap, with the gap between them coming entirely from F58's higher off-hour and
real-gap rate on the observation side, not from anything on the forecast side.
**Nothing was filled and nothing was joined this session (SPEC 2.2); these
counts are what the next session's join must reconcile against**, the way
session 11 reconciled CDG's join against session 10's gap map and session 16
reconciled DSM's against session 15's.

**Plain first read — yes, this airport is usable for the recipe the same way
the other three were**, but its full record is a genuine step down in
cleanliness from what the small verify-on-contact sample suggested, and that
correction is recorded here rather than smoothed over. Nothing found here
justifies changing any earlier decision at EGLC, CDG or DSM, and nothing found
here changes D14, D30, or how the pairing rule is applied — the same rule is
used at every airport, including where, as at CDG and now more so at Dubbo, it
costs real days (SPEC 4.5, D30).

---

## 2026-08-19 — Session 21: ONE-TIME HOUSEKEEPING RESTRUCTURE (documentation
only, nothing deleted)

This session touched no data, no model and no pull. Its job was to cut the
per-session token cost of the three living documents by relocating settled
weight and trimming duplication — never by deleting anything. Two safety
nets hold everything: **git history** (every prior version of every file)
and the new **DECISIONS-archive.md** (the moved content, verbatim). This
entry is the record the session's own end-of-session steps require.

**What moved, and what stayed — the full account.**

Moved verbatim to `DECISIONS-archive.md`, with a one-line pointer left in
place of each:
- **D1–D12** (the founding planning decisions: project scope, EGLC as
  location, IEM over Weather Underground, the Previous-Runs-not-Historical
  choice, the March 2021 floor, reanalysis excluded, the D13-style split
  idea, 24-hour lead, the single-fixed-hour target, the frozen bar's shape,
  drop-not-fill, gradient-boosted trees). Moved because their conclusions
  are now codified as active SPEC rules — the operative rule lives in SPEC,
  the DECISIONS entry was only ever the settled "why" behind it.
- **F1–F4**, session 01's EGLC-only verify-on-contact findings (the
  archive's apparent start date; EGLC's observation record; EGLC's
  twice-hourly reporting; the forecast variable pulled). Moved because they
  are settled, EGLC-only, and superseded as ongoing precedent by the
  project-wide findings that followed (F8, F9, D14).
- **F6**, the EGLC-only `gfs_seamless`-versus-`gfs_global` equivalence
  check. Moved because it is settled and EGLC-only; D16 (kept live) is the
  active rule it supports, and the same comparison was later repeated,
  per airport, at DSM (F40) and Dubbo (F52) — both kept live, since those
  are where the current, airport-specific picture actually lives.
- **F11**, the correction to F1's superseded continuity claim. Moved to sit
  beside F1 in the archive, per the session prompt's explicit instruction.
  F8 (kept live) is the finding that actually maps EGLC's forecast gap;
  F11 only records that F1's earlier claim about it was wrong.

**Kept live in DECISIONS.md, deliberately, and checked against the session
prompt's Task 3c list:** every still-active precedent (D13, D14, D16, D17,
D18, D19, the three locks D21/D31/D35, D22, and the airport-opening/
convention decisions D26, D27, D30, D32, D33, D36, D37); the results of
record F16, F30, F47 and F48's honest reading across them; every
project-wide finding still in play, including the 492-hour gap findings
(F8, F22, F38, F57 — now cited together in SPEC 3.2, see below) and the
`gfs_seamless`-differs finding (F40, F52); all Dubbo (in-progress) material
in full (D36, D37, F49–F59); and every open question, live or closed —
**Q30 is the only one still open**, and it was left exactly as written.
Everything not explicitly named for moving was left live, per the prompt's
"when in doubt, keep it live" instruction (3e) — including D15, P1–P3, and
every closed Q1–Q29, none of which the prompt asked to move.

**Confirmation each moved block is byte-for-byte identical.** Before
writing `DECISIONS.md`'s replacement pointers, each of the four blocks
above was extracted by exact line range from the original file, written
into the archive, and then checked back against the original text
programmatically — all four matched byte-for-byte. `git diff` against the
prior committed version of `DECISIONS.md` will show only those four
regions removed (replaced by one pointer line each) and this new entry
appended; nothing else in the file's 5,000-plus other lines was touched.

**SPEC 3.2's three near-identical gap paragraphs are now one general
statement — and one factual correction was made along the way.** The
session prompt described the collapse as "shared hour-for-hour by EGLC, CDG
and DSM (F8, F22, F38) but **not** by Dubbo, which has its own scattered
gaps instead." That is not what session 20 actually found. **F57 (session
20) shows Dubbo's forecast series has the exact same 492-hour gap, same
start hour, same end hour, same length, as the other three** — "four
airports on four continents now share it hour for hour." What *is*
Dubbo-specific is a different thing entirely: F58's finding that Dubbo's
**observation** record (not the forecast archive) carries the highest
off-hour report rate and real gap count of the four airports. Writing the
collapsed SPEC 3.2 paragraph the way the prompt suggested would have put a
false claim into SPEC, so it was not followed literally. SPEC 3.2 now
states the true, verified fact — the gap is shared hour-for-hour by all
four airports pulled so far (F8, F11, F22, F38, F57) — and points to each
airport's own DECISIONS finding for the specifics. This is flagged here,
in STATUS's consistency check, and in the session's own report to the
owner, rather than silently corrected. **Nothing about the frozen bar or
any active rule changed as a result** — this is a wording accuracy fix to
a factual background paragraph, not a methodological change.

**STATUS.md is now a pure snapshot**, per the session prompt's Task 1. The
accumulated 20-session narrative (previously 1,663 lines) is unchanged in
git history; the new file (about 65 lines) holds only the current stage, a
compact per-airport status table pointing at SPEC 3.4/5.0, a high-level
"done" list pointing at DECISIONS rather than restating it, the single next
session, and the one live open question (Q30, partial).

**CLAUDE.md now names DECISIONS-archive.md** as a fourth document, read
only when a session needs deep history from a passed stage or airport, not
routinely — and states plainly that STATUS.md is a snapshot whose own
history lives in git. The "read the three live files in full every
session" rule is otherwise unchanged.

**What did not happen.** No data was pulled, joined, built, trained or
evaluated. Dubbo's join and validation rehearsal — the actual next
modelling session — was not started. No content of any moved decision or
finding was edited, only relocated. No active rule, no split date, no
locked setting, and no frozen-bar wording changed in meaning anywhere.

**Append-only resumes, in both files, starting now.** This restructure was
authorised as a one-time exception to the append-only rule (CLAUDE.md,
DECISIONS.md's own header). It is not a precedent for rewriting the log
again; new material goes to the bottom of `DECISIONS.md`, never into
`DECISIONS-archive.md`, from this point on.

---

## 2026-08-19 — Session 22 findings (the Dubbo join, bias look and
validation rehearsal)

The first modelling session for the fourth airport, Dubbo. It mirrors
session 16 at DSM, which mirrored session 11 at CDG and sessions 04/05 at
EGLC. **Dubbo's test year was not touched**: the two 2026 YSDU raw chunk
files were never opened, the 2025 chunk was cut off at 2025-07-31 on load,
and the script asserts that no date on or after 2025-08-01 reached any
table. Nothing was tuned, varied or chosen again — the locked recipe (D21,
restated per airport as D31/D35) was applied at the fourth location and
nothing else. The script is `scripts/session22_model.py` and the full real
output is `notes/session-22-check-output.txt`. Two consecutive runs
produced identical output apart from the clock time in the header line;
PART 0 proves against `scripts/session05_model.py` that 0 model settings
differ and exactly 1 constant differs (TARGET_HOUR, 12 to 2), which is
D37 and nothing else.

**F60. The join at 02:00 UTC at Dubbo, and every drop reconciled exactly
against session 20's gap map (F59) — including the one respect in which
Dubbo's expected drops differ in kind from every earlier airport's.**

One row per day: date, forecast temperature, observed temperature, and the
residual the model learns.

```
                                         days   kept   drop  no fc  null fc  no obs
inner-training 2021-03-24..2024-07-31   1,226  1,193     33      0       21      12
validation     2024-08-01..2025-07-31     365    360      5      0        0       5
```

```
cause                                             expected   actual  verdict
the 492-hour forecast gap (F57, F59)                    21       21  MATCHES
observation-side losses, inner-training (F59)           12       12  MATCHES
observation-side losses, validation (F59)                5        5  MATCHES
TOTAL days dropped                                      38       38  MATCHES

inner-training paired rows (F59)                      1,193    1,193  MATCHES
validation paired rows (F59)                            360      360  MATCHES
```

**The forecast-gap loss is 21 days here, not the 20 every earlier airport
lost from the identical gap.** EGLC (12:00), LFPG (12:00) and DSM (18:00)
all target an hour *after* the gap's last missing hour, 2024-01-19 11:00
UTC, so 2024-01-19 already carries a value at their targets and survives.
Dubbo's 02:00 UTC target falls *before* 11:00, so 2024-01-19 is still
inside the gap at 02:00 and is lost too — 2023-12-30 through 2024-01-19,
21 consecutive days. This was predicted by F59 from the target hour alone,
before anything was joined, and the join found exactly 21.

**The observation side is not clean here, unlike DSM's.** DSM lost zero
days on the observation side in five years (F41, F42). Dubbo loses 17 —
12 in inner-training, 5 in validation — split between two causes, both
predicted in advance by F59 and both confirmed exactly:
- **4 days lost to an off-hour-only report** (all inside the loaded
  window; the fifth of F59's five whole-period off-hour days,
  2025-08-30, sits in the test year and does not appear here):
  2022-07-23, 2022-07-25 and 2022-10-21 (all `:30`, 30 minutes out,
  dropped by D14) and 2025-03-08 (`:31`, 29 minutes out, dropped by D14).
- **13 days lost to no routine report anywhere near the hour at all**:
  2022-10-22/23/24 (inside the 42+37+19-hour outage F58 found),
  2022-12-12, 2023-03-23, 2023-05-10, 2024-02-04, 2024-05-14, 2024-07-20
  (inner-training), and 2024-09-18, 2024-11-17, 2024-11-27, 2025-07-22
  (validation).

**The pairing itself needed no adapting and worked exactly as F53
predicted.** Every one of the 1,574 kept days paired at a 0-minute offset
— Dubbo reports on the hour, so the target-hour report is itself the
observation, the same shape as LFPG. Exactly one day in the whole period
had more than one report inside the 15-minute window (not itself a
problem; D14 already handles it by taking the nearest).

Row counts beside the three prior airports: inner-training 1,205 (EGLC),
1,204 (CDG), 1,206 (DSM), 1,193 (Dubbo); validation 364, 365, 365, 360.
**Dubbo keeps the fewest rows of the four airports in both periods** —
consistent with F58's finding that Dubbo's full observation record is a
genuine step down in cleanliness from what its three-week verify-on-contact
sample suggested. Nothing was filled (SPEC 2.2), and every count above
matched what F59 predicted before the join ran — no surprise, no stop.

**F61. Dubbo's bias at 02:00 UTC is a fourth distinct shape: the
calendar/season structure CDG showed, but concentrated into ONE local
season rather than spread across the year — and it is phase-shifted into
Dubbo's own summer, exactly as the flipped-hemisphere check asked whether
it would be.** Inner-training only; the validation year's values were not
explored and the test year not touched.

Overall, beside EGLC (F13), CDG (F28) and DSM (F43):

```
                            EGLC       CDG       DSM      YSDU
days                       1,205     1,204     1,206     1,193
mean bias degC            -0.108    +0.050    -0.231    -0.136
median degC               +0.000    +0.100    -0.200    -0.100
st dev degC                1.551     1.654     2.550     1.740
mean |bias| degC           1.172     1.248     1.973     1.260
station warmer, %           48.7      51.7      45.5      45.3
min / max degC        -7.0/+5.6 -7.7/+5.8 -10.4/+9.2 -12.8/+8.0
```

EGLC and CDG are measured at 12:00 UTC, DSM at 18:00 UTC and Dubbo at 02:00
UTC (D33, D37) — all four are their own airport's local midday, which is
what is held constant, not the UTC hour (SPEC 4.1). **GFS is harder to
beat at Dubbo than at either European airport but easier than at DSM** —
mean |bias| 1.260 sits between CDG's 1.248 and DSM's 1.973, close to CDG's.
The mean bias is small (-0.136), so as at the other three airports most of
the error is structure and day-to-day noise, not a constant offset.

Against forecast temperature, Dubbo's coldest days behave differently from
every airport so far:

```
forecast band (degC)     days  mean bias   st dev  mean |bias|     EGLC      CDG      DSM
0 to 5                      1     +0.300      nan        0.300   -0.049   -0.687   -0.781
5 to 10                    13     +1.046    1.384        1.231   +0.361   +0.223   -0.337
10 to 15                  248     +0.252    1.719        1.268   +0.387   +0.339   +0.465
15 to 20                  295     +0.456    1.625        1.243   -0.287   +0.320   +1.098
20 to 25                  242     +0.026    1.594        1.144   -0.746   -0.142   +0.953
25 to 30                  198     -0.630    1.442        1.188        -        -   -0.147
30 to 45                  196     -1.301    1.723        1.497        -        -   -3.089

coldest 10%  n=119  forecast  +4.7 to +13.0 degC  mean bias +0.499 (EGLC +0.097, CDG -0.351, DSM -1.066)
warmest 10%  n=119  forecast +31.6 to +39.4 degC  mean bias -1.418 (EGLC -1.155, CDG -0.784, DSM -2.993)
```

**Dubbo has by far the narrowest cold end of the four airports (F57), and
on the coldest tenth of its own forecasts GFS actually runs slightly too
COLD (+0.499)** — the only one of the four airports where the coldest-tail
bias is positive. CDG and DSM both ran too warm at their own cold ends;
EGLC's was flat. **The warm end overshoots as at every airport** — -1.301
in the hottest band, -1.418 across the warmest tenth, between EGLC's
-1.155 and DSM's -2.993 and larger than CDG's -0.784.

By season (Northern-calendar label, for column alignment with the three
prior airports' published tables):

```
season (Northern label)    days  YSDU bias   st dev  YSDU |bias|     EGLC      CDG      DSM
winter DJF                  248     -0.973    1.638        1.408   +0.356   -0.092   -0.805
spring MAM                  342     +0.073    1.635        1.135   -0.061   +0.614   +0.923
summer JJA                  334     +0.140    1.614        1.176   -0.549   -0.056   -0.208
autumn SON                  269     +0.027    1.881        1.387   -0.052   -0.401   -1.187
```

**One season carries almost the entire calendar signal.** Northern-labelled
"winter DJF" is -0.973 degC; the other three seasons sit between +0.027 and
+0.140, essentially flat by comparison. This is CDG's kind of bias (F28
found CDG's structure lived mainly in the calendar, spread more evenly
across seasons) sharpened into a single strong season rather than spread
across the year, and it is larger in that one season than any single
seasonal figure CDG produced.

**The flipped-season check, examined explicitly as the session prompt
asked.** "Winter DJF" is a Northern-calendar label; December, January and
February are Dubbo's own SUMMER (D37, and F61's bias-by-month table in the
notes file: Dec -1.054, Jan -1.158, Feb -0.723 — the three most negative
months of the year). The `season_sin`/`season_cos` features (D19) encode
only calendar position, with no hemisphere information built in, so a
model that had somehow learned "Northern-hemisphere summer (Jun-Aug) is
warm" and applied it blindly would put its largest correction near
June-August. Instead **the largest-magnitude seasonal bias sits in
December-February — Dubbo's own actual summer** — which is exactly the
Southern-summer-in-Dec-Feb signal the session prompt asked to check for.
This is evidence the underlying physical bias is genuinely phase-shifted
at Dubbo, not a copy of any Northern airport's calendar shape, and that
the day-of-year encoding is free to fit whatever local structure is
actually there rather than being tied to a hemisphere.

**F62. The rehearsal: at Dubbo the correction beats all four references,
by a margin between CDG's and DSM's — the first result on the region and
hemisphere axis F46/F48/D36 named as untested.**

Model: the locked D21/D31/D35 recipe, fitted on Dubbo's 1,193
inner-training rows only. PART 0 of the output proves the method was
reused rather than re-chosen: 0 model settings differ from session 05's,
and of the shared constants exactly one differs, TARGET_HOUR (12 to 2),
which is D37 and nothing else. Two consecutive runs produced identical
output apart from the header's clock time.

All five methods scored on the same 355 common validation days (5 of
Dubbo's 360 paired validation rows drop out because persistence needs the
previous day's observation and it is one of F61's missing-observation
days):

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.397     -0.392      2.027       10.90
Persistence                2.577     +0.020      3.451       16.00
Climatology                2.888     +1.319      3.578       11.64
Mean-bias reference        1.368     -0.256      2.005       10.76
ML-corrected               1.283     -0.062      1.890       10.31
```

Verdicts:

```
vs Raw GFS              YES   1.283 against 1.397  ->  0.115 degC better (8.2%)
vs Persistence          YES   1.283 against 2.577  ->  1.295 degC better (50.2%)
vs Mean-bias reference  YES   1.283 against 1.368  ->  0.086 degC better (6.3%)
vs Climatology          YES   1.283 against 2.888  ->  1.606 degC better (55.6%)
```

**This is a validation rehearsal, not the frozen bar (SPEC 5.3, 5.0). A
good number here does not mean Dubbo has passed.**

Four things the numbers say, read honestly:

1. **The recipe travels to a fourth continent, a flipped hemisphere and a
   flipped season cycle.** Applied unchanged 14,504–16,683 km from the
   three existing airports (F49), at a third distinct target hour, on a
   bias shaped like nothing seen before (F61), it beats every reference.
2. **The margin sits between CDG's and DSM's, closer to CDG's**: 8.2%
   against EGLC's 6.0%, CDG's 3.4%, DSM's 16.1%. Raw GFS at Dubbo (1.397)
   is harder to beat than at either European airport but easier than at
   DSM (1.748), which lines up with F61's bias-magnitude ordering.
3. **The mean-bias reference beats raw GFS at Dubbo (1.368 against
   1.397)**, as it did at EGLC and DSM and did not at CDG — there is a
   small constant worth taking (-0.136 degC on inner-training). The model
   beats that reference by 6.3%, so the win is still mostly structure.
4. **The seasonal pattern helps in only 2 of 4 Northern-labelled seasons —
   the fewest of any airport so far — and one season carries almost the
   whole result:**

```
season         days   raw GFS   ML-corr   YSDU chg   EGLC chg   CDG chg   DSM chg
winter DJF       90     1.344     1.290    -0.055     +0.087     +0.025    -0.414
spring MAM       90     1.219     1.241    +0.022     -0.015     -0.057    -0.184
summer JJA       90     1.170     1.236    +0.066     -0.321     -0.122    +0.061
autumn SON       85     1.884     1.368    -0.516     -0.049     -0.044    -0.598
```

   Northern-labelled autumn (SON, Dubbo's own local spring) carries almost
   the entire win (-0.516 of the average improvement); spring and summer
   (Dubbo's own autumn and winter) both got very slightly worse. EGLC,
   CDG and DSM each helped in 3 of 4 seasons; Dubbo helps in only 2.
   Day-by-day, the correction was closer to the truth than raw GFS on
   **190 of 355 days (53.5%)** — the lowest win rate of the four airports
   (CDG 55.3%, DSM 55.6%), consistent with the result leaning more heavily
   on one strong season than the other three airports' rehearsals did.

Feature importances — forecast temperature carries the largest share of
any airport yet:

```
feature             EGLC gain %  CDG gain %  DSM gain %  YSDU gain %  YSDU splits
forecast_temp_c           44.3%       35.9%       45.0%       47.8%        1,633
season_sin                26.7%       39.9%       37.3%       30.2%        1,555
season_cos                29.0%       24.2%       17.7%       22.0%        1,012
```

In-sample MAE on Dubbo inner-training was 0.961 degC against raw GFS's
1.260 (EGLC 0.879, CDG 0.945, DSM 1.221) — shown only to confirm the fit
did something; it proves nothing about performance on unseen data.

How each reference was built, identical in method to the three prior
airports, fitted on Dubbo inner-training only:
- **Raw GFS** — the forecast value itself, uncorrected.
- **Persistence** — the previous calendar day's 02:00 UTC observation.
  Past values only (SPEC 2.1d). The first scored validation day takes its
  persistence value from inner-training, legal per D21.8/D31.8/D35.8's
  note, unchanged here.
- **Climatology** — the seasonal average of the *observed* temperature at
  Dubbo within 7.5 days of that position in the year, training-window
  only (SPEC 2.1c).
- **Mean-bias reference** — the forecast plus -0.1360 degC, the mean
  Dubbo inner-training bias and nothing else.
- **ML-corrected** — the forecast plus the model's predicted residual.

Nothing was fitted on the validation year: not the model, not the
climatology, not the mean bias, not any encoding. **No SPEC edit was made
and none was authorised.**

**F63. What a Dubbo rehearsal win does and does not answer — the same
honest accounting F46 gave DSM.**

F46 named two axes stage 2's first pair (EGLC, CDG) left untested: the
region axis (answered by DSM) and the year axis (still not answered by
anyone). Dubbo attacks a third, named in D36 when it was opened: the
hemisphere and season-cycle axis.

- **The hemisphere/season-cycle axis: answered, for the first time.**
  Dubbo is Southern Hemisphere, 14,504–16,683 km from the three existing
  airports, with physical seasons six months out of phase. The recipe
  wins there too, on a bias shaped differently from any of the first
  three (F61), and the flipped-season check found the calendar signal
  sitting where Dubbo's own summer actually falls rather than copying a
  Northern shape.
- **The year axis: still NOT answered.** Dubbo's rehearsal year is
  2024-08-01 to 2025-07-31 — the same twelve months every earlier
  rehearsal used, because D13's dates are shared by every airport. This
  result says nothing about what a different year would have done, at
  any airport.
- **Not the controlled EGLC-CDG comparison.** Dubbo changes the location
  **and** the target hour (D37, SPEC 4.1), the same honest caveat D33
  attaches to DSM. A Dubbo result answers "does the recipe travel to a
  different hemisphere and season cycle at a comparable local time", and
  must not be quoted as though only the location had moved.

**Read as: independent hemisphere, independent season cycle, same shared
D13 twelve months, two things changed from the European pair (location
and target hour) — the same honest reading D33/F46 give DSM.**

---

## 2026-08-19 — Session 23: THE DUBBO METHOD LOCK (no test yet)

No model was built, run or refitted this session, no data was loaded, and
**Dubbo's test year was not touched**. This section is the written lock for
the fourth airport, mirroring what D35 did for DSM (which mirrored D31 for
CDG and D21 for EGLC), plus the correspondence check that proves it is D35
with the location and the target hour swapped and nothing else.

**A numbering note, made before anything else, because it affects every
reference below.** The session 23 prompt suggested this lock be numbered
D38. Session 20 already used D38 for its own entry (the SPEC housekeeping
that recorded DSM's pass and added Dubbo's row — see above,
"2026-08-19 — Session 20 decision"), which the session 23 prompt-writer
could not have known when the prompt was drafted, since it was written
before session 20 ran. DECISIONS is append-only and D38 is settled, so this
lock is **D39**, not D38. Nothing else about the prompt's instructions is
affected by this — it is a numbering correction only.

**D39. Dubbo's method is LOCKED. This entry fully specifies what Dubbo's
sealed-test session will run.**

This is **D35 with the airport and the target hour swapped and nothing else
touched.** Every methodological choice below — the model, its settings, the
features, what is predicted, the pairing rule, the missing-data rule, the
references, the metric, the bar, and the one-look rule — is the same choice
D35 made, which was the same choice D31 and D21 made before it. Not one of
them is new.

**Two things differ from D35, exactly as two things differed from D31 when
D35 was written.** D35 could not say "only the location changed" against
D31, because DSM changed the location **and** the target hour. The same is
true here: Dubbo changes the location **and** the target hour against every
earlier lock, including D35 (D37, F50, SPEC 4.1). That cost was accepted on
purpose, in advance, and is written into SPEC 4.1 and D37. It is repeated
here so the test session cannot report a Dubbo result as though it were the
same controlled comparison EGLC and CDG make between them.

Why it is written out separately rather than by pointing at D35: D35 names
Des Moines throughout and fixes the target at 18:00 UTC, so Dubbo's test
session would otherwise have to reach back to a DSM-named record and
translate it — three times over, through D31 and D21 before it — while the
test year was open. The whole value of a lock is that the executing session
decides nothing (D21.11, D31.11, D35.11). A translation is a decision. So
the translation is done here, now, with Dubbo's test year still unopened,
and the test session executes this record and reports.

**D39.1 — Target.** The temperature at **02:00 UTC** at **Dubbo, Australia
(IEM/ICAO station code `YSDU`, IEM network `AU__ASOS`)**, the station at
latitude -32.2167, longitude 148.5747, elevation 275 m — IEM's own
position, per SPEC 3.4 and F49. The forecast comes from the Open-Meteo grid
point that position maps to: latitude -32.274643, longitude 148.59375,
elevation 279 m, 6.69 km from the airport with a +4 m height difference
(SPEC 3.4, F49) — the largest grid offset of the four airports so far,
still small and still the same kind of steady local error this project
exists to learn (Q5). One row per day.

The hour is **02:00 UTC, not 12:00 or 18:00 UTC**, and that is one of the
two methodological inputs this lock does not share with D35 (the other is
the airport itself). 02:00 UTC is local standard noon at Dubbo (12:00 AEST
in winter, 13:00 AEDT in summer, daylight saving deliberately ignored so
the target stays one fixed UTC hour all year), which is what SPEC 4.1 asks
every airport to target. Decided on principle before any Dubbo data was
seen (D37) and then checked against the timezone database (F50), the same
discipline F32 applied for DSM.

**D39.2 — What the model predicts.** The **residual**: observed minus
forecast (SPEC 4.2). The corrected forecast is the GFS forecast plus the
predicted residual. The model never predicts temperature directly.
Identical to D35.2, D31.2 and D21.2.

**D39.3 — Features.** The D19 minimal set, exactly three:
```
forecast_temp_c   the GFS forecast temperature for that day at 02:00 UTC
season_sin        sin(2 * pi * year_fraction(date))
season_cos        cos(2 * pi * year_fraction(date))
```
where `year_fraction` is `(day_of_year - 1) / 365`, or `/ 366` in a leap
year. No hour-of-day feature — the hour is fixed at 02:00, so it carries no
information, which is D19's reason unchanged. No recent-observation
feature, even though SPEC 2.1d would allow one — see D19 for why. Identical
to D35.3, D31.3 and D21.3 apart from which fixed hour `forecast_temp_c` is
read at, which follows from D39.1. The encoding is hemisphere-blind by
construction, and F61's flipped-season check found the model free to place
its largest correction in Dubbo's own summer (December–February) rather
than copying a Northern-hemisphere shape — evidence the encoding
generalises rather than having quietly learned "June–August is warm".

**D39.4 — Model and settings.** LightGBM gradient-boosted trees (SPEC 4.4,
D12), with exactly the session 05 settings, unchanged:
```
objective=regression_l1   (absolute error, D20)   n_estimators=300
learning_rate=0.05        num_leaves=15           min_child_samples=40
subsample=1.0             colsample_bytree=1.0    reg_alpha=0.0
reg_lambda=0.0            random_state=42         n_jobs=1
deterministic=True        force_row_wise=True     verbose=-1
```
Nothing is tuned, searched or varied in the test session. Library versions
are pinned in `requirements.txt` (D24): python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0. Identical to D35.4, D31.4 and D21.4. Session 22 already ran
this exact configuration at Dubbo, and its PART 0 proved it against
`scripts/session05_model.py`: **0 model settings differ, and exactly 1
shared constant differs — TARGET_HOUR, 12 to 2** (F62). That one constant
is D37 and nothing else.

**D39.5 — Training data for the test: the FULL D13 training window,
2021-03-24 to 2025-07-31, at Dubbo.** That is Dubbo's inner-training **and**
Dubbo's validation year recombined into one training set.
- Reason: the same reason D21.5, D31.5 and D35.5 gave. The D18 split
  existed so the method could be rehearsed without touching the test year.
  The method is locked, so validation has finished its job, and holding a
  year back would only throw away real training data. Refitting on all
  non-test data before the single test is the standard move — and it is
  what all three earlier airports did, so doing anything else here would
  add a further difference on top of the location and the hour.
- Everything fitted is fitted on this window and nothing else: the model,
  the climatology baseline (SPEC 2.1c) and the mean-bias figure.
- **Expected row count, written down before the run, and confirmed against
  session 22's join (F60).** The window holds 1,591 calendar days. Session
  22 kept **1,193 inner-training rows and 360 validation rows**, both
  exactly as F59 predicted before the join ran, so:
  ```
  inner-training rows (F60)                      1,193
  validation rows      (F60)                       360
  expected training rows for the test refit      1,553 of 1,591 calendar days
  days dropped, all reconciled by F60               38
      the shared 492-hour forecast gap               21  (2023-12-30..2024-01-19)
      observation-side losses, inner-training         12
      observation-side losses, validation              5
  ```
  **1,553, not 1,571, 1,569, or 1,569.** Every earlier airport lost only the
  shared forecast-gap days on the training side (EGLC and CDG 22 days each
  including their own small observation losses; DSM 20 days, all gap, none
  observation). Dubbo loses 21 gap days (one more than the three others,
  because its 02:00 target falls before the gap's last missing hour,
  11:00 — see F59, F60) **plus 17 real observation-side losses** — the
  first time any airport's training refit loses meaningful rows to
  something other than the shared gap. This is F58's higher off-hour and
  real-gap rate on the observation side, carried through to the row count
  a lock has to state. A count other than 1,553 is a D39.11 stop signal.
- **Note the consequence, so it is not a surprise:** the model that is
  tested is **not** the model measured in session 22. It is the same
  recipe fitted on about 30% more days than inner-training alone, including
  one more full cycle of seasons. **The test number will not match session
  22's 1.283 rehearsal figure and should not be expected to.** At EGLC the
  equivalent move shifted the number by 0.125 degC (F16), at CDG by 0.169
  degC (F30) and at DSM by 0.234 degC (F47), and in all three cases most of
  that was the weather rather than the extra data.

**D39.6 — Test data: Dubbo, 2025-08-01 to 2026-07-31 (D13), and nothing
after it.** Data after 2026-07-31 is not used, keeping the test set exactly
one calendar year. This is Dubbo's own test year: the dates are the same as
every earlier airport's but the data is a fourth airport's, and it has
never been looked at.

What "opened for the first time" means precisely here. Two yearly chunk
files carry the test year, and the 2025 chunk has been read with a
cut-off:
```
openmeteo_previousruns_gfs_global_YSDU_2026-01-01_2026-07-31.json   never read
iem_asos_YSDU_2026-01-01_2026-07-31_routine.csv                     never read
openmeteo_previousruns_gfs_global_YSDU_2025-01-01_2025-12-31.json   read, but
iem_asos_YSDU_2025-01-01_2025-12-31_routine.csv                     cut at
                                                                    2025-07-31
```
The two 2026 YSDU chunk files have never been opened by any session.
Session 20 counted row presence, gap positions and report timing across
the whole period including the test window, but never a temperature value
from it (F57, F58, F59) — a structural count, not a look at the data.

**One respect in which this is cleaner than every earlier lock, worth
stating plainly rather than silently inherited.** D35.6 had to record that
DSM's (and EGLC's and LFPG's) verify-on-contact samples fell inside the
test year — printed observation values months before the look, not
leakage, but a habit Q29 flagged. Session 19's own findings state that the
Q29 fix was applied **from the start** at Dubbo: every verify-on-contact
sample was drawn from 2021 (the shared archive-start probes) or 2024
(comfortably inside training), and none from 2025-08-01 onward. So unlike
every airport before it, **no value from Dubbo's test year has ever been
printed, computed or looked at, by any session, for any reason.** This
closes the gap Q29 raised, one airport early into the "future airports"
half of its own suggestion.

**D39.7 — Pairing and missing data.** The D14 rule, applied exactly as
written at the other three airports: the routine report is the truth
observation, each target-hour forecast is paired with the report nearest
that hour, and if no report falls within 15 minutes of the hour the day is
dropped and counted. Drop, count, report — nothing filled, ever (SPEC 2.2).
The drop counts for both the training window and the test year are part of
the output.

The location facts inside this: **Dubbo reports on the hour (`:00`)** —
the same shape as LFPG (SPEC 3.4, F53) — where DSM reports at `:54` and
EGLC at `:50`. So the rule pairs 02:00 UTC with the **02:00 report — an
exact match, no offset at all**, session 22 confirming every one of the
1,553 kept training-window days paired at a 0-minute offset (F60). Dubbo
also files a genuine second scheduled report, mostly at `:30` (F55) — the
same shape as EGLC and LFPG, unlike DSM, which has none (F36) — but it is
not used as a fallback: D30 already settled that the pairing rule is not
adapted for one airport, and Dubbo reuses that unchanged.

**Important — Dubbo is unlike the other three here, and this is the one
genuine structural difference the correspondence check below calls out.**
Every earlier lock could state a single expected test-year drop count with
confidence: EGLC and CDG each predicted a handful of days from a named
cause, DSM predicted **zero**. Dubbo cannot. Session 20's gap map (F57,
F59) is explicit:
```
forecast-gap days in Dubbo's test year                            0   (F57, F59)
observation-side losses in Dubbo's test year                      9   (F59)
    of which an off-hour-only report                              1   (2025-08-30, F59)
    of which no report at all near the 02:00 hour                 8   (F59)
expected paired rows                                            356 of 365
```
**The individual dates of the 8 "no report" test-year losses are not named
anywhere in DECISIONS.** F60 named every inner-training and validation loss
by date when the join ran (12 and 5 respectively), because the join had
those rows in front of it; F59's session 20 gap map gave the test-year
*count* (9) without opening the test year to name the dates, exactly as
SPEC 3.3's boundary requires. **This lock cannot go further than F59
already did without opening the test year, so it does not try.** What it
can and does say: 356 of 365 days are expected to carry a paired row. What
it cannot say in advance, and what every earlier lock could: the exact
**scored**-day count. Persistence needs the previous calendar day's
observation, and with 9 scattered observation-side losses instead of 0 or
1, whether a given scored day's *previous* day is itself one of the 9 (or
adjacent to one) cannot be known without the dates — the same mechanism
that cost EGLC, CDG and DSM one extra scored day each when their own
single test-year loss fell where it did (F16, F30, F47). **This is an
expectation, not a requirement**, exactly as D31.7 and D35.7 said of their
own predictions: the test session reports the **actual** paired-row and
scored-day counts, names every date it drops, and reconciles them against
the 356 figure above. A paired-row count other than 356 is a D39.11 stop
signal; a scored-day count below 356 is expected and should be explained by
naming the dates, not treated as a surprise.

**D39.8 — The four references. Anything that has to be *fitted* is fitted
on Dubbo's training window only.** Raw GFS and persistence are fitted on
nothing — they are just values. Climatology and the mean-bias figure are
fitted, and both come from Dubbo's D13 training window (SPEC 2.1c).
- **Raw GFS** — the forecast value itself, uncorrected. *Part of the bar.*
- **Persistence** — the previous calendar day's 02:00 UTC observation at
  Dubbo. Past values only (SPEC 2.1d). *Part of the bar.* Note that for the
  first test day, 2025-08-01, "yesterday" is 2025-07-31, which sits in the
  training window and is not one of F60's named observation-side losses.
  That is a past observation, so it is legal and it will be used; written
  down here so it is not mistaken for leakage later. Identical in substance
  to D21.8's, D31.8's and D35.8's note.
- **Climatology** — the seasonal average of the *observed* temperature at
  Dubbo for that position in the year, averaged over every **Dubbo
  training-window** observation within 7.5 days of it, measured around the
  circle so late December and early January are neighbours (SPEC 2.1c).
  *Informative only.*
- **Mean-bias reference** — the forecast plus one constant: the mean
  **Dubbo training-window** bias. *Informative only* (SPEC 5.2, D23). Worth
  carrying forward from F62: on Dubbo's validation year this reference
  **beat** raw GFS (1.368 against 1.397), as it did at EGLC and DSM and did
  not at CDG, because the constant available at Dubbo is not quite nothing
  (-0.1360 degC on inner-training; the training-window figure will differ
  slightly and is computed in the test session, not here). The model beat
  it by 6.3% all the same, so a win over it on the test year is the
  evidence that the correction is structure and not an offset.

All five methods — the four above plus the corrected forecast — are scored
on the **same set of days**, the days where every method has a value.

**One thing about the bar that is Dubbo-specific and is stated in advance
(F62).** Persistence on Dubbo's validation year was 2.577 degC against raw
GFS's 1.397 — persistence is the weaker reference by a wide margin, roughly
the same order as DSM's split (4.108 against 1.748, F45) though not as
extreme. **So at Dubbo, as at DSM, the binding half of the bar is expected
to be raw GFS, not persistence.** This changes nothing about the bar, which
is both halves as always; it is written down so the test session reports
the raw-GFS margin as the one that decides the verdict in practice.

**D39.9 — The metric and the bar.** Mean absolute error in degrees Celsius
(SPEC 5.1). **Dubbo passes if the corrected forecast has a lower MAE than
both raw GFS and persistence over Dubbo's test year.** No numeric margin —
the bar is qualitative and stays that way (D22, SPEC 5.3). Climatology and
the mean-bias reference are reported but do not decide pass or fail. The
margin is reported prominently alongside the verdict, so a technical pass
by a hair reads as what it is (D22).

**The bar is judged once per airport, on that airport's own data (SPEC
5.0).** EGLC's, CDG's and DSM's passes do not excuse a Dubbo failure, and a
Dubbo result does not re-open any of theirs. Stage 1's 16.3% and stage 2's
13.5%/6.3% are not targets Dubbo has to reach and not numbers Dubbo is
measured against; Dubbo is measured against Dubbo's own raw GFS and Dubbo's
own persistence, and nothing else.

**D39.10 — One look, and the result stands.** Dubbo's test year is opened
once, this method is run once, and whatever comes out is reported
straight — pass or fail, with the seasonal breakdown and the drop counts.
A failure is an honest finding (SPEC 2.4), not something to fix by trying
again. If the result disappoints, the response is a new decision logged
here by the owner, never a quiet re-run. Identical to D21.10, D31.10 and
D35.10.

Read plainly. Dubbo's rehearsal margin, 8.2% (F62), sits between CDG's
3.4% and DSM's 16.1% — closer to CDG's, on the airport whose rehearsal win
is the most concentrated in one season of any airport so far (F62's "2 of
4 seasons helped" and its "-0.516 carries almost the entire result").
**Neither a comfortable pass nor a narrow failure should be treated as
expected.** A Dubbo failure remains an outcome this project reports rather
than avoids.

**D39.11 — Deviation is a stop signal.** If Dubbo's test session finds any
reason to depart from this record — a setting that does not fit, a missing
file, a count that will not reconcile against D39.5 or D39.7, a tempting
small improvement — it **stops and raises it with the owner**. It does not
decide on the fly with the test year open. Any change to the above is a
new DECISIONS entry made deliberately, not an adjustment made mid-run.
Identical to D21.11, D31.11 and D35.11.

**D39.12 — The single-season watch-item, recorded before the look and NOT
acted on.** This is inside the lock so that any inspection after the test
is honest: the place to look was named before anyone knew what the result
was.

F62 measured, on Dubbo's validation year, that the correction's win is
carried almost entirely by one Northern-labelled season (autumn SON,
Dubbo's own local spring, -0.516 degC of the average improvement) while
the other three seasons are close to flat or very slightly worse:
```
season         days   raw GFS   ML-corr   YSDU chg
winter DJF       90     1.344     1.290    -0.055
spring MAM       90     1.219     1.241    +0.022
summer JJA       90     1.170     1.236    +0.066
autumn SON       85     1.884     1.368    -0.516
```
Only 2 of 4 Northern-labelled seasons improved — the fewest of any airport
so far (EGLC, CDG and DSM each improved in 3 of 4) — and the day-by-day win
rate, 53.5% (190 of 355 days), is also the lowest of the four rehearsals.

**This is not a reason to change the method, and the method does not
change. It is locked.** A win concentrated in one season is more exposed to
that particular season's weather in the test year than a win spread across
all four would be — if the test year's version of that one season behaves
differently from the rehearsal year's, the overall margin could move more
than it has at any earlier airport. **If Dubbo's test result behaves
oddly — a swing either way, a season that does not match the rehearsal, a
result that flips from pass to fail or the reverse of what the rehearsal
margin would suggest — this single season is the first place to look**, and
looking there is a description of what happened, never a licence to re-run
or adjust anything (D39.10, D39.11).

**D39.13 — One data-source fact that is stronger at Dubbo than at DSM,
recorded so the test session states it correctly.** At DSM, F40 found
`gfs_global` and `gfs_seamless` genuinely **differ** on recent dates — 259
of 264 hours, by up to 12.3 degC, because Des Moines sits inside CONUS
where non-GFS models can be blended in. At Dubbo the comparison was run in
the same session that verified the airport on contact (F52) rather than
deferred, and it gives the opposite answer: **identical** in both windows
tested, 312 and 264 hours compared, 0 differences in either, at the same
grid point throughout. This confirms F6's original non-CONUS reasoning
(first shown at EGLC) travels to a second non-CONUS, non-European
continent, rather than being a fluke of Europe specifically. Every Dubbo
chunk was pulled with `gfs_global` (D16) regardless, so nothing in the
project depends on this result either way — but the test session should
say that Dubbo's dataset is confirmed identical to what `gfs_seamless`
would have given, which is a stronger claim than DSM's data can make and
one LFPG's still cannot (Q20 was never re-checked there).

---

**The D35 ↔ D39 correspondence check.** Every D35 sub-point set beside its
D39 counterpart, mirroring the format the D31 ↔ D35 check used. Two kinds
of intended difference are expected, exactly as they were between D31 and
D35: `LOCATION` (the airport and what follows from it) and `HOUR` (the
target hour, per D37, and what follows from it). Anything else appearing
in that column would be a stop signal.

```
point  subject                D35 (DSM)                 D39 (Dubbo)               differs?
.1     target hour            18:00 UTC (D33)           02:00 UTC (D37)           HOUR
.1     why that hour          local standard noon       local standard noon       same
.1     airport                Des Moines / DSM          Dubbo / YSDU              LOCATION
.1     station position       41.534 / -93.6531 / 294m  -32.2167 / 148.5747/275m  LOCATION
.1     position source        IEM's own metadata (F31)  IEM's own metadata (F49)  same
.1     grid point             41.52945 / -93.63281      -32.274643 / 148.59375    LOCATION
.1     grid distance/height   1.76 km, -9 m              6.69 km, +4 m            LOCATION
.1     row granularity        one row per day           one row per day           same
.2     what is predicted      residual = obs - fcst     residual = obs - fcst     same
.2     how corrected is made  fcst + predicted resid    fcst + predicted resid    same
.3     features               3: fcst temp, sin, cos    3: fcst temp, sin, cos    same
.3     fcst temp read at      18:00 UTC                 02:00 UTC                 HOUR
.3     year_fraction          (doy-1)/365 or /366       (doy-1)/365 or /366       same
.3     excluded features      no hour, no recent obs    no hour, no recent obs    same
.4     library and model      LightGBM GBDT             LightGBM GBDT             same
.4     objective              regression_l1             regression_l1             same
.4     n_estimators           300                       300                       same
.4     learning_rate          0.05                      0.05                      same
.4     num_leaves             15                        15                        same
.4     min_child_samples      40                        40                        same
.4     subsample              1.0                       1.0                       same
.4     colsample_bytree       1.0                       1.0                       same
.4     reg_alpha / reg_lambda 0.0 / 0.0                 0.0 / 0.0                 same
.4     random_state           42                        42                        same
.4     n_jobs                 1                         1                         same
.4     deterministic          True                      True                      same
.4     force_row_wise         True                      True                      same
.4     verbose                -1                        -1                        same
.4     pinned versions        py 3.12.2, np 2.5.2,      py 3.12.2, np 2.5.2,      same
                              lightgbm 4.7.0             lightgbm 4.7.0
.4     tuning allowed         none                       none                      same
.5     training window        2021-03-24..2025-07-31    2021-03-24..2025-07-31    same
.5     refit on inner+valid   yes                        yes                       same
.5     what else is fitted    model, climatology,        model, climatology,       same
                              mean bias -- all on it     mean bias -- all on it
.5     rows fitted on         1,571 (1,206+365, F42)     1,553 (1,193+360, F60)    LOCATION
.5     calendar days in it    1,591                      1,591                     same
.5     days dropped, cause    20, all forecast gap       38: 21 gap + 17 obs-side  LOCATION
.5     mismatch warning       test != 1.466 rehearsal    test != 1.283 rehearsal   LOCATION
.6     test window            2025-08-01..2026-07-31     2025-08-01..2026-07-31    same
.6     nothing used after     2026-07-31                 2026-07-31                same
.6     files opened first     the two 2026 DSM chunks    the two 2026 YSDU chunks  LOCATION
       time
.6     verification samples   3 test-day obs values      NONE -- Q29 fix applied   LOCATION
       inside the test year   printed (F34/F35, Q29)     from session 19 onward
.7     pairing rule           D14, nearest report,       D14, nearest report,      same
                              15-minute tolerance        15-minute tolerance
.7     report minute          :54                        :00                      LOCATION
.7     pairing offset         6 min (17:54 -> 18:00)     0 min (exact match)      LOCATION
                                                                                   + HOUR
.7     missing data           drop, count, report,       drop, count, report,      same
                              never fill (SPEC 2.2)      never fill (SPEC 2.2)
.7     second scheduled       none exists at all (F36),  exists, mostly :30       LOCATION
       stream                 D30 cannot arise           (F55), refused (D30)
.7     expected fcst-gap days 0 in test year (F38)       0 in test year (F57,F59) same
.7     expected obs-loss days 0 (F41)                    9: 1 off-hour + 8        LOCATION
                                                          no-report (F59)
.7     expected paired rows   365 of 365                 356 of 365               LOCATION
.7     expected scored days   365, pinned exactly        cannot be pinned in      LOCATION
                              (nothing lost, F41)         advance -- see D39.7     (structural)
.7     drop counts reported   training and test          training and test         same
.8     reference 1            raw GFS, in the bar        raw GFS, in the bar       same
.8     reference 2            persistence, in the bar    persistence, in the bar   same
.8     persistence's source   previous day's 18:00 obs   previous day's 02:00 obs  HOUR
.8     first-day note         2025-07-31 is training,    2025-07-31 is training,   same
                              legal, will be used        legal, will be used
.8     reference 3            climatology, +-7.5 days    climatology, +-7.5 days   same
                              circular, informative      circular, informative
.8     reference 4            mean-bias, informative     mean-bias, informative    same
.8     mean-bias note carried better than raw GFS on     better than raw GFS on    same
       from the rehearsal     validation (F45)           validation (F62)         (both beat)
.8     which half binds       raw GFS, not persistence   raw GFS, not persistence  same
       (expected)             (F45)                      (F62)                    (both DSM-like)
.9     metric                 MAE in degC (SPEC 5.1)     MAE in degC (SPEC 5.1)    same
.9     the bar                beat raw GFS AND           beat raw GFS AND          same
                              persistence                persistence
.9     numeric margin         none, qualitative (D22)    none, qualitative (D22)   same
.9     margin reported        yes, prominently           yes, prominently          same
.9     who decides pass/fail  raw GFS + persistence      raw GFS + persistence     same
.9     judged once per        that airport's own data    that airport's own data   same
       airport                (SPEC 5.0)                 (SPEC 5.0)
.10    number of looks        one                        one                       same
.10    number of runs         one                        one                       same
.10    failure handling       reported straight, not     reported straight, not    same
                              re-run                     re-run
.10    rehearsal margin note  widest of three (16.1%),   between CDG and DSM       LOCATION
                              not a reason to expect a    (8.2%), most season-     (structural)
                              pass (F45)                  concentrated win yet
                                                          (F62), no expectation
                                                          either way
.11    deviation handling     stop and raise with        stop and raise with       same
                              the owner                  the owner
.12    watch-item             warm-end overshoot (F44)   single-season             LOCATION
                                                          concentration (F62)      (structural)
.13    gfs_seamless check     run at DSM, and they       run at Dubbo (in the      LOCATION
                              DIFFER (F40)               same session as verify-
                                                          on-contact), and they
                                                          are IDENTICAL (F52)
```

**Verdict of the check: no methodological choice differs.** The `HOUR` rows
are all one decision — D37's target hour — and what follows from it: which
hour the feature is read at, which hour persistence looks back to, and
(combined with the reporting-minute LOCATION fact) which report the
pairing rule lands on. The `LOCATION` rows are the same kinds D31's and
D35's own checks found — which airport it is, which files hold its data,
when the station reports, how many rows and drops follow from that
airport's own record, what the rehearsal already showed about the
references, and two facts about the data and the record (the watch-item
and the `gfs_seamless` result) — **plus one new kind, marked
`(structural)`, that D35's own table did not need**: the expected
test-year drop and scored-day counts, which cannot be pinned to a single
number the way D35.7 pinned DSM's to zero. That structural difference is
named explicitly in D39.7 and is the one thing this check flags as
qualitatively new rather than a same-shaped fact with a different value.

Every setting, every date, every feature, every reference, the metric, the
bar, the one-look rule and the stop-signal rule are the same in D21, D31,
D35 and D39. Nothing was added to D39 that D35 does not require, and
nothing D35 requires was left out of D39.

**The one difference that must not be smoothed over, stated again because
it is the point of the whole check.** Every earlier lock's test-year
prediction resolved to one number the join either matched or did not: CDG
predicted one lost day, DSM predicted zero, and both landed exactly (F30,
F47). **Dubbo's lock cannot make that same promise.** It can and does
predict the paired-row count (356 of 365) with the same confidence as
every earlier lock, because that count follows directly from F59's
whole-hour gap map without opening the test year. It cannot predict the
final scored-day count with the same confidence, because persistence's
day-before dependency interacts with 9 scattered losses in a way that
needs the actual dates to resolve — dates this lock deliberately does not
have, because getting them would mean opening the test year early. The
test session must name every date it drops and show the arithmetic, not
just report a number.

---

## 2026-08-19 — Session 23 note (nothing measured, nothing opened)

This session ran no code, loaded no data and produced no numbers of its
own, so there is no new F-entry. What it produced is D39, the
correspondence check above, one authorised SPEC edit (below), and the
STATUS update.

**Nothing was opened.** Dubbo's test year was not loaded, read, printed,
averaged or fitted on. No model was run, fitted or refitted. No file in
`data/raw/` was read this session at all — every file name in D39.6 comes
from listing the directory and from session 20's and 22's already-published
findings, not from opening a file this session.

**No open question was closed or raised.** Q30 remains the project's only
live open question, unchanged by this session.

**Nothing was committed.**

---
