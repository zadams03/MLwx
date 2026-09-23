# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 69._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).**

**The three-part audit is complete and triaged (DECISIONS D62).** It found
no leakage and no wrong number. 163 of 163 recorded figures reproduce, and
no verdict, claim or figure on record changes (D62.1). Every finding is
classed as must-fix, should-fix or leave-alone (D62.2–D62.7). All must-fix
and should-fix items are done before any Q30 branch is chosen.

**Session 69's fixes are done** (documentation only, D62.5):
- SPEC 5.2, 7.2, 7.4, 7.5, 8.2 and 8.5, and RESULTS sections 5–7, now say
  that the GRIB methods' "raw GFS" baseline is the elevation-adjusted GRIB
  temperature (A68b-02, must-fix).
- SPEC 4.5 now says the historical code keeps the last qualifying report
  (A67-12, must-fix). SPEC 8.7 has new build requirements for new-airport
  code.
- The persistence day basis, the "run once" pointer to D61.4, the RNO
  stage cell, the SPEC 6 pointer to the default recipe, three glosses, and
  CLAUDE.md's planning-chat wording are fixed.
- D62.7 records what each of the five A67-09 files is. No file was deleted.
- F94, D49, F95, D50, D60 and D61 were moved to DECISIONS-archive.md.

**Still to do before Q30** (D62.8):
- **Session 70** (repo fixes, offline): A67-01 provenance manifests
  (must-fix), A67-06, A67-05 with A67-07, A67-08 with A68a-06.
- **Session 71** (network, data only): rebuild L, D, T and R for the same
  45 station-days (A68a-01).

---

## Open questions (live)

- **Q30 (open, unchanged; deferred until sessions 70 and 71 are done,
  D62.2).** Three branches remain open and are the owner's choice: a
  further airport (run under the frozen `B+D,L,R,T` recipe, SPEC 8.7); a
  second test year (now only possible as a live forward-looking 2026-27
  test or a weaker already-seen-year reuse rule); or pooling (SPEC stage
  3). See DECISIONS D59.5 for the three branches and the planning-chat
  recommendation on record (not a decision). If branch (i) is chosen, its
  pre-registration must name the two tracked DSM files for 2026-08-05..
  2026-08-15 (D62.7, A67-15).
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

Next planning session: draft session 70 (repo fixes, offline: A67-01
provenance manifests, A67-06 station column, README, .gitignore) per
D62.8.
