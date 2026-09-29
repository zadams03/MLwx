# DECISIONS.md — the project's memory of *why*

This is an **append-only** log. Add new entries at the bottom. Never delete
or rewrite old entries. Each entry is dated.

It records choices made, why they were made, open questions, and findings.

---

[D1–D12, the founding decisions from initial project planning — project scope, location, data sources, split dates, model type — archived verbatim to DECISIONS-archive.md. Settled and now codified as active SPEC rules (D1→§1, D3→§3.1, D4→§2.1b, D5/D8→§3.2, D7→§4.3/D13, D9→§4.1, D10→§5, D11→§2.2, D12→§4.4). Full text preserved there and in git.]

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

## 2026-09-27 — Session 80 decision: the roadmap (owner, planning chat)

**D72. Owner decision, dedicated roadmap planning session (after session
79; D66.1, D71.7). The project's roadmap from here to its end goal.**
Written at the start of session 80, before any other edit. No data was
read and no model was fit to make it.

- **D72.1 End goal.** A private, live daily tool showing corrected
  day-ahead temperature forecasts for ten or more airports: an hourly
  temperature curve and the daily maximum, at 24-hour and 48-hour leads;
  a choice of which weather model is corrected, plus a blend; and
  probabilistic ranges. It is a private product built with good
  academic practice, not a published study.
- **D72.2 Guiding rules.**
  - (a) **Claims vs build choices.** A claim is a stated result (for
    example, "beats raw GFS by X%"). A claim needs a test on held-out data
    that nothing else has used, fixed in writing first, with one look. A
    build choice is how the product is made (inputs, settings, how models
    are blended). A build choice is made by time-ordered cross-validation
    on data not held out for any claim. It spends no held-out data and is
    never quoted as a result. Build choices are made identically at every
    airport; per-airport selection is still not allowed. Held out for
    claims, and so never used for build choices: a pre-registered test's
    data until that test is run; 2026-27 or later data until its
    pre-registered test is scored; a new airport's held-out years until
    its looks are run. Once any part of a forward year has been scored,
    no new test may be pre-registered on that year.
  - (b) **One new method on one well-understood input first,** then add
    inputs. Inputs are chosen on the real target (the full curve), not on
    one hour.
  - (c) **Adding an airport should be easy:** one script plus a
    checklist, from stage G. The script downloads the new airport's
    history from each source's archive. The rigour steps (verify, lock,
    looks) stay, as a template.
  - (d) **Licensing.** The tool is private: not sold and not shared. Data
    licences are therefore not a constraint. Revisit if that changes.
- **D72.3 Stages, in order.** A and B run side by side, because both are
  time-critical.
  - **A — Benchmark and source probe.** Confidence intervals for results
    on record (SPEC 5.4). A comparison against operational post-processed
    forecasts (NWS MOS and the National Blend of Models, NBM) at DSM, RNO
    and SFO. A read-only probe of each other source (ECMWF, ICON,
    WeatherNext, NBM, GEFS): archive depth, live feed, and which fields
    it offers. Also: whether GFS v17 retrospective runs are public.
  - **B — Forward test and data collection.** Pre-register the 2026-27
    forward test (D72.5). For any source the probe finds has no
    downloadable archive, start saving its daily forecasts (all hours,
    both leads); where to save is decided then (D72.8).
  - **C — Widen the target, on GFS only.** Hourly curve, daily maximum,
    48-hour lead. Written with the weather model as a setting.
  - **D — Correct each other weather model on its own,** on the full
    curve.
  - **E — Blend and stack.** Combine the corrected models, with NBM as an
    input where it exists. Chooses which inputs go forward.
  - **F — Upgrade policy.** What happens when any weather model changes
    version, starting with GFS v17.
  - **G — Live product, version 1.** Daily pipeline, a prediction log that
    is never edited, a simple display, one-script airport onboarding.
  - **H — Probabilistic forecasts.** Ranges with stated odds, judged
    against their own bar, fixed before running.
  - **Ongoing — new airports,** added in batches. Each batch can also
    serve as a stage's claim test.
  - **Conditional — pooling** (combining airports into one model). Opened
    only if the number of airports makes it worthwhile.
- **D72.4 Where claims are judged.**
  - 2026-27 forward year: the GFS recipe on a new year, and whether it
    survives GFS v17 (D72.5).
  - New airports (two unseen years each): the multi-model product.
  - 2027-28 forward year, pre-registered before 2027-08-01: the live
    product as a whole.
  - Spent years at the six airports: other weather models, labelled a
    weaker "spent-year test" (D72.6).
- **D72.5 The 2026-27 forward test (design; locked in session 81).** GFS
  only. Model: SPEC 8's `B+D,L,R,T`, retrained once on all GFS v16 data up
  to 2026-07-31, then frozen, with its file's SHA-256 recorded. All six
  airports. Bar: SPEC 5.3 (beat raw GFS and persistence on MAE). The year
  splits at the GFS v17 go-live date. Period A (2026-08-01 to go-live, v16
  inputs) and period B (go-live to 2027-07-31, v17 inputs, v16-trained
  model) are each judged separately against the same bar. Each gets a
  verdict whatever its length, labelled with its dates and season. No
  2026-27 value is scored until its period ends. For v17, only file paths
  in the fetch code may change. The pre-registration names the two tracked
  DSM files for 2026-08-05..2026-08-15 (D62.7, A67-15). This test does not
  wait for more weather models.
- **D72.6 Other weather models at the six airports.** Allowed as a claim
  test, labelled a "spent-year test" and weaker evidence: the years were
  already used for GFS, and other models' errors partly overlap GFS's.
  The recipe is applied unchanged, the test is pre-registered, and there
  is one look per model. It may use only years that model's build choices
  did not use. Headline product claims come from forward years or new
  airports.
- **D72.7 Stage A's gate.** Before the NBM/MOS comparison is looked at,
  its outcome rule is fixed in writing. If we beat NBM/MOS: carry on. If
  we lose: record how close we got, and consider stacking (NBM as an
  input) and/or a non-US focus. The comparison is run even if we lose. It
  decides direction only; it changes no earlier verdict.
- **D72.8 Known risks and their mitigations.**
  - Stage D could be costly on the full curve: screen each model at a few
    hours by cross-validation first; only models that earn their place
    get the full curve.
  - Other models may not offer the fields SPEC 8's extra features use:
    stage A's probe records which fields each model offers.
  - A source with no downloadable archive gives new airports no history.
    New airports normally get their history by download (D72.2(c)). Only
    for a source the probe finds has no downloadable archive does stage B
    decide how to save it: at a list of candidate airports, the whole
    map, or not at all (new airports then start that source with no
    history).
  - Stage C's claim needs clean new airports: they are chosen before C's
    lock and are not scored before it.
  - Stage A's comparison is at one hour: it is re-run on the full curve
    in stage C, as a description only.
  - If period B shows GFS v17 badly hurts the correction, stage F may move
    earlier.
