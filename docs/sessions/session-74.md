# Session 74 — triage the F113 mismatch (D64.5), record the gaps in SPEC, close D64

Offline. No data is pulled. This session **cannot change any verdict, claim
or figure on record** (D64.1). F109 stands whatever this session finds.
The reserved year (2024-08-01 to 2025-07-31) is scored only to reproduce
F109, under D64.1's standing, and never to select, tune or decide anything.

Work in the step order below. **Do not reorder.** Paste real output at
every step into `notes/session-74-output.txt` and into the chat.

---

## Background (read in DECISIONS: D64, F112, F113)

Session 73 (F113) rebuilt F109 at RNO. Every data stage matches the record
under Variant P. Raw GFS, persistence and B match F109 exactly. One
mismatch remains: **B+D,L,R,T scores 1.2703 in the rebuild against the
record's 1.2742**, with every input matching and the fit repeatable. Two
known recipe differences between the rebuild and the record script were
not tested:

- **G15, column order:** the rebuild uses B then L, D, T, R; the record
  uses D, L, R, T (`FINAL_CODES`, line 118 of the record script).
- **G20, target precision:** the rebuild trains on session 72's 3-decimal
  residual; the record trains on the unrounded residual (line 376).

The record script's path is named in `notes/session-73-output.txt`, Step 5.
The clean-room rule (D64.3) is over. This session may read `scripts/`,
`data/processed/` and `notes/`.

---

## Step 1 — Write the pre-registration (before anything else)

Append the following to DECISIONS.md **verbatim**, under a new heading
`## 2026-09-24 — Session 74 decision: pre-registration of the F113
mismatch triage`. Print it back. Do nothing else until it is written.

> **D65. Pre-registration: triage of F113's B+D,L,R,T mismatch at RNO
> (session 74). Owner decision, planning chat.**
>
> **D65.1 Status.** A verification only, with D64.1's standing. It cannot
> change any verdict, claim or figure. The reserved year is scored only to
> reproduce F109. Nothing is selected on these results.
>
> **D65.2 The settings comparison.** A read-only, exhaustive comparison of
> every setting that affects the RNO B+D,L,R,T fit or its score, between
> the record script and `scripts/session73_fit_score.py`. If any
> difference other than G15 and G20 could affect the fit or its score, the
> session stops before any fit and before any SPEC edit.
>
> **D65.3 The record re-run (R0).** A copy of the record script, changed
> only in its output paths, RNO only, run once into
> `data/rebuild/session74/record_rerun/`. It is skipped, not forced, if it
> cannot be limited to RNO or redirected without changing its logic.
>
> **D65.4 The diagnostic fits.** Exactly three fits, each using session
> 73's Variant P data and code with only the named detail changed:
> - C1: G15 flipped (record column order), G20 as in session 73.
> - C2: G20 flipped (record target), G15 as in session 73.
> - C3: both flipped.
>
> One repeat of C3 in a separate process, for determinism. No other fit.
>
> **D65.5 Expected results.** R0 = 1.2742. C1 = 1.2742. C2 = 1.2703
> (G20 expected to have no effect, since the residual already has at most
> 3 decimals). C3 = 1.2742, with test predictions equal to R0's on 365 of
> 365 days.
>
> **D65.6 Outcome classes.**
> - **A, explained:** C3 matches the record (MAE 1.2742 at 4 dp, and its
>   unrounded MAE equals the record's unrounded value), and where R0 ran,
>   C3's predictions equal R0's on 365 of 365 days. The mismatch is
>   re-labelled "recipe detail", attributed by C1 and C2.
> - **B, unexplained fit:** R0 reproduces 1.2742 but C3 does not.
> - **C, record not reproducible:** R0 does not reproduce 1.2742.
>
> In B and C the result is recorded and there is **no further hunting**.
> Either way D64 closes after this session.
>
> **D65.7 Q33 trigger.** If C1's MAE differs from 1.2703, log Q33 (fit
> noise against verdict margins), for the owner. It is logged only, not
> measured.

---

## Step 2 — Read-only settings comparison (D65.2)

Read the record script and `scripts/session73_fit_score.py`. Write a table
of every item that affects the B+D,L,R,T fit or its score, with record
value, rebuild value, and match yes/no. At minimum cover:

- every LightGBM parameter actually passed, and the resolved defaults
  (compare with `data/rebuild/session73/rno_fit_metadata.json`), including
  any column or row sampling (for example `colsample_bytree`,
  `subsample`, `feature_fraction`, `bagging_fraction`), the seed and
  threading;
- the API used (G14);
- the full column list and its order (G15);
- the target, exactly as each computes it (G20);
- training row order (G19) and row set;
- the data type and container passed to the fit (DataFrame or array,
  float32 or float64, column names);
- how the corrected forecast and MAE are computed (G21, G24);
- library versions used by each (lightgbm, numpy, Python), and the pins.

**Stop rule.** If any item other than G15 and G20 differs and could affect
the fit or its score, **stop here**. If unsure whether a difference could
affect the fit, treat it as if it could. Report the table and go straight
to the end-of-session steps, doing Steps 3–5 not at all. Differences that
cannot affect the fit (logging, file names) are listed and do not stop the
session.

---

## Step 3 — Record re-run, R0 (D65.3), with guardrails

