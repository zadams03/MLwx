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

**D47. Raw-data policy for large re-fetchable sources: manifest, not bytes.** D15 committed raw pulls when raw meant small Open-Meteo JSON. The GRIB pull is ~20 GB, which cannot live in git (binary bloat; GitHub file and repo size limits). For large, re-fetchable public archives such as GFS GRIB, D15s immutable-provenance intent is served by committing the provenance manifest (exact queries, URLs, byte-ranges, and the drop log) plus the processed dataset, and gitignoring the raw bytes -- which are reproducible from the manifest. D15 stands unchanged for small API pulls. The ~20 GB local GRIB cache is disposable and re-fetchable.

---

## 2026-09-18 — Session 46 finding: multi-year rolling-origin generalisation
backtest of the existing frozen recipes (24h lead, GRIB source). A
descriptive profile, not a new verdict.

**F96. This is a descriptive multi-year robustness profile of the EXISTING
FROZEN 3-feature and 5-feature GRIB recipes (SPEC §7, D21.4/D48.6), refit
per fold on each fold's own training window and scored on the following
year, walking the cutoff forward one year at a time. It is not a sealed
test and decides no pass/fail — F94 and F16–F82 stand exactly as reported,
untouched.** Script: `scripts/session46_backtest.py` (new). Full real
output: `notes/session-46-backtest-output.txt`. Tables:
`data/processed/session46_backtest_profile.csv` (150 rows: 5 airports x 10
feature-set/fold combinations x 3 rungs) and
`data/processed/session46_fold_table.csv` (50 rows).

**The integrity boundary, honoured throughout.** Reusing the sealed year
here is legitimate only because nothing is tuned, added, or selected — both
recipes are refit-only, with identical features and identical LightGBM
settings (D21.4) in every fold. The output is a description, used to build
a benchmark for future feature work, never to pick a winner. Feature
*selection* later still needs its own fresh, untouched test year — this
backtest does not substitute for that.

**Mid-session correction to the session prompt itself (docs/session-46.md),
made before Task 1 was built, owner-confirmed.** The session prompt's own
"Reference — the data spans" section stated the 5-feature set is
unavailable before 2024-01-19, citing F85, and restricted the 5-feature
folds to that floor. That citation does not hold for the GRIB source this
session uses: F85 (session 31) found the gap in **Open-Meteo's** own
cloud-cover/wind-speed coverage, not GRIB's — the entire point of the GRIB
build (sessions 36–38, F90/F91, archived; SPEC §7.2) was pulling cloud
cover and wind speed across the full v16 window specifically because
Open-Meteo's window was too short. Checked directly, before any fold was
built: `data/processed/grib_features_v16_window.csv` carries real,
non-null `cloud_cover_grib_pct` and `wind_speed_grib_kmh` values back to
2021-03-24 — zero blank fields across all 7,952 (training) + 1,825
(sealed) rows in the two GRIB feature files. Flagged to the owner mid-session
rather than resolved unilaterally (CLAUDE.md: stop and flag a session-prompt/
SPEC disagreement). **The owner confirmed widening the 5-feature folds to
the same four training starts as 3-feature (2021-03-24 onward), subject to
two conditions this session's script enforces in code: (1) the non-null
check above, done before any fold uses the data — `load_grib_features()`
raises on any blank cloud/wind/temperature field; (2) never using data
before 2021-03-24 regardless — that boundary is the v16 model-version floor
(D48.7), unrelated to data availability, and stays fixed.** The two
original thin 2024-01-19-start 5-feature folds from the session prompt were
KEPT alongside the widened ones, not replaced, so the "does more training
data help" read has a direct within-recipe comparison and the session
prompt's own explicit fold list is still fully present in the output.

**Task 1 — the fold design, as actually run.**

3-feature folds (train → test), full window throughout:
```
fold      train start   train end     train days   test
2022-23   2021-03-24    2022-07-31    495 (THIN)   2022-08-01..2023-07-31
2023-24   2021-03-24    2023-07-31    860          2023-08-01..2024-07-31
2024-25   2021-03-24    2024-07-31    1226         2024-08-01..2025-07-31
2025-26   2021-03-24    2025-07-31    1591         2025-08-01..2026-07-31
```

5-feature folds (widened + the two original thin folds kept for comparison):
```
fold           train start   train end     train days   test
2022-23        2021-03-24    2022-07-31    495 (THIN)   2022-08-01..2023-07-31
2023-24        2021-03-24    2023-07-31    860          2023-08-01..2024-07-31
2024-25        2021-03-24    2024-07-31    1226         2024-08-01..2025-07-31
2025-26        2021-03-24    2025-07-31    1591         2025-08-01..2026-07-31
2024-25-thin   2024-01-19    2024-07-31    195 (THIN)   2024-08-01..2025-07-31
2025-26-thin   2024-01-19    2025-07-31    560 (THIN)   2025-08-01..2026-07-31
```
The 2022-23 fold (~1.35 years of training) and both `-thin` folds are
explicitly flagged THIN in the output — a weaker read, not an equal one,
per the session prompt's own instruction. `2024-25-thin` (~6 months
training) is the same starved-window shape session 32's scout saw (F86,
archived).

**Task 2/3 — the profile (skill vs raw GFS (GRIB), 3-feature and 5-feature
full-window folds; all four years; +/- = beats/loses to raw GFS):**

```
station   2022-23        2023-24        2024-25        2025-26
          3f     5f       3f     5f      3f     5f       3f     5f
EGLC     -0.6%  +4.8%    +6.1%  +6.7%   +6.3%  +12.1%   +17.3% +20.2%
LFPG     +5.7%  +8.4%    +2.3%  +5.1%   +2.8%  +5.7%    +14.8% +16.4%
DSM     +16.4% +17.6%   +25.2% +22.4%  +15.9% +15.5%    +2.3%  +5.6%
YSDU     -4.6%  -5.3%    +7.9% +15.2%  +11.5% +12.5%    +2.5%  +10.5%
RNO      +7.4% +10.2%    +5.7% +10.8%   +2.0% +11.5%    +3.7%  +11.0%
```

