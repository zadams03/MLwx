# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 68b._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md). The feature-selection programme is closed (DECISIONS D59.2).**

**The three-part audit ordered by DECISIONS D60.1 is complete.** The four
reports:

1. `notes/audit-session-66.md`: document audit. No must-fix findings.
2. `notes/audit-session-67.md`: repo and code audit. No must-fix findings
   (6 should-fix, 6 cosmetic, 3 uncertain).
3. `notes/audit-session-68a.md`: correctness part 1, reproducing the record.
   163 of 163 recorded figures reproduce exactly. No must-fix findings (1
   should-fix, 4 cosmetic, 1 uncertain).
4. `notes/audit-session-68b.md`: correctness part 2, the logic and leakage
   review of the headline pipeline. **No leakage and no wrong number
   found.** No must-fix findings (3 should-fix, 4 cosmetic, 0 uncertain).
   The three should-fix findings:
   - A68b-02: the GRIB methods' "raw GFS" baseline is elevation-corrected
     (D48.10), which SPEC 5.2 and sections 7–8 do not say;
   - A68b-01: the F109 script's gap guard only stops on zero rows;
   - A68b-04: `float()` would accept a literal `nan` silently. None exists
     in the data today.

   The carried items A67-04, A67-12 and A67-14 each have a disposition in
   the 68b report (section 2, item 22).

**Triage is next.** No finding from any of the four reports has been
classified, fixed or recorded in DECISIONS yet. Each report lists its own
archive candidates. No archive move was made in 68a or 68b.

---

## Open questions (live)

- **Q30 (open; deferred, per D60.1, until after triage and any resulting
  fix sessions).** Three branches remain open and are the owner's choice: a
  further airport (run under the frozen `B+D,L,R,T` recipe, SPEC 8.7); a
  second test year (now only possible as a live forward-looking 2026-27
  test or a weaker already-seen-year reuse rule); or pooling (SPEC stage
  3). See DECISIONS D59.5 for the three branches and the planning-chat
  recommendation on record (not a decision).
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

Next planning session: owner review of the session-68b report, then triage
of all findings from the four audit reports (66, 67, 68a, 68b) into
must-fix, should-fix and leave-alone, recorded in one DECISIONS entry,
followed by fix sessions.
