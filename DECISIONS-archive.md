# DECISIONS-archive.md — settled decisions and findings, moved verbatim

This is the append-only archive of settled DECISIONS.md entries, moved out
to cut the token cost of reading DECISIONS.md in full every session.
**Nothing here is deleted or altered.** Every block below is byte-for-byte
identical to how it originally appeared in DECISIONS.md; git history holds
every prior version of both files as a second safety net. Read this file
only when a session needs deep history from a passed stage or airport — it
is not part of the routine per-session read (CLAUDE.md).

Moved by **session 21** (2026-08-19), a one-time authorised restructure — see
the session 21 entry near the bottom of DECISIONS.md. After this move, both
files resume strict append-only: new material is added to the bottom of
DECISIONS.md, never here, and nothing is ever moved again as a matter of
routine.

---

## From "2026-08-16 — Initial decisions from planning" (D1–D12)

Moved because their conclusions are now codified as active SPEC rules; the
operative rule lives in SPEC, this is the settled "why" behind it.

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

## From "2026-08-16 — Session 01 findings (first real data pull)" (F1–F4)

Moved because these are settled, EGLC-only verify-on-contact findings,
superseded as ongoing precedent by the project-wide findings that followed
(F8, F9, D14). F1's continuity claim is corrected by F11, moved here
alongside it below.

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

## From "2026-08-16 — Session 02 findings (documentation checks)" (F6 only)

Moved because this is a settled, EGLC-only `gfs_seamless`-vs-`gfs_global`
equivalence check. D16 (pinning `gfs_global`) is the active rule it
supports; the same check was later repeated per airport (F40 at DSM, F52 at
Dubbo — see those live DECISIONS.md entries for the current, airport-by-
airport picture).

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

---

## From "2026-08-17 — Session 04 findings" (F11 only — the correction to F1)

Moved to sit beside F1, which it corrects. F8 (kept live in DECISIONS.md) is
the finding that actually maps EGLC's forecast gap; F11 just records that
F1's earlier continuity claim was wrong.

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
