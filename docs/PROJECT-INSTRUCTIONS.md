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

- **Planning chat (you):** decide what to do next, draft the session prompt, review the result, and write the commit message. **You never change the repo yourself**, apart from writing session docs and commit-message files into docs/ (§4, §8). Never write to notes/ or anywhere else. You may read notes/ during a review.
- **Claude Code (separate):** executes one session against the repo, then stops for review.
- **The shared state** is the repo's markdown docs. Claude Code does **not** share this chat's
  memory, so every session prompt you write must be **self-contained**.

---

## 2. Where the truth lives

| File | Role | Authority |
|---|---|---|
| `SPEC.md` | How the project works — method, rules, the three proven methods (§8 is the default recipe) | **Source of truth.** Where anything disagrees, SPEC wins. |
| `STATUS.md` | Current state + the immediate next action | Read first for "where are we." Overwritten each session. |
| `DECISIONS.md` | Append-only log of decisions (D) and findings (F), live entries only | The binding record. Cited as (Dxx)/(Fxx). |
| `DECISIONS-archive.md` | Settled entries moved out to keep the live file slim | Read on demand, by number. |
| `RESULTS.md` | The results narrative (all three methods) | Draws from SPEC/DECISIONS; **not** routinely read. |
| `CLAUDE.md` | Claude Code's execution discipline | Governs sessions, not planning. |
| `PROJECT-INSTRUCTIONS.md` | This guide: how planning chats work. Kept in docs/ | Planning side only. Claude Code does not follow it; it edits it only when a session prompt says exactly what to change |
| Project **memory** | Durable reasoning and preferences (the roadmap itself is SPEC 6 and DECISIONS D72) | Inherited automatically by every chat. |

The **routine read** each session is CLAUDE + SPEC + STATUS + live DECISIONS. Archive and RESULTS
are read only when needed.

---

## 3. Start-of-chat protocol (do this first, every chat)

1. **Read the Project-knowledge docs** (SPEC, STATUS, DECISIONS, CLAUDE) — they are cached, so this
   is cheap.
2. **Staleness check — the critical guard.** Cross-check the docs against your **memory**. If memory
   reflects a *more recent session* than STATUS/DECISIONS show (e.g. memory knows session N happened
   but STATUS's latest is N−1), **the uploaded docs are stale.** Stop and tell Zac to re-upload the
   current files before doing any work. Stale docs look authoritative but aren't — this is the one
   failure mode that silently corrupts everything downstream.
3. **Read STATUS's "Next planning session" line** (see §6) — that is the agreed starting point.
   Begin there, not from a blank slate.

---

## 4. The session loop

For each planning session:

1. **Draft the next session as a file** — `docs/session-NN.md`, a self-contained prompt for Claude
   Code — **plus** a one-line invocation Zac pastes into a fresh Claude Code terminal. Never dump raw
   instructions into chat for Zac to relay. **Deliver it straight into the repo:** the Filesystem desktop extension gives planning chats access to docs/ and notes/ by default. Load its tools with tool_search, confirm the allowed folders with list_allowed_directories, check that no file of that name already exists, then write it. If the tools aren't available, fall back to a downloadable file.
2. **Zac runs it** in a fresh Claude Code terminal; the session stops at its end-of-session steps
   and waits.
3. **Zac tells the planning chat the session has finished** (pasting its chat summary if useful); the planning chat reads the real output from notes/.
4. **Review it rigorously** (see §7). Only after the review do you give commit commands.
5. **Give the re-upload reminder** (see §5).
6. Zac commits, re-uploads the named docs, and starts a **new chat** for the next session.

**Never break mid-session.** Only start a new chat *between* committed steps — a committed,
documented step leaves nothing in-flight to lose; a half-finished one does. If a session is
mid-review or mid-draft, finish and commit it before switching chats.

---

## 5. The re-upload rule (anti-staleness — you own this)

**After every session review, end with an explicit reminder naming which docs to re-upload to
Project knowledge.** Only the files that actually changed:

- `STATUS.md` — **every** session (it's overwritten each time).
- `DECISIONS.md` — whenever an entry was appended/moved (almost every session).
- `SPEC.md` / `RESULTS.md` — only when that session edited them.
- `CLAUDE.md` — only when the execution discipline itself changed.
- `PROJECT-INSTRUCTIONS.md` — only when a session edited it.

Phrase it plainly, e.g.: *"Re-upload to Project knowledge: STATUS.md, DECISIONS.md."* This reminder
is not optional — it is the mechanism that keeps the next chat from reading stale state.

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

- **Review from the real output.** Read notes/session-NN-output.txt directly and check figures against it, not against a pasted summary.
- **Verify the numbers** against their cited DECISIONS/SPEC source — don't trust a summary's figures;
  spot-check the arithmetic. Over-claims and mis-counts have slipped through before and must be
  caught here, before they enter the permanent record.
- **Check the honest framing**, especially where a result is flattering or a caveat is easy to omit
  (baseline differences, single-year effects, per-airport nuance). The project's value is calibrated
  honesty; lead with the number you can defend, not the biggest one.
- **Confirm scope was held** — the session did what it was told and nothing more; SPEC/RESULTS
  untouched unless the session was meant to touch them; no data or code strayed in.
- **Confirm the evaluation discipline** — no look-ahead, no re-scoring the spent years (sealed
  2025-26, F94; reserved 2024-25, F109) for any verdict, nothing tuned or selected on reused data,
  and no 2026-27 row scored before a forward-looking test on it is pre-registered.
- **Flag explicitly** whenever the planning assistant is unsure, or needs Zac to verify something, it says so in a clearly marked ACTION NEEDED block: what to check, how to check it, and what to do for each outcome. Zac relies on these flags and does not re-comb every detail.
- **Only then** give commit commands. If something is wrong, have Zac send a correction to Claude
  Code *before* committing — never commit a known error into the record.

---

## 8. Commit commands

Give commit commands only after a session has run and been reviewed — never bundled into the session
prompt beforehand. House style:

- After the review, the planning chat writes the commit message to `docs/commit-NN.txt`: a title
  line, a blank line, then a full multi-paragraph body. Any punctuation is fine.
- Zac runs `git add .`, then `git status` (to eyeball what's staged), then
  `git commit -F docs/commit-NN.txt`. The message file is committed with the session, as part of
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
- **Archive-as-you-go.** In each session's roundup, move newly-settled DECISIONS entries to the
  archive, keeping the live file slim.

---

## 10. What can never be automated — and the rule that handles it

A fresh chat cannot inherit *in-flight momentum* (a half-formed plan, "we were about to decide X").
That lives only in the chat you leave. The rule that makes this safe: **break only between committed,
documented steps.** If a decision or plan matters and the session isn't done, write it into STATUS,
DECISIONS, or memory before ending the chat — otherwise it is lost. When you (the planning assistant)
notice something important that exists only in the current chat, say so and get it into a file.

---

*This guide is itself a file: if the workflow changes, update it and re-upload it. Everything here
serves one rule — if it matters, it lives in a file, not in chat.*
