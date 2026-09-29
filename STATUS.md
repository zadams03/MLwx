# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 29 September 2026, after session 84._

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

**ICON decision (D76.2).** The project does not save ICON: 850 hPa
temperature is present in Open-Meteo's Single Runs from 2026-04-02
(F124.2(b)), so D75.1's rule applies.

**Confidence intervals (F125), descriptive only; they change no verdict.**
All 17 airport-results passed the reproduction gate.
- Minimal method (F16 to F82): d over persistence above zero at all five;
  over raw GFS above zero at EGLC and LFPG, not at DSM, YSDU or RNO.
- Richer 5-feature (F94): over persistence above zero at all five; over
  raw GFS above zero at EGLC, LFPG and YSDU, not at DSM or RNO.
- Selected `B+D,L,R,T` (F109): above zero against both, at all five.
- KSFO (F119): above zero against both, in both looks.

**Session 84: GitHub readiness (D76, F126).** Done, read-only except for
the edits listed in F126.4. The audit of the tree and full history found
no secret and no real credential, no large-file problem (largest blob
11.8 MB), and 92 `/Users/` path occurrences in 31 tracked files (reported,
not edited, D76.5). The terms check found open terms at all three
committed sources (Open-Meteo CC BY 4.0, non-commercial free API; IEM
public domain; NOAA NODD open, credit requested). Edits: README.md
rewritten, RESULTS.md section 6.6 (F125's intervals), LICENSE (MIT),
four `.gitignore` lines, one CLAUDE.md rule (no em-dashes, D76.6). Owner-
approved corrections before commit: a README note that raw Open-Meteo JSON
is unchanged and processed files are derived, README training and held-out
windows with citations, RESULTS section 7's roadmap bullet brought up to
date, and SPEC 5.4 and SPEC 6's stage A bullet brought up to date (wording
only). The owner makes the repo public by hand, after review.

---

## Open questions (live)

None new this session. F125.1 is closed by D76.1.

---

## Carried items

- **GFS v17 (D76.7).** Still no Service Change Notice as of 2026-09-29.
  Re-check at each planning session. The go-live date sets period A's
  length. PNS 26-30's statement that the 0.25 degree GRIB2 files remain is
  to be confirmed against the SCN (D73.4).
- **Session 82's MOS near-miss (F123.9).** The owner's decision is
  deferred to the NBM/MOS outcome rule (D72.7, D73.8), now session 85
  (D76.3).
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - whether a comparison against NBM/NWS MOS is pre-registered on
    2026-27 (D73.8, D72.7);
  - how complete Open-Meteo's Single Runs archive is for `icon_global`
    (one missing 18z run found; not scanned), and the timing at hours
    18 to 23 (F124.2; kept open for stage D by D76.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement);
  - model-version histories marked unknown in F123.3;
  - the NBM v4.3 date disagreement between two NOAA pages;
  - whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent).

---

## Next

**Next planning session:** Review session 84. If the review is clean, the owner makes the repo public. Then design session 85: the NBM/MOS comparison and its outcome rule (D72.7), including the carried F123.9 decision and whether 2026-27 gets a pre-registered NBM/MOS test (D73.8).
