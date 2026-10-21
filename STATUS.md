# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 21 October 2026, after session 120._

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. End goal: a private, live tool for
ten or more airports that corrects every GFS run into an hourly curve plus
the daily maximum (D82.2).

- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79; archived,
  still binding).** Pre-registered, models frozen, scripts gated. **None
  has been run.** The hold rule (D73.8) stands.
- **Stage C: done (D100, F150).** The look is not run again (D101.2).
- **Descriptive analysis on spent data and the comparisons (D106, D107,
  D108, D111; F155, F157, F160): done, ECMWF IFS included.** `ANALYSIS.md`
  holds the field guide (Part 1, IFS in item 4), Part 2's comparison tables
  E1 to E16 (IFS in E10 to E16) and the candidates for later. Spent by these
  scores (D107.3, D108.5, D111.6): AIFS's and IFS's test years at the 12
  airports; NBM's, NBS's and MAV's at their airports.
- **ECMWF IFS (D111, F160; closed by D113, F162).** The curve beats IFS at
  12 of 12 airports hourly and for the daily maximum (IFS's 3-hourly steps,
  D111.4). IFS changes no standing in the field guide. The reading check
  (D113.6, F162): no fault mark shows at any of five tests (height,
  position, timing, product changes, decoding), so IFS's cold error is
  recorded as the model's, as read under D108.3, and F160 stands. The
  mx2t3 rerun is dropped (D113.5). T5's two extra fetches
  on the main 0.25 degree grid's first and last 00z dates (F163.9): no mark.
- **Observation plausibility check (D109, D110, F158, F159): done.** No
  cleaning rule is adopted for the historical observations (D111.2). A
  spike and range guard for live observations comes later, as a stage G
  fix and in the live test's scoring script, each in its own entry before
  it acts on any value (D110.7).
- **Stage G, live product v1: live with 49 airports (D105.2, D105.3,
  F154.2).** Public repo zadams03/MLwx-live, page at
  https://zadams03.github.io/MLwx-live/. Redeployed by the owner on
  2026-10-20 (D113.2): MLwx-live commit `0d77fb0`, the workflow copied
  whole from the template (checkout of the latest main, a push that fails
  the job unless it lands, no "latest only" input, schedule :15 and :40),
  with MLwx `d6ca3e4` and models `gfs-models-49` unchanged; manual run
  39488813037 green and its push landed. Audited to 2026-10-19 (F161): no
  cycle lost, no silent push failure.
- **Project health check (D112.2 item 3, D114).** Session 120 audited the
  code (F163): 55 register rows (`notes/session-120-register.csv`), OK
  31, cosmetic 8, stale 16, none wrong or blocking. The layout matches
  D91.3 plus four traced additions (D114.2 answers D109.8). Next: session
  121 audits the record (D114.3), then fix sessions from both registers,
  the README update last.
- **A pre-registered test of the live forecasts (D105.5, amended by
  D112.6 as D113.4 names).** Locked. No accuracy figure is computed or
  shown until its look (D103.2, D105.6).
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **F163's grouping of fixes (F163.10, the output file).** (1) Small code
  fixes, plus D98.2 constants for session 92, 95 and 96's `--gate` and
  the SHA-256 of frozen session 39, 48 and 60 (one ruling). (2) Session
  114's outputs: its Part 1 template with IFS, `part1.md` and
  `part2_comparisons.md` (write-once files), an IFS figure (rulings).
  (3) MLwx-live: README text (template l.65 to 68, and the deployed v1
  README), actions to their Node.js 24 majors, pinning Python 3.12.15, no
  commit when only `last_run` changes; an entry under D105.5(k) first,
  then a redeploy. (4) Cache checks when the drive is attached. (5)
  Rulings only: pytest or unittest (pytest is not in `.venv`); whether
  stage B's session 86 `--gate` (cannot run as it stands, D96.3) needs
  anything before period A; the outside scheduler later.
- **F163.11's readings.** Session 96's `--gate` and session 117's
  `--verify` cannot be re-run as they stand (new; not in D98.2). Session
  63's two check scripts rewrite their committed notes outputs when run.
  Session 109's Gate A takes 29.4 min.
- **Issue lag after the redeploy (F163.8).** About one day of the :15 and
  :40 schedule: 4 scheduled runs in 43 slots, issue lag 5.18 to 6.57 h.
  Too little to judge; re-measured in the MLwx-live fix session (D112.6(d)).
- **Session 114's own checks after IFS (F160.9(4), pinned in F163.7).**
  `--verify` fails on Part 1 (template says "pending"); `part1.md` and
  `part2_comparisons.md` out of date; no IFS figure; `subdaily_max`
  (no effect) and `F156_4` (no IFS entry). Fix sessions (1) and (2).
- **MMMX coverage (F159.8).** 28,950 usable hours (of about 49,000) and
  104 usable days. Seen, not examined.
- F157's readings (F157.7): AIFS's daily-maximum result rests partly on
  its 6-hourly sampling; at the development airports AIFS and the NBM grid
  are read at GFS's position, 1.8 to 8.5 km from the airport (D108.3); NBS
  beats the curve hourly at all 5 airports it covers; the curve reads +0.28
  to +0.70 degrees C low against CLI. Part 3 candidates 6 and 7.
- Descriptive rows at the airport's own position (iem set) for the
  gridded sources at the development airports (planning chat to decide).
- Gates C and D in `scripts/session109_gates.py` loop over all 49
  configured airports; not changed or run (F154.9(4)).
- WeatherNext: deferred until the owner's access is granted (D107.4).

---

## Carried items

- **GFS v17 (D93.5, D93.15, D103.10).** A weekly scheduled task checks for
  the Service Change Notice. Until the first operational v17 cycle is
  recorded in a DECISIONS entry, the config's version table says v16. It
  also sets the end of period A in the live test (D105.5(e)).
- **lightgbm (D93.3).** New scripts may import lightgbm directly.
- **Frozen scripts (D62.3(a), D93.8)** are never edited.
- **Recorded values in scripts (D98.2).** Held as constants and checked by
  a test, never found by searching DECISIONS text.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 120 and commit; then plan
session 121, the audit of the record (D114.3).
