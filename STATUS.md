# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 14 November 2026, after session 130._

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
  has been run.** The hold rule (D73.8) stands. Its three `--guard-check`
  modes pass (F167.5). Session 86's gate can be run again through
  `scripts/session129_stageb_gate.py` (D123.5); run once on 2026-11-14, it
  equals F128 in every field (F172.7).
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
- **Stage G, live product v1: live with 49 airports (D105.2, F154.2).**
  Public repo zadams03/MLwx-live, page at
  https://zadams03.github.io/MLwx-live/. Redeployed 2026-10-27 with fix
  group (3) (D118.2): MLwx-live `628df88`, `MLWX_COMMIT` `d6ca3e4`,
  `MODELS_TAG` `gfs-models-49`, schedule :15 and :40, six actions on
  Node.js 24, Python 3.12.15, no commit or page on a run that changes only
  `last_run.at`. The template matches the deployed workflow apart from the
  two `SET-AT-DEPLOY` values (D105.9). Planning-chat check to 2026-11-01
  00z: every cycle logged, none missing; the 00z cycle's issue lag was
  about 9.4 h (D118.3). D112.8's rule on manual runs stays: none between
  :35 and :55 past the hour.
- **The outside scheduler: reopened (D124.3), for the owner to rule.** Since the
  2026-10-27 redeploy (F173.6): 72 cycles, none missing; issue lag median
  7.44 h, 90th percentile 10.89 h, maximum 12.82 h; three cycles above 12 h
  (2026-11-02 06z, 2026-11-05 00z, 2026-11-09 06z). GitHub started 71 of 856
  schedule slots (8.3 %), about 3.9 runs a day. Options set out in F173.6
  and `notes/session-130-output.txt`: (a) keep; (b) more slots (the record
  says it does not help); (c) an outside trigger calling `workflow_dispatch`;
  (d) a second scheduled workflow, the owner's machine, or a sleeping chain.
- **The independent code review (D124.4, F173): done, nothing fixed.**
  `notes/session-130-register.csv` holds 97 checks of the live tool, its
  workflow, the MOSMIX saver template, stage B's path and the live test's
  scoring script: 42 OK, 1 critical, 7 major, 15 minor, 26 notes, 6
  efficiency. Critical: LT09, a cycle first tried after 12 hours gets one
  try and one fetch error loses it (no cycle has been lost). Major: WF05 (a
  runner crash gives a green job), LT16 (the first v17 cycles would be
  labelled v16), LS09 (the frozen scoring script imports `src/mlwx` as it
  is at the look), LS10 (the log's format cannot change before the looks),
  LS11 (a failed fetch at the look blocks every later run), SB07 (a network
  failure becomes a dropped day in stage B's build), SB11 (a changed NBM or
  MOS layout reads as no value). The findings wait for session 131, in the
  order of F173.7; its first group (a test pinning what the frozen scoring
  script imports, and three rulings) comes before any edit of `src/mlwx`.
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
  its look (D123.2, D116.10). No test yet holds its SHA-256 (F173, TE02). `--score`
  refuses to run until the file is committed and unchanged, the period
  ended 7 days ago, and the inventory passes. It has not been run. The
  readings it takes where D105.5 leaves a choice are in F172.3.
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
- **The session order (D122.2; D121.2's content unchanged).** 128: the MOSMIX
  saver (built, see below). 129: the live test's scoring script and session
  86's gate wrapper (done, see above). 130: the independent, read-only code review
  (done, see above). 131: fixes from that register (F173.7),
  Gates C and D (F154.9(4)), the iem-position rows for AIFS and the NBM grid at
  the development airports, and D115.6's question, each with its rules fixed in
  that session's entry first. 132: stage H's design and build choices. A GFS
  v17 Service Change Notice goes ahead of any of these. Later (D121.2): stage H
  on GFS, whether to pre-register a range test on 2026-27 decided early, while
  no 2026-27 value has been scored (SPEC 2.5); stage D, starting with AIFS,
  then stage E; WeatherNext stays deferred (D107.4). Stage B and the live test
  are scored only when their periods end (D73.8, D105.5).
- **Rulings on ANALYSIS.md's Part 3 (D121.3).** Candidate 6 (station
  guidance where it exists) is parked to stage E; any use first needs an
  owner's ruling on the same-at-every-airport rule (SPEC 2.5). Candidate 7:
  the daily maximum's target (D82.8) is not changed; an official-figure
  maximum at US airports may be added later only as a separate, labelled
  output, by its own entry.
- Stages D, E, F and H follow stage G.
- **MOSMIX saver (D81.2 to D81.5, D122, F171): live (D124.2).** Deployed by
  the owner on 2026-11-14 to the private repository `zadams03/MLwx-mosmix`
  from the template `deploy/mlwx-mosmix/` at `73370ed` (38 stations; every
  three hours at :50; one tar per issue as an asset of the month's Release,
  manifest committed). One run by hand was green: Release `mosmix-2026-11`
  and `manifest/2026-11.csv`. Days before it started are lost, which is
  accepted (D81.5). No MOSMIX test is pre-registered and no saved value is
  compared with anything (D122.7). The private repository was not read by
  session 130; the review's findings on the template are MS04 to MS09.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **Readings from session 130 (F173.8).** Three cycles, not one, passed
  D118.4's 12 h mark. LT09 is rated critical because its condition has
  occurred three times, though nothing was lost. Step 8b's timed re-issue of
  a real cycle was not run (it needs NOAA's archive; the session's network
  rule allowed GitHub only); the parts were timed on synthetic input. The
  owner rules on the scheduler, on the new give-up rule (LT09), on the v17
  label (LT16), on the log's format and a failed fetch at the look (LS10,
  LS11), and on stage B's build (SB07, SB09, SB11).
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
  now lists `tests/test_session127_figures.py` and session 129's two test
  files; it still does not list `tests/test_mosmix_saver.py` or several
  older test files.
- **Readings from session 128 (F171.9).** The saver's first by-hand run on
  GitHub was green (D124.2). `--check-fresh` would not catch one station that stops updating while its
  directory stays. DWD's terms were read on a "Legal notice" page that does
  not name MOSMIX (CC BY 4.0 with credit; reading unconfirmed with DWD).
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
  (D116.4).
- **Recorded values in scripts (D98.2)** and **recorded fingerprints
  (D116.10)**: both now stated in CLAUDE.md.
- **The planning chat's repo access (D118.11).** Through the linked
  computer; writes only into `docs/sessions/` and `docs/commits/`.
- **Tests (D116.2).** `.venv/bin/python -m unittest discover -s tests`;
  333 tests (one skipped when no YAML parser is installed).
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 130 and commit; the planning chat syncs Project knowledge (D118.8); the owner rules on the scheduler; then session 131, the fixes (D122.2).
