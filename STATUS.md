# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 72._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).
The three-part audit is complete and triaged (D62); every must-fix and
should-fix item is done.**

**A clean-room end-to-end rebuild of F109 at RNO is half done (DECISIONS
D64, pre-registered).** It is a verification only and cannot change any
verdict, claim or figure (D64.1).
- Session 72 (data, F112): L, D, T and R re-pulled from raw GRIB for all
  of RNO's train and test days (15,900 of 15,910 messages; the 10 failures
  are the run F90 already found broken). RNO's observation, feature and
  persistence tables were built from the docs alone into
  `data/rebuild/session72/`. Every row count the docs state agrees (17 of
  17 comparable figures).
- Session 73 (next): fit, score, and compare every stage with the record,
  under D64.3–D64.5. The clean-room rule holds until its comparison step.

**For session 73 to know:** one documentation gap changes values. B's
stored precision is not stated anywhere (F112.2, G4). The rebuild rounds
`temperature_grib_c` to 3 decimals before deriving `t2m_raw`. That
differs by 0.001 from using the full value on 655 of 1,590 rows, and so
moves L and D on those rows. Both columns are kept.

---

## Open questions (live)

- **Q30 (open, unchanged; unblocked, D62.2, D62.8).** Three branches
  remain open and are the owner's choice: a further airport (run under the
  frozen `B+D,L,R,T` recipe, SPEC 8.7); a second test year (now only
  possible as a live forward-looking 2026-27 test or a weaker
  already-seen-year reuse rule); or pooling (SPEC stage 3). See DECISIONS
  D59.5 for the three branches and the planning-chat recommendation on
  record (not a decision). If branch (i) is chosen, its pre-registration
  must name the two tracked DSM files for 2026-08-05..2026-08-15 (D62.7,
  A67-15). The owner chose to run the D64 rebuild before Q30.
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

Next planning session: draft session 73 (fit, score and stage-by-stage
comparison, D64).
