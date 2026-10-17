# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 17 October 2026, after session 115._

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
- **Observation plausibility check at the 12 stage C airports (D109,
  F158): done.** Flag and count only; nothing was removed or scored. 772 of
  562,232 hourly values were flagged (one spike, 666 stuck-sensor hours,
  106 large residuals, none out of range). 22 of 23,392 usable daily
  maxima are set by a flagged hour. One value looks like a bad report
  (CYYZ 2025-04-28T01:00Z, 27.0 C between 15.0 and 11.0) and it sets a
  claim-look daily maximum on record. The 37 other airports are not checked.
- **ECMWF IFS: not pulled.** The owner runs the pull by hand (D108.2);
  session 116 checks it, then compares IFS with session 114's script
  unchanged (D108.7, D109.2).
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

- **Observation check, what next (D109.7, F158.5).** Whether the check of
  all 51 airports comes before session 116, and which rules it runs. The
  clear-cut rules (out of range, spike) fired once in 12 airports. The
  stuck-sensor rule (666 hours, all at airports that report whole degrees)
  and the residual rule (106 hours, mostly cold hours: cold air in the
  Reno basin, fronts, Dubbo's afternoon cool change) look like real
  weather and are not changed (D109.6). The raw files carry a dew point
  that was not used; it could tell a stuck sensor from steady weather.
  Any exclusion rule is a later D89 build choice on the development
  airports (D109.6). The effect of the CYYZ value on look A's daily
  maximum score was not computed.
- **Project health check (D109.8).** The repo uses a root layout (`docs/`,
  `notes/`, DECISIONS at the root), not the `research/` and `audit/`
  layout recorded in D90.5. Examined in the planned health-check session.
- **IFS's daily maximum rule (F157.7(1)).** D108.4(b) takes a
  competitor's own maximum field where it exists; IFS's mx2t3 is a
  3-hour field, many windows a day. The script uses IFS's highest
  3-hourly 2 m step as the primary maximum and mx2t3's windows inside the
  local day as a second; session 116's entry should confirm or change
  this before IFS is scored.
- F157's readings (F157.7): AIFS's daily-maximum result rests partly on
  its 6-hourly sampling; at the development airports AIFS and the NBM grid
  are read at GFS's position, 1.8 to 8.5 km from the airport (D108.3); NBS
  beats the curve hourly at all 5 airports it covers; the curve reads +0.28 to +0.70
  degrees C low against CLI. Part 3 candidates 6 and 7.
- Descriptive rows at the airport's own position (iem set) for the
  gridded sources at the development airports (planning chat to decide;
  session 115 became the observation check, D109.2).
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

**Next planning session:** Review session 115 and commit. Then decide from F158 whether the 51-airport observation check comes before session 116 (D109.7); session 116 is the IFS comparisons (D108.7, D109.2), after the owner's hand IFS pull (D108.2).
