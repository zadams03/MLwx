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
