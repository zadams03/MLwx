# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 2 November 2026, after session 127._

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
  modes pass (F167.5).
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
- **The outside scheduler: closed for v1 (D118.4).** Reopened only by a
  new entry, if any cycle's issue lag exceeds 12 h.
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
- **Project knowledge (D118.8).** After the owner commits and pushes, the
  planning chat clones MLwx fresh from GitHub, checks HEAD is the pushed
  commit, and writes each changed file with project_write's `local_path`;
  every file at the root, the archive and ANALYSIS.md included. If a
  write fails, the owner uploads by hand from a list with repo byte sizes
  (D115.2). Size rule: `knowledge_size` against `max_knowledge_size`
  from project_info (one unit, not bytes); above 80 % (1,600,000 of
  2,000,000) is ACTION NEEDED. On 2026-11-01: 668,149 of 2,000,000. Session
  127 adds a new script, a new test, five SVG files (about 114 KB) and
  rewritten documents (README.md and RESULTS.md grew by about 27 KB).
- **The longer-term plan (D121.2, D121.3).** In this order: (1) session
  127, the rewrite (done); (2) the MOSMIX saver (D81.2 to D81.5), in its
  own session; (3) one session for three small items: Gates C and D in
  `scripts/session109_gates.py` (F154.9(4)), by a new script under D116.10;
  rows at the airport's own position (iem set) for AIFS and the NBM grid at
  the development airports, descriptive; and D115.6's question, with its
  rows, pairing and statistics fixed in its own entry first; (4) stage H on
  GFS, with its build choices on the development airports (D89); whether
  to pre-register a range test on 2026-27 is decided early, while no
  2026-27 value has been scored (SPEC 2.5); (5) stage D, starting with
  AIFS, then stage E; whether raw AIFS goes straight into the GFS model as
  inputs is decided when stage D is planned (D72.2(b)); (6) WeatherNext
  stays deferred (D107.4). A GFS v17 Service Change Notice goes ahead of
  all of these: one session for the live tool's v17 handling (D103.10) and
  for preparing stage B's scoring (D73.4, D118.10). Stage B and the live
  test are scored only when their periods end (D73.8, D105.5).
- **Rulings on ANALYSIS.md's Part 3 (D121.3).** Candidate 6 (station
  guidance where it exists) is parked to stage E; any use first needs an
  owner's ruling on the same-at-every-airport rule (SPEC 2.5). Candidate 7:
  the daily maximum's target (D82.8) is not changed; an official-figure
  maximum at US airports may be added later only as a separate, labelled
  output, by its own entry.
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **Session 86's gate (S06): deferred (D118.10).** If stage B needs
  `session86_forward_build.py --gate` before period A is scored, the
  session that prepares stage B's run builds a wrapper with constants
  checked by a test, as D116.3 did; the frozen script is not edited.
- **Readings carried (F163.11, F165.11, F168.6).** Session 63's two check
  scripts rewrite their committed notes outputs when run (noted in
  `scripts/README.md`, with session 76b's write-once checks). The first
  read of the drive hung for several minutes and cleared by itself (cause
  not found). Session 109's Gate A
  takes 29.4 min. Under D116.10 a fix to a script whose SHA-256 is
  recorded goes in a new script; the session 120 audit inventory
  (`scripts.csv`) was not counted as such a record. Session 117's
  `--subset` stops if session 114's script changes, by design.
- **Readings from session 127 (F170.8).** `tests/README.md` does not yet
  list `tests/test_session127_figures.py` (out of scope for session 127).
  The older figures reused in RESULTS.md carry record numbers in their own
  text. Figure (c) says the live test's rules were written on 14 October
  2026 and its forecasts logged from 12 October 2026: the lock came after the
  first cycles and before any scoring.
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
  206 tests.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 127 and commit; the planning chat syncs Project knowledge (D118.8); then plan the MOSMIX saver (D121.2 item 2).
