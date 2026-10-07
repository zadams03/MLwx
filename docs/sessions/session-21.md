# Session 21 — one-time housekeeping to cut token load (nothing deleted)

## What this session is

The four living docs are re-read in full every session, so their size is a
per-session cost. This session **relocates settled weight** out of the routinely
re-read files into an archive, and trims duplication — **documentation only, no
data, no model, no pull.**

**The absolute rule: nothing is deleted. Everything must stay reproducible and
available.** There are two independent safety nets:
1. **git history** preserves every prior version of every file;
2. the **archive file** holds the moved content verbatim.
So "move" here means copy-verbatim-to-archive and leave a pointer — never
remove-and-lose.

This is a **one-time authorised restructure.** After it, DECISIONS.md and the
new DECISIONS-archive.md both resume **strict append-only** — this session is
not a precedent for ever rewriting the log again.

Before starting, read CLAUDE.md, SPEC.md, STATUS.md, DECISIONS.md in full.
Critical rules (SPEC 2) apply. **Do not change the meaning of the frozen bar
(SPEC 5) or any active rule.** If any edit would, stop and flag it.

---

## Task 1 — STATUS.md becomes a pure snapshot

STATUS is meant to describe **current state only**, overwritten each session
(this is its original role in CLAUDE.md). It has accumulated history instead.

Rewrite STATUS.md to hold only:
- current stage and a one-line status;
- a compact airport-status line or small table (or a pointer to SPEC 3.4 / 5.0),
  not a re-description of each airport;
- what is done, high-level, pointing to SPEC/DECISIONS for detail rather than
  restating it;
- **what is next** — the immediate next session only;
- the **live** open questions (ones not yet closed).

Remove the accumulated per-session history and stale "Next" blocks. **Nothing is
lost:** every prior STATUS.md is in git history. Note that fact at the top of the
new STATUS (one line: "history in git"). Keep it lean — this file should stop
growing.

## Task 2 — collapse SPEC's repeated per-airport gap paragraphs (authorised)

SPEC 3.2 now carries three near-identical paragraphs — EGLC's 492-hour gap, then
"CDG has the same gap", then "DSM has the same gap" — and Dubbo breaks the
pattern. Replace those repeated paragraphs with **one** general statement:
- the 492-hour gap (2023-12-30 00:00 to 2024-01-19 11:00 UTC), entirely in the
  training window, dropped and counted never filled (2.2);
- **shared hour-for-hour by EGLC, CDG and DSM** (F8, F22, F38) but **not by
  Dubbo**, which has its own scattered gaps instead (Dubbo's finding) — so the
  gap is common to those three but not archive-universal, and per-location gaps
  also exist;
- point to the per-airport DECISIONS findings for the hour-by-hour specifics.

Nothing is lost: the hour-by-hour detail stays in the DECISIONS findings and in
git. Keep the statement accurate and shorter. Also scan the airport-table notes
for any other clear per-airport near-duplication that can be generalised
**without** losing a fact — collapse only unambiguous duplicates; when in doubt,
leave it.

## Task 3 — create DECISIONS-archive.md and move settled blocks (verbatim)

**3a. Create `DECISIONS-archive.md`** with a header: it is the append-only
archive of settled decisions and findings moved verbatim from DECISIONS.md, kept
in full for reproducibility; read it when deep history from a passed stage/
airport is needed.

**3b. Move — verbatim, unedited — only clearly-settled, no-longer-referenced
material:**
- The **founding decisions D1–D12**: their conclusions are now codified as
  active rules in SPEC (D1→§1, D3→§3.1, D4→§2.1b, D5/D8→§3.2, D7→§4.3/D13,
  D9→§4.1, D10→§5, D11→§2.2, D12→§4.4, etc.). The operative rule lives in SPEC;
  the DECISIONS entry is the settled "why". Move them.
- **Early EGLC-only findings** that are settled and not project-wide precedent
  (e.g. F1 and its correction F11 together, the EGLC verify findings, the
  EGLC-only `gfs_seamless` check). 

**3c. KEEP LIVE in DECISIONS.md** (do NOT move):
- every still-active precedent: **D13** (split), **D14** (pairing), **D16**
  (`gfs_global`), **D17** (temp-only), **D18** (validation approach), **D19**
  (features), the locks **D21 / D31 / D35**, **D22** (qualitative bar), and the
  airport-opening / convention decisions **D26, D27, D30, D32, D33, D36, D37**;
- the **results of record** F16, F30, F47 (referenced for cross-airport
  comparison);
- **project-wide findings** still in play (the 492-hour gap findings, the
  `gfs_seamless`-differs-at-DSM finding, Dubbo's differing-gap finding);
- **all Dubbo (in-progress) material** and **all still-open questions**.

**3d. Leave a one-line pointer** in DECISIONS.md wherever a block was moved,
e.g.: "[D1–D12 and early EGLC findings F1–Fn archived verbatim to
DECISIONS-archive.md — settled founding decisions, now codified in SPEC §§1–5.
Full text preserved there and in git.]"

**3e. When in doubt, keep it live.** A slightly larger live file is fine; a lost
precedent is not. Moved blocks must be **byte-for-byte identical** to the
originals — this is a relocation, not an edit.

## Task 4 — update CLAUDE.md

- Note the living docs are SPEC, STATUS, DECISIONS (read in full each session, as
  now), plus **DECISIONS-archive.md**, which is read **only when a session needs
  deep history from a passed stage or airport** — not routinely.
- Note STATUS is a **snapshot overwritten each session**; its history is in git.
- Keep the existing "read the live docs in full at the start of every session"
  rule — it is important for correctness; the files are simply lighter now.

---

## What to report at the end

- STATUS before/after (and its new length vs old);
- the SPEC 3.2 before/after;
- **a full list of exactly which DECISIONS entries moved and which stayed**, with
  a one-line reason each, so the owner can verify no active precedent left the
  live file;
- confirmation each moved block is byte-for-byte identical in the archive;
- confirmation (git) that nothing is lost and everything remains recoverable;
- the CLAUDE.md before/after;
- confirmation the frozen bar's meaning and every active rule are unchanged.

## What NOT to do

- Do not delete anything anywhere. Move = copy-verbatim + pointer.
- Do not edit the *content* of any moved decision/finding — relocation only.
- Do not move any active precedent, result of record, project-wide finding,
  open question, or Dubbo material (Task 3c).
- Do not change the meaning of the frozen bar or any active rule.
- Do not pull data, build, train, or evaluate anything.
- Do not commit anything.
- Anything ambiguous → keep it live and note it, do not move it.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md (its Task-1 rewrite doubles as this) to show the next
   session is Dubbo's join + validation rehearsal.
2. Append one DECISIONS.md entry recording this one-time restructure (what moved,
   that git + archive preserve everything, and that append-only resumes).
3. Run a consistency check across SPEC, STATUS, DECISIONS **and**
   DECISIONS-archive.md — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
