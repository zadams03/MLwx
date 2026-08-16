# CLAUDE.md — standing rules for every session

Claude Code reads this automatically at the start of every session. These
rules apply every time, so they are not repeated in each session prompt.

Keep all writing plain: simple words, short sentences, define jargon on first
use. This applies to code comments, the spec files, and chat replies.

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
2. **STATUS.md** — the *current state*: what is done, in progress, next.
3. **DECISIONS.md** — an *append-only* log of choices, findings, and why.

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
- **Pasted beats remembered.** The three files change every session. Any copy
  in an old chat is stale. A planning chat works only from files pasted *in
  that same chat*. If a pasted file contradicts memory, the pasted file wins.
- **Never edit a spec file from memory or assumption.** Edit a spec file only
  where the session prompt or the owner explicitly says to, and only with
  content from this session's real work.
- **If the session prompt and a spec file disagree, stop and flag it.** Do
  not guess which to follow.

## The paste-before-work habit

Before a planning chat plans or reviews anything, it asks the owner to paste
the current **STATUS.md** at minimum (plus SPEC or DECISIONS when they matter
for the task) — *before* starting the work, not after.

## Handling inputs and data

- Never change raw, original inputs in place. Keep them untouched in
  `data/raw/` and work on copies.
- Never silently fill missing data. Mark the gaps, count them, report them.
  Any filling-in must be explicitly asked for in the session prompt.
- Because the data sources are live services that can revise data, record the
  pull date and exact query with each raw file, and treat it as a fixed
  snapshot.

## Commit discipline

Claude Code **never** commits, adds, or pushes to version control. It prepares
all changes, writes out the suggested commit message, then stops. The owner
reviews and commits by hand. Nothing enters the project's history without a
person looking first.

## End of every session

1. Run the session's checks and paste the **real output** — actual numbers,
   not a description of them.
2. Run a **consistency check**: re-read all three files and report anything
   that disagrees, any duplicated heading, and any log entry out of order.
   Report only — do not fix silently. The owner decides.

## Session prompts

Work happens in sessions. Each has a short **session prompt** file the owner
writes, kept together in the `docs/` folder, giving a clear record of what was
asked each time.
