# Session 98b: repository cleanup for outside readers (after session 98's stop)

Owner: Zac. Written by the planning chat, 7 October 2026, after session 98
was committed and pushed as a stopped session (D90; output in
`notes/session-98-output.txt`).

## Purpose

Session 98 stopped at its reference gate: scripts read `SPEC.md`,
`DECISIONS.md` and `DECISIONS-archive.md` at the repo root and read or
write files under `notes/`, so D90.5's layout cannot happen. This session
carries out the replacement plan (D91): one safe move
(`PROJECT-INSTRUCTIONS.md` into `docs/`), the SPEC 6 pointer (D90.8), the
libomp gate (D90.9), figures, a rewritten root README and a short README in
each main folder. It runs no model experiment and makes no build choice.
Stage C's first D82.5 comparison is session 99 (D90.3).

## Standing rules for this session (read before anything else)

1. **The record is not edited.** No existing DECISIONS or archive entry is
   changed. No existing file in `docs/` or `notes/` is edited (new README
   files are added there). No script, no data file, and not the workflow
   file (`.github/workflows/stagec-grib-pull.yml`) is edited, moved or
   renamed. Git history is not touched. You never touch the git index (no
   `git mv`, `git add`, `git rm`).
2. **The one move is byte for byte**, with plain `mv`, its SHA-256 checked
   before and after.
3. **No em-dash (U+2014) in any new text** (D76.6, D90.11): README files,
   figure text, D91, F140, STATUS, script comments, everything. Use a
   colon, a comma, brackets or a new sentence. Existing text keeps its
   dashes.
4. **Plain writing** (CLAUDE.md): simple words, short sentences, define
   jargon on first use.
5. **Numbers come from the record only.** Every number in a README or
   figure is copied from SPEC, DECISIONS or a committed data file, and is
   cited to its entry (for example F109, F125.6). No new number is computed
   except figure geometry. **No build-choice score is quoted anywhere
   (SPEC 2.5):** none of F139's cross-validation scores appear in any README
   or figure.
6. **Nothing is installed** (no `pip install`, no `brew install`). **No
   network.** `MLwx-stagec/` is read only by Step 5's gate and is not
   changed. `MLwx-pull/` is not touched.
7. Run Python with `.venv/bin/python -B` (no bytecode files).
8. If anything in this prompt disagrees with SPEC, CLAUDE.md or what you
   find, **stop and report**. Do not guess.

## The layout after this session (D91.3)

The root keeps every file and folder it has now, except
`PROJECT-INSTRUCTIONS.md`, which moves into `docs/`. New: `figures/` at the
root, and a `README.md` in `scripts/`, `data/`, `docs/` and `notes/`.

---

## Step 0: start checks (read only)

1. `git status --porcelain` shows only `?? docs/session-98b.md`. Otherwise
   stop and report.
2. The last DECISIONS entry is D90; the last finding is F139. No D91 or
   F140 exists in either DECISIONS file.
3. SHA-256 equal to the values session 98 reported in
   `notes/session-98-output.txt` (Step 0.3), and report each:
   `scripts/session97_stagec_cv.py`, `scripts/session62_reserved_confirm.py`,
   `data/processed/session63_reserved_confirm_grid.csv`,
   `data/processed/session97_stagec_cv_scores.csv`,
   `.github/workflows/stagec-grib-pull.yml`.
4. None of these exist yet: `figures/`, `scripts/README.md`,
   `data/README.md`, `docs/README.md`, `notes/README.md`,
   `docs/PROJECT-INSTRUCTIONS.md`, `scripts/session98b_figures.py`.
5. Read CLAUDE.md, SPEC, STATUS and DECISIONS in full (as always), plus
   README.md, RESULTS.md, PROJECT-INSTRUCTIONS.md, `requirements.txt`,
   `.gitignore`, `notes/session-98-output.txt`, and the DECISIONS entries
   cited in this prompt.

## Step 1: record D91 (before any other edit)

Copy the text between the lines `BEGIN D91` and `END D91` below (those two
marker lines excluded) into the end of `DECISIONS.md` with `sed`, after the
usual separator, then check it byte-equal with `diff` and `cmp` against the
same extract. Report the line numbers it occupies. Do this before any other
edit.

BEGIN D91
## 2026-10-07: Session 98b decision: session 98's stop accepted, and the restructure replaced (owner, planning chat)

