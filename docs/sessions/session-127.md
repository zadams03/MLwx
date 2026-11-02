# Session 127: the reader-facing documents rewritten in plain language, with new figures

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
This session rewrites the documents people read (README.md, RESULTS.md
and the four folder READMEs) so that a general reader, an academic or a
recruiter can follow them, and adds clear figures drawn only from
committed result files. The record itself (SPEC, DECISIONS, the archive,
ANALYSIS, notes) keeps its form and stays public as the audit trail.
Nothing is fitted, scored or fetched.

## Read first

- STATUS.md in full; SPEC section 2; the live DECISIONS.md in full.
- SPEC sections 5.0, 6, 7.4, 8.5 and 9.5 (for the numbers).
- Archived entries, one at a time by line range: D59.3 (the caveats any
  write-up of F109 must carry), D71.5 (KSFO's framing), F150 (stage C's
  look), F157.7 and F160.9 (how the comparisons are read), D103.2 and
  D105.6 (no live accuracy figure), D107.3 (what the comparisons spent).
- README.md and RESULTS.md in full (they are being rewritten).
- `ANALYSIS.md`: its opening paragraphs before `## Part 1.`, Part 1, and
  Tables 2a and 2b only, by line range.
- The four folder READMEs (`scripts/`, `data/`, `docs/`, `notes/`) in
  full; they are short.
- `scripts/session108_figures.py` (how an earlier figure script held its
  input SHA-256 values and gated its numbers), read only.

## Rules for this session

- **Two audiences (D121.4).** README.md, RESULTS.md and the four folder
  READMEs are written for people: no D or F numbers, and no "SPEC 8"
  style citations, in their running text. Each ends with a section
  "Where these numbers come from": a table that maps each number or
  claim to the record entry or file that holds it. Those tables are the
  only place a citation appears, apart from the two exceptions below.
- **Exceptions.** (a) README's data credits: the body of the current
  section 9 (from the line after its `## 9.` heading to the line before
  `## 10.`) is kept byte-equal, as the last section but one (F167.4);
  its heading may lose its number. (b) `scripts/README.md`'s per-session
  map and its "Scripts to run only in a clone" section keep their
  content and F numbers: they are an index for auditors.
- **Numbers (D121.6).** Every number is copied from the record or from a
  committed result file, never recomputed in prose. Nothing is averaged
  across airports. Where a result has a range, the smallest margin leads.
  RESULTS keeps D59.3's caveats (a) to (e) wherever F109's result is
  given, and KSFO carries D71.5's framing. The comparisons with other
  forecasts are descriptive, on years already used, and the text says
  plainly where the curve trails (hourly: NBS, the NBM grid and AIFS at
  some airports) as well as where it leads. No accuracy figure of any
  kind is given for the live tool (D103.2, D105.6). The "research
  project, not an operational forecast" warning stays near the top of
  README.
- **Plain language.** Short sentences. Define each term once, the first
  time it is used (GFS, bias, MAE, held-out year, pre-registered, lead).
  Name airports by city and code the first time ("Chicago O'Hare (KORD)").
  Prefer plain names to internal labels (say "the hourly curve" rather
  than "stage C" in README; RESULTS may use stage names once explained).
  Keep the owner's own wording of README's opening where it still fits
  ("repeatedly", "that error").
- **Not edited:** SPEC.md apart from Step 8's one pointer; DECISIONS
  apart from D121, F170 and the archive step; ANALYSIS.md apart from
  Step 8's one pointer (Part 1 to the end stays byte-equal); CLAUDE.md;
  `docs/PROJECT-INSTRUCTIONS.md`; every existing script, test, data
  file, figure, model, `src/`, `deploy/`. No network. No 2026-27 value
  is read or scored. No live log, snapshot or page is read.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md, README.md, RESULTS.md,
scripts/README.md, data/README.md, docs/README.md, notes/README.md,
SPEC.md (Step 8 only), ANALYSIS.md (Step 8 only),
scripts/session127_readme_figures.py (new),
tests/test_session127_figures.py (new),
figures/readme/ (new folder and the SVG files of Step 4),
notes/session-127-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `fbfca79`; the tree is clean apart
from this prompt. Tests (`.venv/bin/python -m unittest discover -s
tests`): 195 OK. SPEC 3.4's span (between its two markers) has SHA-256
`a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
`.venv/bin/python scripts/session122_analysis.py --verify`: PASS.
Record in the output file: the SHA-256 of README section 9's body (as
defined under Rules), of `ANALYSIS.md` from `## Part 1.` to the end, and
of every file under `figures/` (`find figures -type f | sort | xargs
shasum -a 256`). Stop if any check fails.

