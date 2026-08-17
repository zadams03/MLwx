# DECISIONS.md — the project's memory of *why*

This is an **append-only** log. Add new entries at the bottom. Never delete
or rewrite old entries. Each entry is dated.

It records choices made, why they were made, open questions, and findings.

---

## 2026-08-16 — Initial decisions from planning

**D1. The project is bias-correction, not weather prediction from scratch.**
We are not building a weather model. GFS already does the physics well. We
learn and correct its repeated *local* mistakes at one airport. Reason:
building a weather model from scratch is a solved, resource-heavy problem we
could only do worse; correcting local bias is tractable, useful, and runs on
a laptop.

**D2. Location: London City airport (EGLC).** Reason: airports report clean,
official, standardised hourly observations, which is the "what actually
happened" truth the method needs.

**D3. Truth data from IEM, not Weather Underground.** Reason: the free
Weather Underground API was discontinued at the end of 2018, and what remains
is largely *personal* weather stations (back-garden sensors) of inconsistent
quality and siting. Those are the wrong ground truth — a forecast should be
checked against an official station, not a hobbyist sensor. IEM serves
official airport METARs free, no account. EGLC confirmed live on IEM (a
current observation was returned dated 10 August 2026).

**D4. Forecast data from Open-Meteo Previous Runs API — NOT the Historical
Forecast API.** This is a critical, easy-to-get-wrong choice.
- The **Previous Runs API** gives genuine past forecasts at a fixed lead-time
  offset (e.g. the value predicted exactly 24 hours before). This is what we
  want: it is what a real forecast looked like on the day.
- The **Historical Forecast API**, despite the name, stitches the freshest
  few hours of many runs into one series — which effectively already contains
  the answer. Training on it would be look-ahead leakage.
Open-Meteo's own docs describe the Previous Runs API as the correct dataset
for training bias-correction models without look-ahead bias.

**D5. Data floor is March 2021.** Confirmed: Open-Meteo's archive of past GFS
forecasts (2m temperature) goes back to March 2021 — about 4.5 years. Reason
it can't go earlier: genuine point-resolution past forecasts were not
routinely archived before then, so that history mostly does not exist to be
recovered. This is a real floor, not a paywall. 4.5 years is enough for
stage 1 (covers several full seasonal cycles).

**D6. Reanalysis (e.g. ERA5, back to 1940) is NOT used as the forecast to
correct.** Reanalysis is a reconstruction of the past made *with* the
observations fed in — it is not a real forecast and has little forecast error
to learn from. Using it would quietly turn the project into a weaker,
different exercise. (It could legitimately help only for computing a
climatology baseline, but for stage 1 we compute climatology from the IEM
observations we already have, so ERA5 is not needed at all.)

**D7. Training window: train ~March 2021 to mid-2025; hold out the most
recent ~12 months as an untouched test period.** Reason: a full-year test set
judges the result across all four seasons, so a lucky run of easy weather
cannot flatter it.

**D8. Stage 1 lead time: 24 hours only. 48 hours is a planned later
addition.** Reason: stage 1's job is to prove the pipeline works end to end;
one lead time keeps it simplest and most reviewable. Comparing 24h vs 48h
(how bias grows with lead time) is interesting but comes later.

**D9. Stage 1 target: temperature at one fixed hour of the day.** This
evolved during planning. The owner ultimately wants a live tool showing a
corrected temperature *curve* across the day (e.g. the 9am value, the noon
value, the daily max). But we deliberately keep stage 1 to a single fixed
hour — the cleanest possible test of "does the core idea work?" — so that a
weak result points clearly at the idea, not at added complexity. Widening to
the full hourly curve is stage 5; the daily max then falls out as the peak of
the curve.

**D10. Evaluation bar (frozen): beat raw GFS AND persistence on MAE over the
held-out test period.** Beating raw GFS is the core claim; beating persistence
("tomorrow = today") is the honesty check against the laziest guess.
Climatology (seasonal average) is an optional third check. The numeric margin
is left qualitative for now; a specific figure may be fixed just before
running, but still before seeing results, and logged here at that point.

**D11. Missing data: drop, count, report — never fill.** Reason: filled data
is invented data and muddies the honest measurement. If gaps turn out
frequent enough to matter, that is a finding to log here, not something to
auto-patch.

**D12. Model type: gradient-boosted trees.** Reason: the data is
table-shaped (one row per forecast, a handful of numeric features), which is
exactly what tree models handle well, and they run on a laptop CPU with no
GPU needed.

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

## 2026-08-16 — Session 01 findings (first real data pull)

Both sources were pulled for real. Q1 and Q2 above are now answered and
closed. Nothing was filled, cleaned, or joined.

**F1. Q1 answered — yes, the forecast archive reaches March 2021, but it
starts on 24 March 2021, not 1 March.** A request for 1–7 March 2021 came
back HTTP 200 with all 168 hourly values null. Stepping the date forward
found the first hour with a real value: **2021-03-24 00:00 UTC**. Spot checks
at 15 April 2021, 1 May, 15 May, 15 June, 15 September, 15 December 2021,
15 March 2022, 15 March 2023 and 15 March 2025 all came back complete, so the
archive is continuous from that start. This refines D5 rather than
contradicting it: the floor is real, and about 5 years 5 months of history is
available up to today. SPEC 3.2 and 4.3 say "March 2021", which is still
true; the owner may want to write the exact date in.

**F2. Q2 answered — EGLC's observation record is good.** Counting a whole
hour as covered only if it has a routine report carrying a real temperature:
- Recent sample, 1–21 July 2026: 504 hours expected, **504 covered, 0 gaps**.
- Early sample, 18 March – 1 April 2021: 336 hours expected, **333 covered,
  3 gaps (0.89%)**. The missing hours are 2021-03-20 06:00, 2021-03-30 05:00
  and 2021-03-30 06:00 UTC.
