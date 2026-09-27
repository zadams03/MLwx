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

## 2026-09-27 — Session 79 decision: the owner's verdict on F119 (KSFO)

**D71. Owner decision, planning chat (after session 78): F119 is accepted
as a PASS. KSFO passes the frozen bar (SPEC 5.3) under the unchanged
`B+D,L,R,T` recipe (SPEC 8), on both of its pre-registered looks.** Written
at the start of session 79, before any SPEC or RESULTS edit. No data was
read and no model was fit to make it.

- **D71.1 Verdict.** PASS, as pre-registered ("pass in both years",
  D70.8). Both looks are spent and will not be repeated (F119.5). With
  KSFO's two held-out years (2024-08-01..2026-07-31) now used, no
  untouched held-out year remains at any of the six airports.
- **D71.2 Headline.** The number to lead with is look A's margin over raw
  GFS (GRIB): 1.2576 vs 1.4263 °C, +11.83% (F119.3). It is the smallest of
  the four bar margins. Look B's +20.16% over raw GFS is always quoted
  with D71.3.
- **D71.3 Look B's raw-GFS year.** Look B's raw GFS (GRIB) MAE, 1.7321 °C,
  is well above look A's (1.4263) and both rehearsal folds' (1.4423 and
  1.3061, F118.5). In look B, persistence (1.7172) edges raw GFS, so
  persistence is the binding half of the bar there: margin 0.3342 °C
  (+19.46%), against 0.3491 °C (+20.16%) over raw GFS (F119.3).
- **D71.4 KSFO's bias is not stable from year to year.** The mean-bias
  reference is worse than raw GFS (GRIB) in both looks (A 1.5000 vs
  1.4263; B 1.7747 vs 1.7321; F119.3). In rehearsal it beat raw GFS on
  both folds (1.3833 vs 1.4423; 1.2500 vs 1.3061; F118.5). The two
  training means in F119.3 (look A +0.3638 °C over 1,223 rows; look B
  +0.1847 °C over 1,587 rows; D70.3) imply a 2024-25 mean(obs − raw GFS)
  of about −0.42 °C, against about +0.36 °C before it. This is arithmetic
  on recorded values, not a new score. `B+D,L,R,T` still beat raw GFS in
  both looks. This is read as insight only: nothing is selected, tuned or
  changed on it.
- **D71.5 Framing (D70.9), carried by every write-up.** KSFO's result is
  for the recipe at a sea-mixed grid point (37.5% sea weight, F117.3). It
  is not directly comparable with the five earlier airports, whose
  reproduction gates passed. KSFO's gate is recorded as failed, explained
  by a difference between the sources (D69). Look B's training includes
  2024-25, by design (D70.3). KSFO's margins are not added to F109's
  five-airport table or to its airport-averaged secondary read (+6.02%).
- **D71.6 Number of looks (SPEC wording).** The five earlier airports each
  had one look per method. KSFO had two, pre-registered, each judged
  separately (D67.3, D70.3, D70.4). SPEC now states the general rule: a
  new airport's number of looks, their windows, and how their verdicts
  combine are fixed in writing in its lock, before any of its held-out
  values are read. When an airport has more than one look, it passes only
  if every look passes; anything else is recorded as a split or a fail
  (as D70.4 did for KSFO). This records existing practice. It changes no
  earlier result.
- **D71.7 Q30 order (D66.1).** The further-airport step is done (KSFO).
  Next is the dedicated roadmap planning session. Pooling and the 2026-27
  forward test stay deferred (D66.2, D67.8, D69.6).
- **D71.8 GFS v17 (planning-chat research, 2026-09-27, not checked by this
  session).** The NWS notice list still shows no GFS v17 Service Change
  Notice. The latest SCN is still SCN26-87 (22 Sep 2026).
- **D71.9 Session 79 plan.** Record D71; fold KSFO into SPEC and RESULTS;
  fix the session-77 review items B1–B5, C1–C3 and E1; record the edits
  as F120; archive D67, D69, D70 and F115–F119.

---

## 2026-09-27 — Session 79 finding: what changed in SPEC.md, RESULTS.md and CLAUDE.md

