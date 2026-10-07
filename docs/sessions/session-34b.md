# Session 34b — execute the archive move (mechanical) + workflow codification

## Scope — one job, then stop

Execute the archive move that session 34a planned, **mechanically** — a script cuts the
approved line ranges out of `DECISIONS.md` and appends them verbatim to
`DECISIONS-archive.md`. No entry is ever re-typed by hand; the moved text is byte-exact
because it is extracted, not regenerated. Then codify the workflow change and fix the one
deferred docs debt. **No code, model, data file, or figure is touched.**

The move set is the approved manifest at `notes/session-34-archive-manifest.md`, **with
the borderline resolved to MOVE**: the session-21 restructure record moves too. Final
KEEP-LIVE set: **D17, F7, F85–F87, all open questions, and the new record entry this
session appends.**

## Standing rules that bind this session

- **Mechanical move only.** Use `awk`/`sed` on line ranges; never hand-reproduce an
  entry. Byte-for-byte or it is wrong.
- **Non-destructive.** Nothing is deleted from the project — moved entries leave the live
  file but land, unaltered, in the archive. Git holds every prior version.
- **Numbering is stable.** Do not renumber; every `(Dxx)`/`(Fxx)` citation still resolves
  across the two files.
- **You never commit.** Prepare changes plus a suggested message; the owner reviews and
  commits by hand.

## Task 0 — verify the manifest still matches the file (do this first)

`DECISIONS.md` must be unchanged since 34a built the index, or the line ranges are stale.
Re-run the header `grep` and confirm the headers still sit at the line numbers the
manifest records (same total line count, same header lines). **If anything has shifted,
stop and report — do not cut against stale ranges.**

## Task 1 — partition and move (one pass, no line-shift bugs)

- Read the **MOVE line ranges** from the manifest. Build the set of move-lines.
- In a **single `awk` pass** over `DECISIONS.md`, split every line into two outputs by
  line number: **keep-lines** and **move-lines**. A one-pass partition avoids the
  shifting-line-number bug that deleting ranges top-down causes.
- **Append** the move-lines to `DECISIONS-archive.md` under one new dated section header —
  `## Moved by session 34b (2026-…)` — with a short note: the archive criterion applied,
  the entry-number ranges moved, and a pointer to `notes/session-34-archive-manifest.md`
  for the per-entry rationale. (One section header + pointer, not 237 hand-written notes;
  the moved entries themselves follow verbatim.)
- **Replace** `DECISIONS.md` with the keep-lines.

## Task 2 — amend the archive file's header note

Session 21's header says archiving was one-time and "nothing is ever moved again as a
matter of routine." **Supersede** that paragraph: from session 34b on, moving settled
entries to the archive is a **routine part of the end-of-session roundup**, while the
append-only / verbatim / nothing-deleted guarantees still hold. Amend the note; preserve
the session-21 history. Ensure this header (permanent home) explains **what the archive
is and how citations-into-archive work** — since session-21's record, which used to carry
that explanation, has now moved.

## Task 3 — codify archive-as-you-go in CLAUDE.md (report before/after)

- **Routine read list:** state that the per-session read is **CLAUDE.md + SPEC.md +
  STATUS.md + live DECISIONS.md**; `DECISIONS-archive.md` is read **on demand** only, when
  a settled finding is needed by number. (RESULTS.md is likewise not a routine read.)
- **End-of-session steps:** add an **archive step** — "move any entries that became
  settled this session to `DECISIONS-archive.md`, per the archive criterion" — so
  archiving is continuous from now on.

## Task 4 — fix the deferred RESULTS.md wording (report before/after)

`RESULTS.md` §2 explains the differing target hours as "because local noon is a different
UTC hour at each longitude." Wrong for the EGLC/LFPG pair: they share 12:00 UTC **by
deliberate design** (12:00 is London's local noon; Paris's is ~11:00 UTC), the clean
"only the location changed" comparison (D26) — while DSM/YSDU/RNO each take their own
local-noon UTC hour. Fix only that sentence; change no figure and no other section.

## Task 5 — record entry (stays live)

Append to the **live** `DECISIONS.md` a new entry at the next sequential D-number (**check
the tail; likely D46**) recording: the archive criterion, the manifest applied (237 moved,
KEEP-LIVE = D17/F7/F85–F87/open questions), the session-21 record moved, the CLAUDE.md
workflow change, the archive-header amendment, and the RESULTS.md fix. **This entry must
carry the "why the archive exists / how it works" explanation forward**, re-homing
session-21's explanatory role so nothing live-needed is lost. This entry stays live.

---

## What NOT to do

- **Do not hand-reproduce, edit, reword, or summarise any moved entry** — `awk`/`sed`
  extraction only, byte-exact.
- **Do not archive** D17, F7, F85–F87, any open question, or the new D46 record.
- **Do not renumber** anything or rewrite `(Dxx)`/`(Fxx)` citations.
- **Do not cut against stale line ranges** — if Task 0 finds any drift, stop.
- **Do not touch any code, script, model, data file, or figure.**
- **Do not modify `SPEC.md`** (its §1 Reno spot already reads "failed").
- **Do not commit.**
- **Do not exceed scope** — log anything else as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the move summary: entries moved, new live line count vs old, and the
   before/after for CLAUDE.md and RESULTS.md.
2. **Refresh STATUS.md:** record session 34b (documentation-only), the new leaner
   live-DECISIONS size, and archive-as-you-go now in force. Drop STATUS's stale "SPEC §1
   Reno in-progress" note (SPEC §1 already reads "failed").
3. **Integrity check — this is the critical one for a move:**
   - every MOVE entry number appears **exactly once** in the archive and **zero times** in
     the live file;
   - **D17 and F7 are still in the live file** (explicit check — they were the correction);
     F85–F87, the open questions, and D46 are all still live;
   - line accounting reconciles: new-live + moved-to-archive = old-live (plus only the new
     section header / record lines you intentionally added);
   - D- and F-numbering is unbroken across the two files read together; no `(Dxx)`/`(Fxx)`
     citation in SPEC/RESULTS/STATUS/CLAUDE now dangles;
   - `git status` shows only `DECISIONS.md`, `DECISIONS-archive.md`, `CLAUDE.md`,
     `RESULTS.md`, `STATUS.md` modified (plus any new script/notes) — no code, data, or
     model.
4. **Write a suggested commit message** — title plus multi-paragraph body, no
   AI-attribution trailers (session 30–33 house style) — then **stop and wait for the
   owner's review.**