All three gaps are whole reports that were never filed, not rows with a blank
temperature. They sit in the early-morning hours, and two of the three are
next to each other, which looks like a short outage rather than a pattern.
Nothing was filled (SPEC 2.2). On this evidence the gap rate is low enough
that dropping unpaired rows will cost very little data, but that is a
two-week snapshot, not proof about the whole period.

**F3. EGLC reports twice an hour, not once.** IEM splits its reports into
"routine" (report_type=3) and "special" (report_type=4). Normally "special"
means an unscheduled extra report. At EGLC it is not: over 1–21 July 2026
there were exactly 504 reports at :50 and exactly 504 at :20 — one of each
per hour, none missing. So EGLC files a scheduled half-hourly report. This
session used the routine :50 report as the hourly observation and kept the
combined pull as a second raw file for the record. The extra :20 report is
spare data available later if it is ever useful.

**F4. The 24-hour-ahead forecast variable is
`temperature_2m_previous_day1`.** This is the value from the model run one
day earlier, which is what SPEC 3.2 asks for. The endpoint also offers a
plain `temperature_2m`, which on this API is the freshest-run series — the
leakage trap SPEC 2.1b warns about. It was deliberately not requested, so it
is not in any raw file. The model name used was `gfs_seamless`.

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

**F6. C2 answered — at EGLC, `gfs_seamless` is purely NCEP GFS, and it returns
data identical to the explicit `gfs_global` string.**

What "seamless" means: Open-Meteo's documentation says a seamless model
"combines all models from a given provider into a seamless prediction", and
for each location picks the highest-resolution model that covers it. For the
NCEP provider the candidates are GFS (global) and HRRR/NAM/NBM (all
CONUS-only, that is the United States). HRRR "data are only available for the
United States, while for other locations, only GFS is used". EGLC is in
London, so no CONUS model can ever apply, and nothing non-GFS is in the NCEP
set to mix in.

That was then checked against the live API. The same request was sent with
several model names, for EGLC, 1–2 July 2026:

```
https://previous-runs-api.open-meteo.com/v1/forecast
  ?latitude=51.505&longitude=0.055
  &hourly=temperature_2m_previous_day1
  &models=<NAME>
  &start_date=2026-07-01&end_date=2026-07-02&timezone=UTC
```

Results:

| model name            | result                                                    |
|-----------------------|-----------------------------------------------------------|
| `gfs_seamless`        | OK — 48 hours, 0 missing, grid 51.487137 / 0.0, elev 4 m  |
| `gfs_global`          | OK — 48 hours, 0 missing, same grid point                 |
| `ncep_gfs_seamless`   | OK — 48 hours, 0 missing, same grid point                 |
| `ncep_gfs_global`     | OK — 48 hours, 0 missing, same grid point                 |
| `gfs013`              | OK — 48 hours, 0 missing, same grid point                 |
| `gfs025`              | accepted, but all 48 values null (grid 51.5 / 0.0)        |
| `gfs_graphcast025`    | accepted, but all 48 values null                          |
| `gfs_global_011`      | rejected — "invalid String value gfs_global_011"          |
| `gfs_global_025`      | rejected — "invalid String value gfs_global_025"          |
| `ncep_gfs_global_011` | rejected — "invalid String value ncep_gfs_global_011"     |
| `ncep_gfs_global_025` | rejected — "invalid String value ncep_gfs_global_025"     |
| `gfs_hrrr`            | rejected — HTTP 400                                       |

Note that the names shown on the current documentation page (`ncep_gfs_global_011`,
`ncep_gfs_global_025`) are **not** accepted by this endpoint. The names that
work are the shorter ones.

`gfs_seamless` and `gfs_global` were then compared value by value over two
windows:
- 1–21 July 2026: 504 hours, **identical, 0 differing values**, 0 missing in
  either.
- 24 March – 5 April 2021 (the very start of the archive): 312 hours,
  **identical, 0 differing values**, 0 missing in either.

Also worth recording: `gfs_graphcast025` returns nothing for this variable and
period, so Google/DeepMind-style AI output is not quietly entering the series
even in principle.

**Recommendation (for the owner to confirm — nothing was changed).** Pin the
explicit string **`gfs_global`** for the session 3 pull, instead of
`gfs_seamless`. At EGLC the two are provably the same data, so this costs
nothing, but it makes the claim "this is exactly NCEP GFS" true by
construction rather than by argument, and it stops a future change to
Open-Meteo's seamless blending from silently changing the dataset underneath
us. If the owner prefers to keep `gfs_seamless` for consistency with the
session 01 raw files, that is also defensible on this evidence — but the
choice should be written down either way. See Q8. Note for stage 2: CDG is
also in Europe, so the same reasoning applies there, but it should be
re-checked rather than assumed.

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

**F11. Correction to F1 — the forecast archive is not continuous.** F1
(session 01) concluded, from nine spot checks, that the archive "is continuous
from that start". That conclusion is **wrong and is superseded by F8**, which
mapped every hour and found a single 492-hour gap running 2023-12-30 00:00 to
2024-01-19 11:00 UTC. F1's other claims stand — the archive does begin at
2021-03-24 00:00 UTC, and a request for 1 March 2021 does return all nulls.
Only the continuity claim fails. F1 itself is left exactly as written, because
this log is append-only; this entry is the correction. The lesson worth keeping:
spot checks can only ever show that the places you looked have data, never that
the places you did not look do.

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

