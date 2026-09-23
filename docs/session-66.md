# Session 66 — Document audit (read-only), first of three audit sessions

## Context

Before choosing a Q30 branch, the owner has asked for a full hygiene and
correctness audit of the project. The plan has three parts:

- **Session 66 (this one):** audit the documents.
- **Session 67:** audit the repo and code, including a fresh-environment
  check.
- **Session 68:** audit correctness, meaning a review of the core pipeline
  for leakage and logic errors, and a reproduction of the recorded results.

After the three audits come triage in the planning chat, then fix sessions,
and only then the Q30 choice.

## Scope

This session is **read-only**. It **reports** findings and **fixes
nothing**, even obvious typos.

Exactly three files may be written:

1. a new `notes/audit-session-66.md`, the findings report;
2. one appended DECISIONS entry, D60 (Step 1);
3. the overwritten STATUS.md.

The scripted checks run as throwaway scripts **outside the repo** (for
example under `/tmp`). Paste their full source into the report's appendix so
the checks can be reproduced.

No file under `scripts/`, `data/` or `docs/` is modified. No data file is
opened. No model is fit. Nothing is scored.

**Do not read DECISIONS-archive.md in full.** Use it only through the
scripted and git checks below. Opening a single archived entry by number is
allowed where a check needs its exact wording.

If this prompt disagrees with a spec file, stop and flag it.

---

## Step 1 — Append D60 (the owner's decision, recorded before the audit)

Add a dated heading, `2026-09-23 — Session 66 decision: ...`, then write D60
with these items:

- **D60.1 Audit before Q30.** Before any Q30 branch is chosen, the owner has
  ordered a full audit, run in this order:
  - session 66: documents;
  - session 67: repo and code, including a fresh-environment check;
  - session 68: correctness, meaning a leakage and logic review of the core
    pipeline and a reproduction of recorded results;
  - then triage in the planning chat, then fix sessions.

  Q30 stays open and unchanged (D59.5).
- **D60.2 Verification recompute on the spent years is permitted, once, in
  session 68.**
  - **What it covers.** Re-running the committed code on 2025-26 (F94) and
    2024-25 (F109) is allowed **only to check reproducibility**.
  - **Pre-registered expectation.** Every recomputed figure must match its
    recorded value to the fourth decimal place.
  - **What it is not.** It is not a verdict and not a new look. No variant,
    tuning, selection or new metric is permitted. Every recorded verdict
    (F16/F30/F47/F64/F82, F94, F109) stands, whatever the recompute shows.
  - **If a figure does not match.** The mismatch is reported as a must-fix
    finding for triage. It is not investigated or corrected within session
    68.
  - **Wording conflicts.** Session 68 must first check SPEC section 2, and
    any other rule text, for wording that forbids this. If it finds any, it
    stops and flags it rather than running.
- **D60.3** This session's own read-only scope, as defined above.

## Step 2 — Full read of the live docs

Read CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md and the live DECISIONS.md in
full. Record every instance of the following:

- a **contradiction**, either between two files or within one;
- **stale wording**: text that D59/F109/F110 or later entries have made
  wrong, such as a count of methods, a reserved year described as live or
  unspent, or superseded next steps;
- a **stale process rule**, meaning a CLAUDE.md or SPEC rule that no longer
  matches how the project actually works, for example the planning-chat
  paste habit versus Project knowledge;
- **duplicated or misplaced content**, such as a duplicate heading, or a
  STATUS section that has grown into a log;
- a **direction mismatch**: anything in SPEC's build order (section 6) or
  RESULTS section 7 that conflicts with the current state (three methods,
  programme closed, Q30 open);
- **plain-language problems** that CLAUDE.md's own style rule would flag,
  such as undefined jargon on first use. List only the notable ones.

## Step 3 — Scripted document checks

Write each check as a script, run it, and paste its real output.

