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

## 2026-09-12 -- Session 42 finding: D48's one authorised look, taken. The
5-feature GRIB recipe PASSES the frozen bar at all five airports, exactly
matching the D48.12 pre-registration.

**F94. This is the single authorised look at the sealed test year for the
5-feature GRIB recipe (D48.13). It stands exactly as reported below -- no
re-tuning, no re-run, no retroactive adjustment.** `scripts/
session39_sealed_test.py` was confirmed unchanged since the F93 commit
(`git diff HEAD` empty against it) and run exactly as-is, once, with no
argument, against session 40's already-pulled `grib_features_sealed_
window.csv` and the existing sealed-year IEM chunks -- no new data pulled.
It completed cleanly: every self-guard (training-row reconciliation,
D48.7; the corrected sealed-row ceiling, D48.8/F93; the in-window date
assertions) passed at every airport, no guard tripped, no unforeseen
error. Full real output: `notes/session40-sealed-test-output.txt` (the
file name is the frozen script's own, unchanged since session 39 -- this
is session 42's real run, replacing session 40's earlier partial output up
to its guard-trip). Summary table: `data/processed/
session40_sealed_test_summary.csv`.

**Task 1 result -- sealed-year MAE, four rungs, all five airports:**

```
airport  Raw GFS (GRIB)  Persistence  3-feature  5-feature  n (test_rows)
EGLC          1.254          2.096       1.037       1.000        364
LFPG          1.382          2.300       1.177       1.156        364
DSM           1.733          4.003       1.694       1.636        365
YSDU          1.317          2.669       1.283       1.179        356
RNO           1.512          2.490       1.455       1.346        365
```

**D48.11 bar verdict -- 5-feature vs raw GFS (GRIB) and persistence, per
airport:**

```
airport  5f vs raw GFS         5f vs persistence      VERDICT
EGLC     1.000 vs 1.254 (+20.2%)  1.000 vs 2.096 (+52.3%)   PASS
LFPG     1.156 vs 1.382 (+16.4%)  1.156 vs 2.300 (+49.7%)   PASS
DSM      1.636 vs 1.733 (+5.6%)   1.636 vs 4.003 (+59.1%)   PASS
YSDU     1.179 vs 1.317 (+10.5%)  1.179 vs 2.669 (+55.8%)   PASS
RNO      1.346 vs 1.512 (+11.0%)  1.346 vs 2.490 (+45.9%)   PASS
```

**5 of 5 airports PASS the frozen bar (SPEC 5.3, D22, D48.11).** This is
the project's first result where every opened airport passes under one
recipe -- including LFPG (which never passed under the existing 3-feature/
Open-Meteo recipe's own rehearsal read at the same window, F86/F87's
5-of-5 read on the diagnostic notwithstanding) and RNO (whose EXISTING
sealed test, F82, failed).

**5-vs-3-feature comparison (reported alongside the bar, not part of it,
D48.10/D48.11) -- 5-feature beats 3-feature at all five airports:**

```
airport  3-feature  5-feature  5-vs-3 skill
EGLC       1.037      1.000       +3.5%
LFPG       1.177      1.156       +1.8%
DSM        1.694      1.636       +3.4%
YSDU       1.283      1.179       +8.2%
RNO        1.455      1.346       +7.5%
```

**Task 2 -- scoring-consistency check, confirmed with one genuine, minor,
verdict-irrelevant finding.** The frozen script's own `passes_persist =
f5_mae < persist_mae` compares `f5_mae` (computed over all of
`test_rows`) against `persist_mae` (computed over the narrower
`common_persist` subset -- days with a usable previous-day observation,
SPEC 2.1d). Where the sealed year has zero days missing a previous-day
observation (DSM, RNO: `no_prev=0`) the two sets are identical and no
question arises. Where it does not (EGLC 1 day, LFPG 1 day, YSDU 9 days)
this is a real day-set mismatch against the shared-day-set convention
F93 documented every prior airport's own sealed test as using for every
rung (raw, persistence, ML-corrected) together. **A read-only diagnostic**
(`scripts/session42_scoring_check.py`, importing `session39_sealed_test.py`
unmodified as a library -- same pattern as session 41's `session41_verify.py`
-- reusing its own fitted models and predictions, fitting nothing new)
recomputed raw/3-feature/5-feature MAE restricted to exactly the
`common_persist` day set, and compared the two bases directly. Full output:
`notes/session-42-scoring-check-output.txt`.

```
station  n(full)  n(common)  no_prev  5f MAE(full)  5f MAE(common)  persist MAE  frozen verdict  common-basis verdict
EGLC        364        363        1       1.000          1.001         2.096          PASS              PASS
LFPG        364        363        1       1.156          1.157         2.300          PASS              PASS
DSM         365        365        0       1.636          1.636         4.003          PASS              PASS
YSDU        356        347        9       1.179          1.165         2.669          PASS              PASS
RNO         365        365        0       1.346          1.346         2.490          PASS              PASS
```

**All five airports give the identical PASS verdict under both day
bases**, against both raw GFS and persistence (the raw-GFS comparison was
never at risk -- raw, 3-feature and 5-feature are all computed on the same
`test_rows` set already, D48.10). The largest MAE shift from restricting
to the common-persist day set is YSDU's, 1.179 -> 1.165 (a 0.014 degC
change on 9 of 356 days), nowhere close to closing a 55.8%-skill margin
against persistence. **Verdict: the mismatch is real and is a genuine,
reportable deviation from the shared-day-set convention F93 named, but it
is verdict-irrelevant at every airport this run** -- reported straight,
per the session prompt's own instruction, rather than silently accepted or
used to withhold the result. It is flagged here for whoever eventually
folds this recipe into SPEC/RESULTS (a later, separate consolidation
session, D48.11), so the frozen script's own day-basis choice is on record
rather than rediscovered.

**Task 3 -- comparison against the D48.12 pre-registration: full,
exact match, no divergence.** D48.12 (recorded before any sealed data was
seen, from F91) predicted: 5-feature beats both raw GFS and persistence at
all five airports; 5-feature beats 3-feature at all five airports; LFPG
passes; RNO passes (a reversal of its own existing sealed-test failure
under the different, existing 3-feature/Open-Meteo recipe, F82, not an
erasure of it, D48.13). **Every one of those four predictions came true,
at every airport, with no exception and no close call** -- the narrowest
raw-GFS margin (DSM, +5.6%) and the narrowest persistence margin (RNO,
+45.9%) are both comfortably positive, and the narrowest 5-vs-3 margin
(LFPG, +1.8%) is still a genuine, if modest, win. **This is the first
pre-registered expectation in the project's history to be confirmed
without exception at every airport it named** (contrast D44.12's Reno
prediction, which named the existing recipe's failure mode in advance and
was also confirmed -- but as a failure, not a clean sweep of passes).

**What this does and does not mean for the project's existing results,
stated per D48.13.** This is a new, separate test of a different recipe
(GRIB source, richer features) on the same sealed test year. It does
**not** re-open, re-test, or overwrite any airport's existing sealed-test
verdict under the existing 3-feature/Open-Meteo recipe -- EGLC F16, LFPG
F30, DSM F47, YSDU F64 and RNO F82 all stand exactly as reported. At EGLC,
DSM and YSDU the project now has two independently-tested, independently-
passing recipes. At LFPG and RNO, the richer GRIB recipe passes where the
existing recipe's own sealed test did not (RNO, F82) or where the honest
reading of the existing recipe's cross-airport comparison never singled it
out as a clean win (LFPG's F30 pass stands on its own terms; the richer
recipe's win here is a separate, additional result, not a correction to
F30). Whether/how to fold the 5-feature GRIB recipe into `SPEC.md`/
`RESULTS.md` as the project's primary method is a later, separate
consolidation session's decision, not made here.

**What this session did not do, on purpose.** Did not modify
`scripts/session39_sealed_test.py` in any way (confirmed by `git diff HEAD`
before and after running it -- empty). Did not re-run, re-tune, or adjust
anything after seeing the results -- the numbers above are the single
authorised look and stand as reported (D48.13). Did not pull any new raw
or processed data -- reused session 40's `grib_features_sealed_window.csv`
and the existing sealed-year IEM chunks, all read-only. Did not touch any
date outside 2025-08-01..2026-07-31 for the sealed side, or before
2021-03-24 for the training side -- enforced by the frozen script's own
assertions, which raised on none of them. Did not modify `SPEC.md` or
`RESULTS.md` -- folding the method in is a separate consolidation session.
Did not re-open, re-score, or adjust any existing airport's sealed-test
verdict (EGLC F16, LFPG F30, DSM F47, YSDU F64, RNO F82 all untouched).
Nothing was committed. Scripts: `scripts/session39_sealed_test.py` (run
unmodified), `scripts/session42_scoring_check.py` (new, read-only
diagnostic). Full real output: `notes/session40-sealed-test-output.txt`,
`notes/session-42-scoring-check-output.txt`. Summary table: `data/
processed/session40_sealed_test_summary.csv`.

---

## 2026-09-12 — Session 43 decision: the proven 5-feature GRIB method is
folded into SPEC.md as a new section 7, documentation only

**D49. `SPEC.md` now describes two methods: the original minimal method
(sections 1–6, unchanged) and the richer 5-feature GRIB method (new section
7), proven by F94. This is a documentation-only consolidation — no code,
model, data, or figure was touched, and no DECISIONS finding or verdict was
changed.** Every number folded into section 7 is copied from, and cited to,
its DECISIONS source (D48, F85–F94) — nothing was recomputed.

**What changed in `SPEC.md`, in full (see the session's own diff for exact
wording):**
- **New `## 7. The richer-features GRIB method`**, placed after section 6
  (not inserted mid-document as a "4A") specifically so sections 5 and 6 —
  cited by number throughout this file and `STATUS.md` — never need
  renumbering. It covers: motivation (Reno's near-constant-bias shape,
  F79/F82); what differs from the minimal method (features, GRIB source and
  lead convention, the elevation/lapse-rate correction, the v16-only
  training window, the unchanged model settings — D48.2–D48.7); validation
  done before the sealed test (F89–F91); the lock and sealed test (D48,
  F92–F94); the sealed-year results table (F94, 5-feature MAE and its skill
  vs raw GFS/persistence/3-feature at all five airports); and a closing
  paragraph stating plainly what this does and does not mean (D48.13) —
  including that raw GFS (GRIB) and raw GFS (Open-Meteo) are not the same
  series, so section 7's margins are not directly comparable, airport for
  airport, to section 5.0's.