**Step 2. Record D121.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-02: Session 127 decision: F169 accepted, the order of the longer-term plan, two audiences for the documents, and session 127's scope (owner, planning chat)

**D121. Owner decisions, planning chat (after session 126's commit): F169 accepted; the order of the longer-term plan (D112.2 item 5); rulings on ANALYSIS.md's Part 3 candidates 6 and 7 and on the MOSMIX saver; the reader-facing documents separated from the record; session 127's scope; and Live index changes.** Written at the start of session 127, before any other edit. No 2026-27 value has been read or scored.

- **D121.1 F169 accepted,** with its readings (F169.8).
- **D121.2 The order of the longer-term plan (owner, 2026-11-02).** (1) Session 127: the plain-language rewrite (D121.4, D121.5). (2) The MOSMIX saver (D81.2 to D81.5 stand), in its own session. (3) One session for three small items: Gates C and D in `scripts/session109_gates.py` (F154.9(4)), by a new script under D116.10; rows at the airport's own position (iem set) for AIFS and the NBM grid at the development airports, descriptive; and D115.6's question, with its rows, pairing and statistics fixed in its own entry first. (4) Stage H on GFS, with its build choices on the development airports (D89); whether to pre-register a range test on 2026-27 is decided early, while no 2026-27 value has been scored (SPEC 2.5). (5) Stage D, starting with AIFS, then stage E; whether raw AIFS goes straight into the GFS model as inputs instead of being corrected first is decided when stage D is planned (D72.2(b)). (6) WeatherNext stays deferred (D107.4). A GFS v17 Service Change Notice goes ahead of all of these: one session for the live tool's v17 handling (D103.10) and for preparing stage B's scoring (D73.4, D118.10). Stage B and the live test are scored only when their periods end (D73.8, D105.5).
- **D121.3 ANALYSIS.md's Part 3 candidates 6 and 7 (F157.7).** Candidate 6 (station guidance where it exists) is parked to stage E; any use first needs an owner's ruling on the same-at-every-airport rule (SPEC 2.5). Candidate 7: the daily maximum's target (D82.8) is not changed; an official-figure maximum at US airports may be added later only as a separate, labelled output, by its own entry.
- **D121.4 Two audiences.** README.md, RESULTS.md and the READMEs in `scripts/`, `data/`, `docs/` and `notes/` are written for people: plain language, no D or F numbers or SPEC section citations in their running text, and a closing "Where these numbers come from" table that maps each number or claim to its record entry. Kept as exceptions: README's data credits body, byte-equal (F167.4); `scripts/README.md`'s per-session map and its run-only-in-a-clone section. SPEC, DECISIONS, the archive, ANALYSIS.md and `notes/` are the record and keep their form; STATUS, CLAUDE and `docs/PROJECT-INSTRUCTIONS.md` are working files. The record stays public: its timestamped history is the evidence that each test was fixed before its look.
- **D121.5 Session 127's scope.** The rewrite of D121.4's documents; a new figure script, `scripts/session127_readme_figures.py`, that draws figures into `figures/readme/` from committed result files only, plotting recorded values and recorded margins, averaging nothing across airports, with every plotted value gated against the record; in SPEC, "RESULTS 6.6" becomes "RESULTS.md"; in ANALYSIS.md's opening, "see README section 9" becomes "see README's data credits section". No model, data file, logged value or live file changes, so D105.5(k) is not engaged. No network.
- **D121.6 Content rules for the rewrite.** Every number is copied from the record; nothing is averaged across airports; the smallest margin leads; D59.3's caveats travel with F109's result, and KSFO keeps D71.5's framing; the comparisons are descriptive on spent years and say where the curve trails as well as where it leads (F157.7, F160.9); no accuracy figure is given for the live tool (D103.2, D105.6); the not-operational warning stays.
- **D121.7 Live index.** Removed (archived): D120 and F169, which are settled. Added: D121 and F170 (F170 when it is written). After session 127: D93, D103, D105, D118, D121, F170.
```

**Step 3. Inventory (read only).** Before writing anything, list in the
output file every number and every claim in the current README.md and
RESULTS.md, each with the citation it carries now, one line each. This
is the checklist for Steps 5 and 6 and the source of their "Where these
numbers come from" tables: each item is either carried into the new text
or listed as dropped with a one-line reason (for example, a detail of
the feature-selection process kept only in the record). Check: the
count of items, carried and dropped, is reported.

**Step 4. The figure script and the figures.**
Write `scripts/session127_readme_figures.py`: standard library only (as
`session108_figures.py`), each input file's SHA-256 held as a constant
and checked before it is read, modes `--gate` and `--draw OUTDIR`, and
write-once (it refuses to overwrite an existing figure). Style: one
consistent look across all figures, a colour-blind-safe palette, direct
value labels where they help, no meaning carried by colour alone, plain
titles and axis labels with units, readable at README width (about 800
px) in light and dark GitHub themes (a white or transparent background
with text that works on both; test both by eye if a converter exists).
Each figure gets one-sentence alt text for README.

The figures:
(a) `stagec_gain.svg`. How much lower the error is than raw GFS, in
per cent, at each of the six new airports, both held-out years, for the
hourly curve and the daily maximum. Values: `margin_pct` for the raw GFS
half in `data/processed/session107_claim_verdicts.csv`. Gate: each value
at 2 decimals equals F150 (and SPEC 9.5); the smallest (KORD, second
look) is marked.
(b) `how_it_works.svg`. A diagram, no numbers: GFS forecast for the
airport, then the features read from it, then one model per airport,
cycle hour and lead, then the running correction for drifting bias,
then the corrected hourly curve to 48 hours, with the day's maximum read
off it. Wording as plain as the README's.
(c) `lock_then_look.svg`. A timeline of how each claim was tested: rules
written down, then one look at years the model never saw, then the
verdict; with the dates of the stage C claim (training to 2024-07-31,
looks 2024-25 and 2025-26, models frozen before the look) and the live
forward test (from 2026-10-12, locked, not yet scored). Every date
gated against the record entry that gives it (F150, D100, D105.5).
(d) `compare_hourly.svg` and (e) `compare_dailymax.svg`. The curve
against each other forecast (raw GFS, AIFS, ECMWF IFS, the NBM grid,
NBS, MAV) at each airport where that source exists, on matched rows, as
in ANALYSIS.md Tables 2a and 2b. Show which is lower and by how much in
a form a general reader can read at a glance (for example, a dot plot of
the per cent difference, with "curve better" on one side). Inputs: the
files under `data/processed/session114_comparisons/` that ANALYSIS
renders those tables from (find them in `scripts/session122_analysis.py`;
read, never run beyond `--verify`). Gate: every plotted pair, rounded as
in the tables, equals Table 2a's and 2b's cells. If no committed file
gives a cell exactly, stop and report; do not compute a substitute. The
caption notes that AIFS and the NBM grid were read at GFS's grid point
at the development airports, and that AIFS's and IFS's daily maxima
come from their coarser time steps.

Checks: `--gate` PASS for every figure; `--draw` into two `mktemp -d`
folders gives byte-equal files; then `--draw figures/readme`; a second
run there is refused. If a converter (`rsvg-convert`, or `cairosvg`
already in the venv) exists, render each figure to a temporary PNG and
look at it; nothing is installed for this. Add
`tests/test_session127_figures.py`: each input constant equals the file's
SHA-256, and `--gate` passes. Record the script's and each figure's
SHA-256.

**Step 5. README.md, rewritten.** Suggested shape, in this order (adjust
if something reads better, and say what changed):
1. Title, one plain sentence on what this is, the live page link
   (https://zadams03.github.io/MLwx-live/), and figure (a).
2. The idea in plain words: a big weather model makes the same local
   error repeatedly; the project learns that error at each airport and
   removes it.
3. Headline results: the hourly curve and daily maximum at six new
   airports, smallest margin first, then the range; one sentence on the
   earlier one-hour-a-day results (the range, pointing to RESULTS).
4. How it works, with figure (b).
5. How the results were kept honest, with figure (c): rules fixed in
   writing first, one look at unseen years, new airports drawn by a
   fixed random rule, a live forward test locked before any of it is
   scored, and the public, timestamped record (link SPEC.md and
   DECISIONS.md here, for anyone who wants to audit it).
6. How it compares with other forecasts, with figure (d): honest both
   ways, descriptive.
7. The live tool: what it shows, 49 airports, how often it runs, the
   write-once log, and that no accuracy figure is shown until its
   pre-registered test.
8. Limitations, short.
9. What comes next, in plain words (D121.2, without the numbers).
10. Repository map; Reproducing; How this was built (keep the
    content of the current sections 6, 7 and 8, in plain words).
11. Where these numbers come from (the table).
12. Data credits and terms (body byte-equal); Licence (its last sentence
    points to "the data credits section" instead of "section 9").
Aim for a README a reader can take in within a few minutes; detail goes
to RESULTS.

**Step 6. RESULTS.md, rewritten.** The full plain story, for a reader
who wants the detail: what the project is and how a result is judged;
the three methods at the first airports (the minimal method and Reno,
the richer features, the selected features with F109's caveats and the
intervals, KSFO with its framing); the hourly curve and daily maximum
(the claim, its margins, and what the drift correction adds); the
comparisons with other forecasts (the one-hour NBM and MOS comparison
and the full-curve comparisons; figures (d) and (e)); what the
descriptive analysis found, in plain words, with the candidates for
later in one short list; the live tool and the two tests still to come;
limitations; what comes next; and Where these numbers come from. Reuse
existing figures where they are clear (`figures/headline_mae.svg`,
`figures/skill_intervals.svg`, `figures/stagec_mae_by_lead.svg`, and any
of `figures/analysis/` that a general reader can follow). Every item of
Step 3's RESULTS inventory is carried or listed as dropped.

**Step 7. The folder READMEs.** `scripts/README.md`: a plain opening
paragraph (what is here, which scripts matter to a reader, which are
frozen and why), then its existing map and its run-only-in-a-clone
section unchanged in content. `data/README.md`, `docs/README.md`,
`notes/README.md`: plain wording, inline citations moved to a short
closing sources table where any remain. No fact is dropped from these
four files.

**Step 8. Two pointers.** SPEC.md: in the sentence `done (DECISIONS
F125; RESULTS 6.6).` replace `RESULTS 6.6` with `RESULTS.md`; nothing
else in SPEC. ANALYSIS.md: in its opening, replace `see README
section 9.` with `see README's data credits section.` (rewrap only that
paragraph).

