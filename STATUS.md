# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 27 September 2026, after session 79._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (D59.2). F109
stands.**

**A sixth airport, San Francisco International (KSFO), passes the
selected-features method on both of its pre-registered looks (F119). The
owner accepted this as a PASS (D71).** SPEC (1, 3.4, 6, 8.5, 8.6(f)) and
RESULTS (6.5) now carry it (F120).

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

---

## Open questions (live)

- **Q30 (open).** The owner's order (D66.1): Q33 (done, F115); a further
  airport under the frozen recipe (KSFO — done, D71.7); then a dedicated
  roadmap planning session, which is next. Pooling is deferred. The
  2026-27 forward test is deferred until the GFS v17 date is known (D66.2,
  D71.8). If a 2026-27 test is ever pre-registered, it must name the two
  tracked DSM files for 2026-08-05..2026-08-15 (D62.7, A67-15).
- **Q32 (unchanged).** Whether a failed sealed test (Reno, minimal method,
  F82) changes the owner's intentions for future terrain-hard airports
  generally.

No other open question is live.

---

## Carried items

- **GFS v17.** Re-check the NWS notice list at each planning session
  (D66.2, D71.8). As of 2026-09-27 (planning-chat research, not checked by
  session 79) no GFS v17 Service Change Notice is listed; the latest SCN is
  still SCN26-87 (22 Sep 2026). The earliest possible go-live is late
  October 2026 (D69.6).
- **Roadmap planning inputs:** P1–P3, Q30 (2026-27, pooling), Q32, SPEC
  5.4, RESULTS §7 terrain descriptor, SPEC stages 4–6, GFS v17 (D66.2,
  D71.8), and KSFO's bias finding: its mean bias changed sign between
  years (D71.4).
- **Archive pointers.** DECISIONS-archive.md's header still says a pointer
  is left in DECISIONS.md for each moved section; sessions 77–79 left
  none. Owner to decide which to keep.

---

## Next

**Next planning session:** Review session 79. Then hold the dedicated
roadmap planning session (D66.1, D71.7), using the roadmap planning inputs
listed above.