**D91. Owner decisions, planning chat (after session 98's stop): the stop
and its readings accepted, the restructure replaced, README section 8, and
session 98b.** Written at the start of session 98b, before any other edit.
No 2026-27 value has been read or scored.

- **D91.1 Session 98's stop accepted.** Its reference gate worked as
  intended. The planning chat had not checked the scripts' own path
  constants (for example `ROOT / "SPEC.md"` and `ROOT / "notes"`) before
  proposing D90.5. The owner accepts session 98's five readings
  (`notes/session-98-output.txt`).
- **D91.2 What stays at the root, and why.** `SPEC.md`, `DECISIONS.md`,
  `DECISIONS-archive.md` and `notes/` stay where they are. Scripts read or
  write them there, including stage B's 2026-27 scripts, which must run
  unchanged (D80.1, F129.6), and the frozen `session39_sealed_test.py` and
  `session62_reserved_confirm.py` (D62.3(a)). No copies or links are left
  at old paths.
- **D91.3 The layout (replaces D90.5).** One move:
  `PROJECT-INSTRUCTIONS.md` to `docs/PROJECT-INSTRUCTIONS.md`. No code
  reads it (session 98, Step 3). Every other file and folder stays where it
  is. New: a `README.md` in `scripts/`, `data/`, `docs/` and `notes/` (new
  files only; no existing file there is edited), and a `figures/` folder at
  the root for the README's figures, drawn by
  `scripts/session98b_figures.py`. The root README is rewritten.
- **D91.4 What D91 replaces in D90.** D90.5 (the layout) is replaced by
  D91.3. D90.6 now applies to one file only: entries written before
  session 98b that place `PROJECT-INSTRUCTIONS.md` at the root resolve to
  `docs/PROJECT-INSTRUCTIONS.md`. D90.7 is withdrawn: the invocation keeps
  its current form, written without a dash: "Read CLAUDE.md, then SPEC.md,
  STATUS.md, and DECISIONS.md in full. Then carry out the session defined
  in docs/session-NN.md, staying strictly within its scope. Stop at the
  end-of-session steps and wait for my review. Do not commit anything."
  In D90.10, the figures go in `figures/` and the script is
  `scripts/session98b_figures.py`. D90.1 to D90.4, D90.8, D90.9, D90.10's
  other rules, D90.11 and D90.12 stand.
- **D91.5 README section 8 (data credits) is updated, not carried over
  word for word.** It adds what was committed or published after it was
  written: the NBM values (F127.3; read from NOAA's NBM archive on AWS,
  bucket `noaa-nbm-grib2-pds`), the raw GFS MOS (MAV) responses from the
  IEM archive (F127.3), the IEM observations for 45 further airports
  (F132.4), and stage C's point values published as Release files (F137,
  derived from NOAA GFS). NBM's terms (planning-chat check of
  https://registry.opendata.aws/noaa-nbm, 2026-10-07, not checked by this
  session): NOAA requests attribution for unaltered NOAA data; it is not
  permitted to state or imply endorsement by or affiliation with NOAA; and
  modified NOAA data may not be presented as original, unaltered NOAA data.
  NBM and NWS MOS leave the "probed only, no data committed" list.
- **D91.6 The personal path in D84.3** (session 98, Step 2.4) is accepted
  as it is. The record is not edited (D90.4). It shows only the owner's
  user name, which the saved outputs already show (F126.2).
- **D91.7 GFS v17.** Unchanged since D90.2 (same day).
- **D91.8 Session 98b** records D91, makes D91.3's move, carries out D90.8
  (the SPEC 6 pointer) and D90.9 (the libomp gate), draws the figures and
  writes the README files under D90.10, D90.11 and D91.5. F140 records
  sessions 98 and 98b.
END D91

## Step 2: reference re-check (before the move)

Session 98's Step 3 found no reference to `PROJECT-INSTRUCTIONS.md` in
`scripts/`, `.github/`, `requirements.txt` or `.gitignore`. Confirm it
(`grep -rnI "PROJECT-INSTRUCTIONS"`). Also search the same places for code
that would collide with the new files: any read or write of a path named
`README.md` under `scripts/`, `data/`, `docs/` or `notes/`, or of a
`figures` folder (search for `README` and for the quoted component
`"figures"`). Classify hits as (a) code or (b) text, as session 98 did.
**If any (a) hit exists, stop before the move** and report.

