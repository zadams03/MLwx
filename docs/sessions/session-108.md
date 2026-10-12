# Session 108: stage C's result folded in, README and figures, a smaller live log (D102)

Suggested model in Claude Code: Sonnet (doc edits and one plotting script).
Follow CLAUDE.md's guardrails: a checkpoint line after each step; stop rather
than work around a failed check; after any compaction, re-read CLAUDE.md,
this prompt and your checkpoints.

## Purpose

Record D102 (F150 accepted, its framing, the GRIB cache move, stage G
brought forward, a smaller Live index). Fold stage C's result into SPEC 9,
SPEC 6 and RESULTS 7. Draw two descriptive figures from session 107's
committed files and bring README.md and data/README.md up to date. Record
F151. Nothing is refit or re-scored; no claim airport table, no
`MLwx-*` folder and no 2026-27 value is read. No network.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2, section 6 (from "**The roadmap
  after stage 2" to the end of the stage G bullet) and section 9.
- `DECISIONS.md` (live) in full.
- `notes/session-107-output.txt`: the summary (first 35 lines) and the
  paragraph starting "Descriptive only (D100.8" (find it with `grep -n`).
- `README.md` and `data/README.md` in full.
- `RESULTS.md`: only the roadmap bullet of section 7 and the closing
  footer (find with `grep -n 'The roadmap'` and `grep -n 'revised after'`).
- `scripts/session98b_figures.py` (the style to copy) and
  `scripts/README.md`.

## Files this session may create or edit (scope list)

- New: `scripts/session108_figures.py`, `figures/stagec_headline.svg`,
  `figures/stagec_mae_by_lead.svg`, `notes/session-108-output.txt`.
- Edited: `DECISIONS.md`, `DECISIONS-archive.md` (archive script only),
  `SPEC.md` and `RESULTS.md` (Step 3 only), `README.md`, `data/README.md`,
  `scripts/README.md` (one line for the new script), `tests/test_stagec.py`
  (one new case; existing cases unchanged), `STATUS.md`.
- Untracked already: `docs/sessions/session-108.md` (this file; do not edit).

Any other changed or new file is a scope breach: report it. No existing
script, data file or figure is edited; frozen scripts never. CLAUDE.md and
`docs/PROJECT-INSTRUCTIONS.md` are not edited. Do not access
`/Volumes/` or any external drive.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-108.md`.
- The last entries in DECISIONS.md are D101 and F150; no D102 or F151 in
  either file. None of the new files in the scope list exists.
- SHA-256 of `data/processed/session107_claim_scores.csv`,
  `session107_claim_days.csv` and `session107_claim_verdicts.csv` equal to
  F150.4. Full values.
- `data/raw/grib/`: report whether it exists and, if so, its file count
  (expected: absent or empty, D102.3). Report only.
- Tests: all pass; report the count.
- Stop if any of this differs, except the `data/raw/grib/` report.

## Step 1: record D102

Copy the block between `<<<D102-START>>>` and `<<<D102-END>>>` (markers
excluded) to the end of DECISIONS.md with `sed`, after a line `---` and a
blank line. Check byte equality with `diff` and `cmp`. Em-dashes: 0. Do not
change the Live index yet (end step 3 does it).

<<<D102-START>>>
## 2026-10-12: Session 108 decision: F150 accepted, its framing, the GRIB cache, stage G next, and a smaller live log (owner, planning chat)

**D102. Owner decisions, planning chat (after session 107): F150 accepted
with its readings, how stage C's result is described, the GRIB cache's new
place, stage G brought forward, and a smaller Live index.** Written at the
start of session 108, before any other edit. No 2026-27 value has been read
or scored. Nothing in D100 or F150 changes, and nothing is refit or
re-scored.

- **D102.1 F150 accepted,** with its three F150.6 readings as written.
- **D102.2 How the result is described (descriptive, D100.8; not a new
  test).** The frozen curve passes at 6 of 6 new airports in both held-out
  years for both outputs, and almost all of the gain over raw GFS comes
  from the baseline. In session 107's output file, the curve's MAE was
  above the baseline's (no drift correction) in 6 of 12 hourly and 5 of 12
  daily airport-look cells. So the drift correction helps when GFS's bias
  shifts and is roughly neutral otherwise. The one clear exception is KORD
  look B, hourly: the baseline's mean error was -0.41 degrees C and the
  curve's -0.05, and the correction gave about a third of the gain over
  raw GFS (MAE: raw GFS 1.3307, baseline 1.2566, curve 1.2214).
- **D102.3 The GRIB cache has moved.** The gitignored cache
  `data/raw/grib/` (about 39 GB, 62,572 files, D47) was moved by the owner
  off the laptop to an external drive, at
  `/Volumes/MY PASSPORT/MLwx-grib-cache/`. No current or stage B script
  reads it. Only finished scripts from sessions 37 to 89 do, so those
  cannot be re-run without the drive. Its manifests stay committed. The
  README's size of "about 20 GB" is corrected.
- **D102.4 Stage G comes next (changes D72.3's order only).** After stage
  C, the next stage is G, live product version 1, on GFS only, built with
  the weather model as a setting (as stage C was) so that later models plug
  in without a rebuild. Its design, including how it handles GFS v17, is
  set in a planning conversation and recorded in its own DECISIONS entry
  before any build. Stages D, E, F and H keep their scope and follow it,
  in that order; stage F still covers every model's version changes.
  Reasons: stage C's method has passed its claim; a never-edited
  prediction log gives forward evidence from now on; the ECMWF archives
  are shallow (F123) and deepen while we wait; GFS v17's earliest go-live
  is about November 2026.
- **D102.5 Unchanged.** Stage B (D73, its hold rule and scripts); the
  rule that no 2026-27 value is scored before its test is pre-registered;
  D72.4's 2027-28 forward year as the place for the live product's claim.
  Stage G makes no claim until one is pre-registered.
- **D102.6 README and figures.** Session 108 brings README.md and
  data/README.md up to date with stage C's result and the order in
  D102.4, and draws two descriptive figures from session 107's committed
  files: per-airport MAE of raw GFS and the curve in each look, for both
  outputs; and MAE by lead per airport. Nothing is averaged across
  airports.
- **D102.7 A smaller live file.** To cut what each session reads, the
  Live index after session 108 is D93, D102 and F151. Archived (still
  binding, cited by number): D82, D88, D89 and D98 (stage C's design,
  restated in SPEC 9 where it matters), D100, D101 and F150 (folded into
  SPEC 9 and RESULTS 7). From now on the index holds only D93, the newest
  session's own entries, and any entry a running stage needs open; a
  session's Read first section names other entries by number.
- **D102.8 SPEC and RESULTS.** Session 108 updates SPEC 6 and 9 and
  RESULTS 7 with the text in its prompt.
- **D102.9 Plan.** Session 108: this entry; SPEC and RESULTS; the figures;
  the README files; a read-only list of which scripts open SPEC.md or
  DECISIONS.md (to show whether SPEC can be shortened safely later); F151.
  Next: stage G's design, in the next planning conversation.
<<<D102-END>>>

## Step 2: the figures (`scripts/session108_figures.py`)

Copy session 98b's approach: Python standard library only, offline, SVG
written by hand, each input's SHA-256 checked before reading (held as
constants, each with a comment naming F150.4, D98.2), new files only
(refuse to overwrite), print every value drawn, bytecode off. Same look as
`figures/headline_mae.svg` (colours, fonts, sizes) so the README is
consistent. No date or random value in the SVG: two runs must give
byte-equal files (check with a run into a `mktemp -d` folder, then delete
it).

Inputs: `session107_claim_verdicts.csv` and `session107_claim_scores.csv`
only. Inspect their headers first and report the columns used.

- **`figures/stagec_headline.svg`**: two panels, "Hourly curve, leads 3 to
  48" and "Daily maximum". For each claim airport (order EDDM, KORD, CYYZ,
  ZGSZ, ZUCK, NZWN), grouped bars: raw GFS and the curve, look A and look
  B. Values: the raw GFS half of the verdicts file (the curve's MAE and raw
  GFS's MAE on the same rows). Check each value against F150's margins:
  100 x (1 - curve / raw) at 2 decimals equals F150.2's raw GFS columns.
  Caption line inside the SVG: "Stage C claim, six new airports, MAE in
  degrees C (F150). Lower is better."
- **`figures/stagec_mae_by_lead.svg`**: six small panels, one per airport.
  x: lead 3 to 48; y: MAE in degrees C. Lines: raw GFS and the curve, look
  A solid and look B dashed. Per lead, pool over the four cycle hours from
  the scores file's per-cell n and MAE: sum(n x MAE) / sum(n). Gate: pooling
  over all cycle hours and leads reproduces, for each airport and look, the
  hourly raw GFS half's n exactly and both MAEs within 1e-9 (from the
  verdicts file); stop if not. Caption: "MAE by forecast hour, per airport,
  pooled over the four GFS runs a day. Descriptive (D100.8)."

Add one line for the script to `scripts/README.md`, in its existing format.
Add one test to `tests/test_stagec.py`: the script's three SHA-256
constants equal those in F150.4, found in either DECISIONS file (D98.2).

## Step 3: SPEC and RESULTS (D102.8)

Each old text must be found exactly once; otherwise stop. Put the `git
diff`s in the output file.

In `SPEC.md`:

(a) Section 6, the sentence `Stages run in this order.` (exactly once)
becomes `Stages run in this order, except that stage G now comes straight
after stage C (DECISIONS D102.4).`

(b) Section 6's stage C bullet, the three lines

```
  F148). Stage C is locked, and its claim is pre-registered on the six
  new airports drawn by the rule in DECISIONS D82.7 (DECISIONS D100);
  its design is section 9.