- **D72.9 Closed and parked.**
  - Q30 is closed. This roadmap replaces it.
  - Q32 is closed. Terrain-hard airports use the default recipe (SPEC
    8.7); Reno passes under it (F94, F109).
  - P1 (direction) is settled by this roadmap. P2 (WeatherNext) is in
    stages A, D and E; its ensemble-spread idea is in H. P3 (harder bars)
    is stage A.
  - A terrain descriptor (RESULTS §7) is parked.
  - DECISIONS-archive.md's header is amended to match practice since
    session 77: no pointer is left in DECISIONS.md for a moved entry.
- **D72.10 The former SPEC 6 stages.** Stage 1 is done. Stage 2
  (individual airports) continues as the ongoing new-airports track.
  Former stage 3 (pooling) is the conditional step. Former stage 4 (add
  models and blend) is stages D and E. Former stage 5 (widen the target,
  and the 48-hour lead) is stage C. Former stage 6 (live product) is
  stage G.
- **D72.11 GFS v17 (planning-chat web search, 2026-09-27, not checked by
  this session).** No GFS v17 Service Change Notice was found; only the
  April 2026 proposals (PNS 26-29, 26-30). Re-check at each planning
  session.
- **D72.12 PROJECT-INSTRUCTIONS.md.** The planning chat's operating guide
  is now tracked in the repo root (committed by the owner before session
  80). Claude Code does not follow it; it follows CLAUDE.md, and edits
  PROJECT-INSTRUCTIONS.md only when a session prompt says exactly what to
  change.
- **D72.13 Session plan.** 80: record this roadmap (this session). 81:
  pre-register the 2026-27 forward test, and train and freeze its model.
  82: stage A's read-only source probe. 83: start daily collection, for
  any source without a downloadable archive. Then stage A's benchmark,
  then stage C onward.

---

## 2026-09-27 — Session 81 decision: pre-registration of the 2026-27 GFS forward test (owner, planning chat)

**D73. Owner decision, planning chat (after session 80): the
pre-registration of the 2026-27 GFS forward test (D72.5).** Written at the
start of session 81, before any data was read or any model was fit. No
2026-27 value has been read or scored. Where this entry is more precise
than D72.5, this entry governs; D73.4 amends D72.5's "only file paths may
change".

- **D73.1 What is tested.** SPEC 8's recipe `B+D,L,R,T`, unchanged: the
  same features and transforms (SPEC 8.1), the same column order (SPEC
  8.8 G15), the same frozen LightGBM settings (D21.4/D48.6, lightgbm
  4.7.0, SPEC 8.8 G14, G17), the same target (observation minus
  `temperature_grib_c`, SPEC 8.8 G20). Six airports: EGLC, LFPG, DSM,
  YSDU, RNO and KSFO, each with its own grid point, target hour, lead and
  elevation constant (SPEC 3.4, 4.1, 5.2, 7.2).
