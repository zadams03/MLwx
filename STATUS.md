# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 29 September 2026, after session 85._

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
models are frozen (F122).**

- **Design (D73).** SPEC 8's `B+D,L,R,T`, unchanged, at all six airports.
  The test year 2026-08-01..2027-07-31 splits at the first operational GFS
  v17 cycle into period A (v16 inputs) and period B (v17 inputs,
  v16-trained model). Each period is judged separately against SPEC 5.3.
- **Hold rule (D73.8).** No 2026-27 value is scored until its period has
  ended and its observations are in. The condition that period A waits
  for, the owner's written decision on an NBM/MOS test on 2026-27, is now
  met by D77.6. Until each period is scored, its data is held out for
  claims (SPEC 2.5).
- **2026-27 NBM/MOS test (D77.6), pre-registered.** The frozen F122
  `B+D,L,R,T` models against NBM at DSM, RNO and KSFO, and against GFS MOS
  (MAV) at DSM, per period; PASS if the model's MAE is lower. Separate from
  D73. Its scripts are written later, with D73.8's.

**Stage A: done except the direction decision.** Source probe (F123), ICON
route check (F124, D76.2: ICON is not saved), confidence intervals (F125),
and now the NBM/MOS comparison on the spent years (F127).

**F127, in brief (descriptive only; it changes no verdict).** All four
airport-looks passed the reproduction gate. MAE in degC, recorded
predictions, d = MAE(competitor) minus MAE(model) with its 95% interval:

| airport-look | competitor | n | model | competitor | raw GFS | d [95%] |
|---|---|---|---|---|---|---|
| DSM 2024-25 | NBM | 365 | 1.4123 | 1.2196 | 1.7043 | -0.193 [-0.308, -0.051] |
| RNO 2024-25 | NBM | 365 | 1.2742 | 1.3192 | 1.6135 | +0.045 [-0.060, +0.156] |
| KSFO A 2024-25 | NBM | 364 | 1.2576 | 1.0000 | 1.4263 | -0.258 [-0.382, -0.131] |
| KSFO B 2025-26 | NBM | 365 | 1.3830 | 1.3023 | 1.7321 | -0.081 [-0.220, +0.044] |
| DSM 2024-25 | MAV | 365 | 1.4123 | 1.5773 | 1.7043 | +0.165 [+0.017, +0.332] |

**Band under D77.4: MIXED** (the model beats NBM at RNO only). The model
beats MAV at DSM (not part of the band). KSFO carries D71.5's framing.

---

## Open questions (live)

None. The planning-chat corrections after review (NBM version dates,
NAM MOS wording, the start-hour question) are recorded in F127.

---

## Carried items

- **Direction decision (D77.4).** F127's band is mixed. The owner chooses
  in writing, before stage C's lock: (a) bring a US-only stacking check
  (NBM as an input) forward from stage E; (b) weight the roadmap towards
  non-US airports; (c) both; or (d) neither, with reasons.
- **GFS v17 (D77.8).** Still no Service Change Notice as of 2026-09-29.
  Re-check at each planning session. The go-live date sets period A's
  length. PNS 26-30's statement that the 0.25 degree GRIB2 files remain is
  to be confirmed against the SCN (D73.4).
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

**Next planning session:** Review session 85. If F127's band is mixed or lose, the owner records the direction decision (D77.4). Then design session 86: the next step in stage B or C (the 2026-27 data-build and scoring scripts, or stage C's start).
