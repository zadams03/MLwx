# Session 99: workflow overhaul (D93)

Suggested model in Claude Code: Opus (this session rewrites the standing
rules and splits the record; later mechanical sessions can use Sonnet).

## Purpose

Cut the reading cost of every session and stop DECISIONS.md growing back.
Record D93; replace CLAUDE.md; make eight edits to
docs/PROJECT-INSTRUCTIONS.md; add a Live index to DECISIONS.md and move every
entry outside it to DECISIONS-archive.md with a checked, reusable script;
check that every citation still resolves; record F142.

No model is fit. No data file, existing script or workflow file is touched.
No 2026-27 value is read. SPEC.md, RESULTS.md and README.md are not edited.

## Files this session may create or edit (scope list)

- New: `scripts/archive_decisions.py`, `notes/session-99-output.txt`.
- Edited: `DECISIONS.md`, `DECISIONS-archive.md`, `CLAUDE.md`,
  `docs/PROJECT-INSTRUCTIONS.md`, `STATUS.md`, `scripts/README.md` (one
  added line only).
- Untracked already: `docs/sessions/session-99.md` (this file; do not edit).

Any other changed or new file is a scope breach: report it, do not hide it.

## Read first

- `STATUS.md` in full.
- `SPEC.md` section 2 only.
- `DECISIONS.md`: not in full (see the owner's exception below); only the
  lines each step names.
- `docs/PROJECT-INSTRUCTIONS.md`: only the sections Step 3 edits, found by
  their headings.

## How to work in this session (the new guardrails, used here first)

- Before each step, re-read that step here. After each step, append one
  checkpoint line to `notes/session-99-output.txt`: step, what was done,
  files changed, check PASS or FAIL.
- If a step's check fails, or anything here disagrees with SPEC, CLAUDE.md
  or a DECISIONS entry: stop and report. Do not work around it.
- Do not print large files or outputs into the conversation. Use `wc`,
  `grep`, `head`, `diff -q`, `cmp` and scripts that print summaries; full
  tables go to the output file.
- Never read `DECISIONS-archive.md` in full. Use `wc`, `tail` and `grep`.
- **Owner's exception to the routine read, for this session only:** do not
  read `DECISIONS.md` in full, and read only section 2 of `SPEC.md`. This
  session edits DECISIONS.md only by `sed` and by the script, and does not
  touch SPEC. Read only the DECISIONS lines a step needs: the last two
  entries for Step 0 (`tail`, `grep -n`), and the file's first lines up to
  its first `---` for Step 5. This is not a disagreement with CLAUDE.md to
  stop on: it is the owner's instruction, also given in the invocation.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-99.md`.
- The last entries in DECISIONS.md are D92 and F141. No D93 or F142 exists in
  either DECISIONS file (`grep -c`). `scripts/archive_decisions.py` and
  `notes/session-99-output.txt` do not exist.
- Record in the output file the byte size and SHA-256 of DECISIONS.md,
  DECISIONS-archive.md, CLAUDE.md, docs/PROJECT-INSTRUCTIONS.md, SPEC.md and
  STATUS.md.
- Stop if any of this differs.

## Step 1: record D93

Copy the block between the markers `<<<D93-START>>>` and `<<<D93-END>>>`
below (markers excluded) to the end of DECISIONS.md with `sed`, after a line
`---` and a blank line, as earlier sessions did. Check byte equality with
`diff` and `cmp` against the block. Em-dashes in the copy: must be 0.

<<<D93-START>>>
## 2026-10-09: Session 99 decision: F141 accepted, the session order, and a workflow overhaul (owner, planning chat)

**D93. Owner decisions, planning chat (after session 98c): F141 accepted,
three carried items, GFS v17, the session order, and a workflow overhaul
that cuts the reading cost of each session.** Written at the start of
session 99, before any other edit. No 2026-27 value has been read or
scored.

- **D93.1 F141 accepted,** with all nine F141.7 readings.
- **D93.2 The invocation.** The claude.ai Project instructions and section
  4 of `docs/PROJECT-INSTRUCTIONS.md` both give D92.4's invocation, with
  `docs/sessions/session-NN.md` (planning-chat check, 2026-10-09).
- **D93.3 lightgbm.** From D90.9 and F140.7, new scripts may import
  lightgbm directly, with no libomp shim.
- **D93.4 RESULTS.md section 7.** Its roadmap paragraph is out of date
  (F140, F141). It is fixed once, in the session that closes D82.5's
  model-structure comparisons, so that it is edited with their outcome.
  Until then it stays an open item.
- **D93.5 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-09, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-91 (6 October 2026).
  With 30 days' notice the earliest go-live is about 8 November 2026. Also:
  SCN 26-47 (updated) now ends NAM MOS on 3 November 2026, not 14 October
  as D77.1 and F127's correction give. NAM MOS was already excluded
  (D77.1), so nothing changes.
- **D93.6 Session order (amends D90.3).** Session 99 is this workflow
  overhaul. The first of D82.5's alternatives against the baseline
  (D89.10) moves to session 100. Its open choices (which alternative
  first, the rule if both alternatives beat the baseline, the model
  settings, and how the cycle hour is encoded) are fixed in session 100's
  own entry, before any score. Nothing else in D89 changes.
- **D93.7 Why the archive step stopped working.** DECISIONS.md had grown
  to 343,813 bytes (about 4,100 lines), against 773 lines after D46, and
  the archive was last changed on 2026-09-29. The end-of-session archive
  step existed, but: (a) its criterion kept any entry still cited by
  STATUS or by a live entry, and each new entry cites recent ones, so
  recent entries never became movable; (b) its default was "when in
  doubt, keep live" (D46); (c) Claude Code applied it alone each session,
  often by repeating an earlier session's reasons, and the planning-chat
  review accepted "nothing moved" without checking the file's size; (d)
  finding entries copied full tables already held in the output files.
  The step checked a criterion but never its outcome. D93.8 to D93.10
  replace it with an explicit list and a size limit checked every
  session.
- **D93.8 The live file (replaces D46's criterion).** DECISIONS.md opens
  with a Live index: the entries in force for current work. The owner
  changes the index only through a DECISIONS entry; a session adds its own
  new entries to it. At the end of every session, every entry not in the
  index moves verbatim to DECISIONS-archive.md, by
  `scripts/archive_decisions.py`. Being cited elsewhere is not a reason to
  keep an entry live: a citation resolves by number in either file, and an
  archived entry is still binding. The index after session 99: D47, D73,
  D77, D79, D82, D88, D89, F139, D93 and F142. D62 is archived; its rule
  that frozen scripts are never edited (D62.3(a)) stands, restated here:
  `session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py` and `session62_reserved_confirm.py` are
  never edited.
- **D93.9 Size limit.** Every session reports the byte size of
  DECISIONS.md after its archive step. Above 80,000 bytes is a
  consistency finding that the next planning session must act on.
- **D93.10 Finding entries.** A finding is at most about 40 lines: what
  was done, the numbers a decision needs, readings for the owner, what was
  not done, and a pointer to the output file. Full tables, lists and logs
  stay in `notes/session-NN-output.txt`, which begins with a summary of at
  most 30 lines.
- **D93.11 Long sessions and their guardrails.** Sessions may be longer
  and cover more, so that fewer sessions pay the start-up reading. In
  return each prompt lists the files the session may create or edit,
  checked against `git status` before the end steps; Claude Code writes a
  checkpoint line after each step, stops rather than works around a failed
  check, and after any mid-session compaction re-reads CLAUDE.md, the
  prompt and its checkpoints before going on.
- **D93.12 Keeping context small.** Claude Code does not print large files
  or outputs into the conversation; scripts print short summaries and
  write full tables to files; the archive is never read in full, only one
  entry at a time by line range.
- **D93.13 The planning side** (`docs/PROJECT-INSTRUCTIONS.md`). The
  planning chat reads its guide and STATUS in full; SPEC, CLAUDE and
  DECISIONS by targeted search unless the session being planned edits
  them; DECISIONS-archive.md is uploaded to Project knowledge for search
  only; the GFS v17 check is the weekly task of D93.15; reviews start
  from the output file's summary and checkpoints.
  Related work is combined into fewer, fuller sessions, and the planning
  chat recommends a Claude Code model for each.
- **D93.14 Session 99's plan.** Record this entry; replace CLAUDE.md; edit
  `docs/PROJECT-INSTRUCTIONS.md`; add the Live index; move every entry
  outside it to the archive with a checked script; check that every
  citation still resolves; record F142. No model, data file or existing
  script is touched.
- **D93.15 Two planning-side automations.** (a) A weekly scheduled task
  (Mondays, 08:57 London time) searches for a GFS v17 Service Change
  Notice and alerts the owner only when it finds one. Planning chats no
  longer re-check v17; a D entry mentions v17 only when the task has
  found a notice. (b) After the owner commits and pushes a reviewed
  session, the planning chat copies the changed files into claude.ai
  Project knowledge itself, from the linked computer, without their
  contents entering the chat (`docs/PROJECT-INSTRUCTIONS.md` section 5).
  The owner no longer re-uploads by hand, except when the planning chat
  reports that a sync failed.
- **D93.16 What each session reads, and the invocation (replaces
  D92.4's).** Each session prompt begins with a Read first section that
  lists what Claude Code reads before the steps: files in full, SPEC
  sections, and DECISIONS entries by number, live or archived. STATUS.md
  and SPEC section 2 are always read. With no list, the default is
  STATUS.md, SPEC section 2 and the live DECISIONS.md in full. A step
  that needs something not read reads just that part and notes it in its
  checkpoint. CLAUDE.md is loaded automatically and is not read again. So
  the invocation is fixed: "Carry out the session defined in
  docs/sessions/session-NN.md: first read what its Read first section
  lists, then do its steps, staying strictly within its scope. Stop at
  the end-of-session steps and wait for my review. Do not commit
  anything." Each session starts in a fresh Claude Code conversation (a
  new terminal or `/clear`): carrying a finished session's context into
  the next costs more than the short start-up read and blurs the review
  boundary.
<<<D93-END>>>

## Step 2: replace CLAUDE.md

Replace the whole of CLAUDE.md with the block between `<<<CLAUDE-START>>>`
and `<<<CLAUDE-END>>>` (markers excluded), extracted with `sed`. Check byte
equality with `diff` and `cmp`. Em-dashes in the new file: count and report
(the title line and the "two roles" and "three files" passages carried from
the old file may keep theirs; new text has none). Put `git diff --stat --
CLAUDE.md` in the output file.

<<<CLAUDE-START>>>
# CLAUDE.md: standing rules for every session

Claude Code reads this automatically at the start of every session. These
rules apply every time, so they are not repeated in each session prompt.

Keep all writing plain: simple words, short sentences, define jargon on first
use. This applies to code comments, the spec files, and chat replies.

Do not use the em-dash (the long dash) in any new text: use a colon, a
comma, brackets or a new sentence instead. Existing text is not edited
to remove it (DECISIONS D76.6).

---

## The two roles

- **The owner** (the human) plans, researches, makes decisions, writes the
  session prompts, reviews all code, and saves it to version control by hand.
- **Claude Code** writes all the code. It does not decide what the project
  should do and does not plan the project on its own. It follows SPEC and the
  current session prompt.

## What to read (D93.16)

CLAUDE.md (this file) is loaded automatically; do not read it again.

Every session prompt begins with a **Read first** section listing what to
read before the steps: which files in full, which SPEC sections, and which
DECISIONS entries (live or archived, by number). Read exactly that. Always
read STATUS.md and SPEC section 2 (the critical rules), even if the list
leaves them out. If a prompt has no list, read STATUS.md, SPEC section 2
and the live DECISIONS.md in full.

If a step turns out to need a rule or entry you have not read, read just
that part, note it in the step's checkpoint line, and carry on. Never act
on a remembered or guessed rule.

## The files

1. **SPEC.md**: the source of truth for how the project should work.
2. **STATUS.md**: a snapshot, overwritten each session: current stage, what
   is next, and live open questions. Not a growing log; its history is in git.
3. **DECISIONS.md**: the live log. It holds only the entries in its Live
   index (D93.8). New entries are appended at the bottom.

Read on demand only, never routinely:

- **DECISIONS-archive.md**: every settled entry, verbatim and still binding.
  **Never read it in full.** To read an archived entry, find its first line
  with `grep -n` (for example `grep -n '^\*\*D62\. ' DECISIONS-archive.md`;
  the space after the full stop skips sub-items such as `**D62.1`),
  then print only that entry's lines. Entry numbers never change, so every
  citation resolves in one of the two files.
- **RESULTS.md**: the reader-facing summary. Never a source of truth.
- **Earlier output files in `notes/`**: read only the lines a step needs.

**PROJECT-INSTRUCTIONS.md** (in `docs/`) is the planning chat's guide.
Claude Code does not follow it and edits it only when a session prompt says
exactly what to change.

The **critical-rules section of SPEC (section 2)** applies to every session,
whether or not the session prompt repeats it. It is non-negotiable.

## One session, one scope

Each session does exactly what its session prompt defines, nothing more. A
session may be long and have many steps; its scope is still only those
steps. If something outside the scope looks broken or worth doing, do not
fix it: report it in the output file as an open question. The owner decides.

## Guardrails inside a session (D93.11)

- **Scope list.** Each prompt lists the files the session may create or
  edit. Before the end-of-session steps, run `git status --porcelain` and
  compare. Any other changed or new file is reported as a scope breach, not
  silently reverted.
- **One step at a time.** Before each numbered step, re-read that step in the
  prompt. After it, append one checkpoint line to
  `notes/session-NN-output.txt`: step, what was done, files changed, and
  whether its check passed.
- **Stop on failure.** If a check fails, or the prompt disagrees with SPEC
  or a DECISIONS entry, stop and report. Do not work around it, and do not
  retry with a changed method unless the prompt allows it.
- **After a compaction.** If the conversation is compacted (summarised)
  mid-session, re-read CLAUDE.md, the session prompt and the checkpoints
  before going on. Re-read other files only if the next step needs them.

## Keeping context small (D93.12)

- Never print a large file or a long output into the conversation. Use
  `wc`, `grep`, `head`, `tail`, `diff -q`, `cmp`, or a script that prints a
  summary.
- Scripts print a short summary to the terminal (counts, headline numbers,
  PASS or FAIL) and write full tables to the output file or a data file.
- Beyond the routine read, read only the parts of files a step needs,
  unless the prompt says to read a file in full.

## Source of truth and conflicts

- **SPEC beats code.** If code and SPEC disagree, SPEC is right. Either fix
  the code to match SPEC, or change SPEC on purpose and note the change in
  DECISIONS. Never let them drift apart quietly.
- **Uploaded beats remembered.** A planning chat works only from the current
  files in claude.ai Project knowledge. If an uploaded file contradicts
  memory or an old chat copy, the uploaded file wins.
- **Never edit a spec file from memory or assumption.** Edit a spec file only
  where the session prompt or the owner explicitly says to, and only with
  content from this session's real work.
- **If the session prompt and a spec file disagree, stop and flag it.** Do
  not guess which to follow.

## Handling inputs and data

- Never change raw, original inputs in place. Keep them untouched in
  `data/raw/` and work on copies.
- Never silently fill missing data. Mark the gaps, count them, report them.
  Any filling-in must be explicitly asked for in the session prompt.
- Because the data sources are live services that can revise data, record the
  pull date and exact query with each raw file, and treat it as a fixed
  snapshot.
- Frozen scripts are never edited (D62.3(a), restated in D93.8).

## Writing DECISIONS entries (D93.10)

- A **decision (D) entry** is copied from the session prompt exactly, with
  `sed`, and checked byte-equal.
- A **finding (F) entry** is at most about 40 lines: what was done, the
  numbers a decision needs, readings for the owner, what was not done, and a
  pointer to the output file. Full tables, lists and logs stay in
  `notes/session-NN-output.txt`.

## Commit discipline

Claude Code **never** commits, adds, or pushes to version control. It
prepares all changes, then stops. It does not write a commit message:
after reviewing the session, the planning chat writes it to
`docs/commits/commit-NN.txt`, and the owner commits by hand with
`git commit -F docs/commits/commit-NN.txt`. Nothing enters the project's
history without a person looking first.

## End of every session

1. **Real output.** Run the session's checks and paste the real numbers, not
   a description of them.
2. **Overwrite STATUS.md** as a current-only snapshot: present state, the
   immediate next action, and live open questions. Never append this
   session's write-up to a log. It ends with a "Next planning session" line.
3. **Archive step (D93.8).** Add this session's own new entries to the Live
   index, and make any index change the session's D entry gives. Then run
   `python3 scripts/archive_decisions.py --apply --session NN`. Every entry
   not in the index moves verbatim to DECISIONS-archive.md. Being cited is
   not a reason to keep an entry live.
4. **Checks.** Run `python3 scripts/archive_decisions.py --citations`; it
   also reports duplicated entries and entries out of order. Re-read only
   what this session changed in SPEC, STATUS and DECISIONS (not the whole
   files) and report anything there that disagrees with the rest of the
   record. Report the byte size of DECISIONS.md: above 80,000 bytes is a
   finding (D93.9). Run the scope-list check. Report only; do not fix
   silently.
5. **Output file.** `notes/session-NN-output.txt` begins with a summary of at
   most 30 lines: what was done, every check with PASS or FAIL, the headline
   numbers, readings for the owner, scope and size checks, and open items.
   The checkpoints and full detail follow it. Report the same summary in
   chat.

## Session prompts

Work happens in sessions. Each has a session prompt file the owner writes,
kept in `docs/sessions/`, giving a clear record of what was asked each time.
<<<CLAUDE-END>>>

## Step 3: edit docs/PROJECT-INSTRUCTIONS.md

Make exactly these eight changes, (a) to (h). Each section is located by its heading line
(a line starting `## N.`) and runs to the line before the next `## ` heading.
If any heading or bullet is not found exactly once, stop and report. Put
`git diff -- docs/PROJECT-INSTRUCTIONS.md` in the output file.

(a) Replace the whole of section 2 (from `## 2. Where the truth lives` up to,
not including, the `---` line before `## 3.`) with the block between
`<<<PI2-START>>>` and `<<<PI2-END>>>`.

(b) Replace the whole of section 3 (from `## 3. Start-of-chat protocol` up to,
not including, the `---` line before `## 4.`) with the block between
`<<<PI3-START>>>` and `<<<PI3-END>>>`.

(c) Replace the whole of section 5 (from `## 5.` up to, not including, the
`---` line before `## 6.`) with the block between `<<<PI5-START>>>` and
`<<<PI5-END>>>`.

(d) Replace the whole of section 7 (from `## 7. How to review a session` up
to, not including, the `---` line before `## 8.`) with the block between
`<<<PI7-START>>>` and `<<<PI7-END>>>`.

(e) In section 9, replace the bullet that starts `- **Archive-as-you-go.**`
(all its lines, up to the next line that does not start with two spaces)
with this one line:
`- **Archive by the Live index.** In each session's end steps, every DECISIONS entry outside the Live index moves to the archive (D93.8). The live file stays under 80,000 bytes (D93.9).`

(f) Insert the block between `<<<PI11-START>>>` and `<<<PI11-END>>>` as a new
section 11, after section 10 and its `---` line, before the closing italic
line that starts `*This guide is itself a file`. End it with a `---` line.

(g) In section 4, replace the line `5. **Give the re-upload reminder** (see §5).`
with `5. **After Zac commits and pushes, sync Project knowledge** (section 5).`,
and in the next line replace `Zac commits, re-uploads the named docs, and starts`
with `Zac starts`.

(h) In section 4, replace the paragraph that starts `The invocation Zac pastes
into Claude Code` (up to the next blank line) with:
`The invocation Zac pastes into a fresh Claude Code conversation is fixed (D93.16); only the number changes: Carry out the session defined in docs/sessions/session-NN.md: first read what its Read first section lists, then do its steps, staying strictly within its scope. Stop at the end-of-session steps and wait for my review. Do not commit anything.`

<<<PI2-START>>>
## 2. Where the truth lives

| File | Role | Authority |
|---|---|---|
| `SPEC.md` | How the project works: method, rules, the three proven methods (section 8 is the default recipe) | **Source of truth.** Where anything disagrees, SPEC wins. |
| `STATUS.md` | Current state and the immediate next action | Read in full every chat. Overwritten each session. |
| `DECISIONS.md` | The live log: only the entries in its Live index (D93.8) | The binding record, cited as (Dxx)/(Fxx). |
| `DECISIONS-archive.md` | Every settled entry, verbatim | Still binding. In Project knowledge for search only; never read in full. |
| `RESULTS.md` | The results narrative (all three methods) | Draws from SPEC/DECISIONS; read only when needed. |
| `CLAUDE.md` | Claude Code's execution discipline | Governs sessions, not planning. |
| `PROJECT-INSTRUCTIONS.md` | This guide: how planning chats work. Kept in docs/ | Planning side only. Claude Code edits it only when a session prompt says exactly what to change. |
| Project **memory** | Durable reasoning and preferences | Inherited automatically by every chat. |

Claude Code reads what each session prompt's Read first section lists
(D93.16). The planning chat reads by need (section 3).

<<<PI2-END>>>

<<<PI3-START>>>
## 3. Start-of-chat protocol (do this first, every chat)

1. **Read this guide and STATUS.md in full.**
2. **Staleness check: the critical guard.** Cross-check STATUS against
   memory. If memory reflects a more recent session than STATUS shows, the
   uploaded docs are stale. Stop and tell Zac to re-upload the current files
   before doing any work. Stale docs look authoritative but are not.
3. **Read STATUS's "Next planning session" line** (section 6) and start there,
   not from a blank slate.
4. **Read the rest by need.** Use project_search for the SPEC sections and
   DECISIONS entries the next session depends on, archived ones included.
   Read SPEC, CLAUDE or DECISIONS in full only when the session being planned
   will edit that file. Never read DECISIONS-archive.md in full.
5. **GFS v17:** no check in the chat. A weekly scheduled task does it and
   alerts Zac when a notice appears (D93.15). Ask Zac only if the next
   session depends on the go-live date.

<<<PI3-END>>>

<<<PI5-START>>>
## 5. Syncing Project knowledge (anti-staleness: you own this)

After Zac has committed and pushed a reviewed session, **the planning chat
copies every changed file into Project knowledge itself** (D93.15). Never
sync before the commit: Project knowledge must match the committed repo.

- **Which files:** `STATUS.md` every session; `DECISIONS.md` and
  `DECISIONS-archive.md` whenever they changed (almost every session);
  `SPEC.md`, `RESULTS.md`, `CLAUDE.md` and `docs/PROJECT-INSTRUCTIONS.md`
  (kept in Project knowledge as `PROJECT-INSTRUCTIONS.md`) only when the
  session edited them.
- **How:** stage each file from the linked computer into the workspace,
  copy it into the working directory, and write it with project_write's
  `local_path` to the same Project-knowledge path, so its contents never
  enter the chat. Then check the staged file's byte size against the repo
  file's.
- **If it fails** (the computer is not linked or asleep, or a write is
  refused): say so plainly and give Zac the list of files to upload by
  hand, for example *"Upload to Project knowledge: STATUS.md,
  DECISIONS.md."*
- **Size:** Project knowledge holds at most 2 MB. Report the total after
  each sync; above 1.6 MB is an ACTION NEEDED item.

<<<PI5-END>>>

<<<PI7-START>>>
## 7. How to review a session (rigour is the point)

The review is where quality is enforced. For every session output:

- **Review from the real output.** Read the summary and checkpoints at the top
  of notes/session-NN-output.txt first. Then check figures against the detail
  with targeted reads (a search or a line range), not a full read of a long
  file.
- **Verify the numbers** against their cited DECISIONS/SPEC source; spot-check
  the arithmetic. Over-claims and mis-counts have slipped through before and
  must be caught here, before they enter the permanent record.
- **Check the honest framing**, especially where a result is flattering or a
  caveat is easy to omit (baseline differences, single-year effects,
  per-airport nuance). Lead with the number you can defend.
- **Confirm scope was held:** the scope-list check in the output file is
  clean; SPEC/RESULTS untouched unless the session was meant to touch them.
- **Confirm the archive and size checks:** every entry outside the Live index
  moved, citations resolve, and DECISIONS.md is under 80,000 bytes (D93.9).
  Never accept "nothing moved" without that check.
- **Confirm the evaluation discipline:** no look-ahead, no re-scoring the
  spent years (sealed 2025-26, F94; reserved 2024-25, F109) for any verdict,
  nothing tuned or selected on reused data, and no 2026-27 row scored before
  a forward-looking test on it is pre-registered.
- **Flag explicitly** whenever the planning assistant is unsure or needs Zac
  to verify something, in a clearly marked ACTION NEEDED block: what to check,
  how to check it, and what to do for each outcome.
- **Only then** give commit commands. If something is wrong, have Zac send a
  correction to Claude Code before committing. Never commit a known error.

<<<PI7-END>>>

<<<PI11-START>>>
## 11. Session design (D93)

- **Fewer, fuller sessions.** Every session pays a fixed reading cost twice
  (planning chat and Claude Code). Combine related work into one session
  rather than a chain of small ones. Check during planning what a session
  will touch (paths, script constants, file names), so follow-up sessions
  are rare.
- **Every prompt begins with a Read first section** (D93.16), as narrow as
  the work allows: SPEC sections by number, DECISIONS entries by number,
  and which files in full. A session that fits models, scores, or records
  a decision reads the live DECISIONS.md in full; a session that only
  moves or edits the record mechanically need not.
- **Every prompt has:** numbered steps, each with its own check and stop
  condition; a scope list of the files the session may create or edit; and
  the end-of-session steps from CLAUDE.md.
- **Every prompt names the DECISIONS entries and SPEC sections each step
  needs,** archived ones by number, so Claude Code reads only those.
- **Every D entry says which Live index changes it makes** (D93.8).
- **Model choice in Claude Code** (Zac's setting): a lighter model (Sonnet)
  for mechanical sessions such as moves, doc edits and checks; the strongest
  model (Opus) for design, statistics and model fitting. The planning chat
  recommends one with each invocation.

<<<PI11-END>>>

## Step 4: the archive script

Write `scripts/archive_decisions.py` (standard library only). It is a
standing tool, reused at the end of every session. Modes:

- `--plan`: read DECISIONS.md. The **header** is every line before the first
  line that is exactly `---`. The rest is split into **spans**: the lines
  between consecutive `---` lines (the `---` lines themselves are
  separators). A span's **ID** is the entry number of the first line in it
  that matches `^\*\*([DF]\d+)\.`; a span with none is `pointer`. The **keep
  list** is read from the Live index in the header: the lines between
  `<!-- live-index-start -->` and `<!-- live-index-end -->` that match
  `^- ([DF]\d+):`. Print a one-line summary (spans, keep, move, bytes) and
  write the full span table (index, first line, line count, bytes, ID, the
  first line of the span cut to 80 characters, KEEP or MOVE) to the output
  file given by `--out`. Stop with an error if: the index is missing or
  empty; a keep ID is in no span or in more than one; a span's matching
  lines give more than one distinct ID. (Sub-items such as `**F138.4` match
  the same pattern and give the same ID as their entry; that is expected.)
  An ID found in more than one span is listed in the table; it stops the
  run only if it is a keep ID.
- `--apply --session NN`: do the plan, then write the new DECISIONS.md as the
  header, then the kept spans in their original order, each preceded by the
  `---` separator exactly as in the original. Append to DECISIONS-archive.md
  a blank line, `---`, a blank line, the heading
  `## Moved by session NN (D93.8)`, then the moved spans in original order,
  each preceded by `---`. Before writing anything, verify in memory: (1) the
  new archive starts with the old archive byte for byte; (2) the line count
  of the new live file plus the moved spans and their separators equals the
  original's plus the added archive lines; (3) re-interleaving kept and moved
  spans by their recorded positions rebuilds the original DECISIONS.md byte
  for byte; (4) every moved span appears verbatim in the new archive section.
  Write only if all four pass; print SHA-256 and byte sizes before and after.
  If nothing is to move, write nothing and say so.
- `--citations`: collect every citation of the form `D` or `F` followed by
  digits (and an optional `.digits` part) in SPEC.md, STATUS.md, CLAUDE.md,
  DECISIONS.md and RESULTS.md. For each distinct entry number, check that an
  entry opening line `**Dnn.` or `**Fnn.` exists in exactly one of
  DECISIONS.md and DECISIONS-archive.md (grep both; never load the archive
  into the conversation). Print counts (resolved, unresolved, found in both)
  and write the unresolved and doubled numbers, with the file and line
  citing them, to `--out`. Also report: any entry number whose first
  opening line (`**Dnn.` or `**Fnn.` followed by a space) appears more
  than once across the two files, and any dated `## YYYY-MM-DD` heading in
  DECISIONS.md that is earlier than the one before it. Report only.

Check the script before use: run `--plan` on a temporary copy of the repo's
two DECISIONS files with a made-up two-entry index, and `--apply` on that
copy, and confirm all four checks pass and the copy rebuilds; delete the
temporary directory. Record this in the output file.

## Step 5: add the Live index and move

(a) Insert the block between `<<<INDEX-START>>>` and `<<<INDEX-END>>>` into
DECISIONS.md immediately before its first line that is exactly `---` (so it
ends the header), with one blank line before and after it. Check with
`grep -c 'live-index-start'` (must be 1).

<<<INDEX-START>>>
## Live index

<!-- live-index-start -->
- D47: raw-data policy for large re-fetchable sources.
- D73: pre-registration of the 2026-27 GFS forward test.
- D77: the NBM/MOS comparison and the 2026-27 NBM/MOS test (D77.6).
- D79: how the 2026-27 tests are reported.
- D82: stage C's design.
- D88: stage C's development table and the curve's baseline.
- D89: the rules for stage C's build choices.
- F139: the baseline's cross-validation scores (the incumbent, D89.7).
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
<!-- live-index-end -->

Every entry not listed here is in DECISIONS-archive.md, unchanged and still
binding. Entry numbers never change, so every citation resolves in one of the
two files. This list changes only through an owner's DECISIONS entry; a
session adds its own new entries (D93.8).
<<<INDEX-END>>>

(b) Run `--plan --out` (append the table to the output file). Check: nine
KEEP spans, one per index ID; header unchanged apart from the index. Stop if
not.

(c) Run `--apply --session 99`. Record the four checks, sizes and SHA-256.

(d) Run `--citations`. Unresolved or doubled numbers are reported, not fixed.

## Step 6: scripts/README.md

Add one line in its list of scripts (where standing or helper scripts are
described; if there is no fitting place, at the end of the list):
`` - `archive_decisions.py`: standing tool. Moves every DECISIONS entry outside the Live index to the archive and checks citations (D93.8). Run at the end of every session. ``

## End of session

Follow CLAUDE.md's new end-of-session steps (Step 2's text), with these
details:

- **F142.** Append it at the bottom of DECISIONS.md, at most about 40 lines
  (D93.10): what moved (span counts, bytes before and after for both files),
  the four checks, the citation check's counts, the script's SHA-256, the
  sizes of CLAUDE.md and PROJECT-INSTRUCTIONS.md before and after, readings
  for the owner, and what was not done. Then add `- F142: session 99's
  finding.` to the Live index, after the D93 line.
- **Archive step:** run `--apply --session 99` again. It should find nothing
  to move; report that.
- **STATUS.md:** overwrite as a current-only snapshot reflecting D93 (the
  Live index, the size limit, session order). Keep the carried items, short.
  The libomp item is now D93.3; the GFS v17 item points to D93.15's
  weekly check. RESULTS section 7 stays an open item (D93.4). End with: **Next planning session:** Review session 99. If it
  passed, the owner commits and pushes (`git commit -F
  docs/commits/commit-99.txt`) and the planning chat syncs Project
  knowledge (PROJECT-INSTRUCTIONS section 5: STATUS, DECISIONS, CLAUDE,
  PROJECT-INSTRUCTIONS, and DECISIONS-archive, which is new there). Then
  plan session 100: fix D93.6's four choices in its D entry, then run the
  first of D82.5's alternatives against the baseline under D89.6.
- **Size check:** DECISIONS.md must now be under 80,000 bytes. If not, it is
  a finding.
- **Output file:** the 30-line summary at the top, then the checkpoints, then
  the detail.

## What this session must not do

No model fit, score or data read; no network call; nothing installed; no
existing script, data file or workflow edited; no DECISIONS or archive entry
retyped, edited or renumbered (moves are mechanical and verified); no
SPEC.md, RESULTS.md, README.md or data/README.md edit. Nothing committed and
no commit message written.
