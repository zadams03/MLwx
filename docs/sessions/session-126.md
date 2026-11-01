# Session 126: health check fix group (6), the README update (last)

Plain words, no em-dashes in any new text (CLAUDE.md). This session edits
documentation only. It ends the project health check.

## Read first

- STATUS.md in full; SPEC section 2.
- Live DECISIONS.md: D118 (D118.5 only), D119 (D119.2, D119.4), F168.
- `notes/session-121-register.csv`: rows RM01, RM02, RM03, RM04, RM07,
  RM09, RM10, RM11 only (by `grep -E '^(RM0[1-9]|RM1[01]),'`).
  `notes/session-120-register.csv`: row C11 only.
- Nothing else in full. Read only the lines of each README a step names.

## Rules for this session

- No script, test, data file, figure, model or SPEC edit. No network.
  No 2026-27 value is read or scored.
- README section 9 (data credits, from `## 9.` to the line before
  `## 10.`) is not edited (F167.4).
- In `ANALYSIS.md`, only the one new paragraph of Step 6. Part 1, Part 2
  and every table stay byte-equal.
- Keep line lengths like the surrounding text. Rewrap only a paragraph
  you change.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md, README.md,
scripts/README.md, data/README.md, docs/README.md, notes/README.md,
ANALYSIS.md, notes/session-126-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `c326483`; the tree is clean apart
from this prompt. Run the tests (`.venv/bin/python -m unittest discover
-s tests`): 195 OK. SPEC 3.4's span (between its two markers) has
SHA-256 `a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
Record the SHA-256 of README section 9's span and of `ANALYSIS.md` from
`## Part 1.` to the end. Run `.venv/bin/python
scripts/session122_analysis.py --verify`: PASS. Stop if any check fails.

**Step 2. Record D120.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0 em-dashes.

```
---

## 2026-11-01: Session 126 decision: F168 accepted, fix group 6 (the README update), and the end of the health check (owner, planning chat)

