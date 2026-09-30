# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 30 September 2026, after session 86._

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
models are frozen (F122), and its data-build script exists and passed
its gate (F128).**

- **Design (D73).** SPEC 8's `B+D,L,R,T`, unchanged, at all six airports.
  The test year 2026-08-01..2027-07-31 splits at the first operational GFS
  v17 cycle into period A (v16 inputs) and period B (v17 inputs,
  v16-trained model). Each period is judged separately against SPEC 5.3.
- **Hold rule (D73.8).** No 2026-27 value is scored until its period has
  ended and its observations are in. The owner's written decision on an
  NBM/MOS test on 2026-27 is D77.6. Until each period is scored, its data
  is held out for claims (SPEC 2.5).
- **2026-27 NBM/MOS test (D77.6), pre-registered.** The frozen F122
  models against NBM at DSM, RNO and KSFO, and against GFS MOS (MAV) at
  DSM, per period. Separate from D73.
- **Build script (F128).** `scripts/session86_forward_build.py`. Its gate
  rebuilt 54 spent-year station-days (9 dates, 6 airports) from fresh
  GRIB and IEM pulls: every value equals the committed training set
  exactly (12 columns, 54 of 54 each), and the frozen models predict
  identically on committed and rebuilt rows (difference 0). Its `--build`
  mode (period A only) is written and has never been run. It runs only
  after period A has ended and its observations are in, with the first
  v17 cycle taken from a DECISIONS entry (D78.7).
- **Next scripts (D78.7).** Session 87: the scoring script and D77.6's
  NBM and MAV fetch. Both scripts are committed before any 2026-27 row
  is built (D73.8).

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2:
ICON is not saved), confidence intervals (F125), NBM/MOS comparison on
the spent years (F127, band MIXED), and the direction decision (D78.1).

---

## Open questions (live)

None.

---

## Carried items

- **GFS v17 (D78.5).** Still no Service Change Notice as of 2026-09-29.
  Re-check at each planning session. The go-live date sets period A's
  length. PNS 26-30's statement that the 0.25 degree GRIB2 files remain is
  to be confirmed against the SCN (D73.4).
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

**Next planning session:** Review session 86. Then design session 87: the 2026-27 scoring script and D77.6's NBM and MAV fetch (D78.7). Re-check GFS v17 (D78.5).