1. **Citation resolution.**
   - Extract every citation of the form `Dnn`, `Dnn.m`, `Fnn` and `Qnn`,
     including "Dnn item m", from SPEC, RESULTS, STATUS, CLAUDE, live
     DECISIONS and `docs/*.md`.
   - Resolve each one against its defining entry (the bold `**Dnn.` /
     `**Fnn.` / `**Qnn.` pattern) in live DECISIONS plus the archive.
   - Report every citation that resolves nowhere, and every entry number
     defined more than once. For each entry, also report which file holds
     it.
2. **Numbering.**
   - List the full defined D, F and Q number sequences.
   - Report every gap and every duplicate. Where the record itself explains
     a gap, say so; otherwise list it as unexplained.
3. **Ordering.**
   - The dated headers in live DECISIONS must be in chronological order.
   - The "Moved by session N" blocks in the archive must be in session order.
   - Report any exceptions.
4. **Cross-references.**
   - Every "section X" or "X.Y" reference inside SPEC and inside RESULTS,
     and every "SPEC X.Y" reference from any file, must point to a heading
     that exists.
   - Where the text is short enough to judge, check that the heading's
     subject matches what the reference says. Report mismatches.
5. **Archive criterion.**
   - For each entry still live in DECISIONS, state whether it meets the
     archive rule (CLAUDE.md, D46): settled, codified elsewhere or
     superseded, and not needed word-for-word by a live open question or
     STATUS's "Next".
   - Report which entries are candidates to archive. Move nothing.
6. **Stale-term sweep.**
   - Search every live doc and `docs/*.md` for: "two methods", "two proven",
     "second method", "reserved year" and "held out" used in the present
     tense, "not yet run", and "pending", plus any other term that Step 2
     showed to be stale.
   - Report each hit with its file and line, and whether it is actually
     stale or fine in context.

## Step 4 — Git history checks

1. **Archive integrity.**
   - Run `git log --numstat -- DECISIONS-archive.md` and report every
     commit that shows deletions.
   - For every commit that added to the archive, check whether the lines it
     added match the lines removed from DECISIONS.md in the same commit,
     ignoring the "Moved by session N" header blocks. That is, check that
     each move was verbatim.
   - Report any line that was added but never removed, or removed but never
     added.
2. **Frozen scripts.**
   - From the docs, list every script declared frozen or locked, with its
     cited entry. Examples: `scripts/session62_reserved_confirm.py` and the
     reserved-year guard script.
   - For each one, report its commit history after the commit that froze it.
   - Report any post-freeze change, and whether the record documents it
     (for example F107's pre-look wiring).
3. **Uncommitted state.** Run `git status` at the start of the session and
   report it.

## The report: `notes/audit-session-66.md`

1. **Summary.** Counts of findings by severity.
2. **Findings table.** Each finding has these fields:
   - **ID** (A66-nn);
   - **severity**: **must-fix** (wrong, contradictory, or breaks a
     citation), **should-fix** (stale, misleading or untidy), or
     **cosmetic**;
   - **file:line**;
   - **evidence**: a quoted line or command output;
   - **suggested fix**, which is not applied.
3. **Clean checks.** List every check that came back clean, stated
   explicitly. A clean result is a result.
4. **Appendix.** The full source of every check script and its raw output.

Report only what you verified. If you are unsure whether something is a
finding, list it as **uncertain** and give your reasoning. Do not drop it.

## End of session

1. Paste into chat the report's summary and findings table, plus the
   real output of the git checks.
2. Overwrite STATUS.md as a current-only snapshot. It should say:
   - the audit programme per D60.1, with session 66 done and its report's
     path;
   - Q30 open but deferred until after the audit and fixes;
   - Q32 unchanged.

   It must end with a "Next planning session" line: owner review of the
   session-66 audit report, then drafting session 67 (repo and code audit),
   including a check of `scripts/` size to decide whether subagents are
   warranted for that session only.
3. Run `git status` and show that only these three things changed:
   - `notes/audit-session-66.md` (new);
   - DECISIONS.md (D60 appended);
   - STATUS.md.
4. Write a suggested commit message. Do not commit anything.
