# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 68a._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md), and the feature-selection programme that produced the third
one is closed (DECISIONS D59.2).** Before any Q30 branch is chosen, the
owner has ordered a three-part audit (DECISIONS D60.1). The third part,
session 68, is split into 68a and 68b (DECISIONS D61.1).

1. **Session 66 — document audit. DONE.** Report:
   `notes/audit-session-66.md`. No must-fix findings.
2. **Session 67 — repo and code audit. DONE.** Report:
   `notes/audit-session-67.md`. No must-fix findings (6 should-fix, 6
   cosmetic, 3 uncertain). Its section 3 is the core pipeline map.
3. **Session 68a — correctness audit, part 1: reproduce the record. DONE.**
   Report: `notes/audit-session-68a.md`. **No must-fix findings** (1
   should-fix, 4 cosmetic, 1 uncertain).
   - The one verification recompute (D60.2, extended and ruled on at the
     gate in D61.4/D61.5) ran once, in a clean clone under `/tmp`.
     **163 of 163 recorded figures reproduce exactly**, across F16, F30,
     F47, F64, F82, F94 and F109. Every full output matches its committed
     record apart from timestamps, and both result CSVs are byte-identical.
     Every verdict stands, as D61.4 says it would whatever the run showed.
   - Sample rebuild from the raw GRIB: all 315 of B's sampled values
     (45 station-days) match the processed CSVs.
   - **L, D, T and R were not rebuilt.** Their raw GRIB bytes were never
     kept on disk, so checking them against source needs a network re-fetch
     (A68a-01, should-fix).
4. **Session 68b — logic and leakage review of the headline pipeline.
   NEXT, not yet drafted.** Scope per D61.3: the scripts behind
   F16/F30/F47/F64/F82, F94 and F109 and their data builds; not the E1–E5
   or combine experiment scripts. 68b recomputes no spent-year figure
   (D61.1). Items already flagged for it: A67-04, A67-12 and A67-14 (the
   session-67 report, section 6.1), plus anything in the 68a report.

All session-66, 67 and 68a findings wait for triage after 68b. Only after
triage and the owner's fix sessions does the owner choose a Q30 branch
(D60.1).

---

## Open questions (live)

- **Q30 (open; deferred, per D60.1, until after the audit and any resulting
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

Next planning session: draft session 68b (logic and leakage review of the
headline pipeline), using the session-67 map (notes/audit-session-67.md
section 3). The session-68a report was reviewed by the owner before commit;
there were no mismatches, and A68a-01 (L/D/T/R not rebuilt from source) is
the nearest open gap, held for triage.
