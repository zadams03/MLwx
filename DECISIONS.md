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

---

## 2026-09-29: Session 84 decision: GitHub readiness (owner, planning chat)

**D76. Owner decisions, planning chat (after session 83): the session 83
review and session 84's plan.** Written at the start of session 84,
before any other edit or network call.

- **D76.1 F125.1 accepted.** The refits' read-only use of committed raw
  files (the Open-Meteo JSON chunks and the IEM observation chunks), as
  the record code does and as F122.3 did, is accepted. It is within
  "committed files" for session 83's purpose.
- **D76.2 ICON: the project does not save ICON.** F124.2(b) found 850
  hPa temperature present in Open-Meteo's Single Runs `icon_global` from
  2026-04-02. D75.1's rule, stated in advance, therefore applies: the
  project does not save ICON itself. This closes D72.8 for ICON. The
  completeness of the Single Runs archive (one missing 18z run found,
  not scanned) and the timing at hours 18 to 23 (F124.2) stay open, for
  stage D.
- **D76.3 Session order.** Session 84 is a GitHub-readiness session
  before the repo goes public: a README rewrite, F125's intervals and
  caveats in RESULTS.md, data credits and terms, a secrets and
  personal-path check, and a licence file. The NBM/MOS comparison and
  its outcome rule (D72.7), the carried F123.9 decision (D75.3) and
  whether 2026-27 gets a pre-registered NBM/MOS test (D73.8) move to
  session 85. The hold rule (D73.8) is unchanged.
- **D76.4 Licence.** The code is released under the MIT licence. Data
  committed in the repo stays under its sources' terms, which the MIT
  licence cannot change; the README says so.
- **D76.5 Public contents.** `docs/`, `notes/` and the planning files
  stay in the public repo as the working record. The README tells
  readers which files to read and which to skip. Personal paths found by
  the audit are reported, not edited: editing old notes would alter the
  record, and the git history keeps them anyway.
- **D76.6 No em-dashes (standing rule).** No new text from session 84
  on uses the em-dash (U+2014). Existing text is not edited to remove
  it. The rule is added to CLAUDE.md's plain-writing rule.
- **D76.7 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice. NOAA's April 2026
  proposal says one will be issued 30 days before go-live, so the
  earliest go-live is about late October 2026.

---

## 2026-09-29: Session 85 decision: the NBM/MOS comparison, its outcome rule and the 2026-27 NBM/MOS test (owner, planning chat)

**D77. Owner decisions, planning chat (after session 84): the NBM/MOS
comparison (D72.7), its outcome rule, the F123.9 decision (D75.3) and a
pre-registered NBM/MOS test on 2026-27 (D73.8).** Written at the start of
session 85, before any network call or data read. No NBM or MOS value
and no 2026-27 value has been read.

- **D77.1 Competitors.** NBM CONUS `core`, the deterministic 2 m
  temperature, at DSM, RNO and KSFO: the primary comparison. GFS MOS
  (MAV) at DSM only: a secondary, descriptive comparison, because MAV
  has no 20:00 UTC projection at RNO or KSFO (F123.4) and no value is
  interpolated in time. NAM MOS is excluded (terminated October 14,
  2026, SCN 26-47). LAMP is excluded (not a day-ahead product).
- **D77.2 Matching.** For each target day D: the same target hour as
  the record (SPEC 3.4); the competitor run with the same nominal cycle
  as our GFS cycle (floor(H/6)x6 UTC on D-1, F5, F89), at the lead that
  makes its valid time equal the target hour (DSM: 18z D-1, 24 h; RNO
  and KSFO: 18z D-1, 26 h). NBM's value is taken at the grid point
  nearest the station's position in SPEC 3.4 (nearest neighbour, no
  interpolation), converted from K to degC. MAV's value is used as
  issued (whole degF), converted to degC exactly; the rounding is a
  recorded caveat and is not corrected. The observation is the one in
  the recorded rows, so every forecast is scored against the same
  value. Missing competitor values are dropped and counted (SPEC 2.2).
- **D77.3 The spent-year comparison.** Recorded predictions only, after
  a reproduction gate: F109's `B+D,L,R,T` at DSM and RNO (2024-08-01 to
  2025-07-31) and F119's saved predictions at KSFO, look A (2024-25) and
  look B (2025-26). No other years: the feature-selection folds
  (2022-23, 2023-24 and truncated 2025-26) chose `B+D,L,R,T`'s features
  and would flatter it. Day set: the recorded model test days on which
  the competitor value is present. Reported per airport-look: MAE of
  the model, the competitor and raw GFS (GRIB, elevation-adjusted), mean
  errors, d = MAE(competitor) - MAE(model) in degC and skill =
  1 - MAE(model)/MAE(competitor), with F125's interval method (7-day
  moving blocks, 10,000 resamples, 95% percentile) and seed 85. NBM
  version segments are labelled; MAE per segment is descriptive only.
  This spends no held-out data: the years are already spent (F94, F109,
  F119). It is descriptive and decides direction only (D72.7). It
  changes no verdict. KSFO carries D71.5's framing. The comparison is
  at one hour; stage C re-runs it on the full curve, as a description
  (D72.8).
- **D77.4 The outcome rule (D72.7), fixed before the comparison is
  run.** Judged on NBM only, on point estimates, over the four
  airport-looks (DSM, RNO, KSFO look A, KSFO look B):
  - **Win:** the model's MAE is lower than NBM's at all four. The
    roadmap carries on as D72 sets it.
  - **Lose:** NBM's MAE is lower than or equal to the model's at all
    four.
  - **Mixed:** anything else.
  On "lose" or "mixed", the gap is recorded (d, skill and intervals),
  and the owner decides in writing, before stage C's lock, between:
  (a) bringing a US-only stacking check (NBM as an input) forward from
  stage E; (b) weighting the roadmap towards non-US airports; (c) both;
  or (d) neither, with reasons. The intervals are reported but do not
  set the band. The MAV comparison is reported and does not set the
  band. The comparison is reported in full whatever the band.
- **D77.5 F123.9 accepted.** Session 82's exploratory MOS request held
  projections valid 2026-08-01 to 08-08 in memory only; no value was
  printed, saved or used, and no observation or score was involved. No
  information about 2026-27 outcomes was learned. It is accepted and
  recorded; no 2026-27 day is excluded because of it.
- **D77.6 A pre-registered NBM/MOS test on 2026-27.** This entry is the
  owner's written decision that D73.8's hold rule requires.
  - What is tested: the frozen F122 `B+D,L,R,T` models (SHA-256 in
    F122), unchanged, at DSM, RNO and KSFO.
  - Competitors and matching: as D77.1 and D77.2. NBM at all three; MAV
    at DSM only.
  - Periods: D73.3's period A and period B, judged separately. Neither
    is scored before it has ended and its observations are in (D73.8).
  - Day set: D73.5's complete-case test days on which the competitor
    value is also present. Missing values are dropped and counted.
  - Pass rule: per airport, per period, per competitor, PASS if the
    frozen model's MAE is lower than the competitor's MAE on that day
    set, otherwise FAIL. Each verdict is labelled with its dates, its
    season and the competitor versions in force.
  - Descriptive, never part of the rule: F125-method intervals, and the
    frozen `B` model and raw GFS on the same days.
  - Separate from D73: no D73 verdict depends on this test, and this
    test changes none.
  - Expectations: none stated.
  - Competitor changes: a version change inside a period does not split
    it; it is labelled. If a competitor has no value in a period (for
    example, it is discontinued), that comparison is void for that
    period. A void comparison is not a fail.
  - Data: fetched from the archives after each period ends, with the
    same valid-time guards. The scripts are written in a later session,
    with D73.8's scripts, and committed before any 2026-27 row is built.
  - KSFO carries D71.5's framing. The write-up leads, in each period,
    with the smallest margin.
- **D77.7 NBM versions (planning-chat web search, 2026-09-29, not
  checked by this session).** v4.2 from 2024-05-15; v4.3 effective on
  or about 2025-05-27 from the 12z run (SCN 25-34 was issued
  2025-04-15, which explains F123.3's two dates); v5.0 from 2026-05-05;
  v5.0.14 on 2026-07-28, which fixed anomalous temperature and dewpoint
  guidance, notably in transition seasons and coastal areas. So both
  spent years use NBM before that fix. v4.3's changes were mainly to
  tropical-cyclone wind and severe-weather products.
- **D77.8 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice; the newest SCN listed
  is SCN 26-87 (2026-09-22). With 30 days' notice, the earliest go-live
  is about late October 2026 or later.
- **D77.9 Session 85's plan.** Record this entry; run the reproduction
  gate; pull NBM and MAV for the spent-year days only; run the
  comparison and apply D77.4's rule; record F127. SPEC 6's stage A and
  stage B bullets are updated to point to this entry and F127.

---

## 2026-09-29: Session 85 finding: the NBM/MOS comparison on the spent years

**F127. The NBM/MOS comparison (D72.7, D77) on the spent years, with
recorded predictions only. All four airport-looks passed the reproduction
gate. NBM and GFS MOS (MAV) values were pulled for the spent-year target
days only. Under D77.4's rule the band is MIXED: the model's MAE is lower
than NBM's at RNO only. Script: `scripts/session85_nbm_mos_comparison.py`
(new; modes `--gate`, `--pull`, `--compare`). Full real output:
`notes/session-85-output.txt`. Run 2026-09-29. Python 3.12.2, numpy
2.5.2, lightgbm 4.7.0, eccodes 2.48.0, requests 2.34.2.**

**F127.1 Steps 0 and 1.**
- `git status --porcelain` showed only `?? docs/session-85.md`. The last
  entries were D76 and F126. No D77 or F127 existed in either DECISIONS
  file. None of the four new paths existed.
- Read: D71.5, D72, D73, F122, F123, F125 and D76 in DECISIONS.md; F5,
  F89, D58 item 6, D70, F109 and F119 in DECISIONS-archive.md; SPEC 3.4,
  5, 8.5 and 8.7; `scripts/session82_source_probe.py` and
  `scripts/session83_confidence_intervals.py` (read only).
- D77 was copied mechanically (`sed`) from `docs/session-85.md` lines 95
  to 198 into DECISIONS.md lines 1726 to 1829 and checked byte-equal with
  `diff`, before any network call or data read. (After this session's
  archive step moved D75 and F126, D77 sits at lines 1571 to 1674.)
- Archive step: D75 and F126 were moved verbatim to DECISIONS-archive.md
  (see its "Moved by session 85" section).

**F127.2 The gate (`--gate`, run once; re-run inside `--compare`). PASSED
at all four.** `session62_reserved_confirm.py` SHA-256 equals D70.2;
`session78_ksfo_looks_predictions.csv` SHA-256 equals F119.4. DSM and RNO
were refit by F125.1's route (functions imported from the record script,
`run_confirm()`'s steps and both guards, only `B+D,L,R,T`); KSFO used the
saved predictions. Compared at full precision with
`session63_reserved_confirm_grid.csv` and `session78_ksfo_looks_grid.csv`.

| airport-look | model MAE (recomputed = recorded) | raw GFS MAE (recomputed = recorded) | days | gate |
|---|---|---|---|---|
| DSM (F109) | 1.4122847644111458 | 1.7043452054794521 | 365 | pass |
| RNO (F109) | 1.2741517803385958 | 1.6134575342465751 | 365 | pass |
| KSFO look A | 1.2575770731513778 | 1.4262582417582421 | 364 | pass |
| KSFO look B | 1.3830033790440732 | 1.7321205479452053 | 365 | pass |

**F127.3 The pull (`--pull`).**
- **Run 1 failed on a network error and wrote nothing.** After about 600
  of 1,095 NBM files, the host name `noaa-nbm-grib2-pds.s3.amazonaws.com`
  could not be resolved (DNS) for `blend.20250621/18/core/...f024` after
  3 retries. The script writes nothing under `data/` until both
  sub-steps finish, and its temporary directory was deleted. **Run 2**,
  the one re-run the prompt allows, with the script unchanged, completed.
  Both runs' output is in the output file.
- **NBM.** Layout as session 82's probe:
  `blend.YYYYMMDD/HH/core/blend.tHHz.core.fFFF.co.grib2` and `.idx`.
  1,095 files planned (for 1,460 airport-look target days; RNO and KSFO
  look A share files) and 1,095 read. Missing: `.idx` 0, file 0; zero
  matching `.idx` lines 0; several 0; failed checks (valid time, units K,
  `2t`, `.idx` date) 0; missing values 0. Size trial: 3 messages,
  4,595,818 B (1,531,939 B each), projected 1.68 GB, under 20 GB.
  Fetched: 1,690,026,394 B (1.69 GB) of messages; 1 request retried. No
  GRIB byte was kept. Latest valid time requested: 2026-07-31 20:00 UTC.
  No valid time after 2026-07-31T23:00 appeared.
- **NBM grid points** (eccodes nearest neighbour; unchanged across each
  window):

| station | grid latitude | grid longitude (0 to 360) | distance | uses |
|---|---|---|---|---|
| DSM | 41.541124 | 266.34249 | 0.873 km | 365 |
| RNO | 39.483896 | 240.228363 | 0.046 km | 365 |
| SFO | 37.619643 | 237.629953 | 0.433 km | 730 |

- **Version check (report only).** The 18z f026 files for cycles
  2025-05-26 and 2025-05-28 each have 117 `.idx` lines. Their 2 m
  temperature messages have the same name, units (K), level, grid (Lambert,
  2,345 × 1,597, 2,539.703 m) and packing: no key differs except the
  dates.
- **MAV** (IEM `api/1/mos.json`, KDSM, model GFS, 18z runs): 365 runs
  requested, 365 with rows, 365 values, 0 missing. Every response's
  projections were valid on or before 2025-08-02. In all 7,665 saved
  projections, `ftime` equals `ftime_utc` and `runtime` equals
  `runtime_utc` (time fields only), so matching was on UTC. The 365 raw
  responses are saved unchanged in `data/raw/iem_mos/session85/`, with one
  `session85_mav.meta.txt` that lists each file's exact query and pull
  time.
- **Points file.** `data/processed/session85_competitor_points.csv`, 1,825
  rows (NBM: DSM 365, RNO 365, KSFO A 365, KSFO B 365; MAV: DSM 365),
  SHA-256
  `681802a27338d0bafddabffdf1bd6d2168b6dd39a2460e07964340445819a63e`. Its
  `.meta.txt` lists the pull date, the bucket, every NBM URL with its byte
  range and `.idx` line, and the counts.

**F127.4 The comparison (`--compare`, run once).** Day set: the recorded
test days on which the competitor value is present (no competitor value
was missing). d = MAE(competitor) − MAE(model), in °C; skill = 1 −
MAE(model)/MAE(competitor). F125's moving-block bootstrap, seed 85, one
generator in the order of the table. Raw GFS is the elevation-adjusted
GRIB temperature (SPEC 5.2). KSFO carries D71.5's framing.

| airport-look | competitor | n | MAE model | MAE competitor | MAE raw GFS | d (°C) [95%] | skill (%) [95%] | d wholly above zero |
|---|---|---|---|---|---|---|---|---|
| DSM (2024-25) | NBM | 365 | 1.4123 | 1.2196 | 1.7043 | −0.193 [−0.308, −0.051] | −15.8 [−26.0, −4.0] | no |
| RNO (2024-25) | NBM | 365 | 1.2742 | 1.3192 | 1.6135 | +0.045 [−0.060, +0.156] | +3.4 [−4.7, +11.2] | no |
| KSFO look A (2024-25) | NBM | 364 | 1.2576 | 1.0000 | 1.4263 | −0.258 [−0.382, −0.131] | −25.8 [−39.1, −12.8] | no |
| KSFO look B (2025-26) | NBM | 365 | 1.3830 | 1.3023 | 1.7321 | −0.081 [−0.220, +0.044] | −6.2 [−16.8, +3.3] | no |
| DSM (2024-25) | MAV | 365 | 1.4123 | 1.5773 | 1.7043 | +0.165 [+0.017, +0.332] | +10.5 [+1.1, +19.6] | yes |

Mean errors (forecast minus observation, °C): DSM model +0.333, NBM
+0.028, MAV +0.253, raw GFS +0.351; RNO model +0.498, NBM +0.315, raw GFS
+0.183; KSFO A model +0.708, NBM −0.024, raw GFS +0.417; KSFO B model
+0.540, NBM +0.294, raw GFS +0.661.

**F127.5 NBM version segments (D77.7 dates, by NBM cycle; descriptive
only).** A target day's segment is the version in force at its 18z D−1
cycle. v4.3 starts at the 2025-05-27 12z run. The hour of v5.0
(2026-05-05) and v5.0.14 (2026-07-28) is not given; 00z is assumed, which
only matters if a switch came after 18z.

| airport-look | segment | n | target days | MAE model | MAE NBM |
|---|---|---|---|---|---|
| DSM | v4.2 | 300 | 2024-08-01..2025-05-27 | 1.4177 | 1.2373 |
| DSM | v4.3 | 65 | 2025-05-28..2025-07-31 | 1.3871 | 1.1378 |
| RNO | v4.2 | 300 | 2024-08-01..2025-05-27 | 1.3770 | 1.4133 |
| RNO | v4.3 | 65 | 2025-05-28..2025-07-31 | 0.7994 | 0.8848 |
| KSFO look A | v4.2 | 299 | 2024-08-01..2025-05-27 | 1.2414 | 1.0300 |
| KSFO look A | v4.3 | 65 | 2025-05-28..2025-07-31 | 1.3321 | 0.8622 |
| KSFO look B | v4.3 | 278 | 2025-08-01..2026-05-05 | 1.4563 | 1.2417 |
| KSFO look B | v5.0 | 84 | 2026-05-06..2026-07-28 | 1.1798 | 1.5196 |
| KSFO look B | v5.0.14 | 3 | 2026-07-29..2026-07-31 | 0.2794 | 0.8333 |

**F127.6 The band under D77.4: MIXED.** On NBM point estimates: DSM,
NBM lower (1.2196 vs 1.4123); RNO, model lower (1.2742 vs 1.3192); KSFO
look A, NBM lower (1.0000 vs 1.2576); KSFO look B, NBM lower (1.3023 vs
1.3830). The model is lower at 1 of 4. Under D77.4, the owner decides in
writing, before stage C's lock, between (a), (b), (c) and (d). The gap is
recorded in F127.4. The MAV comparison and the intervals do not set the
band.

**F127.7 Statements.**
- "This comparison uses spent years and recorded predictions. It is
  descriptive and decides direction only (D72.7, D77.3). It changes no
  verdict."
- "These intervals describe day-to-day sampling within one test year
  only. They do not capture year-to-year variation."
- "MAV values are whole degrees F, used as issued; the rounding is not
  corrected (D77.2)."
- "Both years use NBM before its 2026-07-28 temperature fix (v5.0.14,
  D77.7)."
- Planning-chat correction (SCN 26-70, web search 2026-09-29): v5.0.14
  took effect from the 12z run on 2026-07-28. So KSFO look B's last 3
  target days (2026-07-29 to 07-31) use NBM after the fix; every other
  day in both years uses NBM before it. The segment table already assigns
  them this way.

**Planning-chat corrections to D77 (D77 itself stays byte-equal).**
- D77.1: NAM MOS's end is scheduled, not past. It should read "to be
  terminated effective October 14, 2026 (SCN 26-47)".
- D77.7: SCN 26-24 (updated) sets NBM v5.0 on or about 2026-04-30, from
  the 13z run, not 2026-05-05 (MDL's announcement date). So KSFO look B
  targets 2026-05-01 to 05-05 (5 days) are labelled v4.3 in the segment
  table but were probably made by v5.0. Segments are descriptive only;
  not re-run.
- The start-hour question is closed: v4.3 (12z), v5.0 (13z) and v5.0.14
  (12z) all began before 18z, so assigning 18z runs by date is correct
  given the right dates.

**F127.8 What this did not do.**
- No refit other than F109's recorded route (DSM and RNO, `B+D,L,R,T`
  only). No retune, reselection or re-lock. KSFO used saved predictions.
- No 2026-27 value was requested, received or read.
- No GRIB file was kept. NBM bytes went to a temporary directory outside
  the repo; each message was deleted after its value was read, and the
  directory was deleted.
- No existing script was edited; no guard was edited, bypassed or
  disabled. `data/models/` was not touched. Nothing was installed.
- No direction was decided (D77.4). No verdict changed.
- Nothing was committed and no commit message was written.

---

## 2026-09-30: Session 86 decision: the direction decision, two open items and the 2026-27 scripts (owner, planning chat)

**D78. Owner decisions, planning chat (after session 85): the direction
decision that D77.4 requires, two open items, and the plan for the
2026-27 scripts.** Written at the start of session 86, before any other
edit, network call or data read. No 2026-27 value has been read.