**F120. Documentation only. What changed in SPEC.md, RESULTS.md and
CLAUDE.md in session 79.** KSFO's result (F119, D71) is folded into SPEC
and RESULTS. The session-77 review items B1–B5, C1–C3 and E1
(`notes/session-77-review.txt`, section 4) are settled. No data was read,
no script was run, no model was fit and nothing was scored. Every number
written is copied from F118, F119, D70, D71 or SPEC as it stood. Full
output: `notes/session-79-output.txt`.

**F120.1 Step 0.**
- `git status --porcelain` showed only `?? docs/session-79.md`.
- SHA-256, both equal to F119.4:
  - `data/processed/session78_ksfo_looks_grid.csv`:
    `48c9ceb740146cd1b9ea6d4b3d4da4c719dd4b4852043725c56f506717fb166c`
  - `data/processed/session78_ksfo_looks_predictions.csv`:
    `b4b46adc266ecb5475f253e5b20d02c6505d02af2bd578426095d6ef7f8ad78e`
  These two reads were of bytes only. No other file under `data/` was
  opened.
- D66, D67, D69, D70, F118 and F119 were read in DECISIONS.md, and
  section 4 of `notes/session-77-review.txt` (B1–B5, C1–C4, E1).

**F120.2 Step 1 arithmetic** (recorded values only: training means from
F119.3, counts from D70.3):
`(1587 × 0.1846862003780719 − 1223 × 0.36381439084219136) / 364`
= −0.41716483516483505, **−0.4172** at 4 dp. It matches. D71 was then
appended verbatim, before any SPEC or RESULTS edit.

**F120.3 SPEC.md edits.**
1. **SPEC 1, paragraph 3 (B1).** "judged once on that airport's own test
   year" → each airport is judged on its own held-out data: one look at
   each of the five earlier airports, two pre-registered looks at KSFO,
   and, for any later airport, whatever looks its lock fixes in writing
   before any held-out value is read (5.0).
2. **SPEC 1, KSFO bullet (A1).** "rehearsed and locked ...; not yet
   tested" → "passes the selected-features method on both of its
   pre-registered looks (DECISIONS F119, D71) — see section 8". The
   coastal-airport and gate sentences are kept. A pointer to the D71.5
   framing is added.
3. **SPEC 3.4 airport table, SFO's stage cell (A2; settles C4).** "2 —
   locked, not yet tested" → "2 — passed (selected-features method)".
4. **SPEC 4.3 (B3).** "its own sealed test year, judged once" → its own
   held-out data, looked at only as 5.0 sets out (one look at the five
   earlier airports, two at KSFO, D67.3; a later airport's lock fixes its
   own). The rehearsal paragraph gains: KSFO's rehearsal used the `2022-23`
   and `2023-24` folds of D51's `EXPERIMENT_FOLDS`, because 2024-25 was
   one of its looks (D67.4).
5. **SPEC 5.0 (B2).** The bullets "one look at its own sealed test year"
   and "judged once per airport" are rewritten: one look at each of the
   five earlier airports; two pre-registered looks at KSFO, each judged
   separately (D67.3, D70.3, D70.4); for a later airport, the number of
   looks, their windows and how their verdicts combine are fixed in
   writing in its lock before any held-out value is read (D71.6); the bar
   is judged once per look. **D71.6's combining rule is stated here,
   once:** with more than one look, an airport passes only if every look
   passes; anything else is recorded as a split or a fail. It records
   existing practice and changes no earlier result. It was placed in 5.0
   (scope), not 5.3 (the bar), so the bar's own text is unchanged.
6. **SPEC 5.2 (C3).** The reason the unadjusted-GRIB margins cannot be
   measured is now scoped to the five earlier airports. Added: at KSFO no
   unadjusted rung was registered in its lock (D70), so it was not
   measured there either.
7. **SPEC 6, KSFO bullet (A3).** Heading "— locked, not yet tested" →
   "— passed (selected-features method)". "Its two looks run once, in
   session 78" → both looks were run once in session 78 and both pass
   (F119); the owner accepted it as a PASS (D71); the headline is look A's
   margin over raw GFS (GRIB), 1.2576 vs 1.4263 °C, +11.83%. The rest is
   kept.
