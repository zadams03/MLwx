# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 23 September 2026, after session 66._

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0/7.5/8.7,
RESULTS.md), and the feature-selection programme that produced the third
one is closed (DECISIONS D59.2).** Before any Q30 branch is chosen, the
owner has ordered a three-part audit (DECISIONS D60.1):

1. **Session 66 (this session) — document audit. DONE.** Read-only review
   of CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md, the live DECISIONS.md and
   `docs/*.md`, plus scripted citation/numbering/ordering/cross-reference
   checks and git-history checks. Report: `notes/audit-session-66.md`.
   **Result: no must-fix findings** — no contradiction, broken citation,
   numbering gap, or duplicate-defined entry anywhere. 4 should-fix items:
   two archive-hygiene findings (F94, D49, F95 and D50 now meet the D46
   archive criterion), the superseded STATUS "Next" line (self-resolved),
   and stale CLAUDE.md planning-chat wording (A66-08, resolved by the owner
   at review: planning chats use Project knowledge, not pasting). 4
   cosmetic items (stale parked items P1–P3, a missing section 6 to 8.7
   cross-reference, a few unglossed jargon terms). 0 uncertain. See the
   report, section 5.
2. **Session 67 — repo and code audit, not yet started.** Per D60.1: a
   fresh-environment check plus a repo/code hygiene review. Session 67's own
   drafting should include a check of `scripts/` size to decide whether
   subagents are warranted for that session only (see "Next," below).
3. **Session 68 — correctness audit, not yet started.** Per D60.1: a
   leakage/logic review of the core pipeline and a reproduction of recorded
   results. Per D60.2, a one-time verification recompute of the two spent
   years (2025-26/F94, 2024-25/F109) is permitted in that session only, to
   check reproducibility to the fourth decimal place — not a new look, not a
   verdict, and every existing verdict stands regardless of what the
   recompute shows. Session 68 must first check SPEC section 2 (and any
   other rule text) for wording that would forbid this, and stop and flag
   rather than run if it finds any.

Only after all three audits and the owner's own triage/fix sessions does the
owner choose a Q30 branch (DECISIONS D60.1). Nothing under `scripts/`,
`data/` or `docs/` was touched this session; no data file was opened; no
model was fit; nothing was scored.

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
- **Q32 (unchanged this session).** Whether a failed sealed test (Reno,
  minimal method, F82) — as opposed to just a negative rehearsal — changes
  the owner's intentions for future terrain-hard airports generally. Both
  the richer-features result (F94) and the selected-features result (F109)
  are the owner's practical answers for Reno specifically, but the general
  question was never asked in so many words.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.

---

## Next

Next planning session: draft session 67 (repo and code audit, including a
fresh-environment check). The session-66 report was reviewed by the owner
before commit; its findings wait for triage after session 68. Session 67's
drafting should include a check of the size and count of files under
`scripts/` to decide whether subagents are warranted for that session only.
Q30 stays open and deferred until the full audit programme and any
resulting fix sessions are complete.
