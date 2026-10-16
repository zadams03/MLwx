# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 16 October 2026, after session 113._

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
- **A descriptive analysis of stage C on spent data: done (D106, F155,
  accepted in D107.1).** `ANALYSIS.md` holds the draft field guide.
- **Comparison sources on spent years: probed and mostly pulled (D107,
  F156).** Point values in `data/processed/session113/`: AIFS (12
  airports, from 2025-02-25), the NBM grid and NBS (DSM, RNO, KSFO, KORD,
  CYYZ), MAV (the four US airports), and the official daily maximum (CLI
  and GHCN-Daily, four US airports). **ECMWF IFS is not pulled**: over the
  24-hour gate even at 16 and 32 requests at once (F156.3). Nothing has
  been scored. Session 114's comparison rules are fixed in D107.9.
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

- **IFS pull (F156.9(1)).** A follow-up session with
  `scripts/session113_comparison_pull.py --pull ifs` unchanged needs the
  owner's D107.7 override of the hours (about 26.5 h at 8 at once).
  Until then, session 114 has no IFS values.
- F156's readings (F156.9): NBS's 01/07/13/19 UTC runs hold one hour more
  data than their GFS cycle; NBM grid terrain absent (elevation treatment
  labelled); IFS terrain only from 2024-12-03 and mx2t3 only from 49r1;
  NBS TXN definition before v5.0 not read; the official sources agree on
  fewer days in 2024-25 at KDSM and KORD; KORD's CLI site is 3.07 km from
  IEM's ORD position.
- The owner's rulings and corrections in F156.2, recorded as rulings for
  the owner to confirm in the next D entry.
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

**Next planning session:** Review session 113 and commit; then plan session 114 (D107.9): the comparisons against ECMWF, NBM and MAV, the official-maximum gap, and the field guide finished. WeatherNext is deferred until the owner's access is granted (D107.4).
