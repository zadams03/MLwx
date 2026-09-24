# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 24 September 2026, after session 73._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).
The three-part audit is complete and triaged (D62); every must-fix and
should-fix item is done.**

**The clean-room rebuild of F109 at RNO (DECISIONS D64) has run both parts
and is waiting for the owner's triage.** It is a verification only and
cannot change any verdict, claim or figure (D64.1).
- Session 72 (F112) rebuilt the data tables from the docs alone.
- Session 73 (F113) fitted, scored, sealed and compared every stage.
  - Under Variant P, every data stage matches the record exactly:
    observations, report times, targets, day set, all feature columns and
    their inputs, the complete-case sets, raw GFS and persistence.
  - Raw GFS, persistence and B match F109 to full precision.
  - The rebuild's own fits repeat exactly.
- **Open mismatches (D64.5, for the owner to triage):**
  - **B+D,L,R,T MAE, Variant P: 1.2703 against the record's 1.2742.**
    Every input matches, so D64.4 puts this in the fit-determinism
    category. Two recipe details differ from the record script:
    - column order: the rebuild uses L, D, T, R; the record uses D, L, R, T
      (G15);
    - target rounding: the rebuild trains on a 3 dp residual; the record
      trains on the unrounded one (G20).

    Neither was tested.
  - **Variant G4-alt: L and D differ on the 655 rows (data), and its
    B+D,L,R,T MAE is 1.2596.** The record matches Variant P.
- No breach of session 72's clean room was found (F113.5).

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
  A67-15). The owner chose to finish the D64 rebuild before Q30.
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

Next planning session: review F113, and the owner triages the mismatches
under D64.5.
