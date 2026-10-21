# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 20 October 2026, after session 119._

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
  mx2t3 rerun is dropped (D113.5).
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
- **A pre-registered test of the live forecasts (D105.5, amended by
  D112.6 as D113.4 names).** Locked. No accuracy figure is computed or
  shown until its look (D103.2, D105.6).
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **F162's readings (F162.9).** No reading fault was found. IFS is coldest
  in the evening and at night and least cold near local midday; its
  elevation treatment reduces the cold error rather than causing it. T5
  checked one message on the main 0.25 degree grid; two more fetches would
  cover that grid's first and last 00z dates, if the owner wants them.
  Session choices where D113.6 was open (T4's 20-day window and its
  reading of "no step") are listed in `notes/session-119-output.txt`.
- **F161's readings (F161.10).** Every run commits (the state's
  `last_run`), so overlapping runs always conflict on the state file;
  six actions are forced from Node.js 20 to 24; `setup-python` "3.12"
  floats (runs used 3.12.15). Whether the :15 and :40 schedule shortens
  the issue lag is seen now that the redeploy is done; an outside
  scheduler only if it does not (D112.6(d)).
- **Tests in the venv (F161.1).** `pytest` is not in `.venv`; the suite
  runs as `python3 -m unittest discover -s tests` (181 tests). The health
  check (D112.2) may record this.
- **Session 114's own checks after IFS (F160.9(4)).** Session 114's
  `--verify` now fails on Part 1 (its template still says "pending"), and
  `session114_comparisons/part1.md` and `part2_comparisons.md` are out of
  date. No IFS figure exists (session 114's figures exclude IFS). Its
  `subdaily_max` does not check that every window is present (no effect
  here), and its `F156_4` has no IFS entry.
- **MMMX coverage (F159.8).** 28,950 usable hours (of about 49,000) and
  104 usable days. Seen, not examined.
- **Project health check (D109.8).** The repo uses a root layout (`docs/`,
  `notes/`, DECISIONS at the root), not the `research/` and `audit/`
  layout recorded in D90.5. Examined in the planned health-check session.
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

**Next planning session:** Review session 119 and commit. If F162 shows a
fault mark, the owner rules under D112.3 first. Then the project health
check's audit (D112.2 item 3), then its fixes, ending with the README
update.
