# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 19 October 2026, after session 118._

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
- **ECMWF IFS (D111, F160).** The owner's hand pull was checked (every
  file, count and gap reconciled; 87 HTTP 503 retries, no chunk written
  twice). The curve beats IFS at 12 of 12 airports hourly (claim airports
  +6.3 % EDDM to +32.1 % ZGSZ) and for the daily maximum (IFS's 3-hourly
  steps, D111.4; claim +12.5 % EDDM to +50.0 % NZWN); Benjamini-Hochberg
  rejects at 12 of 12 in both families. IFS changes no standing in the field
  guide. mx2t3, on the days it exists, beats IFS's step maximum at 12 of 12
  and loses to the curve at 10 of 12 (descriptive, computed by
  `scripts/session117_ifs_guide.py --subset`).
- **Observation plausibility check (D109, D110, F158, F159): done.** No
  cleaning rule is adopted for the historical observations (D111.2). A
  spike and range guard for live observations comes later, as a stage G
  fix and in the live test's scoring script, each in its own entry before
  it acts on any value (D110.7).
- **Stage G, live product v1: live with 49 airports (D105.2, D105.3,
  F154.2).** Public repo zadams03/MLwx-live, page at
  https://zadams03.github.io/MLwx-live/. Deployed: MLwx `d6ca3e4`, models
  `gfs-models-49`, one hourly schedule (:40 UTC). Audited to 2026-10-19
  (F161): no cycle lost, no silent push failure, one stale checkout on
  17 Oct that pushed nothing; GitHub ran 39 of 150 schedule slots, issue
  lag median 5.6 h. **Fixes in the template, awaiting the owner's redeploy
  (D112.6, D112.8):** checkout of the latest main, a push that fails the
  job unless it lands, no "latest only" input, schedule :15 and :40.
- **A pre-registered test of the live forecasts (D105.5).** Locked. No
  accuracy figure is computed or shown until its look (D103.2, D105.6).
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **F160's readings (F160.9).** IFS read this way runs cold (mean error
  +0.39 to +1.15 C at 10 of 12 airports), and its 0.4 degree months with no
  height treatment are far worse at KRNO and KSFO; part of its deficit may
  be the open-data product and the reading method (not examined). Raw GFS's
  MAE is below IFS's at 5 of 12 hourly and 8 of 12 for the maximum.
- **An mx2t3 rerun (F160.9(3)).** mx2t3 failed the pull's identity check
  from 2025-02-25T06Z to 2026-02-11T06Z (GRIB short name `max_2t`; whether
  it is the same quantity was not checked). A rerun would add about 350
  days; it needs its own entry, since it changes session 113's check.
- **F161's readings (F161.10).** Every run commits (the state's
  `last_run`), so overlapping runs always conflict on the state file;
  six actions are forced from Node.js 20 to 24; `setup-python` "3.12"
  floats (runs used 3.12.15). Whether the :15 and :40 schedule shortens
  the issue lag is seen after the redeploy; an outside scheduler only if
  it does not (D112.6(d)).
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
- **Until the redeploy (D112.8):** no manual run of MLwx-live between :35
  and :55 past the hour, and "latest only" left unticked. At the redeploy
  the owner copies the whole template with `MLWX_COMMIT` and `MODELS_TAG`
  unchanged (`d6ca3e4...`, `gfs-models-49`).

---

## Next

**Next planning session:** Review session 118 and commit; then the owner
redeploys MLwx-live from the template (D112.8), one step at a time. Then
D112.2's order: the IFS close-out (the reading-fault check and the mx2t3
rerun), the project health check (audit, then fixes, ending with the
README update), then the longer-term plan.
