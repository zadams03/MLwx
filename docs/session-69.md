# Session 69 — Audit triage recorded (D62), documentation fixes, archive move

**Type:** documentation only. No code, no data build, no model fit, no score.

**Why:** the three-part audit (DECISIONS D60, D61) is complete. The four reports
are `notes/audit-session-66.md`, `-67.md`, `-68a.md` and `-68b.md`. They found no
leakage and no wrong number, and 163 of 163 recorded figures reproduce. The
owner has triaged every finding in the planning chat. This session:
- records that triage as one DECISIONS entry, D62;
- makes every documentation fix the triage assigns to it;
- does the archive move.

Two later sessions handle the rest (see D62's session plan below).

---

## Scope (hard limits)

**Files this session may write — exactly these six, nothing else:**
- `DECISIONS.md`: append D62, then the archive removals.
- `DECISIONS-archive.md`: the archive additions.
- `SPEC.md`
- `RESULTS.md`
- `CLAUDE.md`
- `STATUS.md`: overwrite.

**Forbidden:**
- **No file is deleted, renamed or moved anywhere in the repo.** This includes
  the five files in A67-09. They stay exactly where they are.
- No file under `scripts/`, `data/` or `notes/` is modified.
- No frozen script is edited, not even a comment or docstring:
  `session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py`, `session62_reserved_confirm.py`.
- No script is run. No model is fit. Nothing is scored.
- No row of 2024-25 or 2025-26 data is opened.

**Reading allowed (read-only):**
- The four audit reports.
- `DECISIONS-archive.md`, but only by opening a single entry by number where a
  step needs its exact wording.
- `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`,
  for the five correction constants in Step 2a.
- The five files named in A67-09, opened only to state in D62 what each one is.

**Every number written into any file must be copied from a cited source**:
a DECISIONS entry, an audit report, or the params CSV. Cite it inline. Never
compute a new figure.

If this prompt and a spec file disagree, stop and flag it (CLAUDE.md).

---

## Step 0 — Start checks

1. Run `git status --porcelain`. The only expected entry is `?? docs/session-69.md`.
   If anything else appears, stop and report.
2. Read the four audit reports in full: sections 1–2 and the findings and owner
   notes. The appendices only where a step needs them.
3. Open each A67-09 file read-only:
   - `scripts/session01_checks.py`
   - `scripts/session03_checks.py`
   - `scripts/session03_pull.py`
   - `notes/session-01-check-output.txt`
   - `notes/session-53-pressure-output.txt`

   Write one plain sentence per file saying what it is and which session made
   it. Base each sentence on the file's own contents, not its name.

---

## Step 1 — Append D62 (before any other edit)

Append a new dated section to the end of `DECISIONS.md`:
`## 2026-09-23 — Session 69 decision: audit triage (D60, D61) recorded`.

Its entry is **D62**. Write it in plain language, in numbered parts, with the
following content. Use each finding's own ID. For each item, give a
one-line reason in your own words, taken from the audit report.

**D62.1 The audit's outcome.**
- No leakage and no wrong number.
- 163 of 163 recorded figures reproduce (68a).
- 315 of 315 sampled B values were rebuilt exactly from the raw GRIB (68a).
- No verdict, claim or figure on record changes (D60.2, D61.4).

**D62.2 The triage rubric (owner decision).**
- **Must-fix:** SPEC, or a binding rule, is untrue as written today.
- **Should-fix:** a gap in the record, or a latent risk for code that will be
  reused.
- **Leave-alone:** no effect, or a frozen script whose look is spent. These are
  recorded here and nothing else is done.

**All must-fix and should-fix items are done before any Q30 branch is chosen.**
Q30 stays open and unchanged (D59.5, D60.1).

**D62.3 Owner rulings.**
- (a) **Frozen scripts are never edited.** Their issues are recorded in D62.6
  only.
- (b) **A67-12: SPEC 4.5 is changed on purpose to match the code**, per
  CLAUDE.md "SPEC beats code". The historical scripts are not edited. Future
  code must pick the nearest report explicitly (SPEC 8.7 build requirements).
- (c) **A68a-01: a network session will rebuild L, D, T and R** for the same 45
  station-days (session 71).
- (d) **A68b-02 is must-fix.**
- (e) **A67-09 moves from cosmetic to should-fix.** The fix is D62.7's
  one-line description of each file. **No file is deleted.**

**D62.4 Must-fix (3).**
- **A68b-02.** The GRIB methods' raw-GFS rung is the elevation-adjusted GRIB
  temperature (D48.10). SPEC 5.2 calls raw GFS "the uncorrected forecast".
  Fixed in this session: SPEC and RESULTS.
- **A67-12.** SPEC 4.5 says "nearest"; the code keeps the last qualifying
  report. The whole record has 1 tie day (YSDU), with equal temperatures, so
  there is no effect. Fixed in this session: SPEC 4.5 and SPEC 8.7.
- **A67-01.** The provenance for the session 37 and 40 GRIB pulls exists only
  inside the gitignored cache, which does not meet D47. Fixed in session 70.

**D62.5 Should-fix.**

This session (documentation):
- A68b-03: the persistence day basis.
- A66-08: CLAUDE.md's paste wording (owner-reclassified in audit-66 section 5).
- The "run once" wording in SPEC 7.4 and 8.4 needs a pointer to D61.4. This
  point came from 68a's end-of-session check.
- SPEC 3.4's RNO stage, "2 — failed", is true of the minimal method only.
- A66-06.
- A66-07.
- The new SPEC 8.7 build requirements, which carry the lessons of A68b-01,
  A68b-04, A68b-05, A67-12, A67-02 and A67-03.
- A67-09.
- The archive move, which covers A66-01 and A66-02.

Session 70 (repo, offline):
- A67-01
- A67-06
- A67-05 with A67-07
- A67-08 with A68a-06

Session 71 (network):
- A68a-01

**D62.6 Leave-alone (recorded only).**

Frozen, looks spent, no edit:
- **A67-02 and A67-03.** These scripts write fixed, committed output paths. Any
  future re-run must happen in a clean clone.
- **A67-04.** The preflight's "no reserved-year row is read" text has been
  stale since F107. The rows are loaded but not used (68b item 22).
- **A67-14.** It cannot happen on the F109 path (0 of 9,777 complete-case rows).
- **A68a-04.** An absolute path is printed in the F94 output.
- **A68a-05.** The F109 confirm output was captured outside the script, in
  session 64.
- **A68b-01.** The frozen part: the F109 gap guard checks for zero rows only.
  No effect, since there were 365 of 365 rows.
- **A68b-04.** The frozen parts: `float()` accepts `nan`. There are 0 such
  values today.
- **The frozen F94 docstring** (`session39_sealed_test.py:9`) says all rungs
  use "the same common days". The code does not do that (A68b-03).

Other:
- **A66-03.** Resolved itself.
- **Audit-66's "15 dated headers".** This was a prose miscount; its own raw
  output shows 14 (audit-67 section 6.3).
- **A66-04 and A66-05.** P1 is superseded by Q30. P2 and P3 have met their
  trigger and are eligible to revisit. No action. The parked block is not
  edited.
- **A67-10 and A67-11.**
- **A68a-02.** The constants are frozen by D48.3. Terrain interpolation
  matched 5 of 5.
- **A68a-03.** For the minimal method, D60.2's "fourth decimal" is read as the
  recorded precision, which is 3 decimals.
- **A68b-05, A68b-06 and A68b-07.**

**D62.7 Rulings and records.**
- **A67-13.** Small diagnostic GRIB samples under `data/raw/diagnostics/` stay
  tracked. D47 covers the bulk pull only.
- **A67-15.** The two tracked DSM files for 2026-08-05..2026-08-15 must be
  named in any 2026-27 pre-registration, if Q30 branch (i) is chosen.
- **A67-09.** One line per file, from Step 0.3, stating what each is. All five
  stay in the repo.

**D62.8 Session plan.**
- **69:** this session.
- **70:** repo fixes, offline.
- **71:** the L, D, T and R rebuild, with network. Data only. The pull date is
  recorded (SPEC 2.3).
- **Then Q30.**

**D62.9 What this decision did not do.** No code, data, model or figure was
touched. No file was deleted.

---

## Step 2 — SPEC.md edits

Make each edit in place. Keep everything else unchanged. Cite DECISIONS
inline, as SPEC already does. Keep the plain style.

**2a. Raw-GFS baseline (A68b-02).**
- **In 5.2**, reword the Raw GFS bullet. It should say "raw GFS" means the GFS
  forecast *before this project's model corrects it*. Then add a short
  per-method note:
  - **Minimal method (sections 1–6):** the GFS value as Open-Meteo serves it,
    with no adjustment by this project.
  - **GRIB methods (sections 7 and 8):** the GRIB 2 m temperature after this
    project's fixed per-airport elevation adjustment (D48.3). This was
    pre-registered as the baseline in D48.10.
- **Give the five adjustment sizes in °C**, copied from `correction_c` in the
  params CSV.
- **Say plainly** that the margins against a fully unadjusted GRIB baseline
  were never measured. They cannot be now, because both held-out years are
  spent (D59.5).
- **In 7.2**, add one bullet stating the same for the GRIB baseline, pointing
  to 5.2. **In 8.2**, add "and the same raw-GFS baseline (5.2, 7.2)".
- **Under the 7.4 and 8.5 tables**, add one line: "raw GFS (GRIB)" here is the
  elevation-adjusted GRIB temperature (5.2).
- **In 7.5**, extend the existing "not the same series" sentence. The two
  raw-GFS baselines also differ in how elevation is handled: Open-Meteo's own
  processing on one side, this project's fixed adjustment on the other.

**2b. Pairing (A67-12).** In 4.5, add a short paragraph with three points:
- The historical code keeps the **last** qualifying report in the file, not
  explicitly the nearest.
- The two rules differ only when two or more usable reports fall within the
  15-minute window on the same day. That happened on 1 day in the whole record
  (YSDU), with equal temperatures, so no recorded figure is affected
  (audit-67 A67-12, audit-68b item 9).
- New code must select the nearest report explicitly (8.7).

Cite D62.

**2c. Persistence day basis (A68b-03).**
- **In 7.4 and 8.5**, add one sentence each: persistence is scored only on test
  days that have a previous-day observation, while raw GFS and the models use
  every test day.
- **Cite the sources:** for F94, cite F94 Task 2, which found the verdicts
  identical on a common day basis. For F109, cite D58 item 6 and F109: EGLC is
  missing 1 day and YSDU 5.
- **Note** that the minimal method scores every rung on one common day set
  (D21.8).

**2d. "Run once" (68a note).** In 7.4, after "run once, unchanged (DECISIONS
D48.13)", and in 8.4, after "run once, and only once", add a parenthesis. It
should say that one later verification re-run, in session 68a, reproduced
every figure exactly and changed no verdict (DECISIONS D61.4, D62).

