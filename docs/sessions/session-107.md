# Session 107: stage C's look on the six claim airports, run once (D100.12)

Recommended model: Opus (a one-shot held-out result and its write-up).

## Read first

- STATUS.md in full.
- SPEC section 2 and SPEC section 9 (stage C, at its lock).
- The live DECISIONS.md in full (this session records a decision and a
  finding). Archived entries only by number when a step names one: D71.6,
  D79.1, D79.2.
- `notes/session-106-output.txt`: its summary (top, at most 30 lines) and
  checkpoints only.
- `scripts/session106_claim_look.py`: its module docstring and argument
  parser only, to learn the `--look` mode's flags and the files it writes.
  Do not read or edit the rest.

CLAUDE.md is loaded automatically; do not read it again.

## What this session is

Stage C is locked (D100). Its claim test is pre-registered on the six claim
airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN), and the look script passed its
gate (F149). This session records the owner's rulings on F149 (D101), runs
the look exactly once, and records the result (F150). It changes no method,
bar, rule, script, table or model. It edits no SPEC or RESULTS text: the
result is folded in at a later session, after the owner's review.

## Scope list (the only files this session may create or edit)

- `DECISIONS.md`, `DECISIONS-archive.md` (Step 1, Step 5, archive step).
- `STATUS.md` (end steps).
- `notes/session-107-output.txt`.
- The files the `--look` mode writes (named `session107_*`, at the paths
  fixed in the script). List each with its SHA-256 in Step 3's checkpoint.
- Only if Step 4 needs it: `scripts/session107_summary.py` and
  `data/processed/session107_summary.csv`.

Nothing else. In particular: no existing script (frozen or not), no table in
`MLwx-stagec/`, nothing in `MLwx-pull*/`, no SPEC, RESULTS, CLAUDE, README
or test file. No network. Nothing installed. Nothing from 2026-27.

## Step 1: record D101

Copy the text between the two marker lines below into DECISIONS.md, at the
bottom, after a `---` separator, with `sed` (the markers themselves are not
copied). Check it byte-equal to this prompt's text with `diff` and `cmp`.
Do this before any other edit and before any data is read. Do not add D101
or F150 to the Live index yet (end steps do that).

Check: byte-equal; em-dashes in D101: 0. Stop if either fails.

<!-- D101-START -->
## 2026-10-11: Session 107 decision: F149 accepted, three rulings, and how the look is run (owner, planning chat)

**D101. Owner decisions, planning chat (after session 106): F149 accepted
with three rulings, and the rules for running stage C's look once (D100.12)
and reporting it.** Written at the start of session 107, before any other
edit and before any claim airport's value from 2024-08-01 onward has been
read. No 2026-27 value has been read or scored. D100 is unchanged.

- **D101.1 F149 accepted,** with all seven F149.6 readings, and these
  rulings:
  (1) The flagless `--look` run (reading 1) refused before reading any
  table and wrote nothing. The deviation is accepted. The look has not been
  run; session 107's run with the flag is its one run.
  (2) The claim airports' elevation constants stay as built, from the
  unrounded `height_diff_m` (reading 2), as D100.3(b) says: EDDM 0.2589,
  KORD 0.0548, CYYZ 0.0441, ZGSZ 0.1476, ZUCK -0.2521, NZWN 0.5881
  (F149.1). They are not recomputed.
  (3) A bar half with no rows (reading 3) counts as not passing: that look
  fails for that output at that airport, and the write-up says "no rows".
  D79.3's "no verdict" rule belongs to stage B (D73) and does not apply
  here. This ruling is made before the look.
  Readings 4 to 7 are accepted as written.
- **D101.2 The look, run once.** Before it: the look script's SHA-256
  equals F149's; each of the twelve claim tables' SHA-256 equals F149.2's;
  no `session107_*` file exists. Then `--look` is run once, with
  `--confirm-look 107`, unchanged. No other mode of the look script is run
  in session 107. What it produces stands: after any held-out value has been
  printed or written, no method, bar, rule, script or table is changed, and
  the look is not run again.
- **D101.3 If the run stops with an error.** Session 107 stops and reports
  what was printed and which files exist. It does not fix, edit or re-run
  anything. Whether and how the look may be run again is the owner's
  decision, in a new DECISIONS entry that says what was seen.
- **D101.4 Reporting (D100.6, D79.1, D79.2).** Per output (the hourly curve
  at leads 3 to 48; the daily maximum), per airport, per look and per bar
  half (raw GFS; persistence): n, the method's MAE, the comparator's MAE,
  the margin as 100 x (1 - MAE(method) / MAE(comparator)) with the
  difference in degrees C beside it, and pass or fail (strictly lower at
  full precision). Then the verdict per airport and output: PASS, SPLIT or
  FAIL. The claim per output: "passes at N of 6 new airports in both
  held-out years". The finding leads, per output, with the smallest of its
  24 margins (6 airports x 2 looks x 2 halves), naming its airport, look and
  half; a failing margin is negative and leads. It states plainly whether
  D100.7's expectation was met. Nothing is averaged across airports.
  D100.8's descriptive figures go to the output file; the finding cites
  them only where they explain a failing or narrowest margin, and calls
  them descriptive. D100.10's caveats are carried in the finding.
- **D101.5 Not in session 107.** No SPEC or RESULTS edit (the result is
  folded in after the owner has reviewed it); no diagnosis or follow-up
  test; nothing per airport; no model saved beyond what the look mode
  already writes; nothing from 2026-27.
