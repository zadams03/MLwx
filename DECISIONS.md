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

