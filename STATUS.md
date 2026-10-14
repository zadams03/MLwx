# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 14 October 2026, after session 112._

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
- **A descriptive analysis of stage C on spent data: done (D106, F155).**
  `ANALYSIS.md` holds a draft field guide, an appendix with every planned
  statistic, and five candidates for later. It changed nothing; it
  reproduces F147 and F150 exactly. Headline: the curve beats raw GFS at
  12 of 12 airports for both outputs and linear MOS at 11 of 12 hourly
  (formal tests); the daily maximum reads low by +0.12 to +0.25 degrees C
  at every claim airport, consistent with a selection effect (F155.7(3)).
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
- **matplotlib 3.11.2** is now in `.venv` and `requirements.txt` (owner's
  ruling, session 112).

---

## Open questions (live)

- F155's readings (F155.7), for the owner. In particular: (1) a run never
  holds a whole "day 2" (46 hours of leads), so D106.7's day 1 or 2 split
  was replaced by cycle hour, labelled; any later "day 2" wording
  (D106.15) needs the same care. (2) Two bin-edge choices the plan left
  open (|b| and curve minus raw GFS; whole-day diurnal ranges).
- Which statistics go first in `ANALYSIS.md`'s field guide (D106.2).
- Gates C and D in `scripts/session109_gates.py` loop over all 49
  configured airports; not changed or run (F154.9(4)).

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

**Next planning session:** Review session 112 and commit; then plan session 113 (D106.15): the read-only probe and pull of comparison forecasts on spent years, and the official daily maximum at the four US airports. The owner's WeatherNext access request is pending.
