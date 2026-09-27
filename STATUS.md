# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 27 September 2026, after session 78._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (D59.2). F109
stands.**

**A sixth airport, San Francisco International (KSFO), has had its two
pre-registered looks run, once, under the unchanged B+D,L,R,T recipe
(F119).** Both looks are spent and will not be repeated. The owner's
verdict on F119 is still to come.

- **Overall reading: PASS (both looks pass), as pre-registered ("pass in
  both years", D70.8).** B+D,L,R,T MAE against raw GFS (GRIB) and
  persistence:
  - look A (2024-25): 1.2576 vs 1.4263 (+11.83%) vs 1.5113 (+16.79%);
  - look B (2025-26): 1.3830 vs 1.7321 (+20.16%) vs 1.7172 (+19.46%).
- **Band read (secondary, D70.5):** both looks "beats B by more than the
  column-order spread" (margins 0.0958 and 0.0824 °C, band 0.0377).
- **Framing (D70.9), carried by any write-up.** KSFO's result is for the
  recipe at a sea-mixed grid point (37.5% sea weight, F117.3). It is not
  directly comparable with the five earlier airports, whose reproduction
  gates passed. KSFO's gate is recorded as failed, explained by a
  difference between the sources (D69). Look B's training includes
  2024-25, by design (D70.3).
- SPEC and RESULTS do not yet carry the KSFO result: SPEC still describes
  KSFO as "locked, not yet tested". That is for session 79.

---

## Open questions (live)

- **Q30 (open).** The owner's order (D66.1): Q33 (done, F115); a further
  airport under the frozen recipe (KSFO, D67; looks run, F119); then a
  dedicated roadmap planning session. Pooling is deferred. The 2026-27
  forward test is deferred until the GFS v17 date is known (D66.2, D67.8,
  D69.6). If a 2026-27 test is ever pre-registered, it must name the two
  tracked DSM files for 2026-08-05..2026-08-15 (D62.7, A67-15).
- **Q32 (unchanged).** Whether a failed sealed test (Reno, minimal method,
  F82) changes the owner's intentions for future terrain-hard airports
  generally.

No other open question is live.

---

## Carried items

- **GFS v17.** Re-check the NWS notice list at each planning session
  (D66.2, D67.8, D69.6). As of 2026-09-26 (planning-chat research) no
  Service Change Notice was listed; the latest SCN is still SCN26-87 (22
  Sep 2026), and the earliest possible go-live is late October 2026. KSFO
  is unaffected: all its data is v16.
- **Roadmap planning inputs** (carried from the last STATUS): P1–P3, Q30
  (2026-27, pooling), Q32, SPEC 5.4, RESULTS §7 terrain descriptor, SPEC
  stages 4–6, GFS v17 (D66.2, D67.8, D69.6).
- **SPEC wording left for the owner** (session 77 consistency check,
  `notes/session-77-review.txt`): B1–B5 (SPEC 1, 4.3, 5.0, 6 and 8.7
  describe one look per airport; KSFO has two, D67.3) and C1–C3 (SPEC 7
  intro, 7.2 and 5.2 statements scoped to the five earlier airports). Also
  E1: CLAUDE.md's "Commit discipline" says Claude Code writes the suggested
  commit message; the planning chat now writes `docs/commit-NN.txt`. Fix in
  the next session that edits SPEC or CLAUDE.md.

---

## Next

**Next planning session:** Review session 78 and decide the owner's verdict
on F119. Then plan session 79: record the verdict and fold KSFO into SPEC
and RESULTS (with the carried SPEC wording items B1–B5, C1–C3 and CLAUDE.md
E1). After that, hold the roadmap planning session (D66.1).