- **§1 airports list** — Reno's bullet reworded from "failed" to "failed the
  minimal method (F82); passes the richer 5-feature GRIB method (F94) — see
  section 7."
- **§2.1b (leakage rule)** — one sentence added noting the GRIB archive is a
  genuine archived past forecast at a fixed lead (F89), so it satisfies the
  rule's intent by a different route than Open-Meteo's Previous Runs API;
  the rule itself, and what the minimal method uses, is unchanged.
- **§3.2 (forecast source)** — one sentence added pointing out this section
  describes the minimal method's source only, with section 7 having its
  own.
- **§5.0 (results)** — one paragraph added after the existing Reno
  discussion, pointing to section 7's own results table; the existing
  results table and its wording are untouched.
- **§6 (Reno / stage-2 bullet)** — one sentence added noting the richer
  method later passed at Reno (F94, section 7); the existing failure
  record (F82) is untouched.

**The results-table placement choice, decided this session.** The
richer-method's sealed-year results table (F94's own numbers) was placed
directly inside the new section 7, not deferred to `RESULTS.md`. Reasoning:
the numbers are already fully cited to a single DECISIONS finding (F94), so
placing them in section 7 keeps that section self-contained and gives
`STATUS.md`/future sessions one place to point at for the method's own
proven result. `RESULTS.md`'s own job (session 44) is the narrative and
caveat treatment — in particular, the raw-GFS-margin non-comparability
between the GRIB and Open-Meteo baselines — not a restatement of the raw
numbers.