## Step 3: the move (D91.3)

1. Record the SHA-256 of `PROJECT-INSTRUCTIONS.md`.
2. `mv PROJECT-INSTRUCTIONS.md docs/PROJECT-INSTRUCTIONS.md`.
3. Check: the new file's SHA-256 equals the recorded value; nothing is left
   at the old path; `git status --porcelain` shows the old path deleted
   (`D`) and the new one untracked (`??`). Git detects the move when the
   owner stages the files.

## Step 4: path and pointer edits

Report every changed line as a before and after pair. Change nothing else.

1. **`CLAUDE.md`.** Change "**PROJECT-INSTRUCTIONS.md** (repo root)" to
   "**PROJECT-INSTRUCTIONS.md** (in `docs/`)". Report any other line in
   CLAUDE.md that places it at the root, and fix only that path.
2. **`docs/PROJECT-INSTRUCTIONS.md`.** In the table in section 2, change
   "Kept in the repo root" to "Kept in docs/". Report any other line that
   places this file at the root, and fix only that path.
3. **`SPEC.md` (D90.8).** In section 6, stage C bullet, replace the
   sentence "Its next steps are in DECISIONS D88." with "Its development
   table and baseline are set in DECISIONS D88, and the rules for its
   build choices in DECISIONS D89."

## Step 5: libomp (D90.9)

Record each command and its real output.

1. `brew --version`; `brew list --versions libomp`.
   **If libomp is not listed:** skip items 2 to 5, record that the shim
   stays the rule, and go to item 6.