- **D73.2 The frozen models.** One `B+D,L,R,T` model per airport, trained
  once on every complete-case row dated 2021-03-24 to 2026-07-31 (all
  GFS v16), in ascending date order (G19), from committed processed files
  only. It is saved as a LightGBM text model file and its SHA-256 is
  recorded in F122. It is never refit. Also frozen, as descriptive rungs
  only: one plain `B` model per airport, trained the same way on the same
  rows; and one mean-bias constant per airport, mean(observation minus
  raw GFS (GRIB)) over the same rows. The training rows keep the
  historical observation pairing (SPEC 4.5's note); new 2026-27 code
  pairs explicitly to the nearest report (SPEC 8.7).
- **D73.3 The test year and its split.** The test year is 2026-08-01 to
  2027-07-31. A target day is in period B if the GFS cycle that forecasts
  it (SPEC 7.2's lead convention) is an operational GFS v17 cycle, and in
  period A otherwise. Any v16.x cycle is period A. The boundary is the
  first operational v17 cycle, taken from NCEP's Service Change Notice and
  confirmed in the archive. Parallel ("para") data is never used. If no
  operational v17 cycle has forecast any day by 2027-07-31, period A is
  the whole year and period B is not run. If anything other than one
  clean switch happens (a rollback, a second version change, mixed
  cycles), stop: the owner decides in writing before any value is scored.
- **D73.4 Inputs after v17 (amends D72.5).** 2026-27 features are built
  with the same logic as the record pipelines, with only their date
  ranges extended (as F107 did for the reserved year); the code itself is
  new (D73.8). For v17 inputs, file paths may change. How a field is
  fetched (message name, level specification, which accumulation window
  is read) may also change, but only if the physical quantity is
  identical: the same variable, level, time window ending at the target
  hour, units and transform. The owner approves each such change. It is
  decided from v17's documentation and the fields themselves, never from
  any 2026-27 error or score. Each change is written into DECISIONS, with
  its evidence, before any period-B value is scored. If any input to `B+D,L,R,T` or to raw GFS
  (GRIB) cannot be built this way, or the 0.25° GRIB2 grid is no longer
  offered, period B is recorded as void (not run). A void period is not
  a fail. The elevation constants (SPEC 5.2) stay frozen, even though
  v17's terrain differs; they apply to raw GFS and the model alike. The
  grid points (SPEC 3.4) and interpolation (SPEC 8.8 G6) are unchanged.
  Nothing is refit, retuned or reselected.
- **D73.5 The bar and the rungs.** The bar is SPEC 5.3, applied per
  airport per period: the frozen `B+D,L,R,T` model's MAE must be lower
  than both raw GFS (GRIB, elevation-adjusted, SPEC 5.2) and persistence.
  Descriptive rungs, never part of the bar: the frozen `B` model and the
  mean-bias reference. The day basis is SPEC 8.5's: raw GFS and the
  models on every complete-case test day; persistence on test days that
  also have a previous-day observation. Missing forecasts or observations
  are dropped and counted (SPEC 2.2). There is no minimum day count. Each
  period's row count is reported against its full expected count; a
  shortfall is reported and does not block the verdict.
- **D73.6 Verdicts.** Each airport gets one PASS or FAIL per period,
  labelled with the period's dates and season. The two periods answer
  different questions (A: does the recipe hold on a new year; B: does the
  v16-trained model survive v17), so they are not combined, and D71.6's
  every-look-must-pass rule does not apply. Nothing is averaged across
  airports (SPEC 5.0). KSFO carries D71.5's framing. The write-up leads,
  in each period, with the smallest bar margin across the six airports.
  No earlier verdict changes.
- **D73.7 Expectations, stated before any value is seen.** Period A:
  `B+D,L,R,T` passes at all six airports. Period B: no expectation is
  stated. Period A will probably be short (a few months of autumn); its
  verdict stands whatever its length, labelled with its dates and season.
- **D73.8 When it is scored.** No 2026-27 value (model prediction error,
  raw-GFS error or persistence error) is computed until its period has
  ended and its observations are in. **Hold rule:** period A is not
  scored until the owner has decided, in writing, whether to pre-register
  a comparison against NBM/NWS MOS on 2026-27 (stage A, D72.7). Once any
  part of 2026-27 is scored, no new test may be pre-registered on it
  (SPEC 2.5). The 2026-27 data-build and scoring scripts are written in a
  later session and committed before any 2026-27 row is built. They
  implement this entry exactly, and SPEC 8.7's build requirements apply
  to them. Until each period is scored, its data is held out for claims
  and no build choice may use it (SPEC 2.5).
- **D73.9 A consequence, accepted.** Period B's data is held out until it
  is scored, after 2027-07-31. So stage F (upgrade policy) cannot use
  live v17 data for any build choice before then without spending period
  B. Before then, its only v17 training data would be NOAA's v17
  retrospective runs, if they are public (D72.3). The design is not
  changed for this.
- **D73.10 The two DSM A67-15 files** (D62.7): the two tracked DSM files
  for 2026-08-05..2026-08-15. Their paths and SHA-256 are recorded in
  F122. They were not opened in session 81. They are not used to build
  or score anything; period A's data is fetched fresh.
- **D73.11 Session 81's plan.** Record this entry; build the training set
  from committed files; pass a reproduction gate (the new training code
  must reproduce F109's and KSFO look B's recorded MAEs exactly); train
  and freeze the models; record F122.
- **D73.12 GFS v17 (planning-chat web search, 2026-09-27, not checked by
  this session).** Still no Service Change Notice; only the April 2026
  proposals (PNS 26-29, 26-30). The SCN is due 30 days before go-live, so
  the earliest go-live is about late October 2026.

---

## 2026-09-27 — Session 81 finding: the 2026-27 forward test's frozen models

**F122. Offline. The training set for the 2026-27 GFS forward test (D73)
was built from committed files only; the new training code passed the
reproduction gate (all twelve recorded MAEs equal at full precision); and
one `B+D,L,R,T` model, one plain `B` model and one mean-bias constant were
trained and frozen per airport, on every row dated 2021-03-24..2026-07-31.
No 2026-27 value was read. Script: `scripts/session81_freeze_forward_models.py`
(new; modes `--build`, `--gate`, `--freeze`, each run once). Full real
output: `notes/session-81-output.txt`.**

**F122.1 Step 0.**
- `git status --porcelain` showed only `?? docs/session-81.md`.
- `data/models/session81/` did not exist. No file named `session81_*`
  existed under `scripts/`, `data/processed/` or `notes/`.
- Read: D62 (D62.7), D71, D72 and F121 in DECISIONS.md; D58, F107, F109,
  D70 and F119 in DECISIONS-archive.md.
- **The two A67-15 DSM files** (D62.7, D73.10), identified from
  `notes/audit-session-67.md` (A67-15 names exactly these two) and
  `git ls-files`. Not opened; path listing and SHA-256 of bytes only.

| path | size (bytes) | SHA-256 | added by commit |
|---|---|---|---|
| `data/raw/openmeteo_previousruns_gfs_global_DSM_2026-08-05_2026-08-15_q27compare.json` | 6630 | `056f251da567acd63ad3008df3a9b8db59b406d1502ae479f7d3ad416b0894ad` | `11de6f54b7d71448642f65415304fa28ea7ba336` |
| `data/raw/openmeteo_previousruns_gfs_seamless_DSM_2026-08-05_2026-08-15_q27compare.json` | 6629 | `3e1aa911cfbffd7918955b7aee1c85f94206c67e95789b9ecfb25d67fea42d99` | `11de6f54b7d71448642f65415304fa28ea7ba336` |

  Each has a tracked `.meta.txt` sidecar (the pull date and query, SPEC
  2.3), added by the same commit and also not opened:
  `..._gfs_global_..._q27compare.json.meta.txt` (1815 bytes,
  `9a433aa82f23a8c04c93cb9e33af296b53d7843daa5b1ae008551347e9bd3eb3`) and
  `..._gfs_seamless_..._q27compare.json.meta.txt` (1821 bytes,
  `ac33a3fad24fa4106417966950296b470c731c44fa99b51c49decdee75ae2ee4`).
  They are listed here for completeness; A67-15 names the two data files.

**F122.2 Step 1.** D73 was appended to DECISIONS.md under its dated
heading, before any other edit and before any data was read. Its text was
copied mechanically (`sed`) from `docs/session-81.md` lines 77–178 and
checked byte-equal with `diff`.

**F122.3 Step 2: the training set (`--build`).**
- Five earlier airports: the `B` files (`grib_features_v16_window.csv`,
  `grib_features_sealed_window.csv`), the L, D, T, R v16-window,
  sealed-window and reserved-year files (sessions 49, 51, 53, 55, 63;
  SPEC 8.1, F107), and the IEM routine observation chunks, with the
  record script's loading, complete-case and pairing logic (the
  historical pairing, SPEC 4.5's note; D73.2). Added (SPEC 8.7 item 2): a
  blank or non-finite value is rejected at load and counted.
- KSFO: `session76_ksfo_features.csv` and `session76_ksfo_observations.csv`,
  joined as `session77_ksfo_looks.py` does. SHA-256 both equal D70.2
  (`f228301e…c5e9`, `b987dd4f…736c`).
- D's floor transform (SPEC 8.1) applied; complete-case rule (SPEC 8.3).
- The record script's SHA-256 was checked against D70.2
  (`9f8af9af…80b4`) before it was imported, read-only, for `LGB_PARAMS`,
  the G15 column names and `year_fraction`. Every input file's SHA-256 is
  in the output file.
- The script stops on any row dated 2026-08-01 or later in any input or in
  the training set. It did not trip.

| airport | rows | first | last | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 | dup. dates | non-finite rejected | complete-case dropped | no paired obs. dropped | calendar days with no row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EGLC | 1953 | 2021-03-24 | 2026-07-31 | 130 | 365 | 364 | 366 | 364 | 364 | 0 | 0 | 0 | 3 | 3 |
| LFPG | 1953 | 2021-03-24 | 2026-07-31 | 130 | 363 | 365 | 366 | 365 | 364 | 0 | 0 | 0 | 3 | 3 |
| DSM | 1955 | 2021-03-24 | 2026-07-31 | 130 | 365 | 364 | 366 | 365 | 365 | 0 | 0 | 0 | 0 | 1 |
| YSDU | 1929 | 2021-03-24 | 2026-07-31 | 130 | 363 | 357 | 363 | 360 | 356 | 0 | 0 | 0 | 26 | 27 |
| RNO | 1952 | 2021-03-24 | 2026-07-31 | 128 | 365 | 364 | 365 | 365 | 365 | 0 | 0 | 0 | 3 | 4 |
| KSFO (SFO) | 1952 | 2021-03-24 | 2026-07-31 | 130 | 364 | 364 | 365 | 364 | 365 | 0 | 0 | 0 | 3 | 4 |

Years are Aug–Jul; "2020-21" is 2021-03-24..2021-07-31. The window has
1,956 calendar days. Every last date is on or before 2026-07-31. Days with
no row (listed when 20 or fewer):
- EGLC: 2023-06-11, 2024-08-14, 2025-11-21.
- LFPG: 2022-07-23, 2022-07-25, 2026-07-08.
- DSM: 2022-11-30 (no GRIB row).
- YSDU: 27 days (1 with no GRIB row, 26 with no paired observation); not
  listed.
- RNO: 2021-05-02, 2021-05-03, 2022-11-30, 2024-03-21.
- KSFO: 2022-03-17, 2022-11-30, 2024-07-13, 2024-12-20.
No gap was filled. The station column holds the SPEC 3.4 station code, so
KSFO's rows and model files are named `SFO`.

Saved: `data/processed/session81_training_set.csv`, 11,694 data rows,
SHA-256 `ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a`.
Columns: station, target_date, target_hour, the nine G15 columns,
`temperature_grib_c`, `obs_c`; floats written with `repr`, so they read
back exactly.

**F122.4 Step 3: the reproduction gate (`--gate`). PASSED.** The same fit
code as `--freeze`, with only the dates changed. Verification only; no
verdict. Recorded values from `session63_reserved_confirm_grid.csv` (F109)
and `session78_ksfo_looks_grid.csv` (F119, look B).

| fold | airport | model | train | test | recomputed | recorded | equal |
|---|---|---|---|---|---|---|---|
| F109 | EGLC | B | 1225 | 364 | 1.0860865794631305 | 1.0860865794631305 | yes |
| F109 | EGLC | B+D,L,R,T | 1225 | 364 | 1.0007550363323212 | 1.0007550363323212 | yes |
| F109 | LFPG | B | 1224 | 365 | 1.3284737879871744 | 1.3284737879871744 | yes |
| F109 | LFPG | B+D,L,R,T | 1224 | 365 | 1.2368626165917669 | 1.2368626165917669 | yes |
| F109 | DSM | B | 1225 | 365 | 1.4401546527480342 | 1.4401546527480342 | yes |
| F109 | DSM | B+D,L,R,T | 1225 | 365 | 1.4122847644111458 | 1.4122847644111458 | yes |
| F109 | YSDU | B | 1213 | 360 | 1.3029993377880373 | 1.3029993377880373 | yes |
| F109 | YSDU | B+D,L,R,T | 1213 | 360 | 1.2642703316294652 | 1.2642703316294652 | yes |
| F109 | RNO | B | 1222 | 365 | 1.4271639701054912 | 1.4271639701054912 | yes |
| F109 | RNO | B+D,L,R,T | 1222 | 365 | 1.2741517803385958 | 1.2741517803385958 | yes |
| KSFO look B | SFO | B | 1587 | 365 | 1.4653639395559965 | 1.4653639395559965 | yes |
| KSFO look B | SFO | B+D,L,R,T | 1587 | 365 | 1.3830033790440732 | 1.3830033790440732 | yes |

All twelve equal the record exactly. The row counts equal F109's and
D70.3's.

**F122.5 Step 4: the frozen models (`--freeze`).** Per airport, on all its
F122.3 rows (2021-03-24..2026-07-31, ascending date), fit once:
`B+D,L,R,T` (G15 columns, in order) and `B` (the first five). Settings:
`LGB_PARAMS` (D21.4/D48.6), G14, G17. Saved with the booster's
`save_model` (LightGBM text format) under `data/models/session81/`.
Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.

| airport | rows | `<st>_bdlrt.txt` SHA-256 | `<st>_b.txt` SHA-256 | mean-bias constant (°C) |
|---|---|---|---|---|
| EGLC | 1953 | `d6a85e45cf948107d45601fca71388102128d1172ddedbf83840f6ee82d15110` | `fa299dd54908f7d98211bbd1edf2955e8acb493997564c6b30b174522f23a461` | -0.21434203789042497 |
| LFPG | 1953 | `ed3f90b604c9b48a2a50923fd2a67439b25a21255c77d80ae9ca13789e8c8c8e` | `257c153fec745954f9f2917fe9f4a51d6c8fd662233f5fb5dcb94c2b8b987022` | -0.16713876088069635 |
| DSM | 1955 | `260d6187f8efa4850790528027ee0d3f726a0c4c6b679511bfa891f2de4dff3b` | `e9cb30bacaf38f9a6b0a602cedc3d9bf2fd2b457bf883d5914316b759264fc9c` | -0.29022710997442464 |
| YSDU | 1929 | `12acbb185d5b927014373a0197b3e6e0ba0be206ff4f434e812bc191976613c3` | `6e85d56bcead9111f0198b2842ffca8cc308909cc63eea6b36820ead66614a51` | -0.3155987558320373 |
| RNO | 1952 | `c809ccfe9863741d715e8b7167a172d6826cfe6ea78e47a943779d7a7bcb5819` | `8ce348a6ca583fd3bf203c993f0c10887212e5968cf4d925d05de2b8baf4cb0d` | 0.11086936475409828 |
| KSFO (SFO) | 1952 | `c25da039bfbf99db1fd222b171f93a2ea332aaedd828823ed1e09c4d691125f6` | `2649548311f3e396de933d1a78650fc6df9001719bab97b929e2002c9af42ca3` | 0.02647489754098368 |

The mean-bias constant is mean(`obs_c` − `temperature_grib_c`) over the
same rows, at full precision (D73.2).

- `data/models/session81/manifest.json`, SHA-256
  `03830586c64039814b3d697b414e29ed18a359d9798d87451e8aa3575365c298`. It
  holds, per airport, the training range, row count, mean-bias constant and
  both model files' SHA-256; and the training set's SHA-256, the column
  lists, `LGB_PARAMS` and the Python, numpy and lightgbm versions.
- **Reload check:** each of the twelve saved models, reloaded with
  `lightgbm.Booster(model_file=...)`, predicts its own training rows
  identically to the in-memory model: maximum absolute difference 0.0 in
  all twelve. No error or MAE was computed on the training rows.

**F122.6 What this did not do.**
- It read, pulled or built no row dated 2026-08-01 or later, and made no
  network call. The two A67-15 files were not opened.
- It computed no score except the Step 3 gate, which re-computed recorded
  figures only. No MAE or error on the frozen models' training rows.
- It used only `B+D,L,R,T` and `B`, with the frozen settings. No other
  feature set, setting, seed or column order.
- It changed no earlier verdict or figure.
- It edited no existing script. It wrote no 2026-27 data-build or scoring
  script (D73.8).
- It edited SPEC.md only by one sentence at the end of SPEC 6's stage B
  bullet. It did not edit RESULTS.md, README.md, CLAUDE.md or
  PROJECT-INSTRUCTIONS.md, and wrote nothing under `data/raw/`.
- Nothing was committed and no commit message was written.

---

## 2026-09-28 — Session 82 finding: stage A's source probe

**F123. Stage A's read-only source probe (D72.3, D74.3). Each source was
checked against a fixed checklist: archive, live feed, fields, coverage,
class. Nothing was chosen. Script: `scripts/session82_source_probe.py`
(new; reads the network and prints; writes no data file). Full real output,
with every URL, listing excerpt, decoded message's metadata and the
documentation read: `notes/session-82-output.txt`. All pages and listings
accessed 2026-09-28.**

**F123.1 Steps 0–2.**
- Step 0: `git status --porcelain` showed only `?? docs/session-82.md`. The
  last entries were D73 and F122; no D74 or F123 existed in either
  DECISIONS file; neither new path existed. D72, D73, SPEC 8.1 and the
  archived F85, F88 and F89 were read.
- Step 1: D74 was copied mechanically (`sed`) from `docs/session-82.md`
  lines 72–99 and checked byte-equal with `diff`.
- Step 2: SPEC 4.3's sentence on data after 2026-07-31 was replaced by
  D74.1's text. CLAUDE.md step 3 gained D74.2's sentence.

**F123.2 Summary.** Fields, in order: 2 m temperature / total cloud / 10 m
wind / 2 m dewpoint / 850 hPa temperature / surface or MSL pressure /
downward shortwave at the surface. "y" means yes, "n" means no; a date means
"from that date". Floors were found by listing, and presence after a floor
was not scanned for gaps.

| source, product | earliest genuine run | access | 24 h / 48 h leads, step | fields T2/cloud/wind/Td/T850/p/SW | airports | class | weakest tag |
|---|---|---|---|---|---|---|---|
| ECMWF IFS open data (AWS `ecmwf-forecasts`) | 2023-01-18 (0.4°); 0.25° from 2024-02-01 | anonymous HTTPS/S3 | both, 3-hourly (00/12z to 360 h, 06/18z to 144 h) | y / 2025-11-21 / y / 2024-03-06 / y / y / 2024-03-06 | all six | Shallow (2023-01-18) | verified |
| ECMWF AIFS Single (same bucket) | 2025-02-10 (pre-operational `aifs/` 2024-02-29..2025-02-25, no cloud or SW) | anonymous | both, 6-hourly | y / y / y / y / y / y / y | all six | Shallow (2025-02-10) | verified |
| DWD ICON global (opendata.dwd.de) | none: only the latest run of each cycle is on the server | anonymous HTTPS | both, hourly to 78 h (00/12z to 180 h, 06/18z to 120 h) | y / y / y / y / y / y / y (by folder name; not decoded) | all six | **No archive** (about 24 h) | verified (listing); retention documentation only |
| NOAA GEFS 0.25° `pgrb2s` + 0.5° `pgrb2a` (AWS `noaa-gefs-pds`) | 2017-01-01 (v12 layout from 2020-09-23) | anonymous | both, 3-hourly (0.25° to 240 h) | y / y / y / y / 0.5° only / y / y | all six | Deep | verified |
| Google WeatherNext 3 (and 2) | WN3: 2026, 2024–25 backfill in progress; WN2: 2022 | Google account and request form | WN3 hourly; WN2 6-hourly | WN3 all y; WN2 y / n / y / n / y / y / n | all six | **Blocked** (account and request form) | documentation only |
| NOAA NBM CONUS `core` (AWS `noaa-nbm-grib2-pds`) | 2020-05-18 (`core/` layout from 2020-09-30) | anonymous | both; hourly to 36 h (to 48 h from 2026-05-05), then 3-hourly | y / y / speed y / y / n / n / y | DSM, RNO, KSFO | Deep | verified |
| NWS MOS (IEM archive: GFS, MEX, NAM, LAV, NBS, NBE) | GFS MOS 2003-12-16; LAV, MEX 2020-07-12; NBS/NBE 2020-07-23 | anonymous (third-party archive) | GFS MOS 3-hourly to 60 h, then 66, 72 h | tmp y / sky cover (category) / wsp y / dpt y / n / n / n | DSM, RNO, KSFO | Deep | verified (stations and projections); versions unknown |
| GFS v17 retrospective runs | none found public | — | — | — | — | not classed (none found) | unknown |
| Open-Meteo Previous Runs API (second route) | per model, F123.5 | anonymous | `previous_day1` and `_day2` both present, hourly | all but T850 | all six | Shallow | verified |

**F123.3 Per source.**
- **ECMWF IFS.** 1,344 date folders, 2023-01-18..2026-09-28; 6 missing
  (2023-04-27..05-02). The open-data field set grew inside the archive:
  2 m dewpoint and `ssrd` from 2024-03-06; total cloud cover (`tcc`) only
  from 2025-11-21. So all seven fields exist together only from
  2025-11-21. `ssrd` is accumulated from step 0 (J m⁻², `stepRange` 0-24).
  IFS `tcc` is stored as a fraction (0–1); AIFS `tcc` is in %. Cycle changes
  inside the archive (documentation only): 48r1 2023-06-27, 49r1 about
  Oct 2024, 50r1 with AIFS v2 2026-05-12. Live: data.ecmwf.int lists 4 date
  folders (2026-09-25..28), and the documentation says the last 12 runs are
  kept. The AWS 00z 2026-09-28 files appeared 06:25–07:34 UTC.
- **ECMWF AIFS.** `aifs-single/` from 2025-02-10 under `0p25/experimental/`,
  moved to `0p25/oper/` from 2025-02-26, when the pre-operational `aifs/`
  folder ended. `aifs-ens/` from 2025-07-02. Six-hourly steps only.
- **DWD ICON global.** Icosahedral grid (`icon_global_icosahedral_*`),
  `.grib2.bz2`. Every file on the server is from the current runs
  (2026-09-27 12z to 2026-09-28 06z), so none was decoded (scope). Shortwave
  comes as direct plus diffuse (`aswdir_s`, `aswdifd_s`) and net (`asob_s`);
  their averaging window is unknown. DWD documentation: files are deleted
  after 24 hours, and there is no public long-term archive. A third-party
  Zarr copy (Hugging Face `openclimatefix/dwd-icon-global`, folders
  2023–2025) exists; it is not official and could not be decoded here.
- **GEFS.** 3,558 date folders, 2017-01-01..2026-09-28, none missing;
  31 members plus mean and spread. Cloud and SW are 6-hour averages that
  reset every 6 h (f024 = 18–24 h, f027 = 24–27 h). 850 hPa temperature is
  in the 0.5° files only. The 0.25° field set grew on 2022-10-19 (VIS,
  MSLET, CPOFP, ceiling; no field removed). Versions (documentation only):
  v12.0 2020-09-23; v12.1.2 2021-07-20; v12.3 in 2022; v12.3.18 about
  2026-02-24; v12.3.20 on 2026-06-15, which fixed "errant negative"
  shortwave values by storing DSWRF at 6 rather than 3 significant digits.
  GEFSv13 is planned alongside GFS v17 (documentation only).
- **WeatherNext.** An anonymous listing of `gs://weathernext` returned
  HTTP 403/401. WeatherNext 3 (released August 2026) is now current;
  real-time data is under "experimental terms" and historical data under
  CC BY 4.0. Cost and retention: unknown.
- **NBM.** 2,322 date folders, 2020-05-18..2026-09-28; 3 missing
  (2020-10-23..25); 24 cycles a day; CONUS Lambert grid, 2,345 × 1,597 at
  2.54 km. The CONUS files carry no surface or MSL pressure and no 850 hPa
  temperature. A `global` domain from 2024-05-15 carries upper-air fields
  only (27 messages at f024; no 2 m temperature). The listing dates match
  the documented v4.0 (2020-09-29/30), v4.2 (2024-05-15) and v5.0
  (2026-05-05). v4.3's date disagrees between two NOAA VLab pages
  (2025-04-15 vs 2025-05-27); both are recorded. The v5.0 page notes a
  "temperature adjustment made July 28, 2026".
- **Unknown:** ICON's shortwave window and model versions; the retention of
  WeatherNext and ICON (beyond DWD's 24 h statement); MOS version changes;
  49r1's exact date.

**F123.4 MOS answer.** KDSM, KRNO and KSFO each appear in IEM's archive for
GFS MOS (runs 2021-03-24 and 2026-07-28), MEX, NAM, LAV, NBS and NBE (21,
15, 21, 38, 23 and 21 projections). Each had a `tmp` element. GFS MOS 00z
and 12z projections are 3-hourly (6–60 h, then 66 and 72 h), so they
include DSM's 18:00 UTC target hour (SPEC 3.4). **20:00 UTC (RNO, KSFO) is
not a GFS MOS, NAM MOS or NBS projection** (the nearest are 18:00 and
21:00). LAV is hourly but reaches only about 38 h. MEX and NBE give
12-hourly projections. No forecast value was printed or used. Version
changes inside the archive: unknown.

**F123.5 Open-Meteo second route (EGLC, SPEC 3.4; present/null hour counts
only).**
- `gfs_global`: `temperature_2m_previous_day1` from 2021-03-24 (as SPEC
  3.2); cloud cover from 2024-01-19 (as F85).
- `ecmwf_ifs025`: from 2024-02-04.
- `ecmwf_aifs025_single`: from 2025-02-18.
- `icon_global`: from 2024-01-19. These three models returned grid 51.5,
  0.0, 4 m.
- For each of these four models, the six fields other than 850 hPa
  temperature were present for
  72 of 72 hours at `previous_day1` and `_day2` on 2025-06-10..12. Cloud
  cover shares temperature's floor, except for GFS.
- **`temperature_850hPa_previous_day1` was rejected (HTTP 400) for every
  model**, with the same error F85 recorded for GFS.
- **GEFS has no working route:** `ncep_gefs025` and
  `ncep_hgefs025_ensemble_mean` are accepted but return 0 of 72 hours at
  the anchor. Their printed "floors" are artifacts of the bisection and mean
  nothing. `gfs025_ensemble` was rejected.
- The Historical Forecast API was not used.

**F123.6 GFS v17 answer.** No public GFS v17 retrospective or reforecast
forecast runs were found. Six candidate AWS bucket names returned
`NoSuchBucket`. The NOMADS `gfs/para/` and `gfs/v17.0/` listings returned
HTTP 403. EMC's GFSv17 page links only to verification statistics for
retrospective streams 1a–4. PNS 26-29 says nothing on retrospective data;
it plans C1152 (9 km) and "significant folder directory structure and name
changes". The public `noaa-ufs-gefsv13replay-pds` (1980–2026) is a replay
to ERA5, not forecast runs. So D73.9's condition ("if they are public") is
not met as of 2026-09-28 (unknown, not proven absent).

**F123.7 Lists for session 83.**
- **No archive:** DWD ICON global (official open data; about 24 h
  retention). Its second routes are Open-Meteo from 2024-01-19 and the
  unofficial third-party Zarr copy.
- **Blocked:** Google WeatherNext (all versions): a Google account and an
  approved request form are needed.

**F123.8 Other global models not probed this session:** UK Met Office
global, Environment Canada GDPS, JMA GSM. Recorded only so they stay visible
(D74.3).

**F123.9 Scope notes, reported plainly.**
- Before the script was written, one exploratory MOS request used runtime
  2026-07-31 00z. The response held projections valid 2026-08-01..08-08.
  They sat in memory only; no value was printed, saved or used. The final
  script uses earlier runtimes and stops if any projection is valid after
  2026-07-31.
- The first ECMWF run of the script stopped on a connection reset from a
  throttled server. The retry was widened and the section re-run in full.
  Only the complete run is in the output file.
- Samples decoded: ECMWF 10, GEFS 8, NBM 5, others 0. Every one was dated on
  or before 2026-07-31, every one was under 2.4 MB, and metadata only was
  printed. Each run's temporary directory, outside the repo, was deleted.

**F123.10 What this did not do.** It read no 2026-27 value and no
observation, computed no score, used no account, installed nothing, and
wrote nothing under `data/`. It edited no existing script, and edited SPEC
and CLAUDE.md only as D74 says. It did not edit RESULTS.md, README.md or
PROJECT-INSTRUCTIONS.md. It chose no source, save location or NBM/MOS
outcome rule. Nothing was committed and no commit message was written.

**F123.11 Planning-chat note, 2026-09-28, not checked by this session.**
PNS 26-30 was read in full. It proposes removing the 0.50 and 1.00 degree
GFS GRIB2 files and says the 0.25 degree pgrb2 files remain available. It is
a proposal; confirm against the v17 SCN (D73.4).

---

## 2026-09-29 — Session 83 decision: the ICON route check and confidence intervals (owner, planning chat)

**D75. Owner decision, planning chat (after session 82): session 83's
plan.** Written at the start of session 83, before any network call or
data read.

- **D75.1 ICON: checked first, decided after.** F123 classed DWD ICON
  global as "No archive" (about 24 h). The planning chat found two
  Open-Meteo routes in documentation (2026-09-29, not checked by this
  session): Previous Runs (`icon_global`, from 2024-01-19, no 850 hPa
  temperature at any offset, F123.5) and Single Runs (any run by its
  initialisation time, most models from 2026-04-02; its variable list
  includes 850 hPa temperature). Session 83 checks, read-only and on
  valid times no later than 2026-07-31 (F124):
  (a) the first day `shortwave_radiation_previous_day1` and `_day2` are
  present, against `temperature_2m_previous_day1`'s floor;
  (b) whether Single Runs serves `icon_global` from 2026-04-02, with 850
  hPa temperature, and all four cycles (00, 06, 12, 18 UTC);
  (c) whether `temperature_2m_previous_day1` at each hour H equals the
  Single Runs value from the run at floor(H/6)x6 UTC on the day before,
  at lead 24 + (H mod 6): the GFS convention (F5, F89).
  The owner decides whether the project saves ICON (D72.8) after
  reviewing F124. Stated in advance: if 850 hPa temperature is present,
  the project does not save ICON; if it is absent, the owner chooses
  between saving ICON natively (to get 850 hPa temperature) and using
  ICON without feature L.
- **D75.2 Confidence intervals (stage A; SPEC 5.4, D72.3).** For every
  result on record: F16, F30, F47, F64, F82 (minimal method), F94
  (richer method), F109 (selected method) and F119 looks A and B
  (KSFO). Descriptive only: they change no verdict and are not a new
  look. They reuse the spent years (sealed 2025-26, reserved 2024-25)
  descriptively; no verdict, selection or build choice is drawn from
  them (SPEC 2.5). Gate first: every MAE recomputed must equal its
  recorded figure at the entry's precision; a result that fails gets no
  interval. Statistic: the paired per-day MAE difference (reference minus
  model, degC) and skill (1 - model/reference), model against raw GFS
  and against persistence, on the days both have. Method: moving-block
  bootstrap, 7-day blocks, 10,000 resamples, seed 83, 95% percentile
  interval. Recorded as F125.
- **D75.3 Carried.** The owner's decision on session 82's MOS near-miss
  (F123.9) is deferred to the NBM/MOS outcome rule (D72.7, D73.8), and
  is taken when that rule is written.
- **D75.4 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice; only the April 2026
  proposals (PNS 26-29, 26-30). The earliest go-live is about late
  October 2026.

---

## 2026-09-29 — Session 83 finding: the ICON route check

**F124. A read-only check of Open-Meteo's two ICON routes (D75.1). It
printed only HTTP status, error reasons, grid metadata, valid-time ranges,
present/null counts and match counts. Script:
`scripts/session83_icon_route_check.py` (new; reads the network and
prints; writes no data file). Full real output:
`notes/session-83-output.txt`. Run 2026-09-29.**

**F124.1 Steps 0 and 1.**
- Step 0: `git status --porcelain` showed only `?? docs/session-83.md`.
  The last entries were D74 and F123; no D75, F124 or F125 existed in
  either DECISIONS file; neither new script nor the output file existed.
  D72, D73, D74, F122, F123 and D51, and the archived F5, F89, F16, F30,
  F47, F64, F82, F94, F109, F119, D21.8, D58 item 6 and D70 were read.
- Scope note: before D75 was appended, a `head -3` looking for saved
  predictions printed the header and first two rows of three committed
  files (`session78_ksfo_looks_predictions.csv`,
  `session63_reserved_confirm_grid.csv`,
  `session40_sealed_test_summary.csv`). All are spent-year values already
  on record. Nothing was scored or used from that print.
- Step 1: D75 was copied mechanically (`sed`) from `docs/session-83.md`
  lines 82–125 into DECISIONS.md lines 1342–1385 and checked byte-equal
  with `diff`. (After this session's archive step moved D74, D75 sits at
  lines 1307–1350.)

**F124.2 The answers.** EGLC (SPEC 3.4), `icon_global`, default grid-cell
selection. Every successful response returned grid 51.5, 0.0, 4 m.
- **(a) Radiation floor, past-run route.** On 2024-01-17..21 (120 hours):
  `temperature_2m_previous_day1` and `shortwave_radiation_previous_day1`
  are both first present at 2024-01-19T12:00 (60 present, 60 null each).
  `shortwave_radiation_previous_day2` is first present at 2024-01-20T12:00
  (36 present, 84 null), one day later. No widening was needed.
- **(b) Single Runs.** `run=2026-04-01T18:00`: HTTP 400, "The requested
  model run is not available. Model: dwd_icon, run: 2026-04-01T18:00Z".
  `run=2026-04-02T00:00` and `run=2026-07-29T18:00`: HTTP 200, 48 hours
  each; `temperature_850hPa` 48 present, 0 null; `temperature_2m` 48/0;
  `shortwave_radiation` 47/1. So 850 hPa temperature is served from
  2026-04-02 in both runs checked. Cycles: 00, 06 and 12 UTC answered on
  2026-06-10 and 18 UTC on 2026-07-29, but `run=2026-06-10T18:00` returned
  HTTP 400 ("not available"). All four cycles exist in the archive, but
  not on every day checked.
- **(c) Timing.** 18 of 24 hours of 2026-06-11 match: at hours 00–17 the
  past-run `temperature_2m_previous_day1` equals exactly the Single Runs
  value from the run at floor(H/6)x6 UTC on 2026-06-10, lead 24 + (H mod
  6). Hours 18–23 could not be tested, because that run (2026-06-10 18z)
  is not available. For those hours an equal value was found in other
  2026-06-10 runs at hours 20 (00z, 12z), 21 (12z) and 22 (06z, 12z), and
  in none at 18, 19 and 23. These equalities are not interpreted:
  they are single-value coincidences, not a run pattern. Of the five
  requests, the four that answered were fully present (past run 24/0; the
  00z, 06z and 12z runs 54/0 each); the 18z run returned HTTP 400.

**F124.3 Notes.** No request needed a retry. HTTP 400 answers ("run not
available") were final and not retried; only network errors, 429 and 5xx
would have been. No response held a valid time after 2026-07-31T23:00
(the latest was 2026-07-31T17:00).

**F124.4 What this did not do.**
- No forecast value was printed or saved.
- No observation was read, and nothing was scored.
- No valid time after 2026-07-31 was requested or received.
- No ICON decision: whether the project saves ICON is the owner's, from
  this finding (D75.1).
- It wrote nothing under `data/`, edited no existing script, and
  installed nothing.

---

## 2026-09-29 — Session 83 finding: confidence intervals for the results on record

**F125. Offline. 95% moving-block bootstrap intervals (D75.2) for the
paired per-day MAE difference d = MAE(reference) − MAE(model), in °C, and
for skill = 1 − MAE(model)/MAE(reference), in %, for all 17
airport-results on record, against raw GFS and against persistence. All
17 passed the reproduction gate. Script:
`scripts/session83_confidence_intervals.py` (new; reads committed files
only; writes nothing). Full real output: `notes/session-83-output.txt`.
Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

**F125.1 Where the per-day errors came from.**
- **Saved predictions:** only KSFO's (F119):
  `data/processed/session78_ksfo_looks_predictions.csv`, SHA-256
  `b4b46adc…d78e`, equal to F119.4. Used as saved; no refit.
- **Minimal method (F16–F82):** refit by the record scripts' own
  functions (`session07`, `13`, `18`, `24`, `29_test.py`). Each script
  calls `main()` when imported, which would overwrite its committed
  output note. So each file was parsed and run without three top-level
  statements: its docstring, its libomp loader shim (already run by the
  import below) and the bare `main()` call. Then `main()`'s own steps were
  called in order: `prove_it_matches_the_lock()` (its assertions did not
  trip), `join()` (reconciled: yes at all five), `fit_on_training()` and
  `score_test_year()`. Their printed text was suppressed.
- **F94:** functions imported from `session39_sealed_test.py`, following
  `run_airport()` step by step, with its guards applied as it applies
  them (in-window dates, row assertions, training-row reconciliation,
  sealed-row ceiling). Only the 5-feature model was fitted.
- **F109:** functions imported from `session62_reserved_confirm.py`
  (SHA-256 checked against D70.2 first), following `run_confirm()` step
  by step, with its two guards. As F122.4. The session-48 guard was not
  called, edited or disabled.
- All seven record scripts were unchanged against HEAD; their SHA-256 are
  in the output file. No file was written, and no `__pycache__` file was
  added.
- **For the owner:** 3.2 of the session prompt says "from committed
  processed files only". The record code for the minimal method, F94 and
  F109 also reads committed raw files, read-only: the Open-Meteo JSON
  chunks (minimal method) and the IEM observation chunks (all three), as
  F122.3 did. No processed file exists for the minimal method. This
  session followed the record code rather than stop.

**F125.2 The gate.** Every MAE (model, raw GFS, persistence) equals the
entry's recorded figure at the entry's printed precision, and every day
count equals the entry's.

| result | precision | EGLC | LFPG | DSM | YSDU | RNO |
|---|---|---|---|---|---|---|
| minimal (F16, F30, F47, F64, F82) | 3 dp | pass (363) | pass (363) | pass (365) | pass (347) | pass (365) |
| F94 | 3 dp | pass (364/363) | pass (364/363) | pass (365/365) | pass (356/347) | pass (365/365) |
| F109 | 4 dp | pass (364/363) | pass (365/365) | pass (365/365) | pass (360/355) | pass (365/365) |

| result | precision | look A | look B |
|---|---|---|---|
| F119 (KSFO) | full (repr) | pass (364/363) | pass (365/365) |

Days are model and raw GFS / persistence. **17 of 17 pass.**

**F125.3 Method, as D75.2 and the session prompt's 3.3.** Paired days =
days on which both the model and the reference have an error, ordered by
date: the common day set for the minimal method; every test day for raw
GFS and the persistence day set for persistence in the others. Blocks of
7 consecutive days, starts uniform on 0..n−7, ceil(n/7) blocks truncated
to n, the same resampled days for model and reference. 10,000 resamples,
`numpy.random.default_rng(83)`, one generator, in the order of the tables
below, raw GFS before persistence. 2.5th and 97.5th percentiles.

**F125.4 Minimal method (F16–F82), sealed year 2025-26, one common day
set.**

| airport | reference | n | d (°C) [95%] | skill (%) [95%] | d wholly above 0 |
|---|---|---|---|---|---|
| EGLC | raw GFS | 363 | +0.202 [+0.096, +0.298] | +16.3 [+8.5, +22.1] | yes |
| EGLC | persistence | 363 | +1.056 [+0.830, +1.262] | +50.4 [+43.0, +56.3] | yes |
| LFPG | raw GFS | 363 | +0.188 [+0.070, +0.301] | +13.5 [+5.5, +20.3] | yes |
| LFPG | persistence | 363 | +1.092 [+0.847, +1.291] | +47.5 [+39.8, +53.2] | yes |
| DSM | raw GFS | 365 | +0.115 [−0.071, +0.287] | +6.3 [−4.2, +14.8] | no |
| DSM | persistence | 365 | +2.303 [+1.862, +2.823] | +57.5 [+51.5, +62.8] | yes |
| YSDU | raw GFS | 347 | +0.041 [−0.058, +0.146] | +3.3 [−4.9, +11.1] | no |
| YSDU | persistence | 347 | +1.458 [+1.135, +1.842] | +54.7 [+47.1, +61.3] | yes |
| RNO | raw GFS | 365 | −0.044 [−0.179, +0.127] | −3.1 [−13.4, +8.1] | no |
| RNO | persistence | 365 | +1.032 [+0.750, +1.344] | +41.4 [+32.4, +49.7] | yes |

Raw GFS here is Open-Meteo's (SPEC 5.2).

**F125.5 Richer 5-feature method (F94), sealed year 2025-26.**

| airport | reference | n | d (°C) [95%] | skill (%) [95%] | d wholly above 0 |
|---|---|---|---|---|---|
| EGLC | raw GFS | 364 | +0.254 [+0.151, +0.347] | +20.2 [+13.7, +25.0] | yes |
| EGLC | persistence | 363 | +1.096 [+0.872, +1.302] | +52.3 [+45.2, +57.8] | yes |
| LFPG | raw GFS | 364 | +0.226 [+0.114, +0.332] | +16.4 [+8.9, +22.6] | yes |
| LFPG | persistence | 363 | +1.144 [+0.904, +1.342] | +49.7 [+42.5, +55.5] | yes |
| DSM | raw GFS | 365 | +0.098 [−0.078, +0.266] | +5.6 [−4.8, +14.6] | no |
| DSM | persistence | 365 | +2.367 [+1.924, +2.855] | +59.1 [+53.4, +64.1] | yes |
| YSDU | raw GFS | 356 | +0.138 [+0.033, +0.251] | +10.5 [+2.6, +18.2] | yes |
| YSDU | persistence | 347 | +1.504 [+1.169, +1.891] | +56.3 [+49.1, +62.9] | yes |
| RNO | raw GFS | 365 | +0.166 [−0.017, +0.396] | +11.0 [−1.3, +22.6] | no |
| RNO | persistence | 365 | +1.144 [+0.874, +1.436] | +45.9 [+38.4, +52.7] | yes |

**F125.6 Selected method `B+D,L,R,T` (F109), reserved year 2024-25.**

| airport | reference | n | d (°C) [95%] | skill (%) [95%] | d wholly above 0 |
|---|---|---|---|---|---|
| EGLC | raw GFS | 364 | +0.235 [+0.146, +0.312] | +19.0 [+12.6, +24.2] | yes |
| EGLC | persistence | 363 | +1.224 [+0.995, +1.479] | +55.0 [+48.5, +61.2] | yes |
| LFPG | raw GFS | 365 | +0.172 [+0.090, +0.263] | +12.2 [+6.8, +17.6] | yes |
| LFPG | persistence | 365 | +1.286 [+1.016, +1.548] | +51.0 [+43.0, +57.5] | yes |
| DSM | raw GFS | 365 | +0.292 [+0.118, +0.491] | +17.1 [+7.4, +27.0] | yes |
| DSM | persistence | 365 | +2.696 [+2.263, +3.228] | +65.6 [+60.8, +70.3] | yes |
| YSDU | raw GFS | 360 | +0.225 [+0.111, +0.354] | +15.1 [+7.9, +22.3] | yes |
| YSDU | persistence | 355 | +1.333 [+1.077, +1.598] | +51.7 [+44.9, +57.9] | yes |
| RNO | raw GFS | 365 | +0.339 [+0.190, +0.532] | +21.0 [+13.2, +28.5] | yes |
| RNO | persistence | 365 | +1.482 [+1.190, +1.807] | +53.8 [+46.3, +60.4] | yes |

**F125.7 Selected method `B+D,L,R,T` at KSFO (F119).** D71.5's framing
applies.

| look | reference | n | d (°C) [95%] | skill (%) [95%] | d wholly above 0 |
|---|---|---|---|---|---|
| A (2024-25) | raw GFS | 364 | +0.169 [+0.032, +0.295] | +11.8 [+2.4, +20.0] | yes |
| A (2024-25) | persistence | 363 | +0.255 [+0.058, +0.453] | +16.9 [+4.1, +28.2] | yes |
| B (2025-26) | raw GFS | 365 | +0.349 [+0.198, +0.508] | +20.2 [+12.7, +26.8] | yes |
| B (2025-26) | persistence | 365 | +0.334 [+0.047, +0.581] | +19.5 [+2.9, +31.7] | yes |

Raw GFS in F125.5–F125.7 is the elevation-adjusted GRIB temperature (SPEC
5.2).

**F125.8 Point estimates on the persistence day set.** Where that set is
smaller than the test set, the model's MAE on it differs from the recorded
all-day figure, so the d and skill above differ slightly from the recorded
margins: F94 EGLC model 1.0008 (recorded 1.000), LFPG 1.1568 (1.156), YSDU
1.1650 (1.179; as F94 Task 2 found); F109 EGLC 1.0023 (1.0008), YSDU
1.2446 (1.2643); F119 look A 1.2562 (1.2576, as F119.3's common-day
re-score). Elsewhere the two sets are the same.

**F125.9 Statements.**
- These intervals describe day-to-day sampling within one test year
  only. They do not capture year-to-year variation (see F96).
- The five airports in F16–F82, F94 and F109 share each test year's
  weather, so their intervals are not independent.
- These intervals change no verdict (D75.2).

**F125.10 What this did not do.**
- Nothing was refit differently, retuned, reselected or re-locked. Every
  model was refit exactly as recorded, or its saved predictions were used.
- No network call.
- Nothing was written under `data/`, and no existing script was edited.
- No verdict changed.
- Nothing was committed and no commit message was written.
