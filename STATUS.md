# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 26 September 2026, after session 77._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (D59.2). F109
stands.**

**A sixth airport, San Francisco International (KSFO), is rehearsed and
locked** under the unchanged B+D,L,R,T recipe (D67, D69, D70). Its two
held-out years (2024-08-01..2026-07-31) are still closed: no model has
been fit on them and none of their values has been read.

- **Q34 is closed (D69).** KSFO's reproduction gate is recorded as
  "failed, explained by a difference between the sources (F117)". There is
  no override; F116.5 stands as a FAIL.
- **Rehearsal (F118), not a gate.** On the 2022-23 and 2023-24 folds,
  B+D,L,R,T beats raw GFS (GRIB) and persistence. Every pipeline check
  passed. The 2022-23 margin over B (0.0319) is within the band; 2023-24's
  (0.1177) is above it.
- **The band (D70.5):** 0.037704595173481126 °C (0.0377), from B+D,L,R,T
  on 2022-23. A secondary read, not part of the bar.
- **The frozen look script (D70.6):** `scripts/session77_ksfo_looks.py`,
  SHA-256 `e4ec113b0dcbc936550b382ffbcdd55d3049878c8b13d74cd83e867a6b3247c1`.
  Its `--dry-run` passed, and its self-test reproduced the rehearsal
  exactly. `--run-looks` has not been run.
- **Framing (D70.9).** KSFO's result will be for the recipe at a sea-mixed
  grid point (37.5% sea weight). It is not directly comparable with the
  five earlier airports.

---

## Open questions (live)

- **Q30 (open).** The owner's order (D66.1): Q33 (done, F115); a further
  airport under the frozen recipe (KSFO, D67; locked, D70); then a
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

**Next planning session:** Review session 77. If it is committed, session
78 checks the look script's hash and runs
`scripts/session77_ksfo_looks.py --run-looks` once, unchanged. After the
KSFO verdict, hold the roadmap planning session (D66.1).