2. Find LightGBM's library inside `.venv` (`find .venv -name
   'lib_lightgbm*'`) and show `otool -L` of it, filtered to `omp`.
3. Show which libomp is loaded without the shim:
   `env -u DYLD_LIBRARY_PATH MLWX_LIBOMP_PATH_SET=1 DYLD_PRINT_LIBRARIES=1 .venv/bin/python -B -c "import lightgbm; print(lightgbm.__version__)" 2>&1 | grep -i -E 'omp|^4\.'`
   Setting `MLWX_LIBOMP_PATH_SET=1` makes the record scripts' shim skip
   itself. If `DYLD_PRINT_LIBRARIES` prints nothing, say so and continue.
4. **The gate, with the shim bypassed:**
   `env -u DYLD_LIBRARY_PATH MLWX_LIBOMP_PATH_SET=1 .venv/bin/python -B scripts/session97_stagec_cv.py --gate`
   It must print the six F109 values with exact equality, 6 of 6, as F139.3
   did.
5. With `TMP=$(mktemp -d)`:
   `env -u DYLD_LIBRARY_PATH MLWX_LIBOMP_PATH_SET=1 .venv/bin/python -B scripts/session97_stagec_cv.py --score --airports EGLC --out-dir "$TMP"`.
   Its rows must be byte-equal to EGLC's rows in
   `data/processed/session97_stagec_cv_scores.csv` (`diff` and `cmp`, as
   F139.5 did). Delete the temporary folder afterwards.
6. **`requirements.txt`: comment text only.** The package lines must stay
   byte-identical (check: the non-comment lines before and after give no
   `diff`).
   - Rewrite the block headed "OpenMP note" in plain words to say:
     LightGBM on macOS needs the OpenMP library `libomp.dylib`; the
     standard fix is `brew install libomp`; what session 98b found (F140:
     the Homebrew and libomp versions, and the gate result); that older
     scripts keep a loader workaround that points at scikit-learn's copy
     and cannot be edited because they are part of the record; that this
     workaround is harmless when Homebrew's libomp is present; and that
     scikit-learn stays pinned for that reason. If item 1 found no libomp,
     write the same block without the session 98b result, and say the
     workaround is still needed.
   - In the eccodes block, change only "This machine has no Homebrew and
     no system eccodes/GRIB library" to "When this was set up (session
     36), the machine had no Homebrew and no system eccodes/GRIB library".

If the gate (item 4) or the byte check (item 5) fails, do not stop the
session: record the result in full, keep the shim as the rule, and say so
in the README and `requirements.txt`.

## Step 6: figures (D90.10, D91.3)

Write `scripts/session98b_figures.py`: Python standard library only (no
numpy, no matplotlib), offline. It reads committed files only, checks each
input's SHA-256 before reading it, writes SVG files into `figures/`, and
refuses to overwrite a file that exists (the project's write-once rule,
SPEC 8.7 item 5). It prints every value it draws. Style for both figures: a
solid white background rectangle (so the figure reads in GitHub's dark
mode), a sans-serif font stack, a `<title>` and `<desc>` element for screen
readers, the values printed on the chart to four decimals for MAE and one
for percentages, and no em-dash.

1. **Required: `figures/headline_mae.svg`.** Grouped bars, one group per
   airport (EGLC, LFPG, DSM, YSDU, RNO, in that order): raw GFS MAE and the
   selected-features method's MAE on the reserved year 2024-08-01 to
   2025-07-31 (F109). Source:
   `data/processed/session63_reserved_confirm_grid.csv` (columns `raw_mae`
   and `final_mae`). Y axis: "MAE (degrees C)", starting at zero. Title:
   "Selected-features method vs raw GFS, reserved year 2024-25 (F109)".
   KSFO is not in this figure (D71.5: not directly comparable).
2. **Optional: `figures/skill_intervals.svg`.** Skill with its 95% interval
   (F125.6) for the same five airports, in two panels side by side: skill
   over raw GFS, and skill over persistence. A point and a horizontal bar
   per airport, with a line at zero. Make it **only if** every value can be
   read by the script from a committed file (a data file if one exists,
   otherwise the saved output that F125 cites, under `notes/`), **and**
   every value equals the figure printed in F125.6 at F125.6's precision.
   Otherwise do not make it, and report why.
3. **Checks:** run the script once; then copy `figures/` to a temporary
   folder, delete the originals, run again, and confirm each new SVG is
   byte-equal to its copy (`cmp`); delete the temporary copy. Report the
   SHA-256 of each SVG and of the script. Check that the headline figure's
   ten printed values equal the grid file's values and, rounded to four
   decimals, the README table's values.

No other figure is made. (A three-method chart was considered and dropped:
the minimal method's raw GFS comes from Open-Meteo and the other methods'
from GRIB, and the methods were tested on different years, so one chart
would invite a wrong comparison.)

## Step 7: the README files (D90.10, D91.3, D91.5)

General rules for all five files: rules 3 to 5 at the top of this prompt;
relative links only; short paragraphs; tables only where they help. Draw
facts from SPEC, STATUS, DECISIONS and RESULTS, and cite them. Where you are
unsure whether a statement is supported by the record, leave it out.

### 7.1 Root `README.md` (full rewrite)

Order and content:

1. **Title** "MLwx" and a one-line subtitle: machine-learning correction of
   GFS temperature forecasts at airports.
2. **In 30 seconds.** Four to six sentences, no jargon left undefined: what
   the project does (learns GFS's repeated local error at an airport from
   past forecasts and observations, and corrects new forecasts); the
   headline (at five airports on the reserved year, the selected-features
   method lowers mean absolute error against raw GFS by 12.2% to 21.0%,
   and every 95% interval lies above zero, F109, F125.6); that each claim
   came from a held-out year opened once, with the pass rule fixed in
   writing first; and what is being built now (stage C: an hourly curve
   for every GFS run, D82).
3. **The headline figure** (`figures/headline_mae.svg`) with a one-line
   caption, then the current README's table and its four caveats, carried
   over. Their numbers and meaning are unchanged; wording may be tightened.
   If the optional figure exists, place it after the caveats with its own
   caption.
4. **What this project demonstrates.** Five to seven short bullets, each
   cited. Use only these facts:
   - pre-registered, one-look evaluation: the pass bar fixed in writing
     before a held-out year is opened, one look per year (SPEC 2.4, 5.0;
     F94, F109);
   - a failure reported honestly: the minimal method failed at Reno (F82);
     a richer method was built and then passed on a fresh look (F94); both
     results stand (D48.13);
   - benchmarked against operational products: the comparison with NWS MOS
     and the National Blend of Models on the spent years was MIXED (F127),
     and the direction decision followed (D78.1);
   - data engineering: stage C's pull read GFS GRIB2 files by byte range on
     GitHub Actions, 65 months, 195,600 files, 1,932,528 messages, each
     month checked before it was published as a Release file (F137, D87);
   - leakage control: time-ordered splits only, guards in code against
     using held-out or future years (SPEC 2.1, D89.3, F139.5);
   - reproducibility: pinned packages, raw pulls committed with their pull
     date and query, SHA-256 checks on inputs, byte-for-byte repeat runs
     (SPEC 2.3, F138, F139.5);
   - the same recipe at every airport, nothing tuned per airport (SPEC 2.5).
5. **How it works.** A Mermaid diagram (a ```mermaid block, which GitHub
   draws), left to right, with these steps only: hourly airport
   observations (IEM) and GFS forecasts (GRIB2 from NOAA on AWS) are
   matched at the airport's grid point; features are built; a LightGBM
   model (gradient-boosted trees) learns the residual, observed minus
   forecast; the corrected forecast is GFS plus the predicted residual; it
   is scored against raw GFS and persistence on a held-out year. Use
   plain-text labels (no em-dash). Then the current README's "Target",
   "Three methods" and "Discipline" text, carried over and tightened.
