# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 2 October 2026, after session 89._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0, 7.5, 8.7;
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six airports (D71.1).

**The roadmap is set (D72; SPEC 6).** Stage A is done. Stage B runs. Stage C
is now opened (D81.9). Then come stages D to H. New airports are an ongoing
track, and pooling is conditional.

**Direction decision (D78.1): option (d), neither.** The roadmap carries
on as D72 sets it.

**Stage B: the 2026-27 GFS forward test is pre-registered (D73), its
models are frozen (F122), and all three 2026-27 scripts exist and passed
their gates (F128, F129). They are unchanged and have never been run.**

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
  reported. D80.1 accepted F129.8's readings.
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

**MOSMIX (F130, D81).** DWD's MOSMIX keeps only about two days of issues on
its server and has no public archive (F130). The owner chose option B
(D81.2): save MOSMIX_L single-station files, all four daily issues, unchanged,
at EGLC (P0478), LFPG (07157), DSM (72546), RNO (72488) and KSFO (72494).
YSDU has no station within 10 km and is not on the list (D81.3). The saver
runs on GitHub Actions and commits to a separate private repository (D81.4).
It is not urgent, and days before it starts are lost, which is accepted
(D81.5). **The saver session has not been run, and no saver exists.** No
MOSMIX test is pre-registered. Stage C's new airports are added to the list
when chosen, where a station exists.

**Stage C: opened (D81.9, D81.10).** Its claim is judged on new airports only,
chosen before its lock and not scored before it. It makes no claim on 2026-27.
Defaults: the daily-maximum definition is decided after F131; bias drift
(D78.2) is tested only after the curve's baseline exists, one change at a
time; new candidate airports are chosen in stage C's design session.

**F131 (session 89, read-only scoping probe): outcome in brief.** The data
route is still open (D81.11).
- **dynamical.org GFS forecast archive.** First init 2021-05-01 (39 of the
  record's first target days have no init); no missing inits to 2026-07-29;
  hourly leads to 120 h; values stored rounded (temperature 0.06 to 0.13 degC,
  PRMSL 0.64 hPa). It holds 4 of the 7 SPEC 8 fields in the same form
  (temperature, wind, radiation, pressure). Cloud cover is an average, not
  the record's instantaneous field. Dew point and 850 hPa temperature are
  absent. On a reduced sample (13 dates per airport), differences from the
  committed GRIB values are small (temperature 0.010 to 0.025 degC on average).
  A full point series would be about 10 GB per variable and spatial chunk;
  all six variables for the six airports about 346 GB and 229,920 reads.
- **GRIB route.** All 8 fields are present at every hour f024 to f053 in all
  four cycles. Estimate for both leads, 2021-03-24 to 2026-07-31: about
  954,528 requests and 695 GB (D81.11's planning figure: 470,000 requests and
  750 GB). Measured about 1.34 s per request, one connection.
- **Hourly observations** for all six airports are already committed (every
  hourly routine report). Daily-maximum sources: the METAR maximum groups
  cannot be counted from the committed files (no raw text); the official daily
  climate maxima and their day windows were not read (unknown).
- F131.9 lists the readings made where the prompt was silent. The largest:
  the first reproduction run hung and was killed, so the reproduction table
  uses every 5th monthly date (13 of 63).

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2:
ICON is not saved), confidence intervals (F125), NBM/MOS comparison on
the spent years (F127, band MIXED), and the direction decision (D78.1).

---

## Open questions (live)

- **F131.9's readings.** The owner confirms or changes them.
- **Stage C design (D81.9 to D81.11).** The data route, the daily-maximum
  definition and the new airports are the owner's, to be recorded in the next
  design session, from F131.

---

## Carried items

- **GFS v17 (D81.7).** Still no Service Change Notice as of 2026-10-02
  (planning-chat check; the newest SCN listed is SCN 26-87, 2026-09-22). With
  30 days' notice the earliest go-live is about 1 November 2026. Re-check at
  each planning session. The go-live date sets period A's length. PNS 26-30's
  statement that the 0.25 degree GRIB2 files remain is to be confirmed against
  the SCN (D73.4).
- **EGLC position note (D81.6).** DWD's cfg places P0478 at 0 deg 03 min W;
  the airport is at about 0 deg 03 min E. If DWD's sign is wrong, the station
  is about 2.5 km from the airport, not 7.7 km. This matters only for a later
  MOSMIX comparison at EGLC. F130 is unchanged. Not checked by a session.
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
    statement). MOSMIX's is measured from listings (F130.2);
  - model-version histories marked unknown in F123.3 (MOSMIX's is listed,
    F130.6);
  - whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent);
  - whether MOSMIX appears in PAMORE, and whether any third party holds
    past MOSMIX issues (F130.2; unknown).

---

## Next

**Next planning session:** Review session 89. Then design stage C from F131: the data route, the daily-maximum definition and the new airports, for the next session to record. Re-check GFS v17 (D81.7).
