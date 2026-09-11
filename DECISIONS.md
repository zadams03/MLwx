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

## 2026-08-19 — Q30 status update (not closed, not re-raised — the fork it named is now fully live)

Q30 was raised after session 18 with a parenthetical: the branch it named
depended on Dubbo finishing its own five steps (verify, pull/map, join and
rehearse, lock, test once). Session 24 finished the fifth and last of those
(F64). **Q30 itself is unchanged and still open** — this is not a new
question and does not close it — but the fork it describes (more airports; a
second test year, the remaining half of the F30/F48 caveat; or stage 3,
pooling) is no longer waiting on anything. Nothing was decided here; this
note only removes the "when Dubbo finishes" qualifier, since Dubbo has now
finished. The owner's choice is unchanged from how Q30 already described it.

---

## 2026-08-20 — Open question raised by session 27 (not acted on)

**Q32. Should Reno's rehearsal loss against raw GFS (-0.4%, F80) change
anything about whether or how the recipe is locked and tested at Reno?** The
session-27 prompt's own instruction was to proceed to lock/test regardless
and judge the bar as-is if the rehearsal showed the simple features
struggling, and that instruction was followed — no lock was attempted this
session, and nothing about the method was varied because of the result
(SPEC 2.4, D21.11). But every prior airport's rehearsal beat raw GFS by some
margin, narrow or wide (EGLC 6.0%, CDG 3.4–3.5%, DSM 16.1%, Dubbo 8.2%); Reno
is the first to come back negative rather than merely narrow. The owner has
not yet been asked, in so many words, whether that changes their intentions
for this specific airport (proceed to lock/test unmodified, as the session
prompt defaults to; or pause before locking to weigh richer features first)
or for how future terrain-hard airports are approached generally. Nothing
was decided this session; this is recorded for the owner, the same shape
Q31 was left in after session 26.

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

## 2026-09-11 — Session 34b decision: archive move executed, archive-as-you-go adopted

**D46. The session-34a manifest was executed mechanically, the borderline call
was resolved to MOVE, and archiving settled entries to `DECISIONS-archive.md`
is now a routine part of every session's end-of-session roundup, not a
one-time exception.**

**What moved.** Session 34a's manifest (`notes/session-34-archive-manifest.md`)
classified 237 header-matched spans of `DECISIONS.md` as MOVE, 12 as KEEP-LIVE,
and left one span BORDERLINE for the owner: the session-21 restructure record
(lines 5624–5730 of the pre-move file), which documented the project's first
archive move. The owner resolved the borderline to MOVE. So this session moved
**238 spans, 8,698 lines**, in six contiguous cuts (the borderline's range sits
directly between two already-adjacent MOVE cuts, so it merged into one:
39–233, 250–255, 276–5009, 5046–6934, 6949–8100, 8121–8842 of the pre-move
file). The move was mechanical: a single `awk` pass partitioned every line of
`DECISIONS.md` by line number into keep-lines and move-lines in one pass (to
avoid the shifting-line-number bug top-down deletion would cause), the
move-lines were appended verbatim to `DECISIONS-archive.md` under one new
dated section, and `DECISIONS.md` was replaced with the keep-lines. No entry
was retyped, edited, reworded, or renumbered.

**What stayed live.** D17 and F7 (kept live rather than moved, correcting the
session-34a session prompt's own "expected MOVE" framing, because the live
richer-features finding F85 depends on their specific wording, not just their
headline); F85–F87 (the live richer-features phase in full); the three
Q30/Q32-bearing open-question blocks; and the parked items P1–P3. `DECISIONS.md`
falls from 9,471 lines to 773 lines before this entry (roughly a 12-fold cut),
plus this entry itself.

