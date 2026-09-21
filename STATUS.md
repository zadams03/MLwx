# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 21 September 2026, after session 59._

---

## Where the project is right now

**The E1–E5 feature-selection sweep is complete: all five families have a
verdict against the frozen 5-feature baseline B.**

Adopted into the eventual combine-phase sweep baseline: `lapse_rate_t2_t850`
(D52), `dewpoint_depression_t2m_floored` (D53), `pressure_tendency_3h_hpa`
(D54), `dswrf_2h_wm2` (D55), `precip_rate_mmh` (D56).

Parked combine-phase candidates: RNO's raw pressure-level temperatures
(D52), relative humidity (D53).

The measurement baseline B is unchanged; the reserved 2024-25 year (D51) is
still untouched; the sealed-year GRIB verdict (F94) and every minimal-method
verdict (F16/F30/F47/F64/F82) stand exactly as reported.

STATUS.md was pruned to a current-only snapshot this session (session 59).
Pre-session history — every earlier session's own write-up — lives in git
and in `DECISIONS.md` (and `DECISIONS-archive.md`) by number; nothing was
lost, only relocated to where it already had a permanent home.

---

## Next

**Next planning session: session 60 — design and open the combine phase:
sweep the five adopted features (D52–D56) together on the three
non-reserved `EXPERIMENT_FOLDS` (D51), with the two parked candidates (D52,
D53) as sweep options, to choose a single final feature set; that one set
is then confirmed on the reserved 2024-25 year (D51) exactly once, at the
finish line. The E1–E5 sweep and the STATUS housekeeping are both done.**

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
