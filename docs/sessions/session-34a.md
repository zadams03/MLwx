# Session 34a — archive manifest (decide only; no file changes)

## Scope — one job, then stop

Decide **which** settled DECISIONS entries should move to `DECISIONS-archive.md`, and
write that decision as a reviewable **manifest**. This session **changes no canonical
file** — it does not move, edit, or delete a single entry. The mechanical move happens in
34b, from the manifest you approve here.

**This session must stay cheap and must not read `DECISIONS.md` in full** (it is large
enough to exceed a single read). Work from a `grep`-built index of entry headers plus
**bounded** reads of only the entries you actually need to judge. Reading the whole file
defeats the purpose of the exercise.

## Why this shape

The archive move in 34b will be done **mechanically** (cut line-ranges from the live file,
append verbatim to the archive) — not by re-typing entries. So all this session needs to
produce is: for every entry, a MOVE/KEEP-LIVE decision, a one-line reason, and — for the
MOVE set — the exact line range, so 34b's script has an unambiguous target.

## Task 1 — build the entry index (mechanical, no full read)

Determine the actual entry-header patterns in `DECISIONS.md` (e.g. `**F82.`-style
finding markers, `**D45.`-style decision markers, and `## <date> — Session NN` section
headers — confirm the real patterns from a few `grep` hits). Then build an index with
line numbers:

```
grep -nE '<the entry/section header patterns>' DECISIONS.md
```

From that, produce a table: **entry number · one-line title · start line · end line**
(end line = the line before the next entry header; last entry ends at EOF). Report the
total entry count and confirm the F- and D-number sequences are contiguous with no gaps
or duplicates. This index is built from headers only — do not read the bodies wholesale.

## Task 2 — classify each entry against the archive criterion

**Archive criterion — move an entry only when BOTH hold:**
- **settled** — its conclusion will not change (a passed airport's cycle, a closed
  question, a decision whose operative rule now lives in SPEC); **and**
- **not actively needed by live work** — no open question depends on reading it in full,
  and the live richer-features phase (F85–F87) does not cite it beyond a headline that
  STATUS or RESULTS already carries.

You may read `STATUS.md` and `RESULTS.md` in full (both are small) — they tell you what
headlines the live snapshot already carries. For the **live** entries F85–F87 and the
open questions, read them (bounded) to see exactly which older entries they cite by
number — anything they cite in full stays live.

Classify **every** entry as MOVE or KEEP-LIVE:
- **Expected MOVE:** the four passed airports' full cycles (EGLC, LFPG, DSM, YSDU —
  verify/pull/join/rehearse/lock/test findings); closed questions; decisions fully
  codified in SPEC.
- **Reno — judge individually.** Reno's cycle is settled and its result stands, so most
  of it is archivable — **but** the live phase reasons about Reno (F87). Any specific Reno
  finding cited in full by F85–F87 or a live open question stays live and is flagged.
  Read the Reno entries (bounded) to make this call per-entry, not as a block.
- **KEEP-LIVE:** sessions 31–33 (F85–F87), every open question and anything it cites in
  full, and the restructure-record entry 34b will add.

## Task 3 — write the manifest

Write `notes/session-34-archive-manifest.md` containing:
- the full entry index (number · title · line range);
- for every entry: **MOVE** or **KEEP-LIVE**, with a one-line reason;
- a consolidated **MOVE list with exact line ranges** (the input 34b's script will act
  on), and the KEEP-LIVE list;
- any borderline calls (especially Reno) called out explicitly for the owner to confirm.

Also report the manifest summary in the session output.

## What NOT to do

- **Do not move, edit, delete, or reword any entry.** No changes to `DECISIONS.md`,
  `DECISIONS-archive.md`, `CLAUDE.md`, `RESULTS.md`, or `STATUS.md` — this session writes
  **only** the manifest file under `notes/`.
- **Do not read `DECISIONS.md` in full** — index by `grep`, then bounded reads only. Keep
  it cheap.
- **Do not touch any code, script, model, data file, or figure.**
- **Do not renumber anything** or propose renumbering — numbers are stable across files.
- **Do not commit.**
- **Do not exceed scope** — if something else looks worth doing, note it in the manifest,
  don't act on it.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the entry index summary (count, contiguity check) and the manifest summary
   (how many MOVE, how many KEEP-LIVE, the Reno calls).
2. **Save** `notes/session-34-archive-manifest.md`.
3. **Consistency check:** every entry in the index is classified exactly once; every MOVE
   entry has a line range; the KEEP-LIVE set includes F85–F87 and all open questions; no
   canonical file was modified (`git status` should show only the new manifest file, plus
   `docs/session-34a.md` if saved there).
4. **Stop and wait for the owner's review** of the manifest. No commit, and no DECISIONS
   or STATUS edit this session — 34b records the work once the move is approved and
   executed.
