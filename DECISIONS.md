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

[F88, session 35's GFS GRIB source feasibility probe (verdict: GO-COSTLY) —
archived verbatim to DECISIONS-archive.md this session (session 38), because
its own question — whether a deeper, credential-free GFS GRIB archive exists
and is worth building — is now settled: sessions 36–38 built the pipeline,
fixed its one gap (RNO elevation, F89/F90), and used it for the full-window
richer-features CV (F91, below), superseding F88's cost-only verdict with a
completed result. Full text preserved there and in git.]

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

**D47. Raw-data policy for large re-fetchable sources: manifest, not bytes.** D15 committed raw pulls when raw meant small Open-Meteo JSON. The GRIB pull is ~20 GB, which cannot live in git (binary bloat; GitHub file and repo size limits). For large, re-fetchable public archives such as GFS GRIB, D15s immutable-provenance intent is served by committing the provenance manifest (exact queries, URLs, byte-ranges, and the drop log) plus the processed dataset, and gitignoring the raw bytes -- which are reproducible from the manifest. D15 stands unchanged for small API pulls. The ~20 GB local GRIB cache is disposable and re-fetchable.

---

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
