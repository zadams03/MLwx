# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 13 October 2026, after session 110._

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
- **Stage G, live product v1: deployed with 12 airports (D104.2, D104.3).**
  Public repo zadams03/MLwx-live, pinned to session 109's commit, models
  `gfs-models-12`, page at https://zadams03.github.io/MLwx-live/. Runs
  issue every cycle; scheduled runs can start hours late (the 24-hour
  catch-up recovers them).
- **49 airports onboarded and ready, not live (D104, F153).** The 12 plus
  37 of the 39 others, by `python -m mlwx.onboard`, gated on NZWN and ORD
  byte for byte. Left out: MMMX (D104.7, smallest cell 767 rows, which
  closes D83.4) and VILK (owner's time-zone rule at the Step 4 stop,
  F153.5: Asia/Kolkata is UTC+5:30). Combined models in
  `../MLwx-live-build/models-49/`, manifest SHA-256 `484590bf...aeea4`
  (`baseline.MANIFEST_SHA256`); tar `../MLwx-live-build/gfs-models-49.tar`,
  1,248,979,968 bytes, SHA-256 `e30f8fb9...f284`. Not uploaded. One dry
  run with all 49 airports into `/tmp/mlwx-dryrun.nm4b4V`.
- **The runner fix (D104.4): made and tested, not yet live.** A
  tracker-order skip no longer fails the job. It goes live at the next
  redeploy (session 111), with the 49 airports.
- Stages D, E, F and H follow stage G.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **GRIB cache.** On an external drive (D102.3).

---

## Open questions (live)

- F153's readings (F153.9), for the owner. In particular: with 49 airports
  configured, `scripts/session109_gates.py` and `python -m mlwx.refit`
  with no airport list stop at a new airport (F153.9(2)); and the model
  asset is now 1.25 GB (F153.9(3)); the workflow expects the asset name
  `gfs-models.tar` (F153.9(8)).

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

**Next planning session:** Review session 110 and commit; then plan session 111: the owner uploads `gfs-models-49.tar` under tag `gfs-models-49`, sets `MLWX_COMMIT` to session 110's commit and `MODELS_TAG` in MLwx-live's workflow and copies the template's comment fix; Claude Code checks the live runs; decide a pre-registered test of the live forecasts (window from 12 October 2026, handling of v17 rows, locked before any 2026-27 scoring including stage B's), whether to save an observation snapshot alongside the log, and whether to add cron times.
