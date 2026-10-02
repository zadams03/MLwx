# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 1 October 2026, after session 88._

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
their gates (F128, F129). They are unchanged this session.**

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
  reported. **F129.8's eight readings are accepted (D80.1)**; neither script
  changes, and F129.7's SHA-256 values stand.
- **The three scripts.** Each 2026-27 mode runs only after its period has
  ended and its observations are in, in this order: build, fetch, score.
  The first operational v17 cycle and the NBM and MAV version labels come
  from DECISIONS entries written first.
  1. Build: `scripts/session86_forward_build.py --build` (period A only;
     gate passed, F128). Never run.
  2. Fetch: `scripts/session87_forward_competitors.py --fetch` (gate
     passed, F129.4). Never run.
  3. Score: `scripts/session87_forward_score.py --score` (gate passed,
     F129.5). Never run. It needs the rows file's and points file's SHA-256
     from the build and fetch findings, and the version text from a
     DECISIONS entry (D79.4). Period A's NBM label must name v5.0.15
     (D78.6).
  Period B needs a later build mode and D73.4's v17 entry first (D79.6).
  Its arguments and outputs are in F128.6 and F129.6.

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2:
ICON is not saved), confidence intervals (F125), NBM/MOS comparison on
the spent years (F127, band MIXED), and the direction decision (D78.1).

**Non-US competitor probe (D78.3, D80.3): done, session 88 (F130).**
Read only; nothing was chosen.
- **DWD MOSMIX keeps only about two days on DWD's server and has no public
  archive: class No archive.** MOSMIX_L all-stations holds 8 issues (03,
  09, 15, 21 UTC; span 42 h), MOSMIX_S 48 hourly issues. DWD states no
  retention period anywhere read. The prompt's six-hour second listing was
  not possible this session (two listings 13 minutes apart, identical).
  PAMORE holds NWP forecasts for about 1.5 years under registration for
  research and authorities, and does not name MOSMIX. Other holders are
  named only by secondary sources.
- **Stations.** LFPG 07157 (0.17 km) and the US airports DSM, RNO, KSFO have
  main stations. EGLC's station P0478 is an interpolation station, 7.7 km
  from IEM's position. YSDU (Dubbo) has no MOSMIX station within 10 km
  (nearest 221.75 km).
- **Other products.** BoM town forecasts at Dubbo: daily minimum and
  maximum only, no archive. Met Office site-specific: blocked (account and
  API key).
- **The save decision (D80.5) is open.** Options A, B and C stand as D80.5
  wrote them. Nothing is decided, and no saver exists.

---

## Open questions (live)

- **D80.5, MOSMIX daily saves.** The owner chooses between no saving,
  single-station files at a short list (EGLC, LFPG and YSDU now, stage C's
  candidate airports later) or the whole map, and where a saver would run.
  A saver is new code and needs its own session. Every day without one
  is a day of MOSMIX history lost.
- **F130.9's readings.** Four readings were made where session 88's prompt
  was silent (the tag for the MOSMIX rows; "main" station means a `+` in the
  TTT symbol; the timing table uses a past day; some terms read through
  search and fetch tools). The owner confirms or changes them.
- **F130.8, repeated download.** The helper script downloaded the same
  MOSMIX_S file three times (about 112 MB). The owner notes it.

---

## Carried items

- **GFS v17 (D80.6).** Still no Service Change Notice as of 2026-10-01
  (planning-chat search; the newest SCN listed is SCN 26-87, 2026-09-22).
  The earliest go-live is about 31 October 2026. Re-check at each planning
  session. The go-live date sets period A's length. PNS 26-30's statement
  that the 0.25 degree GRIB2 files remain is to be confirmed against the
  SCN (D73.4).
- **Open item D78.2 (bias drift).** A correction that adapts to recent
  bias is a candidate build choice for stage C, tested by time-ordered
  cross-validation, identically at every airport. Nothing is decided.
- **MOSMIX matching and fairness (D80.4).** Any matching rule for a MOSMIX
  comparison is the owner's later decision. F130.5 records that MOSMIX uses
  current station observations as predictors, and the leads and model runs
  of each issue.
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - how complete Open-Meteo's Single Runs archive is for `icon_global`
    (one missing 18z run found; not scanned), and the timing at hours
    18 to 23 (F124.2; kept open for stage D by D76.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement). MOSMIX's is now measured from listings (F130.2);
  - model-version histories marked unknown in F123.3 (MOSMIX's is now
    listed, F130.6);
  - whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent);
  - whether MOSMIX appears in PAMORE, and whether any third party holds
    past MOSMIX issues (F130.2; unknown).

---

## Next

**Next planning session:** Review session 88. Then decide on MOSMIX daily saves (D80.5) and, if any, plan the saver session; otherwise open stage C. Re-check GFS v17 (D80.6).
