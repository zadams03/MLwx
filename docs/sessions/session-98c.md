# Session 98c: tidy docs/ into sessions/ and commits/

Owner: Zac. Written by the planning chat, 7 October 2026, after session
98b was committed (D91, F140).

## Purpose

`docs/` holds about 150 files in one flat list: session prompts, commit
messages, its README, the planning guide and a handover note. This session
puts the session prompts in `docs/sessions/` and the commit messages in
`docs/commits/`, and updates the paths that live files give for them
(D92). No code reads `docs/` (session 98, Step 3). It runs no model
experiment and makes no build choice.

## Standing rules for this session (read before anything else)

1. **The record is not edited.** No existing DECISIONS or archive entry is
   changed. No session prompt, commit message or file in `notes/` is
   edited; they are only moved (the prompts and messages) or left alone
   (`notes/`). No script, no data file, and not the workflow file is
   edited, moved or renamed. Git history is not touched. You never touch
   the git index (no `git mv`, `git add`, `git rm`).
2. **Moves are byte for byte**, with plain `mv`, every moved file's
   SHA-256 checked before and after.
3. **No em-dash (U+2014) in any new text** (D76.6, D90.11). Existing text
   keeps its dashes.
4. **Plain writing** (CLAUDE.md).
5. **Nothing is installed. No network.** No Python run is needed.
6. If anything in this prompt disagrees with SPEC, CLAUDE.md or what you
   find, **stop and report**. Do not guess.

## The layout after this session (D92.2)

```
docs/
├── README.md
├── PROJECT-INSTRUCTIONS.md
├── HANDOVER-richer-features.md
├── sessions/      every session-*.md (prompts and correction files)
└── commits/       every commit-*.txt
```

---

## Step 0: start checks (read only)

1. `git status --porcelain` shows only `?? docs/session-98c.md`. Otherwise
   stop and report.
2. The last decision entry is D91 and the last finding is F140 (with
   F140.13). No D92 or F141 entry exists in either DECISIONS file.
3. `docs/sessions/` and `docs/commits/` do not exist.
4. SHA-256 of these five files equal to the values F140 records:
   `scripts/session97_stagec_cv.py`, `scripts/session62_reserved_confirm.py`,
   `data/processed/session63_reserved_confirm_grid.csv`,
   `data/processed/session97_stagec_cv_scores.csv`,
   `.github/workflows/stagec-grib-pull.yml`.
5. List `docs/` and count: tracked `session-*.md` files, tracked
   `commit-*.txt` files, and any other file. Any file other than
   `session-*.md`, `commit-*.txt`, `README.md`, `PROJECT-INSTRUCTIONS.md`,
   `HANDOVER-richer-features.md`, `.DS_Store` and this prompt: stop and
   report.
6. Read CLAUDE.md, SPEC, STATUS and DECISIONS in full (as always), plus
   `docs/PROJECT-INSTRUCTIONS.md`, `README.md`, `docs/README.md`,
   `notes/README.md` and `scripts/README.md`.

## Step 1: record D92 (before any other edit)

Copy the text between the lines `BEGIN D92` and `END D92` below (those two
marker lines excluded) into the end of `DECISIONS.md` with `sed`, after the
usual separator, then check it byte-equal with `diff` and `cmp` against the
same extract. Report the line numbers it occupies.

BEGIN D92
## 2026-10-07: Session 98c decision: F140 accepted, and docs/ split into sessions/ and commits/ (owner, planning chat)

**D92. Owner decisions, planning chat (after session 98b): F140 accepted,
and docs/ split into sessions/ and commits/.** Written at the start of
session 98c, before any other edit. No 2026-27 value has been read or
scored.

- **D92.1 F140 accepted,** with its twelve readings (F140.11) and the
  corrections after review (F140.13).
