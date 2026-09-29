# CLAUDE.md — standing rules for every session

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

## The three files

The project keeps three living documents. Read all three **in full** at the
start of every session, in this order, **before** reading the session prompt:

1. **SPEC.md** — the source of truth for *how the project should work*.
2. **STATUS.md** — a *snapshot*, overwritten each session: current stage,
   what is next, and any open questions still live. It is not a growing log —
   its history lives in git, not in the file itself.
3. **DECISIONS.md** — an *append-only* log of choices, findings, and why. As
   of session 34b, this is the **live** file only — settled material is moved
   out routinely (see "End of every session" below).

**The routine per-session read is CLAUDE.md + SPEC.md + STATUS.md + live
DECISIONS.md — nothing else, every session.** Two further files exist and are
read **on demand only**, never routinely:

- **DECISIONS-archive.md** — settled decisions and findings moved out of
  DECISIONS.md verbatim (nothing deleted, everything reproducible). Open it
  only when a session needs deep history from a passed stage or airport, in
  particular an archived entry's exact wording rather than just its headline.
  Entry numbers (`Dxx`/`Fxx`) never change when an entry moves, so a citation
  in any live file always resolves, in either file.
- **RESULTS.md** — a standalone, reader-facing technical summary, cited back
  to DECISIONS.md. Open it only when a session needs that summary; it is
  never a source of truth (SPEC beats it, same as code).

**PROJECT-INSTRUCTIONS.md** (repo root) is the operating guide for the
claude.ai planning chat. Claude Code does not follow it and does not read
it routinely. Claude Code follows this file. It edits
PROJECT-INSTRUCTIONS.md only when a session prompt says exactly what to
change.

The **critical-rules section of SPEC (section 2)** applies to every session,
whether or not the session prompt repeats it. It is non-negotiable.

## One session, one scope

Each session does exactly what its session prompt defines — nothing beyond
that scope. If something outside the scope looks broken or worth doing, do
**not** fix it this session. Log it in DECISIONS.md as an open question. The
owner decides later.

## Source of truth and conflicts

- **SPEC beats code.** If code and SPEC disagree, SPEC is right. Either fix
  the code to match SPEC, or change SPEC on purpose and note the change in
  DECISIONS. Never let them drift apart quietly.
- **Uploaded beats remembered.** The three files change every session. Any
  copy in an old chat is stale. A planning chat works only from the current
  files uploaded to claude.ai Project knowledge. If an uploaded file
  contradicts memory or an old chat copy, the uploaded file wins.
- **Never edit a spec file from memory or assumption.** Edit a spec file only
  where the session prompt or the owner explicitly says to, and only with
  content from this session's real work.
- **If the session prompt and a spec file disagree, stop and flag it.** Do
  not guess which to follow.

## Reading the current files before work

A planning chat reads the current committed **SPEC.md**, **STATUS.md**,
**DECISIONS.md** and **CLAUDE.md** from claude.ai Project knowledge, guided by
the planning-side `PROJECT-INSTRUCTIONS.md`. The owner re-uploads every
changed file after each commit, so the planning chat never works from a
stale copy.

## Handling inputs and data

- Never change raw, original inputs in place. Keep them untouched in
  `data/raw/` and work on copies.
- Never silently fill missing data. Mark the gaps, count them, report them.
  Any filling-in must be explicitly asked for in the session prompt.
- Because the data sources are live services that can revise data, record the
  pull date and exact query with each raw file, and treat it as a fixed
  snapshot.

## Commit discipline

Claude Code **never** commits, adds, or pushes to version control. It
prepares all changes, then stops. It does not write a commit message:
after reviewing the session, the planning chat writes it to
`docs/commit-NN.txt`, and the owner commits by hand with
`git commit -F docs/commit-NN.txt`. Nothing enters the project's history
without a person looking first.

## End of every session

1. Run the session's checks and paste the **real output** — actual numbers,
   not a description of them.
2. **Overwrite STATUS.md**: this means **pruning it to a current-only
   snapshot** — present state, the immediate next action, and live open
   questions only — **never appending that session's write-up to an
   accumulating log.** Its history lives in git and DECISIONS.md.
3. Run a **consistency check**: re-read all three files and report anything
   that disagrees, any duplicated heading, and any log entry out of order.
   Report only — do not fix silently. The owner decides. Write the findings
   into the session's output file (`notes/session-NN-output.txt`) as well as
   reporting them in chat.
4. **Archive step:** move any DECISIONS.md entries that became settled this
   session to DECISIONS-archive.md, per the archive criterion (settled,
   codified elsewhere or superseded, and not needed word-for-word by any live
   open question or STATUS.md's "Next" section) — mechanically, verbatim,
   never by hand-reproducing an entry. This is routine as of session 34b, not
   a one-time exception; see DECISIONS-archive.md's own header and DECISIONS
   D46 for the full account.

## Session prompts

Work happens in sessions. Each has a short **session prompt** file the owner
writes, kept together in the `docs/` folder, giving a clear record of what was
asked each time.
