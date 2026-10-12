# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 12 October 2026, after session 108._

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. End goal: a private, live tool for
ten or more airports that corrects every GFS run into an hourly curve plus
the daily maximum (D82.2).

- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79; archived,
  still binding).** Pre-registered, models frozen, scripts gated. **None
  has been run.** Per period, after it ends: build, fetch, score. The hold
  rule (D73.8) stands. Session 86's `--gate` cannot be re-run (D96.3).
- **Stage C: done (D100, F150).** Both outputs pass at 6 of 6 claim
  airports in both held-out years. The result is in SPEC 9.5, RESULTS 7 and
  the README (D102.2). The look is not run again (D101.2).
- **Stage G is next (D102.4):** live product version 1, on GFS only, with
  the weather model as a setting. Stages D, E, F and H follow it.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.
- **GRIB cache.** Moved to an external drive (D102.3). Only finished
  scripts from sessions 37 to 89 read it.

---

## Open questions (live)

- F151's readings (F151.8), for the owner.

---

## Carried items

- **GFS v17 (D93.5, D93.15).** A weekly scheduled task checks for the
  Service Change Notice and alerts the owner. The go-live date matters for
  stage G's design.
- **lightgbm (D93.3).** New scripts may import lightgbm directly.
- **Frozen scripts (D62.3(a), D93.8)** are never edited.
- **Recorded values in scripts (D98.2).** Held as constants and checked by
  a test, never found by searching DECISIONS text.
- **Later work (D90.12).** A `src/` package only at stage G.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 108. The owner commits and pushes (`git commit -F docs/commits/commit-108.txt`) and the planning chat syncs Project knowledge. Then design stage G (live product v1 on GFS, including GFS v17 handling) in the planning chat, and plan session 109.