```

become

```
  F148). Stage C is locked (DECISIONS D100), and its claim passed: both
  outputs pass at 6 of 6 new airports, drawn by the rule in DECISIONS
  D82.7, in both held-out years (DECISIONS F150, D102). Its design and
  result are section 9.
```

(c) The stage G bullet, the three lines

```
- **Stage G — live product, version 1.** A daily pipeline, a
  prediction log that is never edited, a simple display, and
  one-script airport onboarding.
```

become

```
- **Stage G — live product, version 1.** A daily pipeline, a
  prediction log that is never edited, a simple display, and
  one-script airport onboarding. It comes straight after stage C, on
  GFS only, with the weather model as a setting; its design includes
  how it handles GFS v17. Stages D, E, F and H follow it, with their
  scope unchanged (DECISIONS D102.4).
```

(d) Section 9.5, the two lines

```
across airports. Expected: both outputs pass at all six. The result will be
recorded here and in RESULTS.md once the look is run.
```

become

```
across airports. Expected: both outputs pass at all six.

**Result (DECISIONS F150, D102).** The look was run once, in session 107.
Both outputs pass at 6 of 6 new airports in both held-out years, as
expected. The smallest margin is at KORD, look B, against raw GFS: +8.216
percent (+0.1093 degrees C) for the hourly curve and +2.589 percent
(+0.0297 degrees C) for the daily maximum. Almost all of the gain over raw
GFS comes from the baseline. Described only (DECISIONS D100.8, not part of
the bar): the curve's MAE was above the baseline's in 6 of 12 hourly and 5
of 12 daily airport-look cells, so the drift correction helps when GFS's
bias shifts and is roughly neutral otherwise. The clear exception is KORD
look B, hourly, where the baseline's mean error was -0.41 degrees C and
the curve's -0.05, and the correction gave about a third of the gain
(MAE: raw GFS 1.3307, baseline 1.2566, curve 1.2214).
```

In `RESULTS.md`, section 7's roadmap bullet:

(e) the two lines

```
  after each of its periods ends (DECISIONS D73, D77.6, D79). Stage C is
  open: it widens the target from one hour a day to an hourly curve from
