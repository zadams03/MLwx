# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 27 September 2026, after session 81._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six airports (D71.1).

**The roadmap is set (D72; SPEC 6).** Stages A (benchmark and source
probe) and B (forward test and data collection) run side by side; then
C to H; new airports are ongoing; pooling is conditional.

**Stage B: the 2026-27 GFS forward test is pre-registered (D73), and its
models are frozen (F122).**

- **Design (D73).** SPEC 8's `B+D,L,R,T`, unchanged, at all six airports.
  The test year 2026-08-01..2027-07-31 splits at the first operational GFS
  v17 cycle: period A (v16 inputs) and period B (v17 inputs, v16-trained
  model), each judged separately against SPEC 5.3. Stated expectation:
  period A passes at all six airports; none for period B (D73.7).
- **Frozen (F122).** Per airport, one `B+D,L,R,T` model, one plain `B`
  model and one mean-bias constant, trained once on every row dated
  2021-03-24..2026-07-31, saved under `data/models/session81/` with
  their SHA-256 in `manifest.json` and F122. The new training code first
  reproduced F109's and KSFO look B's recorded MAEs exactly (12 of 12).
- **Hold rule (D73.8).** No 2026-27 value is scored until its period has
  ended and its observations are in. Period A is not scored until the
  owner has decided, in writing, whether to pre-register a comparison
  against NBM/NWS MOS on 2026-27 (stage A, D72.7). Until each period is
  scored, its data is held out for claims and no build choice may use it
  (SPEC 2.5). The 2026-27 data-build and scoring scripts are written in a
  later session and committed before any 2026-27 row is built.

---

## Open questions (live)

None.

---

## Carried items

- **GFS v17 (D73.12).** Still no Service Change Notice as of 2026-09-27
  (planning-chat web search, not checked by session 81); only the April
  2026 proposals (PNS 26-29, 26-30). The SCN is due 30 days before
  go-live, so the earliest go-live is about late October 2026. Re-check
  at each planning session. The go-live date sets period A's length.
- **Uncertainties that stages A and B will answer:** other sources'
  archive depth, live feed and fields; whether GFS v17 retrospective runs
  are public (D72.3, D73.9); the v17 go-live date; and whether a
  comparison against NBM/NWS MOS is pre-registered on 2026-27 (D73.8).

---

## Next

**Next planning session:** Review session 81. Then draft session 82:
stage A's read-only source probe (D72.13).
