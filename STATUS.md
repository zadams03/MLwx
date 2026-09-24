# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 24 September 2026, after session 74._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).
The three-part audit is complete and triaged (D62); every must-fix and
should-fix item is done.**

**The clean-room rebuild of F109 at RNO is complete, and D64 is closed
(F114.6).** It was a verification only and changed no verdict, claim or
figure. F109 stands.
- Every data stage matches the record. Raw GFS, persistence and B match
  F109 to full precision.
- The one mismatch (B+D,L,R,T 1.2703 against 1.2742) is explained, class A
  (F114). The record's column order (B, then D, L, R, T) reproduces
  1.2742 exactly. Target rounding has no effect.
- The details the rebuild had to guess are now recorded in SPEC 8.8.

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
  A67-15). The D64 rebuild the owner chose to finish first is now done.
- **Q32 (unchanged).** Whether a failed sealed test (Reno, minimal method,
  F82), as opposed to just a negative rehearsal, changes the owner's
  intentions for future terrain-hard airports generally. The
  richer-features result (F94) and the selected-features result (F109) are
  the owner's practical answers for Reno specifically, but the general
  question was never asked in so many words.
- **Q33 (new, logged only, F114).** Changing only the column order moved
  RNO's B+D,L,R,T reserved-year MAE by 0.0038 °C. How large is fit-to-fit
  variation, compared with the verdict margins on record, especially the
  small ones (for example DSM over B, +1.94%)? Any measurement needs its
  own pre-registration and cannot re-score spent years for a verdict.

No other open question is live; everything else has been closed by a
decision or a finding (see DECISIONS.md).

---

## Next

Next planning session: review F114, then the owner chooses a Q30 branch,
and considers Q33.
