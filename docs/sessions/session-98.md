# Session 98: repository restructure and cleanup for outside readers

Owner: Zac. Written by the planning chat, 7 October 2026, after session 97
was committed and pushed (D89, F139).

## Purpose

The repository is public (https://github.com/zadams03/MLwx). This session
makes it read well to an outside reviewer, above all through a clear file
structure, **without changing the work or the record**. It moves the
record files into two folders, rewrites the README, adds a short README to
each main folder, adds one or two figures drawn from committed data, and
settles the libomp question. It runs no model experiment and makes no build
choice. Stage C's first D82.5 comparison moves to session 99 (D90.3).

## Standing rules for this session (read before anything else)

1. **The record is not edited.** No existing DECISIONS or archive entry is
   changed. No file in `docs/` or `notes/` is edited. No script, no data
   file, and not the workflow file (`.github/workflows/stagec-grib-pull.yml`)
   is edited, moved or renamed. Git history is not touched.
2. **Moves are byte for byte.** Files are moved with plain `mv` (not
   `git mv`: you never touch the git index). Every moved tracked file's
   SHA-256 is recorded before the move and checked after it.
3. **No em-dash (U+2014) in any new text** (D76.6, D90.11): README files,
   figure text, D90, F140, STATUS, script comments, everything. Use a colon,
   a comma, brackets or a new sentence. Existing text keeps its dashes.
4. **Plain writing** (CLAUDE.md): simple words, short sentences, define
   jargon on first use.
5. **Numbers come from the record only.** Every number in a new README or
   figure is copied from SPEC, DECISIONS or a committed data file, and is
   cited to its entry (for example F109, F125.6). No new number is computed
   except figure geometry. **No build-choice score is quoted anywhere
   (SPEC 2.5):** none of F139's cross-validation scores appear in any README
   or figure.
6. **Nothing is installed** (no `pip install`, no `brew install`). **No
   network.** `MLwx-stagec/` and `MLwx-pull/` are read only where Step 6
   says, and are not changed.
7. Run Python with `.venv/bin/python -B` (no bytecode files).
8. If anything in this prompt disagrees with SPEC, CLAUDE.md or what you
   find, **stop and report**. Do not guess.

## The target layout (D90.5)

```
MLwx/
├── README.md              (rewritten, Step 8)
├── LICENSE                (unchanged)
├── requirements.txt       (comment text only, Step 6)
├── CLAUDE.md              (stays at root: Claude Code reads it there)
├── .gitignore             (unchanged)
├── .github/               (unchanged)
├── scripts/               (unchanged, plus README.md and one new script)
├── data/                  (unchanged, plus README.md)
├── research/
│   ├── README.md          (new)
│   ├── SPEC.md            (from root)
│   ├── RESULTS.md         (from root)
│   ├── DECISIONS.md       (from root)
│   ├── archive/
│   │   └── DECISIONS-archive.md   (from root)
│   └── figures/           (new, Step 7)
└── audit/
    ├── README.md          (new)
    ├── session98_path_map.csv     (new, Step 4)
    ├── STATUS.md          (from root)
    ├── PROJECT-INSTRUCTIONS.md    (from root)
    ├── sessions/          (was docs/)
    └── outputs/           (was notes/)
```

`scripts/` and `data/` stay where they are because the code depends on
their paths: every script finds the repo root as one folder up, scripts
import each other, frozen scripts and the workflow name them by path, and
data paths are hard-coded.

---

## Step 0: start checks (read only)

1. `git status --porcelain` shows only `?? docs/session-98.md`. Otherwise
   stop and report.
2. The last entries are D89 and F139. No D90 or F140 exists in either
   DECISIONS file.
3. SHA-256 equal to the record (report each):
   `scripts/session97_stagec_cv.py` (F139), `scripts/session62_reserved_confirm.py`
   (D70.2), `data/processed/session63_reserved_confirm_grid.csv`
   (`0138ba039d0bd077e71b829789a8d3c93175e22493ed115f7503b2baa30f4ed3`),
   `data/processed/session97_stagec_cv_scores.csv` (F139.4), and
   `.github/workflows/stagec-grib-pull.yml` (full value from F137 or the
   entry that records it).
4. None of these exist yet: `research/`, `audit/`, `data/README.md`,
   `scripts/README.md`, `scripts/session98_figures.py`.
5. Read CLAUDE.md, SPEC, STATUS and DECISIONS in full (as always), plus
   README.md, RESULTS.md, PROJECT-INSTRUCTIONS.md, `requirements.txt`,
   `.gitignore`, and the DECISIONS entries cited in this prompt.

## Step 1: record D90 (before any other edit)

Copy the text between the lines `BEGIN D90` and `END D90` below (those two
marker lines excluded) into the end of `DECISIONS.md` with `sed`, then
check it byte-equal with `diff` and `cmp` against the same extract. Report
the line numbers it occupies. Do this before any other edit.

BEGIN D90
## 2026-10-07: Session 98 decision: F139 accepted, GFS v17, and the repository restructure (owner, planning chat)

**D90. Owner decisions, planning chat (after session 97): F139 accepted,
GFS v17, the session order, and the repository restructure.** Written at
the start of session 98, before any other edit. No 2026-27 value has been
read or scored.

- **D90.1 F139 accepted.** The owner accepts F139 and all ten F139.6
  readings. D89.4 is clarified: "not imported here" means that
  `scripts/session97_stagec_cv.py` never imports or calls the session-48
  reserved-year guard itself. The record script it imports,
  `scripts/session62_reserved_confirm.py`, loads the session-48 module at
  load time for its own use, as F139.6.1 reads.
- **D90.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-07, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is still SCN 26-89 (2 October
  2026). With 30 days' notice the earliest go-live is now about 6 November
  2026.
- **D90.3 Session order.** Session 98 is a repository restructure and
  cleanup for outside readers. The first of D82.5's alternatives against
  the baseline (D89.10) moves to session 99. Nothing else in D89 changes.
  The hold rule (D73.8) is unchanged.
- **D90.4 Purpose and limits.** The public repository should read well to
  an outside reviewer without changing the work or the record. No existing
  DECISIONS or archive entry is edited. No file of the working record
  (session prompts, commit messages, saved outputs, audits) is edited. No
  script, data file or the workflow file is edited, moved or renamed. Git
  history is not rewritten. Files that move are moved byte for byte.
- **D90.5 The layout.** The root keeps `README.md`, `LICENSE`,
  `requirements.txt`, `CLAUDE.md` (Claude Code reads it from the root),
  `.gitignore`, `.github/`, `scripts/` and `data/`. `scripts/` and `data/`
  stay because the code depends on their paths. `research/` holds
  `SPEC.md`, `RESULTS.md`, `DECISIONS.md`, `archive/DECISIONS-archive.md`
  and `figures/`. `audit/` holds `STATUS.md`, `PROJECT-INSTRUCTIONS.md`,
  `sessions/` (formerly `docs/`) and `outputs/` (formerly `notes/`).
  `audit/session98_path_map.csv` lists every moved tracked file's old path,
  new path and SHA-256. Each of `research/`, `audit/`, `scripts/` and
  `data/` gets a short `README.md` that explains the folder.
- **D90.6 Citations.** Entries written before session 98 cite the old
  paths (for example `notes/session-85-output.txt`, `docs/session-97.md`,
  or a bare `STATUS.md`). They are not edited; they resolve through D90.5's
  path map. From session 98 on, new text cites the new paths. The live
  files `CLAUDE.md`, `PROJECT-INSTRUCTIONS.md`, `SPEC.md` and `STATUS.md`
  have their path references updated in session 98, with no other change
  except D90.8.
- **D90.7 The session invocation from session 99:** "Read CLAUDE.md, then
  research/SPEC.md, audit/STATUS.md, and research/DECISIONS.md in full.
  Then carry out the session defined in audit/sessions/session-NN.md,
  staying strictly within its scope. Stop at the end-of-session steps and
  wait for my review. Do not commit anything."
- **D90.8 SPEC 6.** Stage C's bullet points to D88 for the development
  table and baseline and to D89 for the rules for its build choices.
- **D90.9 libomp.** The owner installed Homebrew (version 7.0.8) and found
  that lightgbm 4.7.0 imports in a fresh interpreter with no loader shim
  (owner's terminal, 2026-10-07). Session 98 records which libomp library
  is loaded and gates it: with the shim bypassed, `session97_stagec_cv.py
  --gate` must reproduce F109's six values exactly, and its EGLC `--score`
  must be byte-equal to EGLC's committed rows. If both pass, scripts from
  session 99 on may import lightgbm directly, without the shim. Scripts
  that import a record script still run that script's shim, which is
  harmless. scikit-learn stays pinned, because the frozen scripts' shim
  uses its copy of libomp. If Homebrew's libomp is absent or the gate fails,
  the shim stays the rule and the README and `requirements.txt` only
  document it. The session installs nothing.
- **D90.10 Reader-facing files.** `README.md` is rewritten for outside
  readers. Figures in `research/figures/` are drawn by
  `scripts/session98_figures.py` (Python standard library only) from
  committed files only. Every number in a README or figure is copied from
  the record and cited. No build-choice score is quoted (SPEC 2.5). The
  README ends with the author's name, Zachary Adams.
- **D90.11 Writing rule.** No em-dash in any new text (D76.6), including
  the README files, figure text, D90, F140, STATUS and commit messages.
- **D90.12 Later work, not this session.** A `tests/` folder with a real
  test suite (the leakage guards and a reproduction of the headline from
  committed data) after stage C's first D82.5 comparison; a `src/` package
  only at stage G. Neither folder is created empty.
END D90

## Step 2: read-only audit (report only, fix nothing)

Report each in the output file:

1. `git ls-files | wc -l`, and `git count-objects -vH`.
2. Tracked files that look like clutter: `git ls-files` matching
   `.DS_Store`, `__pycache__`, `*.pyc`, `.venv`, `.claude`, `*.log`.
3. The 15 largest tracked files with sizes.
4. Tracked files outside `docs/` and `notes/` that contain an absolute
   path from this machine (`/Users/`) or anything that looks like a secret
   (`token`, `api_key`, `password`, `BEGIN .* PRIVATE KEY`). Compare with
   F126's baseline and report only what is new since F126.
5. Statements in the current README.md that STATUS or DECISIONS have made
   stale (list them; Step 8 replaces the README anyway).

If anything here needs fixing outside this session's scope, log it as an
open question in F140. Do not fix it.

## Step 3: the reference gate (before any move)

Search `scripts/`, `.github/`, `requirements.txt` and `.gitignore` for any
reference to a path that will move: `docs/`, `notes/`, `SPEC.md`,
`STATUS.md`, `DECISIONS.md`, `DECISIONS-archive.md`, `RESULTS.md`,
`PROJECT-INSTRUCTIONS.md`.

Classify every hit as:
- **(a) code:** the path is opened, read, written, hashed, listed or
  passed to a command when the script runs; or
- **(b) text:** a comment, a docstring, or a string that is only printed.

Report counts per file, and list every (a) hit in full with its line.
**If any (a) hit exists, stop before moving anything:** write the output
file to `notes/session-98-output.txt` (the old location), overwrite STATUS
with the stop reason, and wait. Text hits (b) are expected and are left
alone: scripts are not edited, and D90.6's path map resolves them.

## Step 4: the moves

1. Build `audit/session98_path_map.csv` with the header
   `old_path,new_path,sha256` and one row per **tracked** file that moves,
   from `git ls-files` (so untracked and ignored files such as `.DS_Store`
   are not listed). Rows in `git ls-files` order. The moves are:
   - `SPEC.md` to `research/SPEC.md`
   - `RESULTS.md` to `research/RESULTS.md`
   - `DECISIONS.md` to `research/DECISIONS.md` (it already holds D90)
   - `DECISIONS-archive.md` to `research/archive/DECISIONS-archive.md`
   - `STATUS.md` to `audit/STATUS.md`
   - `PROJECT-INSTRUCTIONS.md` to `audit/PROJECT-INSTRUCTIONS.md`
   - every file under `docs/` to the same relative path under
     `audit/sessions/`
   - every file under `notes/` to the same relative path under
     `audit/outputs/`

   The SHA-256 is computed before the move. Write the map file before
   moving anything. It is the one file in `audit/` created before the moves
   (create `audit/` for it).
2. Move with plain `mv`: create `research/archive/`, then move the six
   files, then `mv docs audit/sessions` and `mv notes audit/outputs`. If a
   folder move leaves anything behind (for example an ignored
   `.DS_Store`), move what is left into the new folder and remove the empty
   old folder. Report what happened. This prompt (untracked) travels to
   `audit/sessions/session-98.md`; it is not in the map.
3. **Check, and report each:**
   - every row's `new_path` exists and its SHA-256 equals the row's value
     (report: rows, matches, mismatches);
   - no `old_path` exists any more, and `docs/` and `notes/` are gone;
   - the root listing (`ls -A`) is exactly: `.git`, `.github`, `.gitignore`,
     `.venv`, `.claude` (if present), `.DS_Store` (if present), `CLAUDE.md`,
     `LICENSE`, `README.md`, `audit`, `data`, `requirements.txt`,
     `research`, `scripts`;
   - `git status --porcelain` shows the old paths as deleted (`D`) and the
     new folders as untracked (`??`), and nothing under `scripts/`,
     `data/` or `.github/` as changed. Git does not store moves: it detects
     them when the owner stages the files, from the equal content.

## Step 5: path references in the live files

Change **only path references**, using this map: `docs/` to
`audit/sessions/`, `notes/` to `audit/outputs/`, and each moved file's name
to its new path where the text names where the file is or tells a reader to
open it. Do not reword anything else, except the items below. Report every
changed line as a before and after pair.

1. **`CLAUDE.md`.** Update the path references (for example the files to
   read, `docs/commit-NN.txt`, `notes/session-NN-output.txt`, "kept
   together in the `docs/` folder", "PROJECT-INSTRUCTIONS.md (repo root)",
   the archive's location). Add this one sentence as a new paragraph
   directly under the heading "## The three files": "SPEC.md, RESULTS.md,
   DECISIONS.md and the archive (archive/DECISIONS-archive.md) live in
   research/. STATUS.md and PROJECT-INSTRUCTIONS.md live in audit/. Session
   prompts and commit messages are in audit/sessions/, and saved outputs in
   audit/outputs/ (DECISIONS D90.5)."
2. **`audit/PROJECT-INSTRUCTIONS.md`.** Update the path references: section
   1 (the planning chat writes session docs and commit-message files into
   `audit/sessions/`, never writes to `audit/outputs/` or anywhere else,
   and may read `audit/outputs/` during a review); the table in section 2
   (each file shown with its new path; "Kept in the repo root" becomes
   "Kept in audit/"); section 4 (`audit/sessions/session-NN.md`; the
   Filesystem extension sentence should say it gives access to the repo
   folder, including `audit/sessions/` and `audit/outputs/`; the review
   reads the real output from `audit/outputs/`); section 7
   (`audit/outputs/session-NN-output.txt`); section 8
   (`audit/sessions/commit-NN.txt`, both places). Then add this paragraph
   at the end of section 4: "The invocation Zac pastes into Claude Code
   takes this form (DECISIONS D90.7): Read CLAUDE.md, then
   research/SPEC.md, audit/STATUS.md, and research/DECISIONS.md in full.
   Then carry out the session defined in audit/sessions/session-NN.md,
   staying strictly within its scope. Stop at the end-of-session steps and
   wait for my review. Do not commit anything."
3. **`research/SPEC.md`.**
   - Section 6, stage C bullet: replace the sentence "Its next steps are in
     DECISIONS D88." with "Its development table and baseline are set in
     DECISIONS D88, and the rules for its build choices in DECISIONS D89."
   - Search SPEC for `notes/`, `docs/` and the moved file names used as
     paths. Update each path (at least the G17 row's
     `notes/session-64-preflight-output.txt`, which becomes
     `audit/outputs/session-64-preflight-output.txt`). Report every hit.
4. **`research/RESULTS.md`, `research/DECISIONS.md`, the archive, and all
   of `audit/sessions/` and `audit/outputs/`: not edited** (D90.4, D90.6).
   RESULTS names SPEC.md and DECISIONS.md by file name only, which still
   holds because all three now sit together in `research/`.

## Step 6: libomp (D90.9)

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
4. **The gate, with the shim bypassed** (this also checks the scripts
   still run after the move):
   `env -u DYLD_LIBRARY_PATH MLWX_LIBOMP_PATH_SET=1 .venv/bin/python -B scripts/session97_stagec_cv.py --gate`
   It must print the six F109 values with exact equality, 6 of 6, as F139.3
   did.
5. `env -u DYLD_LIBRARY_PATH MLWX_LIBOMP_PATH_SET=1 .venv/bin/python -B scripts/session97_stagec_cv.py --score --airports EGLC --out-dir "$TMP"`,
   with `TMP=$(mktemp -d)`. Its rows must be byte-equal to EGLC's rows in
   `data/processed/session97_stagec_cv_scores.csv` (`diff` and `cmp`, as
   F139.5 did). Delete the temporary folder afterwards.
6. **`requirements.txt`: comment text only.** The package lines must stay
   byte-identical (check: the non-comment lines before and after give no
   `diff`).
   - Rewrite the block headed "OpenMP note" in plain words to say:
     LightGBM on macOS needs the OpenMP library `libomp.dylib`; the
     standard fix is `brew install libomp`; what session 98 found (F140:
     the Homebrew and libomp versions, and the gate result); that older
     scripts keep a loader workaround that points at scikit-learn's copy
     and cannot be edited because they are part of the record; that this
     workaround is harmless when Homebrew's libomp is present; and that
     scikit-learn stays pinned for that reason. If item 1 found no libomp,
     write the same block without the session 98 result, and say the
     workaround is still needed.
   - In the eccodes block, change only "This machine has no Homebrew and
     no system eccodes/GRIB library" to "When this was set up (session
     36), the machine had no Homebrew and no system eccodes/GRIB library".

If the gate (item 4) or the byte check (item 5) fails, do not stop the
session: record the result in full, keep the shim as the rule, and say so
in the README and `requirements.txt`.

## Step 7: figures (D90.10)

Write `scripts/session98_figures.py`: Python standard library only (no
numpy, no matplotlib), offline. It reads committed files only, checks each
input's SHA-256 before reading it, writes SVG files into
`research/figures/`, and refuses to overwrite a file that exists (the
project's write-once rule, SPEC 8.7 item 5). It prints every value it
draws. Style for both figures: a solid white background rectangle (so the
figure reads in GitHub's dark mode), a sans-serif font stack, a `<title>`
and `<desc>` element for screen readers, the values printed on the chart
to four decimals for MAE and one for percentages, and no em-dash.

1. **Required: `research/figures/headline_mae.svg`.** Grouped bars, one
   group per airport (EGLC, LFPG, DSM, YSDU, RNO, in that order): raw GFS
   MAE and the selected-features method's MAE on the reserved year
   2024-08-01 to 2025-07-31 (F109). Source:
   `data/processed/session63_reserved_confirm_grid.csv` (columns `raw_mae`
   and `final_mae`). Y axis: "MAE (degrees C)", starting at zero. Title:
   "Selected-features method vs raw GFS, reserved year 2024-25 (F109)".
   KSFO is not in this figure (D71.5: not directly comparable).
2. **Optional: `research/figures/skill_intervals.svg`.** Skill with its 95%
   interval (F125.6) for the same five airports, in two panels side by
   side: skill over raw GFS, and skill over persistence. A point and a
   horizontal bar per airport, with a line at zero. Make it **only if**
   every value can be read by the script from a committed file (a data
   file if one exists, otherwise the saved output that F125 cites, now
   under `audit/outputs/`), **and** every value equals the figure printed
   in F125.6 at F125.6's precision. Otherwise do not make it, and report
   why.
3. **Checks:** run the script once; then copy `research/figures/` to a
   temporary folder, delete the originals, run again, and confirm each new
   SVG is byte-equal to its copy (`cmp`); delete the temporary copy. Report
   the SHA-256 of each SVG and of the script. Check that the headline
   figure's ten printed values equal the grid file's values and, rounded to
   four decimals, the README table's values.

No other figure is made. (A three-method chart was considered and dropped:
the minimal method's raw GFS comes from Open-Meteo and the other methods'
from GRIB, and the methods were tested on different years, so one chart
would invite a wrong comparison.)

## Step 8: the README files (D90.10)

General rules for all five files: rules 3 to 5 at the top of this prompt;
relative links only (they must resolve on GitHub after the move); short
paragraphs; tables only where they help. Draw facts from SPEC, STATUS,
DECISIONS and RESULTS, and cite them. Where you are unsure whether a
statement is supported by the record, leave it out.

### 8.1 Root `README.md` (full rewrite)

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
3. **The headline figure** (`research/figures/headline_mae.svg`) with a
   one-line caption, then the current README's table and its four caveats,
   carried over. Their numbers and meaning are unchanged; wording may be
   tightened. If the optional figure exists, place it after the caveats
   with its own caption.
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
6. **Status and roadmap.** Rewrite from STATUS and SPEC 6 as of session 98:
   stage A done (F123 to F125, F127, D78.1); stage B pre-registered with
   frozen models and gated scripts, not yet run, scored only after each
   period ends (D73, F122, F128, F129); stage C under way: design (D82,
   D83), pull complete (F137), development table built and gated (F138),
   cross-validation rules fixed (D89), baseline fitted (F139). **Do not
   quote F139's scores.** Then stages D to H in one line each, and the new
   airports track.
7. **Repository layout.** A tree of the new layout with a few words per
   folder (emoji labels are fine here: README ⭐, research 📚, audit 🗃️,
   scripts 🐍, data 💾), each folder linked to its README. One sentence on
   why scripts are named by session number (the record cites them by
   path).
8. **Reproducing.** Carry over the current section, with updated paths and
   the libomp outcome from Step 6. Keep the honest line that the full run
   order is spread across DECISIONS, and add that `scripts/README.md`
   lists the scripts behind each headline result.
9. **How this was built.** Carry over the current paragraph unchanged in
   meaning: the owner planned the work, made every decision, wrote every
   session prompt and reviewed every change; the code was written by Claude
   Code (Anthropic's AI coding tool) one scoped session at a time; every
   change was reviewed and committed by hand. Link to `audit/` for the
   full working record.
10. **Data credits and terms.** Carry over section 8 word for word.
11. **Licence.** Carry over section 9, then a final line: "Author:
    Zachary Adams."

Aim for a README a reviewer can skim in two minutes: sections 2 to 4
should fit on one or two screens.

### 8.2 `research/README.md`

What the folder is (the scientific record). Suggested reading order:
RESULTS.md (the results narrative), SPEC.md (how the project works; the
source of truth), DECISIONS.md (the append-only log; D entries are
decisions, F entries are findings, cited as Dxx and Fxx), `archive/`
(settled entries moved out word for word). Then `figures/` and the script
that draws them.

### 8.3 `audit/README.md`

What the folder is: the working record of how the project was run.
Explain the loop in a few sentences: the owner plans each session in a
planning chat and writes its prompt (`sessions/session-NN.md`); Claude
Code carries out that one session and saves its real output
(`outputs/`); the owner reviews it and commits it by hand with a commit
message saved as `sessions/commit-NN.txt`. Name `STATUS.md` (the current
snapshot) and `PROJECT-INSTRUCTIONS.md` (the planning guide). Note that
some saved outputs contain file paths from the author's machine (F126.2).

Then **"Paths before session 98":** a short table mapping the old
locations to the new ones (`docs/` to `audit/sessions/`, `notes/` to
`audit/outputs/`, and the six root files), a link to
`session98_path_map.csv` for the file-by-file list, and one sentence: the
DECISIONS entries written before session 98 cite the old paths, and are
not edited (D90.6).

### 8.4 `scripts/README.md`

1. How the scripts are named and run: `sessionNN_*.py` was written in
   session NN; its prompt is `audit/sessions/session-NN.md` and its output
   `audit/outputs/`; run with `.venv/bin/python scripts/<name>.py`. Why
   the names are kept (the record cites the scripts by path, and frozen
   scripts check each other's SHA-256).
2. **Frozen scripts**, never edited: list them, from SPEC and DECISIONS
   (at least `session39_sealed_test.py`, `session48_reserved_year.py`,
   `session60_combine_design.py`, `session62_reserved_confirm.py`; add any
   other the record marks frozen, with its entry).
3. **Key scripts, by result.** A table with about 20 to 30 rows: script,
   what it does in one line, and the DECISIONS entry. Group the rows: the
   minimal method (its pull, model and sealed test per airport); the
   richer method (GRIB pull, decode, join, sealed test; F94); the
   selected-features method (the E1 to E5 experiments, the combine sweep,
   the reserved-year build and confirmation; F109); KSFO (F119); stage B
   (the frozen models and the 2026-27 build, competitor fetch and scoring
   scripts); stage C (pull, verify, release check, development table,
   cross-validation); and `session98_figures.py`. Each role must come from
   the script's docstring or the cited entry, not from its name alone.
4. **Everything else**: one line per session range (for example "sessions
   01 to 33: per-airport checks, pulls and models for the minimal method").
5. One sentence: the GitHub Actions workflow
   (`.github/workflows/stagec-grib-pull.yml`) runs
   `session91_grib_pull.py` and `session92_verify_chunk.py`.

### 8.5 `data/README.md`

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

## Step 9: final checks (report each)

1. Every relative link in the five README files resolves to an existing
   path (list links checked and any failures).
2. No U+2014 in any new file, and no U+2014 in any line added to an edited
   file (check the added lines of each diff).
3. `git status --porcelain` and `git diff --stat`: the only changes are the
   moves, the new files, and edits to `CLAUDE.md`,
   `audit/PROJECT-INSTRUCTIONS.md`, `research/SPEC.md`,
   `research/DECISIONS.md` (D90 and F140 appended, plus any archive move),
   `audit/STATUS.md`, `README.md` and `requirements.txt` (comment lines
   only). Nothing under `scripts/` changed except the two new files
   (`README.md`, `session98_figures.py`); nothing under `data/` changed
   except `data/README.md`; `.github/` unchanged.
4. SHA-256 of the files checked in Step 0 item 3, unchanged.
5. No `__pycache__` written.

## Step 10: end of session

1. **F140.** Append F140 to `research/DECISIONS.md`: a finding for each of
   Steps 0 to 9, with real values (counts, SHA-256 values, the gate
   results, the libomp path and versions, which figures were made and
   why), then "Readings made where the prompt is silent" (numbered, for
   the owner to confirm), then "What this did not do". Mark plainly that
   no model experiment was run and no build choice was made.
2. **Overwrite `audit/STATUS.md`** as a current-only snapshot (CLAUDE.md),
   using the new paths throughout. Its last line:
   "**Next planning session:** Review session 98. If it passed, the owner
   commits and pushes, removes the old docs and notes folders from the
   Filesystem extension's allowed folders, and sets the GitHub About box;
   then plan session 99: the first of D82.5's alternatives against the
   baseline, under D89.6. Re-check GFS v17."
3. **Consistency check** (CLAUDE.md): re-read CLAUDE.md, SPEC, STATUS and
   DECISIONS and report anything that disagrees, any duplicated heading,
   any entry out of order, and any live file that still names an old path.
4. **Archive step** (CLAUDE.md), into `research/archive/DECISIONS-archive.md`,
   by the usual criterion, mechanically and verbatim.
5. Write the full real output to `audit/outputs/session-98-output.txt`.
6. Stop and wait for the owner's review. Do not commit, add or push, and do
   not write a commit message.
