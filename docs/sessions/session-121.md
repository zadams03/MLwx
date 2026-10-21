# Session 121: project health check, audit part 2 (the record)

Recommended model: Opus (consistency judgement across the record).

This session audits the record, read-only, under D114.3 and D114.4. It
records D115, audits SPEC, STATUS, DECISIONS, RESULTS, ANALYSIS, the
READMEs, CLAUDE, `docs/PROJECT-INSTRUCTIONS.md`, every citation in them and
the Project-knowledge sync, writes a register in session 120's format, and
records F164. Nothing is fixed.

## Read first

- `STATUS.md` and SPEC section 2 (always, D93.16).
- `DECISIONS.md`, the live file, in full (this session records D115 and F164).
- `notes/session-120-register.csv` in full (the register format, D114.7) and
  the summary at the top of `notes/session-120-output.txt` (at most 30 lines).
- `docs/PROJECT-INSTRUCTIONS.md` in full (it is audited in Step 7).
- Archived entries only when a step names them, one entry at a time by line
  range (D93.12): D90.4, D90.6, D91.3, D92.2, D98.2.

Every other file is read in the step that audits it, and only as far as that
step needs.

## Limits

- D114.4 applies in full. No existing tracked file is edited except
  `DECISIONS.md`, `DECISIONS-archive.md` (archive step only) and `STATUS.md`.
- No network. No GRIB cache. No 2026-27 value is read or scored, no MLwx-live
  file is read, no error is computed (D105.6).
- The only frozen-script runs allowed are stage B's three `--guard-check`
  modes (Step 3), as in session 120's C01.
- `DECISIONS-archive.md` is never read in full: checks run by script, and
  single entries are read by line range.
- Scripts print short summaries; full lists go to files (D93.12).

## Scope (files this session may create or edit)

- Edit: `DECISIONS.md`, `DECISIONS-archive.md` (archive step only),
  `STATUS.md` (overwrite).
- Create: `scripts/session121_audit.py`, `data/processed/session121_audit/`
  (any files inside), `notes/session-121-register.csv`,
  `notes/session-121-output.txt`.
- Nothing else. `docs/sessions/session-121.md` is the only untracked file
  expected at the start.

## Register (D114.7)

`notes/session-121-register.csv` has session 120's columns, in its order:
`id,area,file,checked,result,severity,proposed_fix,touches_record,touches_frozen,touches_live_test,needs_owner_ruling`.
Severity is one of OK, cosmetic, stale, wrong, blocks. Rows that pass are
kept as OK. Ids use two-letter prefixes so they never clash with session
120's: CI citations, SP SPEC, ST STATUS, DE DECISIONS, RE RESULTS, AN
ANALYSIS, RM READMEs, CL CLAUDE, PI PROJECT-INSTRUCTIONS, PK the sync. A row
that repeats an item already in session 120's register cites its id and adds
nothing new.

---

## Step 0. Start

Check: HEAD is `b4d3eb5`; the tree is clean apart from the untracked
`docs/sessions/session-121.md`; `.venv/bin/python -m unittest discover -s
tests` runs OK (record the count). Report the byte size of `DECISIONS.md`.

Stop if HEAD differs, the tree has other changes, or a test fails.

## Step 1. Record D115

Append the text between the two marker lines below to the end of
`DECISIONS.md`, copied with `sed` (CLAUDE.md), with one blank line and `---`
before it as for every entry. Do not change the Live index yet (the archive
step applies D115.8).

Check: the appended block is byte-equal to the source (`diff` and `cmp`),
and has 0 em-dashes.

Stop on any difference.

<!-- D115 start -->
## 2026-10-21: Session 121 decision: F163 accepted, the Project-knowledge sync, and the record audit's scope (owner, planning chat)

