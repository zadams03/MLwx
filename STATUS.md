# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 12 October 2026, after session 109._

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
- **Stage C: done (D100, F150).** Both outputs pass at 6 of 6 claim
  airports in both held-out years. The look is not run again (D101.2).
- **Stage G, live product v1: built and gated, not deployed (D103, F152).**
  The package `src/mlwx/` (GFS only, the weather model is a setting), 12
  airports, the 2,208 frozen product models (manifest SHA-256
  `16485f38...41ef`, 306 MB, to be one Release asset, in
  `../MLwx-live-build/models/`), the log, tracker state, page and runner,
  and the live repo's files in `deploy/mlwx-live/`. Gates A to D passed
  (D103; owner rulings at the Gate D stop in F152.7). One dry run was made
  into `/tmp/mlwx-dryrun.R8jNkG`. The workflow is untested on GitHub.
  Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- F152's readings (F152.11), for the owner.

---

## Carried items

- **GFS v17 (D93.5, D93.15, D103.10).** A weekly scheduled task checks for
  the Service Change Notice. Until the first operational v17 cycle is
  recorded in a DECISIONS entry, the config's version table says v16.
- **lightgbm (D93.3).** New scripts may import lightgbm directly.
- **Frozen scripts (D62.3(a), D93.8)** are never edited.
- **Recorded values in scripts (D98.2).** Held as constants and checked by
  a test, never found by searching DECISIONS text.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 109. The owner commits (`git commit -F docs/commits/commit-109.txt`, written by the planning chat) and the planning chat syncs Project knowledge. Then plan session 110: the owner creates MLwx-live; deploy (set the two placeholders in the workflow, upload the models as a Release asset, run it by hand first); check the first live runs; the onboarding script and the other 39 airports.