6. **Status and roadmap.** Rewrite from STATUS and SPEC 6: stage A done
   (F123 to F125, F127, D78.1); stage B pre-registered with frozen models
   and gated scripts, not yet run, scored only after each period ends (D73,
   F122, F128, F129); stage C under way: design (D82, D83), pull complete
   (F137), development table built and gated (F138), cross-validation rules
   fixed (D89), baseline fitted (F139). **Do not quote F139's scores.**
   Then stages D to H in one line each, and the new airports track.
7. **Repository map.** A table of every root entry, grouped as: **Start
   here** (`README.md`, `RESULTS.md`, `figures/`); **The research record**
   (`SPEC.md`, `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`); **Code
   and data** (`scripts/`, `data/`, `requirements.txt`, `.github/`); **How
   the work was run** (`docs/`, `notes/`, `CLAUDE.md`); and `LICENSE`. One
   line each on what it is; folders link to their README. Then two
   sentences: the record files sit at the root, and scripts are named by
   session number, because the scripts read them there and the record cites
   them by path (D91.2).
8. **Reproducing.** Carry over the current section, with the libomp outcome
   from Step 5. Keep the honest line that the full run order is spread
   across DECISIONS, and add that `scripts/README.md` lists the scripts
   behind each headline result.
9. **How this was built.** Carry over the current paragraph unchanged in
   meaning: the owner planned the work, made every decision, wrote every
   session prompt and reviewed every change; the code was written by Claude
   Code (Anthropic's AI coding tool) one scoped session at a time; every
   change was reviewed and committed by hand. Link to `docs/` and `notes/`
   for the full working record.
10. **Data credits and terms.** Carry over the current section 8 and update
    it as D91.5 says. Keep its existing entries' wording; add the new items
    from D91.5 in the same style, each with its entry; keep the line that
    the terms were read on 2026-09-29 and add that NBM's were read on
    2026-10-07 (D91.5).
11. **Licence.** Carry over section 9, then a final line: "Author:
    Zachary Adams."

Aim for a README a reviewer can skim in two minutes: sections 2 to 4
should fit on one or two screens.

### 7.2 `docs/README.md`

What the folder is: the working record of how each session was planned.
Explain the loop in a few sentences: the owner plans each session in a
planning chat and writes its prompt (`session-NN.md`); Claude Code carries
out that one session and saves its real output in `../notes/`; the owner
reviews it and commits it by hand, with the commit message saved as
`commit-NN.txt`. Name `PROJECT-INSTRUCTIONS.md` (the planning guide; moved
here from the root by D91.3) and `HANDOVER-richer-features.md` (say what it
is from its own text). Suffixes such as `03b`, `34a` and `98b` mark a
session that was split or re-run.

### 7.3 `notes/README.md`

What the folder is: each session's saved real output
(`session-NN-output.txt` and similar), the audit reports
(`audit-session-*.md`), and other records named in DECISIONS. Scripts
write some of these files here and the record cites them by path, so the
folder and file names stay as they are (D91.2). Note that some files
contain file paths from the author's machine (F126.2).

### 7.4 `scripts/README.md`

1. How the scripts are named and run: `sessionNN_*.py` was written in
   session NN; its prompt is `docs/session-NN.md` and its output is in
   `notes/`; run with `.venv/bin/python scripts/<name>.py`. Why the names
   are kept (the record cites the scripts by path, and frozen scripts check
   each other's SHA-256).
2. **Frozen scripts**, never edited: list them, from SPEC and DECISIONS
   (at least `session39_sealed_test.py`, `session48_reserved_year.py`,
   `session60_combine_design.py`, `session62_reserved_confirm.py`; add any
   other the record marks frozen or unchangeable, such as stage B's
   2026-27 scripts under D80.1, with its entry).
3. **Key scripts, by result.** A table with about 20 to 30 rows: script,
   what it does in one line, and the DECISIONS entry. Group the rows: the
   minimal method (its pull, model and sealed test per airport); the
   richer method (GRIB pull, decode, join, sealed test; F94); the
   selected-features method (the E1 to E5 experiments, the combine sweep,
   the reserved-year build and confirmation; F109); KSFO (F119); stage B
   (the frozen models and the 2026-27 build, competitor fetch and scoring
   scripts); stage C (pull, verify, release check, development table,
   cross-validation); and `session98b_figures.py`. Each role must come from
   the script's docstring or the cited entry, not from its name alone.
4. **Everything else**: one line per session range (for example "sessions
   01 to 33: per-airport checks, pulls and models for the minimal method").
5. One sentence: the GitHub Actions workflow
   (`.github/workflows/stagec-grib-pull.yml`) runs
   `session91_grib_pull.py` and `session92_verify_chunk.py`.

### 7.5 `data/README.md`

What each folder holds, from the record: `raw/` (IEM observations,
Open-Meteo JSON, GRIB pull manifests and small samples under
`diagnostics/`, and the rest of its subfolders; each raw file has a
`.meta.txt` with its pull date and exact query, SPEC 2.3; the bulk GRIB
cache `raw/grib` is not committed, D47); `processed/` (built tables and
result files, named by the session that wrote them); `models/` (the frozen
2026-27 models, F122); `rebuild/` (what the record says it is, cited).
Then stage C's data, which is outside the repo: the Release
`stagec-grib-pull-v1` (F137) and the local folders `MLwx-pull/` and
`MLwx-stagec/` beside the repo (D88.8). End with a pointer to the data
terms in the root README.

## Step 8: final checks (report each)

1. Every relative link in the five README files resolves to an existing
   path (list links checked and any failures).
2. No U+2014 in any new file, and no U+2014 in any line added to an edited
   file (check the added lines of each diff).
3. `git status --porcelain` and `git diff --stat`: the only changes are
   the move, the new files (`figures/`, the four folder READMEs,
   `scripts/session98b_figures.py`, `docs/session-98b.md`, this session's
   output file), and edits to `CLAUDE.md`, `docs/PROJECT-INSTRUCTIONS.md`
   (after the move), `SPEC.md`, `DECISIONS.md` (D91 and F140 appended, plus
   any archive move), `DECISIONS-archive.md` (archive move only, if any),
   `STATUS.md`, `README.md` and `requirements.txt` (comment lines only).
   Nothing else under `scripts/`, `data/`, `docs/`, `notes/` or `.github/`
   changed.
4. SHA-256 of the files checked in Step 0 item 3, unchanged.
5. No new `__pycache__` written.
6. The root listing (`ls -A`), shown in full.

## Step 9: end of session

1. **F140.** Append F140 to `DECISIONS.md`. Open it with one short item on
   session 98 (it recorded D90, ran its audit, and stopped at Step 3; full
   output `notes/session-98-output.txt`; no F entry was written then). Then
   a finding for each of this session's Steps 0 to 8, with real values
   (SHA-256 values, the gate results, the libomp path and versions, which
   figures were made and why), then "Readings made where the prompt is
   silent" (numbered, for the owner to confirm), then "What this did not
   do". Mark plainly that no model experiment was run and no build choice
   was made.
2. **Overwrite `STATUS.md`** as a current-only snapshot (CLAUDE.md). Clear
   the session 98 open questions that D91 settles. Its last line:
   "**Next planning session:** Review session 98b. If it passed, the owner
   commits and pushes and sets the GitHub About box; then plan session 99:
   the first of D82.5's alternatives against the baseline, under D89.6.
   Re-check GFS v17."
3. **Consistency check** (CLAUDE.md): re-read CLAUDE.md, SPEC, STATUS and
   DECISIONS and report anything that disagrees, any duplicated heading,
   any entry out of order, and any live file that still places
   `PROJECT-INSTRUCTIONS.md` at the root.
4. **Archive step** (CLAUDE.md), by the usual criterion, mechanically and
   verbatim.
5. Write the full real output to `notes/session-98b-output.txt`.
6. Stop and wait for the owner's review. Do not commit, add or push, and do
   not write a commit message.
