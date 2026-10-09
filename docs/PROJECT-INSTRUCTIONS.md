# ML Weather — Planning-Chat Operating Guide

> **For Claude Code:** this file is the operating guide for the
> claude.ai planning chat. Claude Code does not follow it. Claude Code
> follows CLAUDE.md, and edits this file only when a session prompt
> says exactly what to change.

This is the operating guide for **planning sessions** on the ML Weather project (per-airport
LightGBM MOS models that bias-correct GFS temperature forecasts). It is the planning-side
counterpart to `CLAUDE.md` (which governs Claude Code execution). Its single purpose: make sure
**nothing is lost between chats**, so each new planning session starts fully current.

Read this at the start of every planning chat. It applies to you (the planning assistant), and it
tells you what to do, in what order, and what must never be skipped.

---

## 0. Why this exists

Planning happens in claude.ai chats. Reopening a long old chat reprocesses the whole conversation
at full usage cost, so the workflow is instead: **one new chat per planning session**, each
inheriting current state from Project knowledge + memory. That only works if the *state* is
genuinely captured in files, because a fresh chat remembers nothing of previous conversations
except what is written down. So the governing principle is:

> **If it matters, it lives in a file (SPEC, STATUS, DECISIONS, or memory) — never only in chat.**
> Chat context does not survive. Files and memory do.

---

## 1. The two-loop architecture

- **Planning chat (you):** decide what to do next, draft the session prompt, review the result, and write the commit message. **You never change the repo yourself**, apart from writing session docs into docs/sessions/ and commit-message files into docs/commits/ (§4, §8). Never write to notes/ or anywhere else. You may read notes/ during a review.
- **Claude Code (separate):** executes one session against the repo, then stops for review.
- **The shared state** is the repo's markdown docs. Claude Code does **not** share this chat's
  memory, so every session prompt you write must be **self-contained**.

---

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

---

## 3. Start-of-chat protocol (do this first, every chat)

1. **Read this guide and STATUS.md in full.**
2. **Staleness check: the critical guard.** Cross-check STATUS against
   memory. If memory reflects a more recent session than STATUS shows, the
   uploaded docs are stale. Stop and sync Project knowledge (section 5), or ask Zac to upload the current files if the sync fails,
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

---

## 4. The session loop

For each planning session:

1. **Draft the next session as a file** — `docs/sessions/session-NN.md`, a self-contained prompt for Claude
   Code — **plus** a one-line invocation Zac pastes into a fresh Claude Code terminal. Never dump raw
   instructions into chat for Zac to relay. **Deliver it straight into the repo:** the Filesystem desktop extension gives planning chats access to docs/ and notes/ by default. Load its tools with tool_search, confirm the allowed folders with list_allowed_directories, check that no file of that name already exists, then write it. If the tools aren't available, fall back to a downloadable file.
2. **Zac runs it** in a fresh Claude Code terminal; the session stops at its end-of-session steps
   and waits.
3. **Zac tells the planning chat the session has finished** (pasting its chat summary if useful); the planning chat reads the real output from notes/.
4. **Review it rigorously** (see §7). Only after the review do you give commit commands.
5. **After Zac commits and pushes, sync Project knowledge** (section 5).
6. Zac starts a **new chat** for the next session.

**Never break mid-session.** Only start a new chat *between* committed steps — a committed,
documented step leaves nothing in-flight to lose; a half-finished one does. If a session is
mid-review or mid-draft, finish and commit it before switching chats.

The invocation Zac pastes into a fresh Claude Code conversation is fixed (D93.16); only the number changes: Carry out the session defined in docs/sessions/session-NN.md: first read what its Read first section lists, then do its steps, staying strictly within its scope. Stop at the end-of-session steps and wait for my review. Do not commit anything.

---

## 5. Syncing Project knowledge (anti-staleness: you own this)

After Zac has committed and pushed a reviewed session, **the planning chat
copies every changed file into Project knowledge itself** (D93.15). Never
sync before the commit: Project knowledge must match the committed repo.

- **Which files:** `STATUS.md` every session; `DECISIONS.md` and
  `DECISIONS-archive.md` whenever they changed (almost every session);
  `SPEC.md`, `RESULTS.md`, `CLAUDE.md` and `docs/PROJECT-INSTRUCTIONS.md`
  (kept in Project knowledge as `PROJECT-INSTRUCTIONS.md`) only when the
  session edited them. `DECISIONS-archive.md` is kept in Project knowledge
  as `claude/DECISIONS-archive.md`.
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

