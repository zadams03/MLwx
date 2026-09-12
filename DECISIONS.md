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
