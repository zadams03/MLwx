# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 14 October 2026, after session 111._

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
- **Stage G, live product v1: live with 49 airports (D105.2, D105.3,
  F154.2).** Public repo zadams03/MLwx-live, pinned to session 110's
  commit, models `gfs-models-49`, one hourly schedule (:40 UTC), page at
  https://zadams03.github.io/MLwx-live/. Every cycle from 2026-10-12 12z
  to 2026-10-14 00z is logged; the first 49-airport cycle is 2026-10-13
  18z. Issue lag so far 5 h 25 min to 8 h 59 min.
- **A pre-registered test of the live forecasts (D105.5).** Locked before
  any value on or after 2026-08-01 is scored. Period A runs to the last
  v16 cycle or 2027-07-31 18z. No accuracy figure is computed or shown
  until its look (D103.2, D105.6).
- **Made and tested in session 111, not yet live (F154):** the
  observation snapshot (`obs/`, D105.7), and the template with `obs/` in
  its commit line (D105.9). They go live at the next redeploy. The refit
  and Gate A now handle 49 airports (D105.8).
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- F154's readings (F154.9), for the owner. (1) and (5) were fixed at
  review.
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

**Next planning session:** Review session 111 and commit; then the owner's redeploy (D105.9): set `MLWX_COMMIT` in MLwx-live's workflow to session 111's commit and copy the template's two commit lines (`git add log state` and `if [ -d obs ]; then git add obs; fi`); then a dedicated planning chat on deeper statistics of the current models, using only spent data (D105.10).
