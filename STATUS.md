# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 15 November 2026, after session 132._

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. Stage C's curve passed its claim
(F150). The end goal (D118.5): a live tool for ten or more airports that
corrects every GFS run into an hourly curve to 48 hours ahead, plus the
daily maximum; version 1 is live and public (D103.9).

- **The documents have two audiences (D121.4, F170).** README.md, RESULTS.md
  and the READMEs in `scripts/`, `data/`, `docs/` and `notes/` are written
  for people: plain language, no D, F or SPEC numbers in their running text,
  and a closing "Where these numbers come from" table. Kept as exceptions:
  README's data credits body, byte-equal (F167.4), and `scripts/README.md`'s
  per-session map and its clone section. SPEC, DECISIONS, the archive,
  ANALYSIS.md and `notes/` are the record and keep their form; STATUS,
  CLAUDE and `docs/PROJECT-INSTRUCTIONS.md` are working files. The new
  figures are in `figures/readme/`, drawn by
  `scripts/session127_readme_figures.py` from committed result files only.
- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79; archived,
  still binding).** Pre-registered, models frozen, scripts gated. **None
  has been run.** The hold rule (D73.8) stands. Session 86's gate can be run
  again through `scripts/session129_stageb_gate.py` (D123.5, F172.7).
  **Prepared by session 131 (D125.5, F174):** the build is accepted only if
  `scripts/session131_stageb_build_check.py` says PASS (no day dropped for a
  fetch failure), otherwise its outputs are moved aside and kept and it is
  run again; the competitor fetch first runs session 87's `--gate`; the look
  runs `scripts/session131_stageb_score.py` (session 87 with F122.5's values
  held as constants). `tests/test_stageb_rules.py` checks ties, the day
  basis, "no verdict", the v17 split, the rows file's dates and the three
  `--guard-check` modes. The `--build` path was rehearsed on 2025-06-01 to
  2025-06-14 at the six airports: 84 of 84 rows equal the training set
  exactly, no drop, in 399 s.
- **Stage C: done (D100, F150).** The look is not run again (D101.2).
- **Descriptive analysis on spent data and the comparisons (D106 to D108,
  D111; F155, F157, F160): done, ECMWF IFS included and closed (D113,
  F162).** `ANALYSIS.md` holds the field guide, Part 2's tables and the
  candidates for later. Spent by these scores (D107.3, D108.5, D111.6):
  AIFS's and IFS's test years at the 12 airports; NBM's, NBS's and MAV's
  at their airports.
- **Observation plausibility check (D109, D110, F158, F159): done.** No
  cleaning rule for the historical observations (D111.2). A spike and
  range guard for live observations comes later, each in its own entry
  (D110.7).
- **Session 132's three items (D127, F176): done, descriptive.** Gates C
  and D pass on the 12 record airports with today's `src/mlwx/`
  (`scripts/session132_gates_cd.py`; 18,768 of 18,768 values equal at each
  of three cycles; pairing 8,639 of 8,640, the one difference by design).
  AIFS and the NBM grid read at the development airports' own position
  (`data/processed/session132_iem/`): the competitor's MAE changes by at
  least 0.05 C at 3 of 6 airports (KDSM, KRNO, KSFO); the largest is the
  NBM grid at KSFO (hourly 1.404 to 0.920, daily maximum 1.868 to 1.196),
  where the curve's lead over it becomes a deficit. Whether ANALYSIS.md's
  Part 1 captions change is for the owner (D127.5(f)). D115.6's question
  (`data/processed/session132_revision/`): the correction points the way
  GFS next revises at 11 of 12 airports (Spearman +0.04 to +0.10, interval
  above 0; NZWN slightly below), small in size; it runs mostly through the
  baseline's part, not the drift tracker's. ANALYSIS.md has Part 4 with
  both. Nothing changes because of either (D127.5, D127.6).
- **Stage G, live product v1: live with 49 airports (D105.2, F154.2).**
  Public repo zadams03/MLwx-live, page at
  https://zadams03.github.io/MLwx-live/. Deployed now (D127.2): MLwx-live
  `b836748` copying the template of session 131b's commit, `MLWX_COMMIT`
  `dad68db` (session 131), `MODELS_TAG` `gfs-models-49`, schedule :15 and
  :40, Python 3.12.15. Manual run 43733122333 on 2026-11-15 was green and
  issued a cycle. The deployed runner has the review's fixes (D125, F174):
  a fetch problem waits and is tried again until the cycle is 20 h old, an
  IEM reply without the expected header makes the cycle wait, and the job
  fails on any runner exit code other than 0 and 2. From this redeploy
  `code_commit` changes; D125.8 says how the live test treats the rows
  after it. D112.8's rule on manual runs stays: none between :35 and :55
  past the hour.