**D115. Owner decisions, planning chat (after session 120's commit): F163 accepted; the hand upload made the standard for Project knowledge; the archive's place there; session 121's scope; a candidate for the longer-term plan; and Live index changes.** Written at the start of session 121, before any other edit. No 2026-27 value has been read or scored.

- **D115.1 F163 accepted,** with its review correction (F163.5 reads "every other stage C gate passes"), its readings (F163.11) and its grouping of fixes (F163.10), which stay open for the fix sessions.
- **D115.2 Project knowledge (owner; amends D93.15(b)).** The hand upload is the standard. After the owner commits and pushes a reviewed session, the planning chat lists each changed file that Project knowledge holds, with its byte size in the repo; the owner uploads each by hand and checks its size. Why: the staging tool that `docs/PROJECT-INSTRUCTIONS.md` section 5 relies on was missing from the planning chats after sessions 119 and 120, and reading the files through the Filesystem extension would put their contents into the chat. `ANALYSIS.md` is one of the files Project knowledge holds; section 5's list omits it, and the copy there dated from 2026-10-14 until the owner re-uploaded it on 2026-10-21. Section 5 is edited in a fix session.
- **D115.3 The archive's place.** Project knowledge holds `DECISIONS-archive.md` at its root, not at `claude/DECISIONS-archive.md` as section 5 says. Section 5's text is corrected in a fix session; the file is not moved.
- **D115.4 Session 121's scope (D114.3; read-only under D114.4).** The record: SPEC, STATUS, DECISIONS (the archive by script and by entry, never read in full, D93.12), RESULTS, ANALYSIS (its text against DECISIONS only; its numbers are register rows C08 and C09's), the root README and the READMEs in `scripts/`, `data/`, `docs/` and `notes/`, CLAUDE, `docs/PROJECT-INSTRUCTIONS.md`, every citation in them, and the sync. SPEC 3.4's two markers and its table format are recorded as fixed for every later edit (register S05). The register follows D114.7. No network, no GRIB cache, and no frozen script beyond stage B's `--guard-check` modes.
- **D115.5 What the planning chat saw in Project knowledge (2026-10-21).** Eight documents at its root, with these listed dates: ANALYSIS.md, DECISIONS.md and STATUS.md 2026-10-21; DECISIONS-archive.md 2026-10-18; PROJECT-INSTRUCTIONS.md, SPEC.md and CLAUDE.md 2026-10-07; RESULTS.md 2026-09-29. The archive's copy is 1,497,010 bytes, the same as the repo's, although its listed date is older than the repo's last change to it, so a listed date does not show whether a copy is current. The reported knowledge size was 657,869 after ANALYSIS.md's upload, below the archive's own byte count, so it is not a byte count.
- **D115.6 A candidate for the longer-term plan (D112.2 item 5; owner).** Does the curve's correction (curve minus raw GFS) for a valid hour predict the direction and size of raw GFS's revision for that same hour in the next cycle (the next cycle's raw GFS minus this cycle's)? Descriptive first, on spent stage C rows (D107.2's terms), with its rows, pairing and statistics fixed in its own entry before any value is computed. Nothing is read for it in session 121.
- **D115.7 Plan.** Session 121: this entry, the record audit, F164. Then fix sessions planned from both registers (F163.10's grouping with F164's additions), each with its own entry; the README update last (D112.2 item 4). The issue lag after the redeploy is re-measured in the MLwx-live fix session (F163.8).
- **D115.8 Live index.** Removed (archived): D108, D111, D113, F157, F160, F161 and F162, which are settled (IFS is closed by D113 and F162; the comparisons and the live-run audit are recorded and accepted). Added: D115 and F164 (F164 when it is written). After session 121: D93, D103, D105, D112, D114, D115, F163, F164.
<!-- D115 end -->

## Step 2. Citations

Run `python3 scripts/archive_decisions.py --citations`. Then, in the new
script, extend the check to every audited file: SPEC, STATUS, RESULTS,
ANALYSIS, the READMEs of Step 6, CLAUDE and `docs/PROJECT-INSTRUCTIONS.md`.
Every (Dxx), (Fxx) or bare Dxx/Fxx reference must resolve to an entry in
either DECISIONS file; a reference to a sub-item (D105.5(k), F163.10) must
resolve to that item's label inside the entry.

Check: counts per file of references, resolved and unresolved; the full list
in `data/processed/session121_audit/citations.csv`. One CI row per file.

Stop only if the script itself fails.

## Step 3. SPEC

(a) **Stage B's markers (register S05).** `**3.4 The airport table.**` and
`Notes on the table:` each appear exactly once. Record the SHA-256 and line
range of the span from the first marker line to the second, so that every
later SPEC edit can check the span is unchanged. Parse the table in that span
independently (row count, column count, the six station codes) and run stage
B's three `--guard-check` modes as in C01.

(b) **SPEC against DECISIONS.** Statements of current state or rule that a
later entry changed: for example section 1's airport list and end goal,
section 6's roadmap (stages B, C and G, and the live product, D103, D105,
D113.2), section 9 against D100 to D102. SPEC wins over other files (SPEC
section 2), but where a later D entry amended a rule SPEC still states, it is
a stale row.

