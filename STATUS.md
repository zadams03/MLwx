# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 3 October 2026, after session 90._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0, 7.5, 8.7;
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six development airports (D71.1).

**The end goal (D82.2, reworded).** A private, live tool for ten or more
airports that corrects every GFS run (four a day), as each run arrives, into
an hourly temperature curve out to the forecast horizon, plus the daily
maximum. The horizon is 24 hours first and 48 hours later. Then a choice of
which weather model is corrected, plus a blend, and probabilistic ranges.

**The roadmap (D72; SPEC 6).** Stage A is done. Stage B runs. Stage C is
open and its design is set (D82). Then stages D to H. New airports are an
ongoing track, and pooling is conditional.

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

**MOSMIX (D81.2 to D81.5).** Daily saves of MOSMIX_L single-station files, all
four issues, at EGLC (P0478), LFPG (07157), DSM (72546), RNO (72488) and KSFO
(72494), run on GitHub Actions and committed to a separate private repository.
**The saver session has not been run and no saver exists.** Days before it
starts are lost, which is accepted. No MOSMIX test is pre-registered. F132
records which of the 47 airports have a MOSMIX station within 10 km (37); the
saver session decides whether the list grows.

**Stage C: design set (D82).**
- **Target and horizon (D82.3).** Every GFS cycle (00, 06, 12, 18 UTC), every
  forecast hour 0 to 24 first. Hours 25 to 48 come later, by a separate
  additive pull. The daily maximum is part of the target.
- **Data route (D82.4).** NOAA GFS GRIB on `noaa-gfs-bdp-pds`, fetched by byte
  range, on GitHub Actions in the public repository, as resumable chunks. Raw
  values at the four grid points around each airport are kept (the record's
  eight fields plus GFS 2 m maximum and minimum temperature); no global field
  is kept. Period 2021-03-24 to 2026-07-31 only. Kept files go to GitHub
  Release files. Gate: at each existing airport's target hour, cycle and lead,
  the new values equal the committed ones. Session 91 builds it.
- **Airports (D82.6).** The owner's 47. Build choices use the six development
  airports only; the 45 new ones stay clean.
- **Daily maximum (D82.8).** Local calendar day, 22 of 24 usable hours.
- **Claim batch (D82.7, F132): EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN.** Drawn
  once, by the rule written first (seed 20261003). Held-out window of each:
  2024-08-01..2026-07-31. Their looks are fixed at stage C's lock. ZGSZ, CYYZ
  and NZWN have sea in their GFS grid box (a flag only). Five airports were
  ineligible on observation coverage: MMMX, OPKC, VILK, RCSS, FACT.
- **Not decided (D82.5).** One model with lead time as an input or one per
  lead; the daily maximum read off the curve or its own model; stage C's claim
  design (bar, looks, lead bands). Fixed by time-ordered cross-validation on
  the development airports, or at the lock, before any claim airport's
  held-out data is read. Stage C's SPEC section is written at its lock. Bias
  drift follows D81.10(b).

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2: ICON is
not saved), confidence intervals (F125), NBM/MOS comparison on the spent years
(F127, band MIXED), direction decision (D78.1, option (d)). F131 (session 89's
scoping probe) is accepted (D82.1).

---

## Open questions (live)

- **F132.8's readings.** The owner confirms or changes them. The largest: the
  grid box is at IEM's airport position; a local day's end is its last minute;
  the held-out window is by local date; `--collect` was run twice after a bug
  in half-hour time zones was fixed (no other airport changed).

---

## Carried items

- **GFS v17 (D81.7).** Still no Service Change Notice as of 2026-10-02
  (planning-chat check; the newest SCN listed is SCN 26-87, 2026-09-22). With
  30 days' notice the earliest go-live is about 1 November 2026. Re-check at
  each planning session. The go-live date sets period A's length. PNS 26-30's
  statement that the 0.25 degree GRIB2 files remain is to be confirmed against
  the SCN (D73.4).
- **EGLC position note (D81.6).** DWD's cfg places P0478 at 0 deg 03 min W; the
  airport is at about 0 deg 03 min E. F132.5 confirms it: the station is 7.69
  km from the airport as listed and 2.47 km with the sign flipped. It is the
  only one of the 47 airports flagged. This matters only for a later MOSMIX
  comparison at EGLC.
- **MOSMIX matching and fairness (D80.4).** Any matching rule for a MOSMIX
  comparison is the owner's later decision. F130.5 records that MOSMIX uses
  current station observations as predictors.
- **Open item D78.2 (bias drift).** A correction that adapts to recent bias is
  a candidate build choice for stage C, tested by time-ordered cross-validation,
  identically at every airport. Nothing is decided.
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - how complete Open-Meteo's Single Runs archive is for `icon_global` (one
    missing 18z run found; not scanned), and the timing at hours 18 to 23
    (F124.2; kept open for stage D by D76.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement). MOSMIX's is measured from listings (F130.2);
  - model-version histories marked unknown in F123.3 (MOSMIX's is listed,
    F130.6);
  - whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent);
  - whether MOSMIX appears in PAMORE, and whether any third party holds past
    MOSMIX issues (F130.2; unknown).

---

## Next

**Next planning session:** Review session 90 and the claim batch. Then plan session 91: build the GitHub Actions GRIB pull and its local test chunk (D82.4, D82.10). Re-check GFS v17 (D81.7).
