# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 24 September 2026, after session 75._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).
The audit is complete and triaged (D62). The clean-room rebuild of F109 at
RNO is complete, and D64 is closed. F109 stands.**

**Q33 is answered descriptively and closed (F115).** Session 75 measured
how much column order alone moves a fit, on the two non-reserved folds
(2022-23 and 2023-24), at all five airports. It was a description only. It
changed no verdict, claim or figure.
- Column order alone moves a B+D,L,R,T fit's MAE by 0.019 to 0.039 °C
  (range across 102 orderings), and a B fit's by 0.014 to 0.030 °C (120
  orderings).
- By the pre-set rule (D66.3), B+D,L,R,T beats B by more than the
  column-order spread on both folds at all five airports: every
  B+D,L,R,T ordering beats every B ordering.
- Scale guide only (different year): DSM's F109 margin over B (0.0279 °C)
  is smaller than DSM's column-order range on both folds.

**Owner decisions after session 74 are recorded in D66:** the Q30
sequencing (D66.1) and the GFS v17 status (D66.2).

---

## Open questions (live)

- **Q30 (open).** The owner has chosen the order (D66.1): (1) Q33,
  descriptively (done, F115); (2) a further airport under the frozen
  B+D,L,R,T recipe (Q30 branch (i), D59.5), with the airport and its test
  design still to be chosen; (3) a dedicated roadmap planning session.
  Pooling is deferred. The 2026-27 forward test is deferred until the GFS
  v17 date is known (D66.2). If a 2026-27 test is ever pre-registered, it
  must name the two tracked DSM files for 2026-08-05..2026-08-15 (D62.7,
  A67-15).
- **Q32 (unchanged).** Whether a failed sealed test (Reno, minimal method,
  F82), as opposed to just a negative rehearsal, changes the owner's
  intentions for future terrain-hard airports generally. The
  richer-features result (F94) and the selected-features result (F109) are
  the owner's practical answers for Reno specifically, but the general
  question was never asked in so many words.

No other open question is live; everything else has been closed by a
decision or a finding (see DECISIONS.md).

---

## Carried items

- **SPEC 7.2 wording (fold into the next session that edits SPEC).** SPEC
  7.2 glosses bilinear interpolation as "weighted by distance", which
  could be read as inverse-distance weighting. SPEC 8.8 G6 says standard
  bilinear, not inverse distance. Add a one-line clarification to SPEC 7.2.
  (Session 74's consistency check: a tension, not a conflict.)
- **GFS v17.** Re-check the NWS notice list at each planning session
  (D66.2). Per D66.2 (planning-chat research, not checked by session 75),
  as of 2026-09-24 no Service Change Notice for GFS v17 was listed.

---

## Next

**Next planning session: review F115. Then plan the new airport (Q30
branch (i)): the owner chooses the airport (or a candidate screen) and the
test design (one look on 2025-26, or two pre-registered looks on 2024-25
and 2025-26). After the airport, hold a dedicated roadmap planning
session. Roadmap session inputs: P1–P3, Q30 (2026-27, pooling), Q32, SPEC
5.4, RESULTS §7 terrain descriptor, SPEC stages 4–6, GFS v17 (D66.2).**