**2e. SPEC 3.4 table.** Change RNO's stage cell to make clear that "failed" is
the minimal method (F82). Reno passes the richer (F94) and selected (F109)
methods. Keep it short enough for a table cell. A footnote under the table is
fine.

**2f. Section 6 (A66-06).** In the "Further airports may follow before stage
3" bullet, add: "using the project's default recipe (8.7)".

**2g. Glosses (A66-07).** At the first use in SPEC of each of these terms, add
a short plain-language gloss:
- **bilinear-interpolated:** estimating a value from the four surrounding grid
  points, weighted by distance;
- **lapse rate:** how fast temperature drops with height;
- **complete-case:** a row is used only if every relevant column has a value.

**2h. New 8.7 subsection: "Build requirements for new-airport code".** Add it
after 8.7's current text, as a short list that cites D62:
1. **Pair observations to the nearest report explicitly** (A67-12).
2. **Reject non-finite values** (`nan`, `inf`) at load, and drop and count them
   as missing (rule 2.2; A68b-04).
3. **Check each GRIB message's full validity date and hour**, not the date
   alone (A68b-05).
4. **A test-year gap guard must compare the row count with the expected full
   count**, not with zero (A68b-01).
5. **Scripts must not write to already-committed record files on a re-run**
   (A67-02, A67-03).