Check: SP rows for (a) and each finding in (b), each with the entry that
dates it and a proposed fix that keeps the span of (a) byte-equal.

Stop if a marker is missing or a guard-check fails.

## Step 4. STATUS

Audit the committed STATUS (session 120's), before it is overwritten: every
statement traces to an entry; each open question is still open (not closed
by a later entry); the "Next planning session" line is present.

Check: ST rows.

## Step 5. DECISIONS

Live file: the Live index matches the entries present; entries are in order,
dated and unduplicated (the script); each live entry's open items are still
open or closed by a named later entry. Archive: by script only (order,
duplicates, every number once across both files). D93.9's size rule.

Check: DE rows.

## Step 6. RESULTS, ANALYSIS and the READMEs

(a) **RESULTS.** Statements of state against DECISIONS (section 7's roadmap,
the open item of D93.4, "Stage G comes next"); the revision footer; 20
numbers chosen evenly through the file, each checked against the entry it
cites.

(b) **ANALYSIS.** Text only (D115.4): the header and status, Part 1's
statements and Part 3's candidates against F155, F157, F160 and F162, and
every file path it names exists. No number is re-checked.

(c) **READMEs.** The root `README.md` and the READMEs in `scripts/`, `data/`,
`docs/` and `notes/`: every path named exists; the layout map against D91.3
and the additions traced in L02 to L07; statements of state against STATUS
and DECISIONS. `tests/README.md` and `deploy/mlwx-live/README.md` are T04 and
M02 already; list any other tracked README and say whether it was audited.

Check: RE, AN and RM rows.

## Step 7. CLAUDE and PROJECT-INSTRUCTIONS

(a) **CLAUDE.md** against D93.8 to D93.16, D97.3, D98.2 and D62.3(a); its
test command against T02; its end-of-session steps against
PROJECT-INSTRUCTIONS sections 4, 6 and 7.

(b) **`docs/PROJECT-INSTRUCTIONS.md`** against D93.13, D93.15, D93.16 and
D115.2 to D115.3: section 2's table (which files it lists), section 4's
Filesystem paragraph against the extension's current reach (the MLwx-all
folder, per the owner's set-up), section 5's file list, archive path and size
rule, section 8, section 9 against SPEC 2.5 and D105.5, and that section 4's
invocation equals D93.16's character for character.

Check: CL and PI rows.

## Step 8. The Project-knowledge sync

From D115.5: for each of the eight files, its repo byte size and SHA-256 at
HEAD and the commits that changed it after its listed date. A file with no
such commit is "current"; one with any is "check: compare byte sizes" (a
listed date proves nothing either way, D115.5). Also: section 5's file list
against the eight; the eight files' total bytes; a reading on section 5's
2 MB and 1.6 MB rule, given that the reported knowledge size is not bytes.

Check: one PK row per file plus rows for the list, the size rule and the
procedure (D115.2, D115.3).

## Step 9. F164 and the grouping

Write F164 (D93.10, at most about 40 lines): what was done, the register's
counts by severity, the headline findings, the proposed grouping of fixes
(F163.10's six groups with this register's rows added to them, and any new
group), readings for the owner, what was not done, pointers.

Check: F164 cites every register id it groups; 0 em-dashes.

## End of session (CLAUDE.md)

1. Real output: every check above with its real numbers.
2. Overwrite STATUS.md as a current-only snapshot. Carry forward the open
   questions still open, including F163.8's issue lag and D115.6's
   candidate. It ends: "**Next planning session:** Review session 121 and
   commit; then plan the first fix session from both registers (F163.10 and
   F164)."
3. Archive step: add F164 to the Live index and apply D115.8, then run
   `python3 scripts/archive_decisions.py --apply --session 121`.
4. Checks: `--citations`; re-read only what this session changed in STATUS
   and DECISIONS; DECISIONS.md's byte size (above 80,000 is a finding); the
   scope-list check against `git status`. Report only.
5. Output file `notes/session-121-output.txt`: a summary of at most 30 lines
   first (including the consistency-check findings), then the checkpoints and
   detail. Report the same summary in chat. Stop and wait for review. Do not
   commit.