- **The product models are in a private repository (D126, D127.2): done.**
  `zadams03/MLwx-models` holds Release `gfs-models-49`, whose
  `gfs-models.tar` has D105.2's SHA-256, checked before upload and on a
  fresh download. MLwx-live downloads it with the fine-grained token in its
  secret `MODELS_TOKEN` (Contents read-only on that repository, no expiry,
  owner's choice), under the cache key `gfs-models-private-gfs-models-49`.
  MLwx-live's public model Releases, their tags and the old cache are
  deleted; fork pull request workflows need approval for all outside
  contributors. The code, the record, the log and the page stay public.
  Stage B's frozen models stay in MLwx.
- **The outside scheduler: kept as it is (D125.7).** No outside trigger is
  built. It is reopened, by a new entry, if any cycle is lost or any issue
  lag exceeds 18 h. To F173.6: 72 cycles since the 2026-10-27 redeploy, none
  missing; issue lag maximum 12.82 h; longest gap between runs 10.84 h.
- **GFS v17's label (D125.6).** Cycles between v17's go-live and the
  redeploy that adds the v17 row may be logged as v16; the entry that
  records the first v17 cycle lists them. Neither test's periods use the
  label.
- **The independent code review (D124.4, F173): its fixes are done (F174)**
  apart from rulings applied later: LT16 (above), LS11 and SB11 (D125.5),
  and the register rows outside D125.8's groups.
- **Project health check (D112.2 item 3, D114 to D120): done (D120.3).**
  Both audits done (F163, F164). All fix groups done: (1) and (2) (D116,
  F165), (8) by the owner (D116.1), (3) live (D117, F166, D118.2), (7) the
  record text and (9) the data credits (D118, F167), (4) the cache checks
  (D119, F168), (6) the README update (D120, F169; documentation only).
  README's data credits section credits ECMWF IFS and AIFS, the NBM grid,
  NBS, MAV, CLI and GHCN-Daily, with the terms read on 2026-11-01; none
  forbids redistribution. `ANALYSIS.md` carries the ECMWF credit too and
  points to that section by name. The three cache checks, run in a clone
  against the drive, all pass (F168).
- **SPEC 3.4's span (S05, D115.4).** Lines 256 to 287, 2,050 bytes,
  SHA-256 `a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`
  (unchanged). Every later SPEC edit checks the span is unchanged.
- **A pre-registered test of the live forecasts (D105.5, amended by
  D112.6 as D113.4 names).** Locked. No accuracy figure is computed or
  shown until its look (D103.2, D105.6).
- **The live test's scoring script (D105.5(l), D123, F172): written, gated
  and frozen from commit `3bf156f` (D124.1).** `scripts/session129_live_score.py`
  (SHA-256 `0c12c621...bf80`) has three modes: `--inventory`, `--gate` and
  `--score`. Gate (a): on synthetic logs built from stage C's claim
  predictions it reproduces session 107's scores and verdicts byte for
  byte. Gate (b): 54 tests on made-up logs. Gate (c): the real inventory on
  a fresh clone passes (132 log files, each added once; none missing). It
  is never edited; a fix goes in a new script recorded in DECISIONS before
  its look (D123.2, D116.10). Its SHA-256 is now held by
  `tests/test_frozen_scripts.py`, and the seven files it imports or reads are
  pinned at their bytes at `3bf156f` by `tests/test_pinned_files.py`
  (D125.4): a change to one is recorded in DECISIONS first and `--gate` is
  run again; the log's columns and time format do not change before both
  looks. If `--score` stops before any score file is written, its partial
  folders are moved aside and kept, and it is run again unchanged
  (D125.5(a)). `--score` refuses to run until the file is committed and
  unchanged, the period ended 7 days ago, and the inventory passes. It has
  not been run. The readings it takes where D105.5 leaves a choice are in
  F172.3.
- **Project knowledge (D118.8).** After the owner commits and pushes, the
  planning chat clones MLwx fresh from GitHub, checks HEAD is the pushed
  commit, and writes each changed file with project_write's `local_path`;
  every file at the root, the archive and ANALYSIS.md included. If a
  write fails, the owner uploads by hand from a list with repo byte sizes
  (D115.2). Size rule: `knowledge_size` against `max_knowledge_size`
  from project_info (one unit, not bytes); above 80 % (1,600,000 of
  2,000,000) is ACTION NEEDED. On 2026-11-01: 668,149 of 2,000,000. Session
  127 added a new script, a new test, five SVG files (about 114 KB) and
  rewritten documents (README.md and RESULTS.md grew by about 27 KB). Session
  128 adds the folder `deploy/mlwx-mosmix/` (about 40 KB), a new test and
  about 4 KB to DECISIONS.md. Session 129 adds two scripts, two tests and
  `data/processed/session129_gate/` (about 1 MB, mostly a byte-equal copy
  of session 107's scores). Session 130 adds only
  `notes/session-130-register.csv` (about 43 KB) and its output file.
  Session 131 adds three scripts, three test files, two small files in
  `data/processed/session131_rehearsal/` and about 9 KB to DECISIONS.md.
  Session 131b changes the live template, its README and its test, and adds
  about 7 KB to DECISIONS.md and its output file. Session 132 adds three
  scripts, a test, `data/processed/session132_iem/` and
  `data/processed/session132_revision/` (together about 0.8 MB), about 10 KB
  to ANALYSIS.md and about 14 KB to DECISIONS.md.
- **The session order (D127.8).** 133: stage H's design and build
  choices (D125.9), including whether to pre-register a range test on
  2026-27 while no 2026-27 value has been scored (D121.2(4), SPEC 2.5). The
  owner chooses each session's model. A GFS v17 Service Change Notice goes
  ahead of it. Later (D121.2): stage H on GFS; stage D, starting with AIFS,
  then stage E; WeatherNext stays deferred (D107.4). Stage B and the live
  test are scored only when their periods end (D73.8, D105.5).
- **Rulings on ANALYSIS.md's Part 3 (D121.3).** Candidate 6 (station
  guidance where it exists) is parked to stage E; any use first needs an
  owner's ruling on the same-at-every-airport rule (SPEC 2.5). Candidate 7:
  the daily maximum's target (D82.8) is not changed; an official-figure
  maximum at US airports may be added later only as a separate, labelled
  output, by its own entry.
- Stages D, E, F and H follow stage G.
- **MOSMIX saver (D81.2 to D81.5, D122, F171): live (D124.2).** Deployed by
  the owner on 2026-11-14 to the private repository `zadams03/MLwx-mosmix`
  (38 stations; every three hours at :50; one tar per issue as an asset of
  the month's Release, manifest committed). Days before it started are
  lost, which is accepted (D81.5). No MOSMIX test is pre-registered and no
  saved value is compared with anything (D122.7). Session 131's template
  fixes (MS04 to MS06, MS08) are deployed: MLwx-mosmix commit `09418d0`
  on 2026-11-15, one manual run green (D127.3).
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **Readings from session 132 (F176.7).** Where D127.6 left a choice,
  the revision script fixed it before its statistics ran (shared
  resamples per set, per-period intervals, breakdowns pooled, two
  extra not-paired reasons); r's ties are broken only by float rounding;
  the curve is further from the next run than raw GFS because most of its
  correction is a steady local bias; the iem summary covers D98.10's days
  only; the NBM grid at KSFO changes Part 1's picture there.

- **Readings from session 131 (F174.11).** (1) At the rehearsal's rate a
  full period A build would take about 2.9 h and about 27 GB of transfer.
  (2) The rehearsal's 0.16 GB peak memory does not test SB08's whole-period
  estimate (1 to 2 GB). (3) The build check counts a decode failure, two or
  more .idx lines or a wrong run stamp as "data" (reported, not blocking),
  and a message 404 as an absence. (4) After the redeploy a runner crash
  makes every run red. (5) `scripts/README.md`'s frozen-scripts table does
  not list the two session 129 scripts. (6) The dry run fetched its cycle
  twice. Register rows outside D125.8's groups were not addressed.
- **Readings carried from session 129 (F172.8), accepted (D124.1).** Rows
  issued after their valid time reach lead 12 (counted by the live test,
  never excluded). `scripts/session112_analysis.py` differs from both
  SHA-256 in its meta files.
- **Readings carried (F163.11, F165.11, F168.6).** Session 63's two check
  scripts rewrite their committed notes outputs when run (noted in
  `scripts/README.md`, with session 76b's write-once checks). The first
  read of the drive hung for several minutes and cleared by itself (cause
  not found). Session 109's Gate A
  takes 29.4 min. Under D116.10 a fix to a script whose SHA-256 is
  recorded goes in a new script; the session 120 audit inventory
  (`scripts.csv`) was not counted as such a record. Session 117's
  `--subset` stops if session 114's script changes, by design.
- **Readings from session 127 (F170.8), accepted (D122.1).** `tests/README.md`
  now also lists `tests/test_mosmix_saver.py` and session 131's three new
  test files; it still does not list several older test files.
- **Readings from session 128 (F171.9).** DWD's terms were read on a "Legal
  notice" page that does not name MOSMIX (CC BY 4.0 with credit; reading
  unconfirmed with DWD). (The per-station freshness gap is fixed in the
  template, MS06.)
- **MMMX coverage (F159.8).** 28,950 usable hours and 104 usable days.
  Seen, not examined.

---

## Carried items

- **GFS v17 (D93.5, D93.15, D103.10).** A weekly scheduled task checks for
  the Service Change Notice. Until the first operational v17 cycle is
  recorded in a DECISIONS entry, the config's version table says v16. It
  also sets the end of period A in the live test (D105.5(e)).
- **lightgbm (D93.3).** New scripts may import lightgbm directly.
- **Frozen scripts (D62.3(a), D93.8; also D70.6, D80.1)** are never
  edited. Their SHA-256 are checked by `tests/test_frozen_scripts.py`
  (D116.4), ten scripts with session 129's two (D125.4).
- **Recorded values in scripts (D98.2)** and **recorded fingerprints
  (D116.10)**: both now stated in CLAUDE.md.
- **The planning chat's repo access (D118.11).** Through the linked
  computer; writes only into `docs/sessions/` and `docs/commits/`.
- **Tests (D116.2).** `.venv/bin/python -m unittest discover -s tests`;
  409 tests, about 65 s (one skipped when no YAML parser is installed).
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 132 and commit; then plan session 133, stage H's design and build choices (D125.9), including whether to pre-register a range test on 2026-27 while no 2026-27 value has been scored (D121.2(4)).