3-feature beats raw GFS (GRIB) at **18 of 20** airport-years (both losses —
EGLC and YSDU, both narrow — fall in the thinnest fold, 2022-23). 5-feature
beats raw GFS (GRIB) at **19 of 20** airport-years (the one loss is also
YSDU's 2022-23). **5-feature beats 3-feature at 17 of the 20 full-window
airport-years, not all 20** — the three exceptions are DSM 2023-24
(5-feature MAE 1.579 vs 3-feature 1.522, 3-feature better), DSM 2024-25
(1.440 vs 1.433, 3-feature better, a very narrow gap) and the thin YSDU
2022-23 fold (1.199 vs 1.191, 3-feature better). The two `-thin` 5-feature
folds (2024-01-19 start, kept from the original prompt) fare markedly
worse still: `2024-25-thin` beats raw GFS at only 2 of 5 airports (LFPG
-22.2%, DSM -17.4%, RNO -4.8%), closely reproducing session 32's scout
finding (F86) that a starved training window, not the extra features, was
the dominant effect; `2025-26-thin` recovers to 4 of 5 (only DSM -1.3%).

**Reading the 5-vs-3 exceptions honestly, by airport, across the four
full-window years:** cloud cover and wind speed reliably help at EGLC
(4/4), LFPG (4/4) and RNO (4/4) — 5-feature beats 3-feature every year at
each of those three. They help variably at YSDU (3/4, the one exception
in the thinnest fold). **At DSM they are marginal to slightly negative**
— 5-feature loses to 3-feature in 2 of 4 years, and even where it wins
(2022-23, 2025-26) the margin is the smallest of any airport. DSM is the
one airport in this project whose target hour sits at dawn-adjacent local
standard noon behind a large, well-behaved seasonal cycle (SPEC 4.1); the
honest reading is that three features (temperature, season_sin,
season_cos) already capture most of DSM's own learnable bias, leaving
little room for cloud cover and wind speed to add anything — unlike
EGLC/LFPG/RNO, where the extra features consistently earn their keep.

**Consistency check against F94 — exact reproduction, at every airport.**
The `2025-26` fold, for both feature sets, uses exactly D48's own training
window (2021-03-24..2025-07-31) and sealed test window
(2025-08-01..2026-07-31) — the identical recipe on the identical data.
Every row count matches F94 exactly (EGLC/LFPG 364, DSM/RNO 365, YSDU 356)
and every MAE (raw GFS, persistence, 3-feature, 5-feature, all five
airports) matches to within 0.0005 degC — a pure independent-recompute
rounding difference, not a divergence. This is strong evidence the backtest
pipeline (join, features, model settings) is a correct reproduction of the
frozen recipe, not a re-implementation that happens to look similar.

**Task 4 — the honest read.**

*Does the 3-feature model consistently beat raw GFS across years, or was
2025-26 flattering?* The answer differs by airport, and is worth stating
plainly rather than as one number. **EGLC and LFPG's sealed-year margins
are clearly the largest of their own four years** (EGLC: -0.6/+6.1/+6.3/
**+17.3%**; LFPG: +5.7/+2.3/+2.8/**+14.8%**) — real evidence supporting the
concern F48 already named, that the shared 2025-26 test year may be
somewhat flattering at these two airports specifically. **DSM shows the
opposite pattern** — its sealed-year margin (+2.3%) is clearly its
*weakest* of the four years, well below 2022-23/2023-24/2024-25's
15–25% margins — so "was 2025-26 a flattering year" does not have one
project-wide answer; it depends on the airport. YSDU and RNO's sealed-year
margins sit within their own historical range, neither the best nor the
worst of their four years.

*Year-to-year variance per airport (raw GFS MAE, an indication of how much
the weather itself varied year to year, independent of any model):* DSM
varies most (1.704–2.094 degC across the four years); RNO is the most
stable (1.454–1.613); EGLC, LFPG and YSDU fall in between. This is
context for reading the skill margins above, not a finding on its own.

*Is any airport's skill fragile — wins some years, loses others?* Only in
the thinnest fold. Every airport passes at 3 and 4 of the full-window
years; the only two losses in the whole 20-airport-year full-window grid
are EGLC and YSDU, both in the 2022-23 fold (the shortest training
window), both narrow (-0.6%/-4.6% for 3-feature, -5.3% for YSDU's
5-feature — EGLC's 5-feature actually holds at 2022-23, +4.8%). This reads
as a thin-training-window effect, not a fragile-airport trait: DSM, LFPG
and RNO win at every one of their four full-window years under both
feature sets, and RNO in particular is now the most consistent airport in
the whole profile.

**RNO's richer-features rescue specifically — the headline read of this
whole profile.** RNO's 5-feature skill vs raw GFS is remarkably stable
across all four independent years: +10.2%, +10.8%, +11.5%, +11.0% — a
tighter band than any other airport shows. F94's single-sealed-year RNO
pass (+11.0%) was always going to invite the question "was that one lucky
year." This profile answers it: RNO's richer-features win reproduces
closely across three prior years the sealed test never touched, under a
strictly time-ordered refit each time. This is the strongest evidence yet
that Reno's richer-features result (F94, reversing the existing recipe's
own sealed-test failure, F82) is a real, repeatable effect rather than a
single-year artifact — though it remains, and stays, a separate finding
about a separate recipe from F82, not an erasure of it (D48.13).

*Is the 5-feature multi-year read still limited, as the original session
prompt expected?* Less than the prompt assumed, now that the GRIB source's
own cloud/wind coverage is confirmed back to 2021-03-24 (this session's own
correction, above) — the widened 5-feature folds now cover the same four
independent years as 3-feature, not just two. What remains genuinely
limited: all four years are drawn from expanding, overlapping training
windows over one continuous ~5.4-year weather record, not four fully
independent samples of climate, and the whole profile — like every result
in this project so far — is GRIB-source-only; it says nothing new about
the existing 3-feature/Open-Meteo recipe's own robustness (F16/F30/F47/
F64/F82), which used a different forecast source entirely and is not
re-examined here.

**One-line synthesis (report only, per the session prompt's own
instruction — not a decision).** Both frozen GRIB recipes beat raw GFS
in the large majority of the 20 airport-years tested (18/20 3-feature,
19/20 5-feature), with the only losses confined to the thinnest training
window; the 5-feature model's edge over 3-feature holds at 17 of the 20
full-window airport-years, reliably at EGLC/LFPG/RNO and variably at YSDU,
but is marginal-to-slightly-negative at DSM, where three features already
capture most of the learnable bias — a materially more robust and more
nuanced picture than a single sealed year could show on its own, and RNO's
richer-features rescue in particular now reads as a repeatable, not a
one-off, effect. This is the benchmark future feature-selection work will
be measured against, not a verdict on any of it.

**What this session did not do, on purpose.** Did not pull any new data —
reused `grib_features_v16_window.csv` and `grib_features_sealed_window.csv`
(sessions 37/40) and the existing IEM chunk files, all read-only. Did not
run +48h lead — 24h only. Did not tune, select, or add any feature or
hyperparameter — both recipes are refit-only, identical settings (D21.4) in
every fold. Did not test any fold on a date it trained on — asserted in
code, per fold, per airport (`train_end < test_start`, plus a per-row date
range assertion). Did not treat this as a sealed test or a new pass/fail —
no verdict field is computed or printed anywhere in the script or its
output. Did not re-open, re-litigate, or restate F94 or F16–F82 as changed
— both stand exactly as reported; the consistency check above confirms
reproduction, not revision. Did not modify `SPEC.md` or `RESULTS.md`.
Nothing was committed.

---

## 2026-09-19 — Session 48 decision: reserve 2024-25 as the feature-selection
programme's confirmation year, enforced in code

**D51. The 2024-25 year (2024-08-01 to 2025-07-31) is reserved as the
untouchable confirmation year for the upcoming feature-selection
programme.** No feature experiment — no backtest run, no model fit, no
result read — may use it, for training or for evaluation, until a single
pre-chosen final feature set is confirmed on it once, at the very end. This
is setup only: no feature experiment, feature model, or 2024-25 result was
run or computed this session (SPEC 2.4's frozen-before-running discipline,
applied here to a confirmation year instead of a bar).

**Why, and why now (cites F96).** F96's own rolling-origin backtest already
used every year 2022–2026 descriptively — as training data, test data, or
both — for the *existing* frozen recipes. That reuse was legitimate only
because nothing was tuned or selected (F96's own "integrity boundary" note).
A feature-selection programme is different in kind: it chooses between
feature sets on the basis of held-out performance, which is itself a form of
fitting to data. Left unreserved, any "winning" feature set chosen from
F96's own years would be chosen in the light of data already seen — the same
selection-bias problem the sealed test (SPEC 5.3, D22) exists to prevent for
a final recipe. F96 having used all the years is exactly why a fresh year
had to be carved out now, before any feature experiment exists to
contaminate it.

**Distinct from, and does not disturb, the 2025-26 sealed year.** F94 (the
5-feature GRIB recipe's one authorised look at 2025-08-01..2026-07-31)
stands exactly as reported. This reservation is a separate held-out year for
a separate purpose — confirming a *selected* feature set, not re-judging any
already-locked recipe — and no minimal-method verdict (F16/F30/F47/F64/F82)
is touched either.

**The confirmation rule.** Feature experiments run on the non-reserved years
only. The winning feature set is chosen there. Then the single, pre-committed
final model is evaluated on 2024-25 exactly once, and that result stands as
reported — the same one-look discipline as every other frozen-bar test in
this project (D21, D31, D35, D39, D44, D48.13).

**Enforced in code, not left to discipline alone.** `scripts/
session48_reserved_year.py` (new) defines the reservation
(`RESERVED_YEAR_START`/`RESERVED_YEAR_END` = 2024-08-01/2025-07-31) and a
guard, `assert_reserved_year_excluded()`, that raises `ValueError` if a
proposed fold's training window *or* test window overlaps any part of the
reserved year — the same "stop rather than allow" pattern as the sealed-test
self-guards (D48.8/F93). It also defines `EXPERIMENT_FOLDS`, the fold list a
future feature-experiment session should build from: F96's own rolling-origin
fold list, minus the fold that tested 2024-25, with the fold that tests
2025-26 truncated so its training window stops at 2024-07-31 — before the
reserved year starts — so the reserved year never enters an experiment's
training pool either, not just its test set.

```
label      train                    test
2022-23    2021-03-24..2022-07-31   2022-08-01..2023-07-31
2023-24    2021-03-24..2023-07-31   2023-08-01..2024-07-31
2025-26    2021-03-24..2024-07-31   2025-08-01..2026-07-31   (train truncated; see below)
```

**The guard was verified by construction only — no experiment run, no
2024-25 result computed.** Running `scripts/session48_reserved_year.py`
(real output: `notes/session-48-guard-check-output.txt`) confirms: all three
`EXPERIMENT_FOLDS` entries pass the guard (no raise); three deliberately
reserved-year-touching folds — one mirroring F96's own original "2025-26"
fold (train crossing straight through the reserved year), one testing the
reserved year directly, one training into it — all raise `ValueError` as
expected, with no model fit and no data loaded anywhere in the script (it is
pure date-range arithmetic).

**The honest cost, stated plainly.** Truncating the "2025-26" experiment
fold's training window to stop before the reserved year costs it 365 days
(1.00 years) of training data versus F96's own equivalent fold (1,591 days
down to 1,226 days) — the price of making the later confirmation genuinely
out-of-sample, not merely unused-for-selection. The feature-selection
programme now has three folds (2022-23, 2023-24, 2025-26-truncated) instead
of F96's four, and the "2022-23" fold remains the thinnest (495 days,
~1.36 years) exactly as it was in F96 — unaffected by the reservation, since
it never reached 2024-25 in the first place.

**What this session did not do, on purpose.** Did not run any feature
experiment, fit any feature model, or compute any result on 2024-25 or any
other year — the guard-verification script above uses only date arithmetic,
no CSV, no model fit. Did not pull any new data. Did not touch the 2025-26
sealed year or restate any existing verdict. Did not choose or lock a
feature-experiment ordering (E1/upper-air or otherwise) — that is a later,
separate session's job, using the F97 availability map. Did not modify
`SPEC.md` or `RESULTS.md`. Nothing was committed. Script: `scripts/
session48_reserved_year.py` (new). Full real output: `notes/
session-48-guard-check-output.txt`.

---

## 2026-09-23 — Session 65 decision: the owner's verdict on F109, the third
method folded into SPEC.md/RESULTS.md, the feature-selection programme
closed, and Q30's own options narrowed by the loss of any untouched
held-out year

**D59. Documentation only. No code, no data, no model fit, no score was run
this session. Five parts: accepting F109's result, closing the
feature-selection programme, folding B+D,L,R,T into SPEC/RESULTS as a
third proven method (with required caveats), archiving the now-settled
programme entries, and an update to Q30's own options now that neither
sealed year remains untouched.**

**D59.1 Result accepted.** The owner reviewed F109 and accepts it as
recorded. B+D,L,R,T passes the frozen bar (D58 item 7) at all five
airports: it beats both raw GFS and persistence on MAE everywhere. The
secondary read holds: 1.2377 vs 1.3170 airport-averaged MAE against plain B
(+6.02%). No ranking among airports is claimed. DSM's +1.94% is consistent
with D58 item 7's own expectation. RNO's +10.72% is descriptive only.
Cites F109.

**D59.2 Feature-selection programme closed.** The programme (D51 reserve →
E1–E5, F97–F105, D52–D56 → combine sweep D57/F106 → lock D58 → build
F107/F108 → one look F109) is complete. No further feature family, variant,
or combination is tested under it. The reserved year is spent for this
programme and is not reused for any verdict. The in-code reserved-year
guard (`scripts/session48_reserved_year.py`'s `assert_reserved_year_
excluded()`) stays in place, untouched, as a permanent tripwire. It is not
retired.

**D59.3 Fold-in, with required caveats.** B+D,L,R,T goes into SPEC as a
new section 8, a third proven method alongside sections 1–6 and section 7.
None of the three erases the others (same spirit as D48.13). It becomes the
**default recipe** for any future airport work or pooling work, applied
unchanged and identically at every airport. Every new airport still needs
its own lock and single test. Any write-up of this result must carry these
caveats:
- (a) one year only;
- (b) this is the first look at the *selected set* on 2024-25, but B was
  already scored on that year descriptively in F96 (D58 item 8);
- (c) the section-8 margins (reserved year 2024-25) and the section-7
  margins (sealed year 2025-26) come from **different years** and must not
  be set side by side as like-for-like;
- (d) DSM's margin over B is small;
- (e) RNO's margin over B was not pre-registered.

**D59.4 Archive.** Once SPEC and RESULTS carry the content: archive
F97–F109 and D52–D58 to DECISIONS-archive.md. D51 and F96 stay live,
because Q30's second-test-year branch (D59.5, below) needs both
word-for-word.

**D59.5 Q30 — options only. Q30 stays open.** A new fact changes the
options: **no untouched held-out year now remains.** The 2025-26 year is
spent (F94) and 2024-25 is spent (F109). The three branches:
- **A further airport.** Run it with B+D,L,R,T frozen unchanged. For a new
  airport, 2024-25 and 2025-26 have never been scored at that airport, and
  the recipe was selected without it. That makes this the cheapest
  genuinely out-of-sample test available now. It needs an airport choice:
  per D32, a harder type (coastal, tropical, or mountainous).
- **A second test year.** This is now only possible in one of two ways:
  - (i) a **live, forward-looking test on 2026-27**
    (2026-08-01..2027-07-31), pre-registered before any of its data is
    scored, and scored once after the year ends. Step 0 of session 65
    confirmed no row anywhere under `data/processed/` reaches or exceeds
    2026-08-01, so this option's clock has not started.
  - (ii) a written rule for reusing an already-seen year, which gives
    weaker evidence.
- **Pooling (SPEC stage 3).** This is the largest build. With five
  locations, location-describing features have few examples to learn from,
  and pooling was previously judged premature.

**Planning-chat recommendation (not a decision, and the owner has not
chosen):** open a further airport under the frozen B+D,L,R,T recipe now.
In parallel, pre-register 2026-27 as a forward-looking test year (a small
documentation step) so that its clock is running. Defer pooling. This
recommendation is recorded for the next planning session; nothing was
decided or started on any of the three branches this session.

**What this decision did not do.** Did not fit any model or compute any
new figure — every number in D59.1–D59.5 is copied from and cited to F109,
D58, F96 or F94. Did not read, load, or score a single row of the reserved
2024-08-01..2025-07-31 year or the sealed 2025-08-01..2026-07-31 year —
Step 0 was a read-only max-date scan of already-committed files under
`data/processed/`, not a score. Did not touch any row dated
2026-08-01 or later — none exists in any committed file (Step 0). Did not
retire or modify the reserved-year guard. Nothing was committed.

---

## 2026-09-23 — Session 65 finding: what changed in SPEC.md, RESULTS.md and
DECISIONS.md this session, and what was archived. Documentation only.

**F110. Records exactly what changed, for the record, so a later session
does not have to re-derive it from a diff. No code, data, model, or figure
was touched anywhere this session; every number moved into `SPEC.md`/
`RESULTS.md` this session was copied from, and cited to, its own DECISIONS
source (mainly F109, D58, D51, F96).**

**Step 0 (integrity check).** `git status --porcelain` showed only the
untracked session prompt, `docs/session-65.md` — no other file had
uncommitted changes before this session's own edits began. A read-only
scan of every `.csv` under `data/processed/` for its own date column (or,
where none exists, the nearest fold-boundary date column) found a maximum
date of **2026-07-31** — the sealed test year's own last day (F94) — at
every file that carries a date at all. **No row anywhere under
`data/processed/` reaches or exceeds 2026-08-01.** This directly supports
D59.5's own statement that the forward-looking-2026-27 branch of Q30 has
not yet started its clock.

**Changes to `SPEC.md`.** One change: a new `## 8. The selected-features
GRIB method (a third, proven method)` was added after section 7, covering
what it is (the table of D58 item 3's four added features, their
committed columns, source files and transforms), what is unchanged from
section 7 (citing F98/F100/F101/F102 for each added family's own source
and lead, to the extent each of those entries states it), the confirmation
fold/settings/complete-case rule (D58 items 4–5), how it was chosen (D51,
F98–F105, D52–D56, D57/F106, D58), the F109 result table, the D59.3
caveats in full, and its status as the project's default recipe (D59.3).
**Sections 1–7 were checked for any literal text asserting the project has
"two" methods (`grep -n -i "two method\|second method\|two independently\|
two proven\|two recipes" SPEC.md`) — none was found, so no other edit was
made to sections 1–7.** (Section 7's own heading, "a second, proven
method," and its own "two independently-tested, independently-passing
methods" sentence in 7.5 are both scoped statements about the minimal and
richer methods specifically, not a claim that the project has only two
methods in total, so neither needed changing.)

**Changes to `RESULTS.md`.** Four changes: (1) the intro paragraph (section
0, unheaded) was rewritten from "two" proven methods to "three," naming
the new section 6 as "act three" and adding "revised after session 65" to
its own dateline; (2) a new `## 6. Act three: the selected-features method`
was inserted after section 5 (act two), with four subsections — why the
programme was run (F97), the protocol (D51, F98–F105, D52–D56, D57/F106,
D58), the F109 result table (bar result led with, the +6.02% secondary
read second, RNO's own margin not headlined, per the session prompt), and
the D59.3 caveats in full; (3) the former `## 6. Limitations and open
directions` was renumbered to `## 7.`, with its own opening line updated
from "two proven methods" to "three," its first bullet (the richer-features/
Reno question) updated to state that upper-air information has since been
tried and partly adopted (`lapse_rate_t2_t850`, D52/D58) while a genuine
terrain descriptor remains untested, its second bullet (the shared-test-year
limitation) rewritten to state that no untouched held-out year now remains
at any airport (D59.5) and what the two remaining options for a further
independent year are, its third bullet (cross-method margin comparisons)
left unchanged in substance with one added sentence noting the
selected-features method's own margins come from a different year, and its
fourth bullet (parked directions) rewritten to state Q30's own three
current branches per D59.5, including the planning-chat recommendation on
record there; (4) the closing footer was updated to add "revised again
(session 65, DECISIONS F110)." **A check for other in-file cross-references
to "section 6" (`grep -n "section 5\\|section 6\\|section 7" RESULTS.md`)
found none pointing at the old section 6 by number anywhere else in the
file — the only "section 7" mention refers to `SPEC.md`'s own section 7,
unrelated to `RESULTS.md`'s own numbering — so no further reference fix was
needed.**

**Changes to `DECISIONS.md`.** Two entries appended this session: **D59**
(five numbered items — result accepted, programme closed, fold-in with
caveats, archive instruction, and Q30's options narrowed) and this entry,
**F110**. Per D59.4, the following entries are archived to
`DECISIONS-archive.md`, mechanically, verbatim, and in order, immediately
after this entry is written: **F97, F98, F99, F100, F101, F102, F103,
F104, F105, F106, F107, F108, F109** and **D52, D53, D54, D55, D56, D57,
D58**. **D51 and F96 stay live**, per D59.4, because Q30's second-test-year
branch (D59.5) needs both word-for-word. **D59 and F110 stay live** — the
session's own record, and load-bearing for the owner's next review. Exact
before/after line counts for both files are reported in the archive move
itself, immediately following this entry.

**What this session did not do.** Did not fit any model, run any script
under `scripts/`, or touch any file under `data/` — this was a
documentation-only session throughout (the session prompt's own scope).
Did not compute any new number — every figure placed into `SPEC.md` or
`RESULTS.md` this session is copied from, and cited to, an existing
DECISIONS finding. Did not open, score, or otherwise touch a single row of
either the reserved 2024-08-01..2025-07-31 year or the sealed
2025-08-01..2026-07-31 year — Step 0's own date scan was read-only, over
already-committed files, and reported dates only. Did not touch any file
dated 2026-08-01 or later, because none exists. Did not retire or modify
the in-code reserved-year guard (D59.2). Nothing was committed — the owner
reviews and commits this session's changes by hand.

**Review corrections (same session, before commit; not a new finding —
wording fixes to this session's own SPEC/RESULTS/STATUS edits, each
re-verified against its cited DECISIONS entry, archive included, before
being applied).** Seven fixes: (1) F97's own count restated as 27
candidate variables across five families, not "seven families" (`SPEC.md`
§8.4 was not affected by this one; the miscount was in `RESULTS.md` §6.1
only). (2) All five feature families (D52–D56) each contributed one
adopted feature, precipitation included — precipitation was adopted by
D56 and only later dropped by the combine-phase sweep's own mechanical
rule (D57/F106), confirmed in D58; it was not dropped by D56 itself. Fixed
in `SPEC.md` §8.4 and `RESULTS.md` §6 (intro, 6.1, 6.2). (3) D's
floor-transform row count (`SPEC.md` §8.1) restated as "1 of 7,952 rows"
(D58 item 3's own wording — the v16 and sealed windows combined) rather
than "training-window rows"; one sentence added naming the reserved-year
feature source files (`session63_reserved_window_with_*.csv`, F107). (4)
`SPEC.md` §8.3's zero-drop attribution corrected to D58 items 5 and 9
(training-window pre-registration and verification); F107's own separate
365-of-365 reserved-year complete-case count added alongside it. (5)
`RESULTS.md` §6.3's DSM sentence re-cited to D58 item 7's own
pre-registered expectation (drawing on F96 and F106's own DSM diagnostic)
rather than to finding 4, which does not itself discuss this. (6)
`RESULTS.md` §7 and `STATUS.md`'s "no untouched held-out year" wording
narrowed from "any airport" to "any of the five airports," and
`RESULTS.md` §7 reworded so it no longer attributes the reserved year
(D51, carved out of the training window) to SPEC 4.3's own split dates
(SPEC 4.3 fixes only the sealed test year). (7) `STATUS.md`'s "Session
65's own work" paragraph trimmed to current-state only, and its "Next"
section's closing line changed to name the owner's still-open Q30 choice
(DECISIONS D59.5) as the next planning session's subject, since the
owner's review of this session's documentation itself already happened in
the planning chat that produced these corrections. No DECISIONS finding
or verdict changed by any of the seven; `D59` itself was not touched.

---

## 2026-09-23 — Session 69 decision: audit triage (D60, D61) recorded

**D62. Documentation only. This entry records the owner's triage of every
finding in the four audit reports (`notes/audit-session-66.md`,
`notes/audit-session-67.md`, `notes/audit-session-68a.md`,
`notes/audit-session-68b.md`), made in the planning chat, and the session
plan that follows from it. No code, data, model or figure is touched by
this entry.**

**D62.1 The audit's outcome.**
- No leakage and no wrong number was found (audit-68b section 1).
- 163 of 163 recorded figures reproduce exactly (audit-68a section 1).
- 315 of 315 sampled B values were rebuilt exactly from the raw GRIB
  (audit-68a section 4.2).
- No verdict, claim or figure on record changes (D60.2, D61.4).

**D62.2 The triage rubric (owner decision).**
- **Must-fix:** SPEC, or a binding rule, is untrue as written today.
- **Should-fix:** a gap in the record, or a latent risk for code that will
  be reused.
- **Leave-alone:** no effect, or a frozen script whose look is spent. These
  are recorded here and nothing else is done.

**All must-fix and should-fix items are done before any Q30 branch is
chosen.** Q30 stays open and unchanged (D59.5, D60.1).

**D62.3 Owner rulings.**
- (a) **Frozen scripts are never edited.** Their issues are recorded in
  D62.6 only. The frozen scripts are `session39_sealed_test.py`,
  `session48_reserved_year.py`, `session60_combine_design.py` and
  `session62_reserved_confirm.py`.
- (b) **A67-12: SPEC 4.5's rule still says "nearest".** A paragraph under
  it now records that the historical code kept the last qualifying report
  (1 tie day, with equal temperatures, so no effect). The historical
  scripts are not edited. New code must select the nearest report
  explicitly (SPEC 8.7 build requirements).
- (c) **A68a-01: a network session will rebuild L, D, T and R** for the
  same 45 station-days (session 71).
- (d) **A68b-02 is must-fix.**
- (e) **A67-09 moves from cosmetic to should-fix.** The fix is D62.7's
  one-line description of each file. **No file is deleted.**

**D62.4 Must-fix (3).**
- **A68b-02.** The GRIB methods' raw-GFS rung is the elevation-adjusted
  GRIB temperature (D48.10). SPEC 5.2 calls raw GFS "the uncorrected
  forecast". So a reader of SPEC alone would take the F94 and F109 margins
  to be against a forecast with no adjustment at all. Fixed in this
  session: SPEC and RESULTS. The SPEC 5.2 edit sits in the FROZEN section
  5 and only clarifies what "raw GFS" means per method; the bar (5.3) and
  every verdict are unchanged.
- **A67-12.** SPEC 4.5 says "nearest"; the code keeps the last qualifying
  report. The whole record has 1 tie day (YSDU), with equal temperatures,
  so there is no effect. Still, SPEC did not say what the historical code
  does. Fixed in this session: SPEC 4.5's rule still says "nearest", and a
  paragraph under it now records the historical code's last-report
  behaviour; SPEC 8.7 requires new code to select the nearest report
  explicitly.
- **A67-01.** The provenance for the session 37 and 40 GRIB pulls (URLs,
  byte ranges, pull times and the failure logs) exists only inside the
  gitignored cache, which does not meet D47. If the cache is deleted, that
  record is lost. Fixed in session 70.

**D62.5 Should-fix.**

This session (documentation):
- **A68b-03: the persistence day basis.** The GRIB methods score
  persistence only on test days with a previous-day observation, while
  raw GFS and the models use every test day. SPEC and RESULTS never say
  so.
- **A66-08: CLAUDE.md's paste wording** (owner-reclassified in audit-66
  section 5). Planning chats now read the files from claude.ai Project
  knowledge, not from pasted copies, so the wording is out of date.
- **The "run once" wording in SPEC 7.4 and 8.4 needs a pointer to
  D61.4.** Both say the frozen script ran once; session 68a then re-ran
  each once more, for verification only. This point came from 68a's
  end-of-session check.
- **SPEC 3.4's RNO stage, "2 — failed", is true of the minimal method
  only.** Reno passes the richer (F94) and selected (F109) methods.
- **A66-06.** SPEC 6's "Further airports may follow" bullet does not say
  which recipe a new airport uses, although SPEC 8.7 makes B+D,L,R,T the
  default.
- **A66-07.** Three terms in SPEC ("bilinear-interpolated", "lapse rate",
  "complete-case") have no plain-language gloss at first use, which
  CLAUDE.md's style rule asks for.
- **The new SPEC 8.7 build requirements**, which carry the lessons of
  A68b-01, A68b-04, A68b-05, A67-12, A67-02 and A67-03. Each is a latent
  risk that had no effect on the record but would matter if the code were
  reused for a new airport.
- **A67-09.** Five tracked files are named in no document and used by no
  other script, so a reader cannot tell what they are.
- **The archive move, which covers A66-01 and A66-02.** F94, D49, F95 and
  D50 now meet the D46 archive criterion: settled, and their headlines are
  carried in SPEC and RESULTS.
- **Reno's result in SPEC 1 and SPEC 6, and RESULTS section 1's account of
  the methods, named only the first two methods; so did SPEC 7.5's
  sentence on which methods pass where.** SPEC 1 and 6 now add that the
  selected-features method (section 8) also passes at Reno (F109).
  RESULTS section 1 now covers all three methods (SPEC 7, 8; F94, F109).
  SPEC 7.5 now says all three methods pass at EGLC, LFPG, DSM and YSDU
  (F16/F30/F47/F64, F94, F109), and Reno fails the minimal method (F82)
  and passes the richer and selected methods (F94, F109). No new figures.
  These were found at session 69's consistency check and fixed in this
  session.

Session 70 (repo, offline):
- **A67-01** (must-fix, D62.4): build committed provenance manifests for
  the session 37 and 40 pulls.
- **A67-06:** `data/processed/session46_fold_table.csv` has no station
  column, so a row can be matched to its airport only by file order.
- **A67-05 with A67-07:** there is no README; the only setup notes are
  comments in `requirements.txt`, and some of those are out of date.
- **A67-08 with A68a-06:** `.gitignore` gaps (no comment on the GRIB cache
  rule, `.claude/` and scratch GRIB files not ignored, and a trailing
  slash that misses a symlinked cache).

Session 71 (network):
- **A68a-01:** L, D, T and R cannot be checked against the raw GRIB
  offline, because their build scripts fetch, decode and delete the bytes
  in one step.

**D62.6 Leave-alone (recorded only).**

Frozen, looks spent, no edit:
- **A67-02 and A67-03.** These scripts write fixed, committed output
  paths. Any future re-run must happen in a clean clone.
- **A67-04.** The preflight's "no reserved-year row is read" text has been
  stale since F107. The rows are loaded but not used (68b item 22).
- **A67-14.** It cannot happen on the F109 path (0 of 9,777 complete-case
  rows).
- **A68a-04.** An absolute path is printed in the F94 output.
- **A68a-05.** The F109 confirm output was captured outside the script, in
  session 64.
- **A68b-01.** The frozen part: the F109 gap guard checks for zero rows
  only. No effect, since there were 365 of 365 rows.
- **A68b-04.** The frozen parts: `float()` accepts `nan`. There are 0 such
  values today.
- **The frozen F94 docstring** (`session39_sealed_test.py:9`) says all
  rungs use "the same common days". The code does not do that (A68b-03).

Other:
- **A66-03.** Resolved itself: session 66's own STATUS.md rewrite replaced
  the stale "Next" line.
- **Audit-66's "15 dated headers".** This was a prose miscount; its own raw
  output shows 14 (audit-67 section 6.3).
- **A66-04 and A66-05.** P1 is superseded by Q30. P2 and P3 have met their
  trigger and are eligible to revisit. No action. The parked block is not
  edited.
- **A67-10 and A67-11.** Lint findings (unused imports and variables,
  f-strings with no placeholders) and functions copied between scripts.
  None affects a result; the copying is how each frozen script stays
  self-contained.
- **A68a-02.** The constants are frozen by D48.3. Terrain interpolation
  matched 5 of 5.
- **A68a-03.** For the minimal method, D60.2's "fourth decimal" is read as
  the recorded precision, which is 3 decimals.
- **A68b-05, A68b-06 and A68b-07.** A68b-05: the L and D fetches check the
  validity date but not the hour; every manifest row's hour was right.
  A68b-06: the five minimal-method scripts' stop checks differ, and some
  only print; 68a reproduced every count. A68b-07: the EGLC Open-Meteo pull
  used a rounded position, but Open-Meteo returned the SPEC 3.4 grid point
  anyway. None has any effect on a value.

**D62.7 Rulings and records.**
- **A67-13.** Small diagnostic GRIB samples under `data/raw/diagnostics/`
  stay tracked. D47 covers the bulk pull only.
- **A67-15.** The two tracked DSM files for 2026-08-05..2026-08-15 must be
  named in any 2026-27 pre-registration, if Q30 branch (i) is chosen.
- **A67-09.** What each of the five files is, from its own contents. All
  five stay in the repo.
  - `scripts/session01_checks.py`: session 01's read-only verify-on-contact
    script; it reports the shape of the first EGLC forecast and
    observation samples and counts their gaps, and writes nothing.
  - `scripts/session03_checks.py`: session 03b's read-only gap-map script;
    it counts rows and maps the missing hours in the full EGLC forecast and
    observation history, without joining or modelling anything.
  - `scripts/session03_pull.py`: session 03b's download script; it pulls
    the full temperature-only history for both sources in yearly chunks
    into `data/raw/`, with a `.meta.txt` beside each chunk.
  - `notes/session-01-check-output.txt`: the saved printed output of
    session 01's verify-on-contact checks at EGLC (forecast archive start,
    observation coverage, and the :20 second report).
  - `notes/session-53-pressure-output.txt`: the saved printed output of
    session 53's pressure-feature (E3) build and validation run, printed by
    `scripts/session53_pressure_pull.py`.

**D62.8 Session plan.**
- **69:** this session.
- **70:** repo fixes, offline.
- **71:** the L, D, T and R rebuild, with network. Data only. The pull date
  is recorded (SPEC 2.3).
- **Then Q30.**

**D62.9 What this decision did not do.** No code, data, model or figure was
touched. No file was deleted.

---

## 2026-09-24 — Session 75 decision: planning-chat decisions and the Q33 pre-registration

**D66. Owner decisions, planning chat (after session 74).** Written before
any model was fit this session.

**D66.1 Q30 sequencing (Q30 stays open).** The owner chose this order:
1. Q33, measured descriptively (session 75).
2. A further airport under the frozen B+D,L,R,T recipe (Q30 branch (i),
   D59.5). The airport and its test design are still to be chosen.
3. A dedicated roadmap planning session, because SPEC 6's stage list is
   out of date.

Pooling is deferred. The 2026-27 forward test (Q30 branch (ii)(i)) is
deferred until the GFS v17 date is known (D66.2).

**D66.2 GFS v17 status (planning-chat research, not checked by session
75).** NWS Public Information Statements 26-29 and 26-30 (April 2026)
propose GFS v17 (a ~9 km, coupled model) for October 2026, marked
tentative. They say a Service Change Notice will be issued 30 days before
go-live, and that folder structure and file names will change. As of
2026-09-24 the NWS notice list shows no such notice.

Why it matters: the recipe is trained on GFS v16 only (D48.7). If v17 goes
live during 2026-27, most of that year would be v17 forecasts. A 2026-27
test would then ask a different question (does a v16-trained correction
survive a model upgrade?) rather than repeat F109 on a new year. The
new-airport branch is unaffected: all its data (2021–2026) is v16. Future
GRIB pulls of v17 data may need path and `.idx` changes. To be re-checked
at each planning session.

**D66.3 Q33 pre-registration.**

*Standing.* A description, not a verdict. It cannot change any verdict,
claim or figure on record. F109 stands. Nothing is selected, tuned or
adopted on these results. No row dated 2024-08-01 or later is used
anywhere: not the reserved year (2024-25, spent, F109), not the sealed
year (2025-26, spent, F94), and nothing from 2026-27.

*Data.* The `2022-23` and `2023-24` folds of D51's `EXPERIMENT_FOLDS`, all
five airports:
- `2022-23`: train 2021-03-24..2022-07-31 (495 days), test
  2022-08-01..2023-07-31;
- `2023-24`: train 2021-03-24..2023-07-31 (860 days), test
  2023-08-01..2024-07-31.

The same committed feature files, transforms, complete-case rule, target,
settings and API as the record (SPEC 8.1, 8.3, 8.8: G14, G17, G19, G20).
Any row dated 2024-08-01 or later is removed at load, before any matrix is
built, and the count removed is reported.

*Models.* `B` (5 columns) and `B+D,L,R,T` (9 columns).

*What varies: column order only.*
- B+D,L,R,T: 100 orderings drawn with `numpy.random.default_rng(75)`,
  duplicates redrawn, **plus** two anchors: the record order (SPEC 8.8
  G15) and session 73's order (B, then L, D, T, R). 102 in total.
- B: all 120 orderings of its 5 columns.
- Seeds: Step 0.2 of session 75 found no random setting in `LGB_PARAMS`
  (`subsample=1.0`, `colsample_bytree=1.0`, no bagging frequency set,
  `deterministic=True`). So the 10-seed check is **not run**.

*What is reported,* per airport and per fold:
- min, max, range and standard deviation of MAE for B and for B+D,L,R,T,
  in °C and as % of the record-order MAE;
- the **win share**: over every (B+D,L,R,T ordering, B ordering) pair, the
  fraction where B+D,L,R,T has the lower MAE;
- the record-order margin over B (record-order B+D,L,R,T against
  canonical-order B), for reference.

*Reading rule, fixed now.* Win share 100% → "B+D,L,R,T beats B by more
than the column-order spread, on this fold". 0% → "B beats B+D,L,R,T by
more than the spread". Anything else → "within the column-order spread".
Stated per airport, per fold. No other reading is added after the results
are seen.

*Scale comparison (rough, different year).* A table setting F109's own
margins over B (SPEC 8.5: EGLC 0.0853, LFPG 0.0916, DSM 0.0279, YSDU
0.0387, RNO 0.1530 °C) and F114's 0.0038 °C shift beside each airport's
B+D,L,R,T MAE range on each fold. Labelled: F109 is 2024-25, these folds
are 2022-23 and 2023-24, and the training windows are shorter (495 and 860
days against F109's 1,226), so this is a guide to scale only.

*Implementation details, fixed before any fit (session 75).*
- The orderings are drawn once and the same list is used at every airport
  and on both folds.
- Each draw is `rng.permutation(9)` applied to the record-order column
  list. A draw that repeats an earlier draw or either anchor is redrawn,
  so all 102 orderings are distinct.
- "Lower MAE" in the win share is strict: a tie counts as not a win.
- The standard deviation is the population form (`numpy.std`, ddof 0).

*What it cannot do.* Change any verdict, claim or figure; select or adopt
anything; touch any row dated 2024-08-01 or later.

---

## 2026-09-24 — Session 75 finding: column order alone, on the 2022-23 and 2023-24 folds (Q33, descriptive)

**F115. Offline, under D66.3. Descriptive only. On both non-reserved folds,
at all five airports, every one of the 102 B+D,L,R,T column orderings has a
lower MAE than every one of the 120 B orderings (win share 100% in all 10
airport-folds). Column order alone moves a fit's MAE by 0.014 to 0.039 °C
(range across orderings). F115 changes no verdict, claim or figure. F109
stands. Full real output: `notes/session-75-output.txt`.**

**F115.1 Step 0.**
- `git status --porcelain` showed only `?? docs/session-75.md`.
- `LGB_PARAMS` (`session62_reserved_confirm.py` l.131–146):
  `objective="regression_l1"`, `n_estimators=300`, `learning_rate=0.05`,
  `num_leaves=15`, `min_child_samples=40`, `subsample=1.0`,
  `colsample_bytree=1.0`, `reg_alpha=0.0`, `reg_lambda=0.0`,
  `random_state=42`, `n_jobs=1`, `deterministic=True`,
  `force_row_wise=True`, `verbose=-1`. No setting makes a fit random:
  `subsample` and `colsample_bytree` are 1.0 and no bagging frequency is
  set (the lightgbm default is 0, no bagging). So Task 2c was not run.
- Both folds match D51's `EXPERIMENT_FOLDS` (495 and 860 training days)
  and neither raises in `assert_reserved_year_excluded()`.

**F115.2 Data.** New script `scripts/session75_order_spread.py`. It imports
the record script's helpers read-only (settings, feature matrix, MAE, the
observation loader, the complete-case rule and the join). It reads only
the committed v16-window files and the IEM observation files.
- Rows removed at load because they are dated 2024-08-01 or later:
  1,825 from `grib_features_v16_window.csv` (the reserved year, all five
  airports); 0 from each of the L, D, T and R v16-window files; and
  observation days EGLC 728, LFPG 729, DSM 730, YSDU 716, RNO 730.
- Non-finite values dropped: 0 everywhere.
- No reserved-year, sealed-year or later file was opened.

**F115.3 Anchor and determinism checks (2a).**

| airport | fold | n_train | n_test | B (canonical) MAE | 4 dp | B+D,L,R,T (record order) MAE | 4 dp |
|---|---|---|---|---|---|---|---|
| EGLC | 2022-23 | 495 | 364 | 1.1676942078095525 | 1.1677 | 1.0970480192866763 | 1.0970 |
| EGLC | 2023-24 | 859 | 366 | 0.9470167774837449 | 0.9470 | 0.8714881558099459 | 0.8715 |
| LFPG | 2022-23 | 493 | 365 | 1.1581288431631402 | 1.1581 | 1.1133895478467908 | 1.1134 |
| LFPG | 2023-24 | 858 | 366 | 1.1605941837409353 | 1.1606 | 1.1221218810408342 | 1.1221 |
| DSM | 2022-23 | 495 | 364 | 1.7262636931223527 | 1.7263 | 1.6498714917606239 | 1.6499 |
| DSM | 2023-24 | 859 | 366 | 1.5787427636597116 | 1.5787 | 1.4882809710048912 | 1.4883 |
| YSDU | 2022-23 | 493 | 357 | 1.199133818957037 | 1.1991 | 1.1431189528380674 | 1.1431 |
| YSDU | 2023-24 | 850 | 363 | 1.126391420782976 | 1.1264 | 1.0948569148657197 | 1.0949 |
| RNO | 2022-23 | 493 | 364 | 1.4011745129574764 | 1.4012 | 1.3384891085072084 | 1.3385 |
| RNO | 2023-24 | 857 | 365 | 1.2971855086239619 | 1.2972 | 1.14583207633231 | 1.1458 |

- **A recorded value at the same column order exists, and all 20 match at
  4 dp, with the same n_train and n_test.** The source is
  `data/processed/session61_combine_sweep_grid.csv` (F106), rows `B` and
  `B+LDTR`. Session 61's fit orders the added columns by `sorted(codes)`,
  which is D, L, R, T, the record order (`session61_combine_sweep.py`
  l.545), and B in `BASE_KEYS` order. The 2023-24 values also match the
  session 61/62/64 table in F109's Step 1 (DECISIONS-archive.md). So the
  stop rule did not fire.
- Record-order B+D,L,R,T repeated in a separate process: predictions
  equal on every test day at all 10 airport-folds (3,640 of 3,640),
  maximum absolute difference 0.0.
- The spread run's own anchor fits equal the 2a fits exactly (20 of 20).

**F115.4 The spread (2b).** 102 B+D,L,R,T orderings (2 anchors and 100
drawn; no draw needed redrawing) and 120 B orderings, on 2 folds at 5
airports: 2,220 fits, no other fit. MAE in °C. The % columns are relative
to that model's record-order MAE (for B, the canonical order). min% and
max% are signed differences from it.

*B (120 orderings)*

| airport | fold | record | min | max | range | sd | min% | max% | range% | sd% |
|---|---|---|---|---|---|---|---|---|---|---|
| EGLC | 2022-23 | 1.1677 | 1.1569 | 1.1773 | 0.0205 | 0.0035 | −0.93% | +0.83% | 1.75% | 0.30% |
| EGLC | 2023-24 | 0.9470 | 0.9421 | 0.9561 | 0.0140 | 0.0032 | −0.52% | +0.96% | 1.48% | 0.34% |
| LFPG | 2022-23 | 1.1581 | 1.1439 | 1.1581 | 0.0143 | 0.0024 | −1.23% | +0.00% | 1.23% | 0.21% |
| LFPG | 2023-24 | 1.1606 | 1.1498 | 1.1704 | 0.0206 | 0.0043 | −0.93% | +0.84% | 1.77% | 0.37% |
| DSM | 2022-23 | 1.7263 | 1.7199 | 1.7495 | 0.0296 | 0.0062 | −0.37% | +1.35% | 1.71% | 0.36% |
| DSM | 2023-24 | 1.5787 | 1.5654 | 1.5885 | 0.0232 | 0.0044 | −0.85% | +0.62% | 1.47% | 0.28% |
| YSDU | 2022-23 | 1.1991 | 1.1842 | 1.2067 | 0.0225 | 0.0046 | −1.24% | +0.63% | 1.88% | 0.38% |
| YSDU | 2023-24 | 1.1264 | 1.1189 | 1.1381 | 0.0192 | 0.0037 | −0.67% | +1.04% | 1.71% | 0.33% |
| RNO | 2022-23 | 1.4012 | 1.3848 | 1.4123 | 0.0275 | 0.0061 | −1.17% | +0.79% | 1.96% | 0.44% |
| RNO | 2023-24 | 1.2972 | 1.2843 | 1.3090 | 0.0247 | 0.0051 | −0.99% | +0.91% | 1.90% | 0.39% |

*B+D,L,R,T (102 orderings)*

| airport | fold | record | min | max | range | sd | min% | max% | range% | sd% |
|---|---|---|---|---|---|---|---|---|---|---|
| EGLC | 2022-23 | 1.0970 | 1.0856 | 1.1095 | 0.0240 | 0.0053 | −1.05% | +1.14% | 2.18% | 0.48% |
| EGLC | 2023-24 | 0.8715 | 0.8671 | 0.8863 | 0.0192 | 0.0037 | −0.51% | +1.70% | 2.20% | 0.43% |
| LFPG | 2022-23 | 1.1134 | 1.1087 | 1.1362 | 0.0275 | 0.0058 | −0.42% | +2.05% | 2.47% | 0.52% |
| LFPG | 2023-24 | 1.1221 | 1.1071 | 1.1297 | 0.0226 | 0.0037 | −1.34% | +0.67% | 2.01% | 0.33% |
| DSM | 2022-23 | 1.6499 | 1.6278 | 1.6664 | 0.0386 | 0.0069 | −1.34% | +1.00% | 2.34% | 0.42% |
| DSM | 2023-24 | 1.4883 | 1.4725 | 1.5047 | 0.0322 | 0.0067 | −1.06% | +1.10% | 2.16% | 0.45% |
| YSDU | 2022-23 | 1.1431 | 1.1334 | 1.1601 | 0.0267 | 0.0059 | −0.85% | +1.48% | 2.33% | 0.52% |
| YSDU | 2023-24 | 1.0949 | 1.0846 | 1.1144 | 0.0298 | 0.0052 | −0.93% | +1.79% | 2.72% | 0.47% |
| RNO | 2022-23 | 1.3385 | 1.3264 | 1.3484 | 0.0219 | 0.0048 | −0.90% | +0.74% | 1.64% | 0.36% |
| RNO | 2023-24 | 1.1458 | 1.1338 | 1.1610 | 0.0272 | 0.0050 | −1.05% | +1.32% | 2.37% | 0.44% |

*Win share and reading (D66.3 rule).* Margin = canonical-order B MAE minus
record-order B+D,L,R,T MAE. Pairs = 102 × 120 = 12,240.

| airport | fold | wins | win share | margin °C | margin % | reading |
|---|---|---|---|---|---|---|
| EGLC | 2022-23 | 12,240 | 100% | 0.0706 | +6.05% | beats B by more than the column-order spread |
| EGLC | 2023-24 | 12,240 | 100% | 0.0755 | +7.98% | beats B by more than the column-order spread |
| LFPG | 2022-23 | 12,240 | 100% | 0.0447 | +3.86% | beats B by more than the column-order spread |
| LFPG | 2023-24 | 12,240 | 100% | 0.0385 | +3.31% | beats B by more than the column-order spread |
| DSM | 2022-23 | 12,240 | 100% | 0.0764 | +4.43% | beats B by more than the column-order spread |
| DSM | 2023-24 | 12,240 | 100% | 0.0905 | +5.73% | beats B by more than the column-order spread |
| YSDU | 2022-23 | 12,240 | 100% | 0.0560 | +4.67% | beats B by more than the column-order spread |
| YSDU | 2023-24 | 12,240 | 100% | 0.0315 | +2.80% | beats B by more than the column-order spread |
| RNO | 2022-23 | 12,240 | 100% | 0.0627 | +4.47% | beats B by more than the column-order spread |
| RNO | 2023-24 | 12,240 | 100% | 0.1514 | +11.67% | beats B by more than the column-order spread |

("beats B" means "B+D,L,R,T beats B ... on this fold", the rule's full
wording.)

**F115.5 Scale comparison (rough, different year).** F109 is 2024-25,
trained on 1,226 days. These folds are 2022-23 (495 days) and 2023-24
(860 days). A guide to scale only. All in °C.

| airport | F109 margin over B | F114 shift | B+D,L,R,T range, 2022-23 | B+D,L,R,T range, 2023-24 |
|---|---|---|---|---|
| EGLC | 0.0853 | 0.0038 | 0.0240 | 0.0192 |
| LFPG | 0.0916 | 0.0038 | 0.0275 | 0.0226 |
| DSM | 0.0279 | 0.0038 | 0.0386 | 0.0322 |
| YSDU | 0.0387 | 0.0038 | 0.0267 | 0.0298 |
| RNO | 0.1530 | 0.0038 | 0.0219 | 0.0272 |

What the table shows, as numbers only: F114's 0.0038 is smaller than every
range here (the smallest is 0.0192). DSM's F109 margin (0.0279) is smaller
than DSM's range on both folds. The other four airports' F109 margins are
larger than their ranges on both folds.

**F115.6 Answer to Q33 (descriptive).** Column order alone moves a
B+D,L,R,T fit's MAE by 0.019 to 0.039 °C (range, 1.6% to 2.7% of the
record-order MAE), and a B fit's by 0.014 to 0.030 °C. F114's 0.0038 °C
(on a different year) is smaller than every one of these ranges. By the pre-set reading rule, on both
folds and at all five airports, B+D,L,R,T beats B by more than the
column-order spread: every B+D,L,R,T ordering beats every B ordering. This
covers the 2022-23 and 2023-24 folds only. It does not re-score or re-read
F109, and it says nothing about 2024-25 itself. **Q33 is answered
descriptively and closed here.**

**F115.7 What this did not do.**
- It changed no verdict, claim or figure. F109 stands.
- Nothing was selected, tuned or adopted.
- No row dated 2024-08-01 or later was used (F115.2).
- No existing script was edited. The record script and sessions 48 and 60
  were only imported, read-only.
- No data was pulled. No value was filled. No file was deleted.
- Nothing under `data/raw/`, `data/processed/` or earlier
  `data/rebuild/` folders was changed.
- SPEC.md, RESULTS.md, README.md and CLAUDE.md were not edited.
- The seed check (2c) was not run: no random setting.

The new files are:
- `scripts/session75_order_spread.py`;
- `data/rebuild/session75/` (`anchor_mae.csv`, `anchor_predictions.csv`,
  `metadata.json`, `orderings.csv`, `spread_mae.csv`, `summary.csv`,
  `win_share.csv`, and `run2/anchor_predictions.csv`);
- `notes/session-75-output.txt`.

F115 stays live: the new-airport pre-registration will cite it. Nothing
was committed.

---

## 2026-09-25 — Session 76 decision: the new airport (KSFO) and its test design

**D67. Owner decisions, planning chat (after session 75): the new airport
and its test design.** Written before any KSFO data was pulled.

- **D67.1 Airport.** San Francisco International (KSFO), Q30 branch (i)
  (D59.5, D66.1), under the frozen `B+D,L,R,T` recipe (SPEC 8), applied
  unchanged. It is a coastal airport, a harder type per D32. Its standard
  offset is UTC−8, so its target hour is 20:00 UTC (local standard noon,
  D33), the same hour and lead (26) as RNO.
- **D67.2 Offset rule (hard filter for new airports under SPEC 8).** R has a
  frozen construction only for lead 24 (target hour a multiple of 6) and
  lead 26 (target hour mod 6 = 2) (SPEC 8.2). A new airport keeps the
  recipe unchanged only if its local-standard-noon hour gives one of those
  two leads, i.e. standard offset 0, −2, +4, ±6, −8, +10 or +12.
- **D67.3 Test design: two pre-registered looks.**
  - Look A: train 2021-03-24..2024-07-31 (1,226 days), test
    2024-08-01..2025-07-31. An exact replica of F109's fold.
  - Look B: train 2021-03-24..2025-07-31, test 2025-08-01..2026-07-31.
  - Each year is judged **separately** against the frozen bar (SPEC 5.3):
    beat raw GFS (GRIB, elevation-adjusted with KSFO's own constant) and
    persistence on MAE.
  - "KSFO passes" is claimed only if both looks pass. If one passes and one
    fails, it is recorded as a split. Nothing is re-run or adjusted.
  - Both looks are frozen in one script before either year is opened, and
    run once, together, in session 78.
  - Pre-registered expectation (to be restated in the lock): pass in both
    years.
- **D67.4 Rehearsal (session 77).** On the `2022-23` and `2023-24` folds of
  D51's `EXPERIMENT_FOLDS` only (the truncated `2025-26` fold is excluded:
  it tests a KSFO held-out year). Purpose: a pipeline check and the
  column-order spread (D67.5). It is **not a gate**: a poor rehearsal does
  not stop the lock (D44 precedent). The only stop is a bug, and any fix is
  to the pipeline, never to the recipe.
- **D67.5 The vs-B band (column-order wobble, F115).** In rehearsal, KSFO's
  column-order spread is measured with F115's method and F115's own
  orderings (`data/rebuild/session75/orderings.csv`: the 102 `B+D,L,R,T`
  orderings; all 120 `B` orderings). **Band = the largest MAE range (max −
  min across orderings) among the four sets {B, B+D,L,R,T} × {2022-23,
  2023-24}.** It is frozen in the lock. For each look, the record-order
  `B+D,L,R,T` margin over canonical-order `B`: above +band → "beats B by
  more than the column-order spread"; below −band → "B beats B+D,L,R,T by
  more than the spread"; otherwise → "within the column-order spread". This
  is a secondary read, not part of the bar. F115's largest range (0.0386 °C)
  is quoted beside it as context only.
- **D67.6 Held-out handling at KSFO.** 2024-08-01..2026-07-31 is held out.
  Before the lock, only counts and timestamps from it are read.
  Verify-on-contact samples are drawn from outside it. No row dated
  2026-08-01 or later is used.
- **D67.7 Session plan.** 76 verify, pull and build; 77 rehearsal, spread
  and lock; 78 the two looks.
- **D67.8 GFS v17 (planning-chat research, 2026-09-25, not checked by this
  session).** The NWS notice list shows no GFS v17 Service Change Notice;
  the latest SCN is SCN26-87 (22 Sep 2026). An SCN comes 30 days before
  go-live, so the earliest possible go-live is late October 2026. KSFO is
  unaffected: all its data (2021-03-24..2026-07-31) is v16. Re-check at
  each planning session (D66.2).

---

## 2026-09-25 — Session 76 finding: KSFO verified on contact, pulled and built; the reproduction gate FAILS

**F116. Network, then offline. No model was fit. No MAE, and no forecast-
minus-observation statistic, was computed for any period. KSFO passed every
verify-on-contact check, and all its data was pulled and built. But the
GRIB-vs-Open-Meteo reproduction gate (F89/F90's criterion) FAILS at KSFO:
mean |diff| 3.395 °C, mean diff −3.326 °C, against a bar of < 1.0 for both.
Per the session prompt (Step 5.4), the session stopped after reporting.
The constant and the pipeline were not changed, and Step 5.5 (feature
sanity) was not run. F116 changes no verdict, claim or figure. F109 stands.
Full real output: `notes/session-76-output.txt`.**

**F116.1 Step 0.**
- `git status --porcelain` showed only `?? docs/session-76.md`.
- The largest date in any `data/processed/*.csv` is 2026-07-31. No row
  reaches 2026-08-01.
- Confirmations from the scripts (file and line in the output file):
  - (a) the elevation constant (`session37_elevation_fix.py`) is the
    bilinear GRIB model terrain (`HGT:surface`, shortName `orog`) at the
    Open-Meteo grid point, minus that grid point's Open-Meteo elevation,
    times the lapse rate, stored at 4 dp. The record's lapse rate is the
    unrounded RNO fit, 7.429007865 °C/km, stored as 7.429. At KSFO both
    give the same stored constant;
  - (b) T at lead 26 uses f026 and f023 of the same 18z run, as at RNO;
  - (c) R at lead 26 uses the native 24–26 h DSWRF average, no
    de-accumulation, as at RNO;
  - (d) L and D depend on the airport only through its target hour, grid
    point and constant.
  The stop rule did not fire.

**F116.2 Verify on contact (Step 2).** All samples are from outside
2024-08-01..2026-07-31.
- **Station.** IEM `CA_ASOS` listing: sid `SFO`, "SAN FRANCISCO INTL",
  latitude 37.619, longitude −122.3749, elevation 5.0 m, timezone
  America/Los_Angeles, `METAR_RESET_MINUTE` 56. `SFO` is not an ICAO code
  (the ICAO code is KSFO).
- **Target hour.** America/Los_Angeles's standard offset is UTC−8 (read
  from a January date), so local standard noon is 20:00 UTC, as D67.1
  says. Cycle 18z, lead 26.
- **Report minute and units** (2023-06-01..2023-06-21, 504 hours). The
  routine report is at `:56` (504 of 505 rows; one off-hour routine
  report at `:36`). 59 special reports are spread over many minutes; the
  most common minute, `:19`, has 4. So there is no second scheduled
  report ("nothing scheduled", as at DSM). tmpc is °C: largest
  |tmpc − (tmpf − 32) × 5/9| is 0.0044 °C over 97 rows. The tz=UTC
  request is UTC: the local-time series lines up at +7 h (PDT) with 100%
  equal values. Pairing offset to 20:00 UTC: 4 minutes (the 19:56 report).
- **Open-Meteo.** Grid point 37.54637, −122.34375, elevation 1.0 m; 8.53 km
  from the station (the farthest in the project); height mismatch −4 m.
  First non-null hour 2021-03-24 00:00 UTC, all null before it.
- **Elevation constant.** HGT:surface from run 2024-06-09 18z f026 (valid
  2024-06-10 20:00). The four surrounding GRIB points have terrain 38.30,
  55.74, 81.98 and 118.46 m. Bilinear terrain at the grid point is
  94.4704 m; gap 93.4704 m. Constant = 7.429 / 1000 × 93.4704 =
  0.6943915763 °C, stored as **+0.6944 °C**
  (`data/raw/diagnostics/session76/session76_elevation_correction_params.csv`).
- **Land mask.** A `LAND:surface` line is in the f026 .idx, but only the
  HGT message was fetched, so nothing is reported (no new pull, Step 2.6).
- **An incident.** The first Step 2 run got HTTP 429 (too many requests)
  from IEM on its second observation request, and saved the 429 text as
  data. That run's partial raw files were deleted. The script was changed
  to check the status before saving and to pause and retry on 429, then
  re-run from the start.

**F116.3 The pull (Step 4).**
- **GRIB**, fetch-decode-discard (the F98 precedent; ~22 GB would not fit
  next to the existing cache). 14 messages per day over 1,956 days: 27,384
  requested, **27,370 OK, 14 failed**, 23,526,628,688 bytes, pulled
  2026-09-25 09:41:21Z .. 11:06:31Z. Each message's parameter, level, step,
  run, and full validity date and hour were checked (SPEC 8.7 item 3).
  All 14 failures are target day 2022-11-30 (run 2022-11-29 18z): "bad
  magic markers", the same upstream index/file mismatch F90 found for RNO
  on the same day. Per field: 1,955 of 1,956; before 2024-08-01, 1,225 of
  1,226; each held-out year, 365 of 365. Non-finite values: 0.
- **Pipeline check.** KSFO's pulled 2021-03-24 TMP 2 m message has the same
  SHA-256 as session 37's cached RNO file. Decoded at RNO's grid point by
  the new code, it gives 8.754 °C, equal to RNO's record value.
- **Observations**: six IEM routine chunks, 2021-03-24..2026-07-31, 46,916
  rows, station SFO only, last row 2026-07-31 23:56.
- **Open-Meteo** `temperature_2m_previous_day1`, 2021-03-24..2024-07-31: 29,424
  hours, 492 null, one unbroken block 2023-12-30 00:00..2024-01-19 11:00 —
  the shared gap (SPEC 3.2). Cloud cover and wind, 2024-01-19..2024-07-31,
  were also pulled for Step 5.5, which was not run.

**F116.4 The build (Step 5.1–5.3).**
- `data/processed/session76_ksfo_features.csv`: 1,955 rows (2022-11-30
  dropped, logged in `session76_ksfo_feature_drops.csv`), the nine model
  columns in record order (SPEC 8.8 G15), then their underlying columns,
  with the rounding of G4, G5 and G7. All 1,955 rows are complete-case.
  The D floor changed 0 rows. Identity checks on `t2m_raw` and the
  tendency: 0 failures.
- `data/processed/session76_ksfo_observations.csv`: nearest usable routine
  report within 15 minutes of 20:00 UTC, inclusive (SPEC 8.7 item 1).
  1,953 of 1,956 days paired (offset −4 min on 1,952, −3 min on 1). 0 tie
  days. Dropped: 2022-03-17 (no usable temperature), 2024-07-13 and
  2024-12-20 (no routine report in the window).
- Counts (days / features / complete / paired / both): before 2024-08-01
  1,226 / 1,225 / 1,225 / 1,224 / 1,223; 2024-25 365 / 365 / 365 / 364 /
  364; 2025-26 365 / 365 / 365 / 365 / 365. Folds: 2022-23 train 495 / 495
  / 495 / 494 / 494, test 365 / 364 / 364 / 365 / 364; 2023-24 train 860 /
  859 / 859 / 859 / 858, test 366 / 366 / 366 / 365 / 365.

**F116.5 The reproduction gate (Step 5.4), before 2024-08-01 only.** On
1,205 identical rows (20 GRIB days fall in Open-Meteo's gap), diff = GRIB
minus Open-Meteo:
- before the constant (`t2m_raw`): mean |diff| 4.026, mean diff −4.020,
  max |diff| 12.632 °C;
- after the constant (`temp`, the gate): **mean |diff| 3.395, mean diff
  −3.326, max |diff| 11.938 °C → FAIL**.

By month (description only), the mean diff is −0.21 to −0.77 °C in
November–February, −2.2 and −2.5 °C in March and October, and −3.8 to
−6.1 °C from April to September (July −6.06). By year it is −2.7 to
−3.9 °C. So the gap is not a constant offset. The constant is tied to
terrain height, so it cannot remove a gap that changes with the season.
**A likely cause, not tested:** a coastal land/sea effect. The four 0.25°
GRIB points around KSFO's grid point lie across the Pacific coast and the
Bay, and Open-Meteo's own grid point (on a finer grid) is a shoreline land
point. A cool marine value mixed into the interpolation would give a
summer-heavy cold gap like this one. This was not checked (no land-mask
field was pulled). The pipeline itself is not implicated (F116.3).

**F116.6 Held-out handling actually followed.** No row dated 2026-08-01 or
later was pulled or built. KSFO's 2024-08-01..2026-07-31 rows were pulled
and built, but only their counts, dates and timestamps were printed (row
and day counts, pull times, dropped-day dates). No held-out temperature,
cloud, wind or other value was printed, summarised or compared. The
reproduction gate and all value summaries use pre-2024-08-01 rows only.

**F116.7 New files.**
- Scripts: `scripts/session76_verify.py`, `session76_grib_pull.py`,
  `session76_obs_om_pull.py`, `session76_build.py`.
- `data/raw/`: `iem_station_metadata_CA_ASOS.geojson`; the four 2023 SFO
  verify samples; six SFO routine chunks; five SFO Open-Meteo temperature
  files; `features/..._SFO_2024-01-19_2024-07-31_cloudwind.json`; each
  with a `.meta.txt`.
- `data/raw/diagnostics/session76/`: the HGT diagnostic GRIB sample and its
  sidecar, `session76_elevation_correction_params.csv`,
  `session76_pull_manifest.csv` (27,384 rows), `session76_pull_failures.csv`
  (14 rows), `session76_decoded_point_values.csv` (27,370 rows).
- `data/processed/`: `session76_ksfo_features.csv`,
  `session76_ksfo_observations.csv`, `session76_ksfo_feature_drops.csv`.
- `notes/session-76-output.txt`.

**F116.8 What this did not do.**
- It fit no model and computed no MAE or forecast-minus-observation
  statistic, for any period.
- It did not change the constant, the lapse rate or the pipeline after the
  gate failed, and did not run Step 5.5.
- It kept no raw GRIB bytes (D47 is met by the manifest).
- It edited no existing script, frozen or not, and did not touch the
  reserved-year guard. It wrote to no existing data file.
- It did not edit SPEC section 5, RESULTS.md, README.md or CLAUDE.md.
- It changed no verdict, claim or figure. F109 stands.
- Nothing was committed.

---

## 2026-09-25 — Open question raised by session 76 (not acted on)

**Q34. KSFO's reproduction gate failed (F116.5). What happens to KSFO?**
D67 opened KSFO under the frozen B+D,L,R,T recipe "applied unchanged", but
the recipe's GRIB temperature at KSFO does not reproduce Open-Meteo's (mean
diff −3.3 °C, strongly seasonal). This is the first time the gate has
failed with the frozen constant already applied; at RNO in F89 it failed
before a constant existed, and F90's constant fixed it. The session did not
choose. Options the owner might weigh, none started:
- stop KSFO and choose another airport under D67.2's offset rule;
- go ahead with the recipe unchanged, recording the gate failure as a
  caveat. The bar compares against the same elevation-adjusted GRIB value,
  so the tests stay internally consistent; but the gate exists to confirm
  the GRIB input is sound;
- first investigate (for example, the land mask of the four GRIB points),
  descriptively and before 2024-08-01 only, and decide after.
Any change to the recipe itself would be a new method, not SPEC 8.