**What this session deliberately did not do.** Did not touch `RESULTS.md`
(session 44's job). Did not run the archive pass (session 44's job, once
both `SPEC.md` and `RESULTS.md` carry the headlines). Did not change any
DECISIONS finding, verdict, or the frozen bar. Did not restructure or
reword any part of sections 1–6 beyond the five pointed edits listed above.
Did not recompute any figure — every number in section 7 is copied from
D48/F85–F94. Nothing was committed.

**Two corrections made to section 7 in a same-day follow-up, both
documentation only, no code or data, nothing committed:**
1. **§7.5's independently-passing-methods sentence was incomplete.** It
   originally read "At EGLC, DSM and YSDU the project now has two
   independently-tested, independently-passing methods," omitting LFPG.
   LFPG passes the minimal method (F30) and the richer method (F94), the
   same as EGLC, DSM and YSDU — the omission was a drafting slip, not a new
   finding. Corrected to name all four, with an explicit closing clause:
   every airport that passed the minimal method also passes the richer
   one; only Reno has just one passing method.
2. **§7.2's elevation-correction bullet could be read as contradicting
   SPEC 3.4's own grid-elevation table.** SPEC 3.4 records Reno's
   Open-Meteo grid point as 1 m from the airport's own elevation (the
   established `gfs_global` point this whole project already uses); §7.2
   separately states a 275 m gap at Reno for the richer method's own GRIB
   grid. Both figures are correct — they describe two different grids
   (Open-Meteo's own downscaled point vs. the raw 0.25° GFS GRIB cell,
   DECISIONS F89's Task 5 finding), not two conflicting measurements of the
   same one. Added one clarifying clause to §7.2 naming this explicitly, so
   a reader comparing the two sections does not read them as inconsistent.

Neither correction changes any number, verdict, or finding — both are
clarifications of exactly what section 7 already meant.

---

## 2026-09-12 — Session 44 finding: RESULTS.md rewritten to cover both
methods, documentation only

**F95. `RESULTS.md` is rewritten so it tells the whole story: the minimal
method (sections 2–4, unchanged in substance — four passes, Reno fails) and
the proven richer 5-feature GRIB method (new section 5, "act two" — five
passes, Reno passes). This is a documentation-only consolidation, mirroring
session 43's own SPEC fold-in (D49) one level down. No code, model, data,
or figure was touched, and no DECISIONS finding or verdict was changed.
Every number in the rewrite was checked against its DECISIONS/SPEC source
before being written down.**

**What changed in `RESULTS.md`, in full.** The intro (section 1) was
re-dated to session 44 and now states the project has two proven methods.
Sections 2–4 (the minimal method's own method description, results table,
and six findings) are left substantially intact — three forward pointers
were added (the intro to section 2, a note under the section-3 results
table, and a closing sentence on finding 4) so a reader lands on section 5
at the point where the minimal method's own Reno ceiling is described,
without any finding's own wording being rewritten. A new
**section 5, "Act two: the richer-features GRIB method"**, covers: what
differs from the minimal method (D48.2–D48.7); pre-sealed-test validation
(F89–F91); the lock and sealed test (D48, F92–F94) with the F94 results
table in full (5-feature MAE, raw-GFS-GRIB MAE, persistence MAE, 3-feature
MAE, and all three skill margins, at all five airports); **the honest Reno
decomposition** (section 5.4) — leading with the 5-vs-3 margin (+7.5%), not
the vs-raw-GFS margin (+11.0%), naming plainly that the GRIB raw-GFS
baseline at Reno (1.512) is measurably weaker than the Open-Meteo baseline
the minimal method faced (1.414, F82), and showing the pass is robust to
that difference (a recomputed ~+4.8% margin against an Open-Meteo-quality
baseline) rather than an artifact of it; **the LFPG window story** (section
5.5) — LFPG failed the richer features on the 1.5-year window (F86 −7.7%
3-feature / F87 −2.1% 5-feature) but passes on the full 4.4-year window and
the sealed test (F91, F94), naming the short window, not the features, as
the binding constraint that was fixed; and a closing synthesis (section
5.6) on honest magnitude (5-vs-3 ranges +1.8% to +8.2%) and the
non-comparability of the two methods' raw-GFS baselines (SPEC 7.5). Section
6 (formerly section 5, "Limitations and open directions") was updated: the
"richer features at Reno" parked item is marked done, with what it showed
and its honest caveat; the single-shared-test-year limitation is restated
to cover both methods; a new bullet on cross-method margin comparability
was added; the parked-directions list had the now-completed richer-features
item removed. The closing footer was re-dated and now cites this entry
(F95).

**What this session deliberately did not do.** Did not touch `SPEC.md`.
Did not alter any minimal-method verdict, figure, or finding — every number
in sections 2–4 matches the pre-session file exactly. Did not recompute
anything — every number in the new section 5 is copied from and cited to
D48/F85–F94, and the two derived percentages stated explicitly as
recomputed-for-context (the ~+4.8% Reno figure, `1 − 1.346/1.414`) are
computed only from numbers already on record, shown with their arithmetic
so they can be checked. Did not run the archive pass (session 45's job,
per this session's own prompt). Nothing was committed.

---

## 2026-09-12 — Session 45 decision: the GRIB-build sub-project's evidence
base is archived; a RESULTS.md wording fix

**D50. Documentation only. Two tasks: a small phrasing fix in `RESULTS.md`
section 5.5, and the archive pass that closes out the GRIB-build
sub-project (docs/session-36.md through docs/session-44.md). No code,
model, data, or figure was touched.**

**Task 1 — RESULTS.md §5.5 fix.** The sentence "3-feature −7.7%, 5-feature
−2.1%, on the scout and the follow-up CV respectively (DECISIONS F86, F87)"
mis-paired the two figures with their sources: both −7.7% (3-feature) and
−2.1% (5-feature) are the follow-up CV's own LFPG numbers (F87); the scout
(F86) gives LFPG a different pair (3-feature −25.7%, 5-feature −13.5%).
Rather than retype four figures inline, the sentence was reworded to the
neutral form that avoids the mis-pairing entirely: "both models stayed
negative across the scout and the follow-up CV (DECISIONS F86, F87)." No
figure anywhere else in `RESULTS.md` was touched.

**Task 2 — the archive pass.** Applied the D46 criterion (an entry is a
MOVE candidate once its conclusion is settled and no live open question or
`STATUS.md`'s own "Next" section needs its specific wording, only its
headline) to every build-era entry, session 31 onward.

*MOVE (headlines already carried in `SPEC.md` §7 / `RESULTS.md` §5):*
**F85, F86, F87, F89, F90, F91, F92, F93, D48.** F88 was already archived
in session 38.

*KEEP-LIVE:*
- **D46** — not build-era; the archiving-workflow decision itself, out of
  this session's scope.
- **The F88 pointer note** — already archived in session 38; left in place,
  untouched.
- **D47** — a standing rule (governs future large-pull provenance, like
  D15), not a settled finding, even though it sat inside the same
  session-37 entry as F90. Split out and kept live.
- **F94 — borderline, flagged rather than moved.** It meets the same MOVE
  criterion (settled, headline carried in `SPEC.md` §7 / `RESULTS.md` §5),
  but per the session prompt it is flagged for the owner instead of moved
  silently: it is the headline five-of-five-airports result and very
  fresh. It stays live in `DECISIONS.md` pending the owner's own call on
  whether to archive it now or let it age first, the same way F16/F30/F82
  aged before their own airport's record was folded into SPEC/RESULTS and
  eventually archived.
- **D49, F95** — the consolidation records themselves (SPEC/RESULTS
  fold-in), explicitly kept live: recent, and `STATUS.md` still references
  them directly.
- **Q30, Q32, the parked items (P1–P3), and D17/F7** — pre-build-era or
  otherwise already settled to stay live by earlier decisions (D46 itself,
  for D17/F7); out of this session's scope, untouched.

**The move itself.** A single-pass line partition of `DECISIONS.md` (three
contiguous move ranges in the pre-move file: lines 145–774, 887–1286 and
1291–2058 of that file) extracted 1,797 lines verbatim, unedited, and
appended them to `DECISIONS-archive.md` under a new dated section,
`## Moved by session 45 (2026-09-12)`, with a short note and a pointer to
`SPEC.md` §7 / `RESULTS.md` §5 for the headlines. `DECISIONS.md` was then
replaced with the remaining (kept) lines, in the same order, plus this
entry. Lines 1070–1286 of the pre-move file (F90's own text) moved while
lines 1287–1290 (D47, embedded in the same session-37 section) did not —
the only place a single original section had to be split rather than moved
or kept whole. No entry was retyped, edited, reworded, or renumbered; every
`(Dxx)`/`(Fxx)` citation resolves exactly as it did before the move, now
into `DECISIONS-archive.md` for the moved set.

**What did not happen this session.** No entry's content was edited,
reworded, or summarised — only relocated, verbatim, by mechanical
line-range extraction (`sed`). No entry was renumbered. `SPEC.md` was not
touched. `RESULTS.md` was touched only for the §5.5 clause above — no
figure, table, or any other section changed. No code, script, model, data
file, or figure was touched. Nothing was committed — the owner reviews and
commits this and every prior change by hand.

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
