# DECISIONS-archive.md — settled decisions and findings, moved verbatim

This is the append-only archive of settled `DECISIONS.md` entries, moved out
to cut the token cost of reading `DECISIONS.md` in full every session.
**Nothing here is deleted or altered.** Every block below is byte-for-byte
identical to how it originally appeared in `DECISIONS.md`; git history holds
every prior version of both files as a second safety net. This file is
**not** part of the routine per-session read (`CLAUDE.md`) — read it only
when a session needs deep history from a passed stage or airport, in
particular an archived entry's exact wording rather than just its headline
(most needs are already served by the headline already carried forward into
`SPEC.md` or `RESULTS.md`).

**How citations into this file work.** Entry numbers (`Dxx`, `Fxx`) never
change when an entry moves here. A `(Dxx)`/`(Fxx)` citation anywhere —
`SPEC.md`, `RESULTS.md`, `STATUS.md`, `CLAUDE.md`, or a still-live
`DECISIONS.md` entry — always resolves to exactly one entry, in exactly one
of the two files; no move ever breaks a citation. A reader who hits a
`(Dxx)`/`(Fxx)` they don't recognise as still-live in `DECISIONS.md` should
look here next. `DECISIONS.md` also leaves a short pointer at the top of each
dated section this file absorbed, naming what moved and why.

**Archiving is a routine part of every session's end-of-session roundup, not
a one-time exception.** Session 21 (2026-08-19) made the first move, an
authorised one-time restructure, and at the time said "nothing is ever moved
again as a matter of routine." **That framing is superseded, starting with
session 34b (2026-09-11):** moving settled entries out of the live
`DECISIONS.md` is now routine (`CLAUDE.md`'s "End of every session" list),
applying the same settled-and-not-needed-live criterion each time. What is
unchanged, and never will be: entries move **verbatim**, nothing is ever
deleted, and numbering is never reused or renumbered. Session 21's own
restructure record — the meta-record of the *first* move — has itself since
been moved here (by session 34b), immediately below the founding D1–D12/F1–F4
material it describes moving.

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

---

## Moved by session 34b (2026-09-11)

The archive criterion (restated in D46, live in `DECISIONS.md`) was applied
to the whole of `DECISIONS.md` as it stood after session 33, per the manifest
at `notes/session-34-archive-manifest.md` (session 34a), with the manifest's
one BORDERLINE call (the session-21 restructure record) resolved to MOVE by
the owner. This is the **second** archive move — the first, session 21, moved
D1–D12 and F1–F4/F6/F11 and sits at the top of this file. This move covers
the rest of what was live before session 34b: **D13–D45 and F5, F8–F84**,
except **D17 and F7**, which stayed live because the live richer-features
finding F85 depends on their specific wording, not just their headline. Kept
live in `DECISIONS.md`: D17, F7, F85–F87 (the richer-features phase in full),
every open question (Q30, Q32), and the parked items (P1–P3). See the
manifest for the full per-entry rationale, and D46 (live in `DECISIONS.md`)
for this session's summary. The blocks below are exactly what was cut from
`DECISIONS.md`, unedited.

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

## 2026-08-16 — Session 03b findings (the full historical pull)

The full pull ran for real: 2021-03-24 to 2026-07-31, both sources, six
yearly chunks each, 24 files in `data/raw/` with a `.meta.txt` beside every
one. Nothing was joined, filled, cleaned or modelled.

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

## 2026-08-19 — Session 24 findings (the Dubbo sealed test)

The single authorised look at Dubbo's test year (D39.10), executing DECISIONS
D39 exactly as written. The script is `scripts/session24_test.py` and the
full real output is `notes/session-24-check-output.txt`. Two consecutive runs
produced byte-identical output apart from the clock time in the header line.
PART 0 proves against `scripts/session05_model.py` that 0 model settings
differ, and against `scripts/session18_test.py` (DSM's sealed test) that
exactly 1 constant differs — TARGET_HOUR, 18 to 2 — which is D37 and nothing
else; every loader function is IDENTICAL once docstrings are stripped out,
so "the airport and the hour changed, and nothing else" is checked in code,
not argued.

**F64. DUBBO PASSES. At Dubbo the corrected forecast beats both raw GFS and
persistence on the held-out test year — the narrowest margin of the four
airports, and the one D39.12's watch-item said in advance to read carefully.**

The verdict first, because that is what the session was for:

```
                        MAE degC   part of bar?
Raw GFS                    1.251   YES
Persistence                2.669   YES
Climatology                3.143   no  (informative)
Mean-bias reference        1.238   no  (informative)
ML-corrected               1.210   the claim

vs Raw GFS       BEATEN   1.210 against 1.251  ->  0.041 degC better (3.3%)
vs Persistence   BEATEN   1.210 against 2.669  ->  1.458 degC better (54.7%)
```

**Dubbo passes on the frozen bar (SPEC 5.3, 5.0, D39.9): the corrected
forecast has a lower MAE than both raw GFS and persistence over 2025-08-01
to 2026-07-31 at Dubbo.** The margin is stated prominently because D22
requires it. It is **0.041 degC, a 3.3% cut against raw GFS** — a clear pass,
but the smallest margin any airport has returned on a sealed test year
(EGLC 16.3%, CDG 13.5%, DSM 6.3%), continuing the same direction DSM's test
already showed against its own rehearsal.

**The training refit and the test-year join both reconcile exactly against
what D39 predicted before the look — including the one respect in which
D39's own prediction was structurally weaker than every earlier lock's.**

```
training window kept rows            predicted   actual   verdict
inner-training (F60)                     1,193    1,193    MATCHES
validation (F60)                           360      360    MATCHES
full refit total (D39.5)                 1,553    1,553    MATCHES

test-year paired rows (D39.7)         predicted   actual   verdict
forecast-gap days                            0        0    MATCHES
days lost to an off-hour-only report         1        1    MATCHES
days lost to no report near 02:00            8        8    MATCHES
days lost to a report with no temp           0        0    MATCHES
paired rows                                356      356    MATCHES
```

**Every one of the 9 test-year observation-side drops is named here, for the
first time anywhere in this project** — D39.7 deliberately left them
unnamed, because naming them would have meant opening the test year early:

```
2025-08-30   off-hour report only (:30, 30 min out) — dropped by D14
2025-10-28   no report near 02:00 at all
2025-11-15   no report near 02:00 at all
2025-11-25   no report near 02:00 at all
2025-11-30   no report near 02:00 at all
2025-12-03   no report near 02:00 at all
2026-01-18   no report near 02:00 at all
2026-02-14   no report near 02:00 at all
2026-04-12   no report near 02:00 at all
```

**Unlike every earlier airport, the paired-row count (356) and the
scored-day count (347) are not the same drop.** D39.7 explained why in
advance: persistence needs the previous calendar day's observation, and with
9 scattered losses instead of DSM's 0 or CDG's 1, some of those losses cost
the day *after* them as well. Exactly that happened, on all 9 of the 9 — each
of the 9 dates above cost persistence its following day too, so 356 paired
rows became **347 scored days**, all five methods judged on the same 347:

```
2025-08-31   2025-10-29   2025-11-16   2025-11-26   2025-12-01
2025-12-04   2026-01-19   2026-02-15   2026-04-13
```

No day was lost twice — the 9 "day after" losses are all distinct from the 9
original losses and from each other. This is a genuinely new shape of
bookkeeping in the project (every earlier airport's paired-row and scored-day
counts differed by at most one), and it is exactly what D39.7 said would need
the actual dates to resolve.

**D39.8's persistence note, checked and confirmed as legal.** The first
scored day, 2025-08-01, takes its persistence value from the 2025-07-31
02:00 observation (+13.0 degC) — a training-window value, not one of F60's
named observation-side losses, exactly as D39.8 said in advance.

The full table, all five methods on the same 347 days:

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.251     -0.212      1.748        7.50
Persistence                2.669     +0.069      3.765       19.00
Climatology                3.143     +1.687      4.061       13.36
Mean-bias reference        1.238     -0.020      1.735        7.31
ML-corrected               1.210     +0.144      1.686        6.57
```

**D39.8 named the deciding half of the bar in advance and it was right.**
Persistence at Dubbo is 2.669 degC, **2.13 times raw GFS**, so the raw-GFS
comparison is what decides the verdict in practice; the persistence half is
met by a wide margin that says little. Both halves are still required by the
bar and both were met.

**It beats the mean-bias reference too, but only by 2.3% (1.210 against
1.238) — the thinnest evidence of learned structure any airport has shown.**
At EGLC the model beat the mean-bias reference by 15.7%, at CDG by 13.0%, at
DSM by 3.4%. At Dubbo it beats it by 2.3%. The mean training-window bias
itself is **-0.1914 degC** — smaller than DSM's -0.2715 but larger than
CDG's -0.0600 and EGLC's -0.1479 — so a small constant is worth taking here,
as D39.8 said, and what is left over after taking it is a thin but real win.
The honest reading: at Dubbo, more of the correction's margin over raw GFS is
carried by that one constant than at any airport tested so far, and less is
left over as structure — continuing DSM's direction, not reversing it.

**Day by day, not just on average.** The correction was closer to the truth
than raw GFS on **182 of 347 days (52.4%)** and further away on 165
(47.6%), with no day where it made no difference. That is the lowest of the
four airports — EGLC 60.9% (F16), CDG 58.7% (F30), DSM 53.4% (F47) — a clean
descending order across the four sealed tests so far, though nothing in the
recipe orders them; it is simply what each airport's own test year gave.

**Per season, the correction helped in two of the four — the fewest of any
airport, matching what F62 already found on the rehearsal, but the SEASON
THAT HELPED IS NOT THE SAME PAIR:**

```
season         days   raw GFS   ML-corr    change   persistence
winter DJF       83     1.325     1.330    +0.005         2.880
spring MAM       90     1.010     0.972    -0.038         2.278
summer JJA       90     1.194     1.199    +0.004         1.978
autumn SON       84     1.498     1.359    -0.138         3.619
```

("change" is corrected MAE minus raw GFS MAE. Negative means better than raw
GFS.) On the validation year (F62), winter and autumn (SON) helped; on the
test year, spring and autumn (SON) help — **winter and spring swapped which
one hurts and which one helps**, while summer stayed a small loss in both
years and autumn (SON) — Dubbo's own local spring, the season D39.12's
watch-item named in advance — helped in both, but by much less.

**The single-season watch-item (D39.12), read exactly as it was written down
before the look: the season that carried almost the entire rehearsal win is
where almost the entire shrinkage happened.** F62 measured the correction's
validation-year win as carried overwhelmingly by Northern-labelled autumn
SON, -0.516 degC of the average improvement on 85 days, with the other three
seasons close to flat. On the test year that same season, 84 days, improved
by only -0.138 degC — a swing of **+0.378 degC**, more than two-thirds of
its own prior margin gone. Weighted across the year, that one season's own
shrinkage (roughly a quarter of the year's days, losing 0.378 degC of margin)
is close to sufficient on its own to explain the whole-year margin's fall
from 0.114 degC (8.2%, F62) to 0.041 degC (3.3%, this session) — winter and
spring's sign flips roughly cancel each other (winter +0.060 degC worse,
spring 0.060 degC better) and summer improved slightly (+0.066 to +0.004).
**This is exactly the exposure D39.12 named before anyone knew the result:
a win concentrated in one season is more exposed to that season's own
year-to-year weather than a win spread across all four would be, and here
that is the visible mechanism behind the narrower test margin — a
description, not a licence to re-run or adjust anything (D39.10, D39.11).**

**Feature importances, the sanity check that it used what it was meant to:**

```
feature                 gain  gain share   splits   s22 share  s22 splits
forecast_temp_c        4457.7       45.3%    1,560       47.8%       1,633
season_sin              2987.9       30.3%    1,480       30.2%       1,555
season_cos              2399.9       24.4%    1,160       22.0%       1,012
```

Nothing is ignored and nothing dominates; the shares are close to session
22's inner-training-only figures. Beside the other three sealed tests: EGLC
51.8/24.5/23.7, CDG 38.2/34.9/26.9, DSM 43.4/36.1/20.6. Dubbo's forecast-
temperature share (45.3%) sits between CDG's and DSM's.

**The test number against session 22's rehearsal number — a difference was
expected (D39.5) and it is not a problem.**

```
method                  s22 valid   s24 test  difference
Raw GFS                     1.397      1.251      -0.146
Persistence                 2.577      2.669      +0.092
Climatology                 2.888      3.143      +0.255
Mean-bias reference         1.368      1.238      -0.130
ML-corrected                1.283      1.210      -0.073
days scored                   355        347

margin over raw GFS:  validation +0.114 (8.2%)   test +0.041 (3.3%)
```

Read the raw GFS row first: the test year was genuinely easier for GFS at
Dubbo than the validation year was (1.251 against 1.397), and every method's
raw MAE fell with it except persistence and climatology, which rose slightly.
**The margin fell more than raw GFS's own difficulty would explain on its
own** — which is what the season-by-season table above already shows in
more detail.

**For the record, in-sample MAE on the training window was 1.005 degC
against raw GFS's 1.298 (session 22's inner-training figure was 0.961).** A
model always looks better on the data it was fitted to; that figure proves
nothing and is here only so it is not a surprise later.

**How the recipe travelled, all four sealed tests side by side:**

```
method                      EGLC       CDG       DSM     Dubbo
Raw GFS                    1.242     1.396     1.815     1.251
Persistence                2.096     2.300     4.003     2.669
Climatology                2.972     3.774     5.030     3.143
Mean-bias reference        1.234     1.389     1.760     1.238
ML-corrected               1.040     1.208     1.700     1.210
days scored                  363       363       365       347
training rows fitted       1,569     1,569     1,571     1,553

margin over raw GFS        16.3%     13.5%      6.3%      3.3%
margin over persistence    50.4%     47.5%     57.5%     54.7%
margin over mean-bias ref  15.7%     13.0%      3.4%      2.3%
seasons helped               4/4       3/4       3/4       2/4
day-by-day win rate        60.9%     58.7%     53.4%     52.4%
```

**Every one of the last four rows moves in the same direction across the
four airports in the order they were tested** — narrower margins, fewer
seasons helped, lower day-by-day win rate. Nothing in the recipe orders
airports this way; it is a description of what each airport's own test year
gave, not a trend the project predicted or relied on. Read together with
F63: the recipe travels to a fourth continent, a flipped hemisphere and a
flipped season cycle, and it still passes — but by the thinnest margin yet,
on the airport whose rehearsal was already the most concentrated in one
season of the four (F62).

**Rehearsal margin against test margin, all four airports — Dubbo is the
second airport, after DSM, where the test margin is SMALLER than the
rehearsal margin:**

```
airport            rehearsal margin              test margin
EGLC             +0.074 degC (6.0%)      +0.202 degC (16.3%)
CDG              +0.050 degC (3.5%)      +0.188 degC (13.5%)
DSM              +0.282 degC (16.1%)      +0.115 degC (6.3%)
Dubbo            +0.114 degC (8.2%)       +0.041 degC (3.3%)
```

D39.10 named Dubbo's rehearsal margin (8.2%, between CDG's and DSM's) in
advance and said explicitly that this was not a reason to expect a pass
either way. What happened: the test margin fell, as DSM's did and the two
European airports' did not — two airports rising, two falling, on a sample
of four.

**One data-source fact, confirmed rather than re-run this session (D39.13).**
Every Dubbo forecast chunk was pulled with `models=gfs_global` (D16, F57).
The `gfs_global` versus `gfs_seamless` comparison was run at verify-on-
contact (F52, not deferred) and found the two strings **identical** — unlike
DSM, where they differ by up to 12.3 degC on 259 of 264 hours (F40) because
Des Moines sits inside CONUS. So Dubbo's result is confirmed genuine NCEP GFS
by two independent facts: the D16 pin, and the by-construction equivalence
F52 already measured. This session re-quoted F52 and F40; it did not re-run
either comparison.

**What this session did not do, on purpose.**
- **The script was run once for the result of record, and once more only to
  confirm byte-identical output** — determinism rests on the fixed seed,
  `deterministic=True`, `n_jobs=1`, the pinned versions in `requirements.txt`
  (D24), and this is now confirmed directly rather than only by the pattern
  in F14, F15, F29, F45 and F47's own single run.
- **Nothing was analysed beyond the locked run.** The single-season watch-
  item was described using the figures the run printed. No further pass was
  made over the test year to explain anything further.
- **The deeper evaluation (SPEC 5.4) stays optional and was not opened**
  (D29). The project still has no formal significance figure for any
  airport's win, and at 3.3% on 347 days that limit bites hardest here of
  any airport yet.
- **No SPEC edit was made this session, and none was authorised.** The bar
  was judged as written. SPEC 1, 3.4, 5.0 and 6 still describe Dubbo as
  stage 2 "in progress" and carry no test-year row for it; those are now out
  of date and are flagged for the owner in this session's consistency check
  rather than changed here — the same choice DSM's session 18 made (F47).
- **Nothing was committed.**

---

**F65. What four passes now establish, and what is genuinely new: the
hemisphere/season-cycle axis is answered, and the margin has now shrunk on
three of the last four data points in a row.**

This is written separately, mirroring F48's role after the third pass,
because it is easy to over-claim four passes and because Dubbo's result adds
a specific new piece of information rather than just one more airport.

**1. The hemisphere/season-cycle axis, named untested by F46/F48/D36, is now
answered.** Dubbo is Southern Hemisphere, 14,504–16,683 km from the three
existing airports (F49), with a bias shaped like nothing seen before (F61) —
concentrated in one local season rather than spread across the year, and
phase-shifted into Dubbo's own summer rather than copying a Northern shape.
**The same recipe, unchanged, wins there too**, on the sealed test year and
not only the rehearsal. That is genuinely independent evidence along a third
axis, after DSM answered the region axis (F48).

**2. The year axis is still not answered, and cannot be by this result.**
D13's split dates are shared by every airport, so Dubbo's test year is the
same twelve months EGLC's, CDG's and DSM's were. Four passes on one calendar
year are not four independent draws of weather. F46 and F63 wrote this down
before the look and it stands unchanged.

**3. Dubbo is not the controlled comparison EGLC and CDG make between them,
and it is not even the single-change comparison DSM makes against them.**
Dubbo changes the location **and** the target hour against every earlier
airport (D37, SPEC 4.1, F63). A Dubbo result answers "does the recipe travel
to a fourth continent, a flipped hemisphere and a flipped season cycle, at a
third distinct local-noon hour". It must not be quoted as if only the
location had moved.

**4. The margin has now shrunk from rehearsal to test on two of the four
airports, and Dubbo's test margin is the smallest of any airport yet by a
wide margin — under half of DSM's, which itself was under half of CDG's.**

```
airport   rehearsal margin over raw GFS   test margin over raw GFS
EGLC              +0.074 degC (6.0%)          +0.202 degC (16.3%)
CDG               +0.050 degC (3.5%)          +0.188 degC (13.5%)
DSM               +0.282 degC (16.1%)         +0.115 degC (6.3%)
Dubbo             +0.114 degC (8.2%)          +0.041 degC (3.3%)
```

F48 read DSM's fall as the shared test year being an easier one for GFS in
Europe than elsewhere, which flattered the two European rehearsals-to-test
rises. Dubbo's own fall cannot be read the same way in full: DSM's fall was
broad-based (F47's season table shows winter and spring both stopped
helping), while Dubbo's fall is traceable in large part to one specific
mechanism named in advance — the single season D39.12 flagged shrinking from
carrying almost the whole win to carrying only a modest share of it (F64).
**Two different routes to the same direction of result**, which is itself
informative: it says a concentrated-season win is a genuinely fragile shape,
not a DSM-specific fact about continental interiors.

**5. So the honest summary across all four airports: the method wins on both
years at all four places, by 6.0%, 3.5%, 16.1% and 8.2% on the four
rehearsal years and by 16.3%, 13.5%, 6.3% and 3.3% on the one shared test
year.** The range across eight airport-years is roughly 3% to 16%, the same
range F48 already gave across six — Dubbo's two points sit inside it rather
than widening it, but at its lower edge on the test side. Anyone quoting
16.3% alone is quoting the best of eight, and anyone quoting only test-year
figures is quoting a declining sequence that may or may not continue at a
fifth airport.

**6. The claim that the correction learns structure, not just an offset, is
now at its thinnest anywhere.** The margin over the mean-bias reference —
15.7% at EGLC, 13.0% at CDG, 3.4% at DSM, **2.3% at Dubbo** — has fallen at
every airport since EGLC, with Dubbo the smallest yet. The claim still holds
in the same direction at all four airports, and it held on Dubbo's own
rehearsal by 6.3%. But at Dubbo, more of the win is the constant than
anywhere tested so far, and the amount left over as structure is the
smallest yet measured.

**7. Nothing here re-opens EGLC's, CDG's or DSM's results.** SPEC 5.0 judges
each airport once on its own data. F16, F30 and F47 stand as written; F64
stands beside them, not above or below them.

---

## 2026-08-19 — Session 25 decisions (a fifth airport opens: a mountain-valley airport)

Q30's first branch — more airports, "ramp up difficulty" — is the one the
owner picked, aimed at the first genuinely terrain-affected case. Both
entries below were written before any mountain-airport data was pulled.

**D40. A fifth airport is opened: a broad mountain-valley US airport.**
- **What it is for.** Every airport so far — EGLC, LFPG, DSM, Dubbo — sits at
  low elevation on flat or gently rolling terrain, where GFS's coarse global
  grid is already reliable (raw MAE 1.2-1.8 degC on the four sealed tests).
  This airport is the project's first deliberate attempt at a **hard** case:
  genuinely terrain-affected and high-altitude, where the grid's coarseness
  should matter more and the raw forecast should be measurably worse. The
  question it is opened to ask is whether the correction delivers its
  biggest wins exactly where the raw model is worst - the method's actual
  selling point, not yet tested.
- **US, for pristine data.** As with DSM (D32), the United States is chosen
  so IEM's record quality is not itself a variable - the point is to make
  terrain the only new axis, not data quality alongside it.
- **Broad-valley, not pathological.** The session prompt named the failure
  mode to avoid: a narrow-canyon station (Aspen-style) where the forecast
  grid point describes an essentially different place and any bias becomes
  unlearnable noise rather than a structure the model can find. The two
  candidates it named - Bozeman (Montana) and Reno (Nevada) - were both
  confirmed on contact (F66) rather than picked from a map.
- **This is the "more airports, harder difficulty" branch of Q30.** Stage 3
  (pooling) and a second test year (Q30's other two branches) are **not**
  opened and nothing about either was written or started.
- Everything else is reused unchanged from the four airports already in the
  project, pending verification that this airport's data supports it: the
  two data sources (SPEC 3.1, 3.2), the model string pin (D16), temperature
  only (D17), the split dates (D13), the pairing rule (D14), the
  drop-count-report rule (SPEC 2.2), the minimal three features (D19), the
  model settings (D21.4) and the frozen qualitative bar (SPEC 5.3, D22).
  **One thing is not reused - the target hour. See D41.**

**D41. This airport's target hour is local standard noon - 19:00 UTC - a
fourth distinct target hour.**
- **The problem, familiar from D33 and D37.** Bozeman's standard-time offset
  is UTC-7 (Mountain Standard Time). Local standard noon (12:00) is
  therefore 19:00 UTC - a fourth distinct target hour, after 12:00 (EGLC,
  LFPG), 18:00 (DSM) and 02:00 (Dubbo). This is D33's convention applied a
  third time: hold *local midday* constant across airports, not the UTC
  hour, because a fixed UTC hour is a different time of day at every
  longitude.
- **The decision.** The target is **local standard noon, 19:00 UTC**, with
  daylight saving deliberately ignored so the target stays a fixed UTC hour
  all year, exactly as D33 and D37 do. Montana observes daylight saving
  (MDT, roughly March-November); the **standard** offset (MST, UTC-7) is
  used regardless, per D27's convention and the session prompt's explicit
  instruction.
- **Checked against the timezone database before being trusted, and it
  matches exactly.** See F67. The same discipline F32 applied for DSM and
  F50 for Dubbo: state the expected hour on principle, then confirm it
  against real timezone data rather than assuming from a nominal "Mountain
  Time = UTC-7" guess.
- **The honest consequence, recorded plainly, exactly as D33 and D37
  recorded it.** This airport changes **both** the location and the target
  hour against EGLC and LFPG, so D26's "only the location changed" does not
  hold for it either. Read a result from this airport as: independent
  terrain regime, high altitude, same shared D13 twelve months, two things
  changed from the European pair (location and target hour) - the same
  honest reading D33/F46 give DSM and D37/F63 give Dubbo.
- **Chosen on principle, before any data from this airport was seen**, in
  the same style rule 2.4 requires for the frozen bar.
- **No SPEC edit was made or authorised this session.** SPEC 4.1 already
  states the local-midday principle generally (D34), so adding this airport
  to SPEC 3.4's table, once the full pull confirms the data, is a later
  session's job.

**Expectations, set honestly and in advance (a note, not a decision).** GFS
is expected to be **much worse** at a genuine mountain-valley airport than at
any of the four flat airports tested so far (raw MAE possibly 2-4 degC or
more, against the 1.2-1.8 degC range measured at EGLC/CDG/DSM/Dubbo). A big
correction would be the exciting outcome - the method's biggest win landing
exactly where the raw model is worst. A modest win, or a finding that the
three-feature minimal set (forecast temperature, season) is not enough to
capture terrain-driven bias, is equally informative and may be the airport
that motivates richer features (cloud cover, wind, a terrain-mismatch term)
later. This is a genuine test of the minimal feature set, not just another
confirmation of a recipe that has now passed four times running.

---

## 2026-08-19 — Session 25 findings (airport #5 verified on contact)

This session pulled small samples only. **No full dataset was pulled,
nothing was joined, built, trained or evaluated, and nothing from EGLC, CDG,
DSM or Dubbo was touched or re-run.** Thirty-two raw files went into
`data/raw/`, each with a `.meta.txt` beside it recording the pull time and
the exact request (SPEC 2.3). The scripts are `scripts/session25_pull.py`
and `scripts/session25_checks.py`; the full real output is
`notes/session-25-check-output.txt`, and the pull log is
`notes/session-25-pull-output.txt`. Two consecutive runs of the checks
script produced byte-identical output.

**Q29 fix continued from session 19.** Every sample this session pulls sits
in 2021 (the archive-start probes, shared with every airport) or 2024
(comfortably inside training, nowhere near the test year). Nothing here
touches 2025-08-01 onward.

**F66. The station chosen - Bozeman (BZN) over Reno (RNO) - and the grid
mismatch measured for both before choosing. The key mountain figure turned
out real but SMALL for both candidates, not the "hundreds of metres" the
session prompt flagged as possible.**

Both candidates come from IEM's own metadata, in two DIFFERENT state
networks (unlike Dubbo's two same-network candidates, session 19) - pulled
first so nothing is typed in from memory or a map (D28's rule):

```
IEM's entries, exactly as returned:
       sid   sname               network   elevation   tzname                archive_begin
BZN    BZN   BOZEMAN/GALLATIN    MT_ASOS   1364.0 m    America/Denver        1948-01-01
RNO    RNO   Reno - Tahoe        NV_ASOS   1345.0 m    America/Los_Angeles   1943-01-05
coordinates:  BZN  lat 45.7881, lon -111.1608
              RNO  lat 39.4839, lon -119.7711
METAR_RESET_MINUTE:  BZN = 56    RNO = 55
```

**Neither candidate's IEM code is an ICAO code** (Bozeman's ICAO code is
KBZN, Reno's is KRNO) - the same non-ICAO-station-id situation DSM's `DSM`
already established (F31, Q28, closed by D38's "station code" heading), so
this is consistent with the existing airport table rather than a new
wording problem.

A short 7-day comparison sample (2024-06-01 to 2024-06-08, outside the test
year) was pulled for both, including - new for this session, because the
session prompt's central ask is the elevation mismatch - a forecast sample
for each, so the grid-point elevation could be compared before choosing:

```
        routine METAR      forecast          grid distance   GRID ELEVATION MISMATCH
BZN     168/168 present    192/192 present   6.02 km         grid 1348.0 m vs station 1364.0 m -> -16.0 m
RNO     168/168 present    192/192 present   6.02 km         grid 1344.0 m vs station 1345.0 m -> -1.0 m
```

**Both mismatches are real but small, not the "hundreds of metres" the
session prompt named as possible** - worth recording as a genuine finding,
not smoothed over. The reading: Open-Meteo's roughly 0.25-degree GFS grid
cell, averaged over a genuinely BROAD valley floor at either candidate,
lands close to the valley's own elevation rather than blending in the
nearby peaks - which is close to what "broad, not pathological" should look
like by construction, and is exactly why neither candidate shows the
dramatic mismatch a narrow canyon station (the Aspen case the prompt says to
avoid) would produce. It also means the mean-bias-reference watch item the
session prompt flags for the evaluation session should not be read as "a
large fixed altitude offset is guaranteed here" - that will depend on
temperature structure more than on the grid's raw elevation label.

**Bozeman was chosen on the "broad, not pathological" criterion**, weighing
the two candidates' surrounding terrain rather than the (near-identical)
grid-mismatch numbers, which did not favour one over the other. Bozeman
sits in the Gallatin Valley, a wide agricultural valley many kilometres
across, bounded by the Bridger Range to the north and the Gallatin and
Tobacco Root ranges to the south and west at a comfortable distance - real
mountain-terrain effects (elevation, cold-air drainage, a genuine
winter/summer diurnal range) without the valley narrowing to a canyon. Reno
sits in the Truckee Meadows, but immediately to its west the Sierra Nevada
front rises steeply to peaks above 3,000 m within about 20 km - a sharper,
more abrupt transition right at the edge of the valley than Bozeman's more
gradually-rising surrounding ranges. Both are legitimate choices under the
session prompt's own naming of them; Bozeman is the clearer case of the two
broad-valley candidates.

```
                latitude   longitude   elevation
EGLC            51.5053     0.0553         5 m
LFPG            49.0153     2.5344       109 m
DSM             41.534    -93.6531       294 m
YSDU           -32.2167   148.5747       275 m
BZN             45.7881  -111.1608     1,364 m
BZN is 7,359 km from EGLC, 1,482 km from DSM (the nearest of the four).
```

**BZN is by far the highest-elevation airport in the project so far** -
1,364 m against DSM's 294 m, the next highest - even though the GRID
mismatch specifically (F66 above) is modest. The altitude itself, not the
grid-point offset, is the genuine new variable this airport tests.

**F67. The target hour checked, not assumed: local standard noon here really
is 19:00 UTC.**

D41 fixes the target at local standard noon and says that is 19:00 UTC.
That was checked against the timezone database, using the timezone name
IEM's own metadata gives (`America/Denver`):

```
timezone from IEM metadata     : America/Denver
mid-summer (daylight saving)   : 12:00 UTC = 06:00 MDT (UTC-6)
mid-winter (standard time)     : 12:00 UTC = 05:00 MST (UTC-7)
standard-time offset           : UTC-7  (read from a January date, guaranteed standard time)
so local standard noon (12:00) = 19:00 UTC
D41 expects                    = 19:00 UTC
VERDICT                        : MATCHES
```

The standard offset was read from a January date, the same way F32 read
DSM's January date and F50 read Dubbo's July date - each time from
whichever month is guaranteed to sit outside that hemisphere's
daylight-saving window. Montana does observe daylight saving; D41 (and the
session prompt) use the standard offset regardless, per D27's convention.

**F68. The forecast archive starts here on exactly the same hour as at every
other airport: 2021-03-24 00:00 UTC.**

```
probe 1, 2021-03-01..2021-03-07 : 168 rows, ALL 168 null
probe 2, 2021-03-18..2021-03-26 : 216 rows, 72 with a value, 144 null
                                  first non-null = 2021-03-24T00:00
                                  value range -2.7 to 7.9 degC

recent sample 2024-06-01..2024-06-21 : 504 rows, 504 with a value, 0 null
                                       value range 1.4 to 29.2 degC
```

This is the fifth location, on a fifth kind of terrain, to give the same
answer down to the hour - including the detail that the API answers HTTP
200 with all-null values before its archive begins rather than returning an
error (F1, F20, F33, F51). **The practical consequence: the D13 split dates
carry over here unchanged.** Training 2021-03-24 to 2025-07-31 and testing
2025-08-01 to 2026-07-31 are as available at this airport as at the other
four. The first airport with real terrain complexity gives the same archive
floor as four flat ones did.

**F69. `gfs_global` and `gfs_seamless` DIFFER here, more sharply than at
DSM - the check the session prompt asked for, and it matters exactly as
much as expected at a CONUS mountain point.**

```
window 2021-03-24..2021-04-05 (early, inside training)    : 312 hours compared, 0 differ
                                                              (grid points differ, values do not)
window 2024-08-05..2024-08-15 (out-of-test-year, Q29 fix)  : 264 hours compared, 258 differ
                                                              largest difference: 16.5 degC
same grid point in either case : NO (gfs_global and gfs_seamless report
                                      different grid points throughout, unlike
                                      at Dubbo where they coincided, F52)
```

**This is the same shape F40 found at DSM - identical on old data, sharply
different on recent data - but the recent-data difference is bigger here:
16.5 degC against DSM's 12.3 degC (F40), on almost the same share of hours
(258 of 264, 97.7%, against DSM's 259 of 264, 98.1%).** The reading is the
same as F40's: `gfs_seamless` blends in a higher-resolution CONUS-only NCEP
model (HRRR, NAM or NBM) where `gfs_global` does not, and a high-resolution
model should differ from coarse global GFS *most* exactly where terrain is
complex - which is this airport's whole reason for existing. **Every chunk
pulled at this airport uses `gfs_global` regardless (D16), so nothing in
the project depends on this result either way, but D16's pin is doing real
work again here, in exactly the place it matters most so far.**

**F70. This station reports 4 minutes before the hour (`:56`) - so the D14
pairing rule applies as written at the 19:00 UTC target, with a small
4-minute offset, and loses no target-hour day in either sample.**

```
recent sample 2024-06-01..2024-06-22 : 503 reports, minute-past-hour :56 x503
early  sample 2021-03-18..2021-04-01 : 333 reports, minute-past-hour :56 x333
distance from the nearest hour        : 4 min on every report in both samples
within D14's 15-minute window         : 503 of 503, and 333 of 333
outside it, so D14 drops them         : 0, and 0
```

IEM's own station metadata agrees: this station's `METAR_RESET_MINUTE`
attribute is `56` (F66). **Does D14 need adapting? No.** The report at
`(H-1):56` serves hour `H` - the same shape DSM's `:54` reporting takes
(F34), a smaller offset even than DSM's 6 minutes. What D14 would keep at
this airport's own target hour, observation side only:

```
recent sample 2024-06-01..2024-06-22  21 calendar days, 21 kept, 0 dropped
early  sample 2021-03-18..2021-04-01  14 calendar days, 14 kept, 0 dropped
pairing offset on every kept day      : 4 minutes, min and max alike
e.g. 2024-06-01 -> report 18:56 UTC, 20.0 degC
     2021-03-18 -> report 18:56 UTC, 13.89 degC
```

**Not one report in either sample falls outside D14's tolerance, and every
day is kept** - the same clean shape DSM showed (F34) and unlike Dubbo's
messier record (F58, F59). On this evidence D14 needs no adapting here.

**Gap counts, nothing filled (SPEC 2.2).** A `:56`-reporting station needs
the same "which hour does this report serve" accounting DSM's `:54`
reporting needed (F34, Q26): the report stamped `(H-1):56` serves hour `H`,
so a plain on-the-hour gap count would misread every hour as missing. With
that accounting applied:

```
recent sample : 504 hours expected, 502 covered, 2 missing
                (1 is a request-boundary artefact - the window's first hour,
                2024-06-01 00:00, needs a report from 2024-05-31 23:56, not
                requested, the same artefact Q26 named for DSM; the other,
                2024-06-13 20:00, is a genuine gap)
early  sample : 336 hours expected, 332 covered, 4 missing
                (1 boundary artefact, 2021-03-18 00:00; 3 genuine gaps -
                2021-03-20 07:00, 2021-03-22 08:00, 2021-03-30 05:00)
reports with no temperature : 0 in both samples
```

Neither the target hour (19:00 UTC) nor any of the genuine gaps falls on
it in either sample, which is why F70's target-hour count above shows 0
dropped despite these observation-side gaps existing elsewhere in the day.

**F71. Both non-European-airport risks - whether `tmpc` needs new units
handling, and whether the `tz=UTC` request really is UTC - were measured
here too, and both need no new handling, in the same shape DSM showed.**

**Units.** US METARs are written in whole-degree Fahrenheit, so a small
Celsius/Fahrenheit-derived rounding gap is expected, the same pattern DSM's
F35 found:

```
file : iem_asos_BZN_2024-06-01_2024-06-04_routine-tmpc-tmpf.csv   72 rows

valid (UTC)        tmpc     tmpf   (tmpf-32)*5/9   difference
2024-06-01 00:56   18.89    66.00          18.89       +0.001
2024-06-01 01:56   16.67    62.00          16.67       +0.003
2024-06-01 02:56   16.11    61.00          16.11       -0.001

largest disagreement across all 72 rows : 0.004444 degC
tmpc range in this sample               : 1.67 to 22.78 degC
```

`tmpc` is degrees Celsius here, the same field and the same units every
other airport uses (compare DSM's largest disagreement of 0.0044 degC, F35 -
essentially the same size gap).

**Timezone.** Every IEM request in this project sends `tz=UTC`. The same
window was pulled a second time with `tz=America/Denver`; June sits inside
Mountain Daylight Time (MDT, UTC-6), not the standard offset (MST, UTC-7)
used for the target hour - this check measures whichever offset is actually
in force during the sample, exactly as F35's DSM check landed inside
daylight saving too:

```
shift (hours)   rows compared   temperatures equal
        +3              69              5  (7.2%)
        +4              68              5  (7.4%)
        +5              67              9  (13.4%)
        +6              66             66  (100.0%)
        +7              65              9  (13.8%)
        +8              64              5  (7.8%)
        +9              63              5  (7.9%)
       +10              62              4  (6.5%)
```

A single clean 100% at +6 hours, and early June is exactly when
`America/Denver` is on daylight saving at UTC-6. So the `tz=UTC` request
really is UTC. Open-Meteo labels its own side of the join `timezone=GMT`,
`utc_offset_seconds=0`, so both series are stamped in UTC and neither needs
shifting.

**F72. The "special" (SPECI) report stream is genuinely unscheduled here -
like DSM, unlike EGLC, LFPG and Dubbo.**

```
recent window 2024-06-01..2024-06-22, 21 days (504 hours)
  routine rows           : 503
  routine + special rows : 561
  special-only rows      : 58
  distinct minutes used  : 30
  busiest minutes        : :21 x6, :09 x4, :23 x3, :32 x3, :43 x3, :37 x3
  most-common minute share: 10.3% of all special-only rows
```

At EGLC, LFPG and Dubbo the "special" stream turned out to be a second
SCHEDULED report (F3, F19, F55); at DSM it was genuinely unscheduled,
spread across 38 minutes with none used more than four times in three
weeks (F36). Here, 58 special-only reports spread across 30 different
minutes with the busiest carrying only 10.3% of them - the same
weather-driven shape DSM shows, not a scheduled second report. **Recorded,
not acted on.** This airport reuses the routine report as the truth
observation, exactly as D30 already settled for the other four; there is no
fallback stream to consider using instead.

**F73. Plain first read - yes, this airport is usable for the recipe the
same way the other four were, and the mountain-specific check the session
was opened to make (the elevation mismatch) is now measured rather than
assumed.** Every verify-on-contact check passed:

- the Previous Runs API carries the location, with a grid point 6.02 km
  away and a real but modest -16 m elevation mismatch - smaller than the
  session prompt flagged as possible, and explained by the grid cell
  averaging over a genuinely broad valley floor (F66);
- the archive reaches back to the same 2021-03-24 00:00 UTC start hour, so
  the fixed D13 split dates need no change (F68);
- `gfs_global` and `gfs_seamless` DIFFER here, more sharply than at DSM
  (16.5 degC against 12.3 degC on the largest single difference) - the
  clearest evidence yet that D16's pin matters, at exactly the airport
  where terrain makes a high-resolution blended model diverge most from
  coarse global GFS (F69);
- IEM carries the station in `MT_ASOS` with a clean observation record - 2
  of 504 hours missing in the recent sample, 4 of 336 in the early sample,
  each including one request-boundary artefact and the rest genuine short
  gaps, comparable in cleanliness to DSM's record (F70);
- the pairing rule needs no adapting: this station reports 4 minutes before
  the hour, comfortably inside D14's tolerance, losing zero target-hour
  days in both samples (F70);
- the units and the timezone need no new handling, in the same shape DSM
  required (F71);
- and the one genuinely airport-specific choice, the target hour, was made
  on principle before any data was seen (D41) and then confirmed against
  the timezone database (F67).

**A rough, informal sense of the raw forecast error, from the
out-of-test-year sample only - not a test-year figure and not part of any
pipeline.** Pairing the 21-day recent forecast sample against the paired
19:00 UTC observations under D14 gives a rough MAE of **1.233 degC** over 21
days (min error 0.02, max error 5.36 degC) - inside the 1.2-1.8 degC range
the four flat airports' *sealed test years* measured (SPEC 5.0), not
obviously the "2-4 degC+" the session prompt flagged as a plausible
mountain-airport outcome. **This is not evidence the terrain hypothesis is
wrong.** Three weeks of June is a small, single-season sample - mountain
cold-air-drainage and inversion effects that drive large raw-GFS bias are
typically a winter, clear-night phenomenon (the F44/F45 warm-end story at
DSM was itself a summer-forecast effect measured only once the whole year
was joined), and a 21-day summer window cannot see that. The honest
statement is: this sample does not by itself confirm GFS is badly behaved
here, and the real test is the full year once pulled and joined - which is
exactly why the session prompt asks for "a rough sense only" rather than a
conclusion.

**Nothing found here justifies changing any earlier decision at EGLC, CDG,
DSM or Dubbo.** The one thing that is not reused - the target hour - was
decided in advance and its cost to D26's "only the location changed" claim
is written into D41 rather than glossed over, exactly as D33 and D37 did.

**No new open question is raised this session.** SPEC's per-airport wording
(D34) already covers a fourth distinct target hour without a fresh
conflict, the way it was built to; the small grid-elevation mismatch (F66)
is a genuine, honestly-reported finding rather than a blocker; and every
other check followed the same shape session 19 already established for a
non-European, non-ICAO-code airport.

---

## 2026-08-19 — Session 26 (corrected) decision (Task 0): the fifth airport
switches from Bozeman to Reno

A previous version of the session 26 prompt jumped straight to Reno without
recording the switch, and the files-vs-prompt disagreement was correctly
caught and stopped on. This corrected session records the switch first, as a
new dated decision, before doing anything else.

**D42. The fifth airport is switched from Bozeman (BZN) to Reno (RNO). This
supersedes D40; D40 itself is left exactly as written, per the append-only
rule.**

- **What D40 recorded.** Session 25 (D40) opened a fifth airport and chose
  Bozeman, Montana, after verifying two candidates (Bozeman and Reno) on
  contact and comparing their grid-elevation mismatches (F66). D40 stands as
  the honest record of that choice, made at that moment, from the
  information available then. It is not edited or retracted.
- **What changed, and when.** After reviewing session 25's results, the
  owner switched the choice to Reno. That switch was made in discussion and
  had not yet been written into DECISIONS or STATUS before this session —
  the record said Bozeman while the intended work was Reno. This entry is
  that missing write-down, made before any further work proceeds on the
  fifth airport.
- **Why the switch.** The fifth airport's job (D40) is a genuine
  *terrain-hard* test: does the correction deliver its biggest wins exactly
  where raw GFS is worst. Bozeman's own numbers turned out to argue against
  it being that test:
  - Bozeman's grid-elevation mismatch is only **-16 m** (F66), and it sits in
    a **wide, grid-resolved valley** — the ~0.25-degree GFS grid cell,
    averaged over the valley floor, lands close to the valley's own
    elevation rather than blending in nearby peaks. Raw GFS should therefore
    handle it about as well as it handles a flat airport: Bozeman is
    "high-altitude flat", not a terrain test, even though its altitude
    (1,364 m) is real and by far the highest in the project.
  - **Reno sits in a valley against the steep Sierra Nevada front** —
    immediately to its west the terrain rises very steeply to peaks above
    3,000 m within about 20 km (F66's own comparison). Its difficulty is
    expected to be **horizontal terrain complexity** (foehn / downslope
    warming, cold-air drainage off a nearby steep escarpment), which the
    small **vertical** grid-elevation mismatch (**-1 m**, smaller even than
    Bozeman's) does not capture and cannot rule out. A small elevation
    mismatch does not mean an easy forecast when the difficulty is
    horizontal rather than vertical.
  - **Reno's true difficulty is only knowable by running it** — exactly the
    same honest limit D40 already stated about both candidates before either
    was pulled in full. The switch is a bet that the harder physical setting
    (proximity to a steep mountain front) is more likely to produce the
    terrain-hard test D40 was opened to find than the wide, evenly-resolved
    valley Bozeman turned out to be.
- **What is set aside, not discarded.** Bozeman is set aside as the fifth
  airport. Its verification (F66–F73) remains on record in full and could be
  revisited later — as a sixth airport, or otherwise — if the owner ever
  wants it; nothing about it was wrong, and D40's reasoning for choosing it
  at the time (the clearer "broad, not pathological" case of the two) still
  stands as an honest account of that comparison. It is simply no longer the
  airport this session's pull and gap-map target.
- **Everything else carried over unchanged from D40, now pointed at Reno.**
  US, for pristine IEM data quality (as D32 chose for DSM). Broad-valley,
  not pathological (the Aspen-style narrow-canyon failure mode D40 named to
  avoid — Reno's own metadata, F66, shows it hourly-and-complete like
  Bozoman, so this is not that failure mode either). Everything else reused
  unchanged from the four airports already in the project, pending
  verification: the two data sources (SPEC 3.1, 3.2), the model string pin
  (D16), temperature only (D17), the split dates (D13), the pairing rule
  (D14), the drop-count-report rule (SPEC 2.2), the minimal three features
  (D19), the model settings (D21.4) and the frozen qualitative bar (SPEC
  5.3, D22). **One thing is not reused — the target hour. See below.**

**Reno's target hour: 20:00 UTC, not Bozeman's 19:00 UTC — confirmed against
the timezone database in this session's own checks script, not inherited.**

D41 computed 19:00 UTC for *Bozeman* (Mountain Standard Time, UTC-7). Reno is
**Pacific** (`America/Los_Angeles`), one hour further west. This session's
`scripts/session26_checks.py` computes the standard-time offset directly from
a January date (guaranteed outside daylight saving) rather than assuming the
nominal "Pacific = UTC-8" figure carries over uninspected:

```
timezone from IEM metadata     : America/Los_Angeles
mid-summer (daylight saving)   : 12:00 UTC = 05:00 PDT (UTC-7)
mid-winter (standard time)     : 12:00 UTC = 04:00 PST (UTC-8)
standard-time offset           : UTC-8
so local standard noon (12:00) = 20:00 UTC
VERDICT                        : MATCHES the session prompt's expectation
```

This is the same discipline F32 (DSM), F50 (Dubbo) and session 25's own PART
0c (Bozeman) applied: state the expected hour on principle, then confirm it
against real timezone data. **20:00 UTC is Reno's target hour** — the fourth
distinct target hour among the airports SPEC now tracks, after 12:00 (EGLC,
LFPG), 18:00 (DSM) and 02:00 (Dubbo). Counting Bozeman's own brief
candidacy, it is the **fifth** distinct target-hour value computed anywhere
in the project's history: D41 computed 19:00 UTC for Bozeman before this
session's switch set that airport aside (D41's own text also called 19:00
"a fourth distinct target hour", counting the same way at the time — before
Reno's 20:00 existed to make either count stale). Daylight saving is
deliberately ignored (D27's convention, applied a fifth time counting
Bozeman, a fourth among airports SPEC tracks), so the target stays one fixed
UTC hour all year; Nevada does observe daylight saving (PDT, roughly
March–November), and the standard offset (PST, UTC-8) is used regardless.

**The honest consequence, recorded plainly, exactly as D33/D37/D41 recorded
it for the three earlier non-European airports.** Reno changes **both** the
location and the target hour against EGLC and LFPG, so D26's "only the
location changed" claim does not hold for it. Read a result from Reno as:
independent terrain regime (this time genuinely terrain-complex, per the
reasoning above), same shared D13 twelve months, two things changed from the
European pair — the same honest reading D33/F46 give DSM, D37/F63 give
Dubbo, and D41 gave Bozeman.

**No SPEC edit is made by this decision itself.** The SPEC edits authorised
for this session (A-1 to A-4) are recorded separately below, as their own
decision entry, mirroring how session 20's D38 kept its SPEC-housekeeping
edits in one entry distinct from the substantive per-airport decisions
around it.

---

## 2026-08-19 — Session 26 decision: SPEC housekeeping (Dubbo's pass
recorded, Reno added to SPEC, mirroring D38's shape)

**D43. SPEC is brought up to date with two facts that were already true and
had not yet been written down (Dubbo's pass), plus one new airport row
(Reno, in progress).** This entry documents the four authorised edits (A-1
to A-4, the session 26 prompt) and no others, made in Part A, before Part
B/C's pull and gap map ran — mirroring session 20's D38 approach of doing
the careful documentation edits before the mechanical pull, and session 15's
approach of writing a marker for the one fact (the 492-hour gap) that could
not honestly be filled in until the pull was mapped, then filling it in once
it was.

- **A-1 (§1, §3.4 first table, §5.0, §6).** Dubbo's sealed test ran in
  session 24 and passed (DECISIONS F64: corrected 1.210 vs raw GFS 1.251 vs
  persistence 2.669, 347 scored test days) but SPEC had not yet been updated
  to say so — an oversight carried forward from session 24's own "no SPEC
  edit was authorised" note. Updated: §1's Dubbo bullet to **passed**;
  §3.4's YSDU stage cell from `2 — in progress` to `2 — passed`; §5.0's
  results table gained a YSDU row (`PASSED (stage 2, 347 test days) | 1.210
  vs 1.251 vs 2.669`) and its paragraph beneath now names Dubbo's figures,
  the fact that all four passed airports' single looks are spent on the
  same twelve months (F65's extension of F30/F48's reading), and that
  Dubbo — like DSM — changed its target hour against the European pair;
  §6's Dubbo bullet changed from "IN PROGRESS" to "PASSED", citing its full
  chain of findings (F49–F56, F57–F59, F60–F63, D39, F64), mirroring how the
  DSM bullet already reads.
- **A-2 (§3.4 airport table, both sub-tables).** A RNO row was added to
  each table, using session 25's own recorded figures (F66) rather than the
  session prompt's summary of them: station code `RNO`, stage `2 — in
  progress`, target hour `20:00` (confirmed above), network `NV_ASOS`,
  position lat 39.4839 / lon -119.7711 / elevation 1345 m, grid point lat
  39.537918 / lon -119.765625 / elevation 1344 m, grid distance 6.02 km,
  height mismatch -1 m, reports at `:55`, pairing offset 5 minutes. **The
  "also files at" cell reads "not yet checked"** rather than a guessed
  value — session 25's checks did not run a routine-plus-special sample for
  Reno the way it did for Bozeman (F72), so whether Reno files a second
  scheduled report is genuinely unknown, not merely unrecorded, and D28's
  rule (never write the table from memory or assumption) means the honest
  entry is "not yet checked", flagged as an open item (Q31, below) rather
  than silently left blank or copied from Bozeman's or DSM's answer.
- **A-3 (§1 airport list).** A Reno bullet was added: "Reno, Nevada (IEM
  station code RNO, ICAO code KRNO) — stage 2, in progress. The project's
  first mountain/terrain-affected airport." The parenthetical follows the
  DSM precedent (IEM station code, not ICAO, since `RNO` is not an ICAO
  code — Reno's ICAO code is `KRNO`, per F66).
- **A-4 (§3.2, §3.3).** §3.2's forecast-gap paragraph and archive-floor
  paragraph now name Reno alongside the four other airports, with the
  verified answer this session's Part C actually measured (F75: same 492-
  hour window, same start, same end, same length) rather than a "to be
  verified" marker — mirroring session 15's two-step approach (D34's own
  note #1): the marker was the working state during Part A, and it was
  replaced with the measured fact once Part C's gap map ran later in this
  same session, so SPEC never asserts something this session had not yet
  checked. §3.3's verify-on-contact paragraph now lists Dubbo alongside the
  other three fully-checked airports (an oversight-fix — Dubbo's own F49–F56
  checks were never added to this list when they were made) and adds a new
  paragraph stating plainly that Reno's own verify-on-contact was partial
  and happened across two sessions (25's candidate-comparison depth, 26's
  full-pull depth), rather than letting the existing wording imply Reno
  received the same checklist Bozeman did.
- **One additional wording correction inside A-4's authorised section,
  flagged rather than silently taken further than needed.** The gap
  paragraph's continent count ("four different continents" for EGLC, CDG,
  DSM and Dubbo) does not hold up under inspection — EGLC and CDG are both
  in Europe, so four airports span three continents, not four. Adding Reno
  (also North America, alongside DSM) would have compounded a new
  inaccuracy rather than merely extended an old one, so the phrase was
  changed to name the continents directly ("across Europe, North America
  and Australia") instead of counting them. This is a wording-accuracy fix
  inside the section A-4 already authorises editing, in the same spirit as
  session 21's SPEC 3.2 correction; it changes no rule, date, setting or
  bar. Flagged here and in this session's consistency check rather than
  left for the owner to discover.

**What did not change.** Sections 5.1 (the metric), 5.2 (which references
decide the bar) and 5.3 (the qualitative bar itself, D22) are untouched. No
edit here adds anything a result must clear or removes anything it already
had to. The frozen bar's *meaning* is exactly what it was before this
session — checked edit by edit, the same discipline sessions 09, 15 and 20
applied to their own SPEC edits.

**Why this is a decision entry and not just a finding.** Sessions 09 (D28),
15 (D34) and 20 (D38) established the pattern: bringing SPEC into line with
facts already established elsewhere in the log, or adding a new airport's
row from real pulls, is itself the kind of change this project tracks as a
decision, because it is edited under authorisation rather than discovered by
measurement. D43 is that same kind of entry for session 26.

---

## 2026-08-19 — Session 26 findings (Reno verified against the timezone
database, and the full pull and gap map)

Part B pulled Reno's full history for both sources, 2021-03-24 to
2026-07-31, mirroring session 03b (EGLC), session 10 (LFPG), session 15
(DSM) and session 20 (Dubbo) file for file. Part C mapped every hour. **No
data was joined, built, trained or evaluated, and Reno's test year was
touched only structurally** — row presence, gap positions, report timing —
never a temperature value. The scripts are `scripts/session26_pull.py` and
`scripts/session26_checks.py`; the full real output is
`notes/session-26-check-output.txt`, and the pull log is
`notes/session-26-pull-output.txt`. Two consecutive runs of the checks
script produced byte-identical output (confirmed by diff). No retry fired on
the pull and no rate limit was hit; every chunk was written on the first
attempt.

**F74. Reno's target hour, 20:00 UTC, confirmed against the timezone
database — not inherited from Bozeman's 19:00 UTC.** Recorded in full inside
D42 above, since the confirmation is what D42's target-hour claim rests on;
summarised here for the finding sequence: `America/Los_Angeles`'s standard
(non-daylight-saving) offset, read from a January date, is UTC-8, so local
standard noon is 20:00 UTC, matching the session prompt's expectation
exactly. This is the fourth distinct target hour among the airports SPEC
tracks (12:00, 18:00, 02:00, now 20:00) — the fifth counting Bozeman's
19:00 UTC (D41), which was set aside before entering SPEC.

**F75. Reno's forecast series has EXACTLY the same 492-hour gap as EGLC,
LFPG, DSM and Dubbo, down to the hour. It is one gap and there are no
others, and the archive floor matches too.**

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
    matches the EGLC/LFPG/DSM/Dubbo gap : YES - same start, same end, same length
```

Five airports on three continents (Europe: EGLC, LFPG; North America: DSM,
Reno; Australia: Dubbo) now share this gap hour for hour, which is as close
to proof as this project can get that it belongs to the Open-Meteo archive
itself, not to any place. The grid point returned across all six chunks is
lat 39.537918, lon -119.765625, elevation 1344.0 m — the **exact same
figures** session 25's candidate sample (B0) got for Reno (F66), so the full
pull describes the same place the earlier sample did (`same grid point:
yes`, checked programmatically, not just eyeballed).

Reno's target hour (20:00 UTC) falls **after** the gap's last missing hour
(11:00 UTC), the same as EGLC (12:00), LFPG (12:00) and DSM (18:00) and
unlike Dubbo (02:00, which falls before it). So 2024-01-19 already carries a
value at Reno's target and survives — the gap is expected to cost **20 days
at the target hour, 2023-12-30 through 2024-01-18**, not 21 the way it did
at Dubbo (F59). Confirmed directly below (F77): exactly 20.

**Training-window value ranges, both series, checked and sane, both in
Celsius. The test window's values were not looked at.**

```
forecast (GFS, training window) : n = 37,692   min = -11.9   max = 40.2   mean = 14.18 degC
observed (RNO, training window) : n = 38,085   min = -15.0   max = 41.11  mean = 13.50 degC
```

Kelvin would read about 250–310, so neither series has a unit problem.
**Reno's training-window range does not look obviously wider or harder than
the four flat airports' own ranges** — its coldest forecast (-11.9) sits
between LFPG's (-8.5, F26) and DSM's (-30.0, F38), and its warmest (40.2) is
unremarkable beside EGLC's 40.7 (F10) and Dubbo's 40.9 (F57). This is a
purely structural, all-24-hours observation on the training window, exactly
the kind F13 warns not to over-read as a statement about one target hour —
whatever terrain-driven structure exists at Reno's 20:00 UTC target
specifically is a question for the join session, not this one. It is
recorded here because the session prompt asked for it as a structural
sanity check, not because it settles anything about the terrain hypothesis
D42 rests on.

**Q30's other branches remain untouched.** Nothing about stage 3 (pooling)
or a second test year was opened or acted on this session.

**F76. Reno's observation record is clean — the second-cleanest of the five
airports after DSM — and the request-boundary artefact its `:55` reporting
predicts is real, small and fully accounted for, the same shape DSM's `:54`
reporting produced (Q26, F39).**

```
reports in files           : 46,836
minute-past-hour spread    : :48 x1, :52 x2, :53 x2, :55 x46,831
reports with no temperature: 1   (2021-11-26 08:55 UTC)
reports >15 min from any hour, dropped (D14): 0
expected hours in period   : 46,944
hours with an observation  : 46,834
hours missing              : 110 (0.23% of the period)

training 2021-03-24..2025-07-31: 38,184 expected, 38,085 usable, 99 missing (0.26%)
test     2025-08-01..2026-07-31:  8,760 expected,  8,749 usable, 11 missing (0.13%)

gap runs (whole period): 26 in total
    1 hour        17 runs      17 hours
    2-5 hours       6 runs      15 hours
    6-23 hours      2 runs      19 hours
    1-7 days        1 run       59 hours
longest: 59 hours  2021-05-02 06:00 -> 2021-05-04 16:00 UTC
```

Against the other four airports: EGLC 44 (0.09%, F9), LFPG 140 (0.30%,
F23), DSM 11 (0.02%, F39), Dubbo 477 (1.02%, F58 — the real, non-off-hour
gaps only). **Reno's 110 missing hours (0.23%) sit between LFPG's and
Dubbo's**, closer to LFPG's, with no run anywhere near Dubbo's 42/37/19-hour
outages. **Zero off-hour reports across the whole five-year record** — no
routine report anywhere in the period sits more than 15 minutes from a whole
hour, so D14's tolerance rejects nothing at Reno, the same clean shape DSM
showed (F39: 3 off-hour reports total) and unlike LFPG (97, F23) or
especially Dubbo (235, F58). Nothing was filled (SPEC 2.2); the one report
carrying no temperature was counted, not filled.

**The `:55`-report boundary artefact, checked chunk by chunk rather than
assumed.** Reno reports 5 minutes before the hour (`:55`), the same shape
DSM's `:54` reporting and Bozeman's `:56` reporting both take (F34, session
25), so the report serving hour `H` is stamped `(H-1):55` — outside the
request window that covers hour `H`, at the very first hour of every chunk
after the first. Checked directly: at every chunk boundary from 2022 onward,
the first hour of that chunk is genuinely uncovered by that chunk's own
file, exactly as `:55` reporting predicts (`CONFIRMED` in the script's own
boundary check). Unlike Dubbo, whose on-the-hour reporting meant this
artefact did **not** apply (session 20 checked and found it absent), Reno's
artefact is real but small: it touches no target hour, because 20:00 UTC is
served by the 19:55 report of the *same* day, inside the *same* chunk — the
boundary only ever bites the whole-period midnight-hour count, which is
already folded into the 110-hour total above via the ordinary gap map (the
artefact hours are indistinguishable from genuine gaps in that count, and
are not separately subtracted, matching how F39 and F58 reported DSM's and
Dubbo's own equivalents).

**Units.** Session 25's B5 check already confirmed `tmpc` at this station
(on the candidate sample) agrees with the Fahrenheit-derived figure to about
0.004 degC, the same rounding-only gap DSM's F35 found — not re-run this
session, since the field and the pipeline are unchanged and the check
already exists on record for this exact station.

**F77. Days lost at Reno's 20:00 UTC target, both sides, written down before
any join — the numbers the next session's join must reconcile against,
mirroring session 10/15/20's gap maps for CDG/DSM/Dubbo.**

```
                                       days    expected rows   dropped (fc / obs)
inner-training 2021-03-24..2024-07-31  1,226           1,203        23 / 20 fc, 3 obs
validation      2024-08-01..2025-07-31   365             365         0 / 0
test            2025-08-01..2026-07-31   365             365         0 / 0
whole period                           1,956           1,933        23 / 0 overlap
```

**Observation side: 3 days lost of 1,956 (0.15%), all training, all to "no
report near the hour" — zero to off-hour reports, matching the zero off-hour
rate F76 found.**

```
2021-05-02  [training]  no routine report near the 20:00 hour
2021-05-03  [training]  no routine report near the 20:00 hour
2024-03-21  [training]  no routine report near the 20:00 hour
```

This is the cleanest observation-side result at the target hour of any
airport except DSM's zero (F41) — cleaner than EGLC's, LFPG's three
off-hour losses (F25) and far cleaner than Dubbo's 26 (F59). **Reno loses no
day at all to an off-hour report at the target hour**, which follows
directly from F76's whole-record zero.

**Forecast side: 20 days lost, all inside the shared 492-hour gap, all
consecutive, all in inner-training** — 2023-12-30 through 2024-01-18, exactly
as F75 predicted from the target hour falling after the gap's last missing
hour (11:00 UTC). The same count DSM (F41) and the two European airports
(F12, F27/D31.7) lost from the identical gap; Dubbo alone lost 21 because its
02:00 target falls before 11:00 (F59).

**Expected paired rows for the eventual join: 1,933 of 1,956 calendar days
(98.8%).** Against the other four airports: EGLC and LFPG each about 1,933
(98.8%, F12, F27/D31.7), DSM 1,936 (99.0%, F42), Dubbo 1,909 (97.6%, F60).
**Reno sits essentially level with EGLC and LFPG**, well ahead of Dubbo and
just behind DSM's cleanest-yet record — all five losing the same ~20-day
shared forecast gap, with the small remaining gap between them coming
entirely from each airport's own observation-side rate, not from anything
forecast-side.

**Nothing was filled and nothing was joined this session (SPEC 2.2); these
counts are what the next session's join must reconcile against**, the way
session 11/16/22 reconciled CDG's/DSM's/Dubbo's joins against their own
session's gap map.

**Plain first read — yes, Reno is usable for the recipe the same way the
other four airports were**, and its record is genuinely cleaner than
session 25's Bozeman-focused checks might have suggested was typical of a
mountain station: no off-hour reports at all in five years, a request-
boundary artefact that behaves exactly as `:55` reporting predicts, and a
gap map that matches the shared archive gap precisely. Nothing found here
justifies changing any earlier decision at EGLC, CDG, DSM or Dubbo, and
nothing found here changes D14, D30, or how the pairing rule is applied —
the same rule is used at every airport (SPEC 4.5, D30). **Whether Reno's
raw-GFS error at 20:00 UTC is actually large — the whole point D42 opened
this airport to test — is not answered by anything in this session.** That
question needs the join, which is deliberately not done here (session 26
scope).

---

## 2026-08-19 — Open question raised by session 26 (not acted on)

**Q31. Does Reno file a second scheduled report, the way EGLC, LFPG and
Dubbo do (at `:20`/`:30`/`:30`) rather than the way DSM and Bozeman do
(genuinely unscheduled)?** SPEC 3.4's "also files at" cell for RNO reads
"not yet checked" (D43/A-2) rather than a guessed value, because no session
has pulled a routine-plus-special sample for Reno the way session 25's B4
did for Bozeman (F72) or session 19's equivalent did for Dubbo (F55).
Nothing in the project's pipeline uses the "special" stream as the truth
observation at any airport (D30), so this is a bookkeeping gap rather than a
data one — the same shape Q28 was before D38 closed it for DSM. A short
routine-plus-special sample, pulled from outside the test year (the Q29
fix), would answer it in one request; not done here because it was outside
this session's authorised scope (A-1 to A-4 plus Parts B/C).

---

## 2026-08-20 — Session 27 findings (the Reno join, bias look and validation
rehearsal)

The first modelling session for the fifth airport, Reno. It mirrors session 22
at Dubbo, which mirrored session 16 at DSM, session 11 at CDG and sessions
04/05 at EGLC. **Reno's test year was not touched**: the 2026 RNO raw chunk
file was never opened, the 2025 chunk was cut off at 2025-07-31 on load, and
the script asserts that no date on or after 2025-08-01 reached any table.
Nothing was tuned, varied or chosen again — the locked recipe (D21, restated
per airport as D31/D35/D39) was applied at the fifth location and nothing
else. The script is `scripts/session27_model.py` and the full real output is
`notes/session-27-check-output.txt`. PART 0 proves against
`scripts/session05_model.py` that 0 model settings differ and exactly 1
constant differs (TARGET_HOUR, 12 to 20), which is D42 and nothing else. Two
consecutive fits on the fitted data produced byte-identical predictions.

**F78. The join at 20:00 UTC at Reno, and every drop reconciled EXACTLY
against session 26's gap map (F75, F77) — nothing surprised, nothing stopped.**

One row per day: date, forecast temperature, observed temperature, and the
residual the model learns.

```
                                         days   kept   drop  no fc  null fc  no obs
inner-training 2021-03-24..2024-07-31   1,226  1,203     23      0       20        3
validation     2024-08-01..2025-07-31     365    365      0      0        0        0
```

```
cause                                             expected   actual  verdict
the 492-hour forecast gap (F75, F77)                    20       20  MATCHES
observation-side losses, inner-training (F77)            3        3  MATCHES
observation-side losses, validation (F77)                 0        0  MATCHES
TOTAL days dropped                                      23       23  MATCHES

inner-training paired rows (F77)                      1,203    1,203  MATCHES
validation paired rows (F77)                            365      365  MATCHES
```

**The forecast-gap loss is 20 days, matching EGLC/LFPG/DSM and NOT Dubbo's
21** — Reno's 20:00 UTC target falls after the gap's last missing hour
(2024-01-19 11:00 UTC), the same shape as the three airports whose target
falls after it, so 2024-01-19 survives.

**The observation side is the cleanest pairing behaviour of any airport so
far.** The 3 dropped days are all inner-training, all "no routine report
nearest the hour at all" (genuine outages, not off-hour reports): 2021-05-02
and 2021-05-03 (inside the 59-hour outage F76 found, 2021-05-02 06:00 to
2021-05-04 16:00 UTC) and 2024-03-21. **Zero days were lost to an off-hour
report**, matching F76's whole-record zero exactly. Every one of the 1,588
kept days paired at a steady **-5 minutes** from the target hour (the 19:55
report serving 20:00) — no variation at all, and **zero days had more than
one report inside D14's 15-minute window**. Nothing was filled (SPEC 2.2).

Row counts beside the four prior airports: inner-training 1,205 (EGLC), 1,204
(CDG), 1,206 (DSM), 1,193 (Dubbo), **1,203 (Reno)** — second only to DSM;
validation 364, 365, 365, 360, **365 (Reno, no day lost)**.

**F79. Reno's bias at 20:00 UTC is a fifth distinct shape: persistently
positive, unlike any prior airport's sign-flipping pattern, and largest in
winter — the one measure that lines up with the terrain hypothesis (D42).**
Inner-training only; the validation year's values were not explored and the
test year not touched.

Overall, beside EGLC (F13), CDG (F28), DSM (F43) and Dubbo (F61):

```
                            EGLC       CDG       DSM     Dubbo       RNO
days                       1,205     1,204     1,206     1,193     1,203
mean bias degC            -0.108    +0.050    -0.231    -0.136    +0.492
median degC               +0.000    +0.100    -0.200    -0.100    +0.640
st dev degC                1.551     1.654     2.550     1.740     1.758
mean |bias| degC           1.172     1.248     1.973     1.260     1.390
station warmer, %           48.7      51.7      45.5      45.3      67.7
min / max degC        -7.0/+5.6 -7.7/+5.8 -10.4/+9.2 -12.8/+8.0  -7.7/+7.4
```

**Reno's mean |bias| (1.390) sits INSIDE the four flat airports' own range
(1.172–1.973)** — not above it, so this single headline measure does not by
itself confirm the terrain hypothesis. What is genuinely new is the **sign**:
the station ran warmer than GFS on **67.7%** of inner-training days, well
above every other airport's 45–52%, and the mean bias stayed **positive
across almost every forecast-temperature band and every season** — a
steadier, closer-to-constant warm offset than the sign-flipping,
band-and-season-dependent shapes the other four airports showed (EGLC's
warm-end-only, CDG's spread-calendar, DSM's both-and-larger, Dubbo's
single-season). Against forecast temperature:

```
forecast band (degC)     days  mean bias   st dev  mean |bias|     EGLC      CDG      DSM    Dubbo
-10 to 0                    27     +0.689    1.361        1.247        -   +1.800   -1.087        -
0 to 5                     123     +0.730    2.220        1.752   -0.049   -0.687   -0.781   +0.300
5 to 10                    204     +0.562    2.176        1.761   +0.361   +0.223   -0.337   +1.046
10 to 15                   161     +0.212    2.085        1.634   +0.387   +0.339   +0.465   +0.252
15 to 20                   153     +0.548    1.906        1.541   -0.287   +0.320   +1.098   +0.456
20 to 25                   151     +0.722    1.222        1.142   -0.746   -0.142   +0.953   +0.026
25 to 30                   163     +0.518    1.183        1.052        -        -   -0.147   -0.630
30 to 45                   221     +0.260    1.285        0.998        -        -   -3.089   -1.301

coldest 10%  n=120  forecast -5.0 to +4.2 degC  mean bias +0.669  mean |bias| 1.617
warmest 10%  n=120  forecast +32.8 to +38.2 degC  mean bias +0.076  mean |bias| 0.905
```

Every single band is positive — the station never runs colder than GFS on
average at any forecast temperature, the only airport of the five where that
is true. By season:

```
season         days   RNO bias   st dev  RNO |bias|     EGLC      CDG      DSM    Dubbo
winter DJF      251     +0.165    2.382       1.850   +0.356   -0.092   -0.805   -0.973
spring MAM      342     +1.159    1.445       1.484   -0.061   +0.614   +0.923   +0.073
summer JJA      337     +0.400    1.332       1.053   -0.549   -0.056   -0.208   +0.140
autumn SON      273     +0.070    1.668       1.263   -0.052   -0.401   -1.187   +0.027
```

**Winter is Reno's own largest-magnitude season (mean |bias| 1.850, against
1.053–1.484 in the other three)** — the one result that does line up with
the terrain hypothesis: cold-air drainage and downslope (foehn) warming are
both winter effects, and this is the first sign the model has any structured
winter signal to learn from. Spring carries the largest **mean** bias
(+1.159) but with the widest spread relative to season, so winter is the
season where the *size* of the miss, not just its average direction, stands
out most.

**F80. The rehearsal: at Reno the correction does NOT beat raw GFS — the
first such result in the project — though it still beats persistence,
climatology, and (barely) the mean-bias reference.**

Model: the locked D21/D31/D35/D39 recipe, fitted on Reno's 1,203
inner-training rows only. All five methods scored on the same 365 common
validation days (Reno loses no day to a missing previous-day observation):

```
method                  MAE degC  bias degC  RMSE degC  worst miss
Raw GFS                    1.493     -0.013      2.183        9.86
Persistence                2.756     -0.014      3.632       12.22
Climatology                3.774     +0.122      4.769       18.40
Mean-bias reference        1.524     -0.505      2.240       10.35
ML-corrected               1.499     -0.492      2.100        8.49
```

Verdicts:

```
vs Raw GFS              NO    1.499 against 1.493  ->  -0.006 degC worse (-0.4%)
vs Persistence          YES   1.499 against 2.756  ->  +1.257 degC better (45.6%)
vs Mean-bias reference  YES   1.499 against 1.524  ->  +0.025 degC better (1.7%)
vs Climatology          YES   1.499 against 3.774  ->  +2.275 degC better (60.3%)
```

**This is a validation rehearsal, not the frozen bar (SPEC 5.3, 5.0). A poor
number here does not mean Reno has failed** — the bar is judged once, on the
sealed test year, in a later session (D18 exists precisely because
rehearsal and test years can differ; F16 and F64 both record how much the
weather alone moved a airport's number between the two).

Four things the numbers say, read honestly:

1. **The recipe does not clearly travel to Reno.** Applied unchanged at a
   fifth location with a fourth distinct target hour, on a bias shaped like
   nothing seen before (F79, persistently positive rather than sign-flipping),
   it loses to raw GFS by a hair — 0.006 degC on 365 days, well within noise,
   but a loss, not a win.
2. **The margin over the mean-bias reference (1.7%) is the thinnest of any
   airport's rehearsal** — EGLC 5.3%, CDG 4.0–4.1%, DSM 14.9%, Dubbo 6.3%,
   Reno 1.7%. The "the model learned structure, not just an offset" claim,
   already noted as thinnest anywhere for Dubbo on the sealed test (F65,
   2.3%), is thinner still here, on the rehearsal. F79's finding that Reno's
   bias looks closer to a constant (persistently positive, less
   band/season-dependent) than the other four airports' shapes is the
   likely reason: there is less real structure available for the model to
   add beyond what the mean-bias reference already captures.
3. **The seasonal pattern helps in only 2 of 4 seasons, and winter carries
   essentially the whole win:**

```
season         days   raw GFS   ML-corr   RNO chg   EGLC chg   CDG chg   DSM chg   Dubbo chg
winter DJF       90     2.431     2.275    -0.156     +0.087     +0.025    -0.414     -0.054
spring MAM       92     1.255     1.233    -0.022     -0.015     -0.057    -0.184     +0.022
summer JJA       92     0.807     0.919    +0.112     -0.321     -0.122    +0.061     +0.066
autumn SON       91     1.500     1.586    +0.086     -0.049     -0.044    +0.061     +0.086
```

   Winter is Reno's only season with a win of any real size, and it is
   consistent with F79's winter-biggest-bias finding — but summer and
   autumn both got worse, and the winter win (-0.156) is not large enough
   to pull the full-year average ahead of raw GFS. Day-by-day, the
   correction was closer to the truth than raw GFS on **172 of 365 days
   (47.1%)** — below half, and the lowest win rate of any airport's
   rehearsal (CDG 55.3%, DSM 55.6%, Dubbo 53.5%).
4. **The in-sample-to-validation gap is the largest yet, consistent with
   overfitting a mostly-constant signal.** In-sample MAE on Reno
   inner-training was 1.004 degC against raw GFS's 1.390 (a 27.8%
   "improvement"), the largest in-sample gain of any airport (EGLC 0.879,
   CDG 0.945, DSM 1.221, Dubbo 0.961) relative to its own raw-GFS figure,
   yet it produced the smallest validation gain (-0.4%). That pattern — a
   flexible model fitting a signal that is close to a constant plus noise
   very tightly in-sample, then adding little on unseen data — is the
   ordinary signature of overfitting, and it is coherent with F79's finding
   that Reno's bias is more constant-like than the other four airports'.

Feature importances:

```
feature             EGLC gain %  CDG gain %  DSM gain %  Dubbo gain %  RNO gain %  RNO splits
forecast_temp_c           44.3%       35.9%       45.0%         47.8%       40.4%       1,842
season_sin                26.7%       39.9%       37.3%         30.2%       35.7%       1,173
season_cos                29.0%       24.2%       17.7%         22.0%       23.9%       1,185
```

Nothing is ignored and nothing dominates; Reno's split between temperature
and season sits inside the range every other airport has shown.

How each reference was built, identical in method to the four prior
airports, fitted on Reno inner-training only:
- **Raw GFS** — the forecast value itself, uncorrected.
- **Persistence** — the previous calendar day's 20:00 UTC observation. Past
  values only (SPEC 2.1d). The first scored validation day, 2024-08-01,
  takes its persistence value from 2024-07-31, which sits in inner-training
  — a past observation, so legal.
- **Climatology** — the seasonal average of the *observed* temperature at
  Reno within 7.5 days of that position in the year, training-window only
  (SPEC 2.1c).
- **Mean-bias reference** — the forecast plus +0.4921 degC, the mean Reno
  inner-training bias and nothing else.
- **ML-corrected** — the forecast plus the model's predicted residual.

Nothing was fitted on the validation year: not the model, not the
climatology, not the mean bias, not any encoding. **No SPEC edit was made
and none was authorised.**

**F81. What a Reno rehearsal loss does and does not answer — the honest
accounting F46/F63 gave DSM and Dubbo, applied to a result that reads the
other way.**

- **The terrain hypothesis (D42) is not confirmed by the headline measures.**
  Raw GFS's rehearsal-year error at Reno (1.493) is not the hardest of the
  five — DSM (1.748) still clearly is, and Reno sits between Dubbo (1.397)
  and CDG (1.426). Reno's inner-training mean |bias| (1.390, F79) sits
  inside the four flat airports' own range rather than above it. On these
  two measures, D42's expectation that Reno would be the hardest raw-GFS
  problem of the five is not borne out this session.
- **The one measure that does line up with the terrain hypothesis is
  winter.** Reno's own worst season for bias size (F79) is also the one
  season where the correction clearly wins (F80) — directionally consistent
  with cold-air-drainage/downslope effects being real but not large enough,
  spread across the rest of the year, to lift the annual figure past raw
  GFS.
- **Whether the simple D19 features are enough at Reno is now a genuine,
  open question rather than a settled one.** F80's four readings together —
  the outright rehearsal loss, the thinnest-yet margin over the mean-bias
  reference, the lowest day-by-day win rate, and the largest in-sample/
  validation gap — point the same direction: more of Reno's residual than
  at any prior airport looks like it needs information the model does not
  have (cloud cover, wind, a genuine terrain feature) rather than more of
  what it already has (forecast temperature, calendar position).
- **Not the controlled EGLC-CDG comparison.** Reno changes the location
  **and** the target hour (D42, SPEC 4.1), the same honest caveat D33/D37
  attach to DSM and Dubbo.
- **This is a rehearsal result, not a verdict.** SPEC 5.3's bar is judged
  once per airport (SPEC 5.0), on the sealed test year, in a later session.
  D18 exists specifically because a rehearsal and a sealed test can differ,
  sometimes by a lot in either direction (F16, F64). A negative rehearsal
  does not pre-decide Reno's test result, and per the session-27 prompt the
  locked recipe proceeds to lock and test regardless — the bar is judged
  as-is, not adjusted to fit what the rehearsal showed.

**Read as: independent terrain regime, same shared D13 twelve months, two
things changed from the European pair (location and target hour) — the same
honest reading D33/D37 give DSM and Dubbo. Unlike every prior rehearsal,
this one is a loss, not a win — recorded straight, as SPEC 2.4 requires.**

---

## 2026-08-20 — Session 28 decision: Reno's method lock

**D44. Reno's method is LOCKED. This entry fully specifies what Reno's
sealed-test session will run.**

This is **D39 with the airport and the target hour swapped and nothing else
touched.** Every methodological choice below — the model, its settings, the
features, what is predicted, the pairing rule, the missing-data rule, the
references, the metric, the bar, and the one-look rule — is the same choice
D39 made, which was the same choice D35, D31 and D21 made before it. Not one
of them is new, and none is changed to try to rescue Reno's poor rehearsal
(F80, F81).

**Two things differ from D39, exactly as two things differed each time a
lock was written for a new airport.** Reno changes the location **and** the
target hour against every earlier lock, including D39 (D42, F74, SPEC 4.1).
That cost was accepted on purpose, in advance, when the fifth airport was
opened and then switched (D40, D42). It is repeated here so the test session
cannot report a Reno result as though it were the same controlled comparison
EGLC and CDG make between them.

Why it is written out separately rather than by pointing at D39: D39 names
Dubbo throughout and fixes the target at 02:00 UTC, so Reno's test session
would otherwise have to reach back to a Dubbo-named record and translate it —
four times over, through D35, D31 and D21 before it — while the test year was
open. The whole value of a lock is that the executing session decides nothing
(D21.11, D31.11, D35.11, D39.11). A translation is a decision. So the
translation is done here, now, with Reno's test year still unopened, and the
test session executes this record and reports.

**D44.1 — Target.** The temperature at **20:00 UTC** at **Reno, Nevada
(IEM/station code `RNO`, ICAO code `KRNO`, IEM network `NV_ASOS`)**, the
station at latitude 39.4839, longitude -119.7711, elevation 1345 m — IEM's
own position, per SPEC 3.4 and F66. The forecast comes from the Open-Meteo
grid point that position maps to: latitude 39.537918, longitude -119.765625,
elevation 1344 m, 6.02 km from the airport with a -1 m height difference
(SPEC 3.4, F66, confirmed again at the full pull in F75) — by far the
smallest grid-elevation mismatch of any airport in the project, even though
Reno is by far the highest-elevation airport (1,345 m). Reno's difficulty, if
any, is expected to come from horizontal terrain complexity — the nearby
Sierra Nevada front — not from this vertical mismatch (D42). One row per day.

The hour is **20:00 UTC, not 12:00, 18:00 or 02:00 UTC**, and that is one of
the two methodological inputs this lock does not share with D39 (the other is
the airport itself). 20:00 UTC is local standard noon at Reno (12:00 PST in
winter, 13:00 PDT in summer, daylight saving deliberately ignored so the
target stays one fixed UTC hour all year), which is what SPEC 4.1 asks every
airport to target. Decided on principle before any Reno data was seen (D42)
and then checked against the timezone database (F74), the same discipline
F32, F50 and session 25's own PART 0c applied for DSM, Dubbo and Bozeman.

**D44.2 — What the model predicts.** The **residual**: observed minus
forecast (SPEC 4.2). The corrected forecast is the GFS forecast plus the
predicted residual. The model never predicts temperature directly. Identical
to D39.2, D35.2, D31.2 and D21.2.

**D44.3 — Features.** The D19 minimal set, exactly three:
```
forecast_temp_c   the GFS forecast temperature for that day at 20:00 UTC
season_sin        sin(2 * pi * year_fraction(date))
season_cos        cos(2 * pi * year_fraction(date))
```
where `year_fraction` is `(day_of_year - 1) / 365`, or `/ 366` in a leap
year. No hour-of-day feature — the hour is fixed at 20:00, so it carries no
information, which is D19's reason unchanged. No recent-observation feature,
even though SPEC 2.1d would allow one — see D19 for why. Identical to D39.3,
D35.3, D31.3 and D21.3 apart from which fixed hour `forecast_temp_c` is read
at, which follows from D44.1. **Not changed despite the rehearsal loss**:
adding a feature (cloud cover, wind, a terrain descriptor) would be moving
the goalposts after seeing a discouraging result, not applying a fixed
method. F81 already names richer features as a possible future direction —
that is a stage-4/SPEC-6 question, not something this lock reaches for.

**D44.4 — Model and settings.** LightGBM gradient-boosted trees (SPEC 4.4,
D12), with exactly the session 05 settings, unchanged:
```
objective=regression_l1   (absolute error, D20)   n_estimators=300
learning_rate=0.05        num_leaves=15           min_child_samples=40
subsample=1.0             colsample_bytree=1.0    reg_alpha=0.0
reg_lambda=0.0            random_state=42         n_jobs=1
deterministic=True        force_row_wise=True     verbose=-1
```
Nothing is tuned, searched or varied in the test session. Library versions
are pinned in `requirements.txt` (D24): python 3.12.2, numpy 2.5.2, lightgbm
4.7.0. Identical to D39.4, D35.4, D31.4 and D21.4. Session 27 already ran
this exact configuration at Reno, and its PART 0 proved it against
`scripts/session05_model.py`: **0 model settings differ, and exactly 1
shared constant differs — TARGET_HOUR, 12 to 20** (session 27 findings,
above). That one constant is D42 and nothing else.

**D44.5 — Training data for the test: the FULL D13 training window,
2021-03-24 to 2025-07-31, at Reno.** That is Reno's inner-training **and**
Reno's validation year recombined into one training set.
- Reason: the same reason D21.5, D31.5, D35.5 and D39.5 gave. The D18 split
  existed so the method could be rehearsed without touching the test year.
  The method is locked, so validation has finished its job, and holding a
  year back would only throw away real training data. Refitting on all
  non-test data before the single test is the standard move — and it is what
  all four earlier airports did, so doing anything else here would add a
  further difference on top of the location and the hour.
- Everything fitted is fitted on this window and nothing else: the model, the
  climatology baseline (SPEC 2.1c) and the mean-bias figure.
- **Expected row count, written down before the run, and confirmed against
  session 27's join (F78), which itself matched session 26's gap map (F77)
  exactly.** The window holds 1,591 calendar days. Session 27 kept **1,203
  inner-training rows and 365 validation rows**, both exactly as F77
  predicted before the join ran, so:
  ```
  inner-training rows (F78)                      1,203
  validation rows      (F78)                       365
  expected training rows for the test refit      1,568 of 1,591 calendar days
  days dropped, all reconciled by F78               23
      the shared 492-hour forecast gap               20  (2023-12-30..2024-01-18)
      observation-side losses, inner-training          3
      observation-side losses, validation               0
  ```
  **1,568, not 1,591, 1,588, or any other figure.** Reno's forecast-gap loss
  (20 days) matches EGLC, LFPG and DSM rather than Dubbo's 21, because Reno's
  20:00 UTC target falls after the gap's last missing hour (11:00 UTC), the
  same shape those three airports share (F75). The 3 observation-side losses
  are the cleanest of any airport's training-window pairing so far bar DSM's
  zero (F76, F78) — zero of them are off-hour reports, all three are genuine
  outages. A count other than 1,568 is a D44.11 stop signal.
- **Note the consequence, so it is not a surprise:** the model that is tested
  is **not** the model measured in session 27. It is the same recipe fitted
  on about 30% more days than inner-training alone, including one more full
  cycle of seasons. **The test number will not match session 27's 1.499
  rehearsal figure and should not be expected to.** At EGLC the equivalent
  move shifted the number by 0.125 degC (F16), at CDG by 0.169 degC (F30), at
  DSM by 0.234 degC (F47) and at Dubbo by 0.073 degC (F62 to F64, 1.283 to
  1.210), and in each case most of that was the weather rather than the extra
  data. **Given F80's finding that Reno's in-sample gain did not survive to
  validation (overfitting a near-constant signal, F81), the direction of this
  shift is genuinely unpredictable in advance** — unlike the four passed
  airports, where the refit-on-more-data shift moved the number but never
  flipped a pass to a fail or back. This is named here, before the look, so
  it is not read as a surprise afterward.

**D44.6 — Test data: Reno, 2025-08-01 to 2026-07-31 (D13), and nothing after
it.** Data after 2026-07-31 is not used, keeping the test set exactly one
calendar year. This is Reno's own test year: the dates are the same as every
earlier airport's but the data is a fifth airport's, and it has never been
looked at.

No value from Reno's test year has ever been printed, computed or looked at,
by any session, for any reason. Session 25's candidate-comparison sample for
Reno (F66) and session 26's structural gap map (F75–F77) both stayed on the
training side or reported counts only, never a temperature value from the
test window, the same Q29-closing discipline Dubbo's verify-on-contact
established (D39.6). Session 26's own text is explicit that the 2026 RNO
chunk files have never been opened and the 2025 chunk was read with a
2025-07-31 cutoff (session 26 Part C); session 27 repeats and re-asserts this
programmatically (session 27 findings, above: "the script asserts that no
date on or after 2025-08-01 reached any table").

**D44.7 — Pairing and missing data.** The D14 rule, applied exactly as
written at the other four airports: the routine report is the truth
observation, each target-hour forecast is paired with the report nearest that
hour, and if no report falls within 15 minutes of the hour the day is dropped
and counted. Drop, count, report — nothing filled, ever (SPEC 2.2). The drop
counts for both the training window and the test year are part of the
output.

The location facts inside this: **Reno reports at `:55`**, 5 minutes before
the hour — the same shape DSM's `:54` reporting takes (SPEC 3.4, F76). So the
rule pairs 20:00 UTC with the **19:55 report — a 5-minute offset**, session
27 confirming every one of the 1,588 kept training-window days paired at a
steady -5 minutes, with zero variation and zero days carrying more than one
report inside the 15-minute window (F78). Whether Reno files a second
scheduled report remains unchecked (Q31, SPEC 3.4's "not yet checked" cell);
it does not matter here, because D30 already settled that the pairing rule is
not adapted for one airport and Reno reuses that unchanged regardless of the
answer.

**Reno's test-year prediction is the cleanest of any airport so far, cleaner
even than DSM's.** F77's gap map, written down before any join, is explicit:
```
forecast-gap days in Reno's test year                              0   (F75, F77)
observation-side losses in Reno's test year                        0   (F77)
expected paired rows                                            365 of 365
```
Unlike Dubbo, whose test-year loss could only be bounded as a count without
named dates (D39.7), Reno's test-year prediction is a clean zero on both
sides — the 492-hour forecast gap falls entirely inside the training window
(F75), and F76's whole-five-year observation record carries zero off-hour
reports and no outage anywhere near the test year at the 20:00 target. **The
expected scored-day count is also 365 of 365**: persistence needs the
previous calendar day's observation, and since no test-year day and no day
immediately before it (2025-07-31, the "yesterday" for the first test day)
is among the 3 named training-side losses (2021-05-02, 2021-05-03,
2024-03-21, none near 2025-07-31), nothing is expected to cost a scored day
the way it did at EGLC, CDG, DSM and Dubbo (F16, F30, F47, F64 each lost
exactly one extra scored day this way). **This is an expectation, not a
requirement**, exactly as D31.7, D35.7 and D39.7 said of their own
predictions: the test session reports the **actual** paired-row and
scored-day counts, names any date it drops, and reconciles them against the
365 figure above. A paired-row or scored-day count other than 365 is a
D44.11 stop signal.

**D44.8 — The four references. Anything that has to be *fitted* is fitted on
Reno's training window only.** Raw GFS and persistence are fitted on
nothing — they are just values. Climatology and the mean-bias figure are
fitted, and both come from Reno's D13 training window (SPEC 2.1c).
- **Raw GFS** — the forecast value itself, uncorrected. *Part of the bar.*
  **Record explicitly, per the session prompt: raw GFS is the half of the bar
  most likely to fail here.** F80's rehearsal found the correction lost to
  raw GFS by 0.006 degC (-0.4%) — the first negative rehearsal in the
  project. If the sealed test repeats that loss, it is a legitimate,
  honestly-reported outcome (SPEC 2.4), not something to fix by adjusting the
  method after the fact.
- **Persistence** — the previous calendar day's 20:00 UTC observation at
  Reno. Past values only (SPEC 2.1d). For the first test day, 2025-08-01,
  "yesterday" is 2025-07-31, which sits in the training window and is not
  one of F78's named observation-side losses. That is a past observation, so
  it is legal and it will be used; written down here so it is not mistaken
  for leakage later. Identical in substance to D21.8's, D31.8's, D35.8's and
  D39.8's note. On the rehearsal (F80), persistence was Reno's weakest
  reference by a wide margin (2.756 against raw GFS's 1.493) — the same
  shape DSM and Dubbo showed (D39.8) — so persistence is expected to remain
  the easier half of the bar to beat, with raw GFS the one genuinely at risk.
- **Climatology** — the seasonal average of the *observed* temperature at
  Reno for that position in the year, averaged over every **Reno
  training-window** observation within 7.5 days of it, measured around the
  circle so late December and early January are neighbours (SPEC 2.1c).
  *Informative only.*
- **Mean-bias reference** — the forecast plus one constant: the mean **Reno
  training-window** bias. *Informative only* (SPEC 5.2, D23). On Reno's
  rehearsal (F80) this reference did **NOT** beat raw GFS (1.524 against
  1.493, itself a loss) — unlike EGLC, DSM and Dubbo, where the constant
  offset beat raw GFS, and more like CDG, where it did not (D39.8). The
  constant available at Reno is real (+0.4921 degC on inner-training, F80)
  but not enough on its own to
  beat raw GFS on the validation year; the training-window figure will differ
  slightly and is computed in the test session, not here. The ML-corrected
  model beat the mean-bias reference by only 1.7% on the rehearsal (F80) —
  the thinnest margin of any airport's rehearsal — so a win over it on the
  test year, even a narrow one, is the evidence that whatever the correction
  adds is structure and not merely the same offset restated.

All five methods — the four above plus the corrected forecast — are scored on
the **same set of days**, the days where every method has a value.

**D44.9 — The metric and the bar.** Mean absolute error in degrees Celsius
(SPEC 5.1). **Reno passes if the corrected forecast has a lower MAE than both
raw GFS and persistence over Reno's test year.** No numeric margin — the bar
is qualitative and stays that way (D22, SPEC 5.3). Climatology and the
mean-bias reference are reported but do not decide pass or fail. The margin
is reported prominently alongside the verdict, so a technical pass by a hair
reads as what it is, and so does a technical failure (D22).

**The bar is judged once per airport, on that airport's own data (SPEC
5.0).** EGLC's, CDG's, DSM's and Dubbo's passes do not excuse a Reno failure,
and a Reno result does not re-open any of theirs. The prior four airports'
margins (3.3%–16.3% on their sealed test years) are not a target Reno has to
reach and not a number Reno is measured against; Reno is measured against
Reno's own raw GFS and Reno's own persistence, and nothing else. **A Reno
failure is not a defect in the project — it is exactly the kind of honest,
possibly-negative finding SPEC 2.4 and D22 exist to allow the bar to
produce.**

**D44.10 — One look, and the result stands.** Reno's test year is opened
once, this method is run once, and whatever comes out is reported straight —
pass or fail, with the seasonal breakdown and the drop counts. A failure is
an honest finding (SPEC 2.4), not something to fix by trying again. If the
result disappoints, the response is a new decision logged here by the owner,
never a quiet re-run. Identical to D21.10, D31.10, D35.10 and D39.10.

Read plainly. Reno's rehearsal margin was **-0.4%** (F80) — the first
negative rehearsal margin of any airport in the project, against EGLC's
6.0%, CDG's 3.4–3.5%, DSM's 16.1% and Dubbo's 8.2%, all positive. **A test
result that repeats a loss should not be treated as a surprise; nor should a
test result that reverses to a win** — D18 exists precisely because rehearsal
and test years can differ, sometimes by more than the gap between any two of
the four passed airports' own validation and test figures (F16, F30, F47,
F62-to-F64). Neither outcome licenses any change to this lock.

**D44.11 — Deviation is a stop signal.** If Reno's test session finds any
reason to depart from this record — a setting that does not fit, a missing
file, a count that will not reconcile against D44.5 or D44.7, a tempting
small improvement — it **stops and raises it with the owner**. It does not
decide on the fly with the test year open. Any change to the above is a new
DECISIONS entry made deliberately, not an adjustment made mid-run. Identical
to D21.11, D31.11, D35.11 and D39.11. **This holds with particular force
here: a poor rehearsal is not a licence to add a feature, retune a setting,
or otherwise nudge the recipe toward a pass. The whole point of a written
lock is that it is decided before the result is known, not adjusted once a
discouraging signal appears.**

**D44.12 — The near-constant-bias / overfit watch-item, recorded before the
look and NOT acted on.** This is inside the lock so that any inspection
after the test is honest: the place to look was named before anyone knew the
result, mirroring D39.12's single-season watch-item for Dubbo.

F80 and F81 together found four things on Reno's rehearsal that point the
same direction: the correction lost to raw GFS outright (-0.4%); its margin
over the mean-bias reference was the thinnest of any airport (+1.7%); its
day-by-day win rate was the lowest of any airport (47.1%, below half); and
its in-sample-to-validation gap was the largest of any airport (27.8%
in-sample "improvement" collapsing to -0.4% out-of-sample). F79 explains the
likely mechanism: Reno's bias is unusually close to a **constant** — warmer
than GFS in 67.7% of inner-training days (against 45–52% elsewhere) and
positive in almost every forecast-temperature band and every season, rather
than the sign-flipping, band-and-season-dependent shapes the other four
airports showed. A flexible model fitting a signal that is close to a
constant-plus-noise very tightly in-sample, then adding little on unseen
data, is the ordinary signature of overfitting.

**This is not a reason to change the method, and the method does not
change. It is locked.** **If Reno's sealed test also fails to beat raw
GFS, this near-constant-bias / overfit pattern is the expected explanation,
recorded here in advance — not a bug to hunt or a surprise to explain away
after the fact.** The one measure that did line up with the terrain
hypothesis (D42) on the rehearsal was winter, the season with both the
largest bias magnitude (F79) and the correction's only clear win (F80); **if
Reno's test result behaves oddly — a swing either way, a season that does not
match the rehearsal, a result that flips from fail to pass — winter is the
first place to look**, and looking there is a description of what happened,
never a licence to re-run or adjust anything (D44.10, D44.11).

---

**The D39 ↔ D44 correspondence check.** Every D39 sub-point set beside its
D44 counterpart, mirroring the format the D35 ↔ D39 check used. Two kinds of
intended difference are expected, exactly as they were between D35 and D39:
`LOCATION` (the airport and what follows from it) and `HOUR` (the target
hour, per D42, and what follows from it). Anything else appearing in that
column would be a stop signal.

```
point  subject                D39 (Dubbo)               D44 (Reno)                differs?
.1     target hour            02:00 UTC (D37)           20:00 UTC (D42)           HOUR
.1     why that hour          local standard noon       local standard noon       same
.1     airport                Dubbo / YSDU              Reno / RNO (KRNO)         LOCATION
.1     station position       -32.2167/148.5747/275m    39.4839/-119.7711/1345m   LOCATION
.1     position source        IEM's own metadata (F49)  IEM's own metadata (F66)  same
.1     grid point             -32.274643/148.59375      39.537918/-119.765625     LOCATION
.1     grid distance/height   6.69 km, +4 m             6.02 km, -1 m             LOCATION
.1     row granularity        one row per day           one row per day           same
.2     what is predicted      residual = obs - fcst     residual = obs - fcst     same
.2     how corrected is made  fcst + predicted resid    fcst + predicted resid    same
.3     features               3: fcst temp, sin, cos    3: fcst temp, sin, cos    same
.3     fcst temp read at      02:00 UTC                 20:00 UTC                 HOUR
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
.5     inner-training rows    1,193                      1,203                     LOCATION
.5     validation rows        360                        365                       LOCATION
.5     expected refit rows    1,553 of 1,591 days        1,568 of 1,591 days       LOCATION
.6     test window             2025-08-01..2026-07-31   2025-08-01..2026-07-31    same
.6     test-year files opened  none before this lock     none before this lock    same
.7     pairing rule            D14, 15-min tolerance     D14, 15-min tolerance    same
.7     reports at              :00 (0-min offset)        :55 (5-min offset)       LOCATION
.7     expected test-yr drop   9 obs-side (dates unknown) 0 (both sides)          LOCATION
.7     expected paired rows    356 of 365                 365 of 365               LOCATION
.8     four references         raw GFS, persistence,     raw GFS, persistence,    same
                              climatology, mean-bias     climatology, mean-bias
.8     what is fitted on       Dubbo training window     Reno training window     LOCATION
                              only                       only
.9     metric                  MAE, degrees C            MAE, degrees C           same
.9     bar                     beat raw GFS AND          beat raw GFS AND         same
                              persistence, qualitative   persistence, qualitative
.10    one look                yes                        yes                     same
.11    deviation = stop        yes                        yes                     same
.12    watch-item type         one season (autumn SON)   near-constant bias /     LOCATION
                                                          overfit pattern
```

**Everything outside the LOCATION and HOUR columns reads "same".** In
particular — the point the session prompt asked to be confirmed explicitly —
**the features (D44.3) and the model settings (D44.4) are byte-for-byte
identical to D39's, D35's, D31's and D21's, despite Reno's rehearsal loss.**
No feature was added, no setting was tuned, and no tolerance was widened to
try to turn the -0.4% rehearsal into a pass before the test runs. The only
non-LOCATION, non-HOUR row that is not a flat "same" is `.12`, the
watch-item, which is expected to differ in *content* airport to airport (it
names whatever the rehearsal actually found) while staying identical in
*function* — a place to look, named before the result, never a licence to
adjust the method.

---

## 2026-08-20 — Session 29 finding: Reno's sealed-test result

**F82. RENO DOES NOT PASS. At Reno the corrected forecast does not beat raw
GFS on the held-out test year — the project's first failure, and one D44.12
named as the expected outcome before this session opened the test year.**

The verdict first, because that is what the session was for:

```
                        MAE degC   bias degC   RMSE degC   worst miss   part of bar?
Raw GFS                    1.414      -0.355       1.999          9.89   YES
Persistence                2.490      +0.015       3.355         13.88   YES
Climatology                4.027      +0.855       5.167         16.20   no  (informative)
Mean-bias reference        1.500      -0.730       2.098         10.26   no  (informative)
ML-corrected               1.458      -0.575       1.990          7.86   the claim

vs Raw GFS       NOT BEATEN   1.458 against 1.414  ->  0.044 degC worse (-3.1%)
vs Persistence   BEATEN       1.458 against 2.490  ->  1.032 degC better (+41.4%)
```

**Reno fails the frozen bar (SPEC 5.3, 5.0, D44.9): the corrected forecast
does not have a lower MAE than raw GFS over 2025-08-01 to 2026-07-31 at
Reno, though it does beat persistence by a wide margin.** Exactly the half
of the bar D44 and D44.12 named in advance as most likely to fail, did. The
margin is stated prominently because D22 requires it whether the result is a
pass or a fail: **-0.044 degC, a 3.1% loss against raw GFS** — the corrected
forecast is worse than doing nothing, on average, over the sealed year.
Persistence is beaten comfortably (+41.4%, 2.490 against 1.458), so the
verdict turns entirely on the raw-GFS half, exactly as D44.8 said it would.

**This is Reno's single authorised look (D44.10), executed exactly as D44
specified, and the result stands (D44.10, D44.11). No re-run, no tuning, no
adjustment was made or considered.** `scripts/session29_test.py` proves
itself against the D44 lock value-by-value (23 of 23 match), against
`scripts/session05_model.py`'s settings and shared code (character-identical),
and against `scripts/session24_test.py` (Dubbo's sealed test) function by
function — exactly one constant differs, TARGET_HOUR (2 → 20, D42), and the
only functions whose text differs (`features`, `load_forecast_target_hour`,
`load_obs_target_hour`, `fit_on_training`) differ by docstring and printed
labels only, proved identical in executable shape with docstrings stripped.

**The training refit and the test-year join both reconcile exactly against
what D44 predicted before the look — including the scored-day count, which
D44.7 could predict cleanly for Reno where D39.7 could not for Dubbo.**

```
training window kept rows            predicted   actual   verdict
inner-training (F78)                     1,203    1,203    MATCHES
validation (F78)                           365      365    MATCHES
full refit total (D44.5)                 1,568    1,568    MATCHES

test-year paired rows (D44.7)         predicted   actual   verdict
forecast-gap days                            0        0    MATCHES
days lost to an off-hour-only report         0        0    MATCHES
days lost to no report near 20:00            0        0    MATCHES
days lost to a report with no temp           0        0    MATCHES
paired rows                                365      365    MATCHES
scored days (persistence lookback)         365      365    MATCHES
```

**Every one of D44.7's predictions landed exactly — zero test-year drops on
either side, the cleanest test-year prediction of any airport confirmed as
the cleanest test-year result.** No date was dropped from Reno's test year
for any reason; all 365 calendar days paired and all 365 were scored,
including persistence, since 2025-07-31 (the first day's "yesterday") sits
in the training window and was never one of F78's three named
observation-side losses. Nothing was filled (SPEC 2.2).

**Day by day, not just on average — and the only airport below half.** The
correction was closer to the truth than raw GFS on **159 of 365 days
(43.6%)** and further away on 206 (56.4%), with no day where it made no
difference. That is lower even than the rehearsal's own 47.1% (F80), and the
only day-by-day win rate below 50% of any airport tested so far — EGLC
60.9% (F16), CDG 58.7% (F30), DSM 53.4% (F47), Dubbo 52.4% (F64).

**Per season, the correction helped in two of the four — tying Dubbo for
the fewest of any airport — but the season pair is not the one the
rehearsal found:**

```
season         days   raw GFS   ML-corr    change   persistence
winter DJF       90     2.359     2.184    -0.175         2.328
spring MAM       92     1.020     1.215    +0.195         3.224
summer JJA       92     0.899     1.075    +0.176         1.962
autumn SON       91     1.398     1.375    -0.024         2.443
```

("change" is corrected MAE minus raw GFS MAE. Negative means better than raw
GFS.) On the rehearsal (F80), winter and spring helped; on the test year,
**winter and autumn help instead — spring flips from a thin win (-0.022) to
the year's worst loss (+0.195), and autumn flips from a loss (+0.086) to a
small win (-0.024).** Winter is the one season that stayed a win in both
periods, and grew slightly more negative (-0.156 → -0.175) — the single
measure D44.12 named in advance as lining up with the terrain hypothesis
(D42), and it is the one measure that continued to line up here.

**D44.12's near-constant-bias / overfit watch-item, read exactly as it was
written down before the look.** F80 named four rehearsal readings that
together pointed at overfitting a near-constant signal; the same four
readings, measured on the test year, point the same way or further:

```
measure                                     rehearsal (F80)   test year (F82)
margin vs raw GFS                                     -0.4%             -3.1%
margin vs mean-bias reference                         +1.7%             +2.8%
day-by-day win rate                                   47.1%             43.6%
in-sample improvement over raw GFS                    27.8%      25.0% (in-sample),
                                                                  collapsing to -3.1% oos
```

The raw-GFS margin did not merely repeat its rehearsal loss — it **widened**,
from -0.4% to -3.1%. The margin over the mean-bias reference and the
day-by-day win rate moved in opposite directions from each other (the former
improved slightly, to +2.8%; the latter worsened, to 43.6%), so neither
alone explains the widening; the model continues to add real, if thin,
structure over a flat offset (it beats the mean-bias reference, +2.8%,
1.458 against 1.500) while still losing to doing nothing at all (raw GFS).
The in-sample-to-out-of-sample gap persists on the full refit exactly as it
did on the rehearsal fit: **25.0% in-sample "improvement" collapses to a
-3.1% loss out-of-sample**, the same shape F81 already named as the
signature of overfitting a signal that is close to a constant.

**Feature importances, the sanity check that it used what it was meant to:**

```
feature                 gain  gain share   splits   s27 share  s27 splits
forecast_temp_c       3259.6       39.1%    1,841       40.4%       1,842
season_sin             2948.8       35.4%    1,155       35.7%       1,173
season_cos             2122.2       25.5%    1,204       23.9%       1,185
```

Nothing is ignored and nothing dominates; the shares are close to session
27's inner-training-only figures, confirming the refit on the larger window
changed the fit only modestly. Beside the four sealed tests: EGLC
51.8/24.5/23.7, CDG 38.2/34.9/26.9, DSM 43.4/36.1/20.6, Dubbo 45.3/30.3/24.4.
Reno's forecast-temperature share (39.1%) is the lowest of the five —
consistent with F79's reading that more of Reno's residual looks close to a
constant that the seasonal features, not the forecast value, are left to
chase.

**The mean-bias figure, refit on the full training window: +0.3746 degC**
(against the rehearsal's inner-training-only +0.4921, F80) — still the
first and only **positive** training-window constant of the five airports;
the other four all run cold (EGLC -0.1479, CDG -0.0600, DSM -0.2715, Dubbo
-0.1914). The station keeps running warmer than GFS on average, exactly as
F79 found.

**The test number against session 27's rehearsal number — a difference was
expected (D44.5) and its direction was explicitly flagged as unpredictable
in advance, unlike the four passed airports.**

```
method                  s27 valid   s29 test  difference
Raw GFS                     1.493      1.414      -0.079
Persistence                 2.756      2.490      -0.266
Climatology                 3.774      4.027      +0.253
Mean-bias reference         1.524      1.500      -0.024
ML-corrected                1.499      1.458      -0.041

margin over raw GFS:  rehearsal -0.4%   test -3.1%
```

Read the raw GFS row first: the test year was easier for GFS at Reno than
the rehearsal year was (1.414 against 1.493), and every method's raw MAE
fell with it except climatology, which rose. The correction's own MAE fell
too (1.499 → 1.458), but by less than raw GFS's did, which is exactly why
the margin widened rather than narrowed — an unusual shape not seen at any
of the four passed airports, where a falling raw-GFS difficulty either
widened or narrowed the margin without ever flipping a pass or threatening
one already secured.

**How the recipe travelled, all five sealed tests side by side:**

```
method                      EGLC       CDG       DSM     Dubbo      Reno
Raw GFS                    1.242     1.396     1.815     1.251     1.414
Persistence                2.096     2.300     4.003     2.669     2.490
Climatology                2.972     3.774     5.030     3.143     4.027
Mean-bias reference        1.234     1.389     1.760     1.238     1.500
ML-corrected                1.040     1.208     1.700     1.210     1.458
days scored                  363       363       365       347       365
training rows fitted       1,569     1,569     1,571     1,553     1,568

margin over raw GFS        16.3%     13.5%      6.3%      3.3%     -3.1%
margin over persistence    50.4%     47.5%     57.5%     54.7%     41.4%
margin over mean-bias ref  15.7%     13.0%      3.4%      2.3%      2.8%
seasons helped               4/4       3/4       3/4       2/4       2/4
day-by-day win rate        60.9%     58.7%     53.4%     52.4%     43.6%
```

**Every row but one continues the same descending trend the four passes
already showed — narrower margins, fewer seasons helped, lower day-by-day
win rate — and the raw-GFS row is the one that finally crosses zero.**
Nothing in the recipe orders the airports this way; it is what each
airport's own weather and each airport's own bias shape gave. The
mean-bias-reference margin is the one exception to a clean monotonic
trend (Reno's 2.8% sits above Dubbo's 2.3%, though still far below EGLC's
and CDG's), which is consistent with F79/F81's reading that Reno's problem
is a large, close-to-constant offset the model partially captures rather
than one it captures worse than every predecessor on every measure.

**Read plainly, and against F81's reading of the rehearsal, written down
before this look:** F81 said the terrain hypothesis (D42) was not confirmed
by the rehearsal's headline measures, that winter was the one measure that
did line up with it, and that whether the simple D19 features are enough at
Reno was "a genuine, open question rather than a settled one." The sealed
test does not resolve that question in the recipe's favour: raw GFS is not
beaten, the constant-bias signature persists on more data, and winter
remains the one part of the year where the correction clearly helps. **This
is exactly the outcome D44 and D44.12 recorded in advance as the expected
one if Reno's simple features turned out not to be enough — a legitimate,
honestly-reported finding about where this recipe's edge lies (SPEC 2.4),
not a defect in the project or a reason to revisit the four airports that
already passed (SPEC 5.0).**

Full script, full output and full reconciliation: `scripts/session29_test.py`
and `notes/session-29-check-output.txt`.

---

## 2026-09-09 — Session 30 decision: SPEC housekeeping (Reno's verdict
recorded, target-hour list consolidated to point at 3.4)

**D45. SPEC is brought up to date with Reno's now-complete result (F82) and
one long-standing staleness item flagged since session 26.** This entry
documents the four authorised edits (A-1 to A-4, the session 30 prompt) and
no others. This session made **no other SPEC edit** — no code was touched,
no model was run, and no figure in SPEC was changed except where named below.

- **A-1 (§3.4 airport table).** KRNO's stage cell changed from `2 — in
  progress` to **`2 — failed`**. Nothing else in that row changed.
- **A-2 (§5.0 results table).** A KRNO row was added: `**FAILED** (stage 2,
  365 test days) | 1.458 vs 1.414 vs 2.490`, using F82's own figures. The
  paragraph beneath the table was extended to name Reno's figures alongside
  the other four, to note that all five airports' single looks are now spent
  on the same twelve months (extending F30/F48/F65's reading one airport
  further), and to add a short paragraph stating Reno is the first airport
  not to beat raw GFS, with the near-constant-bias / overfit reading D44.12
  named in advance and confirmed by F82.
- **A-3 (§6 build order).** The Reno bullet changed from "IN PROGRESS ...
  Not yet tested" to "FAILED (tested once, F82)", with the sealed-test
  figures and verdict added after the existing rehearsal-and-lock summary,
  mirroring how the DSM and Dubbo bullets already read after their own
  passes.
- **A-4 (§4.1 "hours in use" list).** This list had named only EGLC, LFPG
  and DSM since DSM was added, and was never extended when Dubbo or Reno
  joined — flagged as stale by session 26 (open question, not acted on
  then) and left unresolved by every session since. Rather than keep
  appending one bullet per airport to a list §4.1's own opening sentence
  already says lives in the airport table (3.4), the list was replaced with
  a short "for illustration only" paragraph that keeps the two explanatory
  examples (why EGLC/LFPG and DSM differ) and names Dubbo's and Reno's hours
  and the decisions that fixed them (D37, D42), while pointing at 3.4 as the
  one place the hours themselves are recorded. No hour value changed; this
  is a presentation fix, not a data correction.

**What did not change.** Sections 5.1, 5.2 and 5.3 (the metric, the
references, and the qualitative bar itself, D22) are untouched. No edit here
adds anything a result must clear or removes anything it already had to. The
frozen bar's *meaning* is exactly what it was before this session — checked
edit by edit, the same discipline sessions 09, 15, 20 and 26 applied to
their own SPEC edits (D28, D34, D38, D43).

**One remaining staleness item, seen but not authorised to fix.** SPEC
section 1's own airport list still reads "Reno ... stage 2, in progress" —
a second place, distinct from the §3.4 table A-1 was scoped to, that also
needs "failed". The session 30 prompt authorised only A-1 to A-5; changing
section 1's prose was not one of them, so it is left as found and reported
in this session's consistency check for the owner to authorise separately,
the same discipline session 26 applied to its own out-of-scope wording
question (D43).

---

## 2026-09-09 — Session 30 finding: Q31 closed as immaterial

**F83. Q31 (whether Reno files a second scheduled report) is closed as
immaterial — not answered, because it cannot be answered from data already
on hand, and answering it would mean a new IEM pull, which is outside a
documentation-only session's scope.**

Checked before closing rather than assumed: every one of Reno's saved raw
IEM pulls (`data/raw/iem_asos_RNO_*_routine.csv` and their `.meta.txt`
files, from session 26's full six-year pull) was requested with
`report_type=3` — routine reports only. None of them requested
`report_type=4` ("special") or the combined routine-plus-special stream that
answered this same question for EGLC (F3), LFPG (F19), DSM (F36), Dubbo
(F55) and Bozeman (F72). So the data needed to answer Q31 was never pulled,
and the honest options are a new request to IEM (a new data pull, out of
this session's documentation-only scope, SPEC 2.3) or leaving it open
indefinitely.

**Closed as immaterial rather than left open, because D30 already settled
that it cannot change anything even once answered.** Nothing in the
project's pipeline uses the "special" stream as the truth observation at any
airport (D30) — the routine `:55` report is Reno's truth observation
regardless of whether a second scheduled report also exists. SPEC 3.4's
"also files at" cell for RNO keeps its honest current answer, **"not yet
checked"**, rather than being changed to a guess; "not yet checked" and
"immaterial" are two different, both-true statements, and this entry closes
only the open-question status, not the cell's wording. If a future session
ever pulls Reno's special-report stream for some other reason, the cell can
be filled in then from that real data, exactly as D28 requires — it does not
need its own dedicated session to do so.

---

## 2026-09-09 — Session 30 finding: `RESULTS.md` created (no new computation)

**F84. A standalone technical results summary, `RESULTS.md`, was written at
the project root, drawing only on SPEC's and DECISIONS's already-recorded
figures — no model was run and no figure was computed for the first time.**
Every number in it is cited to the DECISIONS finding it comes from (F16,
F30, F47, F64, F82 for the five sealed-test rows; F48, F65, F82 for the
cross-airport readings) and was checked against that finding's own text
before being written down (this session's own consistency sweep, reported
separately, is the record of that check). `RESULTS.md` is a second,
reader-facing presentation of facts SPEC and DECISIONS already hold; it does
not supersede either as the source of truth, and a disagreement between it
and its cited DECISIONS source would mean `RESULTS.md` is wrong, never the
other way round.

---


## Moved by session 38 (2026-09-12)

The archive criterion (D46, live in `DECISIONS.md`) applied to **F88** only (session 35's GFS GRIB source feasibility probe, verdict GO-COSTLY). F88's own question -- whether a deeper, credential-free GFS GRIB archive exists and is worth building -- is now settled: sessions 36-38 built the pipeline, fixed its one gap (RNO elevation, F89/F90), and used it to re-run the richer-features CV on the full v16 window (F91, live in `DECISIONS.md`), superseding F88's own cost-only verdict with a completed result. No live open question or `STATUS.md`'s own "Next" section needs F88's specific wording -- only its number, which resolves here unchanged; F89 and F90 (both still live) already restate, in their own words, the one F88 figure ("up to 4 distinct cycle/lead combinations per calendar day") they reference, so they do not depend on F88's wording surviving in `DECISIONS.md`. The block below is exactly what was cut, unedited.

---

## 2026-09-11 — Session 35 finding: GFS GRIB source feasibility probe
(availability-and-cost only, no build, no pipeline)

**F88. Verdict: GO-COSTLY.** A real, credential-free, deep GFS forecast GRIB2
archive exists and was directly confirmed to carry both needed variables
(total cloud cover, 10 m wind) back to the project's own archive floor — but
aligning it to the existing pipeline carries real, concrete costs beyond
"pull and join." Nothing was built, joined, fitted, or evaluated. No sample
came from inside the sealed test year (2025-08-01 to 2026-07-31); the two
dates sampled are 2021-03-24 (one day after the archive floor) and
2025-06-11. Full real output is `notes/session-35-check-output.txt`; every
sample file is saved untouched under `data/raw/diagnostics/session35/` with
a `.meta.txt` per file (SPEC 2.3).

**Task 1 — candidate sources, compared:**

| source | earliest forecast date found | needed variables | lead hours / cycles | access | credentials |
|---|---|---|---|---|---|
| AWS S3 `noaa-gfs-bdp-pds` (NODD) | confirmed back to at least 2021-03-24 (this session's direct probe) | yes — confirmed by inventory (Task 2) | 3-hourly to 240h, 12-hourly to 384h; 00/06/12/18z | plain HTTPS / S3 API | **none** |
| GCS mirror `global-forecast-system` | same, confirmed same date | same (idx content identical) | same | plain HTTPS | **none** |
| Azure NODD mirror | not confirmed — a guessed container/path 404'd; not pursued further once two working sources were in hand | unknown | unknown | unknown | unknown |
| NCAR GDEX (formerly RDA) `ds084.1` | 2015-01-15 onward, but **sunsetting in early 2026** — NOAA is migrating this exact historical archive onto the AWS bucket above, which is why AWS now reaches back this far | same 37-variable set, incl. surface winds and cloud, per its own page | 3-hourly to 240h, 12-hourly to 384h; 00/06/12/18z | HTTPS/THREDDS; page shows a "Sign In" option | not tested — the AWS copy is credential-free and equally deep, so this was not chased further |
| NCEI historical GFS archive | analysis from 2007; NCEI's own page states the **AWS Big Data window is "trailing 30 days"** | not confirmed at 0.25 deg — NCEI's deeper holdings are often lower-res (0.5/1 deg) | varies | HTTPS | none stated |
| NOMADS live server | rolling 2 days-2 weeks only | n/a, too recent | n/a | HTTPS | none |

**The single most important Task 1 finding is a correction of a secondary
source by direct probe** — exactly the "verify on contact" principle SPEC
3.3 already applies to Open-Meteo (F1, F17, F31, F49, F66), now shown to
matter for a GRIB source too. NCEI's own page states the AWS NODD GFS bucket
is a **"trailing 30-day window."** This session's own direct listing of
`noaa-gfs-bdp-pds` contradicts that for the specific bucket checked: files
for **2021-03-24** are present, at full 0.25 deg global resolution
(~500-550 MB each), with `LastModified` timestamps from 2021 itself — not a
30-day rolling set. This reconciles with public reporting that NOAA is
migrating the deeper NCAR-hosted historical archive (`ds084.1`, 2015-01-15
onward, itself sunsetting in early 2026) onto this same AWS bucket. The
NCEI-stated 30-day figure was very likely accurate for this bucket at some
earlier time and has since been superseded by that migration; either way,
the only fact this project can rely on is the one checked directly, not the
one read on a page.

**Task 2 — the two needed variables, confirmed present by inventory, at
both a near-floor date and a recent pre-test date:**

```
sample                                   TCDC:entire atmosphere   UGRD:10 m above ground   VGRD:10 m above ground
2021-03-24 12z, 24h fcst (valid 03-25)   present (line 636)       present (line 588)       present (line 589)
2025-06-11 12z, 24h fcst (valid 06-12)   present (line 636)       present (line 588)       present (line 589)
```

Identical variable name, level string, forecast-step label, and even line
position in the inventory at both dates — no drift observed between them.
**Confirmed genuinely decodable, not merely labeled**: for the 2025-06-11
sample, the three messages' exact byte ranges (from the `.idx` offsets) were
pulled with a single HTTP Range request each — no full-file download, no
GRIB decode library — and each extracted message starts with the GRIB2
magic marker (`GRIB`) and ends with the required `7777` end marker, i.e.
each is a complete, well-formed GRIB2 record. Message sizes: TCDC 829,229 B,
UGRD 984,341 B, VGRD 961,389 B — each about 0.15-0.2% of the ~514-550 MB
whole multi-variable file, which is itself the key fact behind the volume
estimate in Task 3.

**Task 3 — alignment cost, the part that decides "worth it":**

**1. Grid-to-point mismatch (new, not previously quantified).** The public
`pgrb2.0p25` product is a plain **regular** 0.25 deg lat/lon grid — every
grid point is an exact multiple of 0.25 deg. Checked against that, **none of
the five grid points already recorded in SPEC 3.4 land on that grid**: every
airport's grid latitude sits 0.013-0.038 deg off the nearest 0.25 deg
multiple, and two of the five longitudes (YSDU, RNO) land on a *different*
clean fraction each (1/32 deg at YSDU, 1/64 deg at RNO) rather than on 0.25
deg — the signature of a native or reduced grid whose spacing varies with
latitude, not of the plain regular output grid Open-Meteo's own point
happens to be drawn from. Concretely, this means a raw-GRIB cloud/wind value
read at "the GFS grid point" would come from a **different physical
location** than the one already baked into the existing temperature column
— a second, compounding offset on top of the grid-to-airport offset SPEC 3.4
already documents and accepts as immaterial. This second offset has not
been measured and is not assumed away here; a real build would need to
either interpolate to the exact same point Open-Meteo already uses (method
unconfirmed) or accept an unquantified new discrepancy.

**2. Lead-time/cycle bookkeeping does not reduce to "always use f024."**
SPEC 3.2 already records that Open-Meteo's `previous_day1` is not a clean
fixed 24h lead — it sweeps roughly 24-30h across the day because GFS cycles
only exist every 6 hours (00/06/12/18z) and Open-Meteo stitches hours 24-29
of each cycle together. The same constraint binds a raw-GRIB build. EGLC/
LFPG's 12:00 UTC target and DSM's 18:00 UTC target coincide with standard
cycle hours, so a clean same-cycle `f024` is available for those. **YSDU's
02:00 UTC and RNO's 20:00 UTC targets do not coincide with any standard
cycle hour**, so no single cycle offers an exact 24h lead to either — the
identical reason Open-Meteo's own lead sweeps off 24h. Reproducing Open-
Meteo's exact per-hour cycle/lead choice (the archived F5 finding, not
re-derived this session) or deliberately adopting a different, simpler
convention is a real design decision a build would have to make and record
— it is not automatic.

**3. Volume/time (measured, not modeled).** One cycle+lead pull needs 3
messages (TCDC + UGRD + VGRD) at ~0.8-1.0 MB each (~2.8 MB total),
regardless of how many airports read it, because each message is a global
field. But because the five airports' target hours differ (12:00, 12:00,
18:00, 02:00, 20:00 UTC), **up to 4 distinct cycle/lead combinations are
needed per calendar day**, not 1. Order of magnitude across the ~4.3-year
training window (~1,570 days): roughly 4 `.idx` fetches + 12 range-GETs per
day, ~17 GB of message data and **~25,000 HTTP requests** in total. This is
a materially larger and more custom engineering surface than the existing
pipeline's one-JSON-call-per-airport-per-pull Open-Meteo method (SPEC 3.2),
and it requires a GRIB2 decoder this project's environment does not
currently have (`wgrib2` not found; `pygrib`/`cfgrib` not installed —
checked, not assumed) on top of the interpolation and lead-time logic in
points 1-2.

**4. Failure modes, named but not resolved.** Only two single dates were
checked, both after GFS's FV3-based "v16" implementation (2021-03-22) — so
both sit inside the same model-version family as the project's entire
archive window, which is reassuring but does not rule out a later
sub-version physics update (e.g., a mid-2023 package change) silently
renaming a level or altering packing somewhere in 2021-2025; this was not
scanned. Whether the AWS archive carries its own gaps analogous to Open-
Meteo's known 492-hour gap (SPEC 3.2) is unknown and would need a bulk date
scan this probe deliberately did not do.

**One-paragraph verdict (Task 4), flagged for the owner and not decided
here.** **GO-COSTLY.** The two variables genuinely exist, credential-free,
on two independent clouds, confirmed by both inventory label and a real
decoded-message check, reaching back to (at least) this project's own
2021-03-24 archive floor — so the doubt session 33 raised, "is a deeper GFS
GRIB source even available," is answered **yes**. But the alignment lift is
real and stacks: an unquantified new grid-to-point offset beyond the one
already accepted in SPEC 3.4, a lead-time/cycle-bookkeeping problem this
project has not solved even for two of its five existing airports, a new
GRIB2-decoding dependency absent from this environment today, and an
order-of-magnitude ~17 GB / ~25,000-request pull-and-join effort across five
airports and ~4.3 years — clearly more engineering than any prior
data-acquisition session in this project undertook. **The build-vs-lock
choice — build this GRIB pipeline to unlock the full ~4.3-year richer-
feature window, or lock the richer method on the existing ~1.5-year window
and carry LFPG's caveat (F87) — is the owner's, not decided here.**

**What this session did not do, on purpose.** No full `.grib2` file was
downloaded (only three single-message byte ranges, each under 1 MB). No
decode library was installed. No date range was scanned — only the two
single dates named above, both outside the sealed test year. No join, fit,
model, or evaluation of any kind was performed. `SPEC.md` and `RESULTS.md`
were not modified. Nothing was committed.

---

## Moved by session 45 (2026-09-12)

The archive criterion (D46, live in `DECISIONS.md`) applied to the GRIB-build sub-project's own evidence base and its lock: **F85, F86, F87, F89, F90, F91, F92, F93, and D48**. Every one of these entries is settled -- each conclusion is fixed and will not change -- and each one's headline is already carried forward into `SPEC.md` section 7 and `RESULTS.md` section 5, so no live open question or `STATUS.md`'s own "Next" section needs any of their specific wording, only their numbers, which resolve here unchanged. F88 (session 35's own feasibility probe) was already archived in session 38. **F94** (session 42's sealed-test result) meets the same criterion but is deliberately NOT moved this session -- it is flagged instead, in this session's own manifest (`docs/session-45.md`), because it is the headline result and very fresh; it stays live in `DECISIONS.md` pending the owner's own call. D47 (the raw-data-policy standing rule) sat inside the same session-37 entry as F90; it is split out and kept live, unmoved, for the same reason D15 stays live -- it governs future pulls, not a settled finding. D49 and F95 (the consolidation records themselves) also stay live, as fresh material `STATUS.md` still references directly. The blocks below are exactly what was cut, unedited.

---

## 2026-09-11 — Session 31 finding: data-availability probe for the
richer-features phase (confirms and extends F7/D17)

**F85. Three findings, all from data-availability probes only — nothing was
joined, built, fitted or evaluated this session, and every probe date is
outside the sealed test year (SPEC 3.3, from-Dubbo-onward convention,
F49).** The scripts are `scripts/session31_pull.py` and
`scripts/session31_checks.py`; the full real output is
`notes/session-31-check-output.txt` and the pull log is
`notes/session-31-pull-output.txt`. Every response is saved untouched under
`data/raw/diagnostics/session31/` (38 JSON files, each with a `.meta.txt`
recording the exact query URL and UTC pull time, SPEC 2.3).

**1. Cloud cover and wind speed's first real hour is pinned exactly, and it
matches the shared archive gap's end hour to the minute — at all five
airports, not just EGLC.**

Bracketing 2023-12-20 to 2024-02-01 at EGLC (`cloud_cover_previous_day1`,
`wind_speed_10m_previous_day1`, plus `dew_point_2m_previous_day1` and
`relative_humidity_2m_previous_day1` co-probed in the same request, free):

```
variable                  present   null   first real hour
cloud_cover                    324    732   2024-01-19T12:00
wind_speed_10m                 324    732   2024-01-19T12:00
dew_point_2m                   324    732   2024-01-19T12:00
relative_humidity_2m           324    732   2024-01-19T12:00
```

**All four start at the exact same hour, and that hour is exactly one hour
after the shared 492-hour forecast-gap's last missing hour** (2023-12-30
00:00 to 2024-01-19 11:00 UTC — F8, F22, F38, F57, F75). This confirms D17's
hypothesis (which F7 had only dated to "absent 2023-07-01, present
2024-07-01") down to the hour: these variables do not merely become
available "sometime in early 2024" independently of the forecast-gap — they
switch on at precisely the hour the main temperature series resumes after
the shared archive gap, which reads as one underlying cause (a change in
what Open-Meteo's build process retained) rather than two coincidental
ones.

A targeted check a few days either side of that hour (2024-01-14 to
2024-01-24, not a full re-scan) at the other four airports found the
identical hour, with no variation:

```
station   cloud_cover   wind_speed_10m   dew_point_2m   relative_humidity_2m
LFPG      2024-01-19T12:00  (same, all four)
DSM       2024-01-19T12:00  (same, all four)
YSDU      2024-01-19T12:00  (same, all four)
RNO       2024-01-19T12:00  (same, all four)
```

**Five airports on three continents now share this start hour exactly**,
the same shape the archive floor (F1/F20/F33/F51/F68) and the 492-hour gap
itself (F8/F22/F38/F57/F75) already showed: a property of the Open-Meteo
archive build, not of any one place. `dew_point_2m` and
`relative_humidity_2m` — wave-two features, informational only this phase,
gating nothing — share the identical start hour at every airport too.

**2. Upper-air (925/850 hPa) temperature: NOT free in any form this project
could safely use. Verdict: effectively (c) separate-source — not merely a
recency floor the way cloud/wind is, but a variable class the
previous-day-offset mechanism does not implement at all on this endpoint.**

The variable string was genuinely uncertain, so four spellings were tried at
EGLC (recent window, 2025-06-15/16), each its own request so one bad
spelling could not take a good one down with it. All four were HTTP-rejected
with the **same** verbatim reason, differing only in the variable name
quoted back:

```
temperature_925hPa_previous_day1  -> REJECTED: "Invalid value: Cannot
    initialize SurfacePressureAndHeightVariable<VariableAndPreviousDay,
    VariableOrSpread<ForecastPressureVariable>, ForecastHeightVariable>
    from invalid String value temperature_925hPa_previous_day1"
temperature_850hPa_previous_day1  -> REJECTED, same shape
temperature_925hpa_previous_day1  -> REJECTED, same shape (lowercase 'hpa')
temperature_925HPA_previous_day1  -> REJECTED, same shape (uppercase 'HPA')
temperature_925mb_previous_day1   -> REJECTED, same shape ('mb' suffix)
```

**The identical error class across every casing and unit variant was the
clue that the offset suffix itself, not the spelling, was the problem — so
two follow-up probes isolated that directly, and confirmed it:**

```
temperature_925hPa                (bare, no offset)  -> ACCEPTED,
    48/48 present, real values, grid EXACTLY matches EGLC's established
    gfs_global grid point (51.487137, 0.0, 4.0 m — F17/session 08)
temperature_925hPa_previous_day0  (explicit day-0)    -> REJECTED, same
    verbatim error as every _previous_day1 spelling above
```

**Read together: pressure-level ("upper-air") temperature exists on this
endpoint only in its bare, current-run form — the `_previous_dayN` offset
mechanism this whole project depends on for leakage safety (SPEC 2.1b) does
not parse for this variable class at all, not even at day 0.** The bare form
is exactly the freshest-run series D17 already named as the leakage trap
for plain `temperature_2m` ("On this endpoint it is the freshest-run
series, which is the leakage trap SPEC 2.1b warns about" — D17's own words,
quoted in `scripts/session25_pull.py`'s own comments): using it as a
training feature would mean seeing information from at or after the run
time, not a genuine day-ahead forecast. **So there is no way to pull a
leakage-safe upper-air forecast from this endpoint at all, at any date.**

This also answers the prompt's specific ask about reach: **the "how far
back does it reach" question does not apply, because the offset-based
series does not exist to have a start date.** The same rejection was
returned at all four date-ladder points (2021-03-24, 2023-07-01,
2024-07-01, 2025-06-10..12) at **all five airports**, EGLC included — this
is not a case of upper-air reaching further back than cloud/wind (or less
far); it is categorically unavailable via the mechanism cloud/wind uses,
regardless of date.

**DSM and RNO specifically, per the prompt's ask.** The bare (no-offset,
current-run) form was also pulled at both CONUS airports, and in both cases
the grid point returned is **exactly** the airport's already-established
`gfs_global` grid point — DSM 41.52945/-93.63281/285.0 m (F31), RNO
39.537918/-119.765625/1344.0 m (F66) — confirming genuinely GFS, not a
silent CONUS-model swap of the kind F40/F69 found for `gfs_seamless`, even
in this current-run-only form. This is offered only for completeness: since
the bare form cannot be used without reintroducing leakage, the "genuinely
GFS" confirmation does not make it usable.

**One-line verdict: (c), separate-source — a genuine day-ahead upper-air
forecast is not obtainable from this API/offset at all; getting one would
need a different mechanism (the project's own forward daily archival of
live runs, or a genuine historical-model-run source with real
initialization timestamps), which is a real second-source engineering
lift, not a free addition alongside cloud/wind.**

**3. Five-airport availability table, recent pre-test anchor
(2025-06-10 to 2025-06-12, `previous_day1`, all present/null counts, nothing
filled — SPEC 2.2):**

```
variable                          EGLC          LFPG           DSM          YSDU           RNO
temperature_2m                  72p/0n        72p/0n        72p/0n        72p/0n        72p/0n
cloud_cover                     72p/0n        72p/0n        72p/0n        72p/0n        72p/0n
wind_speed_10m                  72p/0n        72p/0n        72p/0n        72p/0n        72p/0n
dew_point_2m                    72p/0n        72p/0n        72p/0n        72p/0n        72p/0n
relative_humidity_2m            72p/0n        72p/0n        72p/0n        72p/0n        72p/0n
temperature_925hPa            REJECTED      REJECTED      REJECTED      REJECTED      REJECTED
temperature_850hPa            REJECTED      REJECTED      REJECTED      REJECTED      REJECTED
```

Every wave-one and wave-two variable is fully present at all five airports
at this recent anchor — no nulls, no drops. Upper-air is uniformly rejected
everywhere, consistent with finding 2 above: this is not a per-airport gap,
it is the endpoint's own grammar.

**A question for the owner, raised rather than decided (session 31 scope
forbids deciding the richer-features design).** F81 named cloud cover,
wind and a genuine terrain descriptor as the kind of information that might
help at Reno. This session's finding narrows that: cloud cover and wind
speed (plus dew point and relative humidity) are genuinely free from
2024-01-19 12:00 UTC onward at every airport, which means any model using
them needs a **two-tier training window** — a shorter window
(2024-01-19 onward) with the richer features, alongside (or instead of) the
existing full window without them — exactly the shape D17 already
anticipated for stage 1's rejected extra variables, now confirmed to apply
project-wide. **Upper-air temperature is not available in any leakage-safe
form at all**, so it is not a candidate for that two-tier design; if the
owner still wants terrain-descriptive information at Reno, this session's
finding suggests either restricting richer features to the wave-one/
wave-two set with a two-tier window, or a genuinely separate upper-air
source (its own engineering project), or a static terrain-mismatch feature
computed once from station/grid metadata already on hand (elevation
difference, distance — no new pull needed). **Nothing about this was
decided or acted on here** — it is the owner's design choice for the
richer-features planning session (STATUS's stated next step).

**What this session did not do, on purpose.** No feature matrix, model,
join, MAE or corrected forecast of any kind was built. No airport's test
year was touched — every probe date used is 2021-03-24, 2023-07-01,
2024-07-01, 2024-01-14 to 2024-01-24, or 2025-06-10 to 2025-06-12, all
`<=` 2025-07-31. `SPEC.md` and `RESULTS.md` were not modified. Nothing was
committed.

---

## 2026-09-11 — Session 32 finding: richer-features scout (validation-year
only, sealed test NOT opened)

**F86. The scout: a two-tier same-window comparison of a 3-feature and a
5-feature (+ cloud_cover, wind_speed_10m) model, fitted on an identical short
inner-training window at all five airports, judged once on the validation
year. Five features beat three at 3 of 5 airports; five features beat raw GFS
at only 2 of 5; and the short window itself — not the extra features — is the
dominant effect almost everywhere.** No recipe was locked, and the sealed
test year (2025-08-01 to 2026-07-31) was not opened, pulled or evaluated at
any airport — this session's own scripts assert every loaded date is
`< 2025-08-01` before anything is fitted. The scripts are
`scripts/session32_pull.py` (the new raw pull) and
`scripts/session32_scout.py` (the join and the ladder); the full real output
is `notes/session-32-check-output.txt`.

**The design, exactly as the session prompt fixed it in advance.** Because
cloud_cover and wind_speed_10m are free only from 2024-01-19 12:00 UTC onward
at every airport (F85), both models are fitted on the identical short window
**2024-01-19 to 2024-07-31** (~6 months) and judged on the identical
**2024-08-01 to 2025-07-31** validation year — the same validation year every
earlier rehearsal used (D18), so raw GFS's own MAE on it should, and does,
reproduce each airport's already-published validation figure exactly (cross-
check below). The existing locked 3-feature model's validation figures (F15,
F29, F45, F62, F80) were deliberately **not** reused as the comparison — a
fresh 3-feature model was refitted on the same short window as the 5-feature
model, so any difference between the two rungs is attributable to the two
extra features alone, not to a confound with window length. Both models use
the identical locked LightGBM settings (D21.4); nothing was tuned.

**Pull and join (Task 1).** `cloud_cover_previous_day1` and
`wind_speed_10m_previous_day1` were pulled at all five airports over
2024-01-19 to 2025-07-31 (one request per airport, `models=gfs_global`
per D16), saved under `data/raw/features/` with `.meta.txt` provenance. Every
file's first 12 hours (2024-01-19 00:00–11:00 UTC) are null, matching F85's
finding to the hour; nothing else in either pulled series is null at any
airport. Joined to the existing temperature+observation rows at each
airport's own target hour (SPEC 4.5, D14), drop-and-count, nothing filled
(SPEC 2.2):

```
airport  inner rows kept   valid rows kept   scored (common) days
EGLC     195 of 195        364 of 365        363
LFPG     195 of 195        365 of 365        365
DSM      195 of 195        365 of 365        365
YSDU     191 of 195        360 of 365        355
RNO      194 of 195        365 of 365        365
```

Every drop reconciles against facts already on record: EGLC's one validation
drop is its known missing 2024-08-15 observation (F12/F16's pattern); Dubbo's
larger drop count (4 inner, 5 validation) reproduces F58/F59's known higher
off-hour/no-report rate exactly — all five of its persistence-losing
"yesterday" dates match F59's own whole-period list of named validation-year
losses (four no-report dates, 2024-09-18/2024-11-17/2024-11-27/2025-07-22,
and the one off-hour date, 2025-03-08) — and its forecast-null day lands on
2024-01-19 (the one day Dubbo's 02:00 UTC target still sits inside both the
shared archive gap and cloud/wind's own not-yet-real window, per F59's
"Dubbo loses one more day than the other four" finding); Reno's and DSM's
near-zero drop counts match F41's and F77's own clean observation records. **As a correctness check, not
a result**: every airport's raw-GFS and common-day count on this validation
year matches its own already-published rehearsal figure to three decimals —
EGLC 1.239 (F15), LFPG 1.426 (F29), DSM 1.748 (F45), YSDU 1.397/355 days
(F62), RNO 1.493 (F80) — confirming the loader reproduces known behaviour
rather than introducing a new one.

**Task 2 — the ladder, validation-year MAE and skill vs raw GFS (skill =
1 − model/rawGFS):**

```
airport  Raw GFS  +mean-bias  3-feat(short)  5-feat(richer)  Persistence
EGLC      1.239    1.241 (-0.2%)  1.322 (-6.7%)   1.147 (+7.4%)   2.226
LFPG      1.426    1.648 (-15.5%) 1.793 (-25.7%)  1.618 (-13.5%)  2.523
DSM       1.748    2.352 (-34.6%) 1.976 (-13.0%)  2.021 (-15.6%)  4.108
YSDU      1.397    1.335 (+4.4%)  1.317 (+5.8%)   1.294 (+7.4%)   2.577
RNO       1.493    1.677 (-12.3%) 1.600 (-7.2%)   1.642 (-10.0%)  2.756
```

**The headline that matters most, and it is not about cloud or wind: the
freshly-refitted 3-feature (short) model loses to raw GFS at 4 of 5
airports — EGLC, LFPG, DSM and RNO — and the mean-bias reference, fitted on
the same six months, loses to raw GFS everywhere except YSDU.** This is the
short window itself, not the richer features: the existing locked 3-feature
model at the same five airports, fitted on the full 2021–2024 window, beats
raw GFS comfortably everywhere (F15, F29, F45, F62, F80 all show a positive
margin on this same validation year). The likely mechanism is stated plainly
because the session prompt's own design makes it checkable: **the short
window (2024-01-19 to 2024-07-31) contains not a single day from August
through December** — half the calendar year, including the exact months
(August–December 2024) that open the validation year — so `season_sin`/
`season_cos` splits are fitted with no example anywhere near several months
of the validation set's own bias structure (F13/F28/F43/F61/F79 each found a
airport-specific seasonal bias shape). This is a property of the ~6-month
window the session prompt fixed in advance (deliberately thin, stated as
such), not a defect in this session's join or fitting code.

**Does 5-feature beat 3-feature (short), the comparison this scout was built
to isolate? Yes, at 3 of 5 airports — EGLC, LFPG, YSDU — no at DSM and RNO.**

```
airport  3-feat MAE  5-feat MAE  5 beats 3?  change   in-sample gap (3-feat / 5-feat)
EGLC       1.322       1.147       YES      -0.175      +0.364 / +0.290
LFPG       1.793       1.618       YES      -0.175      +0.737 / +0.625
DSM        1.976       2.021       no       +0.045      +0.657 / +0.754
YSDU       1.317       1.294       YES      -0.023      +0.269 / +0.294
RNO        1.600       1.642       no       +0.042      +0.722 / +0.787
```

**At EGLC, LFPG and YSDU the extra features improve BOTH the in-sample fit
and the validation score together** — in-sample MAE fell and validation MAE
fell at the same three airports, which is the shape of genuinely learned
structure, not noise-fitting. **At DSM and RNO the extra features improve
the in-sample fit but WORSEN the validation score** — the in-sample gap widens
at both (DSM +0.657 to +0.754, RNO +0.722 to +0.787) while the model that
looked better on training data did worse on unseen data. That is the
overfitting shape Task 3 was built to catch, and it appears at exactly the
two airports where the extra features do not help: cloud cover and wind
speed give the model more ways to fit the ~195-day training sample without
adding real signal for those two airports' own bias structure.

**5-feature beats raw GFS at only 2 of 5 airports — EGLC (+7.4%) and YSDU
(+7.4%) — the same two airports where the short-window handicap above was
weakest to begin with** (YSDU's mean-bias reference already beat raw GFS on
this window, +4.4%; EGLC's short-window 3-feature loss to raw GFS was the
smallest of the four losing airports, -6.7%). At LFPG, DSM and RNO the
5-feature model does not close the gap the short window itself opened.

**Reno specifically (the session prompt's named question).** 3-feature
(short) MAE 1.600, 5-feature (richer) MAE 1.642 — cloud/wind made Reno's
correction slightly **worse**, not better, on this window. The 5-feature
model's own gain shares (cloud_cover 18.5%, wind_speed_10m 17.3%) show the
tree did lean on both new features rather than ignoring them, but leaning on
them here reads as the overfitting shape above (Reno's in-sample gap widened
from +0.722 to +0.787) rather than as captured structure. As the session
prompt itself anticipated, a null result at Reno is not a surprising one:
Reno's target is local noon, and the clear-calm cold-pool / downslope
mechanism cloud and wind would be expected to capture is largely a
nocturnal effect this target hour does not see. **This scout gives no
positive evidence that cloud cover and wind speed are the missing structure
at Reno specifically** — it neither confirms nor rules out F81's
richer-features hypothesis for Reno, because the short window's own handicap
dominates the result there.

**Overall: 5-feature beats 3-feature (short) at 3 of 5 airports; 5-feature
beats raw GFS at 2 of 5 airports.** Read together with the short-window
finding above, the honest summary is that this scout's design confounds two
things it was built to separate cleanly at the airport level even though it
separates them cleanly at the rung level: the two-tier same-window
comparison does correctly isolate the marginal effect of the two extra
features from window length (that comparison is 3-feat-short vs 5-feat-short,
both on identical data), and on that comparison the richer features help at
three airports and hurt two. But because the ~6-month window itself is
severely handicapped by missing half the calendar year, **neither rung is a
fair stand-in for what a full-window richer-feature model would score**, and
the "beats raw GFS" column mostly reports how much of the short-window
handicap each airport's own bias shape happened to absorb, not how good the
richer features are in absolute terms.

**Flagged for the owner, not decided here, per the session prompt:**

**(a) Go/no-go on a full locked sealed-test cycle for the richer features.**
This scout give a genuine, if noisy, marginal-effect signal (5-feature beats
3-feature-short at 3 of 5 airports, with a real in-sample/validation
improvement at those three and a real overfitting signature at the other
two) but says little about how a richer-feature model would perform if
fitted on the full available window instead of six months — because the
richer features are only available from 2024-01-19 onward, "the full
available window" for a richer model is itself capped at about 1.5 years
(2024-01-19 to 2025-07-31 inner-training-plus-validation), not the ~4.3-year
window the locked recipe uses. Whether that longer-but-still-short window is
enough to fix the seasonal-coverage problem above, and whether the
marginal 3-of-5 win is worth a full lock-and-test cycle at all, is the
owner's call.

**(b) Whether the result justifies chasing a deeper cloud/wind source.**
F85 already established that a real GFS GRIB archive (not reanalysis, which
would leak per SPEC 2.1b) is the only way to get cloud/wind further back than
2024-01-19. This scout's own finding — that the dominant effect in every
number above is the short window, not the two features — is itself an
argument for what such a deeper source would actually buy: it would let a
richer-feature model train on the same multi-year window the locked recipe
uses, removing the seasonal-coverage confound this scout could not avoid,
rather than merely adding two columns to a six-month sample.

**What this session did not do, on purpose.** No recipe was locked (session
32 scope forbids it). The sealed test year was not opened, pulled, joined,
fitted on, or printed at any airport — `scripts/session32_scout.py` asserts
this at load time for both the forecast and the observation series, at every
airport, and the only new raw pull (`scripts/session32_pull.py`) requests
2024-01-19 to 2025-07-31 only. No hyperparameter was tuned and no feature was
hand-picked per airport — the same five features and the same LightGBM
settings were used everywhere. `SPEC.md` and `RESULTS.md` were not modified.
Nothing was committed.

---

## 2026-09-11 — Session 33 finding: seasonal blocked cross-validation on the
1.5-year window (sealed test year NOT opened)

**F87. Blocked six-fold cross-validation across the full feature-complete
window shows the session-32 scout's losses were mostly the short window, not
the recipe: with a full seasonal cycle in training, 3-feature beats raw GFS
at 4 of 5 airports (against 1 of 5 on the scout's 6-month window), and
5-feature beats 3-feature at 4 of 5 and beats raw GFS at 4 of 5. This is a
diagnostic inside the training window only — no recipe was locked and the
sealed test year (2025-08-01 to 2026-07-31) was never loaded, joined, or
scored, for any airport or fold.** The script is `scripts/session33_cv.py`
and the full real output is `notes/session-33-check-output.txt`. No new raw
was pulled — this reuses session 32's cloud/wind pull
(`data/raw/features/`) and the existing temperature/observation chunks
under `data/raw/`.

**The design, exactly as the session prompt fixed it.** Window
2024-01-19 to 2025-07-31 (~18 months, feature-complete at every airport,
DECISIONS F85), split into six contiguous ~3-month calendar blocks (not
named seasons, so the scheme is hemisphere-agnostic and works uniformly at
Dubbo):

```
block  dates
A      2024-01-19 -> 2024-04-18
B      2024-04-19 -> 2024-07-18
C      2024-07-19 -> 2024-10-18
D      2024-10-19 -> 2025-01-18
E      2025-01-19 -> 2025-04-18
F      2025-04-19 -> 2025-07-31   (longer, to reach the window's own end)
```

Each of six folds holds out one block and trains on the other five (~15
months, spanning every calendar month at least once). Four rungs at every
fold: **raw GFS** (no fit), **+ mean-bias** (fit on that fold's training
blocks only), **3-feature** (`forecast_temp_c`, `season_sin`, `season_cos`),
**5-feature** (+ `cloud_cover`, `wind_speed_10m`) — identical locked
LightGBM settings for both fitted models at every fold (D21.4: `objective=
regression_l1, n_estimators=300, learning_rate=0.05, num_leaves=15,
min_child_samples=40, random_state=42, deterministic=True, n_jobs=1`),
nothing tuned, no per-airport feature selection. Persistence is reported for
context only — it needs no fitting and was not part of the CV ladder.

**Leakage-safety justification for blocked CV, recorded here as the session
prompt required.** Blocked leave-one-block-out CV trains on data temporally
surrounding each held-out block, which departs from the strict
train-earlier/test-later split the sealed test uses (SPEC 2.1a). That is
acceptable for this diagnostic, and only because no feature carries temporal
memory: every feature is a same-day GFS forecast value (`forecast_temp_c`,
`cloud_cover`, `wind_speed_10m`, all `_previous_day1`) or a calendar-position
encoding (`season_sin`/`season_cos`), so a training row dated after a
held-out block cannot encode that block's outcome — there is no
autoregressive or lagged channel to leak through, and none was added (the
session prompt's own hard rule). The sealed test remains strictly
train-past-only; this CV is an internal generalization estimate, not that
test.

**Task 1 — row counts and drop counts, whole 1.5-year window, all five
airports.** Every day in the window is `no forecast row` / `forecast null` /
`no cloud+wind row` / `cloud null` / `wind null` / `no usable observation` or
is kept; a day can trigger more than one cause, dropped once.

```
airport   window days   rows kept   dropped   rows per block (A..F)
EGLC            560          559         1     91, 91, 91, 92, 90, 104
LFPG            560          560         0     91, 91, 92, 92, 90, 104
DSM             560          560         0     91, 91, 92, 92, 90, 104
YSDU            560          551         9     89, 90, 90, 90, 89, 103
RNO             560          559         1     90, 91, 92, 92, 90, 104
```

EGLC's one drop and RNO's one drop are both a missing observation. YSDU
(Dubbo) loses the most — 1 null forecast, 1 null cloud, 1 null wind, and 8
"no usable observation" (of which 3 are off-hour reports dropped by D14) —
reproducing F58's already-published finding that Dubbo's own observation
record carries the highest off-hour and real-gap rate of the five airports.
LFPG and DSM lose nothing at all in this window, matching their own clean
records (F23/F39-adjacent). Nothing was filled (SPEC 2.2).

**Task 2 — pooled out-of-fold MAE and skill vs raw GFS (the headline
number, every day held out exactly once):**

```
airport   Raw GFS   +mean-bias      3-feature      5-feature   n days
EGLC        1.204   1.219 (-1.2%)   1.191 (+1.2%)  1.098 (+8.8%)   559
LFPG        1.405   1.440 (-2.5%)   1.513 (-7.7%)  1.434 (-2.1%)   560
DSM         1.882   1.980 (-5.2%)   1.811 (+3.8%)  1.784 (+5.2%)   560
YSDU        1.365   1.347 (+1.4%)   1.278 (+6.4%)  1.284 (+5.9%)   551
RNO         1.423   1.411 (+0.8%)   1.369 (+3.8%)  1.318 (+7.3%)   559
```

Persistence, for context only (its own common subset, dropped where no
previous-day observation exists in the window): EGLC 2.189 (n=557), LFPG
2.501 (n=559), DSM 4.080 (n=559), YSDU 2.442 (n=543), RNO 2.699 (n=557) — the
same shape every earlier session found (persistence far weaker than raw GFS
at DSM and RNO, closer at the European airports).

**Per-fold MAE, all four rungs, so fold-to-fold variance is visible (does
the recipe win in some seasons and lose in others):**

```
EGLC     A       B       C       D       E       F
Raw GFS  0.915   1.346   1.256   1.099   1.066   1.502
+meanbi  1.072   1.320   1.228   1.104   1.081   1.474
3-feat   0.932   1.344   1.123   1.329   1.113   1.286
5-feat   0.807   1.248   1.106   1.084   1.042   1.275

LFPG     A       B       C       D       E       F
Raw GFS  1.198   1.529   1.191   1.642   1.434   1.431
+meanbi  1.269   1.614   1.202   1.689   1.434   1.431
3-feat   1.253   1.408   1.457   1.858   1.481   1.602
5-feat   1.229   1.383   1.455   1.590   1.429   1.505

DSM      A       B       C       D       E       F
Raw GFS  1.614   2.637   2.018   1.763   1.673   1.624
+meanbi  1.575   2.759   2.204   2.137   1.672   1.580
3-feat   1.425   2.104   1.818   1.890   1.469   2.113
5-feat   1.535   1.946   1.780   1.910   1.504   1.997

YSDU     A       B       C       D       E       F
Raw GFS  1.308   1.287   1.280   1.722   1.407   1.211
+meanbi  1.206   1.314   1.188   1.596   1.517   1.270
3-feat   1.291   1.262   1.149   1.304   1.505   1.174
5-feat   1.380   1.236   1.134   1.259   1.568   1.151

RNO      A       B       C       D       E       F
Raw GFS  1.593   1.016   0.969   2.244   1.885   0.908
+meanbi  1.515   0.895   1.094   2.369   1.784   0.883
3-feat   1.331   0.943   1.018   2.207   1.693   1.063
5-feat   1.341   0.875   1.050   2.047   1.614   1.025
```

Every airport wins in some blocks and loses in others — the recipe is not
uniformly better or worse across the calendar, which is exactly what a full
seasonal cycle in training was meant to expose rather than hide. LFPG is the
one airport where 3-feature loses to raw GFS in four of its six blocks (B,
C, D, E all worse or roughly flat), which is what drags its pooled figure
below raw GFS despite winning blocks A and, on 5-feature, most others.

**Task 3 — the overfit diagnostic (pooled in-sample, training-fold, MAE vs
pooled out-of-fold MAE):**

```
airport   3-feat in-sample   3-feat OOF   gap      5-feat in-sample   5-feat OOF   gap
EGLC            0.907           1.191   +0.284           0.784           1.098   +0.314
LFPG            1.021           1.513   +0.492           0.920           1.434   +0.513
DSM             1.151           1.811   +0.660           1.040           1.784   +0.744
YSDU            1.002           1.278   +0.276           0.931           1.284   +0.353
RNO             1.031           1.369   +0.338           0.918           1.318   +0.400
```

("in-sample, pooled" concatenates the training-fold predictions from all six
folds — each row appears in five of six folds' training sets — so it is not
a per-row figure but a pooled diagnostic, as the session prompt asked.) A
positive gap at every airport, for both models, is the ordinary signature of
a flexible tree model fitting its own training fold more tightly than it
generalises — expected, not alarming, given ~15 months of training data per
fold. The 5-feature gap is consistently a little larger than the 3-feature
gap (more features, slightly more capacity to fit training-fold noise), at
every airport, which is the same overfitting shape session 32's scout
already flagged on a much shorter window — smaller here, not absent.

**5-feature importances, averaged across the six per-fold models:**

```
airport   forecast_temp_c   season_sin   season_cos   cloud_cover   wind_speed_10m
EGLC            24.5%           19.9%        16.0%         14.6%           25.0%
LFPG            23.2%           24.3%        20.0%         12.7%           19.8%
DSM             25.4%           28.3%        22.1%          9.7%           14.6%
YSDU            23.9%           24.2%        19.0%          9.2%           23.7%
RNO             20.1%           25.7%        21.2%          9.1%           23.9%
```

Nothing is ignored and nothing dominates at any airport. `wind_speed_10m`
carries a larger gain share than `cloud_cover` at every airport, most
sharply at DSM and RNO (roughly 1.5–2.5x), which is consistent with F86's
own reading that the scout's marginal 5-feature gains leaned on both
features rather than either alone.

**Task 4 — the two branch reads, reported and not decided, exactly as the
session prompt required.**

**Branch A — is the window adequate?** Trained on a full seasonal cycle,
**3-feature beats raw GFS at 4 of 5 airports** (EGLC +1.2%, DSM +3.8%, YSDU
+6.4%, RNO +3.8%) **— only LFPG still loses (-7.7%).** This is a clear
recovery from the scout's 6-month window, where the freshly-refitted
3-feature model lost to raw GFS at 4 of 5 airports (EGLC, LFPG, DSM, RNO —
F86) and beat it only at YSDU. The read: **the proven recipe does recover to
beating raw GFS once the training data spans a full calendar cycle, at
every airport except LFPG.** LFPG's own loss is not explained by anything
this diagnostic measured further — its per-fold table shows the 3-feature
model losing in four of its six blocks, not one bad block dragging an
otherwise-good average.

**Branch B — do the features add real out-of-sample value?** **5-feature
beats 3-feature out-of-fold at 4 of 5 airports** (all but YSDU, where the two
are within 0.006 degC of each other) **and beats raw GFS at 4 of 5 airports**
(all but LFPG, where it narrows the 3-feature loss from -7.7% to -2.1% but
does not close it). This firms up the scout's 3-of-5 marginal-improvement
signal (F86) across six held-out blocks rather than one held-out year, at a
similar 4-of-5 hit rate on the raw-GFS comparison specifically. Reno
specifically: 5-feature (1.318) beats both 3-feature (1.369, +3.8% skill)
and raw GFS (1.423, +7.3% skill) — a real, if modest, positive signal that
did not clearly appear in the scout's own short-window read of Reno
(F86 found cloud/wind made Reno's short-window correction slightly worse,
not better). `wind_speed_10m`'s gain share at Reno (23.9%) is the largest of
any single non-`forecast_temp_c`-or-`season` feature at that airport, ahead
of `cloud_cover` (9.1%).

**One-line synthesis, flagged for the owner and not decided here:** the
1.5-year feature-complete window looks workable at 4 of 5 airports on this
diagnostic — the recipe recovers to beating raw GFS with a full seasonal
cycle in training, and the richer features add a further, real, if modest,
margin at the same 4 of 5 — while LFPG stands out as the one airport where
neither model beats raw GFS on this window, which this session's own tools
cannot explain further.

**Flagged for the owner, per the session prompt — report, do not decide:**

**(a) Is the 1.5-year window workable, or is a deeper GFS GRIB source
mandatory?** This diagnostic's own answer leans toward "workable at most
airports": 3-feature recovers to beating raw GFS at 4 of 5 once a full
seasonal cycle is in training, which was the central open question the
scout's short window could not answer (F86). It does not resolve LFPG,
where even a full-cycle 3-feature model still loses to raw GFS on this
window — whether that is a property of the 1.5-year window specifically, or
something the locked recipe's own full ~4.3-year training window already
handles better (LFPG's locked recipe beats raw GFS by 3.4–13.5% on its own
rehearsal and sealed test, F29/F30), was not tested here and is not
decidable from this session's own numbers.

**(b) Go/no-go on a full locked sealed-test cycle for the richer
features?** This diagnostic gives a firmer, multi-fold version of the
scout's signal — 5-feature beats 3-feature at 4 of 5 airports and beats raw
GFS at 4 of 5 airports, with sane (present-but-modest) overfit gaps at every
airport — which is a stronger case than the scout's single-year read gave.
Whether that is now enough evidence to justify a full lock-and-test cycle,
given the richer-feature window is still capped at ~1.5 years against the
locked recipe's ~4.3, and given LFPG's unresolved loss, is the owner's call.

**What this session did not do, on purpose.** No recipe was locked (session
33 scope forbids it). The sealed test year (2025-08-01 to 2026-07-31) was
never loaded, pulled, joined, fitted on, or printed at any airport or fold —
`scripts/session33_cv.py` asserts every loaded date is inside
`[2024-01-19, 2025-07-31]` and strictly before `2025-08-01` at every load
point, for every airport. No new raw data was pulled — only session 32's
existing `data/raw/features/` pull and the existing `data/raw/` chunks were
read. No hyperparameter was tuned and no feature was hand-picked per
airport. `SPEC.md` and `RESULTS.md` were not modified. Nothing was
committed.

---

## 2026-09-11 — Session 36 finding: GRIB build step 1 — back-extent confirmed,
pipeline validated at 4 of 5 airports, one terrain-driven gap named at RNO

**F89. This session opens the GRIB-build multi-session sub-project (docs/
session-36.md) with its first step: confirm the real fetchable back-extent,
and prove a hand-rolled GRIB→point temperature pipeline reproduces the
existing, trusted Open-Meteo temperature before any cloud/wind pull is
attempted. No bulk pull, no join, no fit, no lock — a validation gate only.**
Scripts: `scripts/session36_grib_pull.py` (byte-range temperature pull) and
`scripts/session36_validate.py` (decode, interpolate, reproduce-check). Full
real command output is `notes/session-36-check-output.txt`. Every extract
and the comparison table are saved under `data/raw/diagnostics/session36/`
with a `.meta.txt` per file (SPEC 2.3). No date after 2025-07-31 was fetched
or touched at any point (SPEC 2.1a, 4.3).

**Task 1 — confirmed back-extent: 2021-01-01, not ~2015. Flagged prominently,
per the session prompt's own instruction, because it materially re-weights
build-vs-lock.** Direct listing of `noaa-gfs-bdp-pds` (not assumed from a
doc page — SPEC 3.3's "verify on contact" principle, same as session 35's
own AWS-bucket correction) shows the bucket's own earliest date folder is
`gfs.20210101/`; probes of 2020-12-31, 2015-01-15, 2010-01-01 and
2000-01-01 all 404. **One wrinkle this session caught before misreading it
as an availability limit**: the 0.25° `pgrb2.0p25` product's *path* changes
from a flat `gfs.<date>/<cycle>/gfs.t<cycle>z.pgrb2.0p25.f<NNN>` layout to a
`.../<cycle>/atmos/...` layout on **2021-03-23** — one day before the
project's own Open-Meteo floor (SPEC 3.2) — and an `/atmos/`-only check
against pre-03-23 dates returns 404 even though the file exists at the flat
path. Bisected and confirmed: the flat-path form returns 200 continuously
back to the bucket's true floor, 2021-01-01. **So the AWS bucket extends the
fetchable window by only ~82 days beyond Open-Meteo's own floor — not the
~11-year (2015+) prize the sub-project's own framing hoped to confirm.**
NCAR's RDA has now fully completed its migration to GDEX — `rda.ucar.edu`
redirects its entire root to `gdex.ucar.edu`, and `data.rda.ucar.edu` no
longer resolves at all — and `ds084.1`'s GDEX landing page shows a "Sign In"
control with no anonymous/credential-free download path this session's
probes could find (a plain-HTTPS guess and a THREDDS-fileServer guess both
404'd). **This is "not found this session," not an exhaustive proof no
credential-free path exists on GDEX** — reported as a probe result, per
session scope. **Confirmed usable window: 2021-01-01 onward, essentially
the same order of magnitude (~4.4 years) as the project's existing
Open-Meteo-based window (~4.3 years), not ~11 years.** This re-weights the
still-open build-vs-lock question (STATUS "Next", Q30): the case for
building the full GRIB pipeline specifically *to reach much further back in
time* is substantially weaker than session 35's framing assumed; whatever
case remains rests on the richer-features win itself (F87), not on extra
history depth.

**Task 2 — GRIB reader installed with no system dependency.** Session 35
found no GRIB decoder and no Homebrew on this machine. This session found
`pip install eccodes` (PyPI package `eccodes==2.48.0`) pulls in
`eccodeslib==2.48.0.26`, a macOS-arm64 wheel that bundles ecCodes' own
compiled binary — no Homebrew, no system library, no admin access needed,
the same shape as the existing libomp workaround `requirements.txt` already
documents for LightGBM. Confirmed working end-to-end (decodes real GFS
messages, correct `shortName`/`validityDate`/`validityTime`/grid keys, see
Task 4/5 below). Recorded in `requirements.txt` (eccodes + its five small
dependencies, all pinned to the exact installed version, matching D24/Q16's
existing reproducibility discipline).

**Task 3 — 76 byte-range GRIB2 temperature extracts pulled, all magic-marker
valid, zero failures.** Sample: an early stretch at Open-Meteo's own floor
(2021-03-24 to 2021-03-28, 5 days) and a recent two-week stretch
(2025-06-01 to 2025-06-14, 14 days) — 19 target dates, all ≤ 2025-07-31.
76 distinct (run-date, cycle, lead) files were needed (not 19×5=95, because
EGLC and LFPG share the same 12z/f024 file on any given run date) — exactly
matching session 35's F88 "up to 4 distinct cycle/lead combinations per
calendar day" estimate (4×19=76). Every file fetched by one `.idx`
byte-range request each; every extract's first/last 4 bytes verified as
`GRIB`/`7777` (a complete, well-formed message, no full-file download at
any point).

**Task 4 — lead-time convention derived and confirmed; one real bug found
and fixed.** For a target valid hour `HH:00` UTC on day D: use the run made
at cycle `floor(HH/6)*6` UTC on day **D−1**, forecast hour `24 + (HH mod 6)`
— directly from SPEC 3.2's own description of how Open-Meteo assembles
`previous_day1` (hours 24–29 of each 6-hourly run, stitched). Concretely:
EGLC/LFPG (12:00 UTC) and DSM (18:00 UTC) land exactly on a cycle boundary,
so lead = f024 (a clean 24h lead — consistent with LFPG's own exact-match
pairing offset, SPEC 4.5); YSDU (02:00 UTC, 00z cycle) and RNO (20:00 UTC,
18z cycle) sit 2 hours past their cycle boundary, so lead = f026. **One real
bug, caught by the reproduction check itself, not by inspection**: ecCodes'
`codes_grib_find_nearest` accepts a query longitude in either −180..180 or
0–360 form and resolves it correctly internally, but the *neighbour*
longitudes it returns are always in 0–360 form — the first version of the
bilinear weight arithmetic used the raw (negative) query longitude against
those 0–360 neighbour values for DSM and RNO (both west of the prime
meridian), producing weights in the thousands and multi-hundred-degree
"temperatures." Fixed by normalising the query longitude to 0–360 before
computing the interpolation weight. EGLC/LFPG/YSDU (non-negative longitudes)
were unaffected and passed on the first run — direct evidence the bug was
the sign/convention handling, not the bilinear formula or the grid read
itself.

**Task 5 — the reproduction gate: PASS at 4 of 5 airports (EGLC, LFPG, DSM,
YSDU); FAIL at RNO, with a named, terrain-linked cause, not a pipeline bug.**

```
station   n   mean|diff|   mean diff   max|diff|   verdict
EGLC     19       0.248       -0.248       0.359     PASS
LFPG     19       0.251        0.217       0.575     PASS
DSM      19       0.181        0.154       0.684     PASS
YSDU     19       0.213       -0.108       0.455     PASS
RNO      19       2.044       -2.044       2.419     FAIL
```

All 95 rows (19 dates × 5 airports): the GRIB message's own
`validityDate`/`validityTime` matched the intended target date/hour exactly
— the lead-time convention itself is correct everywhere, at both sample
eras; the RNO gap is a magnitude problem, not a wrong-hour problem. At
EGLC/LFPG/DSM/YSDU the differences are small (0.18–0.25°C mean absolute) and
**mixed-sign** (−0.248, +0.217, +0.154, −0.108) — the shape of ordinary
rounding/interpolation noise (Open-Meteo's own published values are rounded
to 1 decimal place), not a systematic bias.

**RNO shows a clean, one-sided, systematic cold bias — every one of 19
sample days, both eras, GRIB colder than Open-Meteo by 1.80–2.42°C (mean
−2.044°C, essentially equal to the mean absolute difference — an offset, not
scatter).** Investigated with one small extra diagnostic pull (`HGT:surface`
— model terrain elevation — for the already-fetched 2025-06-10 18z f026
file; byte-range only, 492 KB, saved with its own `.meta.txt`): the four raw
GRIB grid points bracketing RNO's own established grid point (SPEC 3.4) carry
**model terrain elevations of 1591–1914 m — 246–570 m higher than RNO's
actual/grid elevation (1344–1345 m)**. At a standard lapse rate
(~0.65°C/100 m), that spread alone predicts roughly 1.6–3.7°C of cooling in
a plain grid-average relative to a point corrected down to the true
elevation — squarely consistent with the measured −2.044°C mean bias.
**Read plainly: Open-Meteo's own published value is evidently already
elevation-corrected for its target point (an expected downscaling step in
complex terrain); this session's bilinear-only pipeline is not, and RNO —
alone among the five airports, and consistent with its own established
character (SPEC 3.4, DECISIONS D42/F66: "Reno's difficulty ... is expected
to come from horizontal terrain complexity — the nearby Sierra Nevada
front") — sits in terrain steep enough for that gap to surface as a clear,
multi-degree bias rather than noise.** The other four airports' own
grid-to-airport elevation mismatches are all under 10 m (SPEC 3.4), so any
equivalent lapse-rate correction there would be sub-tenth-of-a-degree —
consistent with their small, mixed-sign residuals being ordinary noise
rather than a masked version of the same effect. **RNO's FAIL is
explicitly not a wrong-grid-point, wrong-cycle/lead, or unit/label error**
— the same established SPEC 3.4 point was used, `valid_ok` was true for
every RNO row, and `shortName`/units matched the other four airports exactly
— it is a missing elevation-correction step, named and explained, not an
unexplained failure.

**Overall verdict: the GRIB→point pipeline is PROVEN at 4 of 5 airports
exactly as built (byte-range TMP:2m pull, the derived cycle/lead convention,
plain bilinear interpolation) — sub-degree, unbiased differences against the
trusted Open-Meteo answer key, at both the archive floor and a recent date.
It is NOT yet proven at RNO: the interpolation and lead-time logic are not
implicated (both check out cleanly), but an elevation/lapse-rate correction
step is evidently needed there before RNO's own data could enter step 2's
bulk pull with the same trust the other four airports now have.** This is a
fix to make inside the GRIB-build sub-project, not a reason to distrust the
pipeline generally — and it is itself a small, freshly-confirmed, concrete
piece of evidence for the same "Reno's difficulty is real terrain, not just
a vertical offset" reading DECISIONS D42/F66/F81 already carried, now
demonstrated from a completely different data source (raw model terrain
height) than any of those three findings used.

**Flagged for the owner, not decided here, per the session prompt.** The
sub-project's step 2 (bulk cloud/wind pull) can proceed at EGLC/LFPG/DSM/
YSDU on the pipeline as validated. RNO needs either an elevation-correction
step added before its own values are trusted, or an explicit decision to
carry the same caveat LFPG already carries in the richer-features work
(F87) — proceed anyway and note the gap — neither of which this session
decided. Separately, and more materially: **Task 1's back-extent finding
(2021-01-01, not ~2015) weakens the "much deeper history" case for building
the GRIB pipeline at all** — the owner's build-vs-lock choice (STATUS
"Next") should now weigh this against F87's richer-features signal and
F88's cost estimate, not treat the GRIB route as a way to reach materially
further back in time than the project's existing window already does.

**What this session did not do, on purpose.** No cloud or wind variable was
pulled — temperature only. No bulk/multi-year pull — 76 small byte-range
GRIB2 extracts plus one small diagnostic `HGT:surface` extract, 77 files
total, each under ~900 KB. No date inside the sealed test year
(2025-08-01 to 2026-07-31) was fetched or touched — every sample date is
≤ 2025-07-31. No final feature pipeline was built, nothing was joined to
observations, no model was fitted, nothing was locked. `SPEC.md` and
`RESULTS.md` were not modified. Nothing was committed.

---

## 2026-09-11 — Session 37 finding: GRIB build step 2 — RNO elevation fix,
v16-only bulk pull, cloud/wind validated, feature dataset assembled

**F90. This session is step 2 of 4 of the GRIB-build sub-project (docs/
session-37.md): fix RNO's elevation gap (F89), pull the full feature set
(temperature, cloud cover, 10 m wind) over the v16-only training window at
all five airports, validate cloud/wind against Open-Meteo on the overlap
period, and assemble a validated GRIB feature dataset. It joins nothing to
observations, fits no model, opens no sealed year, and locks nothing.**
Scripts: `scripts/session37_elevation_fix.py` (Task 1), `scripts/
session37_grib_pull.py` (Task 2), `scripts/session37_decode.py` (Tasks 3-4).
Full real output: `notes/session-37-elevation-output.txt`, `notes/
session-37-pull-output.txt`, `notes/session-37-decode-output.txt`. No date
after 2025-07-31 was fetched, decoded, or touched at any point (SPEC 2.1a,
4.3) — asserted in code in both the pull and decode scripts, not just
stated.

**The v16-only window, restated and now actually enforced in code.** Per
this session's own prompt: GFS v16.0 became operational 2021-03-22, so the
window trains only on 2021-03-24 (Open-Meteo's own floor, one day inside
the v16 era) through 2025-07-31, never touching the ~82 pre-v16 (v15) days
the AWS bucket's true floor (2021-01-01, F89) would otherwise make
reachable. A bias-correction model must not cross a model-version boundary,
so those 82 days stay permanently out of scope for this sub-project, not
merely unused this session.

**Task 1 — RNO elevation/lapse-rate downscaling: chosen, applied at all
five airports, and the reproduction gate now PASSES at all five (was 4 of
5, F89).**

HGT:surface (model terrain) was byte-range-fetched for the four airports
that did not already have a sample (RNO's session-36 diagnostic pull was
reused, not re-fetched) and bilinear-interpolated to each airport's own
established grid point, exactly as temperature is. This gives each
airport's own static grid-orography-vs-Open-Meteo-grid-elevation gap (SPEC
3.4's "grid elevation" column — the elevation F89 read as the one
Open-Meteo's own downscaled value is referenced to):

```
station   orog_interp_m   om_grid_elev_m   gap_m
EGLC             37.47              4.0     33.47
LFPG             86.15            109.0    -22.85
DSM             270.11            285.0    -14.89
YSDU            312.12            279.0     33.12
RNO            1619.08           1344.0    275.08
```

RNO's own gap (275 m) is an order of magnitude larger than any other
airport's, consistent with F89's own finding of 246-570 m at the four
points immediately surrounding RNO's grid point specifically.

Two lapse rates were tried against session 36's already-saved 95-row
comparison table (`data/raw/diagnostics/session36/
session36_grib_vs_openmeteo_comparison.csv`), per the session prompt's
"match Open-Meteo empirically" instruction: the standard environmental
lapse rate (6.5 degC/km) and a rate solved exactly to zero out RNO's own
measured mean bias (-2.044 degC, F89) against its own gap, giving
**7.429 degC/km**. Both candidates bring all five airports to PASS; the
RNO-fit rate does modestly better at RNO itself (mean|diff| 0.146 vs 0.256
degC) and is the one adopted:

```
                          BEFORE correction        AFTER correction (7.429 degC/km)
station   n   mean|diff|  mean diff  verdict   mean|diff|  mean diff  verdict
EGLC     19       0.248     -0.248     PASS        0.039      0.000     PASS
LFPG     19       0.251      0.217     PASS        0.130      0.047     PASS
DSM      19       0.181      0.154     PASS        0.126      0.043     PASS
YSDU     19       0.213     -0.108     PASS        0.182      0.138     PASS
RNO      19       2.044     -2.044     FAIL        0.146      0.000     PASS
```

**A notable, unplanned cross-check: EGLC's own pre-correction bias-to-gap
ratio (0.248 degC / 33.47 m = 7.41 degC/km) lands almost exactly on RNO's
independently-fit rate (7.429 degC/km), even though EGLC's own gap (33 m)
is two orders of magnitude smaller and the fit used only RNO's data.**
This is not built into the method — it fell out of applying the same
constant-per-airport correction everywhere and then reading the four
"already-passing" airports' own before/after numbers — and reads as real,
if informal, evidence that this is one genuine physical effect (raw model
orography above the real/reported elevation, corrected by a roughly
uniform lapse rate) rather than an RNO-specific patch. The four
already-good airports' own gaps are small enough (-23 to +33 m) that their
corrections are proportionately small (-0.17 to +0.25 degC) and do not
risk their existing PASS — confirmed above, not assumed.

Correction parameters (gap, chosen lapse rate, resulting constant
degC correction) are saved at `data/raw/diagnostics/session37/
session37_elevation_correction_params.csv` and applied identically by
`session37_decode.py` to every temperature extract Task 2 pulled.

**Task 2 — the v16-only bulk pull: 6,364 distinct (run_date, cycle, lead)
files, 25,456 messages targeted, 25,444 fetched cleanly, 12 failed with a
real, verified, source-side cause; ~20 GB saved under `data/raw/grib/`.**

Matches F88's own advance estimate almost exactly: up to 4 distinct
cycle/lead combinations per calendar day (EGLC/LFPG share one; DSM, RNO,
YSDU each need their own) across 1,591 days = 6,364 files, x4 variables
(`TMP:2 m above ground`, `TCDC:entire atmosphere`, `UGRD`/`VGRD:10 m above
ground`) = 25,456 messages, ~31,800 HTTP requests total (idx + range-GETs).
Run with a pooled `requests.Session` and a 48-thread pool (added to
`requirements.txt`, pinned, since bare `urllib` — session 36's approach —
opens a fresh connection per request and would not finish this volume in a
practical session), a disk-space guard (abort, don't corrupt, below 3 GiB
free), and full skip-if-exists resume support. Wall time: 11.2 minutes for
the full run (~9.5 combos/s once warmed up), a second near-instant pass to
retry the 12 failures.

**The 12 failures (3 combos x 4 variables: RNO target 2022-11-30, DSM
target 2022-11-30, YSDU target 2022-12-01) were investigated, not just
retried and accepted.** All 12 failed the magic-marker check (bytes
returned did not start `GRIB`/end `7777`) on both the original run and a
clean re-run, which ruled out ordinary transient network corruption.
Direct inspection of the affected `.idx` files and their real files' HTTP
`Content-Length` found the actual cause: **the `.idx` file's own last
listed byte offset exceeds the real GRIB2 file's actual length**, by
508 KB-2.93 MB depending on the file — e.g. RNO's 2022-11-29 18z f026 idx
claims a message starting past byte 547,942,907 while the real file is
only 546,857,316 bytes long. This is a genuine, verified upstream
archive/index inconsistency for these three specific run/cycle files (all
clustered on 2022-11-29/30), not a bug in this session's byte-range
arithmetic (confirmed correct against multiple other dates, both 2021-era
and 2025-era, before and after this finding) and not a request-layer
failure (the idx itself fetches fine and looks structurally normal). Per
SPEC 2.2, these 3 (station, target_date) rows are dropped and counted, not
guessed at or worked around; they show up as exactly 3 rows in
`data/processed/grib_features_v16_window_drops.csv` (reason: `missing
extract(s)`), one at each of RNO, DSM and YSDU. No other date in the
pull failed for any reason.

**Disk space, flagged for the owner.** The pull used ~20 GB; free space on
the volume fell from 35 GiB to 14 GiB over the course of this session. SPEC
2.3/DECISIONS D15 commits raw pulls to version control, so this ~20 GB (in
25,444 small files) will enter the repository's history once the owner
commits it — a step-change in repo size versus every prior session. Not
decided here; noted so the owner can weigh it before committing.

**Task 3 — cloud/wind validated against Open-Meteo on the 2024-01-19 to
2025-07-31 overlap (F85): wind speed matches tightly; cloud cover matches
well at the median but has a real, heavy right tail.**

```
station   cloud mean|diff| (pct)   cloud mean_diff   wind mean|diff| (km/h)   wind mean_diff   verdict (both)
EGLC              12.601               -0.638                0.250              +0.197              PASS
LFPG              10.635               -1.982                0.417              -0.342              PASS
DSM               12.115               -1.197                0.253              -0.078              PASS
YSDU              12.017               -1.161                1.141              -0.984              PASS
RNO               10.220               +0.480                1.937              -0.060              PASS
```

Wind speed (derived as sqrt(UGRD^2 + VGRD^2), converted m/s -> km/h to
match Open-Meteo's own unit, confirmed from an existing pull's
`hourly_units`) matches closely at every airport — sub-2 km/h mean
absolute difference everywhere, no material systematic offset (all five
mean signed diffs inside +/-1 km/h). **Cloud cover's mean absolute
difference (10-13 percentage points at every airport) is real, not
dominated by a few outliers in the way the summary number alone might
suggest — but the FULL distribution (pooled across all 2,799 comparable
rows) is stated honestly rather than hidden behind one number:**

```
percentile:  p50    p75    p90    p95    p99
|diff| pct:  1.3    12.6   41.8   60.2   88.0
```

**Half of all rows match within 1.3 percentage points; the top ~10% of
rows disagree by 40+ points, some (56 of 2,800, 2%) by 80+ points —
GRIB and Open-Meteo occasionally landing on opposite ends of the 0-100
scale on the same nominal hour.** No systematic direction (mean signed
diffs are small and mixed-sign across airports, -2.0 to +0.5), so this
reads as cloud cover's own high spatial/temporal sensitivity at the 0.25
deg grid scale in partly-cloudy conditions — a plausibly real
disagreement about a genuinely fast-changing field, not an offset error
comparable to RNO's elevation bias — rather than a bug; it was not
investigated further this session (out of scope: Task 3 asks for
mean|diff|, direction, and a verdict, not a per-day forensic pass). PASS
verdicts use thresholds set this session for this diagnostic only (cloud
15 pct, wind 3 km/h — both stated in `session37_decode.py`'s own
comments), not a SPEC-frozen bar; the full numbers above are reported
either way so no reader depends on the threshold alone. **Flagged for the
owner:** whether the cloud-cover tail is acceptable to carry into step 3
(the richer-features re-run) as-is, or merits its own investigation first,
is not decided here.

**Task 4 — assembled dataset: 7,952 rows (of a possible 7,955 = 1,591
days x 5 airports), 3 dropped (the Task 2 idx-mismatch dates above), saved
separately from both the raw GRIB extracts and the existing Open-Meteo
files.**

```
station   kept   dropped
EGLC      1591        0
LFPG      1591        0
DSM       1590        1
YSDU      1590        1
RNO       1590        1
```

Saved at `data/processed/grib_features_v16_window.csv` (station,
target_date, target_hour, run_date, cycle, lead,
temperature_grib_c [elevation-corrected], cloud_cover_grib_pct,
wind_speed_grib_kmh), `data/processed/grib_features_v16_window_drops.csv`
(the 3 drops, with reason), and `data/processed/
grib_vs_openmeteo_cloudwind_validation.csv` (the full 2,800-row Task 3
comparison). Nothing here is joined to any observation and no model is
fitted — that is step 3 (docs for step 3 not yet written).

**What this session did not do, on purpose.** Did not use any data before
2021-03-24 (the ~82 pre-v16 AWS-only days stay excluded, by design, not by
oversight). Did not pull, decode, or touch any date inside the sealed test
year (2025-08-01 to 2026-07-31) — both the pull and decode scripts assert
this in code. Did not join the assembled dataset to any observation, fit
any model, run any experiment, or lock anything. Did not download any
whole GRIB file — every message was byte-range-fetched. Did not modify or
overwrite any existing Open-Meteo data — `session37_decode.py` opens
`data/raw/features/*.json` read-only for comparison. Did not modify
`SPEC.md` or `RESULTS.md`. Nothing was committed.

## 2026-09-12 — Session 38 finding: GRIB build step 3 -- richer-features CV
on the full v16 window: 5-feature beats raw GFS at 5 of 5 airports, LFPG
recovers, Reno's rescue holds

**F91. This session is step 3 of 4 of the GRIB-build sub-project (docs/
session-38.md): diagnose the session-37 cloud-cover tail, join the
validated GRIB feature dataset to IEM observations over the full v16 window,
re-run the richer-features blocked CV on that full ~4.4-year window (GRIB
source throughout), and sanity-check the source swap. Opens no sealed year,
locks nothing.** Scripts: `scripts/session38_cloud_diagnostic.py` (Task 1),
`scripts/session38_join.py` (Task 2), `scripts/session38_cv.py` (Tasks 3 and
5), `scripts/session38_sanity.py` (Task 4). Full real output: `notes/
session-38-cloud-diagnostic-output.txt`, `notes/session-38-join-output.txt`,
`notes/session-38-cv-output.txt`, `notes/session-38-sanity-output.txt`. No
date on or after 2025-08-01 was loaded, joined, or scored at any point --
asserted in code in every script, not just stated.

**Task 1 -- cloud-cover tail verdict: BENIGN-DEFINITIONAL. GRIB cloud is
used as the feature, on its own terms, not corrected toward Open-Meteo (the
session prompt forbade correcting it either way).** Three checks, all
against F90's own finding (GRIB TCDC matches Open-Meteo cloud at the median,
1.3 pct, but with a heavy tail, p90 41.8, p99 88.0):
- **GRIB TCDC is internally sane over the full 7,952-row window**: every
  value falls inside [0, 100] at every airport, no missing or garbage
  values are possible by construction (a failed decode is already a dropped
  row in `grib_features_v16_window_drops.csv`, F90).
- **The worst-disagreement rows do NOT cluster on a small shared set of
  dates** (the artifact signature session 37's own 12-message idx-mismatch
  failures showed, F90): the 100 highest-|diff| rows out of 2,799 spread
  across 90 distinct dates, only 10 of them repeated, and no station
  dominates the list (16-27 rows each).
- **The disagreement is worst exactly where a genuinely fast-changing,
  partly-cloudy sky would be expected to disagree most between two
  different products, not where a bug would concentrate it**: bucketed by
  Open-Meteo's own reported value, mean|diff| is 7.1-8.9 pct at the clear/
  overcast extremes (0-10 pct and 90-100 pct, 2,281 of 2,799 rows) against
  25.6-27.3 pct in the mid-range bands (10-90 pct, the remaining 518 rows).
  The disagreement's sign is mixed (25.8% GRIB-higher, 36.4% GRIB-lower,
  38% exactly equal after rounding), pooled mean signed diff only -0.90 pct
  points -- the signature of noise/disagreement, not a systematic offset
  (contrast RNO's pre-correction temperature bias, F89: 100% one-sided,
  mean == mean|diff|).

**Task 2 -- join: 7,928 of a possible 7,955 rows kept (99.7%), every drop
reconciling against already-known facts.**

```
airport   GRIB rows available   no usable obs   rows kept
EGLC             1591                  2           1589
LFPG             1591                  2           1589
DSM              1590                  0           1590
YSDU             1590                 17           1573
RNO              1590                  3           1587
```

(GRIB row availability itself already reflects session 37's own 3 idx-
mismatch drops, one each at DSM/YSDU/RNO, F90 -- not re-counted here.) YSDU's
larger drop count (17, of which 10 are >15-minute off-hour reports dropped
by D14) again reproduces Dubbo's own known higher off-hour/no-report rate
(F58/F59/F87). Joined dataset: `data/processed/session38_joined.csv`.

**Task 3 -- blocked seasonal CV on the FULL v16 window (2021-03-24 to
2025-07-31, 1,591 days, 17 contiguous ~93-94-day blocks), GRIB source
throughout. Headline: 3-feature beats raw GFS (GRIB) at 5 of 5 airports; 5-
feature beats 3-feature at 5 of 5 and beats raw GFS (GRIB) at 5 of 5.**

```
airport  Raw GFS(GRIB)  +mean-bias      3-feature      5-feature   n days
EGLC        1.177       1.186 (-0.8%)  1.117 (+5.0%)  1.067 (+9.3%)   1589
LFPG        1.266       1.279 (-1.0%)  1.223 (+3.3%)  1.199 (+5.3%)   1589
DSM         1.887       1.916 (-1.5%)  1.538 (+18.5%) 1.534 (+18.7%)  1590
YSDU        1.358       1.346 (+0.8%)  1.240 (+8.7%)  1.195 (+12.0%)  1573
RNO         1.483       1.455 (+1.9%)  1.391 (+6.2%)  1.295 (+12.7%)  1587
```

Every airport wins in some of the 17 blocks and loses in others (full
per-block tables in the saved output), the same fold-to-fold variance F87
found on the 1.5-year window -- a full seasonal cycle in training does not
make every quarter easy, it makes the pooled result robust to any one
quarter.

**Overfit diagnostic (pooled in-sample vs pooled out-of-fold MAE) -- sane
and consistent with F87's own reading, slightly larger everywhere because
each of the 17 training folds is now ~4 years instead of ~15 months:**

```
airport   3-feat gap   5-feat gap
EGLC        +0.224       +0.266
LFPG        +0.256       +0.322
DSM         +0.337       +0.429
YSDU        +0.240       +0.305
RNO         +0.296       +0.367
```

A positive gap at every airport for both models, the ordinary signature of
a flexible tree model fitting its own training folds more tightly than it
generalises -- not alarming on its own, and every gap stays well inside the
0.2-0.8 degC range F87 already found on the shorter window.

**5-feature importances, averaged across the 17 folds -- nothing is
ignored, nothing dominates, at any airport:**

```
airport   forecast_temp_c   season_sin   season_cos   cloud_cover   wind_speed_10m
EGLC            29.1%           16.8%        15.0%         14.2%           24.8%
LFPG            26.6%           21.7%        16.1%         17.3%           18.2%
DSM             30.9%           26.7%        14.4%         12.6%           15.4%
YSDU            31.1%           17.4%        17.0%         13.2%           21.2%
RNO             21.1%           22.3%        17.7%         14.1%           24.9%
```

**Task 4 -- source-swap sanity check: PASSES both checks. The swap from
Open-Meteo to GRIB temperature did not materially change the baseline.**
Check 1 (strict, identical rows): on the exact same (station, date) rows
Task 2 kept, raw-forecast MAE computed with GRIB temperature vs with
Open-Meteo temperature differs by at most **0.062 degC** at any airport
(EGLC -0.003, LFPG -0.026, DSM -0.026, YSDU +0.055, RNO +0.062) -- an order
of magnitude smaller than any of the skill margins in Task 3's table, and
consistent with F90's own 0.126-0.182 degC (and RNO's post-correction 0.146
degC) reproduction-gate figures on a smaller sample. Check 2 (context,
different windows, not a strict comparison): the GRIB-based full-window raw
and 3-feature CV figures sit in the same general range as each airport's
own established Open-Meteo rehearsal, sealed-test, and F87 1.5-year-CV
figures (full table in the saved output) -- no airport lands in a
materially different regime.

**Task 5 -- the headline reads.**

**Does 5-feature beat 3-feature, and does either beat raw GFS? Yes,
everywhere.** 3-feature beats raw GFS (GRIB) at **5 of 5** airports (F87's
1.5-year Open-Meteo window: 4 of 5, LFPG the exception). 5-feature beats
3-feature at **5 of 5** and beats raw GFS (GRIB) at **5 of 5** (F87: 4 of 5
on both counts).

**LFPG: the full window recovers it.** LFPG was the one airport where
neither model beat raw GFS on F87's 1.5-year Open-Meteo window (3-feature
-7.7%, 5-feature -2.1%, never closing the gap). On the full ~4.4-year GRIB
window, LFPG's 3-feature model beats raw GFS (GRIB) by +3.3% and 5-feature
extends that to +5.3% -- both features help, and the loss does not
reappear. This reads as a window-length effect specific to LFPG (the same
kind of effect F86/F87 already found dominated the whole richer-features
story on the 6-month scout window), now resolved by the same full seasonal
history the locked recipe itself has always trained on, not as a change in
the method.

**Reno: the short-window rescue signal holds, and strengthens.** F87 found
5-feature beat both 3-feature (+3.8% skill) and raw GFS (+7.3%) at Reno on
the 1.5-year Open-Meteo window, the first positive richer-features result
there after the scout's own null result (F86). On the full v16 GRIB window,
**Reno's 5-feature model beats 3-feature by a wider margin (1.295 vs 1.391,
skill vs raw GFS +12.7%, against 3-feature's own +6.2%) and both remain
comfortably ahead of raw GFS.** `wind_speed_10m`'s gain share at Reno (24.9%,
importance table above) is again the larger of the two new features,
consistent with F87's own reading. This is the strongest positive
richer-features signal Reno has produced across all three experiments
(F86 null, F87 modest, this session's fuller and larger).

**One-line synthesis, flagged for the owner and not decided here:** on the
full ~4.4-year v16 GRIB window, with cloud/wind features throughout, the
richer 5-feature recipe beats both the 3-feature recipe and raw GFS at
**every one of the five airports**, including LFPG (which never won on the
shorter window) and Reno (whose rescue signal was previously modest and
1.5-year-only). This is materially stronger and more complete evidence than
either the scout (F86) or the 1.5-year CV (F87) produced. **The step-4
question -- lock the richer method, and on which window (the full ~4.4-year
GRIB window this session used, or something else) -- is the owner's to
decide, not made here.** Nothing was fitted on, or scored against, the
sealed test year at any point.

**What this session did not do, on purpose.** Did not open, load, or score
the sealed test year (2025-08-01 to 2026-07-31) at any point -- every
script asserts every loaded date is `< 2025-08-01`. Did not lock any
recipe. Did not tune any hyperparameter or change settings between the two
models. Did not add a lagged/recent-observation feature, and did not add a
terrain/elevation feature (kept the clean 3-vs-5 comparison, per the
session prompt). Did not hand-pick features per airport. Did not "correct"
GRIB cloud toward Open-Meteo -- Task 1 only characterised it. Did not
modify `SPEC.md` or `RESULTS.md`. Did not pull any new raw data (D47 does
not apply here -- this session wrote only small processed tables under
`data/processed/`, no new GRIB bytes). Nothing was committed.

---

## 2026-09-12 — Session 39 decision: the 5-feature GRIB recipe is locked for
the sealed test (D48), no sealed data touched

**D48. The 5-feature richer-features GRIB recipe is LOCKED, at all five
airports at once. This entry fully specifies what session 40's sealed-test
session will run. Nothing in it was decided with any sealed-year value in
view -- no date on or after 2025-08-01 was loaded, computed, or referenced
anywhere this session.** This mirrors D44's role for Reno (write the lock,
then a separate session executes it once), widened to cover all five
airports in one entry because the recipe itself -- source, features, model,
window -- is now identical across airports; only the per-airport facts
already on record in SPEC 3.4 (target hour, grid point, pairing offset,
elevation correction) differ, exactly as they already did for the existing
locked 3-feature recipe (D21/D31/D35/D39/D44).

**Why now.** F86 (scout) found a real but short-window-confounded signal;
F87 (1.5-year CV) found the recipe recovers at 4 of 5 airports with LFPG
unresolved; F89-F90 (GRIB build steps 1-2) built and validated a GRIB-based
pipeline reaching the full training window, fixing RNO's terrain gap along
the way; F91 (GRIB build step 3, full ~4.4-year CV) found 5-feature beats
both 3-feature and raw GFS at **all five airports**, including the two
previously weak cases (LFPG, Reno). That is the evidence base this lock
rests on. No new evidence is created this session -- this session only
writes the recipe down completely and freezes the code that will execute
it.

**D48.1 — What is predicted.** The **residual**: observed temperature (IEM
METAR) minus GRIB-forecast temperature, at the airport's own target hour
(SPEC 4.1, 4.2). The corrected forecast is the GRIB forecast plus the
predicted residual. Identical in kind to every earlier lock (D21.2, D31.2,
D35.2, D39.2, D44.2) -- only the forecast source changes, from Open-Meteo to
GRIB.

**D48.2 — Airports and their own facts (SPEC 3.4, F89, F90 -- nothing here
is new, only collected in one place).** One row per day, at each airport's
own established target hour and grid point:

```
station  target hour  grid lat     grid lon      grid elev  cycle  lead  reports at  pairing offset
EGLC       12:00 UTC  51.487137    0.0            4.0 m       12z  f024      :50        10 min
LFPG       12:00 UTC  49.027008    2.578125     109.0 m       12z  f024      :00         0 min
DSM        18:00 UTC  41.52945    -93.63281     285.0 m       18z  f024      :54         6 min
YSDU       02:00 UTC -32.274643  148.59375      279.0 m       00z  f026      :00         0 min
RNO        20:00 UTC  39.537918  -119.765625   1344.0 m       18z  f026      :55         5 min
```

Cycle/lead follow F89's derived convention exactly: run at cycle
`floor(HH/6)*6` on day D-1, forecast-hour lead `24 + (HH mod 6)` for target
hour HH.

**D48.3 — The elevation/lapse-rate temperature correction, per airport, as
an exact constant (F90).** Lapse rate **7.429 degC/km** (fit to zero out
RNO's own measured bias, cross-checked against EGLC's independent ratio,
F90), applied as `corrected = raw_grib_temp_c + (orog_interp_m -
grid_elev_m) / 1000 * 7.429`. The gap and the resulting constant per
airport (F90's Task 1 table):

```
station   gap (orog - grid elev)   constant correction applied
EGLC              +33.47 m                  +0.249 degC
LFPG              -22.85 m                  -0.170 degC
DSM               -14.89 m                  -0.111 degC
YSDU              +33.12 m                  +0.246 degC
RNO              +275.08 m                  +2.044 degC
```

These five constants are fixed. They are not refit this session, next
session, or ever, without a new DECISIONS entry -- the whole point of fixing
them now is that the sealed test applies a number decided before it opened,
not one fit to the sealed year.

**D48.4 — Features (exact).**
```
forecast_temp_c   GRIB GFS 2 m temperature (D48.2/D48.3), previous_day1-
                  equivalent lead, elevation-corrected, bilinear-
                  interpolated to the airport's established grid point
season_sin        sin(2 * pi * year_fraction(date))
season_cos        cos(2 * pi * year_fraction(date))
cloud_cover       GRIB TCDC (entire atmosphere), same grid->point, same lead
wind_speed_10m    sqrt(UGRD^2 + VGRD^2) at 10 m, m/s converted to km/h,
                  same grid->point, same lead
```
where `year_fraction` is `(day_of_year - 1) / 365`, or `/ 366` in a leap
year (identical to D44.3). **Two rungs are fitted and reported, not one**:
a 3-feature model (`forecast_temp_c`, `season_sin`, `season_cos`) — the
same feature set as the existing locked recipe, refit on GRIB source — and
the 5-feature model above (the richer-features claim this whole build
exists to test). Nothing is hand-picked per airport; the same two feature
sets are used everywhere.

**D48.5 — Source and pipeline (exact, F89/F90).** GFS 0.25 deg GRIB2 from
AWS `noaa-gfs-bdp-pds`, byte-range fetched per message (never a whole-file
download); ecCodes decode; bilinear interpolation to the airport's own
established `gfs_global` grid point (SPEC 3.4); the D48.3 elevation
correction applied to temperature only (cloud cover and wind speed are used
as GRIB reports them, uncorrected -- F91 Task 1 found the cloud tail
benign-definitional and the session-38 prompt forbade correcting it either
way).

**D48.6 — Model and settings (identical at every airport, no per-airport
tuning -- D21.4, unchanged since session 05).**
```
objective=regression_l1   n_estimators=300      learning_rate=0.05
num_leaves=15             min_child_samples=40   subsample=1.0
colsample_bytree=1.0      reg_alpha=0.0          reg_lambda=0.0
random_state=42           n_jobs=1               deterministic=True
force_row_wise=True       verbose=-1
```
Library versions pinned in `requirements.txt`: python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0. Both the 3-feature and 5-feature model use these identical
settings.

**D48.7 — Training window: 2021-03-24 to 2025-07-31 (v16-only, F89/F90),
trained in FULL -- no inner-training/validation split.** The CV/rehearsal
phase is finished (F86, F87, F91); the sealed run refits on the whole
training window, the same move every earlier lock made at its own airport
(D21.5, D31.5, D35.5, D39.5, D44.5). **Expected training-row count per
airport, taken directly from F91's own full-window join (`session38_joined
.csv`) and reused unchanged, since that join already covers exactly this
training window with no split:**
```
station   expected training rows (of 1,591 calendar days)
EGLC              1,589
LFPG              1,589
DSM               1,590
YSDU              1,573
RNO               1,587
```
A training-row count other than the figure above, at any airport, is a
D48.12 stop signal -- it means either the training data changed since F91
(it should not have) or the frozen script's join logic diverges from
session38_join.py's (it should not).

**D48.8 — Sealed test year: 2025-08-01 to 2026-07-31 (SPEC 4.3, D13), 365
calendar days, opened ONCE per airport, nothing after 2026-07-31.** This is
a genuinely new pull for this recipe: the GRIB feature dataset (temperature,
cloud cover, wind speed) does not yet exist for these dates at any airport,
and pulling it is session 40's job, following the same byte-range/decode
pipeline as session 37 (F90), restricted to this window, saved as
`data/processed/grib_features_sealed_window.csv` in the same column layout
as `grib_features_v16_window.csv`.

The **observation** side of the sealed year is not new -- IEM chunks
covering 2025-08-01 to 2026-07-31 already exist under `data/raw/` for all
five airports (pulled for each airport's own already-completed sealed test
under the existing 3-feature/Open-Meteo recipe, F16/F30/F47/F64/F82) and
are read again here, unchanged, read-only. **Expected scored-day counts, to
reconcile against the observation-side history already on record** (the
D14 pairing rule and each airport's own reporting pattern are unchanged by
the switch to GRIB -- only the forecast source differs):
```
station   already-published scored days (F16/F30/F47/F64/F82)
EGLC                    363
LFPG                    363
DSM                     365
YSDU                    347
RNO                     365
```
The richer-features sealed run may reasonably score **fewer** days than the
figures above, if the new sealed-year GRIB pull hits its own idx-mismatch-
style gaps the way F90's training-window pull hit three (dropped and
counted, SPEC 2.2, not worked around) -- that is a legitimate, reportable
outcome, not an error. It must not score **more** days than the figures
above, since the observation side cannot supply an extra usable pairing
that was not there for the existing recipe's own sealed test. A scored-day
count higher than the relevant figure above, at any airport, is a D48.12
stop signal.

**D48.9 — Pairing and missing data: the D14 rule (SPEC 4.5), unchanged.**
Each forecast valid at the airport's target hour is paired with the
station's nearest routine report to that hour; if none falls within 15
minutes, the day is dropped and counted. Nothing is ever filled (SPEC 2.2).
Persistence's previous-day observation may reach back across the training/
test boundary (e.g. the first test day's "yesterday" is 2025-07-31, inside
the training window) -- that is a past value, legal under SPEC 2.1d, the
same note D44.8 made for Reno.

**D48.10 — What is scored, and on what days.** Four rungs, on the same
common set of days per airport (the days every rung has a value for):
**raw GFS (GRIB, elevation-corrected)**, **persistence** (previous
calendar day's observation), **3-feature** (GRIB source, refit on the full
training window), **5-feature** (the locked richer recipe). This is
deliberately narrower than D44.8's four-reference list (which also reported
climatology and the mean-bias reference) -- the session-39 prompt's own
"what is reported" instruction names exactly these four rungs plus the
5-vs-3 comparison, and that instruction is followed exactly, not widened.

**D48.11 — The bar (frozen, qualitative, unchanged -- SPEC 5.3, D22).** An
airport passes if the **5-feature** corrected forecast has a lower MAE than
**both raw GFS (GRIB) and persistence**, over that airport's own sealed
test year. No numeric margin. Judged once per airport (SPEC 5.0) -- a pass
or fail at one airport does not change another's. **The 5-vs-3-feature
comparison (does the richer recipe actually add value on the true held-out
year) is reported alongside the bar verdict, but is not itself part of the
bar** -- the bar is still exactly "beats raw GFS and persistence," as it has
been at every airport so far. If a given airport passes, the 5-feature GRIB
recipe folds into SPEC only in a later session, after the result is known
(same discipline D44's Reno lock followed) -- this session changes neither
`SPEC.md` nor `RESULTS.md`.

**D48.12 — Pre-registered expectations, recorded before the look (F91,
mirroring D44.12's naming of Reno's expected failure mode in advance).**
From the full-window CV: 5-feature is expected to beat **both** raw GFS and
persistence at **all five airports**; 5-feature is expected to beat
3-feature at **all five airports**; **LFPG is expected to pass** (it lost on
the shorter 1.5-year window but won on the full window, F91); **RNO is
expected to pass** (the richer-features rescue strengthened on the full
window, +12.7% skill, F91) -- a reversal of RNO's own existing sealed-test
failure under the 3-feature/Open-Meteo recipe (F82), stated plainly so a
reversal is read as a genuine result of a different, richer recipe on a
different data source, not as erasing or re-litigating F82's own result
(D48.13 below). Any training-row or scored-day count that will not
reconcile against D48.7 or D48.8, any setting that does not match D48.6, or
any tempting small improvement noticed once the sealed year is open, is a
**stop signal**: the executing session stops and raises it with the owner
rather than deciding on the fly (identical in spirit to D21.11, D31.11,
D35.11, D39.11, D44.11).

**D48.13 — One look, and the result stands, per airport, and it does not
touch any earlier result.** Each airport's sealed test year is opened once
under this recipe, run once, and reported straight, pass or fail. No
re-tuning, no feature/window/lapse-rate change, no re-run, no retroactive
adjustment, whatever the result. **This is a new, separate test of a
different recipe (GRIB source, richer features) -- it does not re-open, retest,
or overwrite any airport's existing sealed-test verdict under the
existing 3-feature/Open-Meteo recipe** (EGLC F16, LFPG F30, DSM F47, YSDU
F64, RNO F82 all stand exactly as reported). If richer-features passes
where the existing recipe already passed, the project has two independently
-tested recipes at that airport; if it passes where the existing recipe
failed (RNO), that is a genuine, separate finding about the richer recipe,
not an erasure of F82.

**The frozen sealed-test script.** `scripts/session39_sealed_test.py`,
written and verified this session (parses; imports cleanly, including the
LightGBM/libomp workaround already proven in every session-3x modelling
script; logic reviewed line-by-line against D48.1-D48.10 above), but **not
run against sealed data** -- its sealed-year feature path
(`data/processed/grib_features_sealed_window.csv`) does not exist yet and
is session 40's own job to produce. The script asserts, in code: every
training-window row it loads has `target_date < 2025-08-01`; every
sealed-year row it loads falls inside `[2025-08-01, 2026-07-31]`, and it
raises rather than proceeding if either bound is violated; and it refuses
to run at all (a clear, named error, not a silent skip) if the sealed
feature file is missing -- which it is, as of this session, on purpose.

**What must not change after the sealed year is opened.** No re-tuning, no
feature/window/lapse-rate change, no re-run, no retroactive adjustment. The
result stands exactly as tested, pass or fail, per airport -- the same rule
D44.10 and D44.11 already state, applied here to five airports and a new
recipe rather than one.

---

## 2026-09-12 -- Session 40 finding: GRIB build step 4b -- the sealed pull
and decode completed cleanly, but the frozen script's own D48.12 self-guard
stopped the run before any model was fit at any airport

**F92. Session 40 opened the sealed test year (D48.8) for the 5-feature
GRIB recipe. The pull and decode (Task 1) completed cleanly at all five
airports, and the existing sealed-year IEM observations (Task 2) were
reused unchanged. Running the frozen script (Task 3,
`scripts/session39_sealed_test.py`, confirmed unmodified against the
session-39 commit by `git diff` before running) tripped its own D48.12 stop
signal at the first airport it processes, EGLC, before fitting any model.
Per the session prompt's explicit instruction, this was NOT worked around,
retried, or patched -- the run stopped there. No sealed-year MAE was
computed and no PASS/FAIL verdict was reached at EGLC or any other airport.
D48's one authorised look (D48.13) has therefore not been taken anywhere --
this is a different situation from Reno's F82, where a look was taken and
came back negative; here, no look happened at all.**

**Task 1 -- the sealed-year GRIB pull and decode: complete, clean, zero
drops at every airport.** Script `scripts/session40_grib_pull.py` mirrors
`scripts/session37_grib_pull.py` exactly (same AWS bucket, same F89
lead/cycle convention, same variable labels), restricted to
2025-08-01..2026-07-31 (D48.8, both bounds asserted before any request).
1,460 distinct (run_date, cycle, lead) files were needed (up to 4/day x 365
days, EGLC/LFPG sharing one); all 5,840 messages (4 variables x 1,460
files) fetched cleanly in one pass, zero failures, 3.5 minutes. Raw saved
under `data/raw/grib/` (gitignored, D47), one `.meta.txt` per file. Full
output: `notes/session-40-pull-output.txt`.

`scripts/session40_decode.py` mirrors `scripts/session37_decode.py`'s
Task-4 assembly logic exactly, applying the five FROZEN D48.3 elevation/
lapse-rate constants unchanged (loaded from session 37's own
`session37_elevation_correction_params.csv`, not refit) to temperature
only. **All five airports decoded 365 of 365 window days, zero drops** --
a materially cleaner forecast-side record than the training window's own
3-drop history (F90). Output: `data/processed/grib_features_sealed_window.csv`
(1,825 rows) and `data/processed/grib_features_sealed_window_drops.csv` (0
rows). Full output: `notes/session-40-decode-output.txt`. Task 2 (sealed-
year observations) needed no new pull -- the existing IEM chunks covering
2025-08-01..2026-07-31 at all five airports (pulled for each airport's own
already-completed 3-feature/Open-Meteo sealed test, F16/F30/F47/F64/F82)
were read again, unchanged, exactly as D48.8 specified.

**Task 3 -- the frozen script tripped its own D48.12 stop signal.**
Running `python scripts/session39_sealed_test.py` unchanged produced, for
EGLC (the first airport in the script's own iteration order):

```
training rows kept : 1589 (matches F91's own expected 1589 -- MATCH)
sealed-year rows kept : 364 (no GRIB row: 0, no usable obs: 1)
existing-recipe (3-feature/Open-Meteo) scored days (F16): 363
```

364 > 363, which the frozen script's own D48.8 self-guard treats as a stop
signal ("the sealed pull may score fewer days than the existing-recipe
history ... never more ... a scored-day count higher ... is a D48.12 stop
signal"), and it raised `AssertionError` before fitting any model. Partial
console output (through the point of the stop): `notes/
session40-sealed-test-output.txt`; no `data/processed/
session40_sealed_test_summary.csv` was written, because the script never
reached that line.

**A read-only diagnostic, not a workaround, gives the owner the full
scope in one pass.** The frozen script's own unmodified functions
(`load_obs_all`, `load_grib_features`, `join_rows`) were imported and
called directly, as a library, to compute every airport's sealed-year row
count against its own D48.8 ceiling -- no guard was bypassed, no model was
fit, nothing was changed in `scripts/session39_sealed_test.py` or anywhere
else:

```
station   sealed rows kept   no_grib   no_obs   D48.8 ceiling   status
EGLC            364              0        1          363       EXCEEDS
LFPG            364              0        1          363       EXCEEDS
DSM             365              0        0          365       within bound (exact match)
YSDU            356              0        9          347       EXCEEDS
RNO             365              0        0          365       within bound (exact match)
```

**Three of five airports (EGLC, LFPG, YSDU) exceed their own D48.8
ceiling; DSM and RNO land exactly on it.** Had the script's airport
iteration order been different, it would still have stopped at the first
of EGLC/LFPG/YSDU it reached -- the outcome is not an EGLC-specific fluke.

**A hypothesis for the mechanism, stated as a hypothesis and not verified
further this session -- confirming it exactly would mean opening the
existing 3-feature/Open-Meteo sealed-year forecast files to find the
specific null dates, which is new investigative work outside this
session's stop-and-report scope.** This session's GRIB sealed-year decode
found zero missing days at every one of the five airports (365 kept, 0
dropped each, Task 1 above) -- a cleaner forecast-side record than the
existing 3-feature/Open-Meteo recipe's own sealed test evidently had, at
least at EGLC, LFPG and YSDU (their own published scored-day counts, 363/
363/347, are all below 365 minus only the observation-side drops this
session measured). **The D48.8 ceiling rule was written on the assumption
that a new forecast source could only ever match or lose ground relative
to the old one** (D48.8's own words: "the observation side cannot supply
an extra usable pairing that was not there for the existing recipe's own
sealed test") -- **but the actual divergence here is on the forecast side,
not the observation side**: GRIB simply appears to have fewer missing days
than Open-Meteo's own `previous_day1` series had over this particular
year, at three of the five airports. The rule's own reasoning did not
anticipate that direction of difference.

**This is the self-guard doing its job, exactly as D48.12 and the session
prompt describe it -- not a bug, and it was not worked around.** No
re-tuning, no feature/window/lapse-rate change, no code edit to
`scripts/session39_sealed_test.py`, and no override was attempted. The
diagnostic above reused the frozen script's own functions unmodified,
purely to report values, not to make it proceed.

**What this leaves standing.** D48's one authorised look (D48.13) has not
been taken at any airport -- the sealed test year was opened (pulled,
decoded, and partially loaded) but the frozen script never reached
model-fitting for any airport, so there is no MAE, no PASS/FAIL, and
nothing yet to compare against the D48.12 pre-registered expectations, at
any of the five airports. Nothing about any earlier result changes: EGLC
F16, LFPG F30, DSM F47, YSDU F64 and RNO F82 all stand exactly as
reported, untouched by this session.

**Flagged for the owner, not decided here.** How to proceed is a real
choice, not a mechanical one: (a) decide the D48.8 ceiling rule itself was
too strict as written, and revise it in a new, written DECISIONS entry
before re-opening the sealed year under a corrected rule; or (b) trace the
specific dates and confirm the hypothesis above before trusting either
recipe's coverage; or (c) something else the owner sees that this session
does not. Whichever path is chosen, D48.13's "one look, and it stands"
rule means the sealed year should not simply be re-opened and re-run under
today's unmodified ceiling rule expecting a different outcome -- the rule
itself, not the data, is what needs a decision first.

**What this session did not do, on purpose.** Did not modify
`scripts/session39_sealed_test.py` or any part of the D48 recipe -- not
the features, model, window, elevation constants, or the D48.8 ceiling
rule. Did not work around, retry, or silently patch the tripped self-guard.
Did not fit any model or compute any sealed-year MAE, at any airport. Did
not pull or touch any date outside 2025-08-01..2026-07-31 for the sealed
pull (both bounds asserted in `scripts/session40_grib_pull.py` and
`scripts/session40_decode.py` before use). Did not commit the raw sealed-
year GRIB extracts (gitignored per D47) -- only the processed feature
file, drop log, and provenance are candidates for commit. Did not modify
`SPEC.md` or `RESULTS.md`. Nothing was committed.

---

## 2026-09-12 -- Session 41 finding: the F92 "EXCEEDS" days are BENIGN, and
the true mechanism is more precise than F92's own hypothesis -- the D48.8
guard compared two different stages of the same pipeline, not two forecast
sources' coverage. The guard is corrected; no model fit, no sealed-year
result seen.

**F93. Session 41 verifies the three "EXCEEDS" airports F92 found (EGLC,
LFPG, YSDU) and sanity-checks the two exact matches (DSM, RNO). Verdict:
BENIGN -- confirmed by real data, not assumed -- but the actual mechanism
is NOT the one F92 proposed as a hypothesis. No model was fit and no
sealed-year MAE, skill, or verdict was computed anywhere in this session
(the integrity boundary the session prompt set).** Script:
`scripts/session41_verify.py`, a read-only diagnostic that imports
`scripts/session39_sealed_test.py` as an unmodified library (its
`load_obs_all`, `load_grib_features`, `join_rows` and `AIRPORTS`/`SEALED_
FROM`/`SEALED_UNTIL` constants) and adds nothing that touches a model.
Full real output: `notes/session-41-verify-output.txt`. No new data was
pulled -- session 40's already-decoded `grib_features_sealed_window.csv`
and the existing sealed-year IEM/Open-Meteo files already on disk were the
only inputs, all read-only.

**What F92 guessed, restated.** F92 hypothesized that GRIB's sealed-year
pull had a cleaner (zero-gap) forecast-side record than Open-Meteo's own
`previous_day1` series had over the same year, at the three EXCEEDS
airports -- i.e. a genuine, if unanticipated, direction of source-quality
difference.

**What this session actually found: that hypothesis is FALSE.** Open-Meteo's
own sealed-year forecast series is independently rebuilt in this session,
row by row, straight from the real archive files
(`openmeteo_previousruns_gfs_global_<station>_2025-01-01_2025-12-31.json`
and `..._2026-01-01_2026-07-31.json`) -- not assumed, not quoted from an
older session. **At every one of the five airports, Open-Meteo's sealed-year
forecast series is 100% present and non-null: 365 of 365 rows at the target
hour, zero gaps.** There is no forecast-side coverage difference between
GRIB and Open-Meteo in the sealed year, at any airport. GRIB is not cleaner
than Open-Meteo here -- both are perfectly clean.

**The real mechanism: D48.8's ceiling compared the new recipe's PRE-
persistence row count against the old recipe's POST-persistence "scored
day" count -- two different stages of the same pipeline.** Every prior
airport's own sealed-test script (`session07_test.py` EGLC,
`session13_test.py` LFPG, `session18_test.py` DSM, `session24_test.py`
YSDU, `session29_test.py` RNO) computes its test-year row count in TWO
stages, not one:
- **stage A** ("paired test rows from part A" in each script's own saved
  output): the plain forecast+observation join, D14 pairing rule, nothing
  about persistence involved yet;
- **stage B** ("days every method is scored on", the "common" set): stage A
  further narrowed to days where YESTERDAY's observation is also available,
  because the persistence rung needs a genuine past value (SPEC 2.1d) and
  every rung -- raw GFS, persistence, climatology, mean-bias, ML-corrected
  -- is deliberately scored on the SAME shared day set in every prior
  session's design.

**D48.8's `PRIOR_SCORED_DAYS` constant held stage B's numbers (363, 363,
365, 347, 365 -- from the "days every method is scored on" line in each
airport's own saved sealed-test output, matching F16/F30/F47/F64/F82).**
But `scripts/session39_sealed_test.py`'s own `join_rows()` -- the function
that produces the new recipe's `test_rows`, whose count the guard
checks -- performs only stage A (a GRIB+observation join; it does not
narrow further for persistence availability, and by design its
`raw_mae`/`f3_mae`/`f5_mae` rungs are scored on the full stage-A set, with
only the separate `persist_mae` rung narrowed further inside `run_airport`
itself). **Comparing a stage-A count against a stage-B ceiling is comparing
two different definitions of "how many days were scored" within the very
same pipeline shape D48 already specifies -- not a genuine difference in
what either forecast source covers.**

**This session independently rebuilt BOTH stages, from raw data, for every
airport, and both reconcile exactly:**

```
station   test_rows(new)   OLD stage-A (rebuilt)   OLD stage-B=PRIOR   extra   extra=stage-A-vs-B gap?
EGLC            364               364                    363            1     YES (1 persistence-narrowed day)
LFPG            364               364                    363            1     YES (1 persistence-narrowed day)
DSM             365               365                    365            0     YES (no persistence narrowing at DSM)
YSDU            356               356                    347            9     YES (9 persistence-narrowed days)
RNO             365               365                    365            0     YES (no persistence narrowing at RNO)
```

**"OLD stage-A (rebuilt)" is this session's own independent reconstruction
of the existing recipe's pre-persistence join, straight from the real
Open-Meteo sealed-year archive and the same `obs_full` series
`session39_sealed_test.py` already loads -- not copied from any note.** It
matches the new (GRIB) recipe's own `test_rows` count EXACTLY, row for row,
at all five airports. And "OLD stage-B" (this session's own recomputation
of the persistence-narrowed common set, mirroring `run_airport()`'s own
`common_persist` loop character-for-character) matches D48.8's
`PRIOR_SCORED_DAYS` figures exactly too. **Both reconciliations are 5-for-5
exact matches, not approximate.**

**Every individual "extra" day was checked and is a genuine, single,
correctly-paired row -- not a double-count, duplicate, mis-dated row, or
wrong-day pairing.** For all 11 extra days (EGLC's 2025-11-22; LFPG's
2026-07-09; YSDU's nine: 2025-08-31, 2025-10-29, 2025-11-16, 2025-11-26,
2025-12-01, 2025-12-04, 2026-01-19, 2026-02-15, 2026-04-13 -- every one
independently reproduced by this session and an EXACT MATCH against the
specific dates already named in each airport's own existing sealed-test
notes file, `notes/session-07/13/24-check-output.txt`):
- the day has a real, decoded GRIB forecast (confirmed present, F92's own
  Task 1: zero GRIB decode drops anywhere) and a real IEM observation
  paired within the D14 15-minute rule (guaranteed by `load_obs_all`'s own
  construction -- a report outside 15 minutes never enters the series at
  all);
- Open-Meteo's OWN forecast for that exact date and hour is also a real,
  present, non-null value (printed for every extra day in the saved
  output) -- directly falsifying F92's forecast-side-gap hypothesis for
  every single one of these 11 days, not just in aggregate;
- YESTERDAY's observation is confirmed missing for every one of the 11 --
  the actual, verified reason the OLD recipe's stage-B narrowing (not any
  forecast-side gap) drops each of these specific days from its own
  published scored-day count.

**Duplicate/mis-dating check on the sealed GRIB feature file itself:**
`grib_features_sealed_window.csv` holds exactly 1,825 rows, 1,825 distinct
(station, date) keys, zero duplicates, zero unparseable or out-of-window
dates -- confirmed by a direct scan, not assumed from F92's own "0 drops"
claim.

**DSM and RNO's exact matches are now confirmed correct for the right
reason, not coincidental.** Both reconcile at stage A AND stage B
simultaneously (365=365=365 at each), because neither airport has any
persistence-narrowing loss in the sealed year (0 days at each, matching
F82's own "paired rows kept: 365" and D44.7's advance prediction) --
there was never a second stage to diverge from at these two airports,
which is exactly why they never showed an EXCEEDS symptom in F92.

**Verdict: BENIGN.** Every extra day is a legitimate GRIB-forecast/
observation pair the old recipe's own raw+obs join also produces
identically; the divergence F92 found is fully and exactly explained by
which of the OLD recipe's own two internal stages `PRIOR_SCORED_DAYS` was
built from, not by any GRIB-vs-Open-Meteo coverage difference. No pairing
bug, no double-count, no mis-dated row, at any of the 11 extra days or at
either of the two exact-match airports.

**D48.8's guard is corrected accordingly -- a guard-only change, nothing
outcome-affecting.** `PRIOR_SCORED_DAYS` (the old recipe's stage-B, "days
every method is scored on" figures: 363/363/365/347/365) is replaced with
`SEALED_ROW_CEILING` (this session's own verified stage-A, GRIB+obs
availability figures: **EGLC 364, LFPG 364, DSM 365, YSDU 356, RNO 365**
-- exactly the `test_rows` counts already reconciled above), because
stage A -- the plain forecast+observation join -- is what `join_rows()`
and the guard it feeds actually measure; comparing it against anything
but another stage-A figure was the mis-specification. The corrected
figures are fixed as a pre-registered expectation, the same role
`EXPECTED_TRAIN_ROWS` already plays for the training window, not a live
recomputation -- session 42 reads the identical, already-pulled sealed
feature file session 40 produced, so these counts will not change between
sessions. **Explicitly unchanged: the features (D48.4), the model and its
settings (D48.6), the training window (D48.7) and its `EXPECTED_TRAIN_
ROWS` guard, the five elevation/lapse-rate constants (D48.3), the bar
(D48.11), and every other self-guard (out-of-window date, missing-file).
This correction was made with NO model fit and NO sealed-year result of
any kind seen -- only availability/row counts, which say nothing about
whether the 5-feature model beats raw GFS and are shared identically
across all four rungs (raw GFS, persistence, 3-feature, 5-feature) --
exactly the integrity boundary the session prompt set out in advance.**

**The exact script edit**, limited to the D48.8 constant and the block that
reads it in `run_airport()` (full diff verified via `git diff`, reproduced
in the session's own report): the `PRIOR_SCORED_DAYS` dict (values 363,
363, 365, 347, 365, with a comment describing it as the "existing recipe's
own scored-day count") is renamed `SEALED_ROW_CEILING` (values 364, 364,
365, 356, 365, with a comment recording this session's finding), and the
`sub()`/print/`AssertionError` text in `run_airport()` is updated to name
the corrected basis and cite F93 instead of F16/F30/F47/F64/F82. The
comparison itself (`if len(test_rows) > ceiling: raise`) is unchanged in
shape -- only the constant's values, name, and surrounding comments
changed. Confirmed by `py_compile` and a clean import (exercising the same
LightGBM/libomp workaround every session-3x script uses) after the edit,
without running `main()` or fitting anything.

**What this session did not do, on purpose.** Did not fit any model. Did
not compute any sealed-year MAE, skill, or verdict, for any rung, at any
airport. Did not change the features (D48.4), the model or its settings
(D48.6), the training window or `EXPECTED_TRAIN_ROWS` (D48.7), the five
elevation/lapse-rate constants (D48.3), or the bar (D48.11) -- confirmed by
diff. Did not touch the out-of-window-date, training-row-count, or
missing-file guards. Did not pull any new data -- only files session 40
and earlier sessions already pulled were read, all read-only. Did not take
D48's authorised look (D48.13) -- that remains session 42's job, now
against a corrected ceiling. Did not modify `SPEC.md` or `RESULTS.md`.
Nothing was committed.

---

## Moved by session 65 (2026-09-23)

The archive criterion (D46, live in `DECISIONS.md`) applied to the feature-selection programme in full: **F97, F98, F99, F100, F101, F102, F103, F104, F105, F106, F107, F108, F109** and **D52, D53, D54, D55, D56, D57, D58**. Every one of these entries is settled -- the programme is closed (DECISIONS D59.2) and its headline is now carried forward into `SPEC.md` section 8 and `RESULTS.md` section 6, so no live open question or `STATUS.md`'s own "Next" section needs any of their specific wording, only their numbers, which resolve here unchanged. **D51** (the reserved-year rule) and **F96** (the multi-year backtest) meet the same settled criterion but are deliberately NOT moved -- DECISIONS D59.4 keeps them live because Q30's own second-test-year branch (D59.5) needs both word-for-word. The blocks below are exactly what was cut, unedited.

---

## 2026-09-18 — Session 47 finding: feature-family availability probe
(radiation, upper-air, moisture, pressure, precipitation) — a map, not an
experiment

**F97. A cheap availability probe, the same shape as sessions 31 (F85) and
35 (F88): finds out which new GRIB feature families exist, under what exact
label/level, at the project's own forecast lead, and how far back — so a
later session can plan feature-experiment ordering on facts rather than
guesses. It builds nothing, models nothing, pulls no bulk data, derives no
feature, and picks no ordering.** Script: `scripts/session47_availability_
probe.py` (new, read-only against the public GRIB archive). Raw idx extracts
and their `.meta.txt` provenance: `data/raw/diagnostics/session47/` (8 `.idx`
files, one per sample-date x cycle/lead combination). Summary tables:
`data/raw/diagnostics/session47/session47_availability_map.csv` (27 rows) and
`session47_precip_rno_spotcheck.csv` (4 rows).

**Method.** Two sample dates, both outside the sealed test year (2025-08-01
onward, SPEC 2.1a/4.3): the v16 floor (2021-03-24, run date 2021-03-23) and a
recent pre-test date (2025-06-15, run date 2025-06-14). For each, the four
distinct (cycle, forecast-hour) combinations the five airports' own target
hours already select (SPEC 3.4, DECISIONS F89's lead convention: cycle
floor(HH/6)*6 on day D-1, forecast hour 24 + (HH mod 6)) — cycle 12z/lead
f024 (EGLC, LFPG), cycle 18z/lead f024 (DSM), cycle 00z/lead f026 (YSDU),
cycle 18z/lead f026 (RNO). For every candidate variable: presence and exact
label/level was read directly from the real `.idx` inventory at both dates
(never assumed), and a real value was confirmed by byte-range-fetching the
message and decoding it with eccodes — at EGLC's own established Open-Meteo
grid point (SPEC 3.4) for the general spot-check, and additionally at RNO's
own grid point for the precipitation family (of particular interest there).
No bulk pull, no date range, no all-five-airport pull — one location's grid
is enough to prove a variable exists (the inventory is global) and decodes
to a real number.

**Result: every one of the 27 candidate variables is present, identically
labelled, at both the v16 floor and the recent date, at the airports' own
forecast lead, and decodes to a real, non-null value.** No candidate was
found absent at either date. Full per-family detail:

```
RADIATION (spot-check: EGLC, 2025-06-15T12:00 UTC; also present 2021-03-24)
  variable        label found              v16  recent  lead  timing
  DSWRF:surface   surface                  Y    Y       Y     18-24h ave (EGLC/LFPG/DSM); 24-26h ave (YSDU/RNO)
  USWRF:surface   surface                  Y    Y       Y     same averaging pattern as DSWRF
  USWRF:toa       top of atmosphere        Y    Y       Y     same averaging pattern as DSWRF
  DLWRF:surface   surface                  Y    Y       Y     same averaging pattern as DSWRF
  ULWRF:surface   surface                  Y    Y       Y     same averaging pattern as DSWRF
  ULWRF:toa       top of atmosphere        Y    Y       Y     same averaging pattern as DSWRF
  LCDC            low cloud layer          Y    Y       Y     BOTH instantaneous (Nh fcst) and 6h/2h-ave variant exist
  MCDC            middle cloud layer       Y    Y       Y     BOTH variants exist, same as LCDC
  HCDC            high cloud layer         Y    Y       Y     BOTH variants exist, same as LCDC
  (DSWRF/DLWRF exist at surface only, not top of atmosphere — confirmed absent there, not just unchecked)

UPPER-AIR / VERTICAL STRUCTURE (spot-check: EGLC)
  variable        label found     v16  recent  lead  timing
  TMP:925 mb      925 mb          Y    Y       Y     instantaneous (Nh fcst)
  TMP:850 mb      850 mb          Y    Y       Y     instantaneous
  TMP:700 mb      700 mb          Y    Y       Y     instantaneous
  HGT:500 mb      500 mb          Y    Y       Y     instantaneous
  HGT:850 mb      850 mb          Y    Y       Y     instantaneous
  UGRD:850 mb     850 mb          Y    Y       Y     instantaneous
  VGRD:850 mb     850 mb          Y    Y       Y     instantaneous
  RH:850 mb       850 mb          Y    Y       Y     instantaneous

MOISTURE (spot-check: EGLC)
  variable        label found                                    v16  recent  lead  timing
  RH:2m           2 m above ground                                Y    Y       Y     instantaneous
  DPT:2m          2 m above ground                                Y    Y       Y     instantaneous
  SPFH:2m         2 m above ground                                Y    Y       Y     instantaneous
  PWAT            entire atmosphere (considered as a single layer) Y    Y       Y     instantaneous

PRESSURE / SYNOPTIC (spot-check: EGLC)
  variable        label found      v16  recent  lead  timing
  PRMSL           mean sea level   Y    Y       Y     instantaneous
  PRES:surface    surface          Y    Y       Y     instantaneous

PRECIPITATION (spot-check: EGLC, and RNO's own grid point)
  variable        label found     v16  recent  lead  timing
  APCP:surface    surface         Y    Y       Y     TWO accumulation windows exist: a short one matching the ave-field
                                                       window (18-24h at lead 24, 24-26h at lead 26) and a cumulative
                                                       one since forecast start ("0-1 day" at lead 24, "0-26 hour" at
                                                       lead 26 — a labelling-format quirk, day vs hour units)
  PRATE:surface   surface         Y    Y       Y     BOTH instantaneous (Nh fcst) and 18-24h/24-26h-ave variant exist
  SNOD:surface    surface         Y    Y       Y     instantaneous (a state field, not an accumulation, despite the name)
  WEASD:surface   surface         Y    Y       Y     instantaneous (a state field, same as SNOD)
```

**Per-family read.**

*Radiation — available but awkward.* All eight fields exist, correctly
labelled, back to the v16 floor. The awkward part: the "ave fcst" window is
not fixed — it runs from the nearest preceding synoptic 6-hour mark to the
forecast lead, so it is a genuine 6-hour average at EGLC/LFPG/DSM (lead 24,
window 18-24h) but only a 2-hour average at YSDU/RNO (lead 26, window
24-26h). A feature built from these fields would carry a different averaging
window at different airports purely as a byproduct of each airport's own
target hour (SPEC 4.1) — a real cross-airport inconsistency to design around,
not a missing-data problem. Cloud-layer fields (LCDC/MCDC/HCDC) additionally
carry an instantaneous variant at the same level, matching the convention the
project's own `TCDC` feature already uses (session 37's own disambiguation
code, DECISIONS-archive F90); a richer-features experiment using low/mid/high
cloud instead of (or alongside) total cloud cover could reuse that same
instantaneous convention directly.

*Upper-air / vertical structure — available and clean, the headline result.*
Every field named in the session prompt (TMP at 925/850/700 mb, HGT at
500/850 mb, UGRD/VGRD/RH at 850 mb) is present, identically labelled, back to
the v16 floor, genuinely a forecast field at the airports' own ~24-26h lead
(not an analysis-only field), and instantaneous — no averaging-window
complication at all. **This is the exact thing DECISIONS F85 found blocked on
Open-Meteo** ("upper-air (925/850 hPa) temperature is not available in any
leakage-safe form on this API/offset, at any date or airport") — the family
the GRIB build was specifically expected to unlock (session 47's own opening
framing) is confirmed genuinely unlocked, with no caveat.

*Moisture — available and clean.* All four fields (RH:2m, DPT:2m, SPFH:2m,
PWAT) are present, correctly labelled, instantaneous, back to the v16 floor.
Dew-point-vs-temperature spread is derivable later from DPT:2m plus the
already-used temperature field, but nothing was derived this session, per
scope.

*Pressure / synoptic — available and clean.* PRMSL and PRES:surface are both
present, correctly labelled, instantaneous, back to the v16 floor. Pressure
*tendency* would need two consecutive runs' worth of this field to derive
later — only the base fields were confirmed here, per scope.

*Precipitation — available but awkward.* All four fields exist back to the
v16 floor. APCP carries two different accumulation windows (see table above),
so a feature built from it must pick one deliberately, and that choice
interacts with the same lead-dependent-window issue radiation has. PRATE
mirrors APCP's own instantaneous/averaged duality. SNOD and WEASD are both
clean instantaneous state fields (not accumulations, despite what their names
might suggest). **The RNO spot-check (2025-06-15T20:00 UTC) returned zero for
all four precipitation fields at Reno's own grid point** — this is a real,
plausible dry/snow-free reading, not a decode failure: each field's own
grid-wide maximum on the same message is well above zero (e.g. APCP's grid
max 64.5 kg/m^2 elsewhere on the same field), so the field itself is not
all-null at that valid time, only Reno's own point is dry.

**What this does not decide.** No feature-experiment ordering was chosen —
that is explicitly out of scope for this session and is planned separately,
with this map in hand. No feature was derived, joined, or added to any
dataset. No model was touched. Nothing about F16–F96 changed.

**What this session did not do, on purpose.** Did not pull any bulk or
date-range data — 8 `.idx` text inventories and 31 small byte-range message
fetches (27 general spot-checks + 4 Reno-specific precipitation spot-checks),
all outside the sealed test year. Did not use any date before 2021-03-24
(v15 is excluded, D48.7) as available. Did not decide which family to try
first, or in what order. Did not derive any feature (e.g. dew-point spread,
pressure tendency) from the confirmed ingredients. Did not modify `SPEC.md`
or `RESULTS.md`. Nothing was committed.

---

## 2026-09-20 — Session 49 finding: E1 (upper-air/vertical-structure) feature
set built and validated — a data build, no model fit, reserved year untouched

**F98. Pulls, decodes, and joins the three E1 upper-air fields (TMP at
925/850/700 hPa) onto the existing 5-feature GRIB dataset, at every date
that dataset already carries OUTSIDE the reserved 2024-25 confirmation year
(D51). Data-build-only, per the session prompt: no model was fit, no MAE or
CV was computed, and 2024-08-01..2025-07-31 was never loaded, pulled, or
joined.** Script: `scripts/session49_upper_air_pull.py` (new). Full real
output: `notes/session-49-upper-air-output.txt`. Outputs: `data/processed/
session49_v16_window_with_upper_air.csv` (6,128 rows), `data/processed/
session49_sealed_window_with_upper_air.csv` (1,826 rows), `data/processed/
session49_upper_air_join_drops.csv` (0 rows), `data/raw/diagnostics/
session49/session49_pull_manifest.csv` (19,083 rows, provenance only — see
below on why no raw bytes were kept).

**Two design decisions made before any pull ran, both stated in the
script's own module docstring:**
1. **No elevation/lapse-rate correction on t925/t850/t700.** SPEC 7.2's
   7.429 degC/km correction fixes a *surface* grid-cell elevation
   mismatch; 925/850/700 hPa are fixed pressure surfaces, not tied to
   surface terrain, so only bilinear horizontal interpolation was applied
   — exactly as the session prompt required, confirmed in the script's own
   printed output before the pull started.
2. **No new 2 m-temperature pull.** The session prompt asked for the
   lapse-rate feature to use the RAW, uncorrected 2 m forecast temperature,
   not the elevation-corrected `temperature_grib_c` the existing 5-feature
   model already uses. Rather than re-pulling 2 m temperature (already
   decoded once for the existing dataset), `t2m_raw` was recovered
   algebraically from data already on disk — `t2m_raw = temperature_grib_c
   - correction_c`, using each airport's own fixed D48.3/F90 constant
   (`data/raw/diagnostics/session37/session37_elevation_correction_params.csv`)
   — needing no new GRIB request at all.

**A third decision, forced by disk space, not by the session prompt: no raw
GRIB2 bytes were kept on disk for this pull.** Free space was ~11 GiB at
the start of this session (session 37's own ~20 GB raw surface-field cache,
gitignored under D47, already occupies this disk); a second full-window,
3-level raw cache built the same way sessions 37/40 built theirs — save
every message permanently, decode later — was estimated at 15+ GB more
(based on the existing cache's own ~846 KB/message average), which this
environment does not have. Instead, each message was byte-range-fetched,
decoded immediately with eccodes, and the bytes discarded — the
fetch-decode-discard pattern session 47's own probe already used, extended
here to a full multi-year pull. A per-request manifest (run_date, cycle,
lead, level, stations, status, detail — no bytes) stands in as the
provenance record, consistent with D47's "manifest, not bytes" policy for
large, re-fetchable sources, taken one step further since not even a local
disposable cache was kept this time. Free disk space was ~12 GiB after the
pull — essentially unchanged, confirming no bytes leaked past the
decode-then-delete step.

**Date range and guard check (session prompt Step 5).** The date list was
built from the existing 5-feature dataset itself (`grib_features_v16_window.csv`,
`grib_features_sealed_window.csv`), not assumed to be every calendar day —
any row whose `target_date` fell inside 2024-08-01..2025-07-31 was skipped
at the point of loading, never held in memory past that line. This produced
a **train span of 2021-03-24..2024-07-31 (1,226 distinct dates)** and a
**sealed span of 2025-08-01..2026-07-31 (365 distinct dates)**, 1,591 dates
total — the same total day-count as the existing dataset's own two files
combined, since the reserved year's ~365 days are simply absent rather than
replaced. Before any pull request was made, both spans were checked with
`scripts/session48_reserved_year.py`'s own `assert_reserved_year_excluded()`
(train==test, since this is a continuous span, not a train/test fold) —
both passed with no exception — and a further defensive per-date scan of
all 1,591 dates confirmed zero reserved-year dates present. Real output:
"Guard check PASSED ... no reserved-year date is in the pull list."

**Pull result: complete, zero failures.** 6,361 distinct (run_date, cycle,
lead) combos were needed (the same four-distinct-files-per-day structure
session 37/F90 already established); 19,083 message fetches (3 levels x
6,361 combos) all succeeded — **0 FAIL rows in the manifest**. Per-field,
per-station-instance counts (a combo shared by EGLC+LFPG counts twice):
t925 7,952/7,952, t850 7,952/7,952, t700 7,952/7,952. The pull took 56.4
minutes at 48-way concurrency (~1.88 combos/s), the same order of
throughput session 37's bulk pull achieved.

**Join result: exact, zero drops, at every airport.** Row counts before and
after the join match exactly at all five airports in both spans (v16_window:
EGLC/LFPG 1,226, DSM/YSDU/RNO 1,225; sealed_window: all five 365) — the
`session49_upper_air_join_drops.csv` log is empty. The v16_window counts
reproduce the existing dataset's own per-airport shortfall from the
idx-mismatch dates (F90) exactly (DSM/YSDU/RNO one day short of EGLC/LFPG),
confirming the join used the existing dataset's real dates, not an assumed
continuous calendar.

**Validation: sanity ranges, and one genuine, reportable anomaly at RNO.**
Real min/max/mean/null-count per new column, per airport (full numbers in
the real output; summary here):

```
station  t2m_raw (mean)  t925 (mean)  t850 (mean)  t700 (mean)  colder-with-height?
EGLC         15.00           7.86         3.81        -3.60      YES
LFPG         16.17           9.33         5.11        -2.58      YES
DSM          15.57          10.12         7.20         0.23      YES
YSDU         22.05          15.66         9.85         1.17      YES
RNO          16.18          20.79        16.13         2.88      NO -- FLAG
```

Every column is null-free at every airport (n_null=0 throughout), and every
one of the 19,083 requested messages decoded successfully — this is not a
decode failure. **At RNO, and only at RNO, the surface-to-925hPa ordering
inverts**: t925 averages ~4.6 degC *warmer* than the surface (t2m_raw), and
t850 sits almost exactly level with the surface (mean lapse_rate_t2_t850 =
0.05 degC, range -1.75 to +1.25, against 8-12 degC average lapse at the
other four airports). **The likely physical cause, stated here as a
plausible explanation, not verified further this session (out of scope):**
RNO's own airport elevation is 1,345 m (SPEC 3.4, the highest in the
project by a wide margin), while the *standard-atmosphere* altitude of the
925 hPa surface is roughly 760 m and of 850 hPa roughly 1,460 m — both close
to or below Reno's own ground level. A fixed-pressure-surface GRIB field at
a level that sits at or below a location's real terrain is extrapolated
below-ground by the model's own analysis scheme rather than representing a
real measured atmospheric layer, which would produce exactly this kind of
anomalous, non-monotonic reading. **This is flagged for session 50, not
fixed here**: an E1 lapse-rate feature built from t2m_raw/t850 may behave
very differently at RNO than at the other four airports, for a real
physical reason tied to Reno's own elevation, not a data-quality problem —
worth watching specifically if RNO's own richer-features rescue (F94, F96)
turns out to interact with this feature differently than the other
airports do.

**Spot-check (session prompt Step 7, last bullet).** F97's own
decoded-value sample date, 2025-06-15, now falls **inside** the reserved
2024-25 confirmation year — a direct consequence of D51 being decided one
session after F97 ran, not a bug in either session. This session's own
pull therefore correctly never touches that date. The spot-check instead
used F97's other confirmed date, the v16 floor (2021-03-24), where F97
confirmed TMP:925/850/700 mb **present** at EGLC's own combo but did not
decode a value there (F97's own decode call used only the recent-date idx).
This session's own EGLC 2021-03-24 row decodes to t925=3.07, t850=0.251,
t700=-7.742 degC — physically plausible and correctly colder with height.

**What this session did not do, on purpose.** Did not fit any model,
compute any MAE, or run any CV — that is session 50's job. Did not load,
pull, reference, or join a single row of the reserved 2024-08-01..2025-07-31
confirmation year (D51) — enforced both by the shared guard function and a
defensive per-date scan, confirmed with 0 reserved dates found. Did not
pull moisture, pressure, or any other E2+ family — upper-air (TMP at
925/850/700 mb) only. Did not re-run or touch the frozen 5-feature sealed-
test script. Did not apply the surface elevation/lapse-rate correction to
any of the three new fields. Did not modify `SPEC.md` or `RESULTS.md`.
Nothing was committed. Script: `scripts/session49_upper_air_pull.py` (new).
Full real output: `notes/session-49-upper-air-output.txt`.

---

## 2026-09-20 — Session 50 finding: the staged E1 (upper-air/vertical-
structure) experiment — a reading, not a verdict; reserved year untouched

**F99. Fits four feature variants (B, B+L, B+Lv, B+v) on the three
non-reserved `EXPERIMENT_FOLDS` (D51) to read whether the upper-air family
(F98) adds skill on top of the frozen 5-feature GRIB baseline. This is a
LEARNING experiment, not a sealed-bar test — it reports a grid, not a
pass/fail verdict (the family call is made in review, per the session
prompt). The reserved 2024-08-01..2025-07-31 confirmation year was never
read, at all, this session.** Script: `scripts/session50_e1_experiment.py`
(new). Full real output: `notes/session-50-e1-experiment-output.txt`.
Tables: `data/processed/session50_e1_experiment_grid.csv` (60 rows: 5
airports x 3 folds x 4 variants) and `data/processed/
session50_e1_experiment_summary.csv` (36 rows: fold-averaged-per-airport,
airport-averaged-per-fold, and grand-overall levels).

**The four variants, all on D21.4/D48.6's unchanged LightGBM settings, no
per-airport feature selection:**
- **B** — the frozen 5-feature set (`temp`, `season_sin`, `season_cos`,
  `cloud_cover`, `wind_speed_10m`), REFIT on these three folds (not a reuse
  of F94/F96, which were fit on different windows).
- **B+L** — B plus `lapse_rate_t2_t850` (one added feature).
- **B+Lv** — B+L plus `t850`, `t925`, `t700` (four added features total).
- **B+v** — B plus `t850`, `t925`, `t700`, WITHOUT the derived lapse rate.

**Sanity check 1 (session prompt "First," item 1) — PASS, checked on every
row, not a spot check.** `t2m_raw == round(temperature_grib_c -
elevation_constant, 3)` (D48.3/F90) was verified against all 7,952 rows of
both session49 output files (both spans, all five airports): max absolute
difference 0.000000000 at every airport (EGLC +0.2486, LFPG -0.1697, DSM
-0.1106, YSDU +0.2461, RNO +2.0436 — signs and magnitudes match D48.3
exactly, RNO's the largest as expected). No STOP triggered.

**Sanity check 2 (item 2) — PASS.** All three `EXPERIMENT_FOLDS` entries
(2022-23, 2023-24, truncated 2025-26) cleared
`assert_reserved_year_excluded()` before any data was loaded. No STOP
triggered.

**An unplanned but strong internal-consistency signal.** The `2025-26`
fold's `B` variant (refit 5-feature baseline, same features as F94/F96,
trained on one fewer year than F94 — 1,222-1,225 days vs F94's 1,591,
because training may not reach the reserved year) reproduces F94/F96's own
raw-GFS and persistence MAE and row counts almost exactly at every airport:
EGLC raw 1.2536 vs F94 1.254 (n=364 vs 364), LFPG 1.3822 vs 1.382 (n=364 vs
364), DSM 1.7334 vs 1.733 (n=365 vs 365), YSDU 1.3167 vs 1.317 (n=356 vs
356), RNO 1.5116 vs 1.512 (n=365 vs 365). This was not asked for but
confirms the pipeline (join, features, model settings) is a correct
reproduction of the frozen recipe, the same kind of check F96's own
`2025-26` fold performed against F94.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, n=15
airport-folds per variant):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+L       1.260      -0.024       +1.9%
B+Lv      1.258      -0.026       +2.0%
B+v       1.271      -0.013       +1.0%
```

**Fold-averaged per airport (mean across the three folds), skill vs B:**

```
station   B+L     B+Lv    B+v
EGLC     +2.7%   +1.6%   +1.6%
LFPG     +2.6%   +2.2%   +1.2%
DSM      +2.2%   +2.7%   -0.1%
YSDU     +2.1%   +1.4%   +0.5%
RNO      -0.0%   +1.8%   +2.0%
```

**The staged question, answered plainly.** (a) `lapse_rate_t2_t850` alone
(B+L) already captures nearly all of the family's benefit at the grand
level: +1.9% skill on one added feature. (b) Adding the raw levels on top
(B+Lv) adds almost nothing further at the grand level (+2.0%, a 0.1-point
gain over B+L) — the derived form is doing almost all of the work overall.
(c) The raw levels WITHOUT the derived form (B+v) underperform B+L at every
fold-averaged airport except RNO (+1.0% overall, clearly the weakest of the
three additions) — the model does better handed the physically-motivated
difference directly than left to reconstruct it from three raw
temperatures.

**DSM, the diagnostic (F96 flagged it as the airport with the most
headroom, since cloud/wind were marginal-to-slightly-negative there): a
real positive signal, and the one airport (besides RNO) where the raw
levels add something the derived form alone does not.** B+L +2.2%, B+Lv
+2.7% (DSM's own best variant), B+v -0.1% (flat/negative — the same shape
cloud/wind showed at DSM in F96). The honest read: upper-air does help at
DSM — lapse rate helps, and the raw levels add a further real increment on
top of it — unlike cloud/wind's own marginal-to-negative read there.

**RNO, pre-registered to behave oddly (F98: t925 there is a below-ground
extrapolation, `lapse_rate_t2_t850` partly degenerate) — the prediction
held, with a genuinely interesting twist.** B+L +0.0% (flat — the derived
lapse-rate feature adds essentially nothing at RNO, exactly as F98
predicted), but B+Lv +1.8% and B+v +2.0% (RNO's own best variant of the
three) — the RAW pressure-level temperatures still carry real, usable skill
at RNO even though the specific derived difference (`t2m_raw - t850`) does
not. This answers the empirical question F98 raised ("whether the
extrapolated value still carries usable signal") with a qualified yes: the
extrapolated field itself still helps, even though the difference computed
from it does not. RNO ran with the identical feature set as every other
airport throughout this experiment — no exclusion, no RNO-specific
feature, per the session prompt's explicit instruction.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — session49's own output files already exclude it, and this
session's own defensive per-row scan found 0 reserved-year rows, on top of
the guard check on all three folds before any data was loaded. Did not
compute any pass/fail verdict anywhere — the four-variant grid is reported;
the family call (whether to keep lapse rate, drop the raw levels, or
neither) is left to review, per the session prompt. Did not do any
per-airport feature selection — identical features at every airport, in
every variant, including RNO. Did not touch any E2+ family (moisture,
pressure, radiation, precipitation). Did not pull any new data — reused
session 49's own output files unchanged. Did not modify `SPEC.md` or
`RESULTS.md`. Nothing was committed. Script:
`scripts/session50_e1_experiment.py` (new). Full real output: `notes/
session-50-e1-experiment-output.txt`.

---

## 2026-09-20 — Session 51 decision: the E1 (upper-air) family verdict, from
the owner's review of F99

**D52. Verdict: E1's adopted contribution to the eventual combine-phase
sweep baseline is the single derived feature `lapse_rate_t2_t850` (the
`B+L` variant). The three raw pressure-level temperatures — `t850`,
`t925`, `t700` — are NOT adopted into the sweep baseline.**

**RNO's raw-level signal is parked, not dropped.** In the F99 grid the raw
pressure levels carry a real, fold-robust skill increment at RNO
specifically (`B+v` skill vs B was +1.4% / +2.0% / +2.7% across the three
folds, while `B+L` was flat-to-slightly-negative there — F99's own
fold-by-fold table). This is recorded as an explicit candidate to revisit
in the later combine phase, where joint value and redundancy across
families are weighed — it is not carried into the E-sweep now.

**Rationale, kept plain.**
(a) `B+L` captures +1.9% of the +2.0% maximum grand-overall skill (F99) on
one added feature instead of four — parsimony with near-equal skill.
(b) The only fold-robust reason to add the raw levels is RNO, and RNO is
already carried to about +11% skill by cloud/wind in the frozen baseline
(F94, stable across all four years in F96), so E1 need not also rescue it.
(c) The DSM case for the raw levels is a single fold (2025-26, F99's own
table), the year F96 flagged as unrepresentative — the weakest evidence in
the grid. Per-fold basis: `data/processed/session50_e1_experiment_grid.csv`.

**This is provisional.** Like every family in the sweep, `lapse_rate_t2_t850`
is confirmed only when the single final feature set is checked on the
reserved year once, at the finish line (D51) — not now.

**Measurement baseline is unchanged.** E2 and every later family in the
sweep are measured against the frozen 5-feature baseline B, **not** against
`B+L`. `B+L` enters only at the combine phase. Cites F99.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`
— the feature-selection programme is exploratory work toward a possible
future locked method, not yet folded into the spec. Did not fit any model
or compute any new figure — every number above is copied from and cited to
F99. Did not touch the reserved 2024-08-01..2025-07-31 confirmation year.

---

## 2026-09-20 — Session 52 finding: the staged E2 (moisture) experiment — a
reading, not a verdict; reserved year untouched

**F100. Fits four feature variants (B, B+D, B+Dv, B+v) on the three
non-reserved `EXPERIMENT_FOLDS` (D51) to read whether the moisture family
(built and validated in session 51, no DECISIONS finding number of its
own assigned there) adds skill on top of the frozen 5-feature GRIB
baseline. This is a LEARNING experiment, not a sealed-bar test — it
reports a grid, not a pass/fail verdict (the family call is made in
review, per the session prompt, mirroring F99). The reserved
2024-08-01..2025-07-31 confirmation year was never read, at all, this
session.** Script: `scripts/session52_e2_experiment.py` (new). Full real
output: `notes/session-52-e2-experiment-output.txt`. Tables: `data/
processed/session52_e2_experiment_grid.csv` (60 rows: 5 airports x 3 folds
x 4 variants) and `data/processed/session52_e2_experiment_summary.csv`
(36 rows: fold-averaged-per-airport, airport-averaged-per-fold, and
grand-overall).

**The four variants, all on D21.4/D48.6's unchanged LightGBM settings, no
per-airport feature selection:**
- **B** — the frozen 5-feature set, REFIT on these three folds (not a
  reuse of F94/F96). Not B+L either — D52's own baseline-unchanged rule.
- **B+D** — B plus `dewpoint_depression_t2m_floored` (one added feature).
- **B+Dv** — B+D plus the raw moisture fields, `v = {relative_humidity_2m,
  specific_humidity_2m, dew_point_2m}` (four added total).
- **B+v** — B plus the raw moisture fields only, WITHOUT the derived
  depression.

**Task 1, item 1 (reserved-year guard) — PASS.** All three `EXPERIMENT_
FOLDS` entries cleared `assert_reserved_year_excluded()` before any data
was loaded.

**Task 1, item 2 (moisture-feature integrity check) — PASS, checked on
every row, not a spot check.** `dewpoint_depression_t2m == round(t2m_raw -
dew_point_2m, 3)` holds exactly (max abs diff 0.0) at all 7,952 rows of
both session51 output files, across all five airports; zero null fields in
`relative_humidity_2m`, `dew_point_2m` or `specific_humidity_2m` anywhere.

**Task 1, item 3 (the depression floor) — applied, one row changed, exactly
as expected.** `dewpoint_depression_t2m_floored = max(dewpoint_depression_
t2m, 0)` changed exactly 1 of 7,952 rows — DSM 2024-01-26, -0.003 -> 0.000
— the same saturation-boundary row session 51's own build already
flagged. The original column is kept intact; the floor applies only
in the feature matrix.

**An unplanned but strong internal-consistency signal, the same check F99
ran.** The `2025-26` fold's `B` variant (refit 5-feature baseline, trained
on one fewer year than F94 because training may not reach the reserved
year) reproduces F94/F96's own raw-GFS and persistence MAE and row counts
almost exactly at every airport: EGLC raw 1.2536 vs F94 1.254 (n=364 vs
364), LFPG 1.3822 vs 1.382 (n=364 vs 364), DSM 1.7334 vs 1.733 (n=365 vs
365), YSDU 1.3167 vs 1.317 (n=356 vs 356), RNO 1.5116 vs 1.512 (n=365 vs
365) — confirming the pipeline (join, features, model settings) is a
correct reproduction of the frozen recipe.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, n=15
airport-folds per variant):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+D       1.233      -0.051      +4.0%
B+Dv      1.231      -0.053      +4.1%
B+v       1.235      -0.049      +3.8%
```

**Fold-averaged per airport (mean across the three folds), skill vs B:**

```
station   B+D     B+Dv    B+v
EGLC     +2.9%   +2.1%   +1.4%
LFPG     +2.7%   +2.0%   +2.7%
DSM      +6.2%   +6.4%   +6.4%
YSDU     +2.0%   +3.2%   +3.1%
RNO      +4.8%   +5.5%   +4.1%
```

**The staged question, answered plainly.** (a) `dewpoint_depression_t2m_
floored` alone (B+D) already captures nearly all of the family's
grand-overall benefit: +4.0% of the +4.1% maximum (B+Dv), on one added
feature. (b) Adding the raw fields on top (B+Dv) adds almost nothing
further at the grand level (+4.1%, a 0.1-point gain over B+D) — the same
shape E1's B+Lv showed over B+L. (c) Unlike E1, the raw fields WITHOUT the
derived form (B+v) are close behind the derived form rather than clearly
weaker — B+v (+3.8%) trails B+D (+4.0%) by only 0.2 points grand-overall,
and at two airports (LFPG, DSM) B+v ties or beats B+D outright. Moisture's
raw fields carry real standalone signal in a way E1's raw pressure-level
temperatures did not (F99's B+v was clearly the weakest addition
everywhere but RNO; E2's is not).

**DSM, the diagnostic (F96: most headroom; F99: upper-air did help there):
the moisture family's strongest and most fold-robust result.** DSM is the
best-skilled airport under every variant (B+D +6.2%, B+Dv +6.4%, B+v
+6.4%) and the only airport where all three per-fold readings are positive
and close together (+5.7%/+6.9%/+5.9% for B+D) — a fold-robust result, not
one fold carrying the average.

**Per-fold caution — two airports where the fold-averaged figure hides a
real split.** **EGLC's B+D fold average (+2.9%) is carried entirely by the
two earlier folds and reverses in the most recent one**: 2022-23 +5.8%,
2023-24 +4.2%, but 2025-26 -1.6% (B+Dv -2.1%, B+v -3.1% — all three
moisture variants lose to B at EGLC in the 2025-26 fold specifically).
**RNO's B+D is flat-to-slightly-negative in the thinnest fold** (2022-23
-0.2%) but strong in the other two (2023-24 +7.0%, 2025-26 +7.7%) — the
same thin-fold weak-read pattern F96 and D52 already named for the
2022-23 fold generally, not a new concern. No other airport shows this
kind of fold split; LFPG, DSM and YSDU are positive in all three folds
under every variant.

**Feature importances (gain-based, percent of the variant's own total
gain, averaged across the three folds) — B+D and B+v, per airport, per
the session prompt's own instruction.** `dewpoint_depression_t2m_floored`
is B+D's leading or near-leading feature at every airport (17.8% at RNO to
27.3% at EGLC), clearly above any single baseline feature at four of five
airports — real signal, not noise. In B+v, `relative_humidity_2m` is the
clear leading raw moisture field at every airport (12.7% at RNO to 23.4%
at EGLC), well ahead of `specific_humidity_2m` (7.3-8.8%) and `dew_point_
2m` (4.3-7.9%) — the raw fields' own signal is carried mostly by relative
humidity, not the other two. Full per-fold breakdown in the real output.
**One inaccuracy in the session-52 prompt's own citation, noted for the
record, not a SPEC/DECISIONS conflict:** the prompt describes this
importance diagnostic as "the same diagnostic F99 reported" — F99's own
script and output (session 50) contain no feature-importance section at
all. The instruction to report importances was followed regardless, since
it is unambiguous on its own terms independent of that citation.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — session51's own output files already exclude it, and this
session's own defensive per-row scan found 0 reserved-year rows, on top of
the guard check on all three folds before any data was loaded. Did not
compute any pass/fail verdict anywhere — the four-variant grid is
reported; the family call is left to review, per the session prompt. Did
not do any per-airport feature selection — identical features at every
airport, in every variant. Did not add `lapse_rate_t2_t850` (E1's own
adopted feature, D52) to B — B stays the frozen 5-feature set only,
per D52's "measurement baseline is unchanged" rule. Did not touch any
E3+ family (pressure, radiation, precipitation). Did not pull any new
data — reused session 51's own output files unchanged. Did not modify
`SPEC.md` or `RESULTS.md`. Nothing was committed. Script: `scripts/
session52_e2_experiment.py` (new). Full real output: `notes/
session-52-e2-experiment-output.txt`.

---

## 2026-09-20 — Session 53 decision: the E2 (moisture) family verdict, from
the owner's review of F100

**D53. Verdict: E2's adopted contribution to the eventual combine-phase
sweep baseline is the single derived feature `dewpoint_depression_t2m_
floored` (the `B+D` variant). The three raw moisture fields —
`relative_humidity_2m`, `specific_humidity_2m`, `dew_point_2m` — are NOT
adopted into the sweep baseline.**

**The raw moisture fields are parked, not dropped, with `relative_
humidity_2m` singled out as the strongest candidate.** In the F100 grid,
`B+v` (raw fields alone, no derived feature) trails `B+D` by only 0.2
points grand-overall (+3.8% vs +4.0%) and ties or beats it outright at two
airports (LFPG, DSM) — closer to the derived form than E1's own raw
pressure levels ever got to `B+L` (D52). F100's own importance breakdown
shows `relative_humidity_2m` carries almost all of the raw fields' signal
(12.7-23.4% of B+v's gain, well ahead of specific humidity and dew point).
This is recorded as an explicit candidate for the combine phase, most
plausibly led by relative humidity alone rather than the full three-field
set — not carried into the E-sweep now.

**Rationale, kept plain.**
(a) `B+D` captures +4.0% of the +4.1% maximum grand-overall skill (F100)
on one added feature instead of three — parsimony with near-equal skill,
the same shape as D52's E1 call.
(b) The closeness of `B+v` to `B+D` is read as the raw fields mostly
re-expressing the same signal the derived feature already captures
directly, not as separate additional information: `B+Dv` (both together)
barely improves on `B+D` alone (+4.1% vs +4.0%, a 0.1-point gain) — if the
raw fields carried real information beyond the derived feature, combining
them should have added more than that.
(c) The fold-level caution in F100 (EGLC's benefit reversing in the
2025-26 fold; RNO flat in the thin 2022-23 fold) is not read as evidence
against the family — it matches the same fold-quality pattern F96 and D52
already named, not a new concern specific to moisture.

**This is provisional.** Like every family in the sweep, `dewpoint_
depression_t2m_floored` is confirmed only when the single final feature
set is checked on the reserved year once, at the finish line (D51) — not
now.

**Measurement baseline is unchanged.** E3 and every later family in the
sweep are measured against the frozen 5-feature baseline B, **not**
against `B+D`. `B+D` enters only at the combine phase. Cites F100.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`.
Did not fit any model or compute any new figure. Did not touch the
reserved 2024-08-01..2025-07-31 confirmation year.

---

## 2026-09-20 — Session 54 finding: the staged E3 (pressure/synoptic)
experiment — a reading, not a verdict; reserved year untouched

**F101. Fits four feature variants (B, B+T, B+Tv, B+v) on the three
non-reserved `EXPERIMENT_FOLDS` (D51) to read whether the pressure/synoptic
family (built and validated in session 53, from F97's own availability map)
adds skill on top of the frozen 5-feature GRIB baseline. This is a LEARNING
experiment, not a sealed-bar test — it reports a grid, not a pass/fail
verdict (the family call is made by the owner in review, per the session
prompt, mirroring F99/F100). The reserved 2024-08-01..2025-07-31
confirmation year was never read, at all, this session.** Script:
`scripts/session54_e3_experiment.py` (new). Full real output: `notes/
session-54-e3-experiment-output.txt`. Tables: `data/processed/
session54_e3_experiment_grid.csv` (60 rows: 5 airports x 3 folds x 4
variants) and `data/processed/session54_e3_experiment_summary.csv` (36
rows: fold-averaged-per-airport, airport-averaged-per-fold, and
grand-overall).

**The four variants, all on D21.4/D48.6's unchanged LightGBM settings, no
per-airport feature selection:**
- **B** — the frozen 5-feature set, REFIT on these three folds (not a
  reuse of F94/F96/F99/F100). Not B+L or B+D either — D52/D53's own
  baseline-unchanged rule.
- **B+T** — B plus `pressure_tendency_3h_hpa` (one added feature — the
  derived form, led with, per the programme's derived-first rule).
- **B+Tv** — B+T plus the two raw pressure fields, `pressure_msl_hpa` and
  `pressure_surface_hpa` (three added total).
- **B+v** — B plus the two raw pressure fields only, WITHOUT the derived
  tendency.
`pressure_msl_lead_minus3_hpa` (the tendency's own raw ingredient) was
never used as a model feature in any variant, per the session prompt.

**Sanity check 1 (tendency arithmetic) — PASS, checked on every row, not a
spot check.** `pressure_tendency_3h_hpa == round(pressure_msl_hpa -
pressure_msl_lead_minus3_hpa, 3)` holds exactly (max abs diff 0.0) at all
7,952 rows of both session53 output files, across all five airports —
matching session 53's own already-passed check.

**Sanity check 2 (reserved-year guard) — PASS.** All three
`EXPERIMENT_FOLDS` entries cleared `assert_reserved_year_excluded()` before
any data was loaded; a defensive per-row scan found 0 reserved-year rows in
the loaded data.

**An unplanned but strong internal-consistency signal, the same check
F99/F100 ran.** The `2025-26` fold's `B` variant (refit 5-feature baseline,
trained on one fewer year than F94 because training may not reach the
reserved year) reproduces F94/F96/F99/F100's own raw-GFS and persistence
MAE and row counts almost exactly at every airport: EGLC raw 1.2536 vs
1.254 (n=364 vs 364), LFPG 1.3822 vs 1.382 (n=364 vs 364), DSM 1.7334 vs
1.733 (n=365 vs 365), YSDU 1.3167 vs 1.317 (n=356 vs 356), RNO 1.5116 vs
1.512 (n=365 vs 365) — confirming the pipeline (join, features, model
settings) is a correct reproduction of the frozen recipe.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, n=15
airport-folds per variant):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+T       1.273      -0.011      +0.9%
B+Tv      1.274      -0.009      +0.7%
B+v       1.284      +0.000      -0.0%
```

**Fold-averaged per airport (mean across the three folds), skill vs B:**

```
station   B+T     B+Tv    B+v
EGLC     +0.6%   +0.6%   +1.4%
LFPG     +1.0%   +1.2%   +0.6%
DSM      +0.7%   -0.3%   -1.0%
YSDU     +0.2%   +0.2%   -0.4%
RNO      +1.6%   +2.2%   -0.0%
```

**The staged question, answered plainly.** (a) `pressure_tendency_3h_hpa`
alone (B+T) already captures the bulk of the family's own grand-overall
benefit — and, unusually against the shape both E1 and E2 showed, it is
the family's OWN BEST variant at the grand level: +0.9% vs B+Tv's +0.7%.
(b) Adding the raw fields on top of the tendency (B+Tv) does not add
further skill at the grand level — it costs 0.2 points against B+T alone,
a small but real reversal of the "adding raw fields on top of the derived
form never hurts" pattern both E1 (B+Lv >= B+L, F99) and E2 (B+Dv >= B+D,
F100) showed. (c) The raw fields alone, without the derived tendency
(B+v), are flat at the grand level (-0.0%) — the family's clearly weakest
single addition, and the only one of the three E1/E2/E3 families where
"raw fields alone" shows essentially no skill at all. **This is by far the
smallest maximum grand-overall skill of the three families explored so
far** (E1's B+Lv +2.0%, F99; E2's B+Dv +4.1%, F100; E3's own maximum, B+T,
+0.9%).

**DSM, the diagnostic (F96: most headroom) — the one airport where adding
the raw fields on top of the derived feature makes things worse, not
better.** DSM's fold-averaged skill: B+T +0.7% (positive, the same modest
shape as elsewhere), but B+Tv -0.3% and B+v -1.0% — DSM is the only
airport in this family where both raw-field variants underperform the
frozen baseline B outright. This is a reversal of the pattern both E1
(B+Lv +2.7% beat B+L +2.2% at DSM, F99) and E2 (B+Dv +6.4% beat B+D +6.2%
at DSM, F100) showed for the same airport — pressure behaves differently
from upper-air and moisture at DSM specifically.

**RNO, pre-registered to possibly NOT show an anomaly (PRMSL is
sea-level-normalised, unlike the below-ground upper-air extrapolation,
F98/F99) — the prediction held, cleanly.** RNO shows the STRONGEST
fold-averaged result of any airport in this family: B+T +1.6%, B+Tv +2.2%
(RNO's own best variant, and the single best airport-variant combination
anywhere in the fold-averaged grid). RNO ran with the identical feature
set as every other airport throughout — no exclusion, no RNO-specific
feature. Unlike F98/F99's upper-air anomaly (t925 below-ground, lapse rate
partly degenerate) and unlike any anomaly flagged for moisture (F100),
pressure/synoptic shows no RNO-specific degradation at all — exactly the
"clean" outcome the session prompt named as the plausible alternative to
an anomaly, and it is what happened.

**A real per-fold reversal, project-wide, in the most recent (2025-26)
fold — flagged as fold-quality, not family weakness, per F96/D52/D53's own
established pattern.** At the airport-averaged-per-fold level, the whole
family is positive in 2022-23 (B+T +1.8%, B+Tv +2.3%, B+v +0.8%) and
mildly positive in 2023-24 (B+T +1.1%, B+Tv +0.4%, B+v -0.2%), but turns
negative across all three variants in 2025-26 (B+T -0.3%, B+Tv -0.6%, B+v
-0.7%) — the only one of the three E-families (E1, E2, E3) whose
airport-averaged fold reading is negative for every added-feature variant
simultaneously in the most recent fold. Per-airport, this reversal is
driven mainly by EGLC (2025-26: B+T +0.0%, B+Tv -5.2%, B+v -2.5% — the
family's single worst fold-airport reading) and RNO (2025-26: B+T -3.1%,
the family's second-worst), while DSM (+0.6%/+1.6%/+0.1%) and LFPG
(+1.4%/+1.4%/-0.2%) stay positive or flat in the same fold. Consistent
with F96/D52/D53's own reading of the thin/edge folds generally, this is
reported as a fold-level pattern, not evidence against the family.

**Feature importances (gain-based, percent of the variant's own total
gain, averaged across the three folds) — B+T and B+v, per airport, per the
session prompt's own instruction.** `pressure_tendency_3h_hpa` sits in the
14.7%-18.1% range at every airport in B+T (RNO 17.9%, LFPG 18.1%, EGLC
17.4%, DSM 14.8%, YSDU 14.7%) — a real, non-trivial share of gain, though
it never dominates the way `dewpoint_depression_t2m_floored` did for
moisture (17.8-27.3%, F100). In B+v, `pressure_msl_hpa` outweighs
`pressure_surface_hpa` at four of five airports (e.g. EGLC 12.8% vs 7.0%,
LFPG 11.7% vs 5.6%, YSDU 10.0% vs 7.1%) but the two are nearly equal at
RNO specifically (11.8% vs 11.7%) — `pressure_surface_hpa`'s importance is
markedly higher at RNO (11.7%) than at any other airport (5.6-8.1%
elsewhere), consistent with RNO's own much lower absolute surface pressure
(D48.3/F90's own elevation story) making surface pressure a genuinely more
separable signal there than at the other four, lower-elevation airports.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — session53's own output files already exclude it, and this
session's own defensive per-row scan found 0 reserved-year rows, on top of
the guard check on all three folds before any data was loaded. Did not
compute any pass/fail verdict anywhere — the four-variant grid is
reported; the family call is left to review, per the session prompt. Did
not do any per-airport feature selection — identical features at every
airport, in every variant, RNO included. Did not add `lapse_rate_t2_t850`
(D52) or `dewpoint_depression_t2m_floored` (D53) to B — B stays the frozen
5-feature set only. Did not touch any E4/E5 family (radiation,
precipitation). Did not re-pull or re-derive any pressure field — reused
session 53's own output files unchanged. Did not modify `SPEC.md` or
`RESULTS.md`. Nothing was committed. Script:
`scripts/session54_e3_experiment.py` (new). Full real output: `notes/
session-54-e3-experiment-output.txt`.

---

## 2026-09-20 — Session 55 decision: the E3 (pressure/synoptic) family
verdict, from the owner's review of F101

**D54. Verdict: E3's adopted contribution to the eventual combine-phase
sweep baseline is the single derived feature `pressure_tendency_3h_hpa`
(the `B+T` variant). The two raw pressure fields — `pressure_msl_hpa` and
`pressure_surface_hpa` — are NOT adopted into the sweep, and — unlike E1
and E2 — nothing from this family is parked as a combine-phase candidate
either.**

**Why nothing is parked (the point that distinguishes E3 from E1/E2).**
E1 parked RNO's raw pressure LEVELS and E2 parked relative humidity
because each showed a real, fold-ROBUST standalone signal at some airport,
just not one general enough to adopt. E3's raw fields do not clear that
bar: `B+v` (raw fields alone) is flat-to-negative grand-overall (-0.0%)
and negative at three of five airports (F101), and `B+Tv` does not beat
`B+T` grand-overall (+0.7% vs +0.9%) — the first family in the programme
where adding the raw fields on top of the derived feature does not help at
all. The one bright spot — RNO's `B+Tv` at +2.2% fold-averaged — rests
mainly on the 2025-26 fold, which F101 reports went negative for the WHOLE
pressure family across every airport and variant, and which F96/D52/D53
already flag as the least representative of the three folds. A signal
whose only support sits inside the least-trusted fold is read as
fold-noise, not a durable Reno effect worth carrying forward — the
opposite of E1's RNO raw-levels signal, which was positive in all three
folds. So the raw pressure fields are dropped, not parked.

**Rationale for the adoption itself, kept plain.** `pressure_tendency_3h_
hpa` is the family's own best variant grand-overall (+0.9%, F101), and it
is a single derived feature — consistent with the programme's "lead with
the derived form" principle (the same shape as D52's lapse rate and D53's
dew-point depression). E3 is the weakest family so far (+0.9% max, vs E1
+2.0%, E2 +4.1%), so this is a small adopted contribution — recorded
honestly as such, not inflated.

**This is provisional.** Like every family in the sweep, `pressure_
tendency_3h_hpa` is confirmed only when the single final feature set is
checked on the reserved year once, at the finish line (D51) — not now.

**Measurement baseline is unchanged.** E4 and every later family in the
sweep are measured against the frozen 5-feature baseline B, **not** against
`B+T` or any other adopted feature. Adopted features enter only at the
combine phase. Cites F101.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`.
Did not fit any model or compute any new figure. Did not touch the
reserved 2024-08-01..2025-07-31 confirmation year.

---

## 2026-09-20 — Session 55 finding: E4 (radiation) feature set built and
validated — a data build, no model fit, reserved year untouched

**F102. Pulls, decodes, joins, and RESOLVES the E4 radiation feature
(`DSWRF:surface`, downward shortwave at the surface) onto the existing
5-feature GRIB dataset, at every date that dataset already carries OUTSIDE
the reserved 2024-25 confirmation year (D51). Data-build-only, per the
session prompt: no model was fit, no MAE or CV was computed, and
2024-08-01..2025-07-31 was never loaded, pulled, or joined. DSWRF:surface
only — not the full eight-field radiation set F97 catalogued.** Script:
`scripts/session55_radiation_pull.py` (new). Full real output: `notes/
session-55-radiation-output.txt`. Outputs: `data/processed/
session55_v16_window_with_radiation.csv` (6,128 rows), `data/processed/
session55_sealed_window_with_radiation.csv` (1,826 rows), `data/processed/
session55_radiation_join_drops.csv` (0 rows), `data/raw/diagnostics/
session55/session55_pull_manifest.csv` (9,542 rows), `data/raw/diagnostics/
session55/session55_window_resolution.csv` (12 rows).

**Step 0 — the window-resolution problem, unique to this family, resolved
before any bulk pull.** F97 found DSWRF:surface carries only a
time-AVERAGED "ave fcst" GRIB field, whose window LENGTH is a byproduct of
each airport's own forecast lead (6h at the lead-24 airports EGLC/LFPG/DSM,
2h at the lead-26 airports YSDU/RNO) — a raw feature built from it would
mean a different physical thing at different airports. This session
checked, directly and freshly (not reusing F97's own idx files, since one
of F97's two sample dates, 2025-06-15, now falls inside the reserved year
established by D51 one session after F97 ran — the same wrinkle session
49 already noted for its own spot-check): does an INSTANTANEOUS
`DSWRF:surface` variant exist alongside the averaged one, the way F97
found for the cloud-layer fields (LCDC/MCDC/HCDC)? Checked by enumerating
EVERY idx line matching `DSWRF:surface` (not just the first) at every
distinct forecast-hour file this session needs — f024, f026 (each
combo's own standard lead) and f022 (the candidate de-accumulation
endpoint for the lead-24 airports) — at two sample dates, the v16 floor
(2021-03-24) and a recent date outside both the sealed year and the
reserved year (2024-06-15, since F97's own 2025-06-15 sample is now
reserved). **Result: NO instantaneous variant exists anywhere checked —
exactly one `DSWRF:surface` line per idx file, always an "ave fcst" step,
at all 6 files, both dates.** Real decoded values (`eccodes` `startStep`/
`endStep`, not just the idx label text) confirmed the exact window bounds
at every file: f024 = 18-24h (6h), f022 = 18-22h (4h), f026 = 24-26h (2h) —
all sharing the same 18h/24h reset marks, at both dates.

**Decision: de-accumulate to a common 2-hour window ending at each
airport's own target hour (session prompt Step 0, item 2).**
- **YSDU, RNO (lead 26):** the native "24-26 hour ave fcst" message IS
  ALREADY the 2-hour window ending at the target hour — used directly, no
  de-accumulation, no second message fetched.
- **EGLC, LFPG, DSM (lead 24):** the native message is a 6-hour average
  ("18-24 hour ave fcst"). A second message at forecast hour 22 carries
  "18-22 hour ave fcst" (4h), the same 18h reset window one GFS
  output-hour earlier, confirmed present and correctly timed by direct
  byte-range fetch and decode (Step 0) before the bulk pull. The trailing
  2-hour average is recovered by energy subtraction: `energy(22h..24h) =
  ave(18h..24h)*6 - ave(18h..22h)*4`, `dswrf_2h_wm2 = energy(22h..24h)/2`.
  Both raw endpoints are kept as their own columns
  (`dswrf_ave_to_lead_wm2`, `dswrf_ave_to_lead_minus2_wm2`) for
  transparency, mirroring E3's own `pressure_msl_lead_minus3_hpa`
  convention. No per-airport statistical standardisation was used
  anywhere — the consistency achieved is physical (an identical, real
  2-hour window, ending at the target hour, at every airport), not
  cosmetic (session prompt Step 0, item 3).

Units: GRIB decodes DSWRF directly in W m**-2 (confirmed by direct
decode) — no unit conversion needed, unlike pressure's Pa->hPa (E3).

**One minor, verdict-irrelevant reporting artifact, noted plainly.** Step
0's own printed decision summary (a console-narration loop over every
forecast-hour file it happened to check, including the intermediate f022
file) mis-describes f022 itself as needing a further de-accumulation
against a nonexistent "f020" file. This is a cosmetic bug in the summary
text only — the actual pull/join code (`build_combos`, `process_combo`,
`build_joined`) computes whether an airport needs de-accumulation solely
from that airport's OWN final standard lead (24 or 26), never treats f022
as a top-level combo of its own, and correctly fetched exactly 1 or 2
messages per airport-date throughout (confirmed exactly by the message
counts below). No computed value is affected; reported for the record
rather than silently left unremarked, the same discipline earlier
sessions applied to their own minor found issues (e.g. F92/F93).

**Guard check (Step 1) — PASS.** The date list was built from the
existing 5-feature dataset's own real rows: train span
2021-03-24..2024-07-31 (1,226 dates), sealed span 2025-08-01..2026-07-31
(365 dates) — identical to E1/E2/E3's own spans. `assert_reserved_year_
excluded()` passed on both spans; a defensive per-date scan of all 1,591
dates found 0 reserved-year dates before any pull request was made.

**Pull (Step 2) — complete, zero failures.** 6,361 distinct (run_date,
cycle, lead) combos (3,181 needing de-accumulation, 2 messages each;
3,180 already-native-2h, 1 message each) -> 9,542 total message fetches
(+9,542 idx fetches, one per message) — **0 FAIL rows** in the manifest,
40.7 minutes at 48-way concurrency. Per-field: `dswrf_to_lead`
requested=7,952 decoded_ok=7,952 failed=0; `dswrf_to_lead_minus2`
requested=4,772 decoded_ok=4,772 failed=0 (4,772 = the exact row count of
the three de-accumulating airports, EGLC+LFPG+DSM, both spans combined).
No raw GRIB2 bytes were kept on disk — fetch-decode-discard, the same
pattern E1/E2/E3 used. Free disk space: 10.65 GiB before, 10.39 GiB after
— the modest drop is scratch-file churn during the pull (E3's own pull,
needing two idx fetches per combo, showed a similar-sized drop), not a
retained cache.

**Join + derive (Step 3) — exact, zero drops, at every airport.** Row
counts before and after the join match exactly at all five airports, both
spans (v16_window: EGLC/LFPG 1,226, DSM/YSDU/RNO 1,225; sealed_window: all
five 365) — `session55_radiation_join_drops.csv` is empty.

**Validate (Step 4) — 0 nulls; all values non-negative; one real, plainly
reportable premise error in the session prompt itself, not a data
defect.** `dswrf_2h_wm2` is null-free at every airport, both spans
(n=1,591 EGLC/LFPG, n=1,590 DSM/YSDU/RNO). Min/mean/max, all W m**-2, no
negative values anywhere:

```
station  min     mean     max
EGLC      4.10   427.36   888.47
LFPG      3.53   464.67   910.32
DSM       8.34   567.08   964.46
YSDU     11.94   683.62  1106.46
RNO      40.73   719.36  1031.10
```

**The session prompt asked this step to check whether YSDU and RNO "read
appropriately low" as low-sun airports — they do not, and the reason is
that the premise itself is wrong, flagged here rather than silently
resolved (CLAUDE.md: stop and flag a session-prompt/SPEC disagreement).**
The session prompt states YSDU's 02:00 UTC target hour is NIGHT and RNO's
20:00 UTC is "near/after sunset for much of the year," expecting
near-zero shortwave there as a correctness check. The measured means
directly contradict this: YSDU (683.62 W/m2) and RNO (719.36 W/m2) are the
HIGHEST of all five airports, not the lowest — broad daylight, not night
or dusk. This is not a pipeline defect: SPEC 4.1's own foundational design
principle is that EVERY airport's target hour is deliberately chosen to
fall at that airport's own local STANDARD NOON, specifically so it sits in
daylight and avoids the dawn/dusk swings a lower-sun hour would bring.
Dubbo's 02:00 UTC target hour was established as local standard noon
(UTC+10 standard time) in DECISIONS D37; Reno's 20:00 UTC was established
as local standard noon (UTC-8 standard time) in DECISIONS D42 — both
checked against the timezone database at the time, not assumed. So the
session prompt's own "night"/"near-sunset" framing for these two airports
contradicts SPEC 4.1 and D37/D42 directly, and the real, measured data
sides with SPEC and DECISIONS, not with the session prompt's premise. No
airport in this project is a low-sun airport by design — that is
precisely SPEC 4.1's point. The pull, the join, and `dswrf_2h_wm2` itself
are unaffected and correct; only the session prompt's own expectation
about which airports should read low was mistaken.

**Open-Meteo cross-check on `shortwave_radiation`, non-reserved overlap
only: a real, larger gap than the temperature/pressure cross-checks
showed, at every airport, exactly as anticipated — reported, not
chased.** Compared over 2024-01-19..2024-07-31 (pre-reservation) and
2025-08-01..2026-07-31 (the sealed span), the same two non-reserved
windows E2/E3's own cross-checks used. Mean|diff| ranges 39.44-50.16 W/m2
across all five airports (EGLC 39.72, LFPG 41.09, DSM 50.16, YSDU 50.15,
RNO 39.44), with a consistently NEGATIVE mean signed difference at every
airport (-13.50 to -31.82 W/m2 — this session's own resolved 2h-window
value runs below Open-Meteo's own `shortwave_radiation` throughout). This
is a materially larger gap than the temperature (<=0.062 degC, F89/F90),
pressure (0.044-0.421 hPa at four airports, session 53's own build — not
separately given its own DECISIONS finding number) or moisture
cross-checks showed, consistent with the session prompt's own expectation
that Open-Meteo's own shortwave averaging convention likely differs from
this session's own resolved 2-hour window — a real, expected reason for a
larger gap, reported here rather than investigated further this session.

**What this session did not do, on purpose.** Did not fit any model,
compute any MAE, skill, or CV. Did not read, load, join, or score a
single row of the reserved 2024-08-01..2025-07-31 confirmation year (D51)
— enforced by the shared guard function plus a defensive per-date scan
(0 hits) before any pull request was made. Did not pull any radiation
field beyond `DSWRF:surface`, or any E5/precipitation field. Did not use
per-airport statistical standardisation to paper over the window
mismatch — the resolved feature is a physically identical 2-hour window
at every airport. Did not do any per-airport feature selection —
identical handling at all five airports throughout. Did not modify
`SPEC.md` or `RESULTS.md`. Nothing was committed. Script:
`scripts/session55_radiation_pull.py` (new). Full real output: `notes/
session-55-radiation-output.txt`.

---

## 2026-09-20 — Session 56 finding: the staged E4 (radiation) experiment — a
reading, not a verdict; reserved year untouched

**F103. Fits four feature variants (B, B+R, B+Rv, B+v) on the three
non-reserved `EXPERIMENT_FOLDS` (D51) to read whether the radiation family
(built and validated in session 55, F102) adds skill on top of the frozen
5-feature GRIB baseline, and specifically whether it adds anything BEYOND
`cloud_cover`, which is already in the baseline and is the dominant control
on how much shortwave reaches the ground (F97). This is a LEARNING
experiment, not a sealed-bar test — it reports a grid, not a pass/fail
verdict (the family call is the owner's review decision in session 57, per
the session prompt). The reserved 2024-08-01..2025-07-31 confirmation year
was never read, at all, this session.** Script:
`scripts/session56_e4_experiment.py` (new). Full real output: `notes/
session-56-e4-experiment-output.txt`. Tables: `data/processed/
session56_e4_experiment_grid.csv` (60 rows: 5 airports x 3 folds x 4
variants) and `data/processed/session56_e4_experiment_summary.csv` (36
rows: fold-averaged-per-airport, airport-averaged-per-fold, and
grand-overall).

**Preamble — a print-text-only cleanup, done first.** F102 flagged a
cosmetic bug in `scripts/session55_radiation_pull.py`'s Step-0 printed
DECISION summary: its final per-combo loop iterated over `windows_seen`,
which also held the lead-2 helper file (e.g. f022, fetched only to
de-accumulate the lead-24 airports' own standard-lead message), so it
wrongly described f022 itself as needing further de-accumulation against a
nonexistent "f020" file. Fixed by changing the loop's iteration source from
`windows_seen.items()` to the real top-level `combos.items()` (the four
actual (cycle, lead) airport combos), reading `windows_seen.get((cycle,
lead), set())` for the printed window. Confirmed by re-reading the changed
lines: only the summary loop's iteration source changed — `build_combos`,
`process_combo`, `build_joined`, the lead/window arithmetic functions, and
every fetch count are byte-for-byte unchanged. The session-55 pull was not
re-run; this session reads session 55's already-committed output files
unchanged, and F102's own numbers stand exactly as reported.

**The four variants, all on D21.4/D48.6's unchanged LightGBM settings, no
per-airport feature selection:**
- **B** — the frozen 5-feature set, REFIT on these three folds (not a
  reuse of F94/F96/F99/F100/F101). Not B+L, B+D, or B+T either — D52/D53/
  D54's own "measurement baseline is unchanged" rule.
- **B+R** — B plus the resolved `dswrf_2h_wm2` feature (F102's own single
  physically-consistent 2-hour-window shortwave feature).
- **B+Rv** — B+R plus the two raw de-accumulation-endpoint columns,
  `dswrf_ave_to_lead_wm2` and `dswrf_ave_to_lead_minus2_wm2`.
- **B+v** — B plus those two raw endpoint columns, WITHOUT the resolved
  `dswrf_2h_wm2`.

**E4's raw set differs in KIND from E1-E3's (session prompt's own framing,
confirmed in the output).** E1-E3's raw fields were independent physical
variables; E4's two raw endpoints are instead the two accumulation-window
averages the resolved `dswrf_2h_wm2` is itself DERIVED FROM. So B+Rv/B+v
test whether the model does better with the raw energy endpoints than with
the clean, physically-resolved 2-hour rate — not whether an independent
variable adds anything.

**A design decision this session had to make, not specified by the session
prompt, reported plainly.** `dswrf_ave_to_lead_minus2_wm2` is blank in the
session-55 output files at YSDU and RNO (the lead-26 airports) — F102's own
build never fetched a second message there, because the native window is
already the target 2-hour window, so no de-accumulation and no second
endpoint exist. To give B+Rv/B+v a well-defined, identically-shaped feature
vector at all five airports without inventing a number (SPEC 2.2),
`dswrf_ave_to_lead_minus2_wm2` was set equal to `dswrf_ave_to_lead_wm2` at
those two airports — the honest statement that no distinct earlier endpoint
exists there, not a filled gap (0 substitutions at EGLC/LFPG/DSM; every row
substituted at YSDU/RNO, 1,590 each). **The direct consequence, confirmed in
the grid: B+R, B+Rv and B+v are mathematically IDENTICAL models at YSDU and
RNO** (byte-identical MAE at every fold) — so the "does the model do better
with raw endpoints than the resolved rate" question is only meaningfully
answerable at the three lead-24 airports (EGLC, LFPG, DSM); at YSDU/RNO all
three radiation variants collapse to the same single feature value.

**Sanity check 1 (reserved-year guard) — PASS.** All three
`EXPERIMENT_FOLDS` entries cleared `assert_reserved_year_excluded()` before
any data was loaded; a defensive per-row scan found 0 reserved-year rows in
the loaded data.

**Sanity check 2 (feature-resolution check) — PASS, checked on every row,
not a spot check.** At the three lead-24 airports (EGLC, LFPG, DSM),
`dswrf_2h_wm2 == (dswrf_ave_to_lead_wm2*6 - dswrf_ave_to_lead_minus2_wm2*4)
/ 2` within a 0.01 W/m2 tolerance (comfortably above the ~0.0025 W/m2
rounding error the stored 3-decimal values can introduce); at the two
lead-26 airports (YSDU, RNO), `dswrf_2h_wm2 == dswrf_ave_to_lead_wm2`
directly. Max abs diff: EGLC 0.002000, LFPG 0.002000, DSM 0.002000 (all
pure rounding noise, well inside tolerance), YSDU 0.000000, RNO 0.000000
(exact). Checked across all 7,952 rows of both session55 output files.

**An unplanned but strong internal-consistency signal, the same check
F99/F100/F101 ran.** The `2025-26` fold's `B` variant (refit 5-feature
baseline, trained on one fewer year than F94 because training may not
reach the reserved year) reproduces F94/F96/F99/F100/F101's own raw-GFS and
persistence MAE and row counts almost exactly at every airport: EGLC raw
1.2536 vs 1.254 (n=364 vs 364), LFPG 1.3822 vs 1.382 (n=364 vs 364), DSM
1.7334 vs 1.733 (n=365 vs 365), YSDU 1.3167 vs 1.317 (n=356 vs 356), RNO
1.5116 vs 1.512 (n=365 vs 365) — confirming the pipeline (join, features,
model settings) is a correct reproduction of the frozen recipe.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, n=15
airport-folds per variant):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+R       1.266      -0.018      +1.4%
B+Rv      1.260      -0.024      +1.9%
B+v       1.263      -0.020      +1.6%
```

**Fold-averaged per airport (mean across the three folds), skill vs B:**

```
station   B+R     B+Rv    B+v
EGLC     +3.8%   +5.4%   +4.7%
LFPG     +2.4%   +3.2%   +2.3%
DSM      -0.2%   +0.1%   +0.0%
YSDU     +1.2%   +1.2%   +1.2%
RNO      +0.8%   +0.8%   +0.8%
```

(YSDU/RNO's three columns are identical by construction — see the design
decision above.)

**E4's own max grand-overall skill against E1/E2/E3, stated plainly, per
the session prompt's own instruction.** E1's max (B+Lv, F99): +2.0%. E2's
max (B+Dv, F100): +4.1%. E3's max (B+T, F101): +0.9%. **E4's max (B+Rv,
this session): +1.9%** — E4 sits just below E1, comfortably above E3, and
well below E2.

**The specific question this experiment answers, read with the real
numbers.** `cloud_cover` is already in the frozen baseline B, and cloud is
the dominant control on shortwave reaching the ground (F97). This is a
marginal-over-cloud test, not a from-scratch test — and the answer is a
real, non-trivial positive one at most airports, not the null result a
"radiation is redundant with cloud" prior might have predicted: radiation
adds skill beyond cloud at four of five airports, clearly at EGLC and LFPG,
modestly at YSDU and RNO (see the design-decision caveat above), and not at
all at DSM.

**EGLC and LFPG — the family's two strongest results, and the only two
airports where the raw-vs-resolved contrast is genuinely tested (both are
lead-24 airports with a real second endpoint).** EGLC's B+Rv (+5.4%) is the
single best airport-variant reading in this family — and at both airports
adding the raw endpoints on top of the resolved rate helps further (EGLC:
Rv +5.4% > v +4.7% > R +3.8%; LFPG: Rv +3.2% > R +2.4% > v +2.3%) — the same
"raw-plus-derived never hurts" shape E1 (F99) and E2 (F100) showed, and
E3 (F101) was the one family that broke.

**DSM, the diagnostic (F96: most headroom, cloud/wind already marginal
there) — the one airport where radiation adds nothing, consistent with the
marginal-over-cloud framing.** B+R is actually slightly negative (-0.2%),
B+Rv and B+v are both essentially flat (+0.1%, +0.0%). Unlike E1 (F99,
+2.7%) and E2 (F100, +6.2%), where DSM showed a clear positive signal,
radiation joins E3 (F101, -0.3%/-1.0% for B+Tv/B+v) as a family that does
not rescue DSM — the honest reading, per the session prompt's own framing,
is that DSM's already-marginal cloud/wind signal leaves shortwave with
nothing further to add once cloud is already in the model.

**YSDU and RNO — a real, modest, single-valued result, not a genuine
raw-vs-resolved reading.** Both post a real positive skill (+1.2%, +0.8%)
that holds identically across B+R/B+Rv/B+v, by construction (see the design
decision above) — the resolved feature itself carries real signal there,
but this family's own "does raw help over resolved" question is silent at
these two airports specifically, a genuine limitation of this experiment at
the lead-26 airports.

**Per-fold spread — this family does NOT reverse in the most recent
fold, unlike E3.** Airport-averaged per fold: 2022-23 (thinnest, per
F96/D52/D53/D54's own established caution) shows the family's smallest
benefit (B+R +0.6%, B+Rv +1.0%, B+v +0.4%); 2023-24 shows its largest
(B+R +2.5%, B+Rv +3.4%, B+v +2.9%); 2025-26 (the most recent, least-trusted
fold per prior sessions) stays POSITIVE across all three variants (B+R
+1.0%, B+Rv +1.3%, B+v +1.6%) — unlike E3 (F101), which reversed to
negative across every variant in this same fold. Full fold-by-fold detail:
`data/processed/session56_e4_experiment_grid.csv`.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — session55's own output files already exclude it, and this
session's own defensive per-row scan found 0 reserved-year rows, on top of
the guard check on all three folds before any data was loaded. Did not
compute any pass/fail verdict anywhere — the four-variant grid is
reported; the family call is left to the owner's review in session 57, per
the session prompt. Did not do any per-airport feature selection —
identical features at every airport, in every variant, RNO included. Did
not add `lapse_rate_t2_t850` (D52), `dewpoint_depression_t2m_floored`
(D53), or `pressure_tendency_3h_hpa` (D54) to B — B stays the frozen
5-feature set only. Did not touch the E5 (precipitation) family. Did not
re-pull or re-derive any radiation field, or re-run session 55's own pull —
reused session 55's own committed output files unchanged. Did not change
any data-path logic in `scripts/session55_radiation_pull.py` — the preamble
fix was print-text only, confirmed by re-reading the changed lines. Did not
modify `SPEC.md` or `RESULTS.md`. Nothing was committed.

---

## 2026-09-20 — Session 57 decision: the E4 (radiation) family verdict, from the owner's review of F103

**D55. Verdict: E4's adopted contribution to the eventual combine-phase sweep
baseline is the single resolved feature `dswrf_2h_wm2` (the `B+R` variant) — the
physically-consistent 2-hour-average downward-shortwave rate F102 built. The two raw
de-accumulation-endpoint columns — `dswrf_ave_to_lead_wm2` and
`dswrf_ave_to_lead_minus2_wm2` — are NOT adopted into the sweep, and — as with E3 —
nothing from this family is parked as a combine-phase candidate either.**

**Why nothing is parked (the point that separates E4 from E1/E2).** E1 parked RNO's
raw pressure LEVELS (D52) and E2 parked relative humidity (D53) because each was a
genuinely SEPARATE physical variable carrying a real, fold-robust standalone signal at
some airport. E4's two raw columns are not a separate variable at all: they are the two
accumulation-window averages that `dswrf_2h_wm2` is itself DERIVED FROM (F103). Adopting
them would add no new physical information — it would only let the model re-do the
de-accumulation the resolved feature already performs, maximally redundant with `R` by
construction. They are also unevenly defined: identical to `dswrf_2h_wm2` at the two
lead-26 airports (YSDU, RNO) by construction, so `B+R`, `B+Rv` and `B+v` are the same
model there (F103). A redundant, unevenly-defined pair is not a portable combine-phase
candidate — so it is dropped, not parked.

**Rationale for the adoption itself, kept plain.** `dswrf_2h_wm2` is a single, clean,
physically-resolved feature — an identical real 2-hour shortwave rate at every airport
(F102) — consistent with the programme's "lead with the resolved form" principle (the
same shape as D52's lapse rate, D53's dew-point depression, D54's pressure tendency). It
carries +1.4% grand-overall skill (F103), of the family's +1.9% maximum (`B+Rv`). The
+0.5pp the raw endpoints add on top rests entirely on the two lead-24 airports EGLC and
LFPG, and — being redundant-by-construction — is read as the model re-deriving the
resolution rather than as new signal. E4 is a mid-strength family (+1.4% adopted, +1.9%
max — above E3's +0.9%, below E1's +2.0% and E2's +4.1%), recorded honestly as such.

**On-record observation for the combine phase (NOT a parked candidate).** At EGLC and
LFPG — the only airports where the raw-vs-resolved contrast is both real and non-flat
(DSM is genuinely tested but reads flat: `B+R` -0.2%, `B+Rv` +0.1%, `B+v` +0.0%;
YSDU/RNO are silent by construction) — the raw endpoints add a little further skill on
top of the resolved rate (EGLC `B+Rv` +5.4% vs `B+R` +3.8%; LFPG `B+Rv` +3.2% vs `B+R`
+2.4%, F103). This is logged as an observation for the combine phase to be aware of, NOT
as a formal parked candidate: it is a fold-AVERAGED read only (no per-fold-per-airport
robustness certification, unlike E1's parked RNO signal), and it is
redundant-by-construction with the adopted feature rather than a separate variable.
Grid: `data/processed/session56_e4_experiment_grid.csv`.

**This is provisional.** Like every family in the sweep, `dswrf_2h_wm2` is confirmed
only when the single final feature set is checked on the reserved year once, at the
finish line (D51) — not now.

**Measurement baseline is unchanged.** E5 and any later work in the sweep are measured
against the frozen 5-feature baseline B, NOT against `B+R` or any other adopted feature.
Adopted features enter only at the combine phase. Cites F103.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`. Did not fit
any model or compute any new figure — every number above is copied from and cited to
F103. Did not touch the reserved 2024-08-01..2025-07-31 confirmation year.

---

## 2026-09-20 — Session 57 finding: E5 (precipitation) feature set built and
validated — a data build, no model fit, reserved year untouched

**F104. Pulls, decodes, and joins the E5 precipitation feature
(`APCP:surface`'s own since-forecast-start cumulative accumulation, turned
into one mean precipitation rate, `precip_rate_mmh`) onto the existing
5-feature GRIB dataset, at every date that dataset already carries OUTSIDE
the reserved 2024-25 confirmation year (D51). Data-build-only, per the
session prompt: no model was fit, no MAE/skill/CV was computed, and
2024-08-01..2025-07-31 was never loaded, pulled, or joined. APCP:surface
only — not PRATE/SNOD/WEASD, and no radiation field.** Script:
`scripts/session57_precip_pull.py` (new). Full real output: `notes/
session-57-precip-output.txt`. Outputs: `data/processed/
session57_v16_window_with_precip.csv` (6,128 rows), `data/processed/
session57_sealed_window_with_precip.csv` (1,826 rows), `data/processed/
session57_precip_join_drops.csv` (0 rows), `data/raw/diagnostics/
session57/session57_pull_manifest.csv` (6,361 rows), `data/raw/diagnostics/
session57/session57_window_resolution.csv` (8 rows).

**Step 0 — window handling, the session prompt's own pre-decided choice
(cumulative-since-start, ONE message, no de-accumulation), confirmed
directly and freshly before any bulk pull, not re-decided.** F97 found
`APCP:surface` exposes TWO accumulation windows at each lead: a short one
matching the ave-field window (the same window `DSWRF:surface`, E4, used)
and a cumulative-since-forecast-start one ("0-1 day acc fcst" at lead 24,
"0-26 hour acc fcst" at lead 26 — a day-vs-hour labelling quirk for the
same "since hour 0" idea). This session checked, directly and freshly (not
reusing F97's own idx files, since one of F97's two sample dates,
2025-06-15, now falls inside the reserved year established by D51 one
session after F97 ran — the same wrinkle sessions 49/55 already noted for
their own spot-checks): every idx line matching `APCP:surface` (not just
the first) at all four distinct real (cycle, lead) combos the five
airports' own target hours select, at two sample dates, the v16 floor
(2021-03-24) and a recent date outside both the sealed year and the
reserved year (2024-06-15). **Result: at every combo/date, exactly one
line parses as the since-start cumulative accumulation** (identified by
its own step text, "0-N hour/day acc fcst", always starting "0-", never
true of the short ave-window-matching line). Real decoded values
(`eccodes` `startStep`/`endStep`, not just the idx label text) confirmed
the exact window bounds at every one of the 8 checks: `startStep=0`,
`endStep=24` at the lead-24 combos (EGLC/LFPG cycle 12z, DSM cycle 18z) and
`endStep=26` at the lead-26 combos (YSDU cycle 00z, RNO cycle 18z), decoded
units `kg m**-2` (== mm, no conversion needed), and valid time exactly
matching the airport's own target hour, at both sample dates. Unlike E4,
this family needs **no second message and no de-accumulation** — the
session prompt's own one-message design is confirmed workable as
specified, not re-decided.

**A structural finding this family's own one-message design forces,
stated plainly per the session prompt's own Step 0 instruction, not a
defect.** `precip_window_hours` is a CONSTANT per airport (24 at
EGLC/LFPG/DSM, 26 at YSDU/RNO), so `apcp_cumulative_mm` and
`precip_rate_mmh` differ only by a fixed per-airport scale — monotone
transforms of each other. LightGBM's tree splits are invariant to a
monotone per-feature transform, so within any single airport's model the
raw total and the mean rate are the SAME feature. **E5 therefore carries
effectively ONE precipitation feature**, not a raw-vs-resolved pair the
way E1–E4 did; `precip_rate_mmh` is kept as the headline form (a common
mm/h scale across airports), `apcp_cumulative_mm` only for transparency.
**Session 58's own E5 experiment should therefore be planned as a clean B
vs B+P, not a four-variant grid.**

**A real cross-airport inconsistency, flagged plainly, not papered over —
explicitly NOT E4-level physical consistency.** Unlike E4's resolved
feature (a physically identical 2-hour window at every airport), this
since-start window is 24h at EGLC/LFPG/DSM but 26h at YSDU/RNO — so
`precip_rate_mmh` is a mean over a 24h span at three airports and a 26h
span at two. Rate-normalisation handles the magnitude/scale, not the span
difference itself — reported honestly as a genuine mild inconsistency, per
the session prompt's own instruction, with no per-airport statistical
standardisation used to hide it.

**Sparsity handling, per the session prompt's own instruction.**
`precip_rate_mmh` is used as one continuous feature, with NO transform (no
log1p, no binary wet/dry flag) — LightGBM handles a zero-inflated
continuous feature natively via its splits. A decoded zero is a REAL, kept
value (a dry forecast), not missing data: SPEC 2.2's drop-and-count applies
only to a genuinely missing message or an unpaired observation row, never
to a legitimate zero. Per-airport zero-fraction, reported descriptively
with no pre-registered expectation of which airport should read driest
(unlike F102's own session prompt, which carried a wrong "which airport
reads low" premise for radiation — not repeated here):

```
station   min      mean     max (mm/h)   zero_fraction
EGLC      0.0000   0.0813   1.8370       0.2866 (456/1591)
LFPG      0.0000   0.0868   2.0028       0.3136 (499/1591)
DSM       0.0000   0.1020   3.0229       0.4642 (738/1590)
YSDU      0.0000   0.0691   2.2790       0.5333 (848/1590)
RNO       0.0000   0.0510   4.4858       0.6195 (985/1590)
```

RNO reads driest by zero-fraction (62.0% of rows dry) and EGLC wettest
(28.7% dry) — measured, not assumed in advance either way.

**Guard check (Step 1) — PASS.** The date list was built from the existing
5-feature dataset's own real rows, exactly as sessions 49/51/53/55 built
theirs: train span 2021-03-24..2024-07-31 (1,226 dates), sealed span
2025-08-01..2026-07-31 (365 dates), 1,591 dates total.
`assert_reserved_year_excluded()` passed on both spans; a defensive
per-date scan of all 1,591 dates found 0 reserved-year dates before any
pull request was made.

**Pull (Step 2) — complete, zero failures.** 6,361 distinct (run_date,
cycle, lead) combos, ONE APCP message each (no de-accumulation, unlike
E4's own up-to-two-message combos) -> 6,361 message fetches (+6,361 idx
fetches, one per message) — **0 FAIL rows**, 12.8 minutes at 48-way
concurrency (~8.27 combos/s). Per-station-instance decode count:
requested=7,952 decoded_ok=7,952 failed=0. No raw GRIB2 bytes kept on disk
(fetch-decode-discard, E1–E4 precedent) — free disk space exactly
unchanged, 10.71 GiB before and after, the cleanest disk-space result of
any family build so far, consistent with the one-message design (contrast
E3's two-idx-fetch-per-combo drop, 11.32 to 9.87 GiB).

**Join + derive (Step 3) — exact, zero drops, at every airport.** Row
counts before and after the join match exactly at all five airports, both
spans (v16_window: EGLC/LFPG 1,226, DSM/YSDU/RNO 1,225; sealed_window: all
five 365) — `session57_precip_join_drops.csv` is empty.

**Validate (Step 4) — 0 nulls; all values non-negative.** `apcp_cumulative_
mm` and `precip_rate_mmh` are null-free at every airport, both spans
combined (n=1,591 EGLC/LFPG, n=1,590 DSM/YSDU/RNO). `min(apcp_cumulative_
mm)=0.000` at every airport — no negative values anywhere. Per-airport
min/mean/max and zero-fraction: see the table above.

**Open-Meteo cross-check on `precipitation`, non-reserved overlap only: a
real gap, exactly as anticipated, not chased.** Compared over
2024-01-19..2024-07-31 (pre-reservation) and 2025-08-01..2026-07-31 (the
sealed span), the same two non-reserved windows E2/E3/E4's own cross-checks
used. mean|diff| ranges 0.0627 mm/h (RNO) to 0.1328 mm/h (DSM) — a large
gap relative to the means above, expected and reported rather than chased,
since this session's `precip_rate_mmh` is a mean over a 24-26h
since-forecast-start window while Open-Meteo's own
`precipitation_previous_day1` is a single hour's own accumulation, a
different convention entirely. Wet/dry co-occurrence (both > 0 vs both ==
0) agrees on 47.9% (EGLC) to 68.6% (RNO) of compared rows:

```
station   n_compared   mean|diff| (mm/h)   mean_diff (mm/h)   agree_fraction
EGLC      560          0.1238               -0.0241             0.4786
LFPG      560          0.1149               -0.0042             0.5089
DSM       560          0.1328               +0.0462             0.5429
YSDU      559          0.0652               +0.0020             0.6726
RNO       560          0.0627               +0.0103             0.6857
```

**What this session did not do, on purpose.** Did not fit any model,
compute any MAE, skill, or CV. Did not read, load, or join a single row of
the reserved 2024-08-01..2025-07-31 confirmation year (D51) — enforced by
the shared guard function plus a defensive per-date scan (0 hits) before
any pull request was made. Did not pull any precipitation field beyond
`APCP:surface` (no PRATE/SNOD/WEASD), or any radiation field. Did not use
any transform on `precip_rate_mmh` (no log1p, no binary wet/dry flag) —
kept as one continuous feature, per the session prompt. Did not do any
per-airport feature selection — identical handling at all five airports
throughout. Did not modify `SPEC.md` or `RESULTS.md`. Nothing was
committed.

---

## 2026-09-21 — Session 58 finding: the staged E5 (precipitation) experiment
— a reading, not a verdict; reserved year untouched. E5 is the LAST family
in the feature-selection programme.

**F105. Fits TWO feature variants (B, B+P — not a four-variant grid, see
below) on the three non-reserved `EXPERIMENT_FOLDS` (D51) to read whether
the precipitation family (built and validated in session 57, F104) adds
skill on top of the frozen 5-feature GRIB baseline. This is a LEARNING
experiment, not a sealed-bar test — it reports a grid, not a pass/fail
verdict (the family call is the owner's review decision in session 59,
D56). The reserved 2024-08-01..2025-07-31 confirmation year was never read,
at all, this session.** Script: `scripts/session58_e5_experiment.py` (new).
Full real output: `notes/session-58-e5-experiment-output.txt`. Tables:
`data/processed/session58_e5_experiment_grid.csv` (30 rows: 5 airports x 3
folds x 2 variants) and `data/processed/session58_e5_experiment_summary.csv`
(18 rows: 10 fold-averaged-per-airport, 6 airport-averaged-per-fold, 2
grand-overall).

**The two variants, both on D21.4/D48.6's unchanged LightGBM settings, no
per-airport feature selection:**
- **B** — the frozen 5-feature set, REFIT on these three folds (not a
  reuse of F94/F96/F99/F100/F101/F103). Not B+L, B+D, B+T, or B+R either —
  D52/D53/D54/D55's own "measurement baseline is unchanged" rule.
- **B+P** — B plus `precip_rate_mmh` (one continuous feature, NO
  transform — no log1p, no binary wet/dry flag; a decoded zero is a real,
  kept dry-forecast value, per F104).

**Why two variants, not four (session prompt section 2, F104's own Step 0
finding).** `precip_window_hours` is a CONSTANT per airport (24h at
EGLC/LFPG/DSM, 26h at YSDU/RNO), so `apcp_cumulative_mm` and
`precip_rate_mmh` are monotone transforms of each other within any one
airport's own rows — LightGBM's tree splits are invariant to a monotone
per-feature transform, so to a tree they are the SAME feature. There is
therefore no meaningful raw-vs-resolved contrast to test, unlike E1–E4. No
Pv/v variant is defined — it would be identical to B+P by construction.

**Sanity check 5a (reserved-year guard) — PASS.** All three
`EXPERIMENT_FOLDS` entries cleared `assert_reserved_year_excluded()` before
any data was loaded; a defensive per-row scan found 0 reserved-year rows in
the loaded data.

**Sanity check 5b (feature-integrity check) — PASS, checked on every row,
not a spot check.** `precip_rate_mmh == apcp_cumulative_mm /
precip_window_hours` holds within a 1e-3 mm/h tolerance at all 7,952 rows
of both session57 output files, across all five airports (max abs diff
0.0000667 at EGLC/LFPG/DSM, 0.0000615 at YSDU/RNO — pure rounding noise on
the 3-decimal stored values, comfortably inside tolerance). `precip_
window_hours` confirmed CONSTANT per airport throughout: 24.0 at
EGLC/LFPG/DSM, 26.0 at YSDU/RNO — matching F104 exactly.

**An unplanned but strong internal-consistency signal, the same check
F99/F100/F101/F103 ran.** The `2025-26` fold's `B` variant (refit
5-feature baseline, trained on one fewer year than F94 because training
may not reach the reserved year) reproduces F94/F96/F99/F100/F101/F103's
own raw-GFS and persistence MAE and row counts almost exactly at every
airport: EGLC raw 1.2536 vs 1.254 (n=364 vs 364), LFPG raw 1.3822 vs 1.382
(n=364 vs 364), DSM raw 1.7334 vs 1.733 (n=365 vs 365), YSDU raw 1.3167 vs
1.317 (n=356 vs 356), RNO raw 1.5116 vs 1.512 (n=365 vs 365) — confirming
the pipeline (join, features, model settings) is a correct reproduction of
the frozen recipe.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, n=15
airport-folds per variant):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+P       1.267      -0.017      +1.3%
```

**Fold-averaged per airport (mean across the three folds), skill vs B:**

```
station   B+P
EGLC     +1.1%
LFPG     +0.9%
DSM      +0.6%
YSDU     -0.0%
RNO      +3.7%
```

**E5's own max grand-overall skill against E1–E4, stated plainly, per the
session prompt's own instruction.** E1's max (B+Lv, F99): +2.0%. E2's max
(B+Dv, F100): +4.1%. E3's max (B+T, F101): +0.9%. E4's max (B+Rv, F103):
+1.9%. **E5's max (B+P, this session): +1.3%** — E5 sits above E3, below
E4, well below E1 and E2. Ordered: E2 (+4.1%) > E1 (+2.0%) > E4 (+1.9%) >
E5 (+1.3%) > E3 (+0.9%).

**The specific question, read with the numbers: does precipitation add
skill on top of B?** A real, modest, mostly-positive result — not a clean
sweep, and not the null result a "precipitation is a weak, sparse signal"
prior might have predicted either. Four of five airports post a positive
fold-averaged skill; YSDU is flat (-0.0%).

**DSM, the diagnostic (F96: most headroom, cloud/wind already marginal
there) — unlike E3 and E4, precipitation adds a small but genuinely
positive, fold-robust signal.** DSM's fold-averaged skill is +0.6%, small
but positive in all three individual folds (2022-23 +0.6%, 2023-24 +0.3%,
2025-26 +1.0%) — the honest reading is that precipitation is the first
family since E1/E2 to add anything at all at DSM, where E3 (F101, -0.3% to
-1.0%) and E4 (F103, -0.2% to +0.1%) both left it flat or negative. The
signal is small, but it is real and consistent across every fold, not
carried by one.

**RNO — the family's strongest and most fold-robust result, by a wide
margin.** RNO's fold-averaged skill (+3.7%) is more than double any other
airport's, and positive in every individual fold (2022-23 +2.9%, 2023-24
+4.8%, 2025-26 +3.4%) — a real, durable signal, not a single-fold
artifact. This is consistent with RNO's own already-established character
(D42, the Sierra Nevada front) making precipitation timing a genuinely
informative signal there.

**EGLC and LFPG — the fold-averaged figure hides a real reversal in the
more recent folds, flagged explicitly rather than left in the average.**
EGLC's benefit (+3.7% in 2022-23, the thinnest fold) reverses to essentially
flat-to-negative in both later folds (2023-24 -0.2%, 2025-26 -0.6%) — the
fold-averaged +1.1% is carried entirely by the thinnest, least-trusted
fold. LFPG shows the same shape one fold later: positive in the two
earlier folds (2022-23 +2.1%, 2023-24 +1.4%) but negative in the most
recent (2025-26 -0.7%). Both patterns match the fold-quality caution
F96/D52–D55 already established for the 2022-23 and 2025-26 folds
specifically, not a new concern unique to precipitation.

**YSDU — flat, with no consistent sign across folds.** Fold-averaged skill
is essentially zero (-0.0%), and the three individual folds do not agree
in sign (2022-23 -0.7%, 2023-24 +0.5%, 2025-26 +0.2%) — the family's
weakest, least-consistent airport-level result.

**Per-fold spread, airport-averaged.** 2022-23 (thinnest, per
F96/D52–D55's own established caution): +1.6% — the family's largest
airport-averaged fold reading. 2023-24: +1.4%. 2025-26 (most recent, least
trusted): +0.8% — smaller than the two earlier folds, but **positive, not
a reversal to negative the way E3 (F101) showed across every variant in
this same fold.** E5 matches E4's shape here (stays positive in every
fold) rather than E3's (reverses to negative in the most recent fold).

**The known cross-airport inconsistency, already on record (F104),
reported again rather than papered over.** The since-start accumulation
window used for `precip_rate_mmh` is 24h at EGLC/LFPG/DSM and 26h at
YSDU/RNO — a mean over spans of different length at different airports.
Rate-normalisation handles the magnitude, not the span-length difference
itself. No per-airport statistical standardisation was used to hide this.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — session57's own output files already exclude it, and this
session's own defensive per-row scan found 0 reserved-year rows, on top of
the guard check on all three folds before any data was loaded. Did not
compute any pass/fail verdict anywhere — the two-variant grid is reported;
the family call is left to the owner's review in session 59 (D56). Did not
add a third or fourth variant, or any Pv/v variant — E5 carries effectively
one feature (F104), so none is defined. Did not do any per-airport feature
selection — identical features at every airport, in both variants, RNO
included. Did not add `lapse_rate_t2_t850` (D52), `dewpoint_depression_
t2m_floored` (D53), `pressure_tendency_3h_hpa` (D54), or `dswrf_2h_wm2`
(D55) to B — B stays the frozen 5-feature set only. Did not re-pull,
re-decode, or re-derive any precipitation field — reused session 57's own
committed output files unchanged. Did not modify `SPEC.md` or `RESULTS.md`.
Nothing was committed. Script: `scripts/session58_e5_experiment.py` (new).
Full real output: `notes/session-58-e5-experiment-output.txt`.

---

## 2026-09-21 — Session 59 decision: the E5 (precipitation) family verdict, from the owner's review of F105

**D56. Verdict: E5's adopted contribution to the eventual combine-phase sweep baseline is
the single feature `precip_rate_mmh` (the `B+P` variant) — the mean since-forecast-start
precipitation rate F104 built. Nothing is parked. Unlike E1 (D52) and E2 (D53), there is
no separate raw physical variable to weigh: F104 established E5 carries effectively one
feature (the raw cumulative total `apcp_cumulative_mm` is a monotone transform of the
rate, the same feature to a tree), so there is nothing to hold back as a combine-phase
candidate.**

**Rationale, kept plain.** `precip_rate_mmh` adds +1.3% grand-overall skill over the
frozen 5-feature baseline B (F105) — a real, mostly-positive result, above E3 (+0.9%) and
below E4 (+1.9%), the second-weakest family in the sweep. It is adopted because the signal
is genuine, physically motivated, and lands where the programme cares most. RNO shows the
family's strongest and most fold-robust benefit by a wide margin (+3.7%, positive in every
fold: +2.9% / +4.8% / +3.4%), consistent with the Sierra Nevada front (D42) making
precipitation timing informative there. DSM, the diagnostic, shows a small but fold-robust
positive signal (+0.6%, positive in all three folds) — the first family since E1/E2 to add
anything at all at DSM, where E3 (F101) and E4 (F103) both left it flat or negative.

**Honest caveats, recorded not hidden.** The strength is mid-low. EGLC's and LFPG's
fold-averaged benefit is carried by the earlier/thinnest folds and reverses to
flat-or-negative in the most recent fold(s) — the fold-quality caution F96/D52–D55 already
established for the 2022-23 and 2025-26 folds, not a defect unique to precipitation. YSDU
is flat (-0.0%) with no consistent sign across folds — the family's weakest airport. A
known mild cross-airport inconsistency stands (F104/F105): the since-start accumulation
window is 24h at EGLC/LFPG/DSM and 26h at YSDU/RNO, so `precip_rate_mmh` is a mean over
spans of slightly different length at different airports — carried forward as a limitation
the combine phase should be aware of, not a reason to withhold adoption. The family stays
net-positive in the most recent 2025-26 fold (+0.8%), matching E4's shape rather than E3's
reversal.

**On-record observation for the combine phase (NOT a parked candidate).** Precipitation's
benefit is uneven and concentrated: strong and durable at RNO, small but consistent at
DSM, thin-fold-carried at EGLC/LFPG, flat at YSDU. The combine phase should expect
precipitation to pull its weight mainly at RNO and DSM, and should watch the EGLC/LFPG
recent-fold softness when the adopted features are swept together. Grid:
`data/processed/session58_e5_experiment_grid.csv`.

**This is provisional.** Like every family in the sweep, `precip_rate_mmh` is confirmed
only when the single final feature set is checked on the reserved year once, at the finish
line (D51) — not now.

**E5 is the last family — the feature-selection sweep is now complete.** All five families
have a verdict against the same frozen 5-feature baseline B. Adopted into the eventual
combine-phase sweep baseline: `lapse_rate_t2_t850` (D52), `dewpoint_depression_t2m_floored`
(D53), `pressure_tendency_3h_hpa` (D54), `dswrf_2h_wm2` (D55), and `precip_rate_mmh`
(D56). Parked combine-phase candidates (separate raw variables held back for the sweep, not
in the baseline): RNO's raw pressure-level temperatures (D52) and relative humidity (D53).
E3, E4 and E5 parked nothing.

**Measurement baseline note.** No family remains to measure against B — E5 closes the
sweep. Adopted features enter together only at the combine phase. Cites F105.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`. Did not fit any
model or compute any new figure — every number above is copied from and cited to F105. Did
not touch the reserved 2024-08-01..2025-07-31 confirmation year.

---

## 2026-09-22 — Session 60 decision: the combine-phase sweep is pre-registered, before the run (session 61)

**D57. The combine-phase sweep is pre-registered here, before the run
(session 61), and enforced by the `scripts/session60_combine_design.py`
manifest. It sweeps the five adopted features (D52–D56) together, with the
two parked candidates (D52, D53) as options, on the three non-reserved
`EXPERIMENT_FOLDS` (D51), to select one single final feature set. That set is
then confirmed on the reserved 2024-25 year exactly once, at the finish line
(D51). No model was fit and no data row was read this session — design only
(the same setup-only shape as D51/session 48).**

**Baseline and harness.** Frozen baseline B is the proven 5-feature GRIB
recipe (SPEC section 7); it is never modified, and features enter only on top
of B. The harness is identical to E1–E5: the three non-reserved
`EXPERIMENT_FOLDS` (2022-23, 2023-24, 2025-26-truncated, D51), all five
airports (EGLC, LFPG, DSM, YSDU, RNO), the frozen LightGBM settings
(D21.4/D48.6), and no per-airport feature selection (identical features at
every airport). Metric: MAE, reported as skill percent vs B, at grand-overall
(mean across the 15 airport-folds), per-fold (airport-averaged), and
per-airport (fold-averaged) — the same three reads as every E-session.

**The variant ladder (14 variants, frozen in the manifest).** B (refit); the
five single-adds B+L / B+D / B+T / B+R / B+P; the full adopted set B+LDTRP;
the five leave-one-out variants from the full set; and the two parked-option
adds B+LDTRP+rh and B+LDTRP+plev (`plev` = `t850`,`t925`,`t700`). A compact,
pre-registered ladder is used rather than a blind 2^5 subset sweep: it holds
the number of comparisons down (less chance the "winner" is a fold-fluke,
which matters because only one reserved-year look protects the pick), and
each rung answers a specific keep/drop question, so the result is
interpretable, not just a bare winner.

**One complete-case row set for the whole selection.** Before any variant is
fit, build a single complete-case dataset over all seven candidate features
(`L`,`D`,`T`,`R`,`P`,`rh`,`plev` — i.e. their underlying columns). Within each
(airport, fold) every variant is fit and scored on identical rows; rows still
differ across airports and across folds, which is expected. There is no
per-variant or core-vs-parked row split — that would break the "same rows for
every variant" guarantee exactly where it matters. **Row-cost guard:** the run
reports, per airport per fold, how many rows the complete-case mask drops
versus a B-only mask; if that exceeds `ROW_COST_GUARD_FRAC` (5%) at any
airport-fold, the run halts and reports rather than proceeding, and the owner
decides in planning. (Not expected to trip: session 58/F105 found these GRIB
fields present wherever B is.) Honest consequence: B refit on this masked set
is not row-identical to F94, so its MAE here is not cross-comparable to F94's
— expected, do not cross-read the two.

**The "clearly worse" thresholds, fixed before the run.** Judged on relative
skill percent, not absolute degrees (MAE runs ~1.0–1.6 degC across airports,
so one degree would mean different things at different airports; percent is
how every family result was reported). A feature's contribution is read two
ways, each where it is reliable: **magnitude** — removing it must worsen the
fold-averaged (airport-averaged) skill by at least `TAU_SKILL` (0.4%, about
half the weakest adopted family, E3's +0.9%); and **robustness** — removal
must be worse in all three folds by sign (no fold where the feature looks
unhelpful). The full magnitude is not required in every fold — the thin
2022-23 fold is noisy and would randomly fail good features (F96/D52–D55
fold-quality caution). All keep/drop reads are at the airport-averaged level;
per-airport and per-fold figures stay diagnostic. **DSM is read as a
diagnostic only** (F96: most headroom, cloud/wind already marginal there) —
it is never a keep/drop vote.

**The selection rule (mechanical, applied by session 61 after the grid is in).**
(1) Start from the full set B+LDTRP. (2) Leave-one-out: a feature is kept if
removing it worsens fold-averaged skill by at least `TAU_SKILL` *and* is worse
in all three folds by sign; otherwise it is a candidate to drop. (3)
**Correlated-feature handling — never drop a correlated batch at once.** If two
or more features are flagged droppable together, drop only one — the one whose
removal does the least fold-averaged damage — resolving ties by `DROP_ORDER`
(`T`,`P`,`R`,`L`,`D`, weakest family first). Then re-measure leave-one-out on
the reduced set: a partner that was masked by the just-dropped feature may now
clear the bar and be kept. Repeat until nothing is flagged droppable. This
defeats the known trap where two overlapping features each look redundant only
because the other is present. (4) The survivors are the core set. (5) Parked
options: test B+core+rh and B+core+plev, each adopted only if it adds at least
`TAU_SKILL` fold-averaged and helps in all three folds by sign, airport-
averaged; `plev` must clear the bar airport-averaged across all five airports
(the recipe-travels tax — an RNO-only gain does not qualify, which is why it
was parked, not adopted). (6) Ties go to the smaller set. (7) No per-airport
selection; DSM diagnostic only. Cloud cover is inside frozen B and is never
dropped, so any feature that overlaps a B feature (e.g. `rh`/`R` vs cloud) is
only ever judged on what it adds *given* B — the correct question.

**Joint backstop, with stop-and-surface.** Leave-one-out reads each feature
given all the others, so the exact set the rule lands on may never have been
fit as a whole. So after the rule selects a set, refit that exact set on the
three folds and confirm: (a) it beats B by at least `TAU_SKILL` fold-averaged,
worse-by-sign in no fold; and (b) it is not meaningfully worse than the full
B+LDTRP model (within `TAU_SKILL`). If either check fails — evidence of
over-pruning or a joint loss — session 61 halts and surfaces the failure with
the full grid. It does not auto-unwind and does not auto-pick a set. The owner
resolves it in the session-62 review. No unsupervised selection of the final
recipe.

**Integrity and reuse guards session 61 must run.** (i) Reuse the committed
feature columns from the E1–E5 build sessions; do not rebuild, re-decode, or
re-derive any feature. (ii) Per-row feature-integrity check on the assembled
table: every feature column matches its committed source file within
tolerance, checked on every row (the same check F105 ran); report pass/fail
and max abs diff. (iii) Internal-consistency check on the join: the refit-B
2025-26 fold must reproduce F94/F96/F99–F105's raw-GFS and persistence MAE
and row counts at every airport, within rounding; report the comparison. (iv)
Report the pairwise-correlation matrix among the candidate features up front,
so the reviewer can see which drop decisions sit in the danger zone.

**Reserved-year and sealed-year discipline.** The reserved 2024-25 year
(2024-08-01..2025-07-31, D51) is not read at all — not this session, not in
the session-61 run. All selection is on the three non-reserved folds only.
Note explicitly: the 2025-26 fold does test on the sealed year
(2025-08-01..2026-07-31, F94), by design — D51 built the folds this way, with
training truncated so they never reach the reserved year — and that is
descriptive reuse, not a fresh verdict look. The single confirmation at the
finish line is on the reserved 2024-25 year, once, after the set is frozen; it
is never a second look at 2025-26. Session 61 must clear
`assert_reserved_year_excluded()` on all three folds before loading any data,
and run a defensive per-row scan confirming zero reserved-year rows (same as
the E-sessions). Carried forward for the finish line: when the frozen set is
confirmed on 2024-25, apply the same complete-case rule over the final set's
features (drop and count rows missing any final-set feature), so the
confirmation matches how the set was selected.

**One wrinkle found while building the manifest, flagged for session 61
rather than resolved silently.** E2's adopted feature,
`dewpoint_depression_t2m_floored` (D53), is not itself a stored column in
`session51_v16_window_with_moisture.csv` or its sealed-window counterpart —
only the raw `dewpoint_depression_t2m` is committed. F100 (session 52) is
explicit about why: the floor (`max(dewpoint_depression_t2m, 0)`, changing
exactly 1 of 7,952 rows) was applied only in that session's own feature
matrix, and "the original column is kept intact" on disk. This is not a
disagreement between SPEC and this session's prompt, and not a new
derivation — the floor formula is already fully pinned by D53/F100 — but it
is a real gap between "committed column" (`dewpoint_depression_t2m`) and
"adopted feature name" (`dewpoint_depression_t2m_floored`) that the session
prompt's own "reused as already built and committed, nothing re-derived"
framing did not anticipate. `CANDIDATE_FEATURES['D']` in the manifest
therefore names the stored raw column plus this exact one-line transform as
a `transform` field, and the header-only pre-flight checks for
`dewpoint_depression_t2m` (the column that actually exists), not a
`_floored` column that does not. Session 61 must apply the transform exactly
as pinned — nothing else — when it builds the complete-case feature matrix.

**What this decision did not do.** Did not fit any model or compute any MAE.
Did not read any data row, from the reserved year, the sealed year, or any
other year — the pre-flight reads headers only. Did not modify `SPEC.md` or
`RESULTS.md`. Nothing was committed. Manifest:
`scripts/session60_combine_design.py` (new). Pre-flight output:
`notes/session-60-preflight-output.txt`.

---

## 2026-09-22 — Session 61 finding: the combine-phase sweep is run exactly as
pre-registered (D57). The mechanical selection rule's OUTPUT is a candidate
set, B+LDRT (drops P; neither parked option adopted) — NOT a verdict. The
reserved 2024-25 year was never read.

**F106. Runs the 14-variant ladder pre-registered in D57 on the three
non-reserved `EXPERIMENT_FOLDS` (D51), applies the mechanical selection rule
with its correlated-feature safeguard and joint backstop exactly as
pre-registered, and reports the grid. Per the session prompt, this is
explicitly NOT a verdict and NOT a decision — the mechanically-produced set
is reported for the session-62 owner review to confirm or override. The
reserved 2024-08-01..2025-07-31 confirmation year (D51) was never read, at
all, this session.** Script: `scripts/session61_combine_sweep.py` (new). Full
real output: `notes/session-61-combine-sweep-output.txt`. Tables: `data/
processed/session61_combine_sweep_grid.csv` (210 rows: 5 airports x 3 folds x
14 variants), `session61_combine_sweep_summary.csv` (126 rows: fold-averaged-
per-airport, airport-averaged-per-fold, grand-overall), `session61_row_cost_
guard.csv` (15 rows), `session61_correlation_matrix.csv` (9x9).

**Two interpretation decisions, made explicit in the script's own module
docstring and flagged here for the session-62 review to check (not a SPEC/
prompt disagreement — a judgment call in turning D57's English rule into
code):**
1. "DSM is diagnostic only — never a keep/drop vote" (D57), read together
   with "all keep/drop reads are at the airport-averaged level" immediately
   before it: every mechanical keep/drop/adopt/backstop decision averages
   over the FOUR non-DSM airports (EGLC, LFPG, YSDU, RNO). DSM is still fit
   and reported in the full grid/summary (all five airports) throughout.
2. `plev`'s own explicit override — "must clear the bar airport-averaged
   across all five airports" — is read as overriding decision 1 specifically
   for `plev`'s own adoption test: voted on using all five airports,
   including DSM, unlike every other keep/drop/adopt decision.

**Guards and integrity checks, all PASS.** Reserved-year guard cleared on all
three `EXPERIMENT_FOLDS` entries before any data was loaded; a defensive
per-row scan of the five E1-E5 committed source files found 0 reserved-year
rows. The complete-case row set (all seven candidate features' underlying
columns present) turned out to be **exactly identical** to a B-only mask
built from the true base 5-feature dataset (`grib_features_v16_window/
sealed_window.csv`, reserved year excluded) — the row-cost guard shows
**0 rows dropped at all 15 airport-folds** (not merely under the 5%
`ROW_COST_GUARD_FRAC`, literally zero), because the five E1-E5 build sessions
each joined onto the identical date list with zero drops of their own
(F98/F100/F101/F102/F104). Integrity check (i): every candidate feature
column in the assembled table matches its committed source file (or D53/
F100's own frozen floor transform applied to the stored raw column) exactly
on every one of 7,952 rows — max abs diff 0.0 throughout; a bonus check
(base columns temp/cloud/wind cross-file consistency, beyond the session
prompt's own item) also PASS, max abs diff 0.0. Integrity check (ii): the
refit-B 2025-26 fold reproduces F94/F96/F99-F105's own raw-GFS and
persistence MAE and row counts at every airport exactly (all five stations
MATCH, e.g. EGLC raw=1.2536 vs reference 1.254, YSDU n=356 vs reference 356).

**Correlation matrix (pooled, all five airports, n=7,952), the two strongest
relationships, both physically expected, neither a surprise:** `dewpoint_
depression_t2m_floored` (D) and `relative_humidity_2m` (rh) at -0.948 (a
lower dewpoint depression is a wetter, higher-humidity air mass, almost by
definition); the three pressure levels `t850`/`t925`/`t700` mutually at
0.88-0.97 (adjacent levels of the same smooth vertical temperature profile).
D also correlates with R (`dswrf_2h_wm2`, 0.747) and with `t850` (0.693) —
clear-sky, low-humidity conditions bring both more shortwave and a warmer
mid-level temperature together. T (`pressure_tendency_3h_hpa`) is the most
independent of the five adopted features, weakly-to-moderately anti-
correlated with D (-0.461) and R (-0.355) and otherwise low. Full matrix:
`session61_correlation_matrix.csv`.

**Grid result — grand overall (mean MAE across 5 airports x 3 folds, n=15
airport-folds), all 14 variants:**

```
variant        mean_MAE   skill_vs_B
B               1.284        --
B+L             1.260      +1.9%
B+D             1.233      +4.0%
B+T             1.273      +0.9%
B+R             1.266      +1.4%
B+P             1.267      +1.3%
B+LDTRP         1.210      +5.7%
B+DTRP          1.212      +5.6%   (drop L)
B+LTRP          1.223      +4.7%   (drop D)
B+LDRP          1.217      +5.2%   (drop T)
B+LDTP          1.218      +5.1%   (drop R)
B+LDTR          1.213      +5.5%   (drop P)
B+LDTRP+rh      1.208      +5.9%
B+LDTRP+plev    1.204      +6.2%
```

Every single-add grand-overall figure reproduces its own E-session's own
grand-overall figure almost exactly, despite the row set here being the
narrower seven-feature complete-case set rather than each family's own
four-variant experiment: B+L +1.9% (F99's own B+Lv max was +2.0%, B+L alone
was also +1.9% there), B+D +4.0% (F100's own B+D was +4.0% exactly), B+T
+0.9% (F101's own B+T was +0.9% exactly), B+R +1.4% (F103's own B+R was
+1.4% exactly), B+P +1.3% (F105's own B+P was +1.3% exactly) — strong
independent confirmation the combine-phase harness reproduces each family's
own prior reading faithfully.

**Selection rule trace (D57 Steps 8-12), all votes on the non-DSM
airport-averaged basis (interpretation decision 1 above) unless noted:**

*Round 1* — full set B+D,L,P,R,T, fold-averaged skill vs B (non-DSM) =
+5.61%, per-fold [+5.42%, +6.84%, +4.56%]:
```
remove D -> B+LPRT   skill=+5.18%  magnitude=+0.43pp  robust=False  DROP CANDIDATE
remove L -> B+DPRT   skill=+5.19%  magnitude=+0.41pp  robust=False  DROP CANDIDATE
remove P -> B+DLRT   skill=+5.48%  magnitude=+0.12pp  robust=False  DROP CANDIDATE
remove R -> B+DLPT   skill=+4.42%  magnitude=+1.19pp  robust=True   KEEP
remove T -> B+DLPR   skill=+4.90%  magnitude=+0.71pp  robust=True   KEEP
```
Three features (D, L, P) flagged droppable together — the correlated-feature
safeguard (D57 Step 10) fired. Dropped only the least-fold-averaged-damage
one, **P** (magnitude +0.12pp, the smallest of the three) — `DROP_ORDER`'s
tie-break was not needed, the magnitudes were already distinct.

*Round 2* — reduced set B+D,L,R,T, fold-averaged skill vs B (non-DSM) =
+5.48%, per-fold [+4.75%, +6.55%, +5.15%]:
```
remove D -> B+LRT    skill=+4.21%  magnitude=+1.27pp  robust=True   KEEP
remove L -> B+DRT    skill=+5.08%  magnitude=+0.41pp  robust=True   KEEP
remove R -> B+DLT    skill=+3.96%  magnitude=+1.53pp  robust=True   KEEP
remove T -> B+DLR    skill=+4.04%  magnitude=+1.45pp  robust=True   KEEP
```
Nothing flagged droppable — **CORE SET = B+D,L,R,T** (i.e. B+LDRT).

**Parked-option tests (D57 Step 11) — neither adopted, both actively
worsened the core set's own skill when added:**
```
rh   : core skill(non-DSM)=+5.48%  core+rh skill(non-DSM)=+4.98%  magnitude=-0.51pp  robust=False  DO NOT ADOPT
plev : core skill(ALL 5)  =+5.55%  core+plev skill(ALL 5) =+5.29%  magnitude=-0.26pp  robust=False  DO NOT ADOPT
```
`plev`'s own vote used all five airports per its explicit D57 override
(interpretation decision 2); both parked options failed on magnitude alone
(negative, not merely sub-threshold), so the "ties go to the smaller set"
clause (D57 Step 12) was never in play.

**FINAL SET (mechanical rule output): B+D,L,R,T — i.e. the full adopted
set minus P (precipitation), with neither parked option added.**

**Joint backstop (D57 Steps 13-14) — PASS:**
```
final set skill vs B (non-DSM, fold-averaged): +5.48%  per-fold [+4.75%, +6.55%, +5.15%]
final set skill vs B (ALL 5,   fold-averaged): +5.55%  per-fold [+4.67%, +6.34%, +5.64%]
full B+LDTRP skill vs B (non-DSM, fold-averaged): +5.61%  per-fold [+5.42%, +6.84%, +4.56%]

check (a) beats B by >= 0.4pp fold-averaged AND worse-by-sign in no fold: True AND True => True
check (b) not meaningfully worse than full B+LDTRP (gap=+0.12pp <= 0.4pp): True
```
Both checks pass. The mechanical rule did not halt.

**DSM, reported as diagnostic only, never a vote (F96/D57):** at DSM, the
full set B+LDTRP reads +6.1% fold-averaged (its own best single addition is
D, +6.2% alone — the moisture-dominance pattern D53/F100 already
established there); the mechanically-produced final set B+LDTR (missing P)
reads +5.7% at DSM — a diagnostic-only 0.4pp softer than the full set at
this one airport, consistent with DSM never having shown a strong precip
signal in F105 either (DSM's own B+P fold-averaged there was a modest
+0.6%). This did not affect the vote, which excludes DSM by design.

**What this finding does and does not mean.** This is the mechanical
selection rule's OUTPUT under D57's pre-registered design, applied exactly
as written (subject to the two interpretation decisions above, which the
session-62 review should check). It is explicitly **not a verdict** — no
pass/fail bar was applied, and the reserved 2024-25 confirmation year was
never touched. The session-62 owner review may confirm B+D,L,R,T as the set
to carry to the reserved-year confirmation (D51), or may read the two
interpretation decisions differently and re-derive a different set from the
same grid (all 210 grid rows, the correlation matrix, and the full selection
trace are on record for that purpose) — either way, D57's own one-look
discipline for the reserved year is unaffected by this session either way.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year (D51)
— the five E1-E5 committed source files already exclude it (confirmed by a
defensive per-row scan, 0 hits), and no code path in this script references
`RESERVED_YEAR_START`/`RESERVED_YEAR_END` except to exclude them. Did not
compute or declare a verdict — the mechanical rule's output is reported as
exactly that, an output, not a decision (the session prompt's own framing,
repeated throughout this script's own printed output). Did not rebuild,
re-decode, or re-derive any feature beyond re-applying D53/F100's own
already-frozen one-line floor transform to the stored raw column. Did not
modify `SPEC.md` or `RESULTS.md`. Nothing was committed.

---

## 2026-09-22 — Session 62 decision: the final feature set is locked, and the
reserved-year confirmation script is frozen and pre-flighted. The reserved
year is NOT opened this session. A reserved-year feature-data gap was
discovered and is flagged for the owner before session 63 can run.

**D58. The single final feature set is locked: B + D, L, R, T — the frozen
5-feature GRIB baseline B (SPEC section 7) plus moisture `D`
(`dewpoint_depression_t2m_floored`), lapse rate `L` (`lapse_rate_t2_t850`),
shortwave radiation `R` (`dswrf_2h_wm2`), and pressure tendency `T`
(`pressure_tendency_3h_hpa`). Precipitation `P` is dropped. Neither parked
option (`rh`, `plev`) is adopted. This is the D57 mechanical rule's own
output (F106), confirmed unchanged in the session-62 owner review.**

**1. The final set.** B + D, L, R, T, chosen in the session-62 owner review
of F106's grid and selection trace. This is exactly the mechanical rule's
own output under D57 — the owner reviewed the full 210-row grid, the
correlation matrix, and the selection trace (F106) and found no reason to
override it. Cites D57, F106.

**2. The two interpretation calls, confirmed.** (i) All keep/drop/adopt/
backstop votes in F106 average over the four non-DSM airports (EGLC, LFPG,
YSDU, RNO) — the only coherent reading of D57's "DSM is diagnostic only,
never a keep/drop vote" read together with its "all keep/drop reads are at
the airport-averaged level." (ii) `plev`'s own adoption test used all five
airports, per its explicit D57 override ("must clear the bar
airport-averaged across all five airports"). This was outcome-neutral:
`plev` failed on magnitude alone (−0.26pp against the core set, F106),
so which airport basis was used made no difference to its rejection. Both
readings are confirmed as the record's own, closing them for good.

**3. The exact feature resolution.** Session 63's frozen script
(`scripts/session62_reserved_confirm.py`) reuses the identical
`CANDIDATE_FEATURES` resolution (source file, column, and transform) for
D, L, R, T that the session-60 manifest and the session-61 sweep used:

| code | committed column | source files | transform |
|---|---|---|---|
| L | `lapse_rate_t2_t850` | `session49_v16_window_with_upper_air.csv` / `session49_sealed_window_with_upper_air.csv` | none |
| D | `dewpoint_depression_t2m` | `session51_v16_window_with_moisture.csv` / `session51_sealed_window_with_moisture.csv` | `dewpoint_depression_t2m_floored = max(dewpoint_depression_t2m, 0)` (D53/F100's own frozen one-line floor; changes exactly 1 of 7,952 rows) |
| T | `pressure_tendency_3h_hpa` | `session53_v16_window_with_pressure.csv` / `session53_sealed_window_with_pressure.csv` | none |
| R | `dswrf_2h_wm2` | `session55_v16_window_with_radiation.csv` / `session55_sealed_window_with_radiation.csv` | none |

No feature is rebuilt, re-decoded, or re-derived — the frozen script
re-applies only D53/F100's own already-pinned floor formula to the stored
raw column, exactly as D57/F106 already did. `P`, `rh`, `plev` are excluded
from the recipe entirely — confirmed absent from the script's own
`FAMILY_KEYS`/`FINAL_CODES` by an in-code assertion.

**4. The confirmation fold (deterministic date arithmetic), pinned in
`scripts/session62_reserved_confirm.py`'s own `CONFIRMATION_FOLD`:**
```
train  2021-03-24 .. 2024-07-31
test   2024-08-01 .. 2025-07-31   (the reserved year — the one authorized look)
```
All five airports (EGLC, LFPG, DSM, YSDU, RNO), the frozen LightGBM settings
(D21.4/D48.6, byte-identical to every prior modelling script in the
programme), no per-airport feature selection.

**5. Complete-case rule (D57 carried forward).** The complete-case row set
is built over only the final-set features' underlying columns — the
columns backing D (raw `dewpoint_depression_t2m`), L, R, T — not the full
seven-feature set F106 used. **Pre-registered expectation: 0 rows dropped**
against a B-only mask, on the training window (F106 found the seven-feature
complete-case set identical to the B-only rows at every airport-fold, and
the four-feature subset can only be a superset of those complete-case rows,
never a smaller one). Verified true on the training window this session
(item 9 below): 1,226/1,226/1,225/1,225/1,225 complete-case rows at
EGLC/LFPG/DSM/YSDU/RNO respectively, matching F98/F100/F101/F102's own
per-airport row counts for that span exactly. **The test-window (reserved
year) row count cannot be checked this session — see the flagged gap,
item 11, below.**

**6. What is scored, per airport, when session 63 runs the confirmation:**
raw-GFS MAE, persistence MAE, refit-B MAE, and refit-(B+D,L,R,T) MAE, on
the reserved-year test set, plus the day-set reconciliation across all four
rungs (F93's own pattern — persistence scored on the subset of test days
with a usable previous-day observation, SPEC 2.1d; raw/B/B+DLRT scored on
the full test set; any mismatch reported, not hidden).

**7. Pre-registered expectations, fixed now, before the look:**
- **The bar (the deliverable):** B+D,L,R,T beats **both** raw GFS **and**
  persistence on MAE at **all five** airports.
- **Secondary read:** B+D,L,R,T beats plain B on the airport-averaged MAE.
  Per-airport variation is expected and allowed — especially at **DSM**,
  where the added features are marginal (F96, and F106's own DSM-diagnostic
  reading of +5.7% for this exact set against the full set's own +6.1%) —
  no per-airport 5-beats-B claim is pre-registered.
- The run reports the outcome against these expectations whatever it is;
  all results are reported; there is no re-run and no tuning after the
  look.

**8. The honesty caveat for the writeup, stated plainly.** The reserved
year was seen once, descriptively, for baseline B only, in F96's multi-year
backtest — but the feature-selection itself (which features to add) never
touched it: E1–E5 (F98–F105) and the combine sweep (F106) ran only on the
three non-reserved `EXPERIMENT_FOLDS`. So session 63's run is a genuine
first look at the *selected set* on 2024-25, not blind in the sense that no
one has ever computed anything on that year (F96 already has, for B alone)
but genuinely first for B+D,L,R,T specifically. Frame it as such when the
result is written up — neither overclaiming blindness the programme does
not have, nor understating that this is the first look at the chosen
recipe.

**9. One-look discipline.** Session 63 runs the frozen confirmation once,
unchanged. A guard that trips on something outcome-orthogonal (row counts,
scored-day-set reconciliation, the same shape as F92/F93) may be corrected
and re-committed *before* the look, because no MAE is seen when it trips —
but the features, model, fold, and bar never change once the look is
taken. This is exactly the shape of the guard already built into
`run_confirm()` (item 11 below): it can be fixed and rerun freely because
it trips before any model is fit.

**10. What this session did not do.** Did not open the reserved year in
any of the four senses ruled out by the session prompt's own hard scope
guard: no reserved-year row was read, loaded, fit on, or scored. No MAE was
computed anywhere on 2024-08-01..2025-07-31. Did not modify `SPEC.md` or
`RESULTS.md`. Did not archive any DECISIONS entry — D52–D57/F106 stay live,
per the session prompt's own instruction, since they remain load-bearing
for session 63.

**11. A reserved-year FEATURE-DATA gap, discovered while building the
confirmation script, verified directly (not assumed), and flagged here for
the owner rather than worked around — this is the one open item before
session 63 can run.** While assembling `scripts/session62_reserved_
confirm.py`'s own feature-loading code, a direct read of every date column
in all eight E1–E4 committed files (the `v16_window`/`sealed_window` pairs
for L, D, T, R — sessions 49, 51, 53, 55) showed:

```
family  v16_window span              sealed_window span             reserved-year (2024-08-01..2025-07-31) rows
L       2021-03-24 .. 2024-07-31     2025-08-01 .. 2026-07-31        0
D       2021-03-24 .. 2024-07-31     2025-08-01 .. 2026-07-31        0
T       2021-03-24 .. 2024-07-31     2025-08-01 .. 2026-07-31        0
R       2021-03-24 .. 2024-07-31     2025-08-01 .. 2026-07-31        0
```

This is not a defect in those sessions — F98's own text already says so
plainly ("the reserved year's ~365 days are simply absent rather than
replaced"), because D51 (in force at the time) forbade any feature
experiment from touching the reserved year at all, and sessions 49/51/53/55
built their date lists directly from that rule. **But the direct
consequence, not previously stated anywhere on record: there is no L, D,
T, or R feature value, for any airport, for any date in
2024-08-01..2025-07-31, in any committed file.** The confirmation fold's
*training* window (2021-03-24..2024-07-31) is fully covered — verified
this session, item 5/9 above — but its *test* window is the reserved year
itself, and that window has zero rows of the four adopted features.

**Consequence for session 63.** `scripts/session62_reserved_confirm.py`'s
`run_confirm()` cannot assemble a complete-case B+D,L,R,T feature matrix
for the reserved year as the committed files stand today — there is
nothing to assemble. The function contains a hard, loud guard (checked
per airport, before any model is fit) that raises a clear `RuntimeError`
naming this gap rather than silently scoring on zero or partial rows, so
if session 63 is run against the files as they exist right now, it stops
immediately with an explanatory error — it does not consume the one
authorized look on a broken or misleading result. **This gap must be
closed before session 63 can produce a real confirmation.** Two ways to
close it, neither decided here (out of this session's lock-only scope,
and the owner's call): (a) a data-build step — reusing the exact,
already-frozen pull/decode/derive code from sessions 49, 51, 53 and 55
unchanged, only extending the date range each already-frozen pipeline
covers to include 2024-08-01..2025-07-31 — run before session 63's
confirmation step, most likely as session 63's own first task or as a
short session 62b; or (b) some other resolution the owner prefers. Pulling
new GRIB data for the reserved year's dates is not itself a "feature
experiment" that D51 forbids (no model is fit, no MAE is read, nothing is
selected) — it is a data-engineering prerequisite the feature-selection
programme's own design did not anticipate needing, since every session
before this one only ever needed the reserved year excluded, never
included. Flagged here per CLAUDE.md's standing instruction to stop and
report rather than silently resolve a session-prompt assumption that does
not hold against the real, checked state of the data.

**What this session did not do (continued).** Did not pull, decode, or
derive any new GRIB data for the reserved year — closing the gap above is
explicitly out of this lock-only session's scope. Did not run
`run_confirm()` at any point — only `preflight()` was executed (`python
scripts/session62_reserved_confirm.py`, no arguments), and it never calls
`run_confirm()`. Real pre-flight output: `notes/
session-62-preflight-output.txt`. The pre-flight's own machinery dry-run on
the already-non-reserved 2023-24 `EXPERIMENT_FOLD` exactly reproduces
session 61's own `B+LDTR` grid row at every airport (raw MAE, persistence
MAE, and B+D,L,R,T MAE match to the fourth decimal at EGLC, LFPG, DSM,
YSDU and RNO) — strong, independent confirmation that this frozen script's
own fit/score machinery is a correct reproduction of the programme's
recipe, not a re-implementation that only looks similar. Scripts:
`scripts/session62_reserved_confirm.py` (new, frozen). Full real output:
`notes/session-62-preflight-output.txt`.

---

## 2026-09-22/23 — Session 63 finding: the reserved-year feature build closes
D58 item 11. Data build only — the reserved year was opened FOR DATA ONLY, no
fit, no score, no selection. `run_confirm()` was never called.

**F107. Extends the already-frozen L, D, T, R pull/decode/derive pipelines
(sessions 49/51/53/55's own code, reused by import, unchanged) to cover the
reserved 2024-08-01..2025-07-31 confirmation year, and applies the one
wiring addition to `scripts/session62_reserved_confirm.py` that Step 0
determined was needed so the frozen confirmation script can see the new
files. Closes the blocker D58 item 11 named. No model was fit. No MAE,
skill, or CV was computed anywhere. `run_confirm()` was never called.**
Script: `scripts/session63_reserved_year_build.py` (new). Full real output:
`notes/session-63-reserved-build-output.txt`. New data files: `data/
processed/session63_reserved_window_with_upper_air.csv`,
`..._with_moisture.csv`, `..._with_pressure.csv`, `..._with_radiation.csv`
(365 rows x 5 airports = 1,825 rows each), plus four
`session63_<family>_join_drops.csv` logs (all empty) and four pull
manifests under `data/raw/diagnostics/session63/` (all 0 FAIL).

**Step 0 — wiring determination, CASE (B).** Reading `scripts/
session62_reserved_confirm.py` first, per the session prompt: its
`load_family()` reads exactly the two files named in `session60_combine_
design.CANDIDATE_FEATURES[code]` (`v16_file`, `sealed_file` — the sessions
49/51/53/55 committed family files) and treats any row whose date falls
inside the reserved year as a "hit" that `run_confirm()` then raises on.
No third, per-family reserved-year source file was already referenced
anywhere in the frozen script or in `CANDIDATE_FEATURES` — so CASE (A) (a
pre-existing but empty reference) did not hold. **CASE (B) held**: a
minimal wiring addition was needed. Applied to `scripts/
session62_reserved_confirm.py` only, in two places: (1) a new module-level
`RESERVED_FAMILY_FILES` dict naming the four `session63_reserved_window_
with_*.csv` files this session produces, one per adopted family; (2) three
new lines at the end of `load_family()` that, if the mapped file exists,
read it and add its rows to the same per-station/date dict `load_family()`
already returns — WITHOUT running those rows through the exclusion check
(they are supposed to be inside the reserved year, by construction of the
file; a defensive assertion raises if one is not). **`session60_combine_
design.py`'s `CANDIDATE_FEATURES` dict was NOT touched** — it stays
byte-for-byte what session 61 already used, so session 61's own
already-reported result (F106) is untouched by this edit. This is an
outcome-orthogonal wiring change (it only affects which rows load, before
any model is fit) of the same class D58 item 9 already named as
pre-look-safe (the F92/F93 guard-fix pattern) — `git diff --stat` confirms
only `scripts/session62_reserved_confirm.py` changed, +47 lines, and
`ast.parse` confirms it still parses correctly. **Neither `preflight()` nor
`run_confirm()` was executed this session** — both fit or would fit a
LightGBM model (preflight()'s own "machinery dry-run" step), which this
session's scope guard forbids ("no model fit ... anywhere"); the wiring
change was verified instead by a separate, read-only, model-free script
(not committed — a scratch check, csv-only, no lightgbm import) that
reproduced `load_family()`'s exact logic and confirmed: 0 hits in the two
original files (unchanged), 1,825 rows added from the four new files
(365 x 5), and — mirroring `build_complete_case`'s own intersection
logic — exactly 365 complete-case reserved-year rows at every airport
(previously 0, per D58 item 11) and 1,226/1,226/1,225/1,225/1,225
complete-case training-window rows at EGLC/LFPG/DSM/YSDU/RNO, matching
D58 item 5's own already-verified count exactly.

**Step 1 — reserved-year date list, built from the base dataset's own
rows.** `data/processed/grib_features_v16_window.csv` filtered to
`target_date` in 2024-08-01..2025-07-31: exactly 365 dates per airport
(2024-08-01..2025-07-31), at all five airports — EGLC, LFPG, DSM, YSDU,
RNO. This is the base 5-feature dataset's own real dates, not an assumed
continuous calendar (mirroring how sessions 49/51/53/55 built their own
date lists from the same file).

**Step 2 — the inverted guard.** `assert_reserved_year_excluded()` was
never called on these dates (it would raise on every one). Instead, the
inverse was asserted and printed for every airport: all 365 dates
confirmed INSIDE 2024-08-01..2025-07-31, at every airport. `scripts/
session48_reserved_year.py` and its `RESERVED_YEAR_START`/`RESERVED_YEAR_
END` constants were only read, never edited.

**Step 3 — the four frozen pipelines, run over the reserved year.**
Elevation corrections (D48.3/F90, reused by import from `scripts/
session49_upper_air_pull.py`, unchanged): EGLC +0.2486, LFPG -0.1697, DSM
-0.1106, YSDU +0.2461, RNO +2.0436 °C — identical to F90/F99's own figures.
Each family's own `build_combos`/`process_combo` (or, for radiation, the
de-accumulation-aware variants) was imported directly from that family's
build script and run unchanged over the reserved-year date list; only the
JOIN step was newly written (the arithmetic copied verbatim from each
family's own `build_joined()`, since that function hard-codes "skip any
date inside the reserved year" and this session needs the opposite
filter — documented in full in `scripts/session63_reserved_year_build.py`'s
own module docstring).

```
family      combos   elapsed    messages requested/decoded_ok/failed
L (upper_air)  1460   13.02 min  t925 1825/1825/0, t850 1825/1825/0, t700 1825/1825/0
D (moisture)   1460   13.68 min  RH 1825/1825/0, DPT 1825/1825/0, SPFH 1825/1825/0
T (pressure)   1460   14.82 min  PRMSL 1825/1825/0, PRES:sfc 1825/1825/0, PRMSL@lead-3 1825/1825/0
R (radiation)  1460    7.40 min  dswrf_to_lead 1825/1825/0, dswrf_to_lead_minus2 1095/1095/0
```

**Zero pull failures across all four families (0 FAIL rows in every
manifest, 4,380/4,380/4,380/2,190 total requests respectively).** Free
disk space: 10.88 GiB before the first pull, 10.97 GiB after all four
(fetch-decode-discard throughout, per D47/F98's own precedent — no raw
GRIB2 bytes kept; a defensive scan after the run found zero leftover
`_scratch_*.grib2` files in any of the four families' own diagnostic
directories).

**Step 4 — verify, real numbers, at every airport, every family.** Join
drops: **0 at every airport, every family** (`session63_<family>_join_
drops.csv` empty in all four cases). Row counts: **output row count equals
the base dataset's own reserved-year row count (365) at every airport,
every family** — EGLC/LFPG/DSM/YSDU/RNO all MATCH, all four families.
Nulls in every derived/committed column: **0**, with one expected, honest
exception — `dswrf_ave_to_lead_minus2_wm2` shows `n_null=730` (2 airports x
365 days), which is NOT a defect: YSDU and RNO are the lead-26 airports
whose native DSWRF window is already the target 2-hour window, so no
second (lead-2) message is fetched for them and this raw endpoint column is
genuinely not applicable there — the exact same convention F102/session55's
own `build_joined()` already uses (blank, not a filled zero, per SPEC 2.2).
Manifests: 0 FAIL rows in all four.

**Spot-checks, physical plausibility.** L/EGLC 2024-08-01: t2m_raw=26.792,
t925=17.656, t850=14.26, t700=3.829, lapse_rate_t2_t850=12.532 —
colder-with-height (t2m_raw > t925 > t850 > t700): YES. L/RNO reserved-year
means: t2m_raw=15.94, t925=20.52 — RNO's surface-to-925hPa inversion (F98,
a real elevation effect at RNO's 1,345 m, not a defect) reproduces here too,
exactly as expected. R/EGLC reserved-year mean `dswrf_2h_wm2`=414.95 W/m2,
0 negative values. T/EGLC reserved-year mean `pressure_tendency_3h_hpa`
=-0.302 hPa (well inside the ±15 hPa sanity range). D/EGLC: 0 rows where
`dew_point_2m` > `t2m_raw` (the physical-sanity check F91/session51 already
established).

**Step 5 — B-completeness check on the reserved year (read-only, no model,
no score).** `temperature_grib_c`, `cloud_cover_grib_pct`,
`wind_speed_grib_kmh` in the base dataset's own reserved-year rows: **0
nulls, at every airport, every column** (365 rows checked per airport).
PASS — this would not have blocked session 64 even before this session's
own build closed the L/D/T/R gap.

**D58 item 11's gap is now closed.** Before this session, `run_confirm()`'s
own hard guard (D58 item 11, session 62) would have stopped immediately —
every one of L/D/T/R had zero rows anywhere inside the reserved year, in
any committed file. After this session, the reserved year has real,
validated L/D/T/R feature values, at every airport, matching the base
dataset's own row count exactly, with zero drops and zero nulls. Session 64
can now run `scripts/session62_reserved_confirm.py --confirm` once,
unchanged, on the 2024-25 fold, per D58's own pre-registered plan.

**What this session did not do, on purpose.** Did not fit any model,
anywhere, in any script (including not running `session62_reserved_
confirm.py`'s own `preflight()`, which fits LightGBM in its "machinery
dry-run" step — verified instead by a separate, model-free, csv-only
scratch check). Did not compute any MAE, skill, or CV. Did not call
`run_confirm()` — session 64 alone spends the single authorized look
(D51). Did not touch the sealed 2025-08-01..2026-07-31 year (F94) — no
sealed-year row was read, pulled, or referenced by this session's own date
list (built from the reserved year only) or by the wiring change (which
only adds a new file path lookup, evaluated only for dates the new file
itself carries). Did not rewrite, append to, or re-decode any existing
committed file — the base dataset and every `v16_window`/`sealed_window`
family file (sessions 49/51/53/55's own commits) are untouched; only new
`session63_*` files were written. Did not build P (precipitation), `rh`, or
`plev` — D58 dropped/parked all three; only L, D, T, R were built, matching
D58's own final set exactly. Did not re-resolve, re-decide, or re-derive
any pinned window, constant, or transform — the elevation-correction
constants, the lapse-rate/dewpoint-depression/tendency/de-accumulation
formulas, and session 55's own 2-hour-window resolution were all reused
exactly as sessions 49/51/53/55 pinned them (the pull/decode functions by
direct import; the join arithmetic copied verbatim, documented in the new
script's own module docstring). Did not do any per-airport feature
selection or variation — identical handling at all five airports
throughout. Did not edit `scripts/session48_reserved_year.py` or its
reserved-year constants — read only. Did not modify `SPEC.md` or
`RESULTS.md`. Did not archive any DECISIONS entry this session — D52-D58
and F106 remain live (still load-bearing for session 64). Nothing was
committed.

---

## 2026-09-23 — Verification addendum to session 63 (not a new session): proves
the session-63 join/derive arithmetic copy is exact for L, D, T; finds one
known, already-documented, verdict-irrelevant rounding artifact for R.
No model fit. No reserved-year scoring. F107 is not edited.

**F108. Addendum to F107, per the session prompt's own framing. Two scripts,
both read-only, both model-free, both run and their real output saved to
`notes/`. Neither touches, fits, scores, or selects on the reserved year in
any modelling sense; Task 3 reads the reserved-year moisture file's own
already-committed columns to check one arithmetic identity, nothing more.**
Scripts: `scripts/session63_join_equivalence_check.py` (Tasks 1–3, new),
`scripts/session63_wiring_scratch_check.py` (Task 4's second script, new —
saves the model-free wiring check F107 described running but did not commit
as a script). Full real output: `notes/session63-join-equivalence-check-
output.txt`, `notes/session63-wiring-scratch-check-output.txt`.

**Method (Tasks 1/2).** For each family (L, D, T, R), `scripts/
session63_join_equivalence_check.py` imports session 63's own `join_L`/
`join_D`/`join_T`/`join_R` functions directly from `scripts/
session63_reserved_year_build.py` (not re-typed) and calls each one, feeding
it the raw decoded input columns already stored in that family's committed
v16_window file (sessions 49/51/53/55) — every row of each file was used
(6,127 rows per family; no sample was needed and no new pull was required,
so Task 2's fallback was never triggered). To avoid touching any committed
file, the join functions' own module-level output path
(`session63_reserved_year_build.PROCESSED`) was temporarily redirected to a
scratch temp directory for the duration of each call, then restored — the
real `data/processed/session63_reserved_window_with_*.csv` files (session
63's own committed output) were never opened for writing by this check.
Each family's own recomputed derived column was then compared row-by-row,
matched by (station, target_date), against that same v16_window file's
already-committed derived column.

**Result — L, D, T: EXACT, max abs diff 0.000000000 at every airport, every
intermediate and derived column, all 6,127 rows each.** `lapse_rate_t2_t850`
(L), `dewpoint_depression_t2m` (D) and `pressure_tendency_3h_hpa` (T) all
reproduce to the full precision Python's own `round()` carries, at EGLC,
LFPG, DSM, YSDU and RNO alike — including the intermediate columns
(`t2m_raw`, `t925`/`t850`/`t700`, `relative_humidity_2m`/`dew_point_2m`/
`specific_humidity_2m`, `pressure_msl_hpa`/`pressure_surface_hpa`/
`pressure_msl_lead_minus3_hpa`). This is the clean confirmation the session
prompt asked for: the arithmetic session 63 copied from these three
families' own `build_joined()` (sessions 49/51/53) is bit-for-bit identical
to what actually ran.

**Result — R: NOT exact. Max abs diff 0.002000000 at EGLC, LFPG and DSM;
0.000000000 at YSDU and RNO. This is a real, nonzero, correctly-reported
result — per the session prompt, this is reported and not fixed.** The
cause is understood and already on record, not new information: `join_R`'s
own derive step (`energy_2h = to_lead * dur_full - to_lead_m2 * dur_partial`)
is defined on the *pre-rounding* decoded values, but the only inputs
available without a new GRIB pull are the committed file's own
`dswrf_ave_to_lead_wm2`/`dswrf_ave_to_lead_minus2_wm2` columns — themselves
already rounded to 3 decimal places for transparency (F102). Feeding those
already-rounded values back through the identical formula reproduces a
double-rounding artifact, present only at the three lead-24, de-accumulating
airports (EGLC, LFPG, DSM) where a second message and a subtraction are
involved; YSDU and RNO (lead-26, single-message, no de-accumulation) are
exact because no second rounding step exists for them. **This is not a new
finding: DECISIONS F103 (session 56) ran the identical check — "`dswrf_2h_wm2
== (dswrf_ave_to_lead_wm2*6 - dswrf_ave_to_lead_minus2_wm2*4) / 2` ... Max
abs diff: EGLC 0.002000, LFPG 0.002000, DSM 0.002000 (all pure rounding
noise, well inside tolerance), YSDU 0.000000, RNO 0.000000 (exact)" — against
F103's own stated 0.01 W/m2 tolerance.** This check's own numbers match
F103's, at the same three airports, to the same six decimal places. Read
plainly: this is independent confirmation the R family's copied arithmetic
is faithful (an incorrect copy would have no particular reason to reproduce
F103's own exact figures), not evidence of a defect — the residual is a
property of comparing against an already-rounded intermediate column, not of
session 63's copied formula. Per the session prompt, no tolerance was
widened, no formula was changed, and no attempt was made to make this read
as zero — it is reported exactly as measured.

**Result — Task 3 (reserved-year moisture arithmetic): PASS, exact, on
every row.** `dewpoint_depression_t2m == round(t2m_raw - dew_point_2m, 3)`
holds with max abs diff 0.000000000 at all five airports, checked on all
1,825 rows of `data/processed/session63_reserved_window_with_moisture.csv`
(0 violations). This directly re-checks the one arithmetic identity the
reserved-year moisture file itself depends on, on the reserved year's own
real, committed data.

**Result — Task 4's second script.** `scripts/
session63_wiring_scratch_check.py` reproduces `scripts/
session62_reserved_confirm.py`'s own `load_family()` and
`build_complete_case()` logic without importing that module (which would
pull in lightgbm and trigger its dylib-path restart) — `CANDIDATE_FEATURES`
is imported from `session60_combine_design.py` (no heavy imports there), and
`RESERVED_FAMILY_FILES` is copied as a plain constant rather than imported.
Confirmed by direct real re-run of this script, matching F107's own
already-reported figures exactly: 0 reserved-year hits in the two original
(v16/sealed) files per family (unchanged); 1,825 rows added per family from
the four `session63_reserved_window_with_*.csv` files (365 x 5); exactly 365
complete-case reserved-year rows at every airport (previously 0, per D58
item 11); and 1,226/1,226/1,225/1,225/1,225 complete-case training-window
rows at EGLC/LFPG/DSM/YSDU/RNO — an exact match to D58 item 5's own
already-verified count. `lightgbm` is confirmed absent from `sys.modules`
throughout the run (printed and checked in the script's own output).

**What this addendum does and does not mean.** It proves the L, D, T
join/derive copy is exact and finds the R family's copy carries a
0.002 W/m2 double-rounding residual at three airports — already documented
by F103, verdict-irrelevant there and here (three orders of magnitude below
any skill margin the programme has ever measured, e.g. E4's own +1.4-1.9%,
F103). It does **not** touch, re-open, or change F107, D58, or any prior
verdict — F107 is not edited, per the session prompt. It does not run
`preflight()` or `run_confirm()` — neither is called anywhere in either
script. Session 64 remains the single authorized reserved-year confirmation
look (D51/D58), unaffected by this addendum either way.

**What this session did not do.** Did not fit any model (`lightgbm` is
never imported by either script — confirmed directly in the wiring script's
own output). Did not compute any MAE, skill, or CV. Did not read a reserved-
year row for any modelling purpose — Task 3's check is a pure arithmetic
identity on already-committed columns, no fit, no score. Did not edit
`scripts/session63_reserved_year_build.py`, `scripts/
session62_reserved_confirm.py`, or any of the sessions 49/51/53/55 scripts —
read/imported only. Did not modify, overwrite, or re-derive any committed
`data/processed/*.csv` file — the join-function re-runs wrote to a scratch
temp directory, never to a real path. Did not widen any tolerance or adjust
the R-family formula to make its diff read as zero. Did not edit F107. Did
not modify `SPEC.md`, `RESULTS.md`, or `STATUS.md`. Did not archive any
DECISIONS entry. Nothing was committed.

---

## 2026-09-23 — Session 64 finding: THE single authorized reserved-year
confirmation of the locked final feature set B+D,L,R,T (D51/D58). PASSES the
frozen bar at all five airports. The look is spent and will not be repeated.

**F109. Runs `scripts/session62_reserved_confirm.py --confirm`, once,
unchanged since the documented pre-look wiring (F107), on the reserved
2024-08-01..2025-07-31 confirmation year (D51). This is THE single
authorized look at the reserved year for the locked final feature set
(D58). It is spent and will not be repeated.** Full real output: `notes/
session-64-preflight-output.txt` (Step 1, the gate), `notes/
session-64-confirm-output.txt` (Step 2, the look).

**Step 0 — pre-look integrity checks, all PASS.** `git status --porcelain`
showed only the untracked session prompt itself (`docs/session-64.md`); no
`scripts/` or `data/processed/` changes. `git diff HEAD -- scripts/
session62_reserved_confirm.py` was empty. `git log -1 --format=%H -- scripts/
session62_reserved_confirm.py` = `a0dc42c3bebbcfd42f4323bdbdf362d1448be7e2`
(the session-63/F107 commit, its last edit — matches the "unchanged since
the documented pre-look wiring" framing exactly, not a fresh session-64
edit). SHA-256 of the script:
`9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4`. All four
`RESERVED_FAMILY_FILES` (`session63_reserved_window_with_{upper_air,
moisture,pressure,radiation}.csv`) confirmed present by path check.

**Step 1 — preflight() re-run: PASS, exact match to session 61 and session
62, at all five airports.** Ran with no arguments via the project's own
`.venv` interpreter (the frozen script's own libomp-restart shim, unchanged
since D24, fired correctly once the correct interpreter was used — a local
environment detail, not a script issue). The printed "RESERVED-YEAR
FEATURE-DATA GAP" block still reads as open in this output — this is
expected, not a regression: that block's own `hits_l/d/t/r` counters are
computed only from `load_family()`'s first loop (over the two original
session 49/51/53/55 committed files), which correctly still contain zero
reserved-year rows; the actual gap closure lives in `load_family()`'s
second loop (loading `RESERVED_FAMILY_FILES` when present, added by F107),
which this preflight path never exercises since it only builds the
training-window complete-case set. Confirmed working correctly in Step 2
below.

The 2023-24 machinery dry-run, compared side by side against session 61's
own `B+LDTR` grid row and session 62's own preflight output:

```
station  source        raw      persist   B        B+DLRT   skill_vs_B  n_train  n_test  no_prev
EGLC     session61    1.0148   2.0164    0.9470   0.8715    +7.98%      859      366     0
EGLC     session62    1.0148   2.0164    0.9470   0.8715    +7.98%      859      366     0
EGLC     session64    1.0148   2.0164    0.9470   0.8715    +7.98%      859      366     0
LFPG     session61    1.2234   2.3689    1.1606   1.1221    +3.31%      858      366     0
LFPG     session62    1.2234   2.3689    1.1606   1.1221    +3.31%      858      366     0
LFPG     session64    1.2234   2.3689    1.1606   1.1221    +3.31%      858      366     0
DSM      session61    2.0349   3.6992    1.5787   1.4883    +5.73%      859      366     0
DSM      session62    2.0349   3.6992    1.5787   1.4883    +5.73%      859      366     0
DSM      session64    2.0349   3.6992    1.5787   1.4883    +5.73%      859      366     0
YSDU     session61    1.3283   2.4417    1.1264   1.0949    +2.80%      850      363     3
YSDU     session62    1.3283   2.4417    1.1264   1.0949    +2.80%      850      363     3
YSDU     session64    1.3283   2.4417    1.1264   1.0949    +2.80%      850      363     3
RNO      session61    1.4541   2.5962    1.2972   1.1458    +11.67%     857      365     1
RNO      session62    1.4541   2.5962    1.2972   1.1458    +11.67%     857      365     1
RNO      session64    1.4541   2.5962    1.2972   1.1458    +11.67%     857      365     1
```

**Every figure matches to the fourth decimal place, at all five airports,
against both sources — no divergence anywhere.** `n_checked` (training-
window complete-case rows) = 6,127 with `max_abs_diff = 0.000000000` on all
four final-set feature columns (identical to session 62's own check).
`no_prev` values above show the dry-run fold used only training-window
dates (2021-03-24..2024-07-31); a direct read of `merged_train_all` in the
dry-run loop confirms no date outside that span, and therefore no
reserved-year date, ever entered it. **Step 1's pass criterion is met.
Proceeding to Step 2.**

**A side effect of running `preflight()`, reported rather than hidden.**
The frozen script's own `OUT_PREFLIGHT` constant hardcodes `notes/
session-62-preflight-output.txt` regardless of which session calls it
(unchanged since session 62 wrote it; not something this session could
edit without touching the frozen script). Re-running `preflight()`
therefore overwrote that file. Before the overwrite was reverted (below),
`git diff` on it showed exactly two kinds of change, nothing else: the
`run at` timestamp, and every `rows loaded`/`of N total` count rising from
7,952 to 9,777 (+1,825 = 5 airports x 365 reserved days) — direct,
independent confirmation that `load_family()`'s F107 wiring addition
(loading `RESERVED_FAMILY_FILES` when present) is active even on this
training-window-only code path, not just in `run_confirm()`. The "Machinery
dry-run" section — the figures compared against session 61 above — was
byte-for-byte unchanged in that diff, confirming the comparison above was
made against session 62's true original numbers, not an artifact of the
overwrite. **The owner restored `notes/session-62-preflight-output.txt` to its
committed original from git**, so that file stands exactly as session 62
left it; this session's own preflight re-run output lives at `notes/
session-64-preflight-output.txt` instead, untouched by the restoration.

**Step 2 — the look. Ran once, `--confirm`, no crash, no guard trip.**
Real output, verbatim:

```
EGLC: n_train=1225 n_test=364 no_obs_dropped=1 no_prev=1 raw=1.2362 persist=2.2259 B=1.0861 B+DLRT=1.0008 vs_raw=PASS vs_persist=PASS
LFPG: n_train=1224 n_test=365 no_obs_dropped=0 no_prev=0 raw=1.4091 persist=2.5233 B=1.3285 B+DLRT=1.2369 vs_raw=PASS vs_persist=PASS
DSM: n_train=1225 n_test=365 no_obs_dropped=0 no_prev=0 raw=1.7043 persist=4.1081 B=1.4402 B+DLRT=1.4123 vs_raw=PASS vs_persist=PASS
YSDU: n_train=1213 n_test=360 no_obs_dropped=5 no_prev=5 raw=1.4897 persist=2.5775 B=1.3030 B+DLRT=1.2643 vs_raw=PASS vs_persist=PASS
RNO: n_train=1222 n_test=365 no_obs_dropped=0 no_prev=0 raw=1.6135 persist=2.7563 B=1.4272 B+DLRT=1.2742 vs_raw=PASS vs_persist=PASS

BAR VERDICT (D58 pre-registered expectation 7): ALL FIVE AIRPORTS PASS
SECONDARY READ: B+D,L,R,T airport-averaged MAE 1.2377 vs B 1.3170  (beats B)
```

**Per-airport table, reserved year 2024-08-01..2025-07-31 (recomputed
margins, all from the numbers above, arithmetic shown so it can be
checked):**

```
station  raw_MAE  persist_MAE  B_MAE   final_MAE  n_test  persist_n  vs_raw    vs_persist  vs_B
EGLC     1.2362   2.2259       1.0861  1.0008     364     363        +19.04%   +55.04%     +7.85%
LFPG     1.4091   2.5233       1.3285  1.2369     365     365        +12.22%   +50.98%     +6.89%
DSM      1.7043   4.1081       1.4402  1.4123     365     365        +17.13%   +65.62%     +1.94%
YSDU     1.4897   2.5775       1.3030  1.2643     360     355        +15.13%   +50.95%     +2.97%
RNO      1.6135   2.7563       1.4272  1.2742     365     365        +21.03%   +53.77%     +10.72%
```

**Scored row count per airport, per rung, out of the 365 complete-case
feature rows F107 built for every airport:**

```
station  n_raw  n_B   n_final  n_persist  no_obs_dropped  no_prev
EGLC     364    364   364      363        1               1
LFPG     365    365   365      365        0               0
DSM      365    365   365      365        0               0
YSDU     360    360   360      355        5               5
RNO      365    365   365      365        0               0
```

raw, B, and B+D,L,R,T (`n_raw`/`n_B`/`n_final`) are all scored on the
identical set of rows — the 365 complete-case feature rows minus
`no_obs_dropped`, the SPEC 4.5/D14 pairing drop (a day dropped because no
routine report fell within 15 minutes of the target hour). Persistence is
scored on a further subset, `n_persist = n_final - no_prev` (SPEC 2.1d: a
day dropped from persistence alone because its previous calendar day has
no usable observation); `no_prev` is counted only among the already-paired
`n_final` rows and is not necessarily the same calendar day as an
`no_obs_dropped` day. **Two airports score below 365, both explained
exactly by these two drops and nothing else:** EGLC loses 1 row to
`no_obs_dropped` (364/365) and a further 1 row for persistence only
(363/364); YSDU loses 5 rows to `no_obs_dropped` (360/365) and a further 5
rows for persistence only (355/360). LFPG, DSM and RNO have zero drops at
every rung. **The persistence margins reported above (vs_persist) are
therefore computed on the persistence subset (`n_persist`), not on
`n_final`** — the same day-set convention F93 already documented for the
sealed test, reported plainly here rather than hidden: EGLC's and YSDU's
persistence margins (+55.04%, +50.95%) are nowhere close to being affected
by scoring on 1 or 5 fewer days. This is a routine observation-pairing
loss, not a feature-completeness gap — F107 already confirmed 365/365/365
complete-case feature rows at every airport before any observation was
joined (e.g. F94's own sealed-year test showed the same pattern: EGLC/LFPG
364, YSDU 356).

**2. THE BAR (D58 item 7): PASS. B+D,L,R,T beats both raw GFS and
persistence at all five airports, with no exception and no close call.**
The narrowest raw-GFS margin (LFPG, +12.22%) and the narrowest persistence
margin (YSDU, +50.95%) are both comfortably positive. This exactly matches
D58's own pre-registered expectation 7, with no divergence.

**3. Secondary read (D58 item 7): B+D,L,R,T beats plain B on
airport-averaged MAE — CONFIRMED.** Airport-averaged final-set MAE 1.2377
vs airport-averaged B MAE 1.3170, a +6.02% skill margin. Per-airport B vs
B+D,L,R,T (description only, no per-airport claim was pre-registered — DSM
variation was explicitly expected, D58 item 7):

```
station  B_MAE   final_MAE  skill_vs_B
EGLC     1.0861  1.0008     +7.85%
LFPG     1.3285  1.2369     +6.89%
DSM      1.4402  1.4123     +1.94%
YSDU     1.3030  1.2643     +2.97%
RNO      1.4272  1.2742     +10.72%
```

**D58 item 7 pre-registered only that per-airport variation was expected,
especially at DSM — no ranking among airports was pre-registered, and none
is claimed here.** DSM's small margin (+1.94%) is consistent with that
expectation(F96's own cloud/wind reading there, and F106's own
DSM-diagnostic +5.7%-vs-+6.1% reading for this same feature set). **RNO's
own margin (+10.72%) was not pre-registered and is descriptive only.**

**4. Reported as measured, no re-framing.** The bar verdict is a clean
PASS at all five airports; there is no worse number to soften or better
number to lead with instead — the result above is the whole of it.

**Honesty caveat (D58 item 8), stated exactly as required.** The reserved
year was seen once before, descriptively, for baseline B alone, in F96's
multi-year rolling-origin backtest — that is on record and is not
overclaimed as unseen. But the feature-selection programme itself (which
features to add — E1–E5, F98–F105, and the combine sweep, F106) never
touched the reserved year at any point; every one of those readings ran
only on the three non-reserved `EXPERIMENT_FOLDS` (D51). **This session is
therefore the first look, ever, at the selected set B+D,L,R,T specifically,
on the reserved year** — genuinely first for the recipe being confirmed,
even though F96 already computed something for B alone on the same
calendar dates. Neither overclaiming blindness the programme does not have,
nor understating that this is the first look at the chosen recipe.

**This was THE single authorized look at the reserved year for this
feature set (D51). It is spent and will not be repeated, for any reason —
not a re-run, not a re-tune, not an alternative variant.** No guard tripped
before or after a result was produced; Step 2 completed cleanly on its one
and only invocation.

**What this session did not do, on purpose.** Did not edit
`scripts/session62_reserved_confirm.py` in any way (`git diff HEAD` empty
before and after running it). Did not run `--confirm` more than once. Did
not touch the sealed 2025-08-01..2026-07-31 year (F94) — no code path in
the frozen script's `run_confirm()` references it, and no sealed-year file
was opened. Did not tune, select, or vary anything on the reserved year —
only what `run_confirm()` itself computes is reported. Did not modify
`SPEC.md` or `RESULTS.md`. Did not archive any DECISIONS entry — D52–D58
and F106–F108 stay live per the session prompt's own instruction, pending
the owner's review of this finding. Nothing was committed.

---

