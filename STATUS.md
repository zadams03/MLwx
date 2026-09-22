# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 63._

---

## Where the project is right now

**The single final feature set remains locked (D58): B + D, L, R, T — the
frozen 5-feature GRIB baseline plus moisture, lapse rate, shortwave
radiation, and pressure tendency.** Precipitation is dropped; neither
parked option (`rh`, `plev`) is adopted. Nothing about the set changed this
session.

**D58 item 11's blocking data gap is now closed (F107).** Session 63
extended the already-frozen L, D, T, R pull/decode/derive pipelines
(sessions 49/51/53/55's own code, reused by import, unchanged) to cover the
reserved 2024-08-01..2025-07-31 confirmation year. All four families now
have real, validated feature values for the reserved year, at every
airport: 365 rows per airport per family, matching the base 5-feature
dataset's own reserved-year row count exactly, zero join drops, zero
nulls, zero pull failures. A minimal, documented wiring addition was made
to `scripts/session62_reserved_confirm.py`'s own `load_family()` function
(a new `RESERVED_FAMILY_FILES` map, pointing at the four new
`session63_reserved_window_with_*.csv` files) so the frozen confirmation
script can see this data — `session60_combine_design.py`'s
`CANDIDATE_FEATURES` (which session 61 already used) was not touched. A
read-only, model-free check confirmed the wiring works: the reserved year
now yields exactly 365 complete-case rows per airport (previously 0), and
the training-window row counts still match D58 item 5's own already-verified
figures exactly.

**No model was fit this session. No MAE, skill, or CV was computed
anywhere. `run_confirm()` was never called** — not even `preflight()`,
since it fits a LightGBM model in its own "machinery dry-run" step, which
this session's scope excluded. The sealed year (2025-08-01..2026-07-31,
F94) was never touched. `scripts/session62_reserved_confirm.py` is still
the frozen script session 64 runs with `--confirm`, once, unchanged — this
session's own edit to it is the one authorized wiring exception (documented
in F107), not a change to its confirmation logic, its feature set, its
fold, or its bar.

Every prior verdict (F16/F30/F47/F64/F82, F94, D52–D58, F106) stands
exactly as reported, untouched.

---

## Next

**Next planning session: session 64 — run the frozen confirmation script
once, unchanged.** Run `scripts/session62_reserved_confirm.py --confirm`
once, unchanged, on the 2024-25 fold. This is the single authorized look
(D51); report the verdict against D58's pre-registered expectations (bar:
B+D,L,R,T beats both raw GFS and persistence at all five airports;
secondary read: beats plain B on airport-averaged MAE).

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