**Step 9. Final checks.**
- README's credits body SHA-256 equals Step 1's.
- `ANALYSIS.md` from `## Part 1.` to the end: SHA-256 equals Step 1's;
  `session122_analysis.py --verify` PASS.
- `git diff SPEC.md` is that one line only; 3.4's span hash unchanged.
- Every file under `figures/` that existed at Step 1 has its Step 1
  SHA-256.
- Running text of README.md, RESULTS.md, `data/README.md`,
  `docs/README.md` and `notes/README.md` holds no D or F number and no
  SPEC section citation outside its sources table (and README's credits
  body): show the grep and its count.
- Every relative link and image path in the six files resolves.
- Each row of each sources table: the number or claim is found in the
  cited entry or file (grep), listed PASS or FAIL in the output file.
- `python3 scripts/archive_decisions.py --citations`: every citation
  resolves.
- 0 em-dashes in added lines (`git diff -U0 | grep '^+' | grep -cP
  '\x{2014}'` gives 0; new files checked directly).
- Tests: 195 plus the new ones, all OK.
- Line counts of README.md and RESULTS.md before and after.

## End of session (CLAUDE.md)

1. **F170**, at most about 40 lines: what changed per file, the figures
   with their SHA-256 and gates, the script's SHA-256, Step 3's counts
   (carried and dropped), every check with PASS or FAIL, readings for
   the owner, what was not done, pointer to `notes/session-127-output.txt`.
2. **Overwrite STATUS.md** as a current snapshot: the documents now have
   two audiences (D121.4); the longer-term order (D121.2) and the
   rulings of D121.3 replace the open question on the longer-term plan;
   keep the other live items. End with: `**Next planning session:**
   Review session 127 and commit; the planning chat syncs Project
   knowledge (D118.8); then plan the MOSMIX saver (D121.2 item 2).`
3. **Archive step:** make D121.7's index changes, add F170, then
   `python3 scripts/archive_decisions.py --apply --session 127`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a summary of at most 30 lines; report the
   same summary in chat. Then stop and wait for review. Do not commit.
