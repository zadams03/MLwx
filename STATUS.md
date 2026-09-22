# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 22 September 2026, after session 62._

---

## Where the project is right now

**The single final feature set is locked (D58): B + D, L, R, T — the frozen
5-feature GRIB baseline plus moisture, lapse rate, shortwave radiation, and
pressure tendency. Precipitation is dropped; neither parked option (`rh`,
`plev`) is adopted.** This confirms D57's mechanical rule's own output
(F106) unchanged, after the owner's review of its full grid and selection
trace found no reason to override it.

The frozen, self-guarded confirmation script (`scripts/
session62_reserved_confirm.py`) is written and pre-flighted. Its pre-flight
(header/date checks, guard checks, column-integrity check, and a machinery
dry-run on the already-non-reserved 2023-24 fold) all passed — the dry-run
exactly reproduces session 61's own `B+LDTR` grid row at every airport,
strong evidence the fit/score machinery is correct. **The reserved
2024-08-01..2025-07-31 year was not opened this session** — no row of it
was read, loaded, fit on, or scored anywhere.

**A blocking data gap was found (D58 item 11) — closing it is session 63's
own job, before session 64 can run the confirmation.** The four
adopted-feature families (L, D, T, R) were each built (sessions 49/51/53/55)
with the reserved year deliberately excluded, per D51's mandate at the
time — verified directly this session: every one of their eight committed
files has zero rows anywhere inside 2024-08-01..2025-07-31. So although the
confirmation fold's *training* window (2021-03-24..2024-07-31) is fully
covered, its *test* window (the reserved year itself) currently has no
L/D/T/R feature value for any airport, for any date. `run_confirm()`
contains a hard guard that will stop with a clear error rather than
silently score on missing data — it will not waste the one authorized look
— but as things stand today, running it would simply stop at that guard.
**Session 63 closes this gap by extending the same already-frozen L/D/T/R
pull/derive pipelines to cover the reserved year's dates — an
outcome-orthogonal data build (raw inputs plus the already-pinned
transforms only, no model fit, no scoring, nothing selected) — so session
64 can then run the frozen confirmation.**

Every prior verdict (F16/F30/F47/F64/F82, F94, D52–D57, F106) stands
exactly as reported, untouched.

---

## Next

**Next planning session: session 63 — the reserved-year feature build
(closes D58 item 11).** Extend the already-frozen L, D, T, R pull/decode/
derive pipelines (sessions 49/51/53/55's own code, unchanged) to cover
2024-08-01..2025-07-31, so the confirmation fold's test window has real
L/D/T/R feature values at every airport. This is an outcome-orthogonal
data build — raw inputs plus the already-pinned transforms (D53/F100's
floor formula and the rest, applied exactly as pinned) only, no model fit,
no MAE, no scoring, nothing selected — so it does not itself touch D51's
one-look discipline.

**Session 64 — run the frozen confirmation script once, unchanged.** Once
session 63 closes the gap, run `scripts/session62_reserved_confirm.py
--confirm` once, unchanged, on the 2024-25 fold. This is the single
authorized look (D51); report the verdict against D58's pre-registered
expectations (bar: B+D,L,R,T beats both raw GFS and persistence at all
five airports; secondary read: beats plain B on airport-averaged MAE).

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
