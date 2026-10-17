# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 17 October 2026, after session 116._

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
- **Descriptive analysis on spent data (D106, F155) and the comparisons
  (D107, D108, F157): done, except ECMWF IFS.** `ANALYSIS.md` holds the
  field guide in D108.6's order, Part 2's comparison tables (E1 to E9)
  and two new candidates. Spent by these scores (D107.3, D108.5): AIFS's
  test years at the 12 airports; NBM's, NBS's and MAV's at their airports.
- **Observation plausibility check at all 51 airports (D109, D110, F158,
  F159): done.** Flag and count only; nothing was removed or scored. Of
  2,357,664 hourly values, none is out of range, 5 are single-hour spikes
  and 2,466 sit in 87 stuck-sensor runs (24 hours or more with one value),
  all at whole-degree airports. The dew point moved during 78 of the 87
  runs (91 % of the hours), 7 runs are saturated (dew point equals
  temperature, fog-like) and 2 are suspect (EGLC, RCSS, 2021). One spike
  is clearly bad: SAEZ 58.0 C on 2021-08-25T01:00Z, which sets a daily
  maximum. 89 of 94,882 usable daily maxima are set by a flagged hour.
  28 of 51 airports have no flag. The live observation log was left out
  (D110.7).
- **ECMWF IFS: not pulled.** The owner runs the pull by hand (D108.2);
  session 117 checks it, then compares IFS with session 114's script
  unchanged (D108.7, D110.2).
- **Stage G, live product v1: live with 49 airports (D105.2, D105.3,
  F154.2).** Public repo zadams03/MLwx-live, page at
  https://zadams03.github.io/MLwx-live/. Models `gfs-models-49`, one
  hourly schedule (:40 UTC).
- **A pre-registered test of the live forecasts (D105.5).** Locked. No
  accuracy figure is computed or shown until its look (D103.2, D105.6).
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- **Whether to propose an observation cleaning rule (F158, F159).** Any
  rule is a later D89 build choice on the six development airports
  (D109.6, D110.6), applied the same everywhere, and not chosen by its
  effect on any spent year's score. Facts for the decision (F159.7): the
  spike check (b) is the only check that fired on likely faults (5 hours);
  the range check (a) never fired and its 60.0 bound missed SAEZ's 58.0;
  the stuck-sensor check (c) as set acts on 2,466 hours that read mostly
  as real weather, and with the dew point (class iv only) on 51 hours. At
  the development airports only EGLC (108 stuck hours) and LFPG (29) are
  flagged. If a rule is ever used in the live test, it goes through the
  test's scoring script and its own DECISIONS entry first (D110.7). Whether
  any rule can apply to stage B's pre-registered test is a separate entry
  before that test is scored (D110.7).
- **Table reader and lead (session 116).** The exposure counts read each
  table row's lead (a row label, not a forecast value) to keep D109.5's
  definition of a target; the prompt said valid time and observation only.
  Recorded for the owner to confirm.
- **MMMX coverage (F159.8).** 28,950 usable hours (of about 49,000) and
  104 usable days. Seen, not examined.
- **Project health check (D109.8).** The repo uses a root layout (`docs/`,
  `notes/`, DECISIONS at the root), not the `research/` and `audit/`
  layout recorded in D90.5. Examined in the planned health-check session.
- **IFS's daily maximum rule (F157.7(1)).** D108.4(b) takes a
  competitor's own maximum field where it exists; IFS's mx2t3 is a
  3-hour field, many windows a day. The script uses IFS's highest
  3-hourly 2 m step as the primary maximum and mx2t3's windows inside the
  local day as a second; session 117's entry should confirm or change
  this before IFS is scored.
- F157's readings (F157.7): AIFS's daily-maximum result rests partly on
  its 6-hourly sampling; at the development airports AIFS and the NBM grid
  are read at GFS's position, 1.8 to 8.5 km from the airport (D108.3); NBS
  beats the curve hourly at all 5 airports it covers; the curve reads +0.28 to +0.70
  degrees C low against CLI. Part 3 candidates 6 and 7.
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

**Next planning session:** Review session 116 and commit. Then decide from F158 and F159 whether to propose an observation cleaning rule (a D89 build choice on the development airports, D109.6, D110.6) before the direction brainstorm; session 117 is the IFS comparisons (D108.7, D110.2), after the owner's hand IFS pull (D108.2).