```

become

```
  after each of its periods ends (DECISIONS D73, D77.6, D79). Stage C is
  done: it widens the target from one hour a day to an hourly curve from
```

(f) the six lines

```
  adopted (DECISIONS D99, F148). Stage C is now locked: its claim test on
  six new airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN) is pre-registered,
  before any of their held-out data was read (DECISIONS D100, SPEC 9).
  Stages D
  to H (other weather models, blending, upgrade policy, the live tool and
  probabilistic ranges) follow; pooling is conditional.
```

become

```
  adopted (DECISIONS D99, F148). Stage C was locked and its claim
  pre-registered on six new airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK,
  NZWN) before any of their held-out data was read (DECISIONS D100). The
  look was run once: both the hourly curve and the daily maximum pass at
  6 of 6 new airports in both held-out years. The smallest margins are at
  KORD, look B, against raw GFS: +8.2 percent hourly and +2.6 percent for
  the daily maximum (DECISIONS F150, SPEC 9.5). Almost all of the gain
  over raw GFS comes from the baseline; the drift correction helps when
  GFS's bias shifts (KORD look B) and is roughly neutral otherwise
  (DECISIONS D102.2, descriptive). Stage G, the live tool on GFS, comes
  next; stages D, E, F and H (other weather models, blending, upgrade
  policy and probabilistic ranges) follow it (DECISIONS D102.4); pooling
  is conditional.
