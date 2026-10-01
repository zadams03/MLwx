# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 30 September 2026, after session 87._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0, 7.5, 8.7;
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six airports (D71.1).

**The roadmap is set (D72; SPEC 6).** Stages A (benchmark and source
probe) and B (forward test and data collection) run side by side. Then
come stages C to H. New airports are an ongoing track, and pooling is
conditional.

**Direction decision (D78.1): option (d), neither.** The roadmap carries
on as D72 sets it.

**Stage B: the 2026-27 GFS forward test is pre-registered (D73), its
models are frozen (F122), and all three 2026-27 scripts exist and passed
their gates (F128, F129).**

- **Design (D73).** SPEC 8's `B+D,L,R,T`, unchanged, at all six airports.
  The test year 2026-08-01..2027-07-31 splits at the first operational GFS
  v17 cycle into period A (v16 inputs) and period B (v17 inputs,
  v16-trained model). Each period is judged separately against SPEC 5.3.
- **Hold rule (D73.8).** No 2026-27 value is scored until its period has
  ended and its observations are in. Until each period is scored, its data
  is held out for claims (SPEC 2.5).
- **2026-27 NBM/MOS test (D77.6), pre-registered.** The frozen F122
  models against NBM at DSM, RNO and KSFO, and against GFS MOS (MAV) at
  DSM, per period. Separate from D73. D79 fixes how both tests are
  reported: margin as a percentage with the difference beside it (D79.1),
  an equal MAE is a fail (D79.2), "no verdict (0 days)" (D79.3), season
  labels (D79.4), intervals with seed 87 (D79.5).
- **The three scripts.** Each 2026-27 mode runs only after its period has
  ended and its observations are in, in this order: build, fetch, score.
  The first operational v17 cycle and the NBM and MAV version labels come
  from DECISIONS entries written first.
  1. Build: `scripts/session86_forward_build.py --build` (period A only;
     gate passed, F128). Never run.
  2. Fetch: `scripts/session87_forward_competitors.py --fetch` (NBM at
     DSM, RNO, KSFO; MAV at DSM; gate passed, 21 of 21 NBM and 5 of 5 MAV
     values equal, F129.4). Never run.
  3. Score: `scripts/session87_forward_score.py --score` (D73 and D77.6;
     gate reproduced F119.3 and F127.4 exactly, F129.5). Never run. It
     needs the rows file's and points file's SHA-256 from the build and
     fetch findings, and the version text from a DECISIONS entry (D79.4).
     Period A's NBM label must name v5.0.15 (D78.6).
  Period B needs a later build mode and D73.4's v17 entry first (D79.6).
  Its arguments and outputs are in F128.6 and F129.6.

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2:
ICON is not saved), confidence intervals (F125), NBM/MOS comparison on
the spent years (F127, band MIXED), and the direction decision (D78.1).

---

## Open questions (live)

- **F129.8's readings.** Eight readings were made where session 87's prompt
  was silent (timing guard over all six airports; no draws for a void or
  short comparison; a zero-row airport is "no verdict (0 days)"; the
  season label; the persistence margin's day basis; file names; MAV
  projection handling; no size trial in `--fetch`). The owner confirms or
  changes them before period A is run.

---

## Carried items

- **GFS v17 (D79.7).** Still no Service Change Notice as of 2026-09-30
  (planning-chat search; the newest SCN listed is SCN 26-87). Re-check at
  each planning session. The go-live date sets period A's length. PNS
  26-30's statement that the 0.25 degree GRIB2 files remain is to be
  confirmed against the SCN (D73.4).
- **Open item D78.2 (bias drift).** A correction that adapts to recent
  bias is a candidate build choice for stage C, tested by time-ordered
  cross-validation, identically at every airport. Nothing is decided.
- **Open item D78.3 (non-US competitors).** Before stage C's new airports
  are chosen: a read-only probe of non-US post-processed station
  forecasts (for example DWD's MOSMIX). Nothing is decided.
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - how complete Open-Meteo's Single Runs archive is for `icon_global`
    (one missing 18z run found; not scanned), and the timing at hours
    18 to 23 (F124.2; kept open for stage D by D76.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement);
  - model-version histories marked unknown in F123.3;
  - whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent).

---

## Next

**Next planning session:** Review session 87. Then choose the next step while period A runs: open stage C, or run D78.3's non-US competitor probe first. Re-check GFS v17 (D79.7).
