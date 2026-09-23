# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 70._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).**

**The three-part audit is complete and triaged (DECISIONS D62).** It found
no leakage and no wrong number. 163 of 163 recorded figures reproduce, and
no verdict, claim or figure on record changes (D62.1). All must-fix and
should-fix items are done before any Q30 branch is chosen.

**Done so far:** session 69's documentation fixes (D62.5) and session 70's
repo fixes (D63):
- A67-01 (must-fix): the session 37 and 40 GRIB pulls now have committed
  pull manifests and failure logs under `data/raw/diagnostics/session37/`
  and `session40/`. Every count reconciles with F90 and F92.
- A67-06: `data/processed/session46_fold_table.csv` has a `station`
  column. `session46_backtest.py` was not edited, so a re-run would drop
  the column again (D63.2).
- A67-05 with A67-07: new `README.md`; two stale comments fixed in
  `requirements.txt`.
- A67-08 with A68a-06: `.gitignore` fixed.

**Still to do before Q30** (D62.8):
- **Session 71** (network, data only): rebuild L, D, T and R for the same
  45 station-days (A68a-01).

---

## Open questions (live)

- **Q30 (open, unchanged; deferred until session 71 is done, D62.2).**
  Three branches remain open and are the owner's choice: a further airport
  (run under the frozen `B+D,L,R,T` recipe, SPEC 8.7); a second test year
  (now only possible as a live forward-looking 2026-27 test or a weaker
  already-seen-year reuse rule); or pooling (SPEC stage 3). See DECISIONS
  D59.5 for the three branches and the planning-chat recommendation on
  record (not a decision). If branch (i) is chosen, its pre-registration
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

## Next

Next planning session: draft session 71 (network, data only: rebuild L, D, T and R for the same 45 station-days, A68a-01) per D62.8.