8. **SPEC 6, "Further airports" bullet (B4).** "... lock, test once" →
   "... lock, test", and the lock fixes in writing how many looks there
   are, their windows and how their verdicts combine, before any held-out
   value is read; each look is run once (5.0, D71.6).
9. **SPEC 7 intro (C1).** "passed at every airport" → "passed at every one
   of this section's five airports (EGLC, LFPG, DSM, YSDU and RNO)", plus:
   KSFO was added later and judged under section 8 only (8.5).
10. **SPEC 7.2, elevation correction (C2).** "negligible at four airports"
    → "negligible at four of this section's five airports", plus: at
    KSFO, added later under section 8, the gap is 93.47 m (3.4).
11. **SPEC 8.5 (A4).** New block "KSFO (added later; DECISIONS F119,
    D71)", after the five-airport paragraphs: the two-look design; a
    two-row table (look A 2024-25, look B 2025-26: n test, raw GFS (GRIB),
    persistence, B, B+D,L,R,T, and % vs raw GFS, persistence and B), all
    at 4 dp as F119.3; the day basis (persistence on 363 of 364 days in
    look A, 365 of 365 in look B); both looks pass; the overall reading is
    PASS as pre-registered; the band read (D70.5) holds in both looks
    (0.0958 and 0.0824 °C against 0.0377). It says plainly that these rows
    are not part of the five-airport table or its +6.02% average.
12. **SPEC 8.6 (A5).** Heading "(DECISIONS D59.3)" → "(DECISIONS D59.3;
    (f) from D71)". New caveat **(f)** carrying D71.2–D71.5 in brief: the
    headline is look A's +11.83%; look B's raw-GFS year was unusually poor
    and persistence bound there; KSFO's mean bias changed sign between
    years (insight only); the sea-mixed grid-point framing; look B's
    training includes 2024-25.
13. **SPEC 8.7 (B5).** "its own lock and single test (6)" → its own lock
    and its own test, with its looks fixed in writing in that lock before
    any held-out value is read (5.0, 6; D71.6). Added: KSFO, the first
    airport run under this recipe after F109, had two pre-registered looks
    and passed both (8.5; F119, D71).

**Item D (other stale lines).** SPEC lines that still called KSFO
"locked" or "not yet tested": SPEC 1's KSFO bullet, SPEC 3.4's SFO stage
cell, and SPEC 6's KSFO heading. All three are covered by items 2, 3 and
7 above. No SPEC line said no untouched held-out year remains "at the
five airports", so no line needed changing for that.

**F120.4 RESULTS.md edits.**
1. **Intro.** "revised after session 79" added to the revision line. Two
   sentences added: a sixth airport, KSFO, has since passed the
   selected-features method on two pre-registered looks (F119, D71); the
   result is for the recipe at a sea-mixed grid point and is not directly
   comparable with the five earlier airports; see section 6.5.
2. **Section 6.4, closing sentence** (consistent with D71.6). "its own
   lock and single test (SPEC 6)" → its own lock and its own test, with
   its looks fixed in writing in that lock before any held-out value is
   read (SPEC 5.0, 6; D71.6).
3. **New section 6.5, "A sixth airport: San Francisco (KSFO)".** Why KSFO
   (D66.1, D67.1, D59.5); the gate failure and the owner's decision (F116,
   F117, D69); the rehearsal and lock (D67.4, F118, F118.7, D70); the
   two-look design (D67.3, D70.3); the result table (as SPEC 8.5's KSFO
   block, F119.3); both looks pass (D70.8, F119, D71.1, D70.5); the
   headline (D71.2); D71.3 and D71.4 stated plainly (with F118.5 and
   F119.3); the D71.5 framing. Every number is cited.
4. **Section 7, "no untouched year" bullet.** Added: KSFO's two held-out
   years (2024-08-01 to 2026-07-31) are now also used (section 6.5,
   D71.1), so no untouched held-out year remains at any of the six
   airports.
