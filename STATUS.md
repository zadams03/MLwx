# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 67._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md), and the feature-selection programme that produced the third
one is closed (DECISIONS D59.2).** Before any Q30 branch is chosen, the
owner has ordered a three-part audit (DECISIONS D60.1):

1. **Session 66 — document audit. DONE.** Report:
   `notes/audit-session-66.md`. No must-fix findings.
2. **Session 67 — repo and code audit. DONE.** Report:
   `notes/audit-session-67.md`. **No must-fix findings.** 6 should-fix, 6
   cosmetic, 3 uncertain. A clean clone set up from `requirements.txt`
   installs every pin exactly, all 67 scripts compile, and the
   `session62_reserved_confirm.py` preflight reproduces F109's 2023-24
   dry-run table to the fourth decimal place at all five airports. The main
   should-fix items: the core GRIB pull's provenance (sidecars and failure
   log) sits only in the gitignored cache, against D47's wording (A67-01);
   two frozen scripts write fixed output files that a re-run would
   overwrite (A67-02, A67-03); the session-62 preflight prints claims that
   are stale since F107 (A67-04); there is no setup README (A67-05). The
   report's section 3 holds the core pipeline map for session 68. All
   session-66 and session-67 findings wait for triage after session 68.
3. **Session 68 — correctness audit. NEXT, not yet drafted.** Per D60.1: a
   leakage and logic review of the core pipeline, plus a reproduction of
   recorded results. Per D60.2, a one-time verification recompute of the two
   spent years (2025-26/F94, 2024-25/F109) is allowed in that session only,
   to check reproducibility to the fourth decimal place. It is not a new
   look and not a verdict, and every existing verdict stands whatever it
   shows. Session 68 must first check SPEC section 2 (and any other rule
   text) for wording that forbids this, and stop and flag if it finds any.
   Session 67's A67-02/A67-03 mean that recompute would overwrite committed
   output files if run in the working repo, so running it in a clean clone
   under `/tmp` is the simple safe option.

Only after all three audits and the owner's own triage and fix sessions does
the owner choose a Q30 branch (DECISIONS D60.1). This session changed only
two files: the new `notes/audit-session-67.md` and this STATUS.md. Nothing
under `scripts/`, `data/` or `docs/` was touched, no model was fitted in the
repo, and no 2024-25 or 2025-26 figure was produced.

---

## Open questions (live)

- **Q30 (open; deferred, per D60.1, until after the three-part audit and any
  resulting fix sessions).** Three branches remain fully open and are the
  owner's choice once the audit programme completes: a further airport (run
  under the frozen `B+D,L,R,T` recipe, SPEC 8.7); a second test year (now
  only possible as a live forward-looking 2026-27 test or a weaker
  already-seen-year reuse rule); or pooling (SPEC stage 3). See DECISIONS
  D59.5 for the full statement of the three branches and the planning-chat
  recommendation on record (not a decision).
- **Q32 (unchanged).** Whether a failed sealed test (Reno, minimal method,
  F82) — as opposed to just a negative rehearsal — changes the owner's
  intentions for future terrain-hard airports generally. Both the
  richer-features result (F94) and the selected-features result (F109) are
  the owner's practical answers for Reno specifically, but the general
  question was never asked in so many words.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.

---

## Next

Next planning session: owner review of the session-67 report
(`notes/audit-session-67.md`), then drafting session 68 (correctness audit)
using that report's core pipeline map (section 3), including a decision on
whether session 68's size warrants subagents.