```

(g) In the footer, `and after session 106 (DECISIONS D100).` becomes `and
after session 106 (DECISIONS D100) and after session 108 (DECISIONS
D102).` (on one line, as the original).

Nothing else in either file changes.

## Step 4: README.md and data/README.md (D102.6)

Plain words, short sentences, no em-dashes in new text. Every number
copied from F150, SPEC 9.5 or D102 and cited by entry. Nothing averaged
across airports. Keep each section about its current length or shorter.

README.md:
- **Section 1:** the last two sentences (stage C "under way") become two
  or three sentences: stage C's corrected hourly curve and daily maximum,
  from every GFS run out to 48 hours, passed its pre-registered test at 6
  of 6 new airports in both held-out years (F150); stage G, the live tool,
  is next (D102.4).
- **Section 2:** retitle "Headline results". Lead with a short stage C
  subsection: `figures/stagec_headline.svg` with an alt text and an
  italic one-line caption, then two to four sentences: what was tested
  (SPEC 9.5), the claim per output, the smallest margins (KORD look B),
  and D102.2's framing in one sentence. Then `figures/stagec_mae_by_lead.svg`
  with its caption. Then the existing F109 content as a second subsection,
  unchanged except its heading. Add D100.10's caveats as one bullet.
- **Section 4:** one short paragraph after "Target": stage C forecasts
  every whole hour from 3 to 48 hours ahead from each GFS run, one model
  per airport, run hour and lead, plus a running correction for drifting
  bias, with the daily maximum read off the curve (SPEC 9.1, 9.3).
- **Section 5:** stage C becomes "done" with one or two sentences (D100,
  F150). The list shows stage G next (D102.4), then D, E, F, H. The "New
  airports" bullet says the six claim airports passed.
- **Section 7:** the GRIB cache bullet: about 39 GB, moved off the laptop
  to an external drive; only finished scripts from sessions 37 to 89 read
  it, so they need the drive to re-run; the manifests stay committed
  (D102.3). Do not print the drive's path in the README.

data/README.md: the `grib` line as in section 7 above (D102.3). In "Stage
C's data, outside the repo", add `MLwx-pull-f025-048/` (forecast hours 25
to 48, D98, F147) and the claim airports' tables in `MLwx-stagec/` (F149),
each in one line, in the existing style, citing entries only (look up any
detail you need in the archive by number; do not list file hashes).

Put both files' `git diff`s in the output file.

## Step 5: which scripts read the record files (read only)

List every file under `scripts/` and `tests/` that opens `SPEC.md` or
`DECISIONS.md` / `DECISIONS-archive.md` by path (for example `grep -ln
'SPEC.md\|SPEC_FILE\|DECISIONS'`, then confirm by reading the lines), and
for each: frozen or not, and whether it searches for text in the file (and
which text) or only hashes or copies it. Output file only, as a table. This
decides nothing; it shows whether SPEC could be shortened later without
breaking a script.

## End of session

Follow CLAUDE.md's end-of-session steps, with these details:

- **F151** (at most about 30 lines): D102 recorded; the SPEC, RESULTS and
  README edits made (by item, not text); the two figures with their gate
  results and SHA-256; the new test; Step 5's count (how many scripts open
  SPEC.md, how many search its text); `data/raw/grib/`'s state from Step 0;
  readings for the owner; what was not done; pointer to
  `notes/session-108-output.txt`.
- **Archive step (D102.7):** set the Live index to exactly D93, D102 and
  F151, then `python3 scripts/archive_decisions.py --apply --session 108`.
  D82, D88, D89, D98, D100, D101 and F150 should move; report what moved
  and DECISIONS.md's size before and after.
- **Checks:** citations, size (under 80,000 bytes), scope, and the test
  suite (all pass; report the count). Consistency re-read of what changed,
  written into the output file.
- **STATUS.md:** current-only snapshot and as short as it can be: stage C
  done (D100, F150); stage G next (D102.4); stage B unchanged; MOSMIX and
  MMMX carried; the GRIB cache on the external drive (D102.3). **Next
  planning session:** Review session 108. The owner commits and pushes
  (`git commit -F docs/commits/commit-108.txt`) and the planning chat syncs
  Project knowledge. Then design stage G (live product v1 on GFS,
  including GFS v17 handling) in the planning chat, and plan session 109.

## What this session must not do

Refit, re-score or re-run any model or the look; read any claim table,
`MLwx-*` folder or 2026-27 value; access `/Volumes/` or the external
drive; use the network; install anything; edit any existing script, data
file or figure; edit SPEC.md or RESULTS.md beyond Step 3. Nothing
committed and no commit message written.
