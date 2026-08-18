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