---

## 6. STATUS.md is the handoff document

STATUS is written for Claude Code, but it is also the bridge across the chat boundary. **Every
`STATUS.md` must end with a "Next planning session" line** — one or two sentences naming the
immediate next action and any open question. That single line carries momentum across chats: a
fresh planning chat inherits the *facts* from the docs and the *reasoning* from memory, but only the
"Next planning session" line tells it what to actually do next. Bake this requirement into every
session prompt's end-of-session steps.

**STATUS stays a current-only snapshot (standing rule, session 59).** STATUS is overwritten each
session to reflect only the present state, the immediate next action, and live open questions —
never grown into an accumulating per-session log. Each session's overwrite **prunes**; it does not
append that session's write-up onto the previous ones. Its full history lives in git and in
`DECISIONS.md`, so pruning loses nothing. A fresh planning chat should always inherit a lean STATUS,
not a long carried-forward chain. (The matching end-of-session rule lives in `CLAUDE.md`.)

---

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

---

## 8. Commit commands

Give commit commands only after a session has run and been reviewed — never bundled into the session
prompt beforehand. House style:

- After the review, the planning chat writes the commit message to `docs/commits/commit-NN.txt`: a title
  line, a blank line, then a full multi-paragraph body. Any punctuation is fine.
- Zac runs `git add .`, then `git status` (to eyeball what's staged), then
  `git commit -F docs/commits/commit-NN.txt`. The message file is committed with the session, as part of
  the record.
- Raw GRIB (large, re-fetchable) is **gitignored** (D47) — commit processed data + manifests, never
  the ~GB raw. Watch that `git status` never stages raw GRIB.

---

## 9. Evaluation discipline (the project's backbone — never relax it)

- **Frozen bar, one look.** Each method gets a single sealed-test look; the sealed year (2025-08-01
  → 2026-07-31, F94) is spent and stands. Never re-open it.
- **Both held-out years are spent (D59).** The sealed year (2025-08-01 → 2026-07-31, F94) and the
  reserved year (2024-08-01 → 2025-07-31, D51, confirmed once in F109) have each had their one look.
  **No untouched held-out year remains at any of the six airports (D71.1).** A new verdict therefore needs either
  a new airport (both years unseen there) or a forward-looking year (2026-27), pre-registered before
  any of its data is scored. The in-code reserved-year guard stays as a permanent tripwire.
- **The feature-selection programme is closed (D59.2).** `B + D, L, R, T` (SPEC §8) is the default
  recipe for any new airport or pooling work, applied unchanged and identically everywhere.
- **Lock before you look.** Freeze a recipe in writing (features, source, settings, pre-registered
  expectations) *before* opening any held-out data; then run once, unchanged.
- **Claims vs build choices (D72.2, SPEC 2.5).** Only a stated result
  needs a frozen, pre-registered, one-look test. Build choices are made
  by time-ordered cross-validation on data not held out for any claim,
  identically at every airport, and are never quoted as results.
- **Forward years.** Once any part of a forward year (e.g. 2026-27) has
  been scored, no new test may be pre-registered on it.
- **Same features at every airport, always.** No per-airport feature selection — it is selection
  bias and it breaks the "recipe travels" result. Per-airport *patterns* are read as insight, never
  acted on as per-airport recipes.
- **Descriptive vs verdict.** Multi-year backtests (F96) are descriptive profiles, not new
  pass/fails; they may reuse data, but selecting anything on them still requires a fresh confirmation
  year.
- **Archive by the Live index.** In each session's end steps, every DECISIONS entry outside the Live index moves to the archive (D93.8). The live file stays under 80,000 bytes (D93.9).

---

## 10. What can never be automated — and the rule that handles it

A fresh chat cannot inherit *in-flight momentum* (a half-formed plan, "we were about to decide X").
That lives only in the chat you leave. The rule that makes this safe: **break only between committed,
documented steps.** If a decision or plan matters and the session isn't done, write it into STATUS,
DECISIONS, or memory before ending the chat — otherwise it is lost. When you (the planning assistant)
notice something important that exists only in the current chat, say so and get it into a file.

---

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

---

*This guide is itself a file: if the workflow changes, update it; the planning chat syncs it to Project knowledge. Everything here
serves one rule — if it matters, it lives in a file, not in chat.*
