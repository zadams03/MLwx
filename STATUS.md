# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 27 September 2026, after session 80._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). F109 stands.**

**A sixth airport, San Francisco International (KSFO), passes the
selected-features method on both of its pre-registered looks (F119). The
owner accepted this as a PASS (D71).**

- **Headline (D71.2):** look A's margin over raw GFS (GRIB), 1.2576 vs
  1.4263 °C, +11.83%. Look B's +20.16% over raw GFS is always quoted with
  D71.3: look B's raw-GFS year was unusually poor, and persistence was the
  binding half of the bar there (+19.46%).
- **Framing (D71.5), carried by every write-up.** KSFO's result is for the
  recipe at a sea-mixed grid point (37.5% sea weight). It is not directly
  comparable with the five earlier airports, whose reproduction gates
  passed. KSFO's gate is recorded as failed, explained by a difference
  between the sources. Look B's training includes 2024-25, by design.
  KSFO's margins are not added to F109's five-airport table or its +6.02%
  average.
- **No untouched held-out year remains at any of the six airports**
  (D71.1).

**The roadmap is set (D72; SPEC 6).** The end goal is a private, live
daily tool for ten or more airports (D72.1). Claims and build choices are
treated differently (D72.2, SPEC 2.5). Stages, in order (A and B side by
side):

- **A — benchmark and source probe:** confidence intervals, a comparison
  against NWS MOS and NBM, and a read-only probe of other sources.
- **B — forward test and data collection:** pre-register the 2026-27 GFS
  forward test, split at the v17 go-live date; save daily forecasts from
  any source with no downloadable archive.
- **C — widen the target, on GFS only:** hourly curve, daily maximum,
  48-hour lead.
- **D — correct each other weather model on its own.**
- **E — blend and stack** the corrected models.
- **F — upgrade policy** for weather-model version changes.
- **G — live product, version 1.**
- **H — probabilistic forecasts.**
- **Ongoing:** new airports, in batches. **Conditional:** pooling.

---

## Open questions (live)

None. Q30 and Q32 are closed (D72.9).

---

## Carried items

- **GFS v17 (D72.11).** No GFS v17 Service Change Notice was found as of
  2026-09-27 (planning-chat web search, not checked by session 80); only
  the April 2026 proposals (PNS 26-29, 26-30). Re-check at each planning
  session. The earliest possible go-live is late October 2026 (D69.6).
- **Uncertainties that stages A and B will answer:** other sources'
  archive depth and fields; whether GFS v17 retrospective runs are
  public; the v17 go-live date, which sets period A's length (D72.5).

---

## Next

**Next planning session:** Review session 80. Then draft session 81:
pre-register the 2026-27 GFS forward test and train and freeze its model
(D72.5, D72.13).