5. **Section 7, last bullet.** Renamed "Parked directions, and the current
   position". It now states: the owner's order is D66.1; Q33 was measured
   (F115); the further-airport step is done (KSFO, D71.7); the next step
   is a roadmap planning session; pooling and 2026-27 stay deferred, the
   forward test until the GFS v17 date is known (D66.2). Removed: "None of
   the three has begun" and "not yet a decision", and the D59.5 branch
   list they belonged to.
6. **Footer.** "and revised after session 79 (DECISIONS F120)" added.

**F120.5 CLAUDE.md edit (E1).** The body of "Commit discipline" is
replaced with the text the session prompt gave: Claude Code does not write
a commit message; the planning chat writes it to `docs/commit-NN.txt`, and
the owner commits with `git commit -F docs/commit-NN.txt`. Nothing else in
CLAUDE.md changed.

**F120.6 Archive.** Moved to DECISIONS-archive.md, verbatim, under "Moved
by session 79 (2026-09-27)": **F115, D67, F116, F117, D69, F118, D70 and
F119**, each with its dated heading. They are one contiguous block in
DECISIONS.md (the file order is F115, D67, F116, F117, D69, F118, D70,
F119). Each is settled: F115 answered Q33 and its one live use (the KSFO
pre-registration, D67.5) is done; D67, D69 and D70 are carried out and
their result is recorded (F119, D71); F116–F119 are now codified in SPEC
(3.3, 3.4, 5.2, 6, 7.3, 8.5, 8.6) and RESULTS (6.5). STATUS.md's "Next"
and the live open questions (Q30, Q32) cite none of them word for word.
**D66, D71 and F120 stay live.** No pointer is left in DECISIONS.md, as in
sessions 77 and 78's practice.

**F120.7 What this did not do.**
- It read no data (Step 0's SHA-256 check read bytes only), ran no
  project script, fit no model and scored nothing.
- It changed no stage status in SPEC 6 (stage 2 stays "IN PROGRESS";
  stages 3–6 are unchanged).
- It changed no earlier verdict or figure. F16, F30, F47, F64, F82, F94
  and F109 and their tables stand.
- KSFO's margins were not added to F109's five-airport table or to its
  airport-averaged +6.02% read.
- It did not edit README.md, PROJECT-INSTRUCTIONS.md, any script, or
  anything under `data/`.
- It wrote no commit message file. Nothing was committed.

**F120.8 Corrections at owner review (same session, before commit).**
Documentation only, same scope guard. No new number. Each settles an item
the session-79 consistency check reported.
1. **SPEC 5.3.** "the bar is applied once per airport (5.0)" → "once per
   look (5.0)". A scope note is added: the test period named in 5.3 is the
   sealed year used by the minimal and richer methods; the
   selected-features method's confirmation year and KSFO's looks are set
   out in 8.3 and 8.5. The bar's meaning is unchanged.
2. **SPEC 6, stage 2 line.** "each judged on its own sealed test year" →
   "each judged on its own held-out data, in the look or looks its lock
   fixes (5.0)".
3. **SPEC 8.2, R.** "the lead-26 airports (YSDU, RNO)" → "(YSDU, RNO and
   KSFO; DECISIONS F116.1, D67.1)".
4. **SPEC 8.6(a).** "the same single-look discipline every method in this
   project uses (5.3)" → one look per airport, the same discipline the five
   earlier airports' tests followed under every method (5.0, 5.3); KSFO,
   under this same method, had two pre-registered looks (5.0, caveat (f)).
5. **RESULTS §7, second bullet heading.** "Each method rests on one year —
   and, together, no untouched year now remains." → "At the five earlier
   airports each method rests on one year; KSFO had two looks — and,
   together, no untouched year now remains at any of the six airports."
6. **STATUS.md, GFS v17 item.** "The earliest possible go-live is late
   October 2026 (D69.6)" added back.
7. **STATUS.md, carried items.** New item: DECISIONS-archive.md's header
   still says a pointer is left in DECISIONS.md for each moved section;
   sessions 77–79 left none. Owner to decide which to keep.
Nothing was committed and no commit message was written.
