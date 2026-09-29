# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 28 September 2026, after session 82._

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

**Stage A: the read-only source probe is done (F123).** Nothing was
chosen.

| source | class | all SPEC 8 fields? |
|---|---|---|
| ECMWF IFS open data | Shallow (2023-01-18; 0.25° from 2024-02-01) | only from 2025-11-21 (cloud cover) |
| ECMWF AIFS Single | Shallow (2025-02-10) | yes |
| DWD ICON global | **No archive** (about 24 h) | yes, by listing |
| NOAA GEFS | Deep (2017-01-01; v12 from 2020-09-23) | yes (850 hPa at 0.5° only) |
| Google WeatherNext | **Blocked** (Google account and request form) | WN3 yes, per documentation |
| NOAA NBM (CONUS) | Deep (2020-05-18) | no 850 hPa, no pressure |
| NWS MOS (IEM archive) | Deep (GFS MOS 2003; NBS 2020-07-23) | temperature, dewpoint, wind, sky only |
| Open-Meteo Previous Runs | Shallow (2024; AIFS 2025-02-18) | no 850 hPa at any offset; no GEFS |
| GFS v17 retrospective runs | none found public | — |

- **No archive (input to session 83):** DWD ICON global.
- **Blocked:** Google WeatherNext.
- **For the NBM/MOS rule (D72.7):** GFS MOS, NAM MOS and NBS have no
  20:00 UTC projection, which is the target hour at RNO and KSFO. DSM's
  18:00 UTC is covered (F123.4).

---

## Open questions (live)

None.

---

## Carried items

- **GFS v17 (D74.4).** Still no Service Change Notice as of 2026-09-28
  (planning-chat search, not checked by session 82). The SCN is due 30 days
  before go-live, so the earliest go-live is about late October 2026.
  Re-check at each planning session. The go-live date sets period A's
  length.
- PNS 26-30 (read by the planning chat, F123): the v17 proposal keeps the
  0.25 degree GFS GRIB2 files. Confirm against the SCN when it appears
  (D73.4).
- **Stage A/B uncertainties.**
  - Closed by F123: each probed source's archive depth, live feed and
    fields. Whether GFS v17 retrospective runs are public: none found as of
    2026-09-28 (F123.6; not proven absent).
  - Still open:
    - the v17 go-live date;
    - whether a comparison against NBM/NWS MOS is pre-registered on
      2026-27 (D73.8, D72.7);
    - where and whether to save ICON (D72.8);
    - retention periods not measured (WeatherNext; ICON beyond DWD's
      statement);
    - model-version histories marked unknown in F123.3;
    - the NBM v4.3 date disagreement between two NOAA pages.

---

## Next

**Next planning session:** Review session 82. Then draft session 83: daily
collection for any source F123 classes as no-archive; if there is none,
stage A's benchmark.