1. List every file the record script writes, and every output path.
2. Decide whether it can be run for RNO only **without changing its
   logic** (for example by an existing argument or airport list). If not,
   **skip R0**, say why, and go to Step 4.
3. Copy it to `data/rebuild/session74/record_rerun/record_copy.py`.
   Change **only** output paths, so every write lands in
   `data/rebuild/session74/record_rerun/`. Print the full `diff` between
   the original and the copy. Any line other than a path is not allowed.
4. Before running: record the SHA-256 of every file from `git ls-files`
   into `data/rebuild/session74/record_rerun/hashes_before.txt`, and print
   `git status --short`.
5. Run the copy once. **Never run the original script.**
6. After running: hash again into `hashes_after.txt`, `diff` the two, and
   print `git status --short`. **If any tracked file changed, stop and
   report.** Do not fix or restore it yourself.
7. Save R0's per-day RNO test predictions and its MAEs (raw GFS,
   persistence, B, B+D,L,R,T, unrounded and 4 dp).

---

## Step 4 — The three diagnostic fits (D65.4)

New script `scripts/session74_diagnose.py`. It uses session 72's tables
and session 73's code path, changing only the named detail per cell.
Outputs go to `data/rebuild/session74/`. Save each cell's per-day test
predictions.

Print for C1, C2, C3 and the C3 repeat: n_train, n_test, the B+D,L,R,T MAE
unrounded and at 4 dp. Then print:

- C3 against its repeat: rows equal, maximum absolute difference;
- C3 against R0 (if R0 ran): rows equal, maximum absolute difference, over
  365 days (this is F113's stage 6, now comparable);
- each cell against the record's 1.2742 and its unrounded value;
- the outcome class (A, B or C) per D65.6, and the attribution from C1
  and C2.

No other fit. Nothing tuned or re-run to pass.

---

## Step 5 — Record the gaps in SPEC

Add a new subsection to SPEC.md, placed after section 8's "Build
requirements for new-airport code" block: **8.8 Implementation details
(from the record, DECISIONS D65).** Keep the edit to this subsection only.

It is one table with columns: item, what the record does, source (script
and line, or DECISIONS entry). Write each row from the **record scripts
and committed files**, not from the rebuild's choice. Rows:

- G1 report tie-break, G2 nearest usable report, G3 the 15-minute edge.
  Read these from the record's observation pairing script, even though
  they made no difference at RNO.
- G4 stored precision of `temperature_grib_c` (3 dp, and `t2m_raw` built
  from it), G5 the elevation constant as used (2.0436), G6 bilinear
  interpolation, G7 rounding order for L and D.
- G14 API, G15 full column list in order, G17 unstated parameters (and the
  pinned lightgbm version they are defaults of), G19 training row order,
  G20 target precision, G24 MAE rounding rule.

Rules:
- If the record does not show the answer for a row, write "not shown by
  the record" and give the rebuild's choice as the rebuild's choice.
- Do not add G8–G10, G16, G18 or G21–G23. For G11–G13, read their
  descriptions in `notes/session-72-output.txt`. Add one only if it could
  change a stored value at some airport, and say why.
- Add one line under the table: "These details are recorded for
  reproducibility. They change no result on record (DECISIONS D64.1,
  D65.1)."

---

## Step 6 — Findings, Q33 and closing D64

Append to DECISIONS.md:

- **F114**, the session's finding. Cover:
  - the settings table;
  - R0's result, or why it was skipped;
  - C1, C2, C3 and the repeat;
  - the outcome class and attribution;
  - the guardrail hash check;
  - the SPEC rows added;
  - a "what this did not do" list.

  State plainly that F114 changes no verdict, claim or figure, and that
  F109 stands.
- **D64 closed**, one short paragraph inside F114: the rebuild is
  complete, the result class, and where the details now live (SPEC 8.8).
- **Q33 only if D65.7's trigger fired**, worded as: "Q33. Changing only
  the column order moved RNO's B+D,L,R,T reserved-year MAE by [x]. How
  large is fit-to-fit variation, compared with the verdict margins on
  record, especially the small ones (for example DSM over B, +1.94%, SPEC
  8.6 (d))? Logged only. Any measurement needs its own pre-registration
  and cannot re-score spent years for a verdict." Fill in [x] from the
  real output.

---

## End-of-session steps

1. Paste the real output of every step run.
2. **Overwrite STATUS.md** as a pruned, current-only snapshot. The D64
   rebuild is closed. Its "Next planning session" line reads: "Next
   planning session: review F114, then the owner chooses a Q30 branch" —
   with "and considers Q33" added if Q33 was logged.
3. Consistency check: re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only.
4. Archive step: move D64, F112 and F113 to DECISIONS-archive.md,
   verbatim and mechanically, since D64 is now closed and SPEC 8.8
   codifies them. Keep D65 and F114 live. If a live open question or
   STATUS's Next still needs any of them word for word, keep it live and
   say why.
5. Confirm you did not edit RESULTS.md, README.md, CLAUDE.md, any file
   under `data/raw/` or `data/processed/`, any existing script, or
   anything under `data/rebuild/session72/` or `data/rebuild/session73/`.
6. Write out a suggested commit message. **Do not commit.** Stop and wait
   for the owner's review.