- **D78.1 Direction: option (d), neither.** F127's band is mixed. The
  owner chooses neither (a) nor (b), for these reasons:
  - (i) F127 is the expected result of a correction of one weather
    model, trained once on a fixed window, against NBM, a blend of many
    models whose bias correction is updated continuously. The gap is
    not uniform: the model's MAE is lower at RNO, and KSFO look B's
    interval spans zero.
  - (ii) NBM as an input is already stage E (D72.3). Bringing it
    forward would break D72.2(b), one input first. NBM also changed
    version several times inside the training window (F123.3, D77.7).
  - (iii) Option (b) rests on an untested premise. Stage A probed no
    non-US post-processed forecast, and some exist (for example DWD's
    MOSMIX, and the Bureau of Meteorology's forecasts at Dubbo).
  - (iv) The lever F127 points to (D78.2) applies at every airport, US
    or not.
  The roadmap carries on as D72 sets it.
- **D78.2 Open item: bias drift.** In F127 the model's mean error is
  warm at all four airport-looks (+0.333 to +0.708 degC). At RNO and
  KSFO look A it is warmer than raw GFS's. The correction learned in
  training was carried into test years in which GFS's own bias had
  shifted, as D71.4 found at KSFO. Planning-chat arithmetic on F127's
  summary figures, assuming normally distributed errors and using each
  test year's own mean (hindsight, insight only, not a finding): with
  both biases removed, NBM's MAE would still be lower at DSM, KSFO look
  A and KSFO look B, so the band would still be mixed. A correction
  that adapts to recent bias is recorded as a candidate build choice
  for stage C. If taken up, it is tested by time-ordered
  cross-validation, identically at every airport (SPEC 2.5). Nothing is
  decided on it now.
- **D78.3 Open item: non-US competitors.** Before stage C's new
  airports are chosen (D72.8), a read-only probe of non-US
  post-processed station forecasts (for example DWD's MOSMIX): archive
  depth, live feed and station coverage. Nothing is chosen on it now.
- **D78.4 A consequence, recorded.** D77.6's 2026-27 test uses the
  frozen F122 models. No later change to the recipe can be claimed
  against NBM on 2026-27. Such a claim would need new airports or the
  2027-28 forward year.
- **D78.5 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice. The newest SCN
  listed is SCN 26-87 (2026-09-22). With 30 days' notice, the earliest
  go-live is about 29 October 2026.
- **D78.6 NBM v5.0.15 (planning-chat web search, 2026-09-29, not
  checked by this session).** SCN 26-74 (2026-08-26) upgraded NBM to
  v5.0.15, effective immediately, to fix its use of gridded tropical
  cyclone data in the Hawaii domain. It falls inside 2026-27 period A,
  so D77.6's labels for period A name it. Its effect on CONUS
  temperature is not known.
- **D78.7 The 2026-27 scripts (D73.8, D77.6), in two sessions.**
  Session 86: the data-build script
  (`scripts/session86_forward_build.py`), with a gate on spent-year
  station-days; its 2026-27 mode is written but not run. Session 87:
  the scoring script and D77.6's NBM and MAV fetch. Both are committed
  before any 2026-27 row is built. The build script's 2026-27 mode:
  - builds period A only, with GFS v16 file paths. Period B needs
    D73.4's v17 entry first;
  - runs only after period A has ended and its observations are in,
    with the first operational v17 cycle taken from a DECISIONS entry
    (D73.3);
  - prints counts only, never a 2026-27 value;
  - writes only new files, and refuses to overwrite any file.

---

## 2026-09-30: Session 86 finding: the 2026-27 data-build script and its gate

**F128. The 2026-27 data-build script exists and passed its gate. The gate
rebuilt 54 spent-year station-days from fresh GRIB and IEM pulls and every
value equals the committed training set exactly. `--build` was written and
not run. No 2026-27 value was requested or read. Script:
`scripts/session86_forward_build.py` (new; modes `--guard-check`, `--gate`,
`--build`). Full real output: `notes/session-86-output.txt`. Run 2026-09-30.
Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0, eccodes 2.48.0, requests
2.34.2.**

**F128.1 Steps 0 and 1.**
- `git status --porcelain` showed only `?? docs/session-86.md`. The last
  entries were D77 and F127. No D78 or F128 existed in either DECISIONS
  file. Neither `scripts/session86_forward_build.py` nor
  `notes/session-86-output.txt` existed.
- SHA-256 equal to F122: `data/processed/session81_training_set.csv`
  (`ab8f25f2…8d4a`) and `data/models/session81/manifest.json`
  (`03830586…c298`).
- Read: D62, D71.4, D72, D73, F122, F127 and D77 in DECISIONS.md;
  F5, F89, F90, D48, F98, F102, F107 and F116 in DECISIONS-archive.md
  (F100 and F101 were located, not read in full; their fields were read from
  the scripts); SPEC 3.4, 4.5, 5.2, 7.2, 8.1, 8.2, 8.7 and 8.8.
- D78 was copied mechanically (`sed`) from `docs/session-86.md` lines 92 to
  156 into DECISIONS.md lines 1856 to 1920 (heading at line 1854) and checked
  byte-equal with `diff`, before any other edit, network call or data read.

**F128.2 The recipe (Step 2).** Written out in full, with file and line
numbers, in `notes/session-86-output.txt`. In brief: GFS 0.25 degree GRIB2
from `noaa-gfs-bdp-pds`, by byte range from the `.idx`; the run of day D-1
at cycle floor(H/6)x6, forecast hour 24 + (H mod 6); bilinear interpolation
to SPEC 3.4's grid point; the elevation constant on temperature only;
stored at 3 decimals (6 for specific humidity), D's floor after rounding,
T from the two rounded pressures, R native at the lead-26 airports and
de-accumulated (6 h x ave to f024 minus 4 h x ave to f022, over 2) at the
lead-24 airports. The five earlier airports' observation is the record's
last qualifying report; the new code and KSFO use the nearest.
No ambiguity, and no difference between the v16-window, sealed-window,
reserved-year and KSFO scripts that changes a value, was found. Two
differences with no effect: the L and D v16-window scripts checked the
validity date but not the hour (A68b-05); the KSFO scripts fetch all fields
in one pass. The stop rule did not fire.

| station | hour | cycle | lead | grid lat | grid lon | grid elev | constant (degC) | reports at | R |
|---|---|---|---|---|---|---|---|---|---|
| EGLC | 12 | 12z | f024 | 51.487137 | 0.000000 | 4 m | +0.2486 | :50 | de-accumulate |
| LFPG | 12 | 12z | f024 | 49.027008 | 2.578125 | 109 m | -0.1697 | :00 | de-accumulate |
| DSM | 18 | 18z | f024 | 41.529450 | -93.632810 | 285 m | -0.1106 | :54 | de-accumulate |
| YSDU | 2 | 00z | f026 | -32.274643 | 148.593750 | 279 m | +0.2461 | :00 | native window |
| RNO | 20 | 18z | f026 | 39.537918 | -119.765625 | 1344 m | +2.0436 | :55 | native window |
| SFO (KSFO) | 20 | 18z | f026 | 37.546370 | -122.343750 | 1 m | +0.6944 | :56 | native window |

The script read every value in this table from SPEC 3.4 and the two params
CSVs; nothing is typed in. Messages per station-day: 15 at the lead-24
airports, 14 at the lead-26 airports (783 for the sample).

**F128.3 Functions copied (nothing imported from a record script; the record
scripts were not run).**

| new function | source |
|---|---|
| `year_fraction` | `session62_reserved_confirm.py` l.217-219 |
| `find_range` | `session76_grib_pull.py` l.167-177 |
| `bilinear_from_gid` | `session76_grib_pull.py` l.180-207 (record: `session49_upper_air_pull.py` l.148-171) |
| `decode` | `session76_grib_pull.py` l.210-233, with the validity limit checked before any value is read |
| `field_plan` (14 fields; R's second message at lead 24) | `session76_grib_pull.py` l.84-99; `session55_radiation_pull.py` l.137-141, 433-443 |
| `derive` | `session76_build.py` l.155-198; R's de-accumulation from `session55_radiation_pull.py` l.552-562 |
| `pair_nearest` | `session76_build.py` l.230-256 |
| `pair_historical` (gate comparison only) | `session62_reserved_confirm.py` l.321-344 |
| libomp loader shim | `session62_reserved_confirm.py` l.89-99 |

Logic taken from the record but written new: the byte-range fetch loop, the
IEM query (the form in any `data/raw/iem_asos_*.meta.txt`), the persistence
lookup (`session62_reserved_confirm.py` l.394-404), the parsing of SPEC 3.4
and the params CSVs, and all `--build` guards and writers. A tie between
two equally near usable reports keeps the earlier one, as `session76_build.py`
does; this is copied convention, not a new choice. The script's SHA-256 is
in the output file.

**F128.4 `--guard-check` (Step 4, run once, all six cases as specified).**
Gate date 2026-07-31 allowed; 2026-08-01 refused. `--build` refused with no
first-v17-cycle and no `--no-v17`; for period B ("period B needs D73.4's v17
entry first"); when the last period-A day plus 3 days is after the run date
(first v17 cycle 2026-11-15T00, run date 2026-09-30); and when a target date
is on or after 2027-08-01 (first v17 cycle 2027-09-01T00, with a simulated
run date of 2028-03-01 so that only this guard fires). No network call, no
data read. There is no positive control for the `--build` guards, because
`--build` is not run.

**F128.5 The gate (`--gate`).** Sample as fixed in the session prompt: 9
dates at 6 airports, 54 station-days. No station-day lacked a committed row.
Size trial: 3 messages (514,601, 845,948 and 952,479 bytes), mean 771,009,
projected 0.56 GiB against the 5 GiB limit.

**Three gate runs, all reported.**
- **Run 1 (started 09:45 UTC): interrupted, not a script failure.** After the
  GRIB pull, the IEM step failed with "Could not find a suitable TLS CA
  certificate bundle" because the whole project folder had disappeared from
  disk while the run was going (it was later restored intact; `git status`
  matched what it was before). Nothing was compared. Its temporary directory
  was deleted. The cause of the folder's disappearance is not known to this
  session; it was not this script.
- **Run 2 (09:52 to 09:57): all comparisons passed** (below), but the writer
  exercise failed with `ValueError: must have exactly one of create/read/
  write/append mode`. A real bug in `write_new` (mode `"wx"`), in
  `--build` code. Fixed (`"x"`).
- **Run 3 (09:57 to 10:03, the whole gate again, script otherwise unchanged):
  everything passed.** Results below are run 3's; run 2's comparison figures
  were identical.

Run 3: 978 requests (138 `.idx`, 54 IEM, 786 message ranges, of which 3 are
the size trial); 783 of 783 GRIB messages OK, 674,387,577 bytes; 54 of 54
rows built, 0 drops; IEM reports read per airport 430 to 432, none unusable;
0 tie days. Pull times and every URL are in the output file.

| group (columns) | pass |
|---|---|
| B (`temp`, `season_sin`, `season_cos`, `cloud_cover`, `wind_speed_10m`, `temperature_grib_c`) | 54 of 54 |
| L (`lapse_rate_t2_t850`) | 54 of 54 |
| D (`dewpoint_depression_t2m_floored`) | 54 of 54 |
| T (`pressure_tendency_3h_hpa`) | 54 of 54 |
| R (`dswrf_2h_wm2`) | 54 of 54 |
| observation (`obs_c`) | 54 of 54 |
| previous-day observation | 54 of 54 |

Every one of the 12 columns is 54 of 54, and every airport is 9 of 9 in
every group. Exact equality, no tolerance. Mismatches: 0. Pairing-only
differences (nearest against the record's last report): 0. Station-days not
rebuilt: 0. (The session prompt lists pairing-only differences for the
observation; the script applies the same rule to the previous-day
observation. None occurred.)

**Plumbing check (5.4).** All 12 model files' SHA-256 equal F122.5 and
`manifest.json`. Predictions of `B+D,L,R,T` and `B` on each committed row
and its rebuilt row: maximum absolute difference 0 at every airport and
model (9 station-days each). No error was computed and no prediction
printed.

**Writer exercise.** In a temporary directory outside the repo, `--build`'s
own writers wrote the rows, manifest, drop log and 54 raw IEM files; the rows
read back equal to the rebuilt values; a second write was refused. The
directory was deleted.

**F128.6 What `--build` will write** (all new; it refuses to run if any
exists): `data/processed/forward2627_periodA_rows.csv` and `.meta.txt`;
`data/raw/diagnostics/forward2627/periodA_grib_manifest.csv` and
`periodA_drop_log.csv`; `data/raw/iem/forward2627/` (raw IEM responses, each
with a `.meta.txt`). Arguments: `--period A`, one of `--first-v17-cycle
YYYY-MM-DDTHH` or `--no-v17`, and `--decision`. It prints counts only. Untested
parts of `--build`: the argument handling and the per-airport last-day
loop run only through the guard function; its use of the shared build
function and writers is covered by the gate.

**F128.7 What this did not do.**
- No 2026-27 value was requested or read. No message or IEM report valid on
  or after 2026-08-01 was requested, and none was returned.
- No `--build` run, with any arguments.
- No model was fit. No error, MAE, bias, skill or verdict was computed. The
  frozen models were only loaded, to compare their outputs on two identical
  inputs.
- Nothing was written under `data/`. `data/models/` was only read. The two
  A67-15 DSM files were not opened.
- No existing script was edited, and no guard was edited, bypassed or
  disabled. SPEC.md, RESULTS.md, CLAUDE.md, README.md and
  PROJECT-INSTRUCTIONS.md were not edited.
- Nothing was installed. Nothing was committed and no commit message was
  written.

---

## 2026-09-30: Session 87 decision: how the 2026-27 tests are reported, and the scoring and competitor scripts (owner, planning chat)

**D79. Owner decisions, planning chat (after session 86): how the
2026-27 tests (D73, D77.6) are reported, and the scope of the scoring
and competitor scripts (D78.7).** Written at the start of session 87,
before any other edit, network call or data read. No 2026-27 value has
been read or scored. This entry makes D73 and D77.6 precise where they
leave a reporting detail open. It changes no pass rule, rung, day set
or expectation.

- **D79.1 Margin.** Where D73.6 and D77.6 say the write-up leads with
  the smallest margin, the margin is a percentage: 100 x (1 -
  MAE(model)/MAE(baseline)), at full precision, with the difference
  MAE(baseline) - MAE(model) in degC shown beside it.
  - D73: per period, the smallest over the six airports and both halves
    of the bar (raw GFS (GRIB) and persistence), twelve values.
  - D77.6: per period, the smallest over DSM against NBM, RNO against
    NBM, KSFO against NBM and DSM against MAV.
  A failing result has a negative margin, so it leads. Reason: the
  airports' error levels differ, so a percentage compares like with
  like; it is also the form of the record's tables (SPEC 7.4, 8.5).
- **D79.2 Ties.** PASS needs a strictly lower MAE at full precision
  (SPEC 5.3, D73.5, D77.6). An equal MAE is FAIL.
- **D79.3 No days.** If an airport has no complete-case day in a period,
  or has complete-case days but none with a previous-day observation,
  its D73 result for that period is "no verdict (0 days)". It is neither
  a pass nor a fail, and it is reported. D77.6's own rule for a
  competitor with no value in a period (void) is unchanged. Otherwise
  D73.5's rule stands: there is no minimum day count.
- **D79.4 Labels.** Each verdict's season label is its first and last
  target date and the calendar months it covers, for example
  "2026-08-01 to 2026-11-10 (Aug, Sep, Oct, Nov)". NBM and MAV version
  labels (D77.6) come from a DECISIONS entry written before that period
  is scored, naming each version and the cycle it started from. The
  scripts print these labels; they do not infer versions.
- **D79.5 Intervals.** D77.6's descriptive intervals use F125's method
  as F127 used it: 7-day moving blocks, 10,000 resamples, 95% percentile,
  for d and skill. Each period uses a new generator,
  numpy.random.default_rng(87), in this order: DSM against NBM, RNO
  against NBM, KSFO against NBM, DSM against MAV. D73 reports no
  intervals, because it did not pre-register any (D73.8: its scripts
  implement it exactly).
- **D79.6 Periods.** The competitor fetch and the scoring script cover
  both periods, so neither needs editing after any 2026-27 row exists.
  Period B is used only with the first operational v17 cycle from a
  DECISIONS entry (D73.3), and is scored only from a period-B rows file
  made by a later build mode that D73.4's v17 entry allows. If period B
  is not run (D73.3) or is void (D73.4), the scripts are not run for it.
- **D79.7 GFS v17 (planning-chat web search, 2026-09-30, not checked by
  this session).** Still no Service Change Notice. The newest SCN listed
  is SCN 26-87 (2026-09-22). The only v17 notices are still the April
  proposals, PNS 26-29 and PNS 26-30. With 30 days' notice, the earliest
  go-live is about 30 October 2026. PNS 26-30 still says the 0.25 degree
  pgrb2 files remain; this is to be confirmed against the SCN (D73.4).
- **D79.8 Session 87's plan.** Record this entry; write and gate the
  competitor script and the scoring script; record F129; add citations
  of D78, F128 and (if both gates pass) F129 to SPEC 6. Neither script's
  2026-27 mode is run.

---

## 2026-09-30: Session 87 finding: the 2026-27 scoring and competitor scripts and their gates

**F129. The 2026-27 scoring script and the NBM and MAV fetch script exist and
both passed their gates. The competitor gate fetched 21 NBM and 5 MAV
spent-year values from the archives and every one equals the session 85 file
exactly. The scoring gate reproduced F119.3 and F127.4 with the new scoring
core, checked the frozen-model plumbing without computing any error, and
exercised the writers. `--fetch` and `--score` were written and never run. No
2026-27 value was requested, read, built or scored. Scripts:
`scripts/session87_forward_competitors.py` (new; modes `--guard-check`,
`--gate`, `--fetch`) and `scripts/session87_forward_score.py` (new; modes
`--guard-check`, `--gate`, `--score`). Full real output:
`notes/session-87-output.txt`. Run 2026-09-30. Python 3.12.2, numpy 2.5.2,
lightgbm 4.7.0, eccodes 2.48.0, requests 2.34.2.**

**F129.1 Steps 0 and 1.**
- `git status --porcelain` showed only `?? docs/session-87.md`. The last
  entries were D78 and F128. No D79 or F129 existed in either DECISIONS file.
  Neither new script, `notes/session-87-output.txt`, nor any file named
  `forward2627_*` under `data/` existed.
- SHA-256, all equal to the recorded values: `session81_training_set.csv`
  and `data/models/session81/manifest.json` (F122); the twelve model files
  (F122.5); `session85_competitor_points.csv` (F127.3);
  `session78_ksfo_looks_predictions.csv` (F119.4);
  `scripts/session62_reserved_confirm.py` (D70.2);
  `scripts/session86_forward_build.py` (`da2ff50c...4125`, from
  `notes/session-86-output.txt`).
- Read: D62, D71.5, D73, F122, F125, D77, F127, D78 and F128 in
  DECISIONS.md; D70 and F119 in DECISIONS-archive.md; SPEC 3.4, 5.2, 5.3,
  8.5, 8.7 and 8.8; `scripts/session85_nbm_mos_comparison.py`,
  `scripts/session83_confidence_intervals.py` and
  `scripts/session86_forward_build.py` (read, not run).
- D79 was copied mechanically (`sed`) from `docs/session-87.md` lines 97 to
  152 into DECISIONS.md lines 2096 to 2151 (heading at line 2094) and checked
  byte-equal with `diff`, before any script was written, any network call
  was made or any model or data file was read for the gates. (Step 0's
  SHA-256 checks and reading of the three scripts came first, as the prompt
  orders them.)
- Scope note. To learn the field names before writing the MAV code, one saved
  spent-year response (`data/raw/iem_mos/session85/KDSM_GFS_20240731T18Z.json`)
  was opened and its keys and first projection were printed. To learn the
  file layouts, the header and first rows of `session78_ksfo_looks_predictions.csv`,
  `session78_ksfo_looks_grid.csv`, `session85_competitor_points.csv` and
  `session81_training_set.csv` were printed. All are spent-year values already
  on record. Nothing was scored from them.

**F129.2 Functions imported or copied.** Nothing was imported from a record
script except in the scoring gate's G2.

| new function | source |
|---|---|
| competitors: `cycle_and_lead` | `session85_nbm_mos_comparison.py` l.113-122 (copied) |
| competitors: `get` (retries, spacing; adds a request log) | same file, l.285-305 (copied, `Missing` from l.281-282) |
| competitors: `nbm_url`, `META_KEYS`, `grib_meta` | same file, l.308-310, l.313-331 (copied) |
| competitors: `fetch_nbm` | same file, `pull_nbm` l.334-511 (adapted: a generic plan of station-days, the limit is "on or after", a drop log by reason, a message SHA-256) |
| competitors: `fetch_mav` | same file, `pull_mav` l.514-578 (adapted: only the matched projection's `tmp` is read; the time fields of the others are read to match and to check the UTC fields; a drop log by reason) |
| both: `load_spec_airports`, `load_spec_cycles` | `session86_forward_build.py` l.226-263 (adapted: SPEC 3.4's first table) |
| both: `last_period_a_day` | same file, l.284-296 (copied) |
| both: `validate_request` | same file, `validate_build_request` l.299-322 (adapted: period B allowed with a first v17 cycle) |
| competitors: `check_gate_date` | same file, l.278-281 (copied) |
| score: libomp loader shim | `session62_reserved_confirm.py` l.89-99 (copied) |
| score: `bootstrap`, `N_BOOT`, `BLOCK` | `session85_nbm_mos_comparison.py` l.685-686, l.707-718 (copied; identical to `session83_confidence_intervals.py` l.407-417) |
| score: `f109_rows` | `session85_nbm_mos_comparison.py` l.156-196 (copied, with the record module passed in) |
| score: `load_frozen_models` | `session86_forward_build.py` `plumbing` l.1061-1084 (adapted: it also loads the boosters and the mean-bias constants) |
| score, G2 only, imported read-only after the SHA-256 check | `session62_reserved_confirm.py`: `load_family` l.249, `load_base_unfiltered` l.299, `load_obs_all` l.321, `build_complete_case` l.347, `join_obs` l.367, `fit_and_score` l.382, and the constants `AIRPORTS` l.107, `FINAL_CODES` l.118, `FINAL_FEATURE_KEYS` l.127, `CONFIRMATION_FOLD` l.171 |

Written new: the two `validate_request` argument checks, the guards and their
cases, `d73_core`, `d77_core`, `season_label`, the row and points loaders, all
writers, the score printing, the gate's comparison with session 85's printed
lines (`parse_s85_notes`) and every gate step. The scripts' SHA-256 are in
F129.7.

**F129.3 `--guard-check`, both scripts (offline: no network call, no data file
read; each run twice, once while building and once to save the output; the
results were identical).**
- Competitors: gate date 2026-07-31 allowed and 2026-08-01 refused. `--fetch`
  refused with neither `--first-v17-cycle` nor `--no-v17`; for period B with
  `--no-v17`; when the last day plus 3 days is after the run date (first v17
  cycle 2026-11-15T00, run date 2026-09-30; the last period-A day is
  2026-11-15 at all six airports); and when a target date is on or after
  2027-08-01 (first v17 cycle 2027-09-01T00, simulated run date 2028-03-01).
  An existing output file is refused, in a temporary directory outside the
  repo, and an absent one is allowed. Positive controls (the same pure
  function, simulated run dates): period A allowed at run date 2026-11-18
  and refused at 2026-11-17; period B (first v17 cycle 2026-11-15T00, days
  2026-11-16 to 2027-07-31) allowed at 2027-08-03. 11 of 11 cases behaved as
  specified.
- Scoring: `--score` refused with neither v17 option; for period B with
  `--no-v17`; for period B when the period-B rows file does not exist (a path
  check only); when the last day plus 3 days is after the run date; for a
  period range or a rows-file date on or after 2027-08-01; for a rows-file
  date outside its period (2026-07-31 in period A); without
  `--nbm-versions`; when an output file exists (temporary directory); and
  when a rows file's SHA-256 differs from `--rows-sha256` (a small temporary
  file). Positive controls: period A allowed at run date 2026-11-18; a rows
  file whose SHA-256 equals the value passed accepted; no output file
  accepted. 13 of 13 cases behaved as specified.
- The guards for `--fetch` and `--score` also refuse a missing `--decision`.
  Their argument-handling code (`run_fetch`, `run_score`) ran only through
  these pure functions, so it is untested end to end, as `--build` was in F128.6.
  It was checked by reading, and by a static check for undefined names.

**F129.4 The competitor gate (`--gate`, run once; 2026-09-30 12:10:24Z to
12:11:20Z).** The session 85 points file's SHA-256 equals F127.3. The sample is
the fixed one: DSM and RNO 2024-08-01, 2024-11-12, 2025-02-18, 2025-05-28,
2025-07-31, and KSFO those five plus 2025-08-01, 2025-09-03, 2026-04-22,
2026-05-06, 2026-07-29 and 2026-07-31. Every target date is on or before
2026-07-31; the latest valid time requested was 2026-07-31 20:00 UTC; every
message's validity was checked before its value was read.
- **Requests and bytes.** 37 requests: 16 NBM `.idx` (165,500 B), 16 NBM
  message ranges (26,182,145 B) and 5 MAV queries (114,323 B). 16 NBM files
  cover the 21 values (RNO and KSFO share a file where they share a day). The
  script does not count retries; the request log lists each answered request
  once. No GRIB byte was kept; the temporary directory was deleted.
- **Values.** **NBM 21 of 21 equal** to the session 85 file (exact
  equality of the stored value). **MAV 5 of 5 equal.** Drops: none. The MAV
  UTC fields were checked on 105 projections, none unequal (time fields only).
- **NBM grid points**, equal to F127.3's table at 6 decimals and to each
  stored row exactly: DSM 41.541124, 266.34249 (0.873 km); RNO 39.483896,
  240.228363 (0.046 km); SFO 37.619643, 237.629953 (0.433 km).
- **Version check (report only).** All 16 files carry the same 2 m
  temperature message: name "2 metre temperature", short name `2t`, units K,
  level height above ground 2 m, Lambert grid 2,345 x 1,597 at 2,539.703 m,
  packing grid_complex_spatial_differencing. The `.idx` line counts are 161
  (f024) and 114 (f026) for the cycles of 2024-07-31, 2024-11-11 and
  2025-02-17; 164 and 117 for 2025-05-27, 2025-07-30 and later 2025 to
  2026-04-21 cycles; and 157 (f026) for 2026-05-05, 2026-07-28 and
  2026-07-30. The sample covers NBM v4.2, v4.3, v5.0 and v5.0.14 (D77.7,
  F127.5).
- **Writer exercise.** In a temporary directory outside the repo the
  `--fetch` writers wrote the gate's points, manifest, drop log and the 5 raw
  MAV responses; the points read back equal to the fetched values and the raw
  responses read back byte-equal; a second write was refused. The directory
  was deleted.
- Runs: 1 (passed at once; no fix was needed).

**F129.5 The scoring gate (`--gate`, run once; 2026-09-30 12:15:06Z to
12:15:07Z). Offline. All four parts passed.**
- **G1. F119.3 through the D73 core.** The KSFO predictions file's SHA-256
  equals F119.4. Columns used, all from that file: `obs_c`, `raw_gfs_c`,
  `persistence_c` (blank on the one day with no previous-day observation),
  `mean_bias_c`, `B_c`, `BDLRT_c`. The core needs nothing else, so no file
  that `session77_ksfo_looks.py` reads was opened. Every rung MAE equals
  `session78_ksfo_looks_grid.csv` at full precision (`repr`) in both looks
  (raw GFS, persistence, mean-bias, `B`, `B+D,L,R,T`, 5 of 5 each), and
  every day count is equal (look A 364, persistence 363; look B 365, 365).
  Both verdicts are PASS. Margins at 2 decimals: look A +11.83% over raw GFS
  and +16.79% over persistence; look B +20.16% and +19.46%; all equal
  F119.3's.
- **G2. F127.4 through the D77.6 core.** DSM and RNO were refit by F125.1's
  route (functions imported read-only from `session62_reserved_confirm.py`
  after its SHA-256 check, `run_confirm()`'s steps and both guards,
  `B+D,L,R,T` only). KSFO looks A and B used the saved predictions. The
  competitor values are from `session85_competitor_points.csv`.
  `numpy.random.default_rng(85)`, in F127's table order. **All five rows
  equal the record**: n; the model, competitor and raw GFS MAEs (4
  decimals); the three mean errors (4 decimals); d and its interval (4
  decimals); skill and its interval (2 decimals). Precision used:
  `notes/session-85-output.txt` prints the MAEs and mean errors at 4
  decimals, d and its interval at 4 decimals and skill and its interval at 2
  decimals, so those are the highest recorded precision for those figures.
  For the model and raw GFS MAEs, the grid files record full precision, and
  those also equal (`repr`) in all five rows. n is exact (365, 365, 364, 365,
  365). The competitor MAEs, mean errors and intervals have no full-precision
  record.
- **G3. Frozen-model plumbing.** The training set's SHA-256 equals F122.3 and
  the twelve model files and `manifest.json` equal F122.5. On the 54
  station-days of F128's gate sample, the scoring script's own predict path
  and a fresh `lightgbm.Booster(model_file=...).predict` on the same G15 array
  differ by a maximum of 0.0 at every airport and both models (9
  station-days each). No error was computed against any observation.
- **G4. Writers.** In a temporary directory outside the repo, the `--score`
  writers wrote G1's and G2's figures as a stand-in predictions file (744
  rows) and scores file (101 rows). Both read back equal, with floats exact. A
  second write was refused. The directory was deleted.
- Runs: 1 (passed at once; no fix was needed).

**F129.6 What `--fetch` and `--score` will write, and their arguments.** Both
write only new files and refuse to run if any exists.
- `scripts/session87_forward_competitors.py --fetch --period A|B
  (--first-v17-cycle YYYY-MM-DDTHH | --no-v17) --decision <entry>`. Period B
  needs `--first-v17-cycle`. It refuses to run until the run date (UTC) is at
  least 3 days after the period's last target day at all six airports. It
  writes `data/processed/forward2627_period{A,B}_competitor_points.csv` and
  `.csv.meta.txt`; `data/raw/diagnostics/forward2627/period{A,B}_nbm_manifest.csv`
  and `period{A,B}_competitor_drop_log.csv`; and
  `data/raw/iem_mos/forward2627/period{A,B}/` (the raw MAV responses, each with
  a `.meta.txt` giving its query and pull time). It prints counts only, never
  a 2026-27 value.
- `scripts/session87_forward_score.py --score --period A|B
  (--first-v17-cycle YYYY-MM-DDTHH | --no-v17) --rows-sha256 <sha>
  --points-sha256 <sha> --nbm-versions "<text>" --mav-versions "<text>"
  --decision <entry>`. Same timing guard. The two SHA-256 values come from the
  findings that record the build and the fetch; the version text is copied
  from a DECISIONS entry written before the period is scored (D79.4). It
  checks all twelve model files and `manifest.json` against F122.5 before
  computing anything. It writes
  `data/processed/forward2627_period{A,B}_predictions.csv`,
  `forward2627_period{A,B}_scores.csv` and its `.csv.meta.txt`. It prints the
  full D73 and D77.6 tables, the labels, and the smallest margin first in each.
- Order of use, per period: build (`session86_forward_build.py --build`), fetch,
  score. Period B needs a later build mode and D73.4's v17 entry first.

**F129.7 SHA-256 of the two scripts (final; neither was edited after its
gate).**
- `scripts/session87_forward_competitors.py`:
  `8f176562954b5b43bdf110bc292f5b04d6d728d2295df9a178d5a5ff5b23d55c`
- `scripts/session87_forward_score.py`:
  `5a6f32c505a5c0a39577a05f2ac82bfac31994f600fe6edbba3f1e936171de6a`

**F129.8 Readings made where the prompt is silent (for the owner to confirm or
change before period A is run).** None changes a pass rule, a rung, a day set
or an expectation.
- **Timing guard scope.** "At every airport" is read as all six airports, for
  `--fetch` as well as `--score`, although `--fetch` only fetches DSM, RNO and
  KSFO. This can only delay `--fetch`, never allow it early.
- **Draws.** D79.5 fixes the order DSM/NBM, RNO/NBM, KSFO/NBM, DSM/MAV. A
  comparison that is void (no competitor value) or has fewer than 7 days
  consumes no draws, and with fewer than 7 days its intervals are not computed
  (the block length is 7). F125 also made no draws for a failed gate.
- **Zero-row airport.** A rows file with an unknown station code or a missing
  column stops the run. An airport with no rows in the file is D79.3's case,
  "no verdict (0 days)", not a stop.
- **Season label (D79.4).** The first and last target date of the verdict's day
  set, and every calendar month from the first to the last.
- **Margin over persistence (D79.1).** The model's MAE on every complete-case
  day against persistence's MAE on the days with a previous-day observation,
  the day basis of D73.5, F119.3 and SPEC 8.5. G1 reproduces F119.3 this way.
- **File names.** The `.meta.txt` names follow F128.6: `<file>.csv.meta.txt`.
- **MAV projections.** Only the one matched projection's `tmp` is read. The
  time fields of the other projections in a response are read, to match and to
  check that the UTC fields equal the plain ones; their values are never read,
  printed or used. In `--gate` a projection valid on or after the limit stops
  the step; in `--fetch` the limit is applied to the projection that is used,
  because a response for the last run of a period holds later projections by
  design.
- **No size trial.** `--fetch` has no projected-size stop as session 85's pull
  had; a period needs at most a few hundred messages of about 1.5 MB.

**F129.9 What this did not do.**
- No 2026-27 value was requested, received, read, built or scored. No NBM
  message, MOS projection or observation valid on or after 2026-08-01 was
  requested, and none was returned. No `--fetch` or `--score` was run, with
  any arguments.
- No fit except G2's verification refit of DSM and RNO by F125.1's route. The
  frozen F122 models were only loaded and used to predict. No error, MAE, bias
  or skill was computed on the frozen models' training rows (F122.6) and none
  on any 2026-27 row.
- Nothing was written under `data/`. `data/models/` was only read. The two
  A67-15 DSM files were not opened.
- No existing script was edited and no guard was edited, bypassed or
  disabled. No `__pycache__` file of the new scripts was kept.
- Nothing was installed. No account was used. Nothing was committed and no
  commit message was written.

---

## 2026-10-01: Session 88 decision: F129.8 accepted, the non-US competitor probe first, and its rules (owner, planning chat)

**D80. Owner decisions, planning chat (after session 87): F129.8
accepted, the next step, and the rules of the non-US competitor probe
(D78.3).** Written at the start of session 88, before any other edit or
network call. No 2026-27 value has been read or scored.

- **D80.1 F129.8 accepted.** The owner accepts all eight readings in
  F129.8 as written: the timing guard over all six airports; no draws
  for a void comparison or one with fewer than 7 days; a zero-row
  airport is "no verdict (0 days)"; the season label; the persistence
  margin's day basis; the file names; the MAV projection handling; and
  no size trial in `--fetch`. Neither script changes; F129.7's SHA-256
  values stand.
- **D80.2 Next step: D78.3's probe before stage C.** The owner runs the
  read-only non-US competitor probe before stage C is opened. Reason:
  secondary sources say DWD keeps MOSMIX on its open data server for
  only about two days, so if MOSMIX is to be saved, every day of delay
  is lost for good.
- **D80.3 The probe's rules.** DWD MOSMIX first; other non-US
  post-processed station forecasts only where cheap (documentation and a
  handful of requests, no account). Candidates: the Bureau of
  Meteorology's forecasts at Dubbo and the Met Office's site-specific
  forecasts. Live files may be downloaded, but only their metadata is
  printed or recorded, never a forecast value; nothing is saved under
  `data/`. At most one MOSMIX_S all-stations file is downloaded, and only
  if it is under 200 MB. Recorded as F130.
- **D80.4 Matching is not decided.** The probe records MOSMIX's issue
  times, the model runs each issue is built on, and the leads to each
  target hour, beside D77.2's rule for NBM. Any matching rule for a
  MOSMIX comparison is the owner's later decision.
- **D80.5 Daily saves: options recorded, nothing decided (D72.8).** If
  F130 confirms short retention, the owner chooses later between:
  (A) no saving, so MOSMIX has no history anywhere; (B) MOSMIX_L
  single-station files at a short list (EGLC, LFPG and YSDU now, stage
  C's candidate airports later), all four daily issues, well under 1 MB
  a day; (C) the whole map, about 320 MB a day for MOSMIX_L, or only the
  2 m temperature at all stations. Where a saver would run: the owner's
  laptop (free; misses days it is off), GitHub Actions (free; scheduled
  runs can be late or skipped, and stop after 60 days without repo
  activity; the repo is public), or a small cloud machine or bucket
  (reliable; small cost). A saver is new code and needs its own session.
  A MOSMIX test on 2026-27 could still be pre-registered, since no
  2026-27 value has been scored, but it would cover only saved days.
- **D80.6 GFS v17 (planning-chat web search, 2026-10-01, not checked by
  this session).** Still no Service Change Notice. The newest SCN listed
  is SCN 26-87 (2026-09-22). The only v17 notices are still PNS 26-29
  and PNS 26-30. With 30 days' notice, the earliest go-live is about 31
  October 2026.
- **D80.7 Planning-chat notes on MOSMIX (2026-10-01, not checked by this
  session).** No retention period was found in DWD's MOSMIX pages. A
  listing of DWD's MOSMIX_L all-stations directory showed eight issues,
  28 Sep 21z to 30 Sep 15z, about 80 MB each: about two days. A 2022
  discussion in the wetterdienst project said no historical MOSMIX was
  available; Meteostat said it keeps only the latest forecast; a
  Fraunhofer group was said to sell some; DWD's PAMORE research service
  was said to hold about two years of past predictions, possibly not
  MOSMIX. All secondary; F130 checks them.
- **D80.8 Session 88's plan.** Record this entry; run the probe (D80.3);
  record F130. No SPEC edit. Nothing is chosen.

---

## 2026-10-01: Session 88 finding: the non-US competitor probe

**F130. Read-only probe of non-US post-processed station forecasts (D78.3,
D80). DWD MOSMIX was probed against a fixed checklist; the Bureau of
Meteorology (Dubbo) and the Met Office were looked at briefly. MOSMIX keeps
only about two days of issues on DWD's server and no public archive of past
issues was found: class No archive. Nothing was chosen. Script:
`scripts/session88_competitor_probe.py` (new; reads the network and prints;
writes no data file; SHA-256 `e168a0c8d07bade5e27e8539bc7704bae9eed078f87832f8a814a7a56368c214`). Full real output, with every URL,
listing, access time and the documentation read:
`notes/session-88-output.txt`. Run 2026-10-01.**

**F130.1 Steps 0 and 1.** `git status --porcelain` showed only
`?? docs/session-88.md`. The last entries were D79 and F129; no D80 or F130
existed in either DECISIONS file; neither new path existed. D72, D77.1, D77.2,
D78, F123, F124, D76.2 and SPEC 3.4, 4.1, 7.2 were read. D80 was copied
mechanically (`sed`) from `docs/session-88.md` lines 91 to 148 into
DECISIONS.md lines 2414 to 2471 (heading at line 2412) and checked byte-equal
with `diff`, before any other edit or network call.

**F130.2 Retention (the main question).**
- Listings (verified, 2026-10-01 16:20Z and again 16:34Z): MOSMIX_L
  all-stations holds **8 issues**, 2026-09-29 21Z to 2026-10-01 15Z, span
  42 h (about 80 MB each; not downloaded). MOSMIX_S all-stations holds
  **48 hourly issues**, 2026-09-29 16Z to 2026-10-01 15Z, span 47 h (about
  37 MB each). Single-station directories hold the same 8 L issues.
- **The second-listing rule was not met.** The prompt asks for a second
  listing at least six hours after the first. This session could not wait; its
  two listings are 13 minutes apart and identical, so it did not see the
  oldest file go. D80.7's planning-chat listing (secondary) saw 8 issues, 28
  Sep 21z to 30 Sep 15z, which fits a rolling window of 8 L issues.
- DWD's statement: **no statement found** on retention in the MOSMIX product
  pages (DE, EN), the German procedure documentation, the English application
  and KML descriptions, the open data help page and the server README
  (documentation only). A per-product "service profile" is mentioned in the
  README; none was found or read.
- Archive routes (pages only, nobody contacted): DWD open data server, no
  MOSMIX archive folder (verified); Climate Data Center, no forecast folder
  (verified); **PAMORE** (documentation only) holds archived NWP model data,
  "forecasts from the last approx. 1.5 years", only data at least 48 hours
  old, registration for research and education, federal and state authorities
  and disaster prevention; the page never names MOSMIX, so whether it holds
  MOSMIX is unknown. Third parties (all secondary): wetterdienst discussion
  780 (2022: "not possible to get historized mosmix"; Meteostat said it holds
  historical MOSMIX on request but its public service keeps only the latest;
  Kempten and Fraunhofer named; 2023-01: a researcher reported full MOSMIX_L
  coverage back to 2020-08-01, source not named); Meteostat's and Open-Meteo's
  documentation: nothing on MOSMIX found.

**F130.3 Summary table, one row per product.**

| product | archive | retention | issue times | 2 m temperature | stations at EGLC, LFPG, YSDU | class | weakest tag |
|---|---|---|---|---|---|---|---|
| DWD MOSMIX_L | none public | 8 issues, about 2 days (verified); no DWD statement | 03, 09, 15, 21 UTC; on the server about 04:20, 10:15, 16:20, 22:15 | `TTT`, kelvin, "Temperature 2m above surface", hourly steps to +240 h | EGLC P0478 (7.69 km); LFPG 07157 (0.17 km); YSDU none within 10 km (nearest 221.75 km) | **No archive** (about 2 days) | secondary (the third-party holders); retention itself verified |
| DWD MOSMIX_S | none public | 48 hourly issues, about 2 days (verified) | hourly; server time about 40 minutes past the hour | `TTT`, kelvin, 240 hourly steps | same stations | **No archive** (about 2 days) | verified |
| BoM town forecasts (précis, `IDN11060.xml`) | none public found | files overwritten; about a week of other files on the FTP | next routine issue shown in the file; 11:45Z and 18:15Z seen | daily minimum and maximum only, Celsius; no hourly value | Dubbo is a location (NSW_PT047); no EGLC or LFPG | **No archive**; daily only | documentation only (terms), listing verified |
| Met Office site-specific | not stated | not stated | hourly update (reported) | hourly (reported) | not checked | **Blocked** (DataHub account and API key) | secondary |

**F130.4 Station table (SPEC 3.4 positions; DWD cfg positions are degrees and
minutes, converted; DWD procedure documentation FAQ 9.1).**

| airport | MOSMIX station | ICAO | distance, cfg / KML position | height | kind, from the 2026-06 station parameter list (TTT symbol) | single-station directory |
|---|---|---|---|---|---|---|
| EGLC | P0478 LONDON/CITY INTL | EGLC | 7.69 km / 7.81 km (published position is west of the airport) | 5 m, difference 0 | **interpolation station** (`ooo` on all 16 elements) | exists |
| LFPG | 07157 PARIS CH.D.GAULLE | LFPG | 0.17 km / 0.61 km | 108 m, -1 | main (`+++`) | exists |
| YSDU | none within 10 km | - | nearest 94743 MOUNT BOYCE AWS, 221.75 km | 1080 m, +805 | - | not applicable |
| DSM (info) | 72546 | KDSM | 0.27 km | 294 m, 0 | main (`++o`) | exists |
| RNO (info) | 72488 | KRNO | 2.08 km | 1344 m, -1 | main (`++o`) | exists |
| KSFO (info) | 72494 | KSFO | 0.79 km | 6 m, +1 | main (`++o`) | exists |

Symbols (procedure documentation, annex A): `+++` nearly hourly from MOS
equations; `++o` nearly hourly, of which nearly 3-hourly from MOS equations,
the rest interpolated; `ooo` nearly hourly from interpolated equations.

**F130.5 Timing (illustration day D = 2026-10-01, D-1 = 2026-09-30; headers
read from the single-station files of P0478).** Our GFS (SPEC 7.2, D77.2):
EGLC and LFPG 12z on D-1, lead 24 h; YSDU 00z on D-1, lead 26 h. Target
12:00 UTC at EGLC and LFPG.

| MOSMIX_L issue on D-1 | lead to 12:00 UTC | referenced model runs |
|---|---|---|
| 03Z | 33 h | ICON 2026-09-30 00Z, ECMWF/IFS 2026-09-29 12Z |
| 09Z | 27 h | ICON 00Z, IFS 00Z (2026-09-30) |
| 15Z | 21 h | ICON 12Z, IFS 00Z |
| 21Z | 15 h | ICON 12Z, IFS 12Z |

MOSMIX_S issues on D-1 are hourly, leads 13 h (23Z) to 36 h (00Z), so one
S issue (12Z) has a 24 h lead. Only one S header was read (issue 2026-10-01
15Z: ICON 12Z, IFS 00Z), so the model runs behind an S issue at other hours
are unknown. YSDU has no MOSMIX station, so no MOSMIX timing exists for it.
**Observations as predictors (documentation only, procedure documentation
2.1.2 and the 2024-07-01 newsletter):** current station observations enter
the forecast equations as predictors ("Nowcastinformation"); the run starts at
minute 30 and uses the hourly reports of the hour just ended. A MOSMIX issue
on D-1 can therefore use observations up to its own issue time, which our
GFS-based correction does not. This bears on fairness of any later matching.
No matching rule was chosen (D80.4).

**F130.6 Version history (DWD change page; details in the output file).**
2026-06-10 retraining with data to September 2025 (previous: to September
2023), a fix to observation data outside Germany ("especially France and
Hungary": hourly temperature forecasts at affected stations were of "very
poor quality"), and over 300 interpolation stations removed; 2025-06-25
thunderstorm forecasts dropped and new stations; 2025-05-07 more parameters
and main and interpolation stations told apart; 2024-10-30 coefficient
retraining; 2024-07-01 start moved 20 minutes later (minute 10 to 30) and
delivery times changed; 2023-09 retraining and quality control; 2023-01
forecasts for more airports; 2022-10, 2021-03, 2019 and 2018-09 station and
coefficient changes. Any saved history spans several versions, including a
temperature fix that touched France (LFPG).

**F130.7 Step 3.**
- **Bureau of Meteorology (Dubbo).** Anonymous FTP (`ftp.bom.gov.au/anon/gen/fwo/`)
  holds the NSW town forecast `IDN11060.xml` with Dubbo as a location: daily
  minimum and maximum for 8 periods (the first 2 hours long), no hourly or
  02:00 UTC value. Terms: free anonymous access under the Bureau's copyright
  notice; a registered user service with charges for use outside it
  (documentation only; the data-feeds page itself answered HTTP 403, the 403
  text carries the terms). Only current files are on the FTP; no archive
  found. Class: **No archive**, and daily values only.
- **Met Office.** Site-specific "Global Spot" is described as post-processed
  and blended; it needs a DataHub account and API key (free plan 360 calls a
  day), and the pages read state nothing on past forecasts. Per the scope
  guard this session recorded that and stopped. Class: **Blocked**. These two
  points were read through a web fetch tool's summary (secondary).

**F130.8 Requests and bytes.** Honest accounting is in the output file (Part
G). The clean script run made 32 requests and 41,948,793 bytes. The script was
executed five times while it was fixed. **It downloaded the same single MOSMIX_S
file (37,480,319 bytes) three times, in three of those runs, so about 112 MB
was downloaded for what the prompt meant as one download.** The prompt's limit
was one file under 200 MB; the file was one and under the limit, but the
repeat downloads were not intended. 47 manual curl requests (about 10 MB) and
8 web search or fetch calls were also made. No MOSMIX_L all-stations file was
downloaded. Both temporary directories were deleted.

**F130.9 Readings made where the prompt is silent (for the owner to confirm).**
- The "weakest tag" for the MOSMIX rows: retention is verified from listings,
  and the rest of the archive search rests on secondary sources.
- A station is called "main" when its TTT symbol contains a `+` (DWD's
  definition: at least one predictand has station-specific MOS equations);
  P0478's `ooo` makes it interpolation. DWD's cfg gives EGLC's position to the
  nearest minute and the published position is 7.7 km west of IEM's.
- The timing table uses one past day for which all four L issues exist, not a
  future day, so no forecast was needed.
- The Met Office and BoM terms and pages were read through search and fetch
  tools for some items; they are tagged secondary where so.

**F130.10 What this did not do.**
- No forecast value was printed, recorded or saved. KML files were read for
  header fields, element names, station names and positions only; the BoM file
  for element types, area names and period times only.
- No observation was read and no score, error or difference was computed.
- No account, key or sign-up was used or created; no one was contacted and no
  data request was filed. Nothing was installed.
- Nothing was written under `data/`, `data/models/` was not touched, and no
  existing script was edited.
- No matching rule, no save decision (D80.5) and no stage C choice was made.
- SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md were
  not edited. Nothing was committed and no commit message was written.

---

## 2026-10-02: Session 89 decision: F130.9 accepted, MOSMIX saves, stage C opened and its scoping probe (owner, planning chat)

**D81. Owner decisions, planning chat (after session 88): F130.9
accepted, MOSMIX daily saves chosen, stage C opened, and the plan for a
read-only stage C scoping probe.** Written at the start of session 89,
before any other edit or network call. No 2026-27 value has been read or
scored.

- **D81.1 F130.9 accepted.** The owner accepts F130.9's four readings as
  written. F130.8 (one MOSMIX_S file downloaded three times) is noted;
  no action.
- **D81.2 MOSMIX saves: option B (D80.5).** MOSMIX_L single-station
  files, all four daily issues, saved unchanged as downloaded, at:
  EGLC (P0478), LFPG (07157), DSM (72546), RNO (72488) and KSFO (72494)
  (F130.4). Stage C's new airports are added when they are chosen, where
  a MOSMIX station exists.
- **D81.3 YSDU is not on the list.** It has no MOSMIX station within 10
  km; the nearest is 221.75 km away (F130.4).
- **D81.4 Where the saver runs.** GitHub Actions, committing to a
  separate private repository, not the public project repository.
  Because about eight MOSMIX_L issues stay on DWD's server (F130.2), the
  saver may run several times a day and save any issue it does not yet
  hold; a late or skipped run then loses nothing unless the gap is longer
  than about 40 hours. The details are the saver session's.
- **D81.5 Timing.** Not urgent. The saver is new code and gets its own
  session when the owner chooses. Days before it starts are lost, and
  this is accepted. No MOSMIX test is pre-registered.
- **D81.6 EGLC position note (planning chat, not checked by this
  session).** DWD's cfg places P0478 at 0 deg 03 min W; London City
  airport is at about 0 deg 03 min E. If DWD's sign is wrong, the
  station is about 2.5 km from the airport, not 7.7 km. This matters
  only for a later MOSMIX comparison at EGLC. F130 is unchanged.
- **D81.7 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-02, not checked by this session).** Still no Service Change
  Notice. The newest SCN listed is SCN 26-87 (2026-09-22). With 30 days'
  notice, the earliest go-live is about 1 November 2026.
- **D81.8 SPEC 6.** Stage B's bullet gets one sentence citing D78.3,
  F130 and D81 (session 89, Step 2).
- **D81.9 Stage C is opened.** Its claim is judged on new airports only
  (D72.8), chosen before stage C's lock and not scored before it. Stage
  C makes no claim on 2026-27: that year stays for D73 and D77.6, and
  once period A is scored no new test may be pre-registered on it
  (D72.2(a)).
- **D81.10 Stage C defaults.** (a) The daily-maximum definition is
  decided after F131. (b) Bias drift (D78.2) is tested only after the
  curve's baseline exists, as one change at a time (D72.2(b)), by
  time-ordered cross-validation, identically at every airport. (c) New
  candidate airports are chosen in stage C's design session, and added
  to the MOSMIX list where a station exists (D81.2).
- **D81.11 The data route is not decided.** A planning-chat estimate
  (not checked): the hourly curve at both leads needs about 24 GRIB
  files a day per lead, about 10 fields each, over about 1,950 days, so
  about 470,000 byte-range requests and about 370 GB of downloads per
  lead, about 750 GB for both. Downloads are decoded and discarded, not
  stored. Session 89 therefore probes, read only: first, the
  dynamical.org GFS forecast archive, which serves point time series
  without whole global fields (planning-chat web search, 2026-10-02,
  secondary: global, 25 variables, 0.25 deg, leads 0 to 384 h, inits
  every 6 h, CC BY 4.0, processed from NOAA's Open Data Dissemination
  archive), with a reproduction check against committed GRIB values on
  spent-year dates; second, the measured cost of the GRIB route. Scope
  cuts (fewer target hours, the 24-hour lead first, fewer years) and
  running the GRIB pull inside AWS are options for later. Nothing is
  chosen.
- **D81.12 Session 89's plan.** Record this entry; the SPEC 6 edit; the
  probe; record F131. Nothing from 2026-27 is read. Nothing is chosen.

---

## 2026-10-02: Session 89 finding: the stage C scoping probe

**F131. Read-only stage C scoping probe (D81.11). Nothing was chosen. The dynamical.org GFS forecast archive was probed first, then the cost of the GRIB route, then hourly observations and daily-maximum sources. Main results: the archive holds only 4 of the 7 fields behind SPEC 8 in the same form (temperature, wind, radiation, pressure) (no 850 hPa temperature, no 2 m dew point, and its cloud cover is an average, not the record's instantaneous field); its first init is 2021-05-01; its values are stored rounded; a full point series would cost far more than the 5 GB limit, so some parts were run on a reduced sample. The GRIB route's cost came out close to D81.11's planning figure. Script: `scripts/session89_stage_c_scoping.py` (new; reads the network and committed files, prints, writes no data file; SHA-256 `0d65bd5ff6bdd8df74d658b89d40cf15a1e2ef4081a186fe98c9d75b1d705fab`). Full real output: `notes/session-89-output.txt`. Run 2026-10-02. Python 3.12.2.**

**F131.1 Steps 0 to 2.**
- `git status --porcelain` showed only `?? docs/session-89.md`. The last entries were D80 and F130; no D81 or F131 existed in either DECISIONS file; the script and the output file did not exist.
- D81 was copied with `sed` from `docs/session-89.md` lines 102 to 165 to DECISIONS.md lines 2640 to 2703 (heading at 2638) and checked byte-equal with `diff`, before any other edit or network call.
- SPEC 6's Stage B bullet gained the one sentence the prompt gives (git diff in the output file). Nothing else in SPEC changed.

**F131.2 The dynamical.org archive, in brief (3.1.1; route: dynamical-catalog 1.0.1, anonymous Icechunk on S3; accessed 2026-10-02; tag verified unless stated).**
- Dataset `noaa-gfs-forecast`, version 0.2.7, licence CC-BY-4.0, built from NOAA's open data archive (documentation only: STAC collection page). A second dataset, `noaa-gfs-forecast-virtual`, holds byte references into NOAA's own bucket; it was listed and not read.
- **First init 2021-05-01 00:00 UTC.** Inits every 6 h; 7,664 inits from then to 2026-07-29T18 (all present, none missing). So the record's first 39 target days (2021-03-24 to 2021-05-01) have no init in the archive, at all six airports.
- Leads: hourly 0 to 120 h, then 3-hourly to 384 h (209 steps). Every hour from 24 to 53 h is present.
- Grid 0.25 degrees, 721 x 1440, latitude north to south, longitude -180 to 179.75 (same nodes as the record's 0 to 359.75 grid). Chunks: 1 init x 105 leads x 121 x 121 cells (30.25 degrees square), 5.9 MiB uncompressed, in shards of 1 x 210 x 726 x 726. Lead chunk 0 holds hours 0 to 104, so the 24 h lead, the 48 to 53 h lead and every target hour share a chunk.
- 25 variables, listed in the output file. No pressure-level variable. Level 2 m, 10 m, 80 m, 100 m, surface, atmosphere and mean sea level only.
- **Stored rounded** (documentation only: the dataset's own page and its source code on GitHub): mantissa bits kept are 7 for 2 m temperature, RH, cloud, radiation; 6 for 10 m wind; 10 for PRMSL and pressure. My arithmetic from that: 2 m temperature is stored on a 0.0625 degC grid at 8 to 16 degC and 0.125 degC at 16 to 32 degC; PRMSL on 0.64 hPa; DSWRF 4 W/m2 near 700; wind 0.125 m/s at 8 to 16 m/s.
- Missing data: the validation report (documentation only, generated 2026-08-15) lists four incomplete inits, 2022-11-29 12Z and 18Z and 2022-11-30 00Z and 06Z, for every variable, from a NOAA index fault that also hit the record (F90, F116). The dataset's `ingested_forecast_length` coordinate is empty (NaT) for all 7,664 inits, so it cannot show completeness. Update policy: the report says missing hours "will be filled in if the index is corrected upstream"; no statement on later corrections of other values was found.

**F131.3 Field match to SPEC 8 (3.1.2).**

| SPEC 8 field (record) | archive variable | present | same definition? |
|---|---|---|---|
| 2 m temperature, instantaneous (TMP 2 m) | `temperature_2m`, degC, instant | yes | same; but stored rounded (F131.2) |
| total cloud cover, instantaneous (TCDC, "N hour fcst", session 37) | `total_cloud_cover_atmosphere`, average over the previous 1 to 6 h, reset every 6 h | yes | **different** (average, not instantaneous). Not compared. |
| 10 m wind, speed from u and v, km/h (u and v each interpolated) | `wind_u_10m`, `wind_v_10m`, instant | yes | same; stored at 6 bits |
| 2 m dew point (DPT 2 m) | none | **absent** | The archive has `relative_humidity_2m` (the record also holds RH). A dew point could be derived from temperature and RH, which is a different calculation; not tested. |
| 850 hPa temperature (TMP 850 mb) | none | **absent** | no pressure-level variable among the 25 |
| downward shortwave at the surface (DSWRF; 6 h window at lead 24, 2 h at lead 26, de-accumulated to 2 h at lead 24) | `downward_short_wave_radiation_flux_surface`, average over the previous 1 to 6 h, reset every 6 h | yes | same windows as the GRIB message (the hourly leads give the 4 h value at f022, so the de-accumulation can be done); stored at 7 bits |
| pressure behind `pressure_tendency_3h_hpa` (PRMSL at lead and lead minus 3 h) | `pressure_reduced_to_mean_sea_level`, Pa, instant | yes | same; stored at 10 bits (0.64 hPa) |
| 6 h maximum and minimum 2 m temperature | `maximum_temperature_2m`, `minimum_temperature_2m`, "over the previous 1 to 6 h, reset every 6 h" | yes | A full 6 h window only at leads 24, 30, 36 and so on; at other leads the window is shorter. No committed value exists, so nothing was compared. |

**F131.4 Reproduction check (3.1.3). Reduced sample; differences between two copies of the same GFS forecast; no pass or fail.** Dates: the 1st of every 5th month from 2021-06-01 to 2026-06-01, 13 dates per airport (**not** every month: see F131.9, readings 2 and 3), at each airport's own cycle and lead (EGLC and LFPG 12z lead 24; DSM 18z lead 24; YSDU 00z lead 26; RNO and KSFO 18z lead 26; each equals SPEC 3.4 and 7.2, checked in code). The archive value was formed as the record forms it (SPEC 8.8 G6, no elevation correction). Units: degC, km/h, %, hPa, W/m2. "Missing" columns: no row was missing on either side. Cloud, dew point and 850 hPa temperature were not compared (F131.3).

| airport | field | rows | missing archive | missing committed | mean abs diff | largest abs diff | exact at 3 dp |
|---|---|---|---|---|---|---|---|
| EGLC | t2m | 13 | 0 | 0 | 0.0178 | 0.0448 | 0 |
| EGLC | wind_kmh | 13 | 0 | 0 | 0.0428 | 0.0969 | 1 |
| EGLC | rh2m | 13 | 0 | 0 | 0.0660 | 0.1953 | 0 |
| EGLC | msl_hpa | 13 | 0 | 0 | 0.1465 | 0.2920 | 0 |
| EGLC | msl_m3_hpa | 13 | 0 | 0 | 0.1724 | 0.2979 | 0 |
| EGLC | tend | 13 | 0 | 0 | 0.1824 | 0.4410 | 0 |
| EGLC | dswrf_lead | 13 | 0 | 0 | 0.4708 | 1.7650 | 0 |
| EGLC | dswrf_m2 | 13 | 0 | 0 | 0.2127 | 0.9550 | 0 |
| EGLC | dswrf_2h | 13 | 0 | 0 | 1.3183 | 5.4784 | 0 |
| LFPG | t2m | 13 | 0 | 0 | 0.0169 | 0.0486 | 1 |
| LFPG | wind_kmh | 13 | 0 | 0 | 0.0211 | 0.0456 | 0 |
| LFPG | rh2m | 13 | 0 | 0 | 0.0493 | 0.1134 | 0 |
| LFPG | msl_hpa | 13 | 0 | 0 | 0.1013 | 0.2503 | 0 |
| LFPG | msl_m3_hpa | 13 | 0 | 0 | 0.1286 | 0.2679 | 0 |
| LFPG | tend | 13 | 0 | 0 | 0.1612 | 0.2715 | 0 |
| LFPG | dswrf_lead | 13 | 0 | 0 | 0.3337 | 1.3520 | 0 |
| LFPG | dswrf_m2 | 13 | 0 | 0 | 0.1228 | 0.4110 | 0 |
| LFPG | dswrf_2h | 13 | 0 | 0 | 0.8425 | 3.2350 | 0 |
| DSM | t2m | 13 | 0 | 0 | 0.0102 | 0.0308 | 2 |
| DSM | wind_kmh | 13 | 0 | 0 | 0.0252 | 0.0466 | 0 |
| DSM | rh2m | 13 | 0 | 0 | 0.0490 | 0.1526 | 0 |
| DSM | msl_hpa | 13 | 0 | 0 | 0.1257 | 0.2390 | 0 |
| DSM | msl_m3_hpa | 13 | 0 | 0 | 0.0824 | 0.2056 | 0 |
| DSM | tend | 13 | 0 | 0 | 0.1237 | 0.2770 | 0 |
| DSM | dswrf_lead | 13 | 0 | 0 | 0.3908 | 1.5092 | 0 |
| DSM | dswrf_m2 | 13 | 0 | 0 | 0.1623 | 0.3828 | 0 |
| DSM | dswrf_2h | 13 | 0 | 0 | 1.1450 | 4.0290 | 0 |
| YSDU | t2m | 13 | 0 | 0 | 0.0245 | 0.0546 | 1 |
| YSDU | wind_kmh | 13 | 0 | 0 | 0.0207 | 0.0449 | 0 |
| YSDU | rh2m | 13 | 0 | 0 | 0.0371 | 0.0832 | 1 |
| YSDU | msl_hpa | 13 | 0 | 0 | 0.0899 | 0.2204 | 0 |
| YSDU | msl_m3_hpa | 13 | 0 | 0 | 0.0943 | 0.1900 | 0 |
| YSDU | tend | 13 | 0 | 0 | 0.1055 | 0.3009 | 0 |
| YSDU | dswrf_lead | 13 | 0 | 0 | 0.6177 | 1.5379 | 0 |
| YSDU | dswrf_2h | 13 | 0 | 0 | 0.6177 | 1.5379 | 0 |
| RNO | t2m | 13 | 0 | 0 | 0.0181 | 0.0473 | 1 |
| RNO | wind_kmh | 13 | 0 | 0 | 0.0141 | 0.0379 | 1 |
| RNO | rh2m | 13 | 0 | 0 | 0.0350 | 0.0875 | 0 |
| RNO | msl_hpa | 13 | 0 | 0 | 0.1010 | 0.2439 | 0 |
| RNO | msl_m3_hpa | 13 | 0 | 0 | 0.1481 | 0.2471 | 0 |
| RNO | tend | 13 | 0 | 0 | 0.1827 | 0.4320 | 0 |
| RNO | dswrf_lead | 13 | 0 | 0 | 0.6005 | 1.6731 | 0 |
| RNO | dswrf_2h | 13 | 0 | 0 | 0.6005 | 1.6731 | 0 |
| SFO | t2m | 13 | 0 | 0 | 0.0119 | 0.0368 | 0 |
| SFO | wind_kmh | 13 | 0 | 0 | 0.0199 | 0.0506 | 0 |
| SFO | rh2m | 13 | 0 | 0 | 0.0433 | 0.0879 | 0 |
| SFO | msl_hpa | 13 | 0 | 0 | 0.1389 | 0.2650 | 0 |
| SFO | msl_m3_hpa | 13 | 0 | 0 | 0.0678 | 0.2060 | 1 |
| SFO | tend | 13 | 0 | 0 | 0.0900 | 0.2538 | 0 |
| SFO | dswrf_lead | 13 | 0 | 0 | 0.4075 | 1.1492 | 0 |
| SFO | dswrf_2h | 13 | 0 | 0 | 0.4075 | 1.1492 | 0 |

Reading: the 2 m temperature differences are 0.010 to 0.025 degC on average and at most 0.055, at the size the stored rounding gives. Exact matches at 3 decimals are rare (1 or 2 of 13 at most), as the rounding predicts. Pressure differs by 0.07 to 0.17 hPa on average, so the 3 h tendency differs by 0.09 to 0.18 hPa on average and up to 0.44. The de-accumulated 2 h radiation at the three lead-24 airports differs by 0.8 to 1.3 W/m2 on average (up to 5.5), larger than the lead-26 airports' 0.4 to 0.6, because the de-accumulation multiplies the rounding. **Second cycle and lead (leads 48 to 53 h):** the committed GRIB files hold one lead per airport (24 at EGLC, LFPG and DSM; 26 at YSDU, RNO and KSFO), so no committed value exists at another lead or cycle: skipped, as the prompt directs.

**F131.5 Speed and size, and the two extrapolations (3.1.4, 3.2). All figures here are ESTIMATES unless marked measured.**

*dynamical.org, one series (2 m temperature at EGLC, the four surrounding points, leads 24 to 53 h).* The full read is every init from 2021-05-01 to 2026-07-29T18, 7,664 inits, one inner chunk each. Its size from the shard indexes (61 inits spread over the archive): mean 1.33 MB per chunk, so about 10.2 GB for the series, **above the 5 GB limit**. So a strided read was done instead: every 24th init, 320 inits, 38,400 values. **Measured:** 1,031 s (3.22 s per chunk read), about 428 MB (from the shard indexes; the library reports no bytes), 0 errors. Extrapolated by 23.95: about 412 min and 10.2 GB for the one series.

*dynamical.org, all fields present, both leads, all six airports.* The six airports' boxes touch 5 distinct spatial chunks (EGLC (1,5), LFPG (1,6), DSM (1,2), YSDU (4,10), RNO and SFO (1,1); latitude chunk, longitude chunk). Each read is one init x one spatial chunk x one variable, and serves every hour and both leads. Mean compressed chunk size over 25 inits x 5 chunks: temperature 1.57 MB, wind u 2.14, wind v 2.17, PRMSL 0.50, DSWRF 1.28, total cloud 1.36 (costed for completeness). For 7,664 inits x 5 chunks = 38,320 reads per variable: 60, 82, 83, 19, 49 and 52 GB. **Total six variables: 229,920 chunk reads, about 346 GB compressed** (about 294 GB without the cloud row). At 3.22 s per sequential read: about 206 h. Dew point and 850 hPa temperature cannot come from this archive.

*GRIB route (noaa-gfs-bdp-pds, 2024-03-14 runs, byte ranges as the record does).* All 132 `.idx` files f021 to f053 for the four cycles answered 200 (f024 to f053 asked; f021 to f023 added because the pressure tendency needs the lead minus 3 h hour). **Every one of the 8 fields is present in every file at every hour, in all four cycles; no hour has a field missing.** DSWRF's window is not constant: at f024, f030, f036, f042 and f048 it is a 6 h average, at f026 a 2 h average, and so on, resetting every 6 h, the same in all four cycles (full list in the output file). **Measured fetch:** 208 messages (24 files x 8 fields = 192, PRMSL at f021 to f023 for 4 cycles = 12, DSWRF at f022 for 4 cycles = 4), all well formed (GRIB marker, edition 2, length field equal to the bytes, end marker 7777; nothing decoded), 177.7 MB (the limit is 500 MB), 279 s, mean 1.34 s per message request (max 8.45), mean 0.55 s per `.idx` request, mean message 854 kB. Extrapolation, one global field serves all airports: 208 messages and 36 `.idx` files per day per lead; 1,956 days (2021-03-24 to 2026-07-31); two leads (the 48 h lead has the same file structure but was not fetched): **813,696 message requests plus 140,832 `.idx` requests = 954,528 requests; 695 GB (348 GB per lead); 324 h of sequential time at the measured rate** (the record used 48-way concurrency, F90; not measured here).

*Side by side with D81.11's planning figure (about 470,000 requests, 370 GB per lead, 750 GB for both; not checked).* GRIB: 954,528 requests (twice the planning count, because it counts the pressure and radiation extra hours and the `.idx` files), 348 GB per lead, 695 GB for both: close on bytes. dynamical.org: 229,920 chunk reads and about 346 GB for all six variables at five airports' chunks, which is about half the GRIB bytes and a quarter of the requests, but with 4 of 7 fields in the same form and rounded values (F131.2, F131.3).

**F131.6 Hourly observations (3.3, counts only, committed files).** For each airport the six yearly routine files (report_type 3, UTC, columns `tmpc` and `dwpc` only; no raw METAR text) hold every hourly report, 46,734 to 46,937 rows from 2021-03-24 (RNO's first report is 05:55) to 2026-07-31. Usual minute: EGLC :50, LFPG :00 (95 rows at :30), DSM :54, YSDU :00 (177 rows at :30), RNO :55, SFO :56. Days (of 1,956) with at least one usable report within 15 minutes of every one of the 24 whole hours: EGLC 1,933, LFPG 1,875, DSM 1,946, YSDU 1,690, RNO 1,930, SFO 1,931. The 24-row count for each airport (hour, days) is in the output file; the hour counts run from 1,926 to 1,956 at EGLC, LFPG, DSM, RNO and SFO, and from 1,928 to 1,942 at YSDU. All hours are already committed; the query is each file's `.meta.txt` URL. Nothing was fetched.

**F131.7 Daily-maximum sources (3.4).**

| airport | METAR 6 h and 24 h maximum groups | official daily climate maximum | maximum of the hourly reports: UTC window of the local standard-time day |
|---|---|---|---|
| EGLC | not counted (no METAR text committed); US-style groups are a US practice (secondary: Wikipedia METAR page), so none expected: unknown | unknown (not read) | 00:00 to 24:00 UTC (standard offset +0) |
| LFPG | as EGLC | unknown (not read); SYNOP groups carry a maximum "over the past day" in the one example read (secondary: Wikipedia SYNOP page); its exact window is unknown | 23:00 to 23:00 UTC (+1) |
| DSM | not counted (needs the `metar` field, F131.6); the US groups exist per the secondary source | NWS climate report (CLI): day window and archive not read: unknown | 06:00 to 06:00 UTC (-6) |
| YSDU | as EGLC | unknown (not read) | 14:00 to 14:00 UTC (+10) |
| RNO | as DSM | as DSM | 08:00 to 08:00 UTC (-8) |
| SFO | as DSM | as DSM | 08:00 to 08:00 UTC (-8) |

IEM's download page (documentation only) lists "Raw METAR" and no 6 h or 24 h maximum field, so counting the groups needs the raw text. The NWS directive PDF could not be read here (no PDF text tool, none may be installed), and no page was read for Meteo-France, the UK Met Office or the Bureau of Meteorology: those cells are unknown, not findings. A day window is a stage C choice; none is made here.

**F131.8 Notes for the owner, not decisions.**
- L (850 hPa temperature) and D (dew point) cannot come from the dynamical.org archive, and its cloud cover is a different field; the recipe's source for them would remain NOAA's GRIB.
- The archive's rounding (F131.2) is coarse for the pressure tendency (3 h change of a field stored at 0.64 hPa) and for the de-accumulated radiation.
- The archive's first init, 2021-05-01, costs 39 training days at every airport.
- A point time series from the archive is slow and large, because each chunk is one init and a 30-degree square: 7,664 reads per variable and chunk. Running it from inside AWS us-west-2 was not measured.
- The 2022-11-29 12Z to 2022-11-30 06Z hole is in both routes.

**F131.9 Readings made where the prompt is silent (for the owner to confirm or change).**
1. The dataset probed is `noaa-gfs-forecast`, the materialised copy. The "virtual" copy was listed and not read.
2. **The first reproduction run hung and was killed.** It was started 2026-10-02 about 11:09 UTC for all 63 monthly dates; after its line for 48 of 63 dates (about 2.7 GB read) the process sat at 0% CPU for hours (the machine's clock also jumped, so it may have slept) and was killed. Its in-memory results were lost. With about 3.7 GB then spent of the 5 GB limit, a rerun of all dates did not fit. The rerun used **every 5th monthly date (13 of 63, 2021-06-01 to 2026-06-01), which covers all 12 calendar months over the five years but is fewer rows than the prompt asked for**, with a graceful stop added at the byte budget. The code was changed (loop order, `--date-step`, a budget stop that prints what was read) between the trial and the runs; the output file lists all runs.
3. Because 2021-05-01 is not in the reduced set, no table row shows the archive missing an init; that is shown by the metadata (F131.2).
4. Reproduction rows added beyond the prompt's list: 2 m relative humidity (as the archive's only moisture field), PRMSL at the lead and at the lead minus 3 h, and the DSWRF average to the lead, to lead minus 2 h and the 2 h value. The tendency is formed from the archive's full-precision values (the record rounds each pressure to 3 decimals first).
5. Bytes are estimated from the shard indexes (the compressed size of each inner chunk touched, plus the index reads); the library reports none. The 5 GB limit is taken as 5 x 10^9 bytes. Total spent, about 4.0 to 4.1 GB: trial 0.12, killed run about 2.7 to 2.8 (its last log line, 2,715 MB, is a lower bound), reduced run 0.72, speed test 0.43.
6. The speed test used EGLC, a strided read (every 24th init) and the extrapolation by the stride. The all-fields estimate uses mean chunk sizes from 25 inits and counts each variable's reads for all 7,664 inits and 5 chunks.
7. The 24 h lead GRIB plan costs the record's messages: the 8 fields at f024 to f029, PRMSL at f021 to f023 and DSWRF at f022 only (the lead-24 airports' de-accumulation). How radiation would be handled at leads 25, 27, 28 and 29 is a stage C design question and was not costed. The 48 h lead was assumed to have the same structure.
8. The xarray open reads the full init axis, so labels after 2026-07-29T18 were in memory (axis labels, not forecast values). Only the last label was printed (2026-10-02T00:00) as the archive's last init. No forecast value after 2026-07-31T23:00 was read, printed or used.
9. The hour assignment for observations follows SPEC 8.8 G2 and G3 (nearest whole hour, :30 goes up, 15 minutes inclusive); counts are over target days 2021-03-24 to 2026-07-31 and use the six yearly routine files only.
10. The mantissa-bit settings come from the project's source code on GitHub (documentation only); the spacing figures are my arithmetic.
11. Some pages were read by plain download and tag-stripping (not a summarising tool). The quoted web text in the output file contains a few em-dashes; they are the sources' own.

**F131.10 Records, installs, requests, bytes, clean-up.**
- Packages, in a throwaway virtual environment inside the temporary directory: dynamical-catalog 1.0.1, xarray 2026.9.0, zarr 3.4.0, icechunk 2.2.2, numpy 2.5.3, pandas 3.0.6, fsspec 2026.9.0, and their dependencies (listed in the output file). The project's environment and `requirements.txt` were not touched.
- dynamical.org: at least 2,550 chunk reads (trial 72, killed run at least 1,692, reduced run 468, speed test 320) and several hundred shard-index reads (312 in the reduced run; the others not all counted), about 4.0 to 4.1 GB estimated (F131.9, item 5). GRIB: 132 `.idx` and 208 byte-range requests, 183,116,897 bytes (5.45 MB of `.idx`, 177.7 MB of messages), one connection at a time. About 14 documentation pages were downloaded (a few more than once while testing). No account, key or email parameter was used.
- **The temporary directory (with the virtual environment and the 208 downloaded GRIB messages, deleted by the script after the check) was deleted at the end; the path no longer exists.**

**F131.11 What this did not do.**
- No forecast valid after 2026-07-31T23:00 UTC and no init after 2026-07-29T18:00 was read; no observation after 2026-07-31 was read. Nothing from 2026-27 was read.
- No score: no error, MAE or skill of any forecast against an observation, on any year. The only comparisons were between the archive and the committed copy of the same GFS forecast, on spent-year dates.
- No observed temperature value was printed, summarised or recorded; observations were counted only.
- No raw forecast value was printed.
- No account, key, token, paid tier, contact or data request. Nothing written under `data/`; `data/models/` was not touched.
- No existing script was edited. The project's environment and `requirements.txt` were not touched. RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md were not edited; SPEC was edited only as Step 2 says.
- No choice of data route, daily-maximum definition, airport or any other stage C design. Nothing was committed and no commit message was written.

---

## 2026-10-03: Session 90 decision: F131 accepted, the end goal reworded, and stage C's design (owner, planning chat)

**D82. Owner decisions, planning chat (after session 89): F131
accepted, the end goal reworded, and stage C's design: target and
horizon, data route, airports, the claim batch rule and the daily
maximum.** Written at the start of session 90, before any other edit or
network call. No 2026-27 value has been read or scored.

- **D82.1 F131 accepted.** The owner accepts F131 and all eleven
  F131.9 readings, including the reduced reproduction sample (13 of 63
  dates) and the strided speed test. Its conclusions stand: the
  dynamical.org archive lacks two of the recipe's inputs (850 hPa
  temperature, 2 m dew point) and defines cloud cover differently, so
  it is not used; the GRIB route holds every field at every hour.
- **D82.2 The end goal, reworded (replaces D72.1's wording).** A
  private, live tool for ten or more airports that corrects every GFS
  run (four a day), as each run arrives, into an hourly temperature
  curve out to the forecast horizon, plus the daily maximum; the
  horizon is 24 hours first and 48 hours later; then a choice of which
  weather model is corrected, plus a blend; and probabilistic ranges.
  It stays a private product built with good academic practice (D72.1,
  D72.2(d)). The rest of D72 is unchanged.
- **D82.3 Stage C's target and horizon.** The corrected forecast is
  made from every GFS cycle (00, 06, 12 and 18 UTC), for every forecast
  hour from 0 to 24 first. Forecast hours 25 to 48 are added later by a
  separate, additive pull; nothing in the first pull is repeated. The
  daily maximum is part of stage C's target (D82.8).
- **D82.4 The data route.** NOAA's GFS GRIB files on
  `noaa-gfs-bdp-pds`, fetched by byte range as the record does (SPEC
  7.2). The pull runs on GitHub Actions in the public project
  repository, as resumable chunks (each job is capped at 6 hours); the
  first chunk measures speed. Each global field is downloaded, the
  values at the four grid points around each airport are read out, and
  the field is discarded: no global field is kept. Fields: the record's
  eight (2 m temperature, total cloud cover, 10 m u and v wind, 2 m dew
  point, 850 hPa temperature, downward shortwave radiation at the
  surface, mean sea level pressure) plus GFS's 2 m maximum and minimum
  temperature. Kept: the raw value at each of the four grid points, per
  airport, field, cycle and forecast hour, so interpolation choices stay
  open. Period: every cycle and forecast hour whose valid time lies
  between 2021-03-24T00:00 and 2026-07-31T23:00 UTC; nothing from
  2026-27. Estimated at about 100 files a day, about 1.6 to 1.8 TB of
  downloads and about 1.5 GB kept for 47 airports (planning-chat
  estimate from F131, not checked). The kept files are published as
  GitHub Release files and downloaded once to the owner's laptop, so
  the repository stays small. Gate: at each existing airport's target
  hour, cycle and lead, the new values equal the committed ones. The
  design details are session 91's.
- **D82.5 What is not decided.** Whether one model takes lead time as an
  input or each lead has its own model; whether the daily maximum is
  read off the corrected curve or has its own model; and stage C's
  claim design (bar, looks, lead bands). These are fixed by
  time-ordered cross-validation on the development airports (D82.6) or
  at stage C's lock, before any claim airport's held-out data is read.
  Stage C's SPEC section is written at its lock. Bias drift follows
  D81.10(b).
- **D82.6 The airports.** The owner's 47-airport list, by ICAO code and
  the owner's region label:
  Europe: EHAM, LTAC, EFHK, LTFM, EGLC, LEMD, LIMC, UUWW, EDDM, LFPB,
  EPWA.
  North America: KATL, KAUS, KORD, KDAL, KBKF, KHOU, KLAX, MMMX, KMIA,
  KLGA, KSFO, KSEA, CYYZ.
  South America: SAEZ, SBGR.
  Asia: ZBAA, RKPK, ZUUU, ZUCK, ZGGG, OEJN, OPKC, WMKK, VILK, RPLL,
  ZSQD, RKSI, ZSPD, ZGSZ, WSSS, RCSS, LLBG, RJTT, ZHHH.
  Africa: FACT. Oceania: NZWN.
  All 47 are in the pull and are the product's airports. EGLC and KSFO
  are already spent. The 45 others are new. **Until a later decision
  says otherwise, no new airport's data is used for any build choice:**
  build choices use the six development airports (EGLC, LFPG, DSM,
  YSDU, RNO, KSFO) only, so every new airport stays clean for this and
  later claim batches (D72.2(a), D72.3 "Ongoing"). Whether the MOSMIX
  list (D81.2) grows to new airports is left to the saver session;
  session 90 records which have a station within 10 km.
- **D82.7 The claim batch: rules fixed before any check is run.** Six
  airports, drawn by this rule and nothing else:
  (a) Excluded: EGLC and KSFO (spent), and LFPB (about 9 km from LFPG, a
  development airport, so weak evidence; it stays in the product).
  (b) Eligible: an airport whose saved hourly observations give a usable
  daily maximum (D82.8) on at least 90 percent of local days in
  2021-03-24..2026-07-31, and on at least 90 percent of local days in
  its held-out window 2024-08-01..2026-07-31. A local day counts only if
  it starts on or after 2021-03-24T00:00 UTC and ends on or before
  2026-07-31T23:59 UTC. An airport with no IEM archive is not eligible.
  (c) Strata and sizes, in this order: Europe 1; North America 2; Asia
  2; South (the owner's South America, Africa and Oceania labels
  together) 1.
  (d) Draw: Python's `random.Random(20261003)`, one generator for the
  whole draw. For each stratum in (c)'s order, `sample` its eligible
  airports, sorted by ICAO code, for its size. If a stratum has fewer
  eligible airports than its size, take them all, and after the last
  stratum fill the shortfall by `sample` from all remaining eligible
  airports, sorted by ICAO code, with the same generator. Record the
  Python version.
  (e) Each drawn airport's held-out window is 2024-08-01..2026-07-31
  (D72.4); its earlier years are for training. Its looks are fixed at
  stage C's lock.
- **D82.8 The daily maximum (stage C's target).** From the routine
  hourly reports (SPEC 3), at every airport: the local calendar day,
  midnight to midnight in the airport's own time zone (civil time,
  daylight saving included); each report assigned to its nearest whole
  hour by SPEC 8.8 G2 and G3; the day's maximum is the highest usable
  hourly value. A day is usable only if usable hours are at least its
  number of hours minus 2 (22 of 24; 21 of 23 and 23 of 25 on
  clock-change days). A peak between hourly reports is missed; this is
  accepted, being the same everywhere. It is not meant to match any
  outside published figure; the aim is accuracy.
- **D82.9 SPEC.** SPEC 1's end-goal paragraph is reworded to D82.2, and
  SPEC 6's stage C bullet records D81 and D82 (session 90, Step 2).
- **D82.10 Sequence.** Session 90: this entry, the SPEC edits, the
  airport metadata check (counts only) and the draw. Session 91: build
  the GitHub Actions pull and run a small local test chunk through
  D82.4's gate. The owner then pushes and starts the full pull. Session
  92: verify the extracts.

---

## 2026-10-03: Session 90 finding: the airport metadata check and the claim batch

**F132. Stage C's 47-airport metadata check (D82.6) and the claim batch draw (D82.7). All 47 airports are in IEM, one station each; the 45 new airports' hourly reports were downloaded and saved, and only counted. The draw ran once and named six airports: EDDM, KORD, CYYZ, ZGSZ, ZUCK and NZWN. Script: `scripts/session90_airport_check.py` (new; modes `--collect` and `--decide`; SHA-256 `c55bab8dc736c2d43a66d640892038e19b2cb517cf5dc2f812e6c9eba6310a8d`). Table: `data/processed/session90_airports.csv` (47 rows, SHA-256 `b53b689f2226e043228725938ad7c47c2069f4831626cc662118559393465db7`, with a `.meta.txt`). Full real output: `notes/session-90-output.txt`. Run 2026-10-03. Python 3.12.2, eccodes 2.48.0, requests 2.34.2.**

**F132.1 Steps 0 to 2.**
- `git status --porcelain` showed only `?? docs/session-90.md`. The last entries were D81 and F131; no D82 or F132 existed in either DECISIONS file; the script, output file and table did not exist. D72, D81, F130, F131, SPEC 1, 3, 4, 6 and 8.8 were read, and the `.meta.txt` of the committed DSM 2021 file.
- D82 was copied mechanically (`sed`) from `docs/session-90.md` lines 94 to 205 into DECISIONS.md lines 2859 to 2970 (heading at line 2857) and checked byte-equal with `diff`, before any other edit or network call.
- SPEC 1's end-goal paragraph and SPEC 6's stage C bullet were replaced as Step 2 says (both passages were found exactly; `git diff -- SPEC.md` is in the output file). Nothing else in SPEC changed.

**F132.2 Identity and position (3.1).** Source: IEM's station metadata, `https://mesonet.agron.iastate.edu/api/1/station/<id>.json`, accessed 2026-10-03 (tag: verified). Each ICAO code was looked up, and for the 11 US airports its three-letter form too; only `*_ASOS` networks count. **All 47 matched exactly one IEM station: none missing, none ambiguous.** US airports use the three-letter id (ATL, AUS, ORD, DAL, BKF, HOU, LAX, MIA, LGA, SFO, SEA), the others the ICAO code. Positions, elevations and time zones are in the table file. Two readings: IEM lists NZWN (Wellington) under the network `NF__ASOS`; and IEM's time zone for ZUUU and ZUCK is `Asia/Chongqing` (a legacy zone name; it loaded). **EGLC and KSFO still match SPEC 3.4** at its precision (EGLC: 51.50528, 0.05528, 5 m, 2.6 m from SPEC's position; KSFO: 37.61897, -122.37489, 5 m, 3.5 m). **LFPB to LFPG: 9.47 km** (SPEC 3.4's position for LFPG).

**F132.3 GFS grid box, land, sea and terrain (3.2, 3.3).** File `gfs.20240314/00/atmos/gfs.t00z.pgrb2.0p25.f000` (both messages were in f000; f001 not needed). Two messages read by byte range, nothing else: `LAND:surface` (bytes 498234083-498266118, 32,036 B) and `HGT:surface` (409252673-409745115, 492,443 B). Each was checked for identity (discipline, category, number, surface type), run date and time, and validity 2024-03-14 00:00. The box and weights follow SPEC 8.8 G6, at IEM's airport position. **Code check:** at KSFO's SPEC 3.4 grid point the sea weight is 0.3750 (F117.3: 0.375) and the model height 94.47 m (SPEC 3.4 notes: 94.47 m). **18 airports have sea in the grid box (land fraction under 1.0):** LTFM, KLAX, KSFO, CYYZ (lake), RKPK, OEJN, OPKC, WMKK, RPLL, ZSQD, RKSI (land 0.0000), ZSPD, ZGSZ, WSSS, RCSS, RJTT, FACT, NZWN. This is a flag only; it excludes nothing. Of the claim batch, ZGSZ (land 0.2223), CYYZ (0.8609) and NZWN (0.6912) carry the flag. Model-height differences run from -58.2 m (ZSQD) to +185.0 m (LTAC); the three beyond 100 m in size are LTAC +185.0, RCSS +183.5 and MMMX +163.6. All 47 are in the table below and in the file.

**F132.4 Hourly observations (3.4).** Request as the committed files (same parameters; `.meta.txt` in the same format, with row count and SHA-256 added). Six yearly pieces per airport (2021-03-24 to 2021-12-31, 2022, 2023, 2024, 2025, then 2026-01-01 to 2026-07-31), 45 airports, 270 files and 270 `.meta.txt` files under `data/raw/`. **No row was later than 2026-07-31 23:59 UTC and none was dropped.** Row counts per airport are 39,041 (MMMX) to 46,935 (WSSS); the usual report minute, rows with no usable temperature, and the days per whole hour are in the output file. The counting code was first checked against F131.6 on the committed files: the count of UTC days with all 24 hours equals F131.6 at all six airports (EGLC 1,933, LFPG 1,875, DSM 1,946, YSDU 1,690, RNO 1,930, SFO 1,931). Notable: MMMX reports at scattered minutes (mostly :40 to :50, 15,380 of 39,041 at :45), so many reports are more than 15 minutes from the hour (G3), and its files are short in 2021 and 2022 (2,199 and 5,763 rows).

**F132.5 MOSMIX and NBM (3.5).** DWD station catalogue (`.cfg`, F130.4's method), accessed 2026-10-03, 5,649 stations. **37 of the 47 airports have a MOSMIX station within 10 km**; the ten beyond 10 km are UUWW (26.0 km), KAUS (13.2), KDAL (18.0), KBKF (11.2), KHOU (37.2), ZBAA (30.2), ZUUU (17.9), ZGGG (29.3), WMKK (47.5) and ZSPD (42.5). Nearest-station ids and distances are in the table file. Of the claim batch: EDDM 10870 (1.15 km), KORD 72530 (3.67), CYYZ 71624 (1.19), ZGSZ 59493 (1.14), ZUCK 57516 (0.49), NZWN 93436 (0.81), all within 10 km. **Longitude sign: only EGLC is flagged** (P0478: 7.69 km as listed, 2.47 km with the sign flipped, as D81.6 noted). No other airport's station of the same ICAO code moves nearer when flipped. NBM domain, from NBM's documentation only (`https://vlab.noaa.gov/web/mdl/nbm-data-availability-v5.0`, read 2026-10-03, which names CONUS, Alaska, Hawaii, Puerto Rico, Guam, Oceanic and Global Upper Air and gives no extents in its text): CONUS for the 11 contiguous US airports (by location; inference), unknown for CYYZ and MMMX, none for the other 34.

**F132.6 Eligibility and the draw (Step 4).** The rule was applied mechanically to the counts. Not eligible: EGLC and KSFO (spent), LFPB (D82.7(a)), and five that fall under 90 percent in at least one window: **MMMX** (5.32 and 0.69), **OPKC** (79.74 in the whole window; 97.40 held out), **VILK** (80.36 and 72.05), **RCSS** (91.51 and 77.81) and **FACT** (93.50 and 84.66). KBKF (97.14 and 93.96) passes. The strata then had Europe 9 eligible, North America 11, Asia 16 and South 3. The draw, as printed (`random.Random(20261003)`, Python 3.12.2):
```
stratum Europe (size 1): ['EDDM', 'EFHK', 'EHAM', 'EPWA', 'LEMD', 'LIMC', 'LTAC', 'LTFM', 'UUWW']
  sample(9 eligible, 1) returned ['EDDM']
stratum North America (size 2): ['CYYZ', 'KATL', 'KAUS', 'KBKF', 'KDAL', 'KHOU', 'KLAX', 'KLGA', 'KMIA', 'KORD', 'KSEA']
  sample(11 eligible, 2) returned ['KORD', 'CYYZ']
stratum Asia (size 2): ['LLBG', 'OEJN', 'RJTT', 'RKPK', 'RKSI', 'RPLL', 'WMKK', 'WSSS', 'ZBAA', 'ZGGG', 'ZGSZ', 'ZHHH', 'ZSPD', 'ZSQD', 'ZUCK', 'ZUUU']
  sample(16 eligible, 2) returned ['ZGSZ', 'ZUCK']
stratum South (size 1): ['NZWN', 'SAEZ', 'SBGR']
  sample(3 eligible, 1) returned ['NZWN']
```
No stratum was short, so no fill was needed. **THE CLAIM BATCH: EDDM (Munich), KORD (Chicago O'Hare), CYYZ (Toronto), ZGSZ (Shenzhen), ZUCK (Chongqing), NZWN (Wellington).** Each one's held-out window is 2024-08-01..2026-07-31 (D82.7(e)). The draw was run once, and neither the seed nor any eligibility result was changed after it.

**F132.7 The 47 airports (compact; the full table is the csv).** Daily maximum percentages are D82.8's usable local days, over 2021-03-24..2026-07-31 and over 2024-08-01..2026-07-31.

| ICAO | IEM ID | sea in box | height diff (m) | MOSMIX within 10 km | daily max usable, all (%) | held-out (%) | eligible | drawn |
|---|---|---|---|---|---|---|---|---|
| EHAM | EHAM | no | -9.3 | yes (2.3 km) | 99.80 | 99.86 | yes | no |
| LTAC | LTAC | no | +185.0 | yes (1.6 km) | 99.85 | 99.86 | yes | no |
| EFHK | EFHK | no | -14.4 | yes (0.2 km) | 99.95 | 100.00 | yes | no |
| LTFM | LTFM | yes | -49.6 | yes (0.8 km) | 99.85 | 99.86 | yes | no |
| EGLC | EGLC | no | +28.3 | yes (7.7 km) | 99.80 | 100.00 | no: spent | no |
| LEMD | LEMD | no | +67.2 | yes (1.9 km) | 99.64 | 100.00 | yes | no |
| LIMC | LIMC | no | +38.7 | yes (1.7 km) | 99.49 | 99.59 | yes | no |
| UUWW | UUWW | no | -21.0 | no (26.0 km) | 99.80 | 100.00 | yes | no |
| EDDM | EDDM | no | +34.8 | yes (1.1 km) | 99.95 | 100.00 | yes | yes |
| LFPB | LFPB | no | +16.1 | yes (0.5 km) | 97.49 | 98.63 | no: LFPB rule | no |
| EPWA | EPWA | no | -3.9 | yes (0.6 km) | 99.64 | 99.86 | yes | no |
| KATL | ATL | no | -34.1 | yes (3.2 km) | 99.85 | 99.86 | yes | no |
| KAUS | AUS | no | +37.9 | no (13.1 km) | 99.69 | 99.73 | yes | no |
| KORD | ORD | no | +7.4 | yes (3.7 km) | 99.80 | 99.59 | yes | yes |
| KDAL | DAL | no | +20.0 | no (17.9 km) | 99.90 | 99.86 | yes | no |
| KBKF | BKF | no | -13.0 | no (11.2 km) | 97.14 | 93.96 | yes | no |
| KHOU | HOU | no | +2.4 | no (37.2 km) | 99.74 | 99.73 | yes | no |
| KLAX | LAX | yes | +38.2 | yes (1.4 km) | 99.74 | 99.45 | yes | no |
| MMMX | MMMX | no | +163.6 | yes (1.2 km) | 5.32 | 0.69 | no: under 90% | no |
| KMIA | MIA | no | +2.2 | yes (4.6 km) | 99.85 | 99.73 | yes | no |
| KLGA | LGA | no | +13.8 | yes (2.2 km) | 99.90 | 99.86 | yes | no |
| KSFO | SFO | yes | +69.9 | yes (0.8 km) | 99.85 | 99.73 | no: spent | no |
| KSEA | SEA | no | -53.5 | yes (1.2 km) | 99.85 | 99.73 | yes | no |
| CYYZ | CYYZ | yes | +5.9 | yes (1.2 km) | 99.64 | 99.86 | yes | yes |
| SAEZ | SAEZ | no | +0.7 | yes (0.7 km) | 99.49 | 99.73 | yes | no |
| SBGR | SBGR | no | +66.5 | yes (0.3 km) | 99.80 | 100.00 | yes | no |
| ZBAA | ZBAA | no | +21.4 | no (30.2 km) | 99.74 | 100.00 | yes | no |
| RKPK | RKPK | yes | +89.8 | yes (0.6 km) | 99.64 | 99.59 | yes | no |
| ZUUU | ZUUU | no | +4.4 | no (17.9 km) | 99.80 | 100.00 | yes | no |
| ZUCK | ZUCK | no | -33.9 | yes (0.5 km) | 99.85 | 100.00 | yes | yes |
| ZGGG | ZGGG | no | +45.1 | no (29.3 km) | 99.85 | 100.00 | yes | no |
| OEJN | OEJN | yes | +32.8 | yes (7.7 km) | 99.85 | 100.00 | yes | no |
| OPKC | OPKC | yes | +13.3 | yes (6.7 km) | 79.74 | 97.40 | no: under 90% | no |
| WMKK | WMKK | yes | +10.5 | no (47.5 km) | 99.74 | 100.00 | yes | no |
| VILK | VILK | no | -5.8 | yes (1.3 km) | 80.36 | 72.05 | no: under 90% | no |
| RPLL | RPLL | yes | -5.6 | yes (1.2 km) | 99.54 | 99.86 | yes | no |
| ZSQD | ZSQD | yes | -58.2 | yes (0.0 km) | 99.85 | 100.00 | yes | no |
| RKSI | RKSI | yes | -1.7 | yes (1.5 km) | 99.69 | 100.00 | yes | no |
| ZSPD | ZSPD | yes | -0.9 | no (42.5 km) | 99.69 | 100.00 | yes | no |
| ZGSZ | ZGSZ | yes | +19.9 | yes (1.1 km) | 99.85 | 100.00 | yes | yes |
| WSSS | WSSS | yes | -3.9 | yes (0.0 km) | 99.85 | 100.00 | yes | no |
| RCSS | RCSS | yes | +183.5 | yes (5.3 km) | 91.51 | 77.81 | no: under 90% | no |
| LLBG | LLBG | no | +75.1 | yes (1.8 km) | 99.39 | 99.45 | yes | no |
| RJTT | RJTT | yes | +1.1 | yes (1.4 km) | 99.80 | 100.00 | yes | no |
| ZHHH | ZHHH | no | +4.7 | yes (0.5 km) | 99.85 | 100.00 | yes | no |
| FACT | FACT | yes | +39.7 | yes (1.9 km) | 93.50 | 84.66 | no: under 90% | no |
| NZWN | NZWN | yes | +79.2 | yes (0.8 km) | 99.54 | 99.86 | yes | yes |

**F132.8 Readings made where the prompt is silent (for the owner to confirm or change).**
1. **The grid box is at IEM's airport position** for every airport. For the record airports the recipe uses SPEC 3.4's Open-Meteo grid point instead; that point was used only once, as a code check at KSFO.
2. **Local day bounds.** A local day's "end" in D82.7(b) is read as its last minute (23:59 local), so a UTC+0 airport's local 2026-07-31 counts and a UTC-7 one's does not. The first local day counted starts on or after 2021-03-24 00:00 UTC. So most airports have 1,955 local days in the whole window (EGLC 1,956).
3. **The held-out window** is read as local dates from 2024-08-01, with the same day rule (729 or 730 days).
4. **Hours in a local day** are the whole UTC hours inside it. For India (UTC+5:30) the first hour starts after local midnight; the day still has 24 whole hours. A day is usable at 22 of 24 (21 of 23, 23 of 25).
5. **A usable hour** has at least one report with a finite `tmpc` assigned to it by G2 and G3 (nearest whole hour; :30 goes up; more than 15 minutes out is dropped). Which report is nearest does not change a count, so no tie rule was needed. Non-finite values found: 0.
6. **The IEM match** counts only `*_ASOS` networks (other-network rows are listed per airport in the output file); for K-airports both the ICAO and the three-letter id were tried. An ambiguous match would have been recorded and left out of the draw as "not eligible"; none occurred.
7. **MOSMIX nearest station** is the nearest of all catalogue entries by the cfg position. The longitude-sign flag is raised when the entry with the same ICAO code would be at least 2 km nearer with its longitude sign flipped (a threshold chosen here; only a flag).
8. **NBM domain** is by location, from domain names only (F132.5); the CONUS grid's extent over Toronto and Mexico City is not stated in the text read, so those are "unknown".
9. **Six yearly pieces,** not seven: the prompt's list gives six.
10. **Time zones** are IEM's `tzname`, loaded with the system tz database through `zoneinfo`.
11. **The `.meta.txt` files** follow the committed format and add row count, byte count and SHA-256.
12. **Run history.** `--collect` was run twice. Run 1 (15:03 to 15:56 UTC) downloaded the files and counted; its VILK result (0 usable local days) was a bug in the script: for half-hour zones the day's hour slots never matched whole UTC hours. The bug was fixed and run 2 (about 16:00 UTC; the downloaded files were checked by SHA-256 and kept, not fetched again) redid the lookups, GRIB messages, counts and MOSMIX. VILK is 80.36 and 72.05 percent in run 2. **No other airport's counts changed between the runs** (checked). The eligibility and the draw came only from run 2's counts, run once. Run 1's output is in the output file.

**F132.9 Requests, bytes, clean-up.**
- Run 1 (script): IEM station metadata 58 requests (147,856 B; two 404 for unknown three-letter ids), GFS idx 1 (31,816 B), GFS messages 2 (524,479 B), IEM ASOS download 309 requests (117,852,013 B; 270 files; 39 requests were network errors, all retried successfully), DWD catalogue 1 (299,502 B): 371 requests, 118,855,666 B. Run 2: IEM station metadata 59 (147,856 B), GFS idx 1, GFS messages 2, DWD catalogue 1: 63 requests, 1,003,653 B. IEM calls were one at a time, at least 1.2 s apart.
- Before the script: 8 exploratory requests (a test of the script's lookup and GRIB functions: IEM station metadata 5 and GRIB 3), and by `curl` while planning: IEM `networks.geojson` (148,655 B), IEM station `EHAM`, network `NL__ASOS` as JSON and as GeoJSON (4 requests), and NBM documentation pages at `vlab.noaa.gov` and `weather.gov` (7 requests; two 404 and one 403). No forecast or observation value was read in any of them.
- **Each run's temporary directory (the two GRIB messages and the DWD catalogue) was deleted at its end** (the script prints "removed: True"; none is left under the scratch directory).
- Rows dropped by the 2026-07-31 limit: 0.

**F132.10 What this did not do.**
- No temperature or dew point value was printed, stored in the state file or summarised; observations were kept in memory only as "usable, yes or no", with times. No statistic of a value was computed.
- No forecast field was read beyond the land-sea mask and the surface height. No score, error or skill of anything.
- Nothing from 2026-27 was requested, received or counted.
- No account, key, token, sign-up or contact.
- No committed file under `data/` was changed, and `data/models/` was not touched. The only new files under `data/` are 270 observation files with 270 `.meta.txt` files, `data/processed/session90_airports.csv` and its `.meta.txt`.
- No existing script was edited. No GRIB pull was built (that is session 91, D82.10). RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md were not edited; SPEC was edited only as Step 2 says.
- Nothing was installed, and nothing was committed. No commit message was written.

---

## 2026-10-03: Session 91 decision: F132 accepted, the 51-airport pull list, grid positions, and the pull's design (owner, planning chat)

**D83. Owner decisions, planning chat (after session 90): F132
accepted, the pull list, grid positions, an open item, and the design
of the stage C GRIB pull.** Written at the start of session 91, before
any other edit or network call. No 2026-27 value has been read or
scored.

- **D83.1 F132 accepted.** The owner accepts F132 and all twelve F132.8
  readings.
- **D83.2 The pull list is 51 airports:** D82.6's 47 plus LFPG, DSM,
  YSDU and RNO. Build choices use all six development airports (D82.6),
  so the pull must include them. Each global field serves every
  airport, so the extra cost is negligible. The four added airports are
  also product airports: the product list is now these 51 (D82.6's 47
  plus LFPG, DSM, YSDU and RNO). They remain development airports, so
  they are never in a claim batch.
- **D83.3 Grid positions.** The six development airports (EGLC, LFPG,
  DSM, YSDU, RNO, KSFO) use SPEC 3.4's grid points: the gate needs
  them, and they keep the record consistent. The 45 new airports use
  IEM's airport position, as F132 did. The raw values at the four grid
  points are kept, so the interpolation choice stays open.
- **D83.4 Open item: MMMX.** It reports at scattered minutes (mostly
  :40 to :50), so under the 15-minute rule (SPEC 8.8 G3) it has almost
  no usable observations (5.32 percent of local days, F132.6). It needs
  its own handling or to be dropped. That is a later decision. It stays
  in the pull.
- **D83.5 The pull's design (completes D82.4).**
  (a) Forecast hours are a setting of the script. The real pull uses
  f000 to f024 (D82.3). The local test chunk uses f000 to f026, so the
  gate reaches the lead-26 airports (YSDU, RNO, KSFO) as well as the
  lead-24 ones. The later f025 to f048 pull reuses the same script.
  (b) A chunk is one calendar month of GFS cycles, by the cycle's
  initialisation date. The first cycle is 2021-03-23T00 (its f024 is
  valid at 2021-03-24T00); the last is 2026-07-31T18. A forecast hour
  whose valid time lies outside 2021-03-24T00 to 2026-07-31T23 UTC is
  not requested.
  (c) Values are kept exactly as decoded, with no rounding and no unit
  conversion, written in a form that reads back to the identical
  number. The kept size may exceed D82.4's 1.5 GB estimate; this is
  accepted.
  (d) Each chunk writes one data file, one per-message manifest and one
  metadata file. A chunk is published as GitHub Release files only if
  it completed. A rerun skips months already published, so the pull is
  resumable.
  (e) A field that GFS does not provide at a forecast hour (for example
  an average or maximum at f000) is recorded as absent by design. A
  missing index file or a message that fails its identity or validity
  check is recorded and left empty. Neither is ever filled (SPEC 2.2).
  A download that still fails after its retries fails the chunk, so
  nothing partial is published.
  (f) On GitHub Actions, at most four months run at once.
  (g) The owner's first Actions run is one month. It measures real
  speed and size. Session 92 checks it before the rest is started. The
  local test chunk checks correctness only; its speed is limited by the
  owner's connection.
- **D83.6 The local test chunk.** Three cycle dates, 2022-01-12,
  2023-07-12 and 2024-04-12, all four cycles, f000 to f026, all 51
  airports. The gate compares, at each development airport's target
  hour, cycle and lead, the GRIB-derived values rebuilt from the new
  extract with the committed values in
  `data/processed/session81_training_set.csv`, on target dates
  2022-01-13, 2023-07-13 and 2024-04-13: 18 station-days, exact
  equality, no tolerance.
- **D83.7 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-03, not checked by this session).** Still no Service Change
  Notice. The newest SCN listed is still SCN 26-87 (2026-09-22). With 30
  days' notice, the earliest go-live is about 2 November 2026.
- **D83.8 Sequence.** Session 91: this entry, the script, the
  positions file, the workflow, and the local test chunk through the
  gate. The owner then pushes and runs one month on GitHub Actions
  (D83.5(g)). Session 92: verify that month's extract, speed and size,
  then the owner starts the rest.

---

## 2026-10-03: Session 91 finding: the stage C GRIB pull and its gate

**F133. The stage C GRIB pull script, its positions file and its GitHub Actions workflow exist. The local test chunk passed the gate: run 1 (all three dates, made by the pre-fix script) 18 of 18 station-days, and run 2 (2024-04-12 only, the fixed script end to end) 6 of 6, exact equality, no mismatch. The workflow was written and not run; nothing was pushed or published. Script: `scripts/session91_grib_pull.py` (new; modes `--positions`, `--plan`, `--chunk`, `--gate`, `--guard-check`; final SHA-256 `72c263b24b06d2e6ab8d1a9c9be3444ddc3ee1c4a8b2cf445556cbedddd1652e`). Workflow: `.github/workflows/stagec-grib-pull.yml` (SHA-256 `f3e05c9a41d4ad86c45921b66df5ca82785910bb88e2fcac2c42580b531c19a0`) and `.github/grib-pull-requirements.txt` (`6ebf1b26a61927aaef792dece6e6af5ab55ffa7ec48218b75ce4a3a211946f51`). Positions: `data/processed/session91_pull_airports.csv` (51 rows, SHA-256 `cf86c692ffb631c28b387d2a7f13c78fa801ec015e5434fee1b03f63cc18fd08`, with a `.meta.txt`). Full real output: `notes/session-91-output.txt`. Run 2026-10-03. Python 3.12.2, eccodes 2.48.0 (ecCodes library 2.48.0), numpy 2.5.2, requests 2.34.2.**

**F133.1 Steps 0 and 1.** `git status --porcelain` showed only `?? docs/session-91.md`. The last entries were D82 and F132; no D83 or F133 existed in either DECISIONS file; none of the new paths existed, and there was no `.github/` folder. SHA-256 equal: `session81_training_set.csv` (F122.3) and `session90_airports.csv` (F132). Read: D47, D62, D82, F128, F131, F132; SPEC 3.4, 7.2, 8.2, 8.7, 8.8; `scripts/session86_forward_build.py` in full; `session90_airports.csv` and its `.meta.txt`. `pip show eccodes`: Requires attrs, cffi, eccodeslib, findlibs, numpy (`eccodeslib` only off Windows; it requires `eckitlib==2.1.1.26`). D83 was copied with `sed` from `docs/session-91.md` lines 98 to 168 into DECISIONS.md lines 3089 to 3159 (heading at 3087) and checked byte-equal with `diff`, before any other edit or network call.

**F133.2 Index survey (Step 2; `gfs.20230712/12`, f000 to f026, 27 `.idx` requests, 1,097,380 B).** Every line listed is in the output file. Selector rules, each matching exactly one line or none at every hour:
- Instantaneous fields (t2m `TMP:2 m above ground`, tcdc `TCDC:entire atmosphere`, u10, v10, d2m, t850 `TMP:850 mb`, prmsl): step `N hour fcst`, the record's form (`session86_forward_build.py` l.371-387, `fc = f"{L} hour fcst"`); at f000 the step is `anl`, and the rule takes `anl` at f000 only. TCDC also has a `W-N hour ave fcst` line at f001 onward; the rule never takes it.
- dswrf (`DSWRF:surface`): `W-N hour ave fcst` with W = 6 x floor((N-1)/6) (`session86_forward_build.py` l.173-176, l.388-389).
- tmax2m, tmin2m (`TMAX`, `TMIN:2 m above ground`): `W-N hour max fcst`, `W-N hour min fcst`, the only matching line, same W.
- **Absent by design:** dswrf, tmax2m and tmin2m at f000 (no line). No other field and hour. So 7 messages at f000 and 10 at every other hour.

**F133.3 Positions file (Step 3).** 51 rows sorted by ICAO: 6 development (SPEC 3.4 grid point, read from SPEC.md by code), 6 claim batch and 39 new (IEM position from `session90_airports.csv`). Four points per airport from `codes_grib_find_nearest` on one message (`gfs.20230712/12` f000 `TMP:2 m above ground`, bytes 413333316-413851604), longitude shifted by +360 first; grid geometry Ni 1440, Nj 721, 90.0 to -90.0, 0.0 to 359.75, increments 0.25. **Check: at all six development airports the four points equal those the record's `bilinear_from_gid` finds, and the bilinear value from the stored indices and weights equals `bilinear_from_gid`'s value exactly.** Cross-check: the 45 IEM-position boxes and weights equal session 90's exactly (as sets; session 90 stores points sorted by latitude, then longitude).

**F133.4 Script, guards, workflow (Steps 4 and 5).**
- Modes as the prompt lists, plus `--positions` (reading 1). `--chunk` fetches by byte range from the `.idx` (`find_range` copied), 16 workers by default, retries only on network errors, 429 and 5xx; checks each message's identity, step type, start and end step, run date and time, full validity date and hour, and grid geometry against the positions file; reads 4 values per airport by grid index; writes `gfs_points_<chunk>.csv.gz`, `manifest_<chunk>.csv.gz` and `chunk_<chunk>.meta.txt` exclusively, and writes nothing if any download fails after its retries or the byte budget would be passed. No interpolation, derivation or rounding in the output; values written with `repr`.
- Guards in code: no cycle after 2026-07-31T18; no valid time after 2026-07-31T23 or before 2021-03-24T00; `--hours` within 0 to 48; months within 2021-03 to 2026-07; existing output refused.
- Workflow: `workflow_dispatch` with input `months`; a plan job lists the Release `stagec-grib-pull-v1`'s assets with `gh` and the job token, expands the range and passes only months whose three files are not all published; a matrix job per month, `max-parallel: 4`, `timeout-minutes: 350`, `ubuntu-latest`, Python 3.12; installs only the pinned file with `--no-deps` (then `pip check`); runs `--chunk --month <m> --hours 0-24 --out out --workers 16`; on success creates the Release if needed and uploads the three files (`permissions: contents: write`, no secret). No cache, no artifact.
- Pinned (the local versions): eccodes 2.48.0, eccodeslib 2.48.0.26, eckitlib 2.1.1.26, findlibs 0.1.3, attrs 26.1.0, cffi 2.1.1, pycparser 3.0, numpy 2.5.2, requests 2.34.2, urllib3 2.7.0, certifi 2026.7.22, idna 3.19, charset-normalizer 3.5.1. **The ecCodes library on Linux comes from `eccodeslib`:** PyPI lists `eccodeslib-2.48.0.26-cp312-cp312-manylinux_2_28_x86_64.whl` and an `eckitlib` manylinux wheel (5 PyPI metadata reads).
- PyYAML is not installed: the workflow was **not parsed**. Its month-expansion code was run locally on six inputs and behaved as intended. **Not testable locally:** the `gh` release listing, creation and upload; the matrix and job outputs; the Linux install of the pinned wheels; speed, size and the 350-minute limit on Actions; four jobs creating the Release at once (handled by a fallback, untested).

**F133.5 Guard check and plan (Step 6.1, 6.2).** 10 of 10 cases behaved as specified: refused cycle 2026-07-31T18 f006, cycle 2026-08-01T00, valid 2021-03-23T23, `--hours 0-49`, an existing output file, `--month 2026-08`, `--dates 2026-08-01`; allowed 2026-07-31T18 f005, 2021-03-23T00 f024, an absent output file. No network. Plan, f000 to f024: **65 months, 7,828 cycles, 195,600 files, 1,932,528 expected messages, valid 2021-03-24T00 to 2026-07-31T23; 0 valid times outside the window.** 2021-03 has 36 cycles and 840 files; 2026-07 has 3,060 files.

**F133.6 The test chunk (Step 6.3), two runs.**
- **Run 1 (pre-fix script, SHA-256 `3b17207377e68de66263df359c83f5f29bb6656d260199e52c3e6aef9c9c466f`):** dates 2022-01-12, 2023-07-12, 2024-04-12, all four cycles, f000 to f026, 8 workers. 12 cycles, 324 files, 324 `.idx` and 3,204 message requests, 0 retries, 2,526,907,686 B, 520.7 s. Statuses: ok 3,194, absent by design 36, idx missing 0, check failed 10. Files: points 2,000,619 B (16,524 rows), manifest 82,817 B, meta 1,571 B. **The 10 failures were a bug in my spot-check code** (it read a key the positions rows do not have), all at 2024-04-12T18 f026; because the spot check sat inside the message checks, the error marked the messages failed, and their values, read before it, were still written. The spot check recorded nothing.
- **The fix** (full diff in the output file; the pre-fix text was rebuilt by reversing the edit and its SHA-256 equals run 1's): the spot check reads `lat_used`/`lon_used` and runs outside the message checks, so an error in it stops the run; values are stored only for a message whose status is `ok`. **Confirmed:** a run with a positions copy whose grid increment is wrong gave 40 of 40 messages "check failed" and 0 of 8,160 value cells non-empty. (A first attempt at this test was invalid: my test patched the module constant but not `read_positions`' default path, so it read the true file; 40 ok. Recorded in the output file.)
- **Run 2 (fixed script, owner's choice in session):** date 2024-04-12, f000 to f026, 8 workers, budget 1.9 x 10^9. 4 cycles, 108 files, 108 `.idx` and 1,068 message requests, 0 retries, 820,753,100 B, 190.7 s. ok 1,068, absent by design 12, idx missing 0, check failed 0. **The ten 2024-04-12T18 f026 messages are all `ok`.** Points 668,449 B, manifest 27,938 B. Its 5,508 points rows equal run 1's for that date string for string; the manifests differ only in those ten statuses.
- **Spot check (run 2):** at EFHK and KATL, for each of the ten fields at 2024-04-12T18 f026, the four grid indices and values read by index equal `codes_grib_find_nearest`'s: 20 of 20.

**F133.7 The gate (Step 6.4).** Record arithmetic copied from `session86_forward_build.py` (`derive`, bilinear term order). Training set SHA-256 checked against F122.3; the positions file's SHA-256 is in each chunk's meta.
- **Run 1's extract: PASSED, 18 of 18 station-days, every one of the 7 columns 18 of 18, every airport 3 of 3 (21 of 21 values). 0 mismatches, 0 missing committed rows, 0 not rebuilt.** Made by the pre-fix script; the values used at RNO and KSFO 2024-04-13 are the ten that were marked "check failed" but had passed every real check.
- **Run 2's extract: 6 of 6 station-days (2024-04-13) equal, 7 of 7 columns each, 0 mismatches.** The other 12 are "not rebuilt" because run 2 holds one date, so the script's all-18 rule prints "GATE NOT PASSED".

**F133.8 Projection (ESTIMATES, from run 1's sizes and speed).** Full f000 to f024 pull: 195,600 files (`.idx` requests), 1,932,528 messages, about 1.52 TB downloaded (about 23.5 GB a month); kept, compressed: points about 1.21 GB (121 B a row, 9,975,600 rows) and manifests about 50 MB; about 19.9 MB a full month. Time at run 1's rate (0.62 files/s, 4.9 MB/s, 8 workers, the owner's connection): about 83 min a month, 87 h for all months in sequence. Limited by the local connection (D83.5(g)); the first Actions run measures the real rate.

**F133.9 Readings made where the prompt is silent (for the owner to confirm).**
1. The positions file is written by a fifth mode, `--positions`, of the pull script, so its provenance is code.
2. At f000 the instantaneous rule takes `anl`.
3. "At most 5 times" is read as 5 retries after the first try, waits 2, 4, 8, 16, 32 s; a short body or a body without the GRIB and 7777 markers counts as a network error.
4. An `.idx` 404 is "idx missing"; a missing or doubled `.idx` line, or an unreadable `.idx`, is "check failed"; a 404 on a message listed in its `.idx` fails the chunk.
5. A missing or non-finite value at any needed grid index fails the whole message (left empty for all airports). None occurred.
6. The process type is eccodes' `stepType` plus `typeOfStatisticalProcessing` where defined.
7. eccodes calls run under one lock (threads download in parallel).
8. Gzip with a zero timestamp, so equal content gives equal bytes.
9. The grid geometry is a set of columns on every positions row (and in the meta); `lon_used` is as the source gives it.
10. `--budget-bytes` is optional with no default limit (Actions runs have none).
11. Spot-check airports: EFHK (first new airport by ICAO code) and KATL (first new airport with a negative longitude); messages: the chunk's last file (all ten fields).
12. The gate leaves out the record's finiteness check on five fields the pull does not hold (t925, t700, rh2m, spfh2m, pres_sfc) and the season columns.
13. In the workflow, Python "3.12" (the newest 3.12.x, printed in each chunk's meta), a month counts as published only with all three files, and uploads replace a partial upload (`--clobber`).
14. A month's cycles with no requested hour are left out (2021-03 starts at 2021-03-23T00, as D83.5(b)).
- Note, not a decision: the later f025 to f048 pull would reach cycles 2021-03-22T00 and T06 (for valid times from 2021-03-24T00). SPEC 7.2 gives v16's start as 2021-03-22 with no hour, so whether those two cycles are v16 is to be checked before that pull.

**F133.10 Requests, bytes, clean-up.** GRIB requests 4,821 and 3,410,709,377 B (survey 27, positions 2, run 1 3,528, run 2 1,176, the two failure tests 44 each), under the 4.5 x 10^9 limit; plus 5 PyPI metadata reads (bytes not counted). No message was written to disk. **The temporary directory (all extracts) was deleted; the path no longer exists.**

**F133.11 What this did not do.** No observation was read; no score, error, MAE, bias or skill was computed; nothing from 2026-27 was requested or read; no forecast value was printed (the gate had no mismatch); no push, workflow run, `gh` call or Release; no account or token; no committed file under `data/` was changed and `data/models/` was not touched; no existing script was edited; nothing was installed; SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md were not edited. Nothing was committed and no commit message was written.

---

## 2026-10-04: Session 92 decision: F133 accepted, the first Actions month, and the bad-month check (owner, planning chat)

**D84. Owner decisions, planning chat (after session 91): F133
accepted, the f025 to f048 start cycle, the first Actions month, the
bad-month check, the next run, and GFS v17.** Written at the start of
session 92, before any other edit or network call. No 2026-27 value
has been read or scored.

- **D84.1 F133 accepted.** The owner accepts F133 and all fourteen
  F133.9 readings.
- **D84.2 The f025 to f048 pull starts at cycle 2021-03-22T12.** GFS
  v16 began with the 12z run of 2021-03-22 (NWS SCN 21-20, updated, 18
  March 2021). Cycles 2021-03-22T00 and T06 are GFS v15 and are not
  used. This settles F133.9's note.
- **D84.3 The first Actions month.** After session 91 was committed
  and pushed, the owner ran month 2022-01 on GitHub Actions. The run
  succeeded in 8 min 25 s (the run time GitHub shows). The Release
  "Stage C GRIB pull" holds its three files, which the owner downloaded
  to `/Users/zacharyadams/Coding Projects/MLwx-pull/`, outside the
  repo. Session 92 verifies them (D83.5(g)).
- **D84.4 The bad-month check (owner's choice, option b).** Today a
  month whose messages are mostly "check failed" would publish with
  empty values (never filled, but not flagged). So a verifier runs in
  the workflow after the chunk and before upload. It fails the month,
  and nothing is published, if: any count differs from the plan
  (cycles, files, messages, rows); any message is "check failed"; any
  message is "absent by design" other than DSWRF, TMAX and TMIN at
  f000, or any of those is not; any key is duplicated; an ok message
  has an empty or non-finite value; a non-ok message has any value; or
  the meta's SHA-256 values do not match the files. "idx missing"
  messages do not fail the month: they are published, left empty, and
  their count is printed in the job log. Because the pull is
  resumable, a failed month is retried by starting the run again.
- **D84.5 The next run.** After session 92 is reviewed and committed,
  the owner runs month 2021-03 alone: it is the partial first month
  (from 2021-03-23T00, 840 files) and the first live test of the
  verify step. If it succeeds and its verify step passed, the owner
  starts 2021-04 to 2026-07 (2022-01 is already published and is
  skipped).
- **D84.6 GFS v17 (planning-chat check, 2026-10-04, not checked by
  this session).** The planning chat could not load the NWS notices
  page; a web search found no GFS v17 Service Change Notice. EMC's
  GFSv17 evaluation page (last updated 5 June 2026) gives the
  implementation as Q1 FY27 (October to December 2026). With 30 days'
  notice, the earliest go-live is about 3 November 2026.

---

## 2026-10-04: Session 92 finding: the 2022-01 Actions extract and the verify step

**F134. The 2022-01 month pulled on GitHub Actions (D84.3) is intact and complete: its three local files equal the Release assets and the meta, and all 13 verifier checks pass (124 cycles, 3,100 files, 30,628 messages, 372 absent by design, 158,100 points rows, 0 check failed, 0 idx missing). The extended gate passed: 93 of 93 station-days at EGLC, LFPG and DSM, all seven columns equal, exact equality. This is the first check that the Linux ecCodes build on Actions decodes exactly as the owner's Mac did. A verify step now runs in the workflow before upload (D84.4). Script: `scripts/session92_verify_chunk.py` (new; the D84.4 checks, plus local-only `--ranges` and `--gate`; SHA-256 `f61136a88ec1b787d84d083d887008af669595cc62a63e920639a737686a1955`). Workflow: `.github/workflows/stagec-grib-pull.yml`, new SHA-256 `804b6d35b863e07f2da1a559958cb2710e889d4439438c68c9c6109544ce02a6`. Full real output: `notes/session-92-output.txt`. Run 2026-10-04. Python 3.12.2, eccodes 2.48.0 (ecCodes library 2.48.0), numpy 2.5.2, requests 2.34.2.**

**F134.1 Steps 0 to 2.**
- `git status --porcelain` showed only `?? docs/session-92.md`. The last entries were D83 and F133; no D84 or F134 existed in either DECISIONS file; the verifier did not exist. SHA-256 equal to F133: the pull script (`72c263b2...652e`), the workflow (`f3e05c9a...19a0`), the requirements file (`6ebf1b26...6f51`) and the positions file (`cf86c692...fd08`); and to F122.3: `session81_training_set.csv` (`ab8f25f2...8d4a`). `MLwx-pull/` held exactly the three expected files and nothing else. Read: D47, D83, F128.2, F133; SPEC 3.4, 7.2, 8.7, 8.8; the pull script and the workflow in full.
- D84 was copied with `sed` from `docs/session-92.md` lines 102 to 144 into DECISIONS.md lines 3223 to 3265 (heading at 3221) and checked byte-equal with `diff`, before any other edit or network call.
- Local files (SHA-256, bytes): `gfs_points_2022-01.csv.gz` `e9d9d885cc918073c0c788371dc275e5719f5369077b0d78374efd9ca8ece130`, 19,850,481; `manifest_2022-01.csv.gz` `4789354a079b59b19970da515699cd4d29e4dbe19daa8962893ebbe99b570ff1`, 786,619; `chunk_2022-01.meta.txt` `9bf877998057505812a4ea38cdf6e432716d5a7159e29c0954c815f676a1db4e`, 1,360.
- Meta (in full in the output file): both data-file SHA-256 values equal the local files'; script SHA-256 equals F133's final (`72c263b2...652e`); positions SHA-256 equals the committed file's; arguments `--chunk --month 2022-01 --hours 0-24 --out out --workers 16` (16 workers). Recorded versions: Python 3.12.14, eccodes 2.48.0, ecCodes library 2.48.0, numpy 2.5.2, requests 2.34.2. Run 2026-10-03T18:26:55Z to 18:35:01Z, 486.5 s; retries 0; HTTP 404 0.
- Release (GitHub REST API, unauthenticated, one request, 2026-10-04T11:33:09Z): `zadams03/MLwx`, tag `stagec-grib-pull-v1`, title "Stage C GRIB pull", not draft, not prerelease, published 2026-10-03T18:35:03Z. Three assets, each with a `digest`: all three sizes and SHA-256 digests equal the local files exactly.

**F134.2 The verifier (Step 3).** `--dir DIR --month YYYY-MM --hours A-B`. It imports from `session91_grib_pull.py` (read-only; not edited): the plan (`parse_month`, `month_cycles`, `plan_chunk`, `expected_messages`, `selector`), `FIELDS`, the column lists, `STATUSES`, `read_positions`, `sha256_file`, `write_gz` (tests only) and, for `--gate`, `load_airports`, `bilinear_stored`, `derive`, `window_start`, `DEV` and `GATE_COLS`. Nothing is typed in. Thirteen named checks, each printing expected, found and PASS or FAIL: layout, cycles, files, manifest rows, messages, points rows, statuses, check failed, absent by design, duplicate keys, ok values, non-ok values, meta sha256. The two value checks read both files fully and reconcile them. It prints the "idx missing" count and exits 0 only if all 13 pass. `--ranges` and `--gate` are local-only and never fail rules.

**F134.3 2022-01 (Step 4).** The plan's own output (`session91_grib_pull.py --plan`) for 2022-01 is 124 cycles, 3,100 files, 30,628 messages, as the prompt expected.

| check | expected | found | result |
|---|---|---|---|
| cycles | 124 | 124 in each file, the plan's set | PASS |
| files | 3,100 | 3,100 in each file, the plan's set | PASS |
| manifest rows | 31,000 (3,100 x 10) | 31,000, the plan's keys | PASS |
| messages (not absent by design) | 30,628 | 30,628 | PASS |
| points rows | 158,100 (3,100 x 51) | 158,100, the plan's keys | PASS |
| check failed | 0 | 0 | PASS |
| absent by design | 372 (DSWRF, TMAX, TMIN at f000) | 372, none extra, none lacking | PASS |
| duplicate keys | 0 | 0 and 0 | PASS |
| ok values | 6,248,112 cells filled and finite | 0 bad | PASS |
| non-ok values | 75,888 cells empty | 0 filled | PASS |
| meta sha256, layout, statuses | equal; session 91's columns; four statuses | as expected | PASS |

"idx missing": 0. Ranges (`--ranges`; units as GRIB gives them): 0 values outside the bounds in every field (632,400 values each for t2m, tcdc, u10, v10, d2m, t850, prmsl; 607,104 for dswrf, tmax2m, tmin2m); the per-field minimum and maximum are in the output file. Read-back: 6,248,112 value cells, 0 whose `repr(float(s))` differs from the stored string. Negative tests on copies in one `mktemp -d` directory (copies re-gzipped with the script's own `write_gz`; an unchanged round trip gave identical bytes): untouched copy exit 0, 13 of 13; (a) ok to "check failed": exit 1, "check failed" fails (and "non-ok values", since the message's cells stay filled); (b) a points row deleted: exit 1, "points rows"; (c) a points row duplicated: exit 1, "duplicate keys" and "points rows"; (d) a cell emptied in an ok message: exit 1, "ok values"; (e) a cell filled in an absent-by-design message: exit 1, "non-ok values"; (f) absent by design to ok: exit 1, "absent by design" (and "messages" and "ok values"); (g) the meta's points SHA-256 changed by one character: exit 1, "meta sha256" only. The originals' SHA-256 were unchanged after the tests.

**F134.4 The extended gate (Step 5). PASSED.** `--gate`, session 91's arithmetic imported, F133.7's operation order (bilinear on the four stored values, then `derive`). EGLC and LFPG 12z lead 24, DSM 18z lead 24 (F128.2), target dates 2022-01-02 to 2022-02-01: 93 station-days, all rebuilt and compared. Every one of the seven columns 93 of 93; every airport 31 of 31 station-days and 217 of 217 values; mismatches 0; no committed row 0; not rebuilt 0. Exact equality, no tolerance. The training set was read with an explicit list of nine columns (station, target date, the seven compared columns). **YSDU, RNO and KSFO use lead 26, which an f000 to f024 extract does not hold, so they are not gated here.**

**F134.5 Speed and size (Step 6).** Measured (meta and D84.3): the chunk took 486.5 s of the run's 8 min 25 s (505 s); 6.37 files/s, 63.0 messages/s; 26,767,295,507 B downloaded (125,901,291 `.idx`, 26,641,394,216 messages), 55.0 MB/s; kept 20,638,460 B (points 19,850,481, 125.6 B a row; manifest 786,619; meta 1,360). **ESTIMATES** for the remaining 64 months (192,500 files and 1,901,900 messages, each month's counts from the plan), at 2022-01's rates: downloads about 1.66 TB (about 1.69 TB for all 65 months); kept about 1.28 GB (about 1.30 GB for all 65); a full month's job about 8.4 min, 2021-03's (840 files) about 2.5 min; wall time at four at once, in month order, about 2.2 h (8.7 h of job time). The Release will hold 195 assets (65 x 3). Against F133.8 (local rate): downloads 1.69 TB against about 1.52 TB; kept about 1.30 GB against about 1.26 GB (1.21 GB points plus 50 MB manifests); a full month 20.6 MB against 19.9 MB; time about 8 min a month against 83 min, so about 2.2 h at four at once against 87 h in sequence locally.

**F134.6 The workflow (Step 7).** One step added to the per-month job, after "Pull one month" and before "Publish": `python scripts/session92_verify_chunk.py --dir out --month "$MONTH" --hours 0-24`. A non-zero exit fails the job, so the publish step is not reached. Nothing else changed (diff in the output file). PyYAML is not installed: not parsed. New SHA-256 `804b6d35b863e07f2da1a559958cb2710e889d4439438c68c9c6109544ce02a6`. Verifier SHA-256 `f61136a88ec1b787d84d083d887008af669595cc62a63e920639a737686a1955`. The step is first tested live by the owner's 2021-03 run (D84.5).

**F134.7 Readings made where the prompt is silent (for the owner to confirm or change).**
1. "Messages" is the plan's message count, the manifest rows not absent by design (30,628); the manifest's row count (31,000, one per file and field) is a separate check.
2. Each count check also requires the set of keys (cycles; cycle and hour; cycle, hour and field; cycle, hour and airport) to equal the plan's, not only the count.
3. Two checks beyond D84.4's list, both failing the month: "layout" (the two headers are session 91's columns; if not, the run stops, since nothing else can be read) and "statuses" (every status is one of session 91's four). Session 91's code cannot produce either failure.
4. "ok values" also fails if a points row's field has no manifest row; a cell that does not read as a number counts as non-finite.
5. The Step 5 gate is a third, local-only option (`--gate`) of the verifier, so its code is committed; the prompt allows one new script.
6. `--gate` gates the development airports whose lead lies inside `--hours`, at every cycle in the month at that airport's cycle hour (target date = cycle date plus one day), and needs every message it uses to be "ok" in the manifest, not only non-empty.
7. Speed: MB is 10^6 bytes. The projection adds the run's 18.5 s outside the chunk to every month's job; bytes scale with messages (and `.idx` bytes with files), kept size with rows; wall time is list scheduling of the 64 months, in month order, on four runners. Rates on Actions may vary from month to month; not measured.
8. Negative tests changed the first matching row; in (a), (c) and (f) a second or third check fails as a direct consequence of the same edit.
9. The workflow's header comment ("uploaded only if its pull completed") and the publish step's name ("only reached if the pull succeeded") were left unchanged, as Step 7 says; both now leave out the verify step.

**F134.8 Requests and clean-up.** One unauthenticated GitHub REST API request (`GET /repos/zadams03/MLwx/releases/tags/stagec-grib-pull-v1`); no other network use. **The negative tests' temporary directory was deleted; the path no longer exists.** No bytecode file of either script was written.

**F134.9 What this did not do.** No GRIB request; no observation read (from `session81_training_set.csv` only the nine named columns were kept); no score, error, MAE, bias or skill; nothing from 2026-27; no forecast value printed beyond the ranges summary (no gate mismatch occurred); no push, workflow run or Release change; no token, `gh` or sign-in; nothing in `MLwx-pull/` changed (SHA-256 checked at the end); no file under `data/` changed and `data/models/` was not touched; no existing script edited; nothing installed; SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing was committed and no commit message was written.

---

## 2026-10-05: Session 93 decision: F134 accepted, run 2, and the 2022-11 failure (owner, planning chat)

**D85. Owner decisions, planning chat (after session 92): F134
accepted, the remaining months run, and the 2022-11 failure.** Written
at the start of session 93, before any other edit or network call. No
2026-27 value has been read or scored.

- **D85.1 F134 accepted.** The owner accepts F134 and all nine F134.7
  readings. The workflow's header comment and the publish step's name
  still describe the old gating (F134.7 item 9); cosmetic, left as is.
- **D85.2 The remaining months.** After session 92 was committed and
  pushed, the owner ran 2021-03 alone on GitHub Actions, then
  2021-04..2026-07. The owner reports every month succeeded except
  2022-11. Session 93 checks the Release (Step 2).
- **D85.3 The 2022-11 failure.** Month 2022-11 failed in the pull
  step, twice, with "CHUNK FAILED, NOTHING WRITTEN", so nothing was
  published for it. First run: DownloadError on
  gfs.20221129/18/atmos/gfs.t18z.pgrb2.0p25.f003, bytes
  417821939-418699246, "failed after 5 retries: broken body (no GRIB
  or 7777 marker)"; files done 2895 of 3000; requests idx 2912,
  message 28599; retries 85; 463 s. Second run (the owner's rerun of
  2022-11 alone): the same error on the same cycle's f002, bytes
  419336616-420214434; files done, requests and retries identical
  (2895, 2912, 28599, 85); 534 s. Identical counts on a different
  file point to a persistent fault in that cycle rather than a
  transient network error.
- **D85.4 Session 93 is diagnosis only.** It finds which messages are
  broken and how, and whether a second NOAA mirror holds them intact.
  The handling of 2022-11 is decided after review (D86). Options the
  planning chat raised: (a) take only the broken messages from the
  mirror, if its bytes are good; (b) a new status, "broken in
  archive", for those messages, left empty and published with their
  count, as "idx missing" is.

---

## 2026-10-05: Session 93 finding: the Release after run 2 and the 2022-11 broken cycle

**F135. Diagnosis only. The Release holds every planned month except 2022-11: 192 assets, all "uploaded". On `noaa-gfs-bdp-pds`, 27 GRIB files in three cycles (2022-11-29T18, 2022-11-30T00 and 2022-11-30T06) are broken: in each, all ten messages the pull asks for fail session 91's body checks, 270 messages in all. Each file looks whole (it starts with "GRIB" and ends with "7777"), but its `.idx` does not match it: the byte ranges point to the wrong places. The Google Cloud mirror holds the same `.idx` files and the same file sizes, and the same 270 messages are broken there. Nothing was fixed or published. Script: `scripts/session93_diagnose.py` (new; modes `--release`, `--diagnose`; SHA-256 `fbaf73a130eb071992a7c65f03c579d926a305da0a67ebb7fb7c5bf4a89a9581`). Full real output, with every file, message, range and hex dump: `notes/session-93-output.txt`. Run 2026-10-05. Python 3.12.2, numpy 2.5.2, requests 2.34.2, eccodes 2.48.0 (ecCodes library 2.48.0).**

**F135.1 Steps 0 and 1.** `git status --porcelain` showed only `?? docs/session-93.md`. The last entries were D84 and F134; no D85 or F135 existed in either DECISIONS file. SHA-256 equal to F134: the pull script (`72c263b2...652e`), the verifier (`f61136a8...1955`) and the workflow (`804b6d35...02a6`). Read: D83, D84, F133, F134 and the pull script in full. D85 was copied with `sed` from `docs/session-93.md` lines 82 to 112 into DECISIONS.md lines 3325 to 3355 (heading at 3323) and checked byte-equal with `diff`, before any other edit or network call.

**F135.2 The Release (Step 2; GitHub REST API, unauthenticated, 4 requests, 2026-10-05T15:11Z).** Release `stagec-grib-pull-v1` ("Stage C GRIB pull"), not draft, not prerelease. **192 assets** (expected 192). Every plan month 2021-03 to 2026-07 has all three files except **2022-11, which has none**. No month is partial; no asset is named for a month outside the plan; every asset's state is "uploaded". Total 1,238,178,639 B (points 1,189,134,875; manifests 48,956,737; meta 87,027). Names, sizes, digests and dates are in the output file. No asset was downloaded.

**F135.3 Which messages are broken (Step 3, S3).** Five cycles, f000 to f024, 125 files. Every `.idx` and HEAD answered except two `.idx` reads (below). Every `.idx` that was read has 743 lines (696 at f000). No range of the ten fields ends beyond its file's Content-Length. Each message was fetched once and given session 91's body checks (length, "GRIB" at the start, "7777" at the end), then its message checks (identity, step, run, validity, grid, finite values at the grid indices).

| cycle | ok | broken | check failed | request error | absent by design | `.idx` not read |
|---|---|---|---|---|---|---|
| 2022-11-29T18 | 137 | 110 | 0 | 0 | 3 | 0 |
| 2022-11-30T00 | 157 | 90 | 0 | 0 | 3 | 0 |
| 2022-11-30T06 | 176 | 70 | 0 | 1 | 3 | 0 |
| 2022-11-30T12 | 231 | 0 | 0 | 16 | 3 | 0 |
| 2022-11-30T18 | 206 | 0 | 0 | 21 | 3 | 20 |
| all | 907 | 270 | 0 | 38 | 15 | 20 |

- **The broken files** (all ten requested messages broken in each; no other file has a broken message): 2022-11-29T18 f002, f003, f009, f011, f012, f013, f017, f018, f022, f023, f024 (11); 2022-11-30T00 f002, f005, f007, f008, f010, f011, f013, f016, f020 (9); 2022-11-30T06 f002, f003, f004, f005, f007, f020, f024 (7). f000 and f001 are never broken.
- **How.** Every broken message has exactly the expected length. 243 have no "GRIB" at the start and no "7777" at the end. 27 (PRMSL, the first message in each broken file, at offset 0) start with "GRIB" but do not end with "7777". In those 27, the length in the GRIB header differs from the `.idx` range, and a second "GRIB" sits exactly at the header's length: for example, 2022-11-29T18 f002 has range 0-870924 (870,925 B), the header gives edition 2 and total length 868,968, and the next "GRIB" is at offset 868,968. 248 of the 270 bodies contain "GRIB" at some offset; 22 contain none. First and last 16 bytes of each are in the output file.
- **D85.3's two ranges** are the t2m messages of 2022-11-29T18 f003 (417821939-418699246) and f002 (419336616-420214434), both broken here.
- **Retries.** 270 broken messages at 5 retries each would be 1,350, not D85.3's 85. The pull stops at the first message that fails after its retries, so it reached only some of them. 85 is 17 x 5, which fits 17 messages retried to the end, but D85.3's figures cannot show which.
- **Request errors are this session's connection, not the archive** (reading 3): 37 network errors (connection reset or closed, read timeout, incomplete read) and one HTTP 503 (2022-11-30T06 f014 t2m). All are in the last three cycles surveyed, and every file with an error also had 4 to 9 messages read ok. The two `.idx` reads that failed (2022-11-30T18 f007, f013; connection closed, read timeout) leave those two files' 20 messages unread. These 58 messages were not requested again (reading 2). So 2022-11-30T12 and T18 show no broken message among the 437 read, but they are not fully checked.

**F135.4 The broken files in more detail (Step 4, all 27).**
- `.idx` line count: 743 in every broken file, the same as every other hour f001 to f024 of its cycle.
- `.idx` offsets: start at 0 and strictly increase in all 27. **In 15 of the 27 the last `.idx` offset is beyond the file's Content-Length** (a request there gives HTTP 416). In the other 12 the 4 bytes at the last offset are not "GRIB". On each cycle's healthy f001, the 4 bytes at the last offset are "GRIB". All 27 broken files, and each healthy f001, end with "7777".
- A 4,096-byte window around each file's t2m `.idx` offset (2,048 bytes before it): no "GRIB" anywhere in the window in all 27, and no "7777" in 26; in 2022-11-29T18 f012 one "7777" at 1,219 bytes before the offset. On a healthy boundary, "7777" sits 4 bytes before the offset and "GRIB" at it.
- Reading: the `.idx` files do not describe these GRIB files. The offsets are not shifted by one fixed amount: the first message's length already differs (F135.3), and the gap grows or shrinks differently from file to file. Nothing was repaired or reinterpreted.

**F135.5 The second mirror (Step 5).** `https://storage.googleapis.com/global-forecast-system/` with S3's paths answered (HTTP 200). For all 27 broken files: **the mirror's `.idx` is byte-identical to S3's (27 of 27), and its Content-Length is equal (27 of 27).** All 270 messages, fetched with the mirror's own `.idx` ranges, are **broken in the same way** (243 with no "GRIB" or "7777", 27 PRMSL with no "7777"). Three messages ok on S3 in each cycle, at the same ranges on the mirror: **81 of 81 SHA-256 identical** (9 distinct messages; reading 6). So the mirror holds the same files as S3, and D85.4's option (a) has no good bytes to take.

**F135.6 Context from the record (read only; not checked further).** F131.2 reports that dynamical.org's validation lists 2022-11-29T12 and T18 and 2022-11-30T00 and T06 as incomplete, "from a NOAA index fault". This session found 2022-11-29T18, 2022-11-30T00 and 2022-11-30T06 broken. 2022-11-29T12 was outside this session's cycles and was not checked. F122.3 records no GRIB row for 2022-11-30 at DSM, RNO and KSFO, whose files come from cycle 2022-11-29T18. DSM's file (f024) is one of the broken files here.

**F135.7 Requests and bytes.** S3: 1,600 requests, 1,002,151,039 B. Google Cloud: 406 requests, 300,658,800 B. GitHub API: 4 requests, 635,183 B. No other host. No whole GRIB file was downloaded. Every byte was held in memory only; nothing was written to disk, so no temporary directory was needed or made. The S3 survey took 5,680 s (8 threads), the whole run 6,089 s.

**F135.8 Readings made where the prompt is silent (for the owner to confirm or change).**
1. "Session 91's checks" are read as both its body checks (`Fetcher.get`, length then markers, all three reported) and its message checks (`process_file` l.656-690, copied into the script with the line numbers, because they are inline there). A body that passes but fails a message check would be "check failed"; none did.
2. "GET once" is kept strictly: the 38 messages with a request error and the two failed `.idx` reads were not requested again. Their state is unknown.
3. The script labels the two failed `.idx` reads "idx missing" in its table (20 messages). They were network errors, not HTTP 404. In session 91 they would have been retried. The script was not edited after the run, so its SHA-256 is the one that ran; the correct reading is given here and in F135.3.
4. Step 3.2 checks the ten fields' ranges only. Step 4.2 adds two 4-byte GETs per file: the file's last 4 bytes, and the 4 bytes at its last `.idx` offset. The same was done on one healthy file of the same cycle, the first hour after f000 that is not broken (f001 in all three cycles).
5. Step 4.3's window is 2,048 bytes before and 2,047 after the `.idx` offset of the file's first broken message in field order (t2m in all 27).
6. Step 5.3's three messages are the first three ok on S3 in hour, then field, order within the cycle, preferring the broken file itself. No broken file had an ok message, so the three were f000 t2m, tcdc and u10 of the cycle every time: 81 comparisons of 9 distinct messages. S3's ranges were used on the mirror (the `.idx` files are identical, so the mirror's own ranges are the same).
7. Step 3.4's marker search covers "GRIB" only, as the prompt says; Step 4.3 searches both markers.
8. An observation, not tried and not a proposal: each broken file starts with "GRIB" and ends with "7777", and its first message's header gives its true length. So the file's own message boundaries may be readable from its headers. Whether to use that is for D86.

**F135.9 What this did not do.** Nothing published or pushed; no workflow run; no Release change; no asset downloaded. No existing code changed (pull script, verifier and workflow SHA-256 unchanged). No file under `data/` changed, and nothing in `MLwx-pull/` was touched. No value decoded beyond session 91's checks; no forecast value printed. Nothing from 2026-27; no observation; no score. No account, token or `gh`. Nothing installed. No bytes kept; no temporary directory made. SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing committed and no commit message written.

---

## 2026-10-05: Session 94 decision: F135 accepted and 2022-11 recovered by a whole-file fallback (owner, planning chat)

**D86. Owner decisions, planning chat (after session 93): F135
accepted, and 2022-11 recovered by a whole-file fallback.** Written at
the start of session 94, before any other edit or network call. No
2026-27 value has been read or scored.

- **D86.1 F135 accepted.** The 27 broken files in 2022-11 have `.idx`
  files that do not match them; the GRIB files themselves end in 7777
  as whole files should. The Google Cloud mirror holds identical
  copies, so option (a) of D85.4 is ruled out.
- **D86.2 Recover, do not leave empty (option c).** When a file's
  `.idx` ranges give a persistently broken body, the pull downloads
  that whole file, finds its messages by walking the GRIB headers
  (not the `.idx`), and takes all ten of the file's fields from it,
  each selected by session 91's own per-message check. Those messages
  get the new manifest status "ok (whole file)", so they stay
  visible. Option (b) of D85.4 (leave them empty) is not chosen. The
  fallback is used only for a persistently broken body; network
  errors and "idx missing" are handled as before.
- **D86.3 The gate.** Before use, the fallback must give byte-identical
  messages and identical points rows to the `.idx` path on healthy
  files, and the normal path must give identical output before and
  after the edit.
- **D86.4 The next run.** After session 94 is reviewed and committed,
  the owner runs 2022-11 alone on GitHub Actions. It is published only
  if the verify step passes. Cycle 2022-11-29T12 (flagged by
  dynamical.org, F131.2, unchecked by session 93) is covered by that
  run.
- **D86.5 Laptop sleep.** Session 93's last two cycles were only partly
  checked because the owner's laptop slept. Long local sessions run
  with the laptop kept awake.

---

## 2026-10-05: Session 94 finding: the whole-file fallback and its gate

**F136. The pull script now has a whole-file fallback (D86.2), the verifier accepts its new status, and the gate passed (D86.3): the normal path gives string-equal manifest and points rows before and after the edit; on two healthy files the forced fallback picks, for every planned field, exactly one walked message, byte-identical (SHA-256) to the `.idx` range's bytes, with points rows equal to the normal path's; and two broken F135 files fall back by themselves, each walk ending at the file's last byte, every field with exactly one passing message and status "ok (whole file)". Nothing was published and no workflow was run. Scripts: `scripts/session91_grib_pull.py` (edited; SHA-256 `b52ffc2ee741853079aa8cb7b63850645fb93974a6e4f39d7f20fb212a432f1f`), `scripts/session92_verify_chunk.py` (edited; `7b59a5c2cfd1b15c8e8c1e769b5b1336735adef151b43eb4487c302a4a18af6a`), `scripts/session94_fallback_gate.py` (new; `0aa3b713ef37f4c9614d60340fbe39f93a55d908fb84438bce362b98ee4f50c8`). The workflow is unchanged (`804b6d35...02a6`). Full real output, with both diffs: `notes/session-94-output.txt`. Run 2026-10-05. Python 3.12.2, eccodes 2.48.0 (ecCodes library 2.48.0), numpy 2.5.2, requests 2.34.2.**

**F136.1 Step 0 and Step 1.**
- `git status --porcelain` printed nothing, not `?? docs/session-94.md`: the prompt file was already committed, in 6e2eee2 (session 93's commit). The tree was clean, so the session went on (reading 1).
- The last entries were D85 and F135; no D86 or F136 existed in either DECISIONS file. SHA-256 equal to F134 and F135: the pull script (`72c263b2...652e`), the verifier (`f61136a8...1955`), the workflow (`804b6d35...02a6`) and `session93_diagnose.py` (`fbaf73a1...9581`). Read: D83 to D85, F133 to F135, the pull script and the verifier in full.
- **What session 91's per-message check tests** (inline in `process_file`, HEAD l.658-696): `discipline`, `parameterCategory`, `parameterNumber`, `typeOfFirstFixedSurface`, `level`, `stepType`, `startStep` and `endStep` against the field's identity in `FIELDS` plus `expected_steps` (l.665-671); `dataDate` and `dataTime` against the cycle (l.672-674); `validityDate` and `validityTime` against cycle plus forecast hour, then `check_valid` (l.675-677); the grid geometry (`Ni`, `Nj`, first and last latitude and longitude, both increments) against the positions file and `gridType` `regular_ll` (l.678-680); a finite, non-missing value at every airport's four grid indices (l.681-690). It tests the step range, so the TMAX, TMIN and DSWRF windows are told apart; the prompt's stop condition did not apply. **"Broken body"** is set in `Fetcher.get` (HEAD l.350-352, retried) and raised as the final `DownloadError` at l.357.
- D86 was copied with `sed` from `docs/session-94.md` lines 79 to 108 into DECISIONS.md lines 3412 to 3441 (heading at 3410) and checked byte-equal with `diff`, before any other edit or network call.

**F136.2 The pull script (Step 2; full diff in the output file).**
- `Fetcher.get` raises `BrokenBody` (a subclass of `DownloadError`, same message text) when its last try failed with a broken body. `process_file` catches it and sends the file to `process_whole_file`; anywhere else it stops the chunk as before. Network errors, HTTP errors, a 404 and "idx missing" are unchanged.
- `Fetcher.get_whole`: one GET of the whole file, session 91's retry policy; the body must equal the response's Content-Length, otherwise retried as a network error. `_whole_lock` holds at most one whole file in memory across all workers.
- `walk_messages`: from byte 0, "GRIB", edition 2, the 8-byte total length, "7777" at the end, then the next; it must end at the file's last byte. A failed walk makes every planned field "check failed".
- Session 91's check was moved, unchanged, into `check_message`, which `process_file` now calls. The fallback applies it to every walked message for every planned field: exactly one must pass, else "check failed". The passing message's values (the same decode and index read) get status "ok (whole file)" (`STATUS_WHOLE`, added to `STATUSES`). All planned fields of a fallen-back file come from the whole file.
- Records: fallback files, bytes and "ok (whole file)" messages in the progress lines, the failure summary and the meta (with one line per fallback file); whole-file requests and bytes in the meta.

**F136.3 The verifier (Step 3; diff in the output file).** "ok (whole file)" is valid (through session 91's `STATUSES`), is treated as ok by "ok values", "non-ok values" and the local `--gate`, and its count is printed beside "idx missing". Tests on copies of the 2022-01 files (one `mktemp -d`, deleted; re-gzip round trip identical): untouched exit 0, 13 of 13; (a) to (g) each fail exactly as in F134.3 (same checks, same counts); **(h) one ok row changed to "ok (whole file)": exit 0, 13 of 13, its count 1; (i) one ok row changed to an invented status: exit 1, "statuses" and "non-ok values" fail.** 10 of 10 as specified. `MLwx-pull/` unchanged (SHA-256 equal to F134.1).

**F136.4 Step 4: the normal path is unchanged. PASSED.** HEAD (`git show`, SHA-256 equal to F133's final) and the edited script, each through `process_file` on 2022-11-29T18 f000, f001 and f010: 30 manifest rows and 153 points rows each, statuses ok 27 and absent by design 3 in both; **manifest rows and points rows string-equal; no file fell back.** Each: 3 `.idx` and 27 message requests, 22,773,312 B, 0 retries.

**F136.5 Step 5.1: the fallback forced on healthy files. PASSED.** 2022-11-29T18 f000: whole file 508,028,392 B, 696 messages walked (696 `.idx` lines), walk ends at the last byte. f001: 536,786,974 B, 743 walked (743 lines), ends at the last byte. For each of the 7 and 10 planned fields: exactly 1 passing message, its range equal to the `.idx` range, SHA-256 equal to the `.idx` range's bytes (17 of 17; table in the output file); absent by design stays so. Points rows (102) string-equal to Step 4's.

**F136.6 Step 5.2: the broken files fall back by themselves. PASSED.** No value printed.

| file | trigger (first field, after 5 retries) | whole file | walked | ends at last byte | fields with exactly 1 passing | status |
|---|---|---|---|---|---|---|
| 2022-11-29T18 f002 | t2m 419336616-420214434, broken body | 539,275,914 B | 743 | yes | 10 of 10 | ok (whole file), 10 |
| 2022-11-30T06 f024 | t2m 427454899-428323505, broken body | 553,400,757 B | 743 | yes | 10 of 10 | ok (whole file), 10 |

The messages found by the walk sit at other offsets than the `.idx` gives (for example f002 t2m at 417969131-418848475), as F135.4 implies. Time per broken file on the owner's connection: 376 s and 520 s (each includes 62 s of retry waits).

**F136.7 Requests and bytes.** Only `noaa-gfs-bdp-pds.s3.amazonaws.com`. Step 4: 60 requests (6 `.idx`, 54 message), 45,546,624 B. Step 5.1: 21 (2 `.idx`, 17 message, 2 whole), 1,059,159,186 B. Step 5.2: 4 counted (2 `.idx`, 2 whole), 1,092,758,440 B, plus 12 broken-body message tries that the fetcher does not count (about 10.5 MB, from the range lengths). In all 97 requests, 2,197,464,250 B counted (about 2.21 GB with the broken tries). Every byte was held in memory; the gate's one temporary directory held only the HEAD script copy and was deleted. Gate run 1,773 s, once, with the laptop kept awake.

**F136.8 Readings made where the prompt is silent (for the owner to confirm or change).**
1. Step 0.1's empty `git status` (F136.1) was taken as passing the check's intent, not as "anything else".
2. "Still gives a broken body after the retries" is read as: the last of the six tries failed with a broken body. A run of failures that ends with a network error stays a `DownloadError` and stops the chunk.
3. The new status is added to session 91's `STATUSES`, so the verifier's "statuses" check accepts it through its import, and the meta's "messages" line now lists five statuses (with "ok (whole file) 0" on a normal month).
4. An "ok (whole file)" manifest row has an empty `idx_line`; `byte_range` and `bytes` give the message's place in the whole file; `reason` gives the file size, the walk count and the trigger. `step_range` and `process_type` are read from the selected message, as on the normal path.
5. Content-Length is read from the GET's own headers (no HEAD request, which the prompt does not list). A missing Content-Length, a 404 or another non-retried status stops the chunk; the byte budget, if set, is reserved once from Content-Length.
6. The walk also requires a total length of at least 20 bytes that fits inside the file.
7. One eccodes handle is made per walked message and every planned field's check is applied to it. A walked message that eccodes cannot open stops the run, as an unopenable message does on the normal path; none occurred.
8. The test-only spot check (`--spot-check`) is not run on whole-file messages, and spot results already read by range for that file are dropped.
9. The verifier's local `--gate` also treats "ok (whole file)" as ok ("every value check").
10. Step 4 calls `process_file` directly per file, since `--chunk` runs whole days, and writes the rows with run_chunk's own csv code; the HEAD copy reads the committed positions file by path. Step 5.1 forces the fallback by calling `process_whole_file` directly; the pull script has no force option. Step 5.1 also checks that the walked range equals the `.idx` range (stricter than asked).
11. The verifier's negative-test driver lived in the session scratchpad, outside the repo, as in session 92; on edited copies it updates the meta's SHA-256 so only the intended check fails, as session 92's results show it did.
12. Docstrings of both scripts were updated to describe the new status.

**F136.9 What this did not do.** No workflow run, push, Release change or `gh` call; the workflow is unchanged. No month was pulled or published, and no extract was written. No forecast value printed. No observation read; no score; nothing from 2026-27. Nothing under `data/` changed and nothing in `MLwx-pull/`; `data/models/` not touched. No bytes kept; no install; no account or token. SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing committed and no commit message written.

---

## 2026-10-05: Session 95 decision: F136 accepted, the 2022-11 run, and the all-months check (owner, planning chat)

**D87. Owner decisions, planning chat (after session 94): F136
accepted, the 2022-11 run, the pull complete, and the all-months
check.** Written at the start of session 95, before any other edit or
network call. No 2026-27 value has been read or scored.

- **D87.1 F136 accepted.** The owner accepts F136 and all twelve
  F136.8 readings.
- **D87.2 A note on session 94's Step 0.** `docs/session-94.md` was
  written before session 93 was committed, so it was committed with
  session 93 and session 94's Step 0 found a clean tree (F136.1).
  Harmless; nothing else was affected.
- **D87.3 The 2022-11 run.** After session 94 was committed and
  pushed, the owner ran 2022-11 alone on GitHub Actions with the
  whole-file fallback. The verify step passed 13 of 13 checks and the
  month was published. Statuses (owner's report from the job log): ok
  29,370; absent by design 360; ok (whole file) 270; idx missing 0;
  check failed 0. The owner reports the 270 messages are exactly
  F135's 27 broken files, so 2022-11-29T12 (flagged by dynamical.org,
  F131.2) was not affected. Session 95 confirms this from the files.
- **D87.4 The pull is complete.** The Release "Stage C GRIB pull"
  (`stagec-grib-pull-v1`) holds all 195 assets (65 months x 3). Its web
  page shows 197 because GitHub adds two "Source code" archives. The
  stage C f000 to f024 pull is complete.
- **D87.5 Session 95 checks all 65 months.** It downloads every asset
  not held locally into `MLwx-pull/` (outside the repo), checks each
  against the Release digest and its meta, runs the verifier on every
  month, checks the totals against the full plan, and runs the
  extended gate on every month at EGLC, LFPG and DSM (lead 24). It
  writes a committed inventory of the Release,
  `data/processed/session95_pull_inventory.csv`.
- **D87.6 GFS v17 (planning-chat check, 2026-10-05, not checked by
  this session).** The NWS notices page lists SCN 26-88 (2 October
  2026) as the newest Service Change Notice; none is for GFS v17. With
  30 days' notice, the earliest go-live is about 4 November 2026.

---

## 2026-10-05: Session 95 finding: all 65 months downloaded and checked

**F137. All 195 Release assets are now held in `MLwx-pull/`, each equal to its Release digest, and every check passed: every meta as expected; the verifier 13 of 13 on all 65 months; no value outside the bounds and no read-back mismatch; the union of all months equals the full plan (7,828 cycles, 195,600 files, 1,956,000 manifest rows, 1,932,528 messages, 9,975,600 points rows), with no key in two months; "ok (whole file)" exactly 270, exactly F135.3's 27 files; check failed 0, idx missing 0. The extended gate passed on every month: 5,861 station-days at EGLC, LFPG and DSM, all seven columns equal, exact equality, 0 mismatches, 0 not rebuilt. The first download attempt stopped on an HTTP 500 and the script was changed on the owner's terms (F137.3). Script: `scripts/session95_check_release.py` (new; modes `--release`, `--download`, `--months`, `--totals`, `--negative`, `--gate`, `--inventory`; final SHA-256 `32c3ed772745b930fa00f06cd9dd300decb45c743e173bec725004c8c24f2af0`). Inventory: `data/processed/session95_pull_inventory.csv` (195 rows, SHA-256 `7177b6612224358051018bb6ef1efed1c7e3bfc88ac08940aa6d1bea0918b70a`) and its `.meta.txt` (`de7bdbd6a57eb55276167c8c7da0e19f7f032de979480a481ac2a9324106be8a`). Full real output: `notes/session-95-output.txt`. Run 2026-10-05. Python 3.12.2, eccodes 2.48.0 (ecCodes library 2.48.0), numpy 2.5.2, requests 2.34.2.**

**F137.1 Step 0 and Step 1.** `git status --porcelain` showed only `?? docs/session-95.md`. The last entries were D86 and F136; no D87 or F137 existed in either DECISIONS file; the new script and inventory did not exist. SHA-256 equal to the record: pull script `b52ffc2e...2f1f` and verifier `7b59a5c2...af6a` (F136), workflow `804b6d35...02a6` (F134, F136), positions file `cf86c692...fd08` (F133), `session81_training_set.csv` `ab8f25f2...8d4a` (F122.3). `MLwx-pull/` held exactly the three 2022-01 files, SHA-256 equal to F134.1. Free disk: 25 GiB. Read: D83, D84, D86, F133 to F136, SPEC 3.4 and 8.7, both scripts in full. D87 was copied with `sed` from `docs/session-95.md` lines 115 to 148 into DECISIONS.md lines 3499 to 3532 (heading at 3497) and checked byte-equal with `diff` and `cmp`, before any other edit or network call.

**F137.2 The Release (Step 2; 2026-10-05T20:28:49Z).** "Stage C GRIB pull", tag `stagec-grib-pull-v1`, not draft, not prerelease, published 2026-10-03T18:35:03Z. **195 assets**: every plan month 2021-03 to 2026-07 has its three files; none outside the plan, no other asset; all "uploaded", all with a SHA-256 digest. The 2022-01 assets equal F134.1 and the local files (sizes and SHA-256). Total 1,257,990,242 B (points 1,208,179,680; manifests 49,718,867; meta 91,695), against F135.2's 192 assets 1,238,178,639 B (1,189,134,875; 48,956,737; 87,027): the difference, 19,811,603 B, is exactly 2022-11's three assets (19,044,805; 762,130; 4,668).

**F137.3 The download (Step 3), two attempts.**
- **Attempt 1 (20:28:57Z):** 36 of 192 downloaded (the meta files 2021-03 to 2024-03 except 2022-01, 52,255 B, each checked against its digest), then `chunk_2024-04.meta.txt` answered HTTP 500 on its first try and both retries (waits 2 s and 4 s). The script stopped as the prompt says; no temporary file was left; the 39 files then held all equalled their digests (checked offline against the Step 2 listing). Reported to the owner.
- **The change (owner's terms, after review):** the download step now first checks every file already in `MLwx-pull/` against its Release size and SHA-256 (a mismatch or a file not in the Release stops), then downloads only the assets not held. This is its normal behaviour, not a resume mode. Retries: at most 3 after the first try, waits 10, 30 and 90 s, on a network error, HTTP 5xx or a digest mismatch; any other HTTP status stops at once. The Step 2 listing is re-used if under an hour old, else the Release is listed again and must give the same 195 names, sizes and digests. Unchanged: temporary name then rename (by `os.link`, which never overwrites), no overwrite or deletion of a held file, no other host.
- **Attempt 2 (20:34:13Z):** the Step 2 listing was 325 s old and was re-used (0 API requests). 39 held files checked, all equal. 156 downloaded, 1,237,299,527 B, 484.7 s, 156 requests, 0 retries. Hosts: `github.com` and its redirect `release-assets.githubusercontent.com`.
- In all: 192 files, 1,237,351,782 B (equal to the Release's sizes). At the end `MLwx-pull/` holds exactly 195 files, each SHA-256 equal to its Release digest, and no temporary file.

**F137.4 The metas (Step 4.1).** All 65: both data-file SHA-256 equal the local files'; positions SHA-256 equals the committed file's; arguments `--chunk --month <m> --hours 0-24 --out out --workers 16` (16 workers everywhere). Script SHA-256: 2022-11 F136's `b52ffc2e...2f1f`; the other 64 F133's `72c263b2...652e`. Versions in every meta: Python 3.12.14, eccodes 2.48.0, ecCodes library 2.48.0. HTTP 404: 0 in every month. Retries: 135 in 2022-11, 1 in 2023-01, 0 elsewhere. 2022-11's meta records 27 whole-file fallbacks, 14,713,332,129 B, 270 messages "ok (whole file)", each walk of 743 messages ending at the file's last byte; chunk 1,022.4 s. Sums over the 65 metas: 1,563,543,208,326 B downloaded on Actions, 26,365.7 chunk seconds. The per-month table (start, end, seconds, workers, retries, 404, bytes, whole-file requests and bytes) is in the output file.

**F137.5 The verifier and the ranges (Step 4.2, 4.3).** All 65 months: exit 0, 13 of 13. "idx missing" 0 in every month; "ok (whole file)" 270 in 2022-11, 0 elsewhere. `--ranges`: 0 values outside the bounds and 0 read-back mismatches in every month (394,235,712 value cells). Per field over all months (units as GRIB gives them): t2m 242.75171875 to 322.44296875000003; tcdc 0.0 to 100.0; u10 -33.96760498046875 to 27.934453125; v10 -30.71757568359375 to 29.15512939453125; d2m 236.704052734375 to 302.3; t850 240.08433593750001 to 312.0498046875; dswrf 0.0 to 1164.42; prmsl 95075.65000000001 to 105505.4375; tmax2m 243.53779296875 to 322.62939453125; tmin2m 242.72767578125 to 320.51044921875.

**F137.6 Totals and the whole-file check (Step 5.1 to 5.4).** The full plan from session 91's own functions gives 7,828 cycles, 195,600 files, 1,956,000 manifest rows, 1,932,528 messages and 9,975,600 points rows, equal to F133.5 and the prompt. The union over all 65 months equals it by key set and count for cycles and files (each from both the manifests and the points files), manifest rows, messages and points rows; no key in more than one row; no key outside its cycle's month. Status totals: ok 1,932,258; absent by design 23,472; idx missing 0; check failed 0; ok (whole file) 270. **The (cycle, hour) files with any "ok (whole file)" message are exactly F135.3's 27** (read from DECISIONS.md and equal to the prompt's list), each with all ten fields so; no other message has that status. Every 2022-11-29T12 message is ok (247 ok, 3 absent by design), so that cycle, flagged by dynamical.org (F131.2), is whole, as the owner reported (D87.3). Whole-file values per field, against 2022-11's normal ok values, 0 outside the bounds; minimum and maximum in the output file.

**F137.7 Negative tests (Step 5.5; one `mktemp -d` directory, deleted).** (a) A copy of `chunk_2021-03.meta.txt` passes the digest check; with byte 100 changed (same size) it fails. (b) The totals check on copies of all 65 points files and 64 manifests (`manifest_2023-06.csv.gz` left out) fails on the missing keys: 120 cycles, 3,000 files, 30,000 manifest rows and 29,640 messages missing from the manifests (2023-06's plan exactly); the points checks pass. `MLwx-pull/` unchanged (SHA-256 of all 195 files equal before and after).

**F137.8 The extended gate (Step 6). PASSED on every month.** The verifier's own `--gate`, EGLC and LFPG 12z lead 24, DSM 18z lead 24. 5,871 station-days in the 65 months; **5,861 rebuilt and compared, all 5,861 with all seven columns equal (exact equality); 0 mismatches; 0 not rebuilt**. By airport: EGLC 1,953, LFPG 1,953, DSM 1,955 station-days (every committed row, F122.3), 13,671, 13,671 and 13,685 values equal. Every column 5,861 of 5,861. **No committed row: 10**, not a failure: EGLC 2023-06-11, 2024-08-14, 2025-11-21; LFPG 2022-07-23, 2022-07-25, 2026-07-08; DSM 2022-11-30 (F122.3's days with no row); and 2026-08-01 at all three (outside the window, reading 7). One gated station-day uses "ok (whole file)" messages: DSM 2022-11-30 (cycle 2022-11-29T18, its f024 and f022 messages); it has no committed row (F122.3), so the whole-file values are not gate-checked against the record. **Not gated:** YSDU, RNO and KSFO use lead 26, which an f000 to f024 extract does not hold; the 45 other airports have no committed record.

**F137.9 The inventory (Step 7).** 195 rows sorted by month then asset name; columns `month`, `asset`, `bytes`, `sha256`, `script_sha256`, `run_start_utc`; `\n` line ends; each `sha256` equals the Release digest (from a listing at 2026-10-05T20:56:33Z) and the local file. SHA-256 in the heading above. The meta follows the positions file's meta style and names the Release, the read time, the script and its SHA-256, and the row count.

**F137.10 Requests and bytes.** GitHub REST API, unauthenticated: 12 requests (four listings of 3: Step 2 twice, download attempt 1, the inventory; attempt 2 re-used the listing), about 645 kB each listing. Release downloads: 195 requests (attempt 1: 36 ok and 3 HTTP 500; attempt 2: 156), 1,237,351,782 B written. No other host; no GRIB request.

**F137.11 Readings made where the prompt is silent (for the owner to confirm or change).**
1. **The download change (F137.3), on the owner's terms:** the first attempt (36 of 192, then `chunk_2024-04.meta.txt` HTTP 500 on all three tries), the change (check held files, download only the missing, 3 retries at 10, 30, 90 s on network errors, 5xx and digest mismatches), why (a transient server error, and the first version refused to run unless exactly 192 files were missing), and the final script SHA-256 `32c3ed77...2af0`. The script keeps no listing between runs, so the re-use reads the saved Step 2 output (`--listing`, a file in the session scratchpad, read only); when re-used, each download link is built in GitHub's standard form `https://github.com/zadams03/MLwx/releases/download/stagec-grib-pull-v1/<name>`, and a fresh listing must give links of that form.
2. Step 2 was run twice: the first run's saved log was cut short by my own `head` in the shell; the second is the one recorded.
3. Steps 4.2 and 4.3 ran the verifier twice per month, once plain and once with `--ranges`, as the prompt words them.
4. "Arguments are `--chunk --month <m> --hours 0-24`" is read as those first, then the workflow's own `--out out --workers 16`, reported.
5. Cycles and files are checked from both the manifests and the points files; keys are compared as integers built from cycle, hour and field or airport.
6. Negative test (b) leaves out 2023-06, and copies all points files too, so the check runs exactly as on the real files.
7. **The 2026-08-01 target dates** (2026-07's last 12z and 18z cycles) are reported by the verifier's `--gate` as "no committed row", not "not rebuilt", because it looks for the committed row first, and the training set ends 2026-07-31. They are recorded as outside the window. Nothing was "not rebuilt".
8. Which gated station-days use a whole-file message is found from the manifests with a copy of the verifier's field map (`session92_verify_chunk.py` l.328-330, 345-346).
9. 2022-11's 135 retries equal 27 x 5, one broken-body run of retries per fallen-back file (arithmetic only; the meta does not split them).

**F137.12 What this did not do.** No GRIB request; no observation read beyond the gate's columns (the verifier's own nine-column read); no score, error, MAE, bias or skill; nothing from 2026-27; no forecast value printed beyond the ranges and Step 5.4's minimum and maximum (no gate mismatch occurred); no push, workflow run or Release change; no token, `gh` or sign-in; nothing in `MLwx-pull/` changed except the 192 added assets; no file under `data/` changed except the two new inventory files, and `data/models/` was not touched; no existing script edited; nothing installed. SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing committed and no commit message written.

---

## 2026-10-06: Session 96 decision: F137 accepted, GFS v17, and the stage C development table (owner, planning chat)

**D88. Owner decisions, planning chat (after session 95): F137
accepted, GFS v17, and the first step on stage C's build choices: the
development table, the curve's baseline, and the rules for features at
every lead.** Written at the start of session 96, before any other
edit. No 2026-27 value has been read or scored.

- **D88.1 F137 accepted.** The owner accepts F137 and all nine F137.11
  readings, including the change to the download step (F137.3).
  Reading 9 (2022-11's 135 retries equal 27 x 5) is the script's
  arithmetic inference; the meta does not record it.
- **D88.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-06, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-89 (2 October
  2026, model changes for the RRFS implementation). Correction to
  D87.6: SCN 26-89 was posted on the same day as SCN 26-88, so 26-88
  was not the newest. With 30 days' notice, the earliest go-live is
  about 5 November 2026. PNS 26-29's proposed October 2026 date can no
  longer be met.
- **D88.3 What comes first.** D82.5's build choices need a development
  table: for each development airport (EGLC, LFPG, DSM, YSDU, RNO,
  KSFO), every GFS cycle in the pull and every forecast hour 0 to 24,
  the record's features rebuilt from the stored grid values, and the
  hourly observation at the valid time. Session 96 builds it and gates
  it against the committed record. It fits no model and computes no
  score.
- **D88.4 The curve's baseline.** SPEC 8's recipe `B+D,L,R,T`, applied
  unchanged at each cycle hour and lead: one model per airport, cycle
  hour (00, 06, 12, 18 UTC) and lead, so 100 models per airport, with
  the record's settings, column order and complete-case rule. This is
  the proven method applied at every hour, one well-understood input
  first (D72.2(b)). It is recorded now and fitted later. D82.5's
  alternatives (one model per lead with the cycle hour as an input; one
  model with lead and hour as inputs) are each compared against it by
  time-ordered cross-validation.
- **D88.5 Features at every lead.** The record's definitions, extended:
  (a) Instantaneous fields (temperature, cloud cover, 10 m wind, dew
  point, 850 hPa temperature, sea level pressure) at every lead,
  including f000 (the analysis), by the record's arithmetic
  (bilinear, elevation constant on temperature only, rounding as SPEC
  8.8 G4 and G7).
  (b) R is the mean downward shortwave radiation over the 2 hours
  ending at the valid time. GFS gives A(N), the average over (W, N],
  W = 6 x floor((N-1)/6). If N - W >= 2: R = ((N - W) x A(N) -
  (N - 2 - W) x A(N - 2)) / 2, where the second term is zero when
  N - 2 = W (so R = A(N) at leads 2, 8, 14, 20). This is the record's
  de-accumulation at lead 24. If N - W = 1 (leads 7, 13, 19): R =
  (A(N) + 6 x A(W) - 5 x A(W - 1)) / 2, adding the last hour of the
  previous 6-hour window. R does not exist at leads 0 and 1.
  (c) T is the sea level pressure at lead N minus that at lead N - 3,
  same cycle, in hPa, from the two rounded pressures as the record
  does. At lead 3 it uses the f000 analysis. T does not exist at
  leads 0 to 2.
  (d) Season terms from the valid date, by the record's
  `year_fraction`.
  (e) GFS's 6-hour maximum and minimum 2 m temperature are kept as
  raw columns (bilinear, degrees C, rounded to 3 decimals, no
  elevation constant) for the later daily maximum work. They are not
  features of the baseline.
- **D88.6 Leads 0 to 2.** The complete-case rule stands. Rows at leads
  0 to 2 stay in the table, marked incomplete and counted, never
  filled. A GFS run arrives about 3.5 to 4 hours after its start time,
  so these leads are already in the past when it lands.
- **D88.7 The observation.** At every valid whole hour: the nearest
  usable report within 15 minutes, inclusive (SPEC 4.5, 8.8 G2 and G3,
  the record's `pair_nearest`; a tie keeps the earlier report). The
  same at every airport.
- **D88.8 Where the table lives.** About 1.17 million rows, so it is
  kept outside the repository, in `MLwx-stagec/` beside `MLwx-pull/`.
  The repository holds the script, a meta file with every table file's
  SHA-256, and a counts file. The table is rebuilt exactly from the
  Release and the committed observation files.
- **D88.9 Rules for build choices.** Before any cross-validation score
  is computed, a DECISIONS entry fixes the folds, the metric, and a
  rule of the form "keep the simpler option unless the other wins by
  more than a stated margin". Build choices are never quoted as
  results (SPEC 2.5).
- **D88.10 SPEC 6.** The stage C bullet records that the pull is
  complete and checked (D87, F137), and points to this entry (session
  96, Step 2).
- **D88.11 Sequence.** Session 96: this entry, the SPEC edit, the
  table and its gate. Then, planned: session 97 writes D88.9's entry
  before any score, then fits the baseline and scores raw GFS and the
  baseline per lead by cross-validation. D82.5's comparisons, the daily
  maximum, and bias drift (D81.10(b)) follow, one change at a time.
  Stage C's claim design is fixed at its lock.

---

## 2026-10-06: Session 96 finding: the stage C development table and its gate

**F138. The stage C development table exists and passed its gate. For the six development airports, every cycle in the pull's plan and every forecast hour 0 to 24, it holds the record's features rebuilt from the stored grid values (D88.5) and the nearest hourly observation (D88.7): 195,600 rows per airport, 1,173,600 in all, in `MLwx-stagec/` beside the repo (D88.8). At EGLC and LFPG 12z lead 24 and DSM 18z lead 24, all 5,861 committed station-days are equal in all ten shared columns and the observation (the record's pairing), exact equality, 0 mismatches. The new R and T arithmetic passed its own tests first. No model was fit and no score computed. Script: `scripts/session96_stagec_table.py` (new; modes `--inputs`, `--test-rt`, `--build`, `--gate`, `--records`, `--guard-check`; SHA-256 `40b63d006a3de4b4b796476c6b2408700bc9200a508feda804a187531b666eee`). Counts: `data/processed/session96_stagec_dev_counts.csv` (150 rows, SHA-256 `304d25a6689b1442ca0b184244a93bc031e9a9157e313cb4b96a04ce22383dfb`). Meta: `data/processed/session96_stagec_dev_table.meta.txt` (`eace666a0f1ab2b65614c340899b849eb0e97c25cf49eaaa45eb83747ce89463`). Full real output: `notes/session-96-output.txt`. Run 2026-10-06, offline. Python 3.12.2, numpy 2.5.2, eccodes 2.48.0 (ecCodes library 2.48.0).**

**F138.1 Steps 0 to 2.** `git status --porcelain` showed only `?? docs/session-96.md`. The last entries were D87 and F137; no D88 or F138 existed in either DECISIONS file; the script, both new `data/processed/` files and `MLwx-stagec/` did not exist. SHA-256 equal to the record: verifier `7b59a5c2...af6a` (F136), `session95_check_release.py` `32c3ed77...2af0` and the inventory `7177b661...b70a` (F137), positions `cf86c692...fd08` (F133), training set `ab8f25f2...8d4a` (F122.3), `session86_forward_build.py` `da2ff50c...4125` (F128, F129.1). Read: D82, D83, D87, F128, F133, F134, F137; SPEC 3.4, 4.5, 6, 7.2, 8.1 to 8.3, 8.7, 8.8; `session86_forward_build.py` and `session92_verify_chunk.py` in full. Observation files: the six yearly routine files per airport (the files F131.6 counted), 36, all tracked, SHA-256 in the output file; their recorded queries run without a gap from 2021-03-24T00:00 to 2026-08-01T00:00 (exclusive end) at all six airports, so they cover the window. Free disk 16 GiB. D88 was copied with `sed` from `docs/session-96.md` lines 114 to 198 into DECISIONS.md lines 3581 to 3665 (heading at 3579) and checked byte-equal with `diff` and `cmp`, before any other edit (my first `diff` used a range one line off and failed; on the right range both are equal). SPEC 6: the old text was found once and replaced as Step 2 says; nothing else in SPEC changed.

**F138.2 Inputs (Step 3).** All 195 files in `MLwx-pull/` equal the inventory (names, bytes, SHA-256). **None of the 36 observation `.meta.txt` files records a SHA-256** (they record the pull time and exact query); their SHA-256 are now in the output file and the table's meta. The six airports' four grid points and weights were read with session 91's `read_positions`, as the verifier's `--gate` does; at all six the position used equals SPEC 3.4's grid point, and session 86's and session 91's parsing of SPEC 3.4 and the params CSVs agree.

**F138.3 R and T on their own (Step 4). All passed.** Lead 24, five made-up input sets: the new R and T are the identical float to session 86's `derive`. Lead 26 (native window), three sets: R is A(26) rounded, equal to `derive`. Exact fractions on a made-up hourly series: D88.5(b) recovers the true 2-hour mean at 23 of 23 leads 2 to 24 (A(N) alone at 2, 8, 14, 20; three terms at 7, 13, 19; two terms elsewhere). R is missing at leads 0 and 1; T at leads 0 to 2; T at lead 3 uses f000.

**F138.4 The table (Step 5).** Rows from session 91's plan (`all_months`, `month_cycles`, `plan_chunk`, hours 0 to 24), cycle then lead: 195,600 per airport. 24 columns: `station`, `cycle_utc`, `cycle_hour`, `lead`, `valid_utc`, `temp`, `temperature_grib_c`, `t2m_raw`, `cloud_cover`, `wind_speed_10m`, `dew_point_2m`, `t850`, `dewpoint_depression_t2m_floored`, `lapse_rate_t2_t850`, `dswrf_2h_wm2`, `pressure_tendency_3h_hpa`, `season_sin`, `season_cos`, `tmax2m_c`, `tmin2m_c`, `obs_tmpc`, `obs_time_utc`, `uses_whole_file`, `complete_case`. Record names (from `session81_training_set.csv`): the ten from `temp` to `season_cos` except `t2m_raw`, `dew_point_2m` and `t850` (SPEC 8.8 G4, G7 names). Imported: from session 86 `load_airports`, `year_fraction`, `window_start`, `parse_reports`, `pair_nearest`, `pair_historical` (and `derive` as the Step 4 reference); through session 92, session 91's plan, `read_positions`, `bilinear_stored` and `derive`. Written new: R and T (D88.5(b), (c)) and the one-line roundings of `t2m_raw`, `dew_point_2m`, `t850`, `tmax2m_c`, `tmin2m_c`. Build run time 180.0 s.

| file | rows | bytes | SHA-256 |
|---|---|---|---|
| `stagec_dev_EGLC.csv.gz` | 195,600 | 8,315,375 | `af8848e091c79aecac5f809536e4dec20757d288f7ebc1cf3e830d33a69c9126` |
| `stagec_dev_LFPG.csv.gz` | 195,600 | 8,377,218 | `5b113123c7642eefb8d212cbe5151f43e8ba343a231dc90d4461ed104e6b661f` |
| `stagec_dev_KDSM.csv.gz` | 195,600 | 8,507,654 | `17461736cd23585781ebf01a842469a1ea6b0e93571bea250869a23271dc0e32` |
| `stagec_dev_YSDU.csv.gz` | 195,600 | 8,431,107 | `57a11a4f00250304f289de158223eff45f841d572e3c3c7f65e5b6fc6c0fa829` |
| `stagec_dev_KRNO.csv.gz` | 195,600 | 8,692,141 | `6e2d0779f6b5ea92dc77e3b074030ac3676bd90cffe3b44ab6e3441c06831ec3` |
| `stagec_dev_KSFO.csv.gz` | 195,600 | 8,637,256 | `11fa6385f05c57cf627734d9caed13927f1e176e07c5fc039f700d30fd1ceff8` |

Observation files: reports read 46,734 (YSDU) to 46,938 (DSM); no usable `tmpc` 1 to 10 per airport, none non-finite; one repeated timestamp (DSM, first kept, counted); tie hours 0.

**F138.5 The gate (Step 6). PASSED.** From the written table, exact equality, no tolerance. Columns compared (held by both): `temp`, `season_sin`, `season_cos`, `cloud_cover`, `wind_speed_10m`, `dewpoint_depression_t2m_floored`, `lapse_rate_t2_t850`, `dswrf_2h_wm2`, `pressure_tendency_3h_hpa`, `temperature_grib_c`; and `obs_c` against the record's pairing (`pair_historical`) of the same reports.

| airport | committed rows | compared | each of the 10 columns equal | `obs_c` equal | committed, no table row | table, no committed row | nearest is not the record's report |
|---|---|---|---|---|---|---|---|
| EGLC 12z lead 24 | 1,953 | 1,953 | 1,953 | 1,953 | 0 | 3 (2023-06-11, 2024-08-14, 2025-11-21) | 0 |
| LFPG 12z lead 24 | 1,953 | 1,953 | 1,953 | 1,953 | 0 | 3 (2022-07-23, 2022-07-25, 2026-07-08) | 0 |
| DSM 18z lead 24 | 1,955 | 1,955 | 1,955 | 1,955 | 0 | 1 (2022-11-30) | 0 |

5,861 station-days, equal to F137.8's; mismatches 0. The seven table-only days are F122.3's days with no row. **Not gated:** YSDU, RNO and KSFO (record lead 26, not in this table; their rows come from the same code); every other cycle hour and lead (R and T there are tested only by Step 4); `t2m_raw`, `dew_point_2m`, `t850`, `tmax2m_c`, `tmin2m_c` (no committed column); the whole-file values (DSM 2022-11-30 has no committed row).

**F138.6 Counts (Step 7.1).** Identical at all six airports: R empty, lead too short 15,648 (leads 0 and 1) and input outside the pull window 7; T empty, lead too short 23,472 (leads 0 to 2) and outside the pull window 10; `tmax2m_c` and `tmin2m_c` empty, absent by design 7,824 each (lead 0); message not ok 0 everywhere; the other GRIB-derived columns never empty; rows using a whole-file message 51. Leads 0 to 2 have 0 complete-case rows (D88.6).

| airport | rows with no observation | complete-case rows, leads 3 to 24 (of 172,128) |
|---|---|---|
| EGLC | 186 | 171,963 |
| LFPG | 600 | 171,598 |
| DSM | 51 | 172,076 |
| YSDU | 1,991 | 170,379 |
| RNO | 457 | 171,723 |
| KSFO | 148 | 171,993 |

**F138.7 Repeatability and guards (Step 7.3, 7.4).** EGLC rebuilt into a `mktemp -d` directory is byte-equal to `MLwx-stagec/`'s (`af8848e0...9126`); the directory was deleted. `--records` also rebuilt all six in memory, byte-equal to the files, before writing the counts and meta. The guards refuse a valid time of 2026-08-01T00:00 and an observation at 2026-08-01T00:00, and allow 2026-07-31T23:00 and 23:59 (4 of 4).

**F138.8 Readings made where the prompt is silent (for the owner to confirm or change).**
1. **Both `temp` and `temperature_grib_c` are columns** (equal values): the record holds both, G15 names `temp`, and the prompt says "temperature".
2. `dew_point_2m` and `t850` take SPEC 8.8 G7's stored names and rounding (degC, 3 decimals); `t2m_raw` is `round(temp - constant, 3)` (G4).
3. **The instantaneous columns come from session 91's `derive`** (the code of F137.8's gate), called with the row's own values; its R and T inputs get a placeholder 0.0 and its R and T outputs are discarded, since R and T come from the new functions at every lead, lead 24 included (Step 4 shows they agree there). A placeholder never reaches the table: a column whose input is not ok is left empty (none occurred).
4. **A fourth empty reason, "outside pull window":** in the first cycles (2021-03-23T00 to T18) some R and T inputs are valid before 2021-03-24T00, so the pull does not hold them (7 R and 10 T cells per airport). Left empty, never filled; the prompt's three reasons do not cover it.
5. Season terms: `sin` and `cos` of `2 * math.pi * year_fraction(valid date)`, session 86's `derive` expression, with `year_fraction` imported.
6. Observations: a repeated timestamp keeps the first report, as session 86's `build_rows` does (DSM, 1). `pair_nearest` is given only the reports within 15 minutes (same result: it keeps only those and sorts them). The gate's `pair_historical` is given the file-order reports within 30 minutes of the hour, repeats included, as the record reads the file; file order was checked sorted.
7. `station` holds SPEC 3.4's code (DSM, RNO, SFO), as the training set does; file names use the ICAO code (KDSM, KRNO, KSFO).
8. Other airports' lines in the points files are decompressed (gzip cannot skip them) but skipped on the `icao` field; none of their values is converted or kept.
9. `uses_whole_file` counts a message as used only if it fed a non-empty column of the row. Booleans are written `true`/`false`; times as `YYYY-MM-DDTHH:MMZ`, as the pull files.
10. The gate's "nearest differs from the record's choice" compares report times (and counts value differences among them).
11. Before the real build, one trial build of EGLC alone went to the session scratchpad, to check run time and structure (counts only, no value printed); it was deleted, and its SHA-256 equals the real file's.
12. The counts file has, per airport and lead, four reason counts for each of the 15 GRIB-derived columns (season columns included), then no observation, whole file and complete case: 67 columns.
13. Archive step: nothing moved, for session 95's reasons (F137's output file).

**F138.9 What this did not do.** No network call. No model fit. No error, MAE, bias, skill, mean, spread or other statistic of any forecast or observation value: counts only. Nothing from 2026-27: no valid time after 2026-07-31T23:00 built and no observation after 2026-07-31T23:59 read. No value printed beyond the synthetic Step 4 numbers (the gate had no mismatch). No non-development airport's observation file opened, and none of its points values used. Nothing in `MLwx-pull/` changed (195 files, SHA-256 as the inventory). No file under `data/` changed except the two new files; `data/models/` not touched. No existing script edited. Nothing installed. SPEC edited only as Step 2 says; RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing committed and no commit message written.

---

## 2026-10-06: Session 97 decision: F138 accepted, GFS v17, and the rules for stage C's build choices (owner, planning chat)

**D89. Owner decisions, planning chat (after session 96): F138
accepted, GFS v17, and the rules for stage C's build choices: folds,
metric and decision rule (D88.9).** Written at the start of session 97,
before any other edit and before any cross-validation score. No
2026-27 value has been read or scored.

- **D89.1 F138 accepted.** The owner accepts F138 and all thirteen
  F138.8 readings, including: both `temp` and `temperature_grib_c`
  kept as columns; the instantaneous columns taken from session 91's
  `derive` with placeholder R and T inputs that never reach the table;
  and the fourth empty reason, "outside pull window" (7 R and 10 T
  cells per airport in the first cycles).
- **D89.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-06, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is still SCN 26-89 (2
  October 2026). The earliest go-live stays about 5 November 2026.
- **D89.3 Folds.** Three time-ordered folds, each with an expanding
  training window. A test year runs 1 August to 31 July:
  fold 2023-24: test cycles 2023-08-01T00 to 2024-07-31T18;
  fold 2024-25: test cycles 2024-08-01T00 to 2025-07-31T18;
  fold 2025-26: test cycles 2025-08-01T00 to 2026-07-31T18.
  With T0 the test year's start (1 August, 00:00 UTC): training rows
  are those with valid time before T0; test rows are those whose cycle
  starts on or after T0 and before the next 1 August. A row whose cycle
  is before T0 and whose valid time is on or after T0 is in neither,
  and is counted. Training thus uses only observations already known
  when the first test cycle starts. The 2022-23 fold is not used: its
  training window (about 1.4 years) is far shorter than the product's
  or the claim airports' (about 3.4 years, D82.7(e)), and would
  unfairly penalise options that fit many small models.
- **D89.4 The spent years.** 2024-25 and 2025-26 are spent at every
  development airport (F94, F109, F119; D71.1), so they may be used
  for build choices (D72.2(a), SPEC 2.5). The session-48 reserved-year
  guard stays unchanged in its own script and is not imported here.
  Nothing from 2026-27 is used.
- **D89.5 Metric.** Mean absolute error (MAE) of the hourly
  temperature, degrees C, full precision (SPEC 8.8 G24), on leads 3 to
  24. Rows: the common row set, meaning test rows that have an
  observation and are complete for every option compared (for the
  baseline, the table's `complete_case`). Per airport: one MAE over all
  its test rows, pooled across the three folds, four cycle hours and
  leads 3 to 24. Headline: the unweighted mean of the six airport
  MAEs. Fold level: per fold, the unweighted mean of the six airports'
  MAEs over that fold's rows.
- **D89.6 Decision rule.** The challenger replaces the incumbent only
  if all three hold: (a) the headline MAE is lower by more than 1
  percent of the incumbent's headline, that is (incumbent - challenger)
  / incumbent > 0.01; (b) the airport MAE is lower at 4 or more of the
  6 airports; (c) the fold-level MAE is lower in at least 2 of the 3
  folds. Otherwise the incumbent stays. A tie keeps the incumbent.
- **D89.7 The incumbent.** For D82.5's model-structure comparisons, the
  incumbent is D88.4's baseline (the proven recipe, unchanged, D72.2(b)),
  even though the alternatives use fewer models. Every later
  comparison names its incumbent in its own DECISIONS entry before it
  is scored.
- **D89.8 Scope of the rule.** It applies to every stage C build choice
  on the hourly curve. A choice is applied to the whole curve and to
  every airport identically: never per airport, cycle hour or lead.
  The daily maximum's metric is fixed in its own entry before any
  daily-maximum score. Changing these rules needs a new DECISIONS entry
  written before the affected score. Build-choice scores are never
  quoted as results (SPEC 2.5).
- **D89.9 The fitting code's gate.** Before any fold is scored, the new
  fitting code reproduces F109's recorded raw GFS and `B+D,L,R,T` MAEs
  at EGLC and LFPG (12z, lead 24) and DSM (18z, lead 24), exactly, from
  the table's rows on the record's days. This is a code check against
  numbers already on record. It is not a new look and decides nothing.
- **D89.10 Sequence.** Session 97: this entry, the fold counts, the gate,
  then the baseline and raw GFS scored per airport, fold, cycle hour
  and lead. No build choice is made. Then, planned: D82.5's
  alternatives, each against the baseline under D89.6, one at a time;
  then the daily maximum and bias drift (D81.10(b)). Stage C's claim
  design is fixed at its lock.

---

## 2026-10-06: Session 97 finding: the cross-validation folds, the gate, and the baseline scored

**F139. Every score in this entry is a build-choice score, not a result (SPEC 2.5); none is a claim, a pass or a fail. Offline. D89 was recorded first. The fold rows were counted under D89.3 with no fit. The new fitting code passed D89.9's gate: it reproduced F109's raw GFS and `B+D,L,R,T` MAEs at EGLC, LFPG and DSM exactly, 6 of 6. D88.4's baseline was then fit (1,584 models) and scored with raw GFS on the same rows, per airport, fold, cycle hour and lead 3 to 24. Headline (D89.5): raw GFS 1.4617, baseline 1.0498 degrees C. No build choice was made. Script: `scripts/session97_stagec_cv.py` (new; modes `--folds`, `--gate`, `--score`, `--guard-check`, `--meta`; SHA-256 `987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91`). Full real output: `notes/session-97-output.txt`. Run 2026-10-06. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

**F139.1 Step 0 and Step 1.** `git status --porcelain` showed only `?? docs/session-97.md`. The last entries were D88 and F138; no D89 or F139 existed in either DECISIONS file; the new script and the three new `data/processed/` files did not exist. SHA-256 equal to the record: the six table files (F138.4), the table meta `eace666a...9463` and counts `304d25a6...3dfb`, `session96_stagec_table.py` `40b63d00...6eee`, `session62_reserved_confirm.py` `9f8af9af...80b4` (D70.2), `session81_training_set.csv` `ab8f25f2...8d4a` (F122.3). `session63_reserved_confirm_grid.csv` is `0138ba039d0bd077e71b829789a8d3c93175e22493ed115f7503b2baa30f4ed3`; that value is recorded in `notes/session-85-output.txt` (lines 21 and 167), not in either DECISIONS file. Read: D70, D71, D72, D82, D88, F109, F122, F138; SPEC 2.5, 5, 8.1 to 8.3, 8.5, 8.8; the record script in full. D89 was copied with `sed` from `docs/session-97.md` lines 105 to 177 into DECISIONS.md lines 3736 to 3808 (heading at 3734) and checked byte-equal with `diff` and `cmp`, before any other edit.

**F139.2 The folds (Step 2, `--folds`, no fit).** Complete-case rows, leads 3 to 24, four cycle hours. Every airport and fold has 40 boundary rows (cycles of 31 July with valid times on 1 August: 1 + 7 + 13 + 19). Test rows of the three folds never overlap (0 at every airport); every training row's valid time is before its T0 (0 violations).

| airport | train 23-24 / 24-25 / 25-26 | test 23-24 / 24-25 / 25-26 | test dropped (not complete) | smallest model train |
|---|---|---|---|---|
| EGLC | 75,555 / 107,760 / 139,864 | 32,205 / 32,104 / 32,059 | 3 / 16 / 21 | 856 / 1,222 / 1,587 |
| LFPG | 75,370 / 107,541 / 139,600 | 32,171 / 32,059 / 31,958 | 37 / 61 / 122 | 844 / 1,209 / 1,566 |
| DSM | 75,647 / 107,847 / 139,964 | 32,200 / 32,117 / 32,072 | 8 / 3 / 8 | 858 / 1,223 / 1,588 |
| YSDU | 74,694 / 106,652 / 138,576 | 31,958 / 31,924 / 31,763 | 250 / 196 / 317 | 845 / 1,207 / 1,568 |
| RNO | 75,341 / 107,534 / 139,643 | 32,193 / 32,109 / 32,040 | 15 / 11 / 40 | 854 / 1,220 / 1,585 |
| KSFO (SFO) | 75,623 / 107,822 / 139,913 | 32,199 / 32,091 / 32,040 | 9 / 29 / 40 | 858 / 1,223 / 1,588 |

`data/processed/session97_stagec_cv_folds.csv`: 1,584 rows, SHA-256 `77fce6c7c288f37a9d63f4e9b9b8675cad26f0e9b8a2ba4b657084496fb01b66`.

**F139.3 The gate (Step 3, `--gate`, D89.9). PASSED, 6 of 6, exact equality.** Table rows on the training set's (station, valid date) keys, F109's fold by valid date; every selected row was complete case.

| airport | train (F122.4) | test (F109) | B+D,L,R,T: this fit = grid `final_mae` | raw GFS: this fit = grid `raw_mae` |
|---|---|---|---|---|
| EGLC 12z, lead 24 | 1,225 (1,225) | 364 (364; grid no_obs 1) | 1.0007550363323212 | 1.23621978021978 |
| LFPG 12z, lead 24 | 1,224 (1,224) | 365 (365) | 1.2368626165917669 | 1.4091397260273972 |
| DSM 18z, lead 24 | 1,225 (1,225) | 365 (365) | 1.4122847644111458 | 1.7043452054794521 |

**F139.4 The scores (Step 4, `--score`; build-choice scores, not results).** 1,584 fits, 118.8 s. The two methods' n are equal in every cell. MAE in degrees C, common row set (D89.5).

| airport | n | raw GFS | baseline | raw GFS by fold 23-24 / 24-25 / 25-26 | baseline by fold |
|---|---|---|---|---|---|
| EGLC | 96,368 | 0.9725 | 0.7742 | 0.9614 / 0.9891 / 0.9672 | 0.7491 / 0.8010 / 0.7725 |
| LFPG | 96,188 | 1.1596 | 0.8937 | 1.1477 / 1.1739 / 1.1571 | 0.8653 / 0.9434 / 0.8726 |
| DSM | 96,389 | 1.7582 | 1.2034 | 1.9144 / 1.6502 / 1.7095 | 1.2463 / 1.1430 / 1.2208 |
| YSDU | 95,645 | 1.4633 | 1.2149 | 1.4724 / 1.5053 / 1.4120 | 1.2457 / 1.1976 / 1.2013 |
| RNO | 96,342 | 2.1717 | 1.1735 | 2.0114 / 2.2890 / 2.2152 | 1.2148 / 1.1860 / 1.1193 |
| KSFO (SFO) | 96,330 | 1.2449 | 1.0390 | 1.2514 / 1.2237 / 1.2595 | 1.0297 / 1.1095 / 0.9777 |
| **headline / fold-level** | | **1.4617** | **1.0498** | 1.4598 / 1.4719 / 1.4534 | 1.0585 / 1.0634 / 1.0274 |

Headline at full precision: raw GFS 1.4616990883475995, baseline 1.049777501605027. **No airport-lead where the baseline is not below raw GFS** (pooled over folds and cycle hours; 0 of 132). The six-airport mean per lead runs from 1.3606 / 0.9648 (lead 3) to 1.5223 / 1.1083 (lead 24); per cycle hour, 12z is lowest for both (1.4380 / 1.0328). Full tables in the output file. `data/processed/session97_stagec_cv_scores.csv`: 3,168 rows, SHA-256 `5604ccd16118fe772cd24a7be83b36ee62e500c78b3ed5bf55c76ed4e78d9d76`.

**F139.5 Repeatability and meta (Step 5).** `--score --airports EGLC` into a `mktemp -d` directory: its 528 rows (with the header) are byte-equal to EGLC's rows in the scores file (`diff` and `cmp`); the directory was deleted. The 2026-27 guard refuses a valid time of 2026-08-01T00:00 and allows 2026-07-31T23:00 (2 of 2). `data/processed/session97_stagec_cv.meta.txt`, SHA-256 `95223b4fbc519c5cc1811d1682e0b0e94c5976c54511dedaf58c4777671b313a`, lists the inputs, script and outputs with SHA-256, `LGB_PARAMS` as passed and the versions.

**F139.6 Readings made where the prompt is silent (for the owner to confirm or change).**
1. **The session-48 module.** As the prompt says, `LGB_PARAMS` and the G15 order are imported from `session62_reserved_confirm.py` (after its SHA-256 check), as session 81 did. That script imports the session-48 reserved-year module at load, for its own use (D70.7, F118.9). This script never imports or calls the guard itself; D89.4's "not imported here" is read that way.
2. The G15 order imported is also checked in code against D70.1's written list.
3. Boundary rows (D89.3, "in neither") are counted whatever their completeness; test rows "dropped as not complete case" are those with no observation (leads 0 to 2 are outside the files' lead range).
4. Error is `obs_tmpc` minus forecast (Step 4.2); the record computes forecast minus observation. Their absolute values are equal bit for bit, so MAEs are unaffected; the sign matters only for the mean error column.
5. A pooled MAE (per airport, per fold, per lead or per cycle hour) is the NumPy mean of the concatenated errors, in fold, cycle hour, lead, then cycle-time order. It is not rebuilt from the per-cell MAEs.
6. Training rows within a model are in ascending cycle time (G19); test rows the same.
7. On load, each table file's SHA-256 is checked against F138.4, `complete_case` is checked against the nine columns and the observation (no disagreement), `temp` is checked equal to `temperature_grib_c`, and every valid and observation time passes the 2026-27 guard.
8. "Smallest training count of any single model": where several models tie, the lowest (cycle hour, lead) is named.
9. The output file adds one table not asked for: each airport's raw GFS and baseline MAE per lead (pooled over folds and cycle hours), from which Step 4.4's last item is read.
10. Output files are written once and refused if present (SPEC 8.7 item 5). Bytecode writing was turned off for every run, so no `__pycache__` was written.

**F139.7 What this did not do.** No network. No build choice: D89.6's rule was not applied, and no setting, feature, parameter or structure was changed, tuned or selected; only D88.4's baseline was fit, with the record's settings. No model was saved, and `data/models/` was not touched. Nothing from 2026-27: no row valid after 2026-07-31T23:00 was read or scored. No non-development airport's data was read. `MLwx-stagec/` and `MLwx-pull/` unchanged (SHA-256 checked at the end). No existing script edited. Nothing installed. SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing committed and no commit message written.

---

## 2026-10-07: Session 98 decision: F139 accepted, GFS v17, and the repository restructure (owner, planning chat)

**D90. Owner decisions, planning chat (after session 97): F139 accepted,
GFS v17, the session order, and the repository restructure.** Written at
the start of session 98, before any other edit. No 2026-27 value has been
read or scored.

- **D90.1 F139 accepted.** The owner accepts F139 and all ten F139.6
  readings. D89.4 is clarified: "not imported here" means that
  `scripts/session97_stagec_cv.py` never imports or calls the session-48
  reserved-year guard itself. The record script it imports,
  `scripts/session62_reserved_confirm.py`, loads the session-48 module at
  load time for its own use, as F139.6.1 reads.
- **D90.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-07, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is still SCN 26-89 (2 October
  2026). With 30 days' notice the earliest go-live is now about 6 November
  2026.
- **D90.3 Session order.** Session 98 is a repository restructure and
  cleanup for outside readers. The first of D82.5's alternatives against
  the baseline (D89.10) moves to session 99. Nothing else in D89 changes.
  The hold rule (D73.8) is unchanged.
- **D90.4 Purpose and limits.** The public repository should read well to
  an outside reviewer without changing the work or the record. No existing
  DECISIONS or archive entry is edited. No file of the working record
  (session prompts, commit messages, saved outputs, audits) is edited. No
  script, data file or the workflow file is edited, moved or renamed. Git
  history is not rewritten. Files that move are moved byte for byte.
- **D90.5 The layout.** The root keeps `README.md`, `LICENSE`,
  `requirements.txt`, `CLAUDE.md` (Claude Code reads it from the root),
  `.gitignore`, `.github/`, `scripts/` and `data/`. `scripts/` and `data/`
  stay because the code depends on their paths. `research/` holds
  `SPEC.md`, `RESULTS.md`, `DECISIONS.md`, `archive/DECISIONS-archive.md`
  and `figures/`. `audit/` holds `STATUS.md`, `PROJECT-INSTRUCTIONS.md`,
  `sessions/` (formerly `docs/`) and `outputs/` (formerly `notes/`).
  `audit/session98_path_map.csv` lists every moved tracked file's old path,
  new path and SHA-256. Each of `research/`, `audit/`, `scripts/` and
  `data/` gets a short `README.md` that explains the folder.
- **D90.6 Citations.** Entries written before session 98 cite the old
  paths (for example `notes/session-85-output.txt`, `docs/session-97.md`,
  or a bare `STATUS.md`). They are not edited; they resolve through D90.5's
  path map. From session 98 on, new text cites the new paths. The live
  files `CLAUDE.md`, `PROJECT-INSTRUCTIONS.md`, `SPEC.md` and `STATUS.md`
  have their path references updated in session 98, with no other change
  except D90.8.
- **D90.7 The session invocation from session 99:** "Read CLAUDE.md, then
  research/SPEC.md, audit/STATUS.md, and research/DECISIONS.md in full.
  Then carry out the session defined in audit/sessions/session-NN.md,
  staying strictly within its scope. Stop at the end-of-session steps and
  wait for my review. Do not commit anything."
- **D90.8 SPEC 6.** Stage C's bullet points to D88 for the development
  table and baseline and to D89 for the rules for its build choices.
- **D90.9 libomp.** The owner installed Homebrew (version 7.0.8) and found
  that lightgbm 4.7.0 imports in a fresh interpreter with no loader shim
  (owner's terminal, 2026-10-07). Session 98 records which libomp library
  is loaded and gates it: with the shim bypassed, `session97_stagec_cv.py
  --gate` must reproduce F109's six values exactly, and its EGLC `--score`
  must be byte-equal to EGLC's committed rows. If both pass, scripts from
  session 99 on may import lightgbm directly, without the shim. Scripts
  that import a record script still run that script's shim, which is
  harmless. scikit-learn stays pinned, because the frozen scripts' shim
  uses its copy of libomp. If Homebrew's libomp is absent or the gate fails,
  the shim stays the rule and the README and `requirements.txt` only
  document it. The session installs nothing.
- **D90.10 Reader-facing files.** `README.md` is rewritten for outside
  readers. Figures in `research/figures/` are drawn by
  `scripts/session98_figures.py` (Python standard library only) from
  committed files only. Every number in a README or figure is copied from
  the record and cited. No build-choice score is quoted (SPEC 2.5). The
  README ends with the author's name, Zachary Adams.
- **D90.11 Writing rule.** No em-dash in any new text (D76.6), including
  the README files, figure text, D90, F140, STATUS and commit messages.
- **D90.12 Later work, not this session.** A `tests/` folder with a real
  test suite (the leakage guards and a reproduction of the headline from
  committed data) after stage C's first D82.5 comparison; a `src/` package
  only at stage G. Neither folder is created empty.

---

## 2026-10-07: Session 98b decision: session 98's stop accepted, and the restructure replaced (owner, planning chat)

**D91. Owner decisions, planning chat (after session 98's stop): the stop
and its readings accepted, the restructure replaced, README section 8, and
session 98b.** Written at the start of session 98b, before any other edit.
No 2026-27 value has been read or scored.

- **D91.1 Session 98's stop accepted.** Its reference gate worked as
  intended. The planning chat had not checked the scripts' own path
  constants (for example `ROOT / "SPEC.md"` and `ROOT / "notes"`) before
  proposing D90.5. The owner accepts session 98's five readings
  (`notes/session-98-output.txt`).
- **D91.2 What stays at the root, and why.** `SPEC.md`, `DECISIONS.md`,
  `DECISIONS-archive.md` and `notes/` stay where they are. Scripts read or
  write them there, including stage B's 2026-27 scripts, which must run
  unchanged (D80.1, F129.6), and the frozen `session39_sealed_test.py` and
  `session62_reserved_confirm.py` (D62.3(a)). No copies or links are left
  at old paths.
- **D91.3 The layout (replaces D90.5).** One move:
  `PROJECT-INSTRUCTIONS.md` to `docs/PROJECT-INSTRUCTIONS.md`. No code
  reads it (session 98, Step 3). Every other file and folder stays where it
  is. New: a `README.md` in `scripts/`, `data/`, `docs/` and `notes/` (new
  files only; no existing file there is edited), and a `figures/` folder at
  the root for the README's figures, drawn by
  `scripts/session98b_figures.py`. The root README is rewritten.
- **D91.4 What D91 replaces in D90.** D90.5 (the layout) is replaced by
  D91.3. D90.6 now applies to one file only: entries written before
  session 98b that place `PROJECT-INSTRUCTIONS.md` at the root resolve to
  `docs/PROJECT-INSTRUCTIONS.md`. D90.7 is withdrawn: the invocation keeps
  its current form, written without a dash: "Read CLAUDE.md, then SPEC.md,
  STATUS.md, and DECISIONS.md in full. Then carry out the session defined
  in docs/session-NN.md, staying strictly within its scope. Stop at the
  end-of-session steps and wait for my review. Do not commit anything."
  In D90.10, the figures go in `figures/` and the script is
  `scripts/session98b_figures.py`. D90.1 to D90.4, D90.8, D90.9, D90.10's
  other rules, D90.11 and D90.12 stand.
- **D91.5 README section 8 (data credits) is updated, not carried over
  word for word.** It adds what was committed or published after it was
  written: the NBM values (F127.3; read from NOAA's NBM archive on AWS,
  bucket `noaa-nbm-grib2-pds`), the raw GFS MOS (MAV) responses from the
  IEM archive (F127.3), the IEM observations for 45 further airports
  (F132.4), and stage C's point values published as Release files (F137,
  derived from NOAA GFS). NBM's terms (planning-chat check of
  https://registry.opendata.aws/noaa-nbm, 2026-10-07, not checked by this
  session): NOAA requests attribution for unaltered NOAA data; it is not
  permitted to state or imply endorsement by or affiliation with NOAA; and
  modified NOAA data may not be presented as original, unaltered NOAA data.
  NBM and NWS MOS leave the "probed only, no data committed" list.
- **D91.6 The personal path in D84.3** (session 98, Step 2.4) is accepted
  as it is. The record is not edited (D90.4). It shows only the owner's
  user name, which the saved outputs already show (F126.2).
- **D91.7 GFS v17.** Unchanged since D90.2 (same day).
- **D91.8 Session 98b** records D91, makes D91.3's move, carries out D90.8
  (the SPEC 6 pointer) and D90.9 (the libomp gate), draws the figures and
  writes the README files under D90.10, D90.11 and D91.5. F140 records
  sessions 98 and 98b.

---

## 2026-10-07: Session 98b finding: the planning guide moved, the libomp gate, the figures and the README files

**F140. Sessions 98 and 98b. No model experiment was run and no build choice was made. Session 98b recorded D91, moved `PROJECT-INSTRUCTIONS.md` into `docs/` byte for byte, made the D90.8 pointer edit in SPEC 6, passed the libomp gate with the loader shim bypassed (F109's six values 6 of 6, and EGLC's scores byte-equal), drew two figures, and wrote the root README and a README in `scripts/`, `data/`, `docs/` and `notes/`. Figure script: `scripts/session98b_figures.py` (new; SHA-256 `8afc584abe5b0b538a703e2911d2fc8a14fec8889a30504aa85d4a6d42a47305`). Full real output: `notes/session-98b-output.txt`. Run 2026-10-07. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

**F140.1 Session 98.** It recorded D90, ran its read-only audit, and stopped at Step 3, the reference gate, because scripts read `SPEC.md`, `DECISIONS.md` and files under `notes/` at their current paths. Nothing was moved. Full output: `notes/session-98-output.txt`. No F entry was written then.

**F140.2 Step 0.** `git status --porcelain` showed only `?? docs/session-98b.md`. The last entries were D90 and F139; no D91 or F140 entry existed in either DECISIONS file (the one text match was D90.11 naming F140). SHA-256 equal to session 98's Step 0.3: `scripts/session97_stagec_cv.py` `987ab6ba...1f91`, `scripts/session62_reserved_confirm.py` `9f8af9af...80b4`, `data/processed/session63_reserved_confirm_grid.csv` `0138ba03...4ed3`, `data/processed/session97_stagec_cv_scores.csv` `5604ccd1...9d76`, `.github/workflows/stagec-grib-pull.yml` `804b6d35...02a6`. None of the seven new paths existed. Read: CLAUDE.md, SPEC, STATUS, DECISIONS, README.md, RESULTS.md, PROJECT-INSTRUCTIONS.md, `requirements.txt`, `.gitignore`, `notes/session-98-output.txt`, and the archived F92, F94, D64, D65, D70.6 and F112 to F119 headings where the README files cite them.

**F140.3 Step 1.** D91 was copied with `sed` from `docs/session-98b.md` lines 84 to 139 (between the markers at 83 and 140) into DECISIONS.md lines 3950 to 4005 (separator at 3948), and checked byte-equal with `diff` and `cmp`, before any other edit. Em-dashes in D91: 0.

**F140.4 Step 2.** `grep -rnI "PROJECT-INSTRUCTIONS"` over `scripts/`, `.github/`, `requirements.txt` and `.gitignore`: no hit, as session 98 found. `README`: one hit, `requirements.txt` line 37, a comment, class (b). The quoted component `"figures"` (either quote): no hit. The bare word "figures" appears only in printed text and comments (for example "published figures"), class (b). No (a) hit, so the move went ahead.

**F140.5 Step 3.** `PROJECT-INSTRUCTIONS.md` SHA-256 `bb4166e925f6638a21c74d75ab5dd1edae34a03c1db378bd9676a5aa4f0cb196` before; moved with plain `mv`; `docs/PROJECT-INSTRUCTIONS.md` has the same SHA-256; nothing left at the old path; `git status` shows ` D PROJECT-INSTRUCTIONS.md` and `?? docs/PROJECT-INSTRUCTIONS.md`.

**F140.6 Step 4.** Three lines changed, before and after in the output file. CLAUDE.md line 50: "(repo root)" became "(in `docs/`)"; no other CLAUDE.md line places the file at the root. `docs/PROJECT-INSTRUCTIONS.md` line 50: "Kept in the repo root" became "Kept in docs/"; no other line places it at the root. SPEC 6, stage C bullet: "Its next steps are in DECISIONS D88." became "Its development table and baseline are set in DECISIONS D88, and the rules for its build choices in DECISIONS D89." The next sentence was rewrapped, not changed.

**F140.7 Step 5: libomp (D90.9). The gate passed and the byte check passed.**
- `brew` was not on the session shell's PATH. Homebrew is at `/opt/homebrew/bin/brew`: `Homebrew 7.0.8`; `brew list --versions libomp`: `libomp 23.1.3`.
- LightGBM's library: `.venv/lib/python3.12/site-packages/lightgbm/lib/lib_lightgbm.dylib`. `otool -L` lists `@rpath/libomp.dylib` (compatibility version 5.0.0); its rpaths are `/opt/homebrew/opt/libomp/lib` and `/opt/local/lib/libomp`.
- Without the shim (`env -u DYLD_LIBRARY_PATH MLWX_LIBOMP_PATH_SET=1`, `DYLD_PRINT_LIBRARIES=1`), `import lightgbm` printed `4.7.0` and loaded two copies of libomp: `/opt/homebrew/Cellar/libomp/23.1.3/lib/libomp.dylib` first, then `.venv/.../sklearn/.dylibs/libomp.dylib` (scikit-learn modules were loaded by the import).
- The gate, shim bypassed (`session97_stagec_cv.py --gate`, 2026-10-07T11:08:55Z, 4.3 s): **6 of 6 equal, exact equality**: EGLC `B+D,L,R,T` 1.0007550363323212 and raw GFS 1.23621978021978; LFPG 1.2368626165917669 and 1.4091397260273972; DSM 1.4122847644111458 and 1.7043452054794521. "GATE PASSED".
- EGLC `--score`, shim bypassed, into a `mktemp -d` folder (264 fits, 19.8 s): its file (529 lines: the header and 528 rows; 36,888 bytes) is byte-equal to the header plus EGLC's rows of `data/processed/session97_stagec_cv_scores.csv` (`diff` and `cmp` silent; both SHA-256 `38e8295dc422c429c14d0ecb09692032855356deee5ff4c5d71cdfbb1aa0cb65`). The folder was deleted. No score was printed or read.
- `requirements.txt`: the OpenMP block was rewritten as Step 5.6 says, and the eccodes sentence changed as asked (one comment line rewrapped). Its 29 non-comment lines are byte-identical before and after (`diff` silent).

**F140.8 Step 6: figures. Both made.**
- `figures/headline_mae.svg` (5,927 bytes, SHA-256 `2bb18ab1a7abfae99ed8c2e5c4dde94e5533e03721250f685e2d3dc3b0111d5c`): grouped bars, raw GFS and `B+D,L,R,T` MAE at EGLC, LFPG, DSM, YSDU, RNO from the grid file (`raw_mae`, `final_mae`), after its SHA-256 check. The ten printed values equal the grid file's at 4 decimals and the README table's: 1.2362, 1.0008; 1.4091, 1.2369; 1.7043, 1.4123; 1.4897, 1.2643; 1.6135, 1.2742.
- `figures/skill_intervals.svg` (7,764 bytes, SHA-256 `4075f6c66867606b45caa3e7acc06df8ac7ea9fa0261b4222c01a2fe1ee40982`): made, because every value can be read by the script from a committed file and equals F125.6 at its precision. No data file holds F125's intervals, so the source is the summary table of `notes/session-83-output.txt`, the output F125 cites (reading 4). All ten (skill, lower, upper) triples equal F125.6.
- Checks: the script ran once; `figures/` was copied to a temporary folder, the originals deleted, the script run again; both SVGs `cmp`-equal to their copies; the copy deleted. A third run into the existing files stopped: "figures/headline_mae.svg exists; figures are written once". Em-dashes in both SVGs and the script: 0.

**F140.9 Step 7: the README files.** Written new: `README.md` (full rewrite, 10 sections), `scripts/README.md`, `data/README.md`, `docs/README.md`, `notes/README.md`. Every number is copied from SPEC, DECISIONS or a committed file and cited. No F139 score appears in any README or figure.

**F140.10 Step 8: final checks.**
- Relative links in the five README files: 35 checked (one with an anchor), 0 failures.
- U+2014: 0 in every new file; 0 in the added lines of CLAUDE.md, SPEC.md, DECISIONS.md, requirements.txt, README.md and `docs/PROJECT-INSTRUCTIONS.md` (against HEAD's root copy).
- `git diff --stat` (before F140 and STATUS): CLAUDE.md 2, DECISIONS.md 59, PROJECT-INSTRUCTIONS.md 204 (deleted), README.md 374, SPEC.md 7, requirements.txt 34; 6 files, 326 insertions, 354 deletions. No tracked file under `scripts/`, `data/`, `docs/`, `notes/` or `.github/` changed.
- The five Step 0 files: SHA-256 unchanged. `MLwx-stagec/`: the six table files' SHA-256 equal F138.4. `MLwx-pull/` not touched.
- No new `__pycache__`: every run used `-B`; the existing ignored `scripts/__pycache__` (last changed 2026-10-03) holds no file newer than the session prompt.
- Root listing (`ls -A`): .DS_Store, .claude, .git, .github, .gitignore, .venv, CLAUDE.md, DECISIONS-archive.md, DECISIONS.md, LICENSE, README.md, RESULTS.md, SPEC.md, STATUS.md, data, docs, figures, notes, requirements.txt, scripts.

**F140.11 Readings made where the prompt is silent (for the owner to confirm).**
1. `brew` was run by its full path, `/opt/homebrew/bin/brew`, because the session shell's PATH lacks `/opt/homebrew/bin`. libomp was listed, so items 2 to 5 ran.
2. **Two libomp copies load without the shim** (F140.7): Homebrew's through LightGBM's rpath, and scikit-learn's because the import loads scikit-learn. The gate and the byte check passed with both loaded. Recorded, not acted on. `requirements.txt` says the workaround is harmless when Homebrew's libomp is present, as D90.9 and the prompt word it.
3. The EGLC file is 529 lines, the header plus 528 rows. F139.5 says "528 rows (with the header)"; the script's own line says "528 rows". Byte-equal either way.
4. **No SHA-256 of `notes/session-83-output.txt` is in the record.** The figure script pins the committed file's value, `d87afdac94582fb598b97518a0b8004575bb140892f386daf1c934cc1c50fb65` (checked equal to HEAD's copy). The grid file's value `0138ba03...4ed3` is the one F139.1 notes is recorded in `notes/session-85-output.txt`. F109's 4-decimal MAEs and F125.6's values are copied into the script only as check constants.
5. **The figure script changed twice after its first run.** (a) After viewing a preview, the skill figure was narrowed from 880 to 760 pixels so it reads on narrow screens and matches the headline figure; the SVGs from the first runs (untracked, this session's own output) were deleted and redrawn. (b) The tool that wrote the script turned the escape for U+2014 (backslash, u, 2014) in its own em-dash check into the literal character; it is now `chr(0x2014)`. Step 6.3's checks, reported above, were run on the final script. No drawn value changed.
6. **The prompt's "each month checked before it was published" does not hold for 2022-01**, which was published before the verify step existed (D84.3, D84.4) and checked afterwards (F134). The README says so.
7. "A richer method ... passed on a fresh look": F94's look was on the same sealed year the minimal method used. The README says the richer method got "its own single look".
8. The benchmark bullet adds F127.6's count (the model's MAE lower at 1 of 4 airport-looks) so the word MIXED has its meaning beside it.
9. The frozen list in `scripts/README.md` adds `session77_ksfo_looks.py` (D70.6) and the three stage B scripts: D80.1 names the two session 87 scripts, and D91.2 names "stage B's 2026-27 scripts", read as including `session86_forward_build.py`.
10. README section 9: the IEM entry gains one sentence on the 45 further airports; the stage C Release values and NBM are new entries; MAV is a new entry whose own terms "were not fetched" (none are in the record); NBM and NWS MOS leave the "probed only" list (D91.5).
11. The root README keeps the old disclaimer and adds one line on how to read Dxx, Fxx and "SPEC 8". It has 10 sections; the skill figure sits after the caveats. The Mermaid diagram was not drawn locally (no renderer is installed); GitHub draws it.
12. `data/README.md` names the two candidate-station samples (YSCB, session 19; BZN, session 25) found among the IEM files.

**F140.12 What this did not do.** No model experiment was run and no build choice was made. No F139 score was read, printed or quoted. Nothing was installed and no network call was made. No existing DECISIONS or archive entry was edited (D91 and F140 appended only). No script, data file or the workflow file was edited, moved or renamed; no existing file in `docs/` or `notes/` was edited except `docs/PROJECT-INSTRUCTIONS.md` after its move, as Step 4 says. `MLwx-stagec/` was only read, by the gate; `MLwx-pull/` was not touched. RESULTS.md, STATUS.md (until the end-of-session overwrite) and `.gitignore` were not edited. The git index was not touched. Nothing was committed and no commit message was written.

**F140.13 Corrections after the owner's review** (`docs/session-98b-correction.md`). Three changes, each reported before and after in `notes/session-98b-output.txt` under "CORRECTION AFTER REVIEW".
- **The skill figure's title.** In `scripts/session98b_figures.py` the title "Selected-features method: skill with 95% intervals, reserved year 2024-25 (F125.6)" (81 characters, cut off at 760 pixels) became "Skill with 95% intervals, reserved year 2024-25 (F125.6)". Nothing else in the script changed; it computes no text width. Both SVGs were deleted and the script run once: `figures/headline_mae.svg` is again `2bb18ab1a7abfae99ed8c2e5c4dde94e5533e03721250f685e2d3dc3b0111d5c`, equal to before. Step 6.3's repeat check (copy, delete, run again, `cmp`): both SVGs equal. **New SHA-256, replacing the values given earlier in F140:** script `49a31e717950a6dfbf3e6c0d5b7aa6858ee7694b40fdff696d277782c32d5ddf`; `figures/skill_intervals.svg` `bac12c278d6af65e149c8cabb20b3dc8bd40948dd44a158e1a521e6384ab4bfe` (7,712 bytes).
- **"One look per year" in README.md.** The rule is one look per method at each held-out year (the sealed year 2025-26 was looked at once by the minimal method and once by the richer method, F94). Section 1 now says "Each claim came from a single look at held-out data"; section 3's first bullet and section 4's "Discipline" bullet now say "each method looks at each held-out year only once (SPEC 2.4, 5.0)". Other README lines found and left unchanged: README.md line 33 ("Each airport was judged once on the reserved year"), line 169 ("held-out data used once"), and `scripts/README.md` lines 43, 49 and 56 ("one-look sealed test", "its one look", "the one look at the reserved year"); each describes one method's look.
- **`requirements.txt`.** "scikit-learn is NOT imported by any script." became "No script imports scikit-learn directly, though importing lightgbm loads parts of it (DECISIONS F140.7)." Comment text only; the non-comment lines are byte-identical (`diff` silent).
