# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 5 October 2026, after session 94._

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
every month but 2022-11 is published on the Release (F135), and the pull has a
whole-file fallback for 2022-11's broken files (D86, F136). Then stages D to
H. New airports are an ongoing track, and pooling is conditional.

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
- **The pull (F133, F134, F135, F136).** `scripts/session91_grib_pull.py`,
  `data/processed/session91_pull_airports.csv` and
  `.github/workflows/stagec-grib-pull.yml`, with the verify step
  (`scripts/session92_verify_chunk.py`, D84.4). **The Release
  `stagec-grib-pull-v1` holds 192 assets: three files for each of the 65
  planned months except 2022-11** (F135.2). Only 2022-01 has been downloaded and checked locally
  (F134); the other months are not yet downloaded or checked.
- **2022-11 (D86, F136).** 27 GRIB files in cycles 2022-11-29T18,
  2022-11-30T00 and 2022-11-30T06 have `.idx` files that do not match them
  (F135); the Google Cloud mirror holds the same files. The owner chose to
  recover them (D86.2). The pull script now has a whole-file fallback: when a
  byte range still gives a broken body after its retries, it downloads the
  whole file, walks its GRIB headers, and takes every planned field from the
  one message that passes session 91's own check, with the status "ok (whole
  file)". The verifier accepts that status and prints its count. The gate
  passed (F136): the normal path is unchanged; on healthy files the fallback
  picks byte-identical messages; two broken files fall back by themselves with
  exactly one passing message per field. **2022-11 has not been run with the
  fallback.** New SHA-256: pull script `b52ffc2e...2f1f`, verifier
  `7b59a5c2...af6a`; the workflow is unchanged (`804b6d35...02a6`).
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

- **F136.8's readings.** The owner confirms or changes them. The largest: a
  broken body triggers the fallback only if the last of the six tries was a
  broken body; an "ok (whole file)" manifest row has an empty `idx_line` and
  gives the message's range within the whole file; the new status is added
  to session 91's status list, so the meta's "messages" line now lists five
  statuses.

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
- **Workflow wording (D85.1).** The workflow's header comment and the
  publish step's name still describe the old gating; cosmetic, left as is.
- **Laptop sleep (D86.5).** Long local sessions run with the laptop kept
  awake.
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

**Next planning session:** Review session 94. If it passed, the owner commits and pushes, runs 2022-11 alone on GitHub Actions and checks its verify step passed (D86.4); then plan the session that downloads and checks all 65 months. Re-check GFS v17 (D81.7).
