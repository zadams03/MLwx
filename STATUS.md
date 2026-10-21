# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 21 October 2026, after session 121._

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. Stage C's curve passed its claim
(F150). End goal as D82.2 words it: a live tool for ten or more airports
that corrects every GFS run into an hourly curve plus the daily maximum
(whether "private" still fits is open, F164 row SP05).

- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79; archived,
  still binding).** Pre-registered, models frozen, scripts gated. **None
  has been run.** The hold rule (D73.8) stands. Its three `--guard-check`
  modes pass (F164.4).
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
  https://zadams03.github.io/MLwx-live/. Redeployed 2026-10-20 (D113.2):
  MLwx-live `0d77fb0`, MLwx `d6ca3e4`, models `gfs-models-49`, schedule
  :15 and :40. Audited to 2026-10-21T06z (F161, F163.8): no cycle lost;
  the one cycle issued twice (2026-10-17T18z) left only its first file on
  main, which the live test scores (D113.3).
- **Project health check (D112.2 item 3, D114, D115).** Both audits are
  done, nothing fixed. Session 120, the code (F163): 55 rows, none wrong
  or blocking. Session 121, the record (F164): 109 rows
  (`notes/session-121-register.csv`), OK 63, cosmetic 17, stale 28, wrong
  1 (RM05: README's data credits), none blocking. Next: fix sessions
  planned from both registers (F163.10, F164.9), each with its own entry;
  the README update last (D115.7).
- **SPEC 3.4's span (S05, D115.4).** Lines 252 to 283, SHA-256
  `a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
  Every later SPEC edit checks the span is unchanged.
- **A pre-registered test of the live forecasts (D105.5, amended by
  D112.6 as D113.4 names).** Locked. No accuracy figure is computed or
  shown until its look (D103.2, D105.6).
- **Project knowledge (D115.2, D115.3).** The owner uploads by hand after
  each commit; the planning chat lists each changed file with its repo
  byte size. The archive sits at the root.
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **The fix-session grouping (F163.10, F164.9).** F163's groups (1) code
  and D98.2 constants, (2) session 114's outputs, (3) MLwx-live, (4) cache
  checks, (5) rulings only, (6) README last; with F164's rows added, and
  three new groups: (7) the record text (SPEC, RESULTS, CLAUDE,
  PROJECT-INSTRUCTIONS section 2, 4, 5, 9; STATUS at each overwrite); (8)
  owner only: compare the Project copies' sizes of PROJECT-INSTRUCTIONS
  (15,438 bytes), SPEC (79,467), CLAUDE (8,234) and RESULTS (53,023) and
  re-upload any that differ (PK05 to PK08); (9) data credits (RM05):
  `data/processed/session113/` commits ECMWF IFS and AIFS, NBM grid, NBS,
  MAV, CLI and GHCN-Daily values, and README section 9 says no ECMWF data
  is committed; the terms need a session allowed the network.
- **Rulings named by F164 (group 5).** Is the goal still "private" (SP05,
  ST02, RM02)? A SPEC section for stage G, or a note that its design stays
  in DECISIONS (SP07)? A SPEC pointer to ANALYSIS.md (SP08)? The size
  rule's unit, since the Project's reported size is not bytes and the
  eight files total 1,898,480 bytes (PI07, PK10)? A test command in
  CLAUDE.md after T02 (CL05)? An archive header line on its order (DE03)?
- **F163.11's readings.** Session 96's `--gate` and session 117's
  `--verify` cannot be re-run as they stand. Session 63's two check
  scripts rewrite their committed notes outputs when run. Session 109's
  Gate A takes 29.4 min.
- **Issue lag after the redeploy (F163.8).** About one day of the :15 and
  :40 schedule: too little to judge; re-measured in the MLwx-live fix
  session (D115.7, D112.6(d)).
- **Session 114's own checks after IFS (F160.9(4), F163.7).** `--verify`
  fails on Part 1; `part1.md` and `part2_comparisons.md` out of date; no
  IFS figure. ANALYSIS.md does not state IFS's cold reading or F162's
  outcome (F164 row AN05). Fix groups (1) and (2).
- **A candidate for the longer-term plan (D115.6).** Does the curve's
  correction for a valid hour predict raw GFS's revision for that hour in
  the next cycle? Descriptive, on spent stage C rows, with its rows,
  pairing and statistics fixed in its own entry before any value is
  computed.
- **The longer-term plan (D112.2 item 5).** Stage B's timing; stages D,
  E, F and H; ANALYSIS.md's Part 3 candidates 6 and 7 (F157.7); rows at
  the airport's own position (iem set) for the gridded sources at the
  development airports; Gates C and D in `scripts/session109_gates.py`
  (F154.9(4)); WeatherNext, deferred until the owner's access is granted
  (D107.4); whether to build a MOSMIX saver; and D115.6's candidate.
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
  edited.
- **Recorded values in scripts (D98.2).** Held as constants and checked by
  a test, never found by searching DECISIONS text.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 121 and commit; then plan the first fix session from both registers (F163.10 and F164).