**The archive criterion, restated for future sessions (it does not change,
only now applies routinely instead of once).** An entry is a MOVE candidate
once its conclusion is settled — codified in `SPEC.md`, superseded by a later
finding at the same airport, or otherwise not needed to understand any
currently open question — and is **not** a MOVE candidate while any live open
question, or `STATUS.md`'s own "Next" section, still cites its specific
wording rather than just its headline. When in doubt, keep it live; a wrong
KEEP-LIVE costs a little re-reading, a wrong MOVE risks losing context a later
session needs and did not know to ask for by number.

**Why the archive exists, and how citations into it work — re-homed here,
since session 21's record (now itself moved) used to carry this
explanation.** `DECISIONS.md` is this project's append-only memory of *why*;
reading it in full every session is what lets a session understand a decision
without re-deriving it. But an append-only log that never shrinks eventually
costs more to read than it returns. `DECISIONS-archive.md` exists to hold
settled material **verbatim** — nothing is ever deleted, only relocated — so
that the routine per-session read (`CLAUDE.md` + `SPEC.md` + `STATUS.md` +
live `DECISIONS.md`) stays a manageable size while the full record stays
available. A `(Dxx)`/`(Fxx)` citation anywhere in `SPEC.md`, `RESULTS.md`,
`STATUS.md`, `CLAUDE.md`, or a still-live `DECISIONS.md` entry always resolves
— by number — to an entry in exactly one of the two files; the number never
changes when an entry moves, so no citation is ever broken by a move, and a
reader who hits a `(Dxx)`/`(Fxx)` they don't recognise as still-live should
check `DECISIONS-archive.md` next. `DECISIONS-archive.md` is deliberately
**not** part of the routine per-session read (`CLAUDE.md`); open it only when
a session needs an archived entry's exact wording, not just its headline —
most needs are already served by the headline already carried forward into
`SPEC.md` or `RESULTS.md`.

**The workflow change (supersedes session 21's "one-time exception"
framing).** Session 21 authorised the first move as a one-time exception to
append-only, and closed with "nothing is ever moved again as a matter of
routine." That framing is now superseded: from this session on, moving
settled entries to `DECISIONS-archive.md` is a **routine** part of the
end-of-session roundup (`CLAUDE.md`'s "End of every session" list), applying
the same criterion above each time, rather than a rare authorised exception.
The append-only, verbatim, nothing-deleted guarantees are unchanged — only
*how often* a move happens changes, not *what* a move is allowed to do.
`DECISIONS-archive.md`'s own header note (amended this session, see below)
carries this same correction, so a reader of either file gets the same
current picture.

**Documentation changes made this session (each reported to the owner in
full, before/after, in the session report):**
- `DECISIONS-archive.md`'s header note amended to supersede the "one-time,
  never again" framing and to carry the "what the archive is / how citations
  work" explanation permanently, since session 21's record (which used to
  carry it) has now itself moved into the archive as content.
- `CLAUDE.md` amended: the routine read list now states plainly that the
  per-session read is CLAUDE.md + SPEC.md + STATUS.md + live DECISIONS.md,
  with `DECISIONS-archive.md` and `RESULTS.md` both read on demand only; the
  "End of every session" list gained a new archive step.
- `RESULTS.md` §2's wording on why the five airports' target hours differ was
  corrected: it previously said the difference was because "local noon is a
  different UTC hour at each longitude" for all five airports, which is
  wrong for EGLC/LFPG specifically — those two share 12:00 UTC **by
  deliberate design** (SPEC 4.1, DECISIONS D26), the clean "only the location
  changed" comparison, not because their longitudes happen to coincide with a
  shared local noon by accident of the general rule. DSM, Dubbo and Reno each
  take their own local-noon UTC hour (D33, D37, D42). No figure or any other
  section of `RESULTS.md` was touched.

**What did not happen this session.** No code, script, model, data file, or
figure was touched. No entry's content was edited, reworded, or summarised —
only relocated, verbatim, by mechanical line-range extraction. No entry was
renumbered. `SPEC.md` was not modified (SPEC §1's Reno line already reads
"failed"). Nothing was committed — the owner reviews and commits this and
every prior change by hand.

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
