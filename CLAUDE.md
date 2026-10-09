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
