# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 22 September 2026, after session 60._

---

## Where the project is right now

**The E1–E5 feature-selection sweep is complete (all five families verdicted,
D52–D56), and the combine-phase sweep that follows it is now designed and
pre-registered — no model fit, no data row read.**

Session 60 wrote `DECISIONS.md` D57: the combine sweep will fit a
pre-registered 14-variant ladder (B; the five single-adds; the full adopted
set B+LDTRP; its five leave-one-out variants; and the two parked-option adds
B+LDTRP+rh / B+LDTRP+plev) on the three non-reserved `EXPERIMENT_FOLDS`
(D51), with pre-registered thresholds (`TAU_SKILL` = 0.4%, a 5%
complete-case row-cost guard, and a fixed backward-elimination drop order),
a mechanical selection rule with a correlated-feature safeguard, and a joint
backstop that halts and surfaces rather than auto-picking if the selected
set fails its own checks. All of this is enforced in code by the new
manifest `scripts/session60_combine_design.py`, which imports (not
redefines) session 48's `EXPERIMENT_FOLDS` and reserved-year guard.

The manifest's header-only pre-flight ran once and passed cleanly (18 of 18
file/column checks present, 14/14 variants). Building it surfaced one
wrinkle, recorded in D57: the E2 feature `dewpoint_depression_t2m_floored`
(D53) is not itself a stored column — only the raw `dewpoint_depression_t2m`
is committed, with the exact floor transform (`max(x, 0)`, per D53/F100)
applied at feature-matrix build time, not persisted to disk. The manifest
names the raw column plus the transform explicitly so session 61 applies
the already-frozen formula rather than guessing or re-deriving.

The measurement baseline B is unchanged. The reserved 2024-25 year (D51) and
the sealed 2025-26 year (F94) are both still untouched. Every prior verdict
(F16/F30/F47/F64/F82, F94, D52–D56) stands exactly as reported.

---

## Next

**Next planning session: session 61 — run the pre-registered combine sweep
(D57): fit the 14-variant ladder on the three non-reserved
`EXPERIMENT_FOLDS` over the single complete-case row set, run the row-cost
guard and the integrity checks, apply the selection rule with the joint
backstop, and report the grid — no verdict, no reserved-year read. The
session-62 owner review then picks the single final feature set.**

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
