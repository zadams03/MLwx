# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 4 October 2026, after session 92._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0, 7.5, 8.7;
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six development airports (D71.1).

**The end goal (D82.2).** A private, live tool for ten or more airports
that corrects every GFS run (four a day), as each run arrives, into an
hourly temperature curve out to the forecast horizon, plus the daily
maximum. The horizon is 24 hours first and 48 hours later. Then a choice of
which weather model is corrected, plus a blend, and probabilistic ranges.

**The roadmap (D72; SPEC 6).** Stage A is done. Stage B runs. Stage C is
open: its design is set (D82, D83), its GRIB pull is built and gated (F133),
and its first month is published and verified (F134). Then stages D to H.
New airports are an ongoing track, and pooling is conditional.

**Stage B: the 2026-27 GFS forward test (D73, F122, D77.6, D79), unchanged.**
It is pre-registered, its models are frozen, and all three 2026-27 scripts
exist and passed their gates (F128, F129). **None has been run.** Order, per
period, after the period ends and its observations are in: build
(`scripts/session86_forward_build.py --build`), fetch
(`scripts/session87_forward_competitors.py --fetch`), score
(`scripts/session87_forward_score.py --score`). The first operational v17
cycle and the NBM and MAV version labels come from DECISIONS entries written
first (D79.4; period A's NBM label must name v5.0.15, D78.6). Period B needs a
later build mode and D73.4's v17 entry. Arguments and outputs are in F128.6
and F129.6. The hold rule (D73.8) stands: no 2026-27 value is scored before
its period has ended.

**MOSMIX (D81.2 to D81.5).** Daily saves of MOSMIX_L single-station files,
all four issues, at EGLC (P0478), LFPG (07157), DSM (72546), RNO (72488) and
KSFO (72494), run on GitHub Actions and committed to a separate private
repository. **The saver session has not been run and no saver exists.** Days
before it starts are lost, which is accepted. No MOSMIX test is
pre-registered. F132 records which airports have a MOSMIX station within 10
km; the saver session decides whether the list grows.

**Stage C.**
- **Design (D82.3 to D82.8, D83.2 to D83.5).** Every GFS cycle, forecast
  hours 0 to 24 first (25 to 48 later, by an additive pull with the same
  script, starting at cycle 2021-03-22T12, the first GFS v16 run, D84.2).
  Raw values at the four grid points around each airport, ten fields,
  2021-03-24T00 to 2026-07-31T23 UTC only, by monthly chunk on GitHub
  Actions, published as Release files. The pull list is 51 airports (D82.6's
  47 plus LFPG, DSM, YSDU, RNO); development airports at SPEC 3.4's grid
  point, the others at IEM's position. Daily maximum: local day, 22 of 24
  usable hours.
- **The pull (F133, F134).** `scripts/session91_grib_pull.py`,
  `data/processed/session91_pull_airports.csv` and
  `.github/workflows/stagec-grib-pull.yml`. F133's readings are accepted
  (D84.1). **Month 2022-01 is published** on the Release
  `stagec-grib-pull-v1` (run on Actions, 8 min 25 s, D84.3) **and verified**
  (F134): the files equal the Release and the meta, all 13 checks pass, and
  the extended gate passed 93 of 93 station-days at EGLC, LFPG and DSM,
  exact equality (the first check that Actions' Linux ecCodes decodes as the
  Mac did). The lead-26 airports are not gated by an f000 to f024 extract.
- **The verify step (D84.4).** `scripts/session92_verify_chunk.py` now runs
  in the workflow after each month's pull and before upload; a failing month
  publishes nothing and is retried by starting the run again. "idx missing"
  messages do not fail a month; their count is printed. The step has not yet
  run on Actions.
- **Estimates (F134.5, from 2022-01).** About 8 min a month on Actions;
  about 2.2 h for the remaining 64 months at four at once; about 1.69 TB
  downloaded and about 1.30 GB kept in all; 195 Release assets when
  complete.
- **Claim batch (D82.7, F132): EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN.**
  Held-out window 2024-08-01..2026-07-31; looks fixed at stage C's lock.
- **Not decided (D82.5).** One model with lead time as an input or one per
  lead; the daily maximum read off the curve or its own model; stage C's
  claim design (bar, looks, lead bands). Fixed by time-ordered
  cross-validation on the development airports, or at the lock. Bias drift
  follows D81.10(b).
- **Open item: MMMX (D83.4).** It reports at scattered minutes, so it has
  almost no usable observations under the 15-minute rule. It needs its own
  handling or to be dropped (a later decision). It stays in the pull.

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2),
confidence intervals (F125), NBM/MOS comparison (F127, band MIXED),
direction decision (D78.1, option (d)).

---

## Open questions (live)

- **F134.7's readings.** The owner confirms or changes them. The largest:
  two checks beyond D84.4's list ("layout" and "statuses", both failing a
  month); the extended gate as a local-only `--gate` option of the
  verifier; the speed projection's method; the workflow's header comment
  and publish-step name left unchanged, so they do not mention the verify
  step.

---

## Carried items

- **GFS v17 (D84.6).** As of 2026-10-04 (planning-chat check) no GFS v17
  Service Change Notice was found. EMC's GFSv17 evaluation page (last updated
  5 June 2026) gives the implementation as Q1 FY27 (October to December
  2026). With 30 days' notice the earliest go-live is about 3 November 2026.
  Re-check at each planning session. The go-live date sets period A's
  length. PNS 26-30's statement that the 0.25 degree GRIB2 files remain is
  to be confirmed against the SCN (D73.4).
- **EGLC position note (D81.6).** DWD's cfg places P0478 west of the
  airport; F132.5 confirms the station is 7.69 km away as listed and 2.47 km
  with the sign flipped. This matters only for a later MOSMIX comparison.
- **MOSMIX matching and fairness (D80.4).** Any matching rule for a MOSMIX
  comparison is the owner's later decision. MOSMIX uses current station
  observations as predictors (F130.5).
- **Open item D78.2 (bias drift).** A correction that adapts to recent bias
  is a candidate build choice for stage C, tested by time-ordered
  cross-validation, identically at every airport. Nothing is decided.
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - how complete Open-Meteo's Single Runs archive is for `icon_global`, and
    the timing at hours 18 to 23 (F124.2; kept open for stage D by D76.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement);
  - model-version histories marked unknown in F123.3;
  - whether GFS v17 retrospective runs are public (none found as of
    2026-09-28, F123.6);
  - whether MOSMIX appears in PAMORE, and whether any third party holds past
    MOSMIX issues (F130.2).

---

## Next

**Next planning session:** Review session 92 and the extended gate. If it passed, the owner commits and pushes, runs 2021-03 alone on GitHub Actions and checks its verify step passed (D84.5), then starts 2021-04..2026-07; then plan the session that downloads and checks all 65 months. Re-check GFS v17 (D81.7).