- **D101.6 Live index.** Removed (archived, still binding by number): F149
  (accepted here; its constants and table hashes are held in the look
  script, D98.2). Added: D101 and F150. After session 107: D82, D88, D89,
  D93, D98, D100, D101, F150.
- **D101.7 Plan.** Session 107: this entry; the pre-look checks; the look,
  run once; the verdicts and margins; F150. The next step is chosen at
  session 108's planning.
<!-- D101-END -->

Checkpoint: Step 1, D101 recorded, DECISIONS.md changed, check result.

## Step 2: pre-look checks (no held-out value is read)

1. SHA-256 of `scripts/session106_claim_look.py` equals
   `5e046acffc6eb28619d1883c8b93b6ff97bc3305addade56be5ab30af169281a`
   (F149).
2. SHA-256 of each of the twelve claim tables in `MLwx-stagec/` equals the
   value in F149.2 (two per airport: hours 0 to 24, then 25 to 48). Hashing
   reads bytes only; do not open the tables otherwise.
3. No file named `session107_*` exists in the repository or in
   `MLwx-stagec/`.
4. `git status --porcelain` shows only DECISIONS.md,
   `notes/session-107-output.txt` and this prompt
   (`docs/sessions/session-107.md`, untracked) changed (session 106 is
   committed).

Check: all four hold. If any fails, stop before Step 3 and report; do not
run the look.

Checkpoint: Step 2, the four results.

## Step 3: the look, run once (D101.2)

Run `python3 scripts/session106_claim_look.py --look --confirm-look 107`
(adding only flags that the argument parser marks as required for `--look`;
if it needs anything else, stop and report before running). Run it once.
Copy its terminal summary into the output file.

If it stops with an error, follow D101.3: stop, report, change nothing.

Check: it finished without error; every file it wrote is named
`session107_*`.

Checkpoint: Step 3, finished or not, the files written with their SHA-256,
the run's wall time.

## Step 4: verdicts and margins (D101.4)

From the look's output files only (never the tables, never a refit),
assemble D101.4's table for both outputs: 48 rows (2 outputs x 6 airports x
2 looks x 2 halves), the 12 verdicts, N of 6 per output, and the smallest
margin per output.

If the look's files already hold every number needed, compute the margins
and the smallest margin by a short inline calculation and show it. If they
do not, write `scripts/session107_summary.py`, which reads only the look's
`session107_*` files and writes `data/processed/session107_summary.csv`.

Checks:
- Each half's pass or fail, computed here from the MAEs, equals the look
  script's own pass or fail where it prints one. Any disagreement is
  reported as a reading; nothing is changed to resolve it.
- Each verdict follows D100.6 from its two looks.
- A bar half with no rows is shown as "no rows, not passing" (D101.1(3)).

Write the full table and D100.8's descriptive figures (baseline without the
drift correction, mean errors, leads 3 to 24 and 25 to 48, per cycle hour,
rows and days counted and dropped by reason) to the output file.

Checkpoint: Step 4, the check results, files changed.

## Step 5: F150

Record F150 in DECISIONS.md, at most about 40 lines (D93.10), titled
"Session 107 finding: stage C's look on the six claim airports". Contents,
in this order:

1. Per output, the lead line: the claim ("passes at N of 6 new airports in
   both held-out years") and the smallest margin as a percentage with its
   degrees C difference, airport, look and half.
2. Whether D100.7's expectation was met, in one sentence.
3. Per output, a compact table: airport, verdict, and the four margins
   (look A raw GFS, look A persistence, look B raw GFS, look B
   persistence), percent to 2 decimals.
4. Script and output files with SHA-256; Python and package versions; run
   date.
5. D100.10's caveats, in one or two sentences.
6. Readings for the owner (anything unexpected, any disagreement from Step
   4, any "no rows").
7. What this did not do (D101.5).
8. A pointer to `notes/session-107-output.txt`.

Framing: lead with the numbers, not adjectives. No average across airports.
Do not explain a failure beyond citing descriptive figures already computed.

Checkpoint: Step 5, F150 recorded, line count.

## End-of-session steps (CLAUDE.md)

1. Real output: the numbers in the output file, not descriptions.
2. Overwrite STATUS.md as a current-only snapshot. Its last line is:
   "**Next planning session:** Review session 107. The owner commits and
   pushes (`git commit -F docs/commits/commit-107.txt`) and the planning
   chat syncs Project knowledge. Then plan session 108: the owner's ruling
   on F150 and folding stage C's result into SPEC 9 and RESULTS 7."
3. Archive step: add D101 and F150 to the Live index and remove F149
   (D101.6); then `python3 scripts/archive_decisions.py --apply --session
   107`.
4. Checks: `python3 scripts/archive_decisions.py --citations`; re-read only
   what this session changed in STATUS and DECISIONS and report anything
   that disagrees with the rest of the record; report DECISIONS.md's byte
   size (above 80,000 is a finding, D93.9); run the scope-list check
   against `git status --porcelain`.
5. Output file: `notes/session-107-output.txt` begins with a summary of at
   most 30 lines, then the checkpoints, then the full tables. The
   consistency-check findings are written into it, not only reported in
   chat.

Then stop and wait for review. Do not commit, add or push. Do not write a
commit message.
