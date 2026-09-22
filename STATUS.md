# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 22 September 2026, after session 61._

---

## Where the project is right now

**The pre-registered combine-phase sweep (D57) has been run (F106). The
mechanical selection rule's output is a candidate feature set — B+D,L,R,T
(the full adopted set B+LDTRP minus precipitation P; neither parked option,
`rh` nor `plev`, adopted) — and the joint backstop passed. This is explicitly
NOT a verdict.** The single final feature set is the session-62 owner
review's call.

Session 61 fit the 14-variant ladder on the three non-reserved
`EXPERIMENT_FOLDS` (D51), over one complete-case row set covering all seven
candidate features. Every guard and integrity check passed: the reserved
2024-25 confirmation year was never touched; the complete-case row set
turned out identical to the true B-only row set (0 rows dropped at any of
the 15 airport-folds); every feature column matched its committed source
file exactly (max abs diff 0.0); the refit-B 2025-26 fold reproduced
F94/F96/F99-F105's own numbers exactly at every airport.

Applying the mechanical selection rule: Round 1 of leave-one-out backward
elimination flagged three features (D, L, P) droppable together, triggering
the correlated-feature safeguard, which dropped only the least-damage one
(P, +0.12pp). Round 2 found nothing further droppable — core set = B+D,L,R,T.
Neither parked option (`rh`, raw relative humidity; `plev`, the three raw
pressure-level temperatures) cleared the bar on top of the core set — both
actively worsened it when added. The joint backstop confirmed the final set
beats B (+5.48% fold-averaged, non-DSM) and is not meaningfully worse than
the full B+LDTRP set (gap +0.12pp, within the 0.4pp threshold).

Two interpretation decisions were required to turn D57's English rule into
code (documented in the script and DECISIONS F106, flagged for session-62 to
check): (1) all keep/drop/adopt/backstop votes average over the four
non-DSM airports, per D57's "DSM is diagnostic only — never a keep/drop
vote"; (2) `plev`'s own adoption vote uses all five airports, per its
explicit "across all five airports" override in D57.

Every prior verdict (F16/F30/F47/F64/F82, F94, D52–D57) stands exactly as
reported. The reserved 2024-25 year and the sealed 2025-26 year both remain
untouched by any selection decision.

---

## Next

**Next planning session: session 62 — owner review of the combine-sweep
grid (F106). Pick the single final feature set** — confirm the mechanical
rule's own output (B+D,L,R,T), override it using the same grid and
selection trace, or resolve the two interpretation decisions differently.
**That set is then confirmed once on the reserved 2024-25 year at the
finish line (D51).** The joint backstop did not halt, so there is no
stop-and-surface failure to resolve — this is a normal review, not a
recovery session.

---

## Open questions (live)

- **Q30 (its richer-features branch is resolved; the question itself stays
  open because its other two branches remain the owner's choice).** The
  owner picked its first branch — more airports, "ramp up difficulty" — and
  Reno's own five steps are finished, ending in a failure under the
  existing recipe. The richer-features branch of that intent has now
  reached its answer (the 5-feature GRIB recipe passes at all five
  airports, F94), and its documentation follow-up (SPEC/RESULTS fold-in,
  archive pass) is done. **Q30's other two branches — a further airport,
  and a second test year (the remaining half of the F30/F48 caveat) — and
  stage 3 (pooling) remain fully open and are the owner's choice**,
  unaffected by how the richer-features branch resolved.
- **Q32 (effectively answered by events, left on record rather than
  formally closed).** Session 27 asked whether Reno's rehearsal loss should
  change anything about locking/testing Reno; the session-28 and session-29
  prompts both instructed proceeding regardless, and that is what happened
  — Reno was locked unmodified (D44) and tested unmodified (F82), and it
  failed. The owner has still not been asked, in so many words, whether a
  failed sealed test (as opposed to just a negative rehearsal) changes their
  intentions for future terrain-hard airports generally — though the
  richer-features branch is the owner's first practical answer for Reno
  specifically.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
