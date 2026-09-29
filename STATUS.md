# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 29 September 2026, after session 83._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six airports (D71.1).

**The roadmap is set (D72; SPEC 6).** Stages A (benchmark and source
probe) and B (forward test and data collection) run side by side. Then
come stages C to H. New airports are an ongoing track, and pooling is
conditional.

**Stage B: the 2026-27 GFS forward test is pre-registered (D73), and its
models are frozen (F122).** Unchanged this session.

- **Design (D73).** SPEC 8's `B+D,L,R,T`, unchanged, at all six airports.
  The test year 2026-08-01..2027-07-31 splits at the first operational GFS
  v17 cycle into period A (v16 inputs) and period B (v17 inputs,
  v16-trained model). Each period is judged separately against SPEC 5.3.
- **Hold rule (D73.8).** No 2026-27 value is scored until its period has
  ended and its observations are in. Period A is not scored until the
  owner has decided, in writing, whether to pre-register a comparison
  against NBM/NWS MOS on 2026-27 (D72.7). Until each period is scored, its
  data is held out for claims (SPEC 2.5).

**Stage A: source probe done (F123); ICON route check done (F124);
confidence intervals done (F125).**

F123's sources, in brief:

| source | class | all SPEC 8 fields? |
|---|---|---|
| ECMWF IFS open data | Shallow (2023-01-18) | only from 2025-11-21 |
| ECMWF AIFS Single | Shallow (2025-02-10) | yes |
| DWD ICON global | No archive (about 24 h) | yes, by listing |
| NOAA GEFS | Deep (2017-01-01) | yes (850 hPa at 0.5° only) |
| Google WeatherNext | Blocked (account and form) | WN3 yes, per documentation |
| NOAA NBM (CONUS) | Deep (2020-05-18) | no 850 hPa, no pressure |
| NWS MOS (IEM archive) | Deep | temperature, dewpoint, wind, sky only |
| Open-Meteo Previous Runs | Shallow (2024) | no 850 hPa at any offset |

GFS MOS, NAM MOS and NBS have no 20:00 UTC projection (RNO, KSFO's target
hour); DSM's 18:00 UTC is covered (F123.4).

**ICON on Open-Meteo (F124), at EGLC:**
- (a) Past-run route: shortwave radiation at `previous_day1` starts at the
  same hour as temperature, 2024-01-19T12:00; `previous_day2` one day
  later.
- (b) Single Runs: `icon_global` from 2026-04-02 00z (2026-04-01 18z is
  "not available"), with 850 hPa temperature present (48 of 48 hours in
  both runs checked). All four cycles exist, but the 2026-06-10 18z run
  was "not available".
- (c) Timing: 18 of 24 hours match the GFS convention exactly (hours
  00–17); hours 18–23 could not be tested, because the 18z run was
  missing.
- **The ICON decision is the owner's, pending (D75.1).** Stated in
  advance: if 850 hPa temperature is present, the project does not save
  ICON; if absent, the owner chooses between saving ICON natively and
  using ICON without feature L.

**Confidence intervals (F125), descriptive only; they change no verdict.**
All 17 airport-results passed the reproduction gate.
- Minimal method (F16–F82): d over persistence above zero at all five;
  over raw GFS above zero at EGLC and LFPG, not at DSM, YSDU or RNO.
- Richer 5-feature (F94): over persistence above zero at all five; over
  raw GFS above zero at EGLC, LFPG and YSDU, not at DSM or RNO.
- Selected `B+D,L,R,T` (F109): above zero against both, at all five.
- KSFO (F119): above zero against both, in both looks.

---

## Open questions (live)

- **F125.1 (for review).** The session prompt's 3.2 says "from committed
  processed files only". The record code for the minimal method, F94 and
  F109 also reads committed raw files, read-only (Open-Meteo JSON and IEM
  chunks), as F122.3 did. Session 83 followed the record code. The owner
  confirms or rejects that reading.

---

## Carried items

- **GFS v17 (D75.4).** Still no Service Change Notice as of 2026-09-29.
  Re-check at each planning session. The go-live date sets period A's
  length. PNS 26-30's statement that the 0.25 degree GRIB2 files remain is
  to be confirmed against the SCN (D73.4).
- **Session 82's MOS near-miss (F123.9).** The owner's decision is
  deferred to the NBM/MOS outcome rule (D72.7, D73.8) and is taken when
  that rule is written (D75.3).
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - whether a comparison against NBM/NWS MOS is pre-registered on
    2026-27 (D73.8, D72.7);
  - where and whether to save ICON (D72.8; now the owner's decision from
    F124, D75.1);
  - how complete Open-Meteo's Single Runs archive is for `icon_global`
    (one missing 18z run found; not scanned), and the timing at hours
    18–23 (F124.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement);
  - model-version histories marked unknown in F123.3;
  - the NBM v4.3 date disagreement between two NOAA pages;
  - whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent).

---

## Next

**Next planning session:** Review session 83. Then the owner decides whether the project saves ICON, from F124 (D75.1). Then design session 84: the NBM/MOS comparison and its outcome rule (D72.7), including the carried F123.9 decision and whether 2026-27 gets a pre-registered NBM/MOS test (D73.8).
