# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 71._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).**

**The three-part audit is complete, triaged (DECISIONS D62), and every
must-fix and should-fix item is done.** It found no leakage and no wrong
number. No verdict, claim or figure on record changes (D62.1).
- Session 69: documentation fixes (D62.5).
- Session 70: repo fixes (D63).
- Session 71: L, D, T and R rebuilt from newly pulled raw GRIB by new,
  independent code for audit 68a's 45 station-days (A68a-01). **180 of 180
  match the committed files exactly; 0 mismatches, 0 missing** (DECISIONS
  F111). The pull manifest is under `data/raw/diagnostics/session71/`.

The session plan in D62.8 is now finished: "Then Q30."

---

## Open questions (live)

- **Q30 (open, unchanged; now unblocked, D62.2, D62.8).**
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

Next planning session: the owner chooses a Q30 branch (D62.8).