State that these apply to **new** code only. The historical and frozen scripts
stand as they are.

---

## Step 3 — RESULTS.md edits

Find each place by its content; line numbers may have moved.

**3a. The 5.3 table and the 6.3 table.** Under each, add one line saying that
"raw GFS (GRIB)" is the elevation-adjusted GRIB temperature (SPEC 5.2,
DECISIONS D48.10).

**3b. The cross-method caveats.** These are the "Honest magnitude" paragraph at
the end of section 5 and the "Cross-method margin comparisons need care"
bullet in section 7. Extend each so it says the two raw-GFS baselines differ
in elevation handling as well as in source:
- the minimal method's baseline carries **no project-applied adjustment**
  (Open-Meteo's served value);
- the GRIB methods' baseline carries **the project's fixed lapse-rate
  adjustment**.

Do not describe the minimal baseline as "uncorrected". RESULTS 5.4 already
credits Open-Meteo with its own downscaling, so keep consistent with that.

**3c. The persistence day basis.** Add one sentence in section 5 and one in
section 6, with the same content and citations as Step 2c.

Do not change any figure, table value or verdict in RESULTS.

---

## Step 4 — CLAUDE.md edit (A66-08)

Reword the two passages named in `notes/audit-session-66.md` section 5:

1. **"The paste-before-work habit" section.** It should say that the planning
   chat reads the current committed SPEC.md, STATUS.md, DECISIONS.md and
   CLAUDE.md from claude.ai Project knowledge, guided by the planning-side
   `PROJECT-INSTRUCTIONS.md`. The owner re-uploads changed files after every
   commit, so the planning chat never works from a stale copy.
2. **The "Pasted beats remembered" bullet.** Change it to "Uploaded beats
   remembered", with the same meaning: the current uploaded file beats any
   memory or old chat copy.

Change nothing else in CLAUDE.md.

---

## Step 5 — Archive move

Move these entries from `DECISIONS.md` to `DECISIONS-archive.md` by the D46
method. The move is mechanical and verbatim, under a new `## Moved by session
69 (date)` block with a one-line criterion note, as earlier moves did:
- **D49, F95 and D50.** Settled; codified in SPEC 7 and RESULTS 5; not cited by
  STATUS or any live question (A66-02).
- **F94.** Its Task 2 content is now carried in SPEC 7.4 and RESULTS by Step 2c
  (A66-01, A68b-03).
- **D60 and D61.** They defined the audit, and D62 now records its outcome.

**Stay live:**
- D17 and F7
- D46 and D47
- D51 and F96
- D59 and F110
- Q30 and Q32
- the parked block (P1–P3)
- D62

After the move, check two things:
- line counts: removed from DECISIONS equals added to the archive, apart from
  the header block;
- every citation of a moved entry in the live files still resolves.

---

## End of session

1. **Checks, pasting the real output:**
   - `git status --porcelain`. Only the six permitted files may appear as
     modified, plus `docs/session-69.md`. **No deleted file.**
   - `git diff --stat`.
   - `grep -n "uncorrected" SPEC.md RESULTS.md`, with each hit shown in context.
   - `grep -n "D62" SPEC.md RESULTS.md CLAUDE.md DECISIONS.md`.
   - The Step 5 line-count and citation checks.
   - Confirm that the five A67-09 files still exist: run `ls -l` on each.
2. **Overwrite STATUS.md** as a current-only snapshot:
   - The audit is triaged (D62).
   - Session 69's fixes are done.
   - Q30 and Q32 are unchanged.
   - End with: "Next planning session: review session 69, then draft session
     70 (repo fixes, offline: A67-01 provenance manifests, A67-06 station
     column, README, .gitignore) per D62.8."
3. **Consistency check** (CLAUDE.md step 3). Report only.
4. **Archive step:** done in Step 5. Report nothing further unless something
   else became settled.
5. **Write the suggested commit message and stop.** Do not commit. Wait for the
   owner's review.