- **D92.2 The layout of docs/.** Session prompts, including correction
  files (`session-*.md`), go in `docs/sessions/`. Commit messages
  (`commit-*.txt`) go in `docs/commits/`. `README.md`,
  `PROJECT-INSTRUCTIONS.md` and `HANDOVER-richer-features.md` stay at the
  top of `docs/`. File names do not change. No code reads `docs/`
  (session 98, Step 3; re-checked in session 98c).
- **D92.3 Citations.** Entries written before session 98c that cite
  `docs/session-NN.md` or `docs/commit-NN.txt` resolve to the same file
  name under `docs/sessions/` or `docs/commits/`. They are not edited.
  Script docstrings that name a prompt under `docs/` resolve the same way.
- **D92.4 The invocation and commit command from session 99.** The
  invocation: "Read CLAUDE.md, then SPEC.md, STATUS.md, and DECISIONS.md
  in full. Then carry out the session defined in
  docs/sessions/session-NN.md, staying strictly within its scope. Stop at
  the end-of-session steps and wait for my review. Do not commit
  anything." The commit command: `git commit -F
  docs/commits/commit-NN.txt`. This replaces D91.4's invocation. The
  planning chat writes session prompts to `docs/sessions/` and commit
  messages to `docs/commits/`.
- **D92.5 notes/ stays flat,** because scripts write there by fixed names
  (D91.2).
- **D92.6 GFS v17.** Unchanged since D90.2 (same day).
END D92

## Step 2: reference re-check (before any move)

Search `scripts/`, `.github/`, `requirements.txt` and `.gitignore` for the
literal `docs/` and for the quoted path component `"docs"` or `'docs'`.
Session 98 found only text hits (docstrings in `session76_verify.py`,
`session76b_cache.py` and `session90_airport_check.py`) and no code hit.
Classify every hit as (a) code (the path is opened, read, written, hashed,
listed or passed to a command when the script runs) or (b) text. **If any
(a) hit exists, stop before moving anything** and report.

## Step 3: the moves (D92.2)

1. Record the SHA-256 of every file to be moved: every `docs/session-*.md`
   (tracked ones, the untracked `docs/session-98c.md` and nothing else) and
   every `docs/commit-*.txt`. Report the counts.
2. Create `docs/sessions/` and `docs/commits/`, then move with plain `mv`:
   each `docs/session-*.md` into `docs/sessions/`, each
   `docs/commit-*.txt` into `docs/commits/`. File names unchanged.
3. **Check, and report each:**
   - every moved file exists at its new path with its SHA-256 unchanged
     (report: files, matches, mismatches);
   - nothing is left at any old path;
   - `ls -A docs` is exactly: `.DS_Store` (if present),
     `HANDOVER-richer-features.md`, `PROJECT-INSTRUCTIONS.md`, `README.md`,
     `commits`, `sessions`;
   - `git status --porcelain` shows each tracked old path as deleted
     (`D`) and the two new folders as untracked (`??`), and nothing under
     `scripts/`, `data/`, `notes/` or `.github/` changed. Git detects the
     moves when the owner stages the files.

In the output file, list every move as `old path -> new path, SHA-256`.

## Step 4: path edits in live files

Change **only** the items below. Report every changed line as a before
and after pair.

1. **`CLAUDE.md`.**
   - `docs/commit-NN.txt` becomes `docs/commits/commit-NN.txt`, in both
     places (the sentence on who writes the commit message, and the
     `git commit -F` command).
   - "kept together in the `docs/` folder" becomes "kept together in the
     `docs/sessions/` folder".
2. **`docs/PROJECT-INSTRUCTIONS.md`.**
   - Section 1: "apart from writing session docs and commit-message files
     into docs/ (§4, §8)" becomes "apart from writing session docs into
     docs/sessions/ and commit-message files into docs/commits/ (§4, §8)".
   - Section 4, item 1: `docs/session-NN.md` becomes
     `docs/sessions/session-NN.md`. Leave the sentence about the
     Filesystem extension's access to docs/ and notes/ as it is (still
     true).
   - Section 8: `docs/commit-NN.txt` becomes `docs/commits/commit-NN.txt`,
     in both places.
   - Add this paragraph at the end of section 4: "The invocation Zac
     pastes into Claude Code takes this form (DECISIONS D92.4): Read
     CLAUDE.md, then SPEC.md, STATUS.md, and DECISIONS.md in full. Then
     carry out the session defined in docs/sessions/session-NN.md, staying
     strictly within its scope. Stop at the end-of-session steps and wait
     for my review. Do not commit anything."
3. **`docs/README.md`** (a reader file written in session 98b). Update the
   loop so the prompt is `sessions/session-NN.md` and the commit message
   is `commits/commit-NN.txt`, each linked to its folder. Add one short
   line under the heading for the loop or above it naming the two
   subfolders. Add "(D92.2)" where the layout is stated. Keep the rest.
4. **`notes/README.md`.** The sentence "The prompt for session NN is
   `session-NN.md` in [../docs/](../docs/README.md)." becomes "The prompt
   for session NN is `session-NN.md` in
   [../docs/sessions/](../docs/sessions/)."
5. **`scripts/README.md`.** "That session's prompt is `session-NN.md` in
   [../docs/](../docs/README.md)" becomes "That session's prompt is
   `session-NN.md` in [../docs/sessions/](../docs/sessions/)".
6. **Search** `README.md`, `SPEC.md`, `RESULTS.md`, `data/README.md` and
   the files above for any other text that places a session prompt or
   commit message directly under `docs/` (for example
   `docs/session-` or `docs/commit-`). Report each hit. Fix it only if it
   is in a file listed in items 1 to 5; report the rest without changing
   them. The root README's map row for `docs/` ("Session prompts, commit
   messages and the planning guide") stays as it is.

## Step 5: final checks (report each)

1. Every relative link in `README.md`, `docs/README.md`,
   `notes/README.md`, `scripts/README.md` and `data/README.md` resolves to
   an existing path (list links checked and any failures).
2. No U+2014 in any line added to an edited file, and none in D92.
3. `git status --porcelain --untracked-files=all` and `git diff --stat`:
   the only changes are the moves, and edits to `CLAUDE.md`,
   `docs/PROJECT-INSTRUCTIONS.md`, `docs/README.md`, `notes/README.md`,
   `scripts/README.md`, `DECISIONS.md` (D92 and F141 appended, plus any
   archive move), `DECISIONS-archive.md` (archive move only, if any) and
   `STATUS.md`, plus this session's output file.
4. SHA-256 of the five files in Step 0 item 4, unchanged.
5. `ls -A` of the root and of `docs/`, shown in full.

## Step 6: end of session

1. **F141.** Append F141 to `DECISIONS.md`: a finding for each of Steps 0
   to 5 with real values (counts, SHA-256 matches, the reference
   re-check), then "Readings made where the prompt is silent" (numbered),
   then "What this did not do". Mark plainly that no model experiment was
   run and no build choice was made.
2. **Overwrite `STATUS.md`** as a current-only snapshot (CLAUDE.md), with
   the new paths. Its last line:
   "**Next planning session:** Review session 98c. If it passed, the owner
   commits and pushes (with `git commit -F docs/commits/commit-98c.txt`)
   and sets the GitHub About box; then plan session 99: the first of
   D82.5's alternatives against the baseline, under D89.6. Re-check GFS
   v17."
3. **Consistency check** (CLAUDE.md): report anything that disagrees, any
   duplicated heading, any entry out of order, and any live file that
   still places a session prompt or commit message directly under
   `docs/`.
4. **Archive step** (CLAUDE.md), by the usual criterion, mechanically and
   verbatim.
5. Write the full real output to `notes/session-98c-output.txt`.
6. Stop and wait for the owner's review. Do not commit, add or push, and do
   not write a commit message.