**D120. Owner decisions, planning chat (after session 125's commit): F168 accepted; session 126 runs fix group (6), the README update, which ends the project health check; and Live index changes.** Written at the start of session 126, before any other edit. No 2026-27 value has been read or scored.

- **D120.1 F168 accepted,** with its readings (F168.6). (4) is done in this session; (2) and (3) are carried in STATUS.
- **D120.2 Session 126's scope.** D119.4's items, plus F168.6(4): a note in `scripts/README.md` that session 76b's two checks are write-once, so a rerun uses a clone with their four outputs moved aside and compares by `cmp` (D119.2). README line 19 reads "This is a research project with a public live tool." README section 9 is not edited (F167.4). No script, test, data file, figure or SPEC is edited, and no network is used. No logged value, model or live file changes, so D105.5(k) is not engaged.
- **D120.3 The health check ends with this session (D114.3, D115.7).** The next planning step is the longer-term plan (D112.2 item 5).
- **D120.4 Live index.** Removed (archived): D114, D115, D119, F163, F164 and F168, which are settled (D115.6's candidate and F168.6's readings are carried in STATUS and `scripts/README.md`). Added: D120 and F169 (F169 when it is written). After session 126: D93, D103, D105, D118, D120, F169.
```

**Step 3. README.md, sections 1 and 5 (RM01, RM02).**
(a) In section 1, replace the sentence `Stage G, the live tool, is next
(D102.4).` with:
`Stage G, the live tool, is running at 49 airports (D103, D105.2):
https://zadams03.github.io/MLwx-live/.`
(b) Replace `This is a research project and a private tool.` with
`This is a research project with a public live tool.` The next sentence
stays.
(c) In section 5, replace the whole `**G. Live product, version 1:
next**` bullet with:

```
- **G. Live product, version 1: live** (D103, D105.2). For every GFS
  cycle, a corrected hourly curve at leads 3 to 48 and each local day's
  maximum, on GFS only, with the weather model as a setting. It runs at
  49 airports in the public repository
  [zadams03/MLwx-live](https://github.com/zadams03/MLwx-live), with a page
  at https://zadams03.github.io/MLwx-live/. Each forecast is written once
  to a log that is never edited (D103.8). The forecasts are under a
  pre-registered test (D105.5); no accuracy figure is computed or shown
  before its look (D103.2, D105.6).
```
Check: `grep -n 'private\|is next\|: next' README.md` finds none of the
old wording in sections 1 and 5.

**Step 4. README.md, section 6's map (RM03, RM04).** In the table:
(a) The `figures/` row's text becomes: `The figures in this file, drawn
by scripts/session98b_figures.py and scripts/session108_figures.py (in
backticks, as now). figures/analysis/ holds the figures of ANALYSIS.md.`
(b) The DECISIONS.md row's text becomes: `The live log of decisions (D)
and findings (F); settled entries move to the archive (D93.8).`
(c) After the STATUS.md row, add: `| | [ANALYSIS.md](ANALYSIS.md) |
Descriptive analysis on spent data: a field guide, comparisons with other
forecasts and ideas for later. Never a source of rules or claims
(D107.2). |`
(d) After the `scripts/` row, add two rows: `| | [src/mlwx/](src/mlwx/)
| The live tool's code, a Python package (stage G, D103.3). |` and `| |
[deploy/mlwx-live/](deploy/mlwx-live/) | The template for the MLwx-live
repository's files and workflow (D105.9). |`
Check: every path in the map exists; the table still has one header row
and consistent columns.

**Step 5. scripts/README.md (RM07, C11, F168.6(4)).**
(a) Add a section `## Scripts to run only in a clone` just before
`## Frozen scripts: never edited`, with two bullets:
- `session63_join_equivalence_check.py` and
  `session63_wiring_scratch_check.py` rewrite their committed output
  files in `../notes/` each time they run. Run them only in a temporary
  clone; the committed notes files are not edited (C11, D116.9). Name
  those output files in the bullet: find them by reading the two
  scripts' write paths, and check each exists in `notes/`.
- `session76b_check_a.py` and `session76b_check_b.py` are write-once:
  each stops if its two output files in `../data/rebuild/session76b/`
  already exist. To run them again, use a temporary clone, move those
  four committed files aside, run the checks, and compare each new file
  with its committed copy by `cmp` (D119.2, F168.5).
(b) In `## Everything else`, after the `Sessions 91 to 98b` bullet, add:
- **Sessions 100 to 106:** stage C's build choices by cross-validation
  (the model structure, the drift tracker, the curve and the daily
  maximum), the table for forecast hours 25 to 48, and the claim
  airports' tables and look (F150).
- **Session 108:** the stage C figures in the root README and RESULTS.md.
- **Session 109:** gates that check the live tool's code
  (`../src/mlwx/`) against stage C's tables and scores (D103).
- **Sessions 112 to 119:** the descriptive analysis in `../ANALYSIS.md`
  and its comparisons with other forecasts (F155, F157, F160, F162), the
  comparison pull (session 113), the observation checks (F158, F159) and
  an audit of the live runs (session 118, F161).
- **Sessions 120 to 123:** the project health check: two audits (F163,
  F164) and fixes (F165, F166).
- `../src/mlwx/`: the live tool's package (D103.3). It also holds the
  airport onboarding and refit of sessions 110 and 111.
(c) After the sentence on `stagec-grib-pull.yml`, add: `The live tool's
workflow template is ../deploy/mlwx-live/.github/workflows/live.yml (in
backticks); it runs in zadams03/MLwx-live, not here (D105.9).`
Checks: every script `session1[0-2][0-9]_*.py` in `scripts/` falls in one
of the new groups; every path named exists. Every F number cited in (b)
is checked: its heading in DECISIONS.md or DECISIONS-archive.md (found
with `grep -n '^\*\*F155\. '` and so on) names that session. If a number
is wrong, use the one the record gives and report it.

**Step 6. The other READMEs and ANALYSIS.md (RM09, RM10, RM11,
F167.8(2)).**
(a) `data/README.md`, end of the `## processed/` paragraph, add: `Folders
named by session hold one piece of work's outputs: for example
session112_analysis/ and session114_comparisons/ (ANALYSIS.md),
session113/ (the comparison forecasts and official maxima on spent
years, credited in the root README's section 9), and session120_audit/
and session121_audit/ (the health check).` (folder names in backticks;
check each exists).
(b) `docs/README.md`, replace the last line `These files are part of the
record and are not edited after the fact.` with: `The session prompts,
the commit messages and the handover note are part of the record and are
not edited after the fact. PROJECT-INSTRUCTIONS.md is a live guide; a
session edits it only when its prompt says exactly what to change.`
(c) `notes/README.md`, after the `Audit reports` bullet, add: `- **Health
check registers:** session-120-register.csv and session-121-register.csv
(in backticks), one row per item checked by the project health check's
two audits (D114.7).`
(d) `ANALYSIS.md`: after its first paragraph (ending `from the owner's
pull (D108.2).`), add one blank line and this paragraph:
`ECMWF IFS and AIFS values are based on data and products of the European
Centre for Medium-Range Weather Forecasts (ECMWF). Copyright © 2023-2026
ECMWF, published under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/); source www.ecmwf.int.
Only the values at each airport's grid points are kept; see README
section 9.`
Checks: `session122_analysis.py --verify` PASS again; the SHA-256 of
`ANALYSIS.md` from `## Part 1.` to the end equals Step 1's.

**Step 7. Final checks.** README section 9's span SHA-256 equals Step 1's.
SPEC.md unchanged (`git diff --quiet SPEC.md`) and 3.4's span hash
unchanged. No file under `figures/`, `scripts/*.py`, `src/`, `tests/`,
`data/` (except `data/README.md`) or `deploy/` changed. 0 em-dashes in
the added lines (`git diff -U0 | grep '^+' | grep -cP '\x{2014}'` gives 0). Tests:
195 OK. Show the changed lines with `git diff --stat` and write the full
diff of the README files and ANALYSIS.md into the output file.

## End of session (CLAUDE.md)

1. **F169**, at most about 40 lines: what changed per file, every check
   with PASS or FAIL, any F number corrected in Step 5, what was not done,
   pointer to `notes/session-126-output.txt`.
2. **Overwrite STATUS.md** as a current snapshot. The health check is done
   (all fix groups). Drop the open question on fix group (6) and the
   session 76b reading (now in `scripts/README.md`); keep the rest. End
   with: `**Next planning session:** Review session 126 and commit; the
   planning chat syncs Project knowledge (D118.8); then plan the
   longer-term plan (D112.2 item 5), whose items STATUS lists.`
3. **Archive step:** make D120.4's index changes, add F169, then
   `python3 scripts/archive_decisions.py --apply --session 126`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a summary of at most 30 lines; report the
   same summary in chat. Then stop and wait for review. Do not commit.
