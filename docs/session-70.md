# Session 70 — repo fixes, offline (DECISIONS D62.5, D62.8)

## Purpose

Carry out the four repo fixes that D62 assigned to this session:

1. **A67-01 (must-fix, D62.4):** build committed provenance manifests for
   the session 37 and session 40 GRIB pulls, from the gitignored sidecars.
   Also commit the two failure CSVs.
2. **A67-06:** add a station column to
   `data/processed/session46_fold_table.csv`, without refitting anything.
3. **A67-05 with A67-07:** write a README / setup note, and fix the
   out-of-date comments in `requirements.txt`.
4. **A67-08 with A68a-06:** fix the `.gitignore` gaps.

Then record the work as **D63** and do the end-of-session steps.

Before starting, read the audit findings for each item in full:
`notes/audit-session-67.md` (A67-01, A67-05, A67-06, A67-07, A67-08) and
`notes/audit-session-68a.md` (A68a-06). They say exactly what each gap is.
Use their wording for what to fix. Do not widen the fix beyond what they
describe.

## Standing rules for this session (D62)

- **No file is deleted.** This includes the cache, the sidecars and any
  tracked file.
- **No frozen script is edited.** The frozen scripts are
  `session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py` and `session62_reserved_confirm.py`. In
  addition, this session edits **no existing script at all**, including
  `session46_backtest.py`.
- **Nothing is scored.** No model is fit. No MAE is computed. No
  observation file is read.
- **No GRIB file is opened or decoded.** Only the sidecar metadata files
  and the failure CSVs are read.
- **Offline.** No network access and no re-fetching.
- **No existing file under `data/raw/` is changed.** New files may be
  added. If a target file name already exists, stop and report. Do not
  overwrite it.
- **Stop and report on any mismatch.** Do not force a reconciliation,
  fill a gap, or guess. Report what you found and wait.

New helper scripts are allowed if they are needed. Name them
`scripts/session70_*.py`. They must be read-only against every existing
file, apart from the one in-place CSV edit in Task 2. Always run Python as
`.venv/bin/python`.

---

## Task 1 — A67-01: provenance manifests for the session 37 and 40 pulls

**Goal.** D47 requires the provenance of the large GRIB pulls to be
committed: URLs, byte ranges, pull times and the drop log. For sessions
37 and 40, this record currently exists only in the gitignored cache.

**Step 1.1 — Find the expected counts in the record.** Before touching the
cache, open `DECISIONS-archive.md`. Find the archived entries that record
the session 37 bulk pull (F90) and the session 40 sealed-year pull (F92,
and F93 if relevant). If you find the counts in a different entry, cite
that one. Copy out, with the entry number, each recorded count:
messages requested, messages fetched, messages dropped, and any stated
per-airport or per-day counts. **Take these numbers from the archive
only**, not from this prompt or from memory.

**Step 1.2 — Inventory the cache (read-only).**
- Locate the GRIB cache and its sidecars. The audit's A67-01 text says
  where they are.
- If the cache, the sidecars or either failure CSV is missing, **stop and
  report what exists.** Do not rebuild anything.
- Count the sidecars. Assign each one to the session 37 pull or the
  session 40 pull, using its own content: its validity dates, its pull
  time, or the folder it sits in. Session 37 covers 2021-03-24 to
  2025-07-31. Session 40 covers the sealed year, 2025-08-01 to 2026-07-31.
  **Stop if any sidecar cannot be assigned unambiguously.**
- Count the rows in each failure CSV.

**Step 1.3 — Reconcile, then stop or continue.** Session 67 reported
31,284 sidecars and a session 37 failure log with 24 rows. Reconcile the
Step 1.2 counts against the Step 1.1 archived counts. Show the
arithmetic, per pull:
- sidecars vs messages fetched;
- failure-log rows vs messages dropped. If the log has more rows than
  drops, explain why from the log's own contents (for example, retries or
  more than one row per message). If the contents do not explain it, it
  is a mismatch.

**If any count does not reconcile exactly, stop here.** Report the table
and wait. Do Tasks 2 to 4 only after the owner replies. Do not write any
manifest.

**Step 1.4 — Build the manifests (only if Step 1.3 reconciles).**
- Look at the existing `*_pull_manifest.csv` files under
  `data/raw/diagnostics/`. Match their naming convention, and match their
  column names where the sidecars hold the same fields.
- Write one manifest per pull:
  - `data/raw/diagnostics/session37/<name>_pull_manifest.csv`
  - `data/raw/diagnostics/session40/<name>_pull_manifest.csv`

  Create the two folders only if they do not already exist.
- **Build them mechanically.** Use one row per sidecar. Copy every field
  verbatim from the sidecar (URL, byte range, pull time, status and any
  others), and add a column with the sidecar's path relative to the
  cache. Sort the rows in a fixed, stated order. Invent no field. If a
  field is blank in a sidecar, leave it blank and count it. Do not fill it.
- Copy each failure CSV **byte-for-byte** into the matching folder, and
  keep its file name. The originals stay where they are.

**Step 1.5 — Checks.** Paste the real output of each.
- Manifest row count equals the sidecar count, for each pull.
- Every sidecar appears exactly once, with no duplicates.
- Blank fields are counted per column.
- Each failure CSV copy has the same checksum as its original
  (`shasum -a 256`).
- The script is re-run on the unchanged cache, and the manifests are
  byte-identical to the first run.
- `git check-ignore -v` on all four new files returns nothing, so they
  are not ignored.

---

## Task 2 — A67-06: station column in `session46_fold_table.csv`

**Goal.** Add a `station` column, so that each of the 50 rows names its
airport directly instead of by file order. Edit the file in place. No
refit and no re-run of `session46_backtest.py`.

**Step 2.1 — Derive the station for each row.**
- Read `scripts/session46_backtest.py` (read-only). Work out the order in
  which it writes the fold table's rows, by station and fold.
- **Cross-check each row** against `data/processed/session46_backtest_profile.csv`,
  which has 150 rows. Match on every shared column, with values compared
  exactly as strings. A row is confirmed only if it matches exactly one
  station, and that station agrees with the write order.
- **Stop on any row that cannot be matched, that matches more than one
  station, or where the match disagrees with the write order.** Report
  it and wait. Do not write the file.

**Step 2.2 — Edit in place (only if all 50 rows are confirmed).**
- Add `station` as the first column. Use the station codes as SPEC writes
  them (EGLC, LFPG, DSM, YSDU, RNO), unless the profile CSV uses a
  different form, in which case match the profile CSV and say so.
- Change nothing else: not the row order, the other values, the
  quoting, the number format, the line endings or the trailing newline.

**Step 2.3 — Checks.** Paste the real output of each.
- The row count is still 50.
- Remove the new column from the edited file, then compare it byte-for-byte
  with `git show HEAD:data/processed/session46_fold_table.csv`. It must be
  identical.
- Show a per-station row count table.
- `git diff --stat` shows only this one data file changed in `data/`.

Note for D63: `session46_backtest.py` is not edited, so a future re-run
would write the file without the column. Record this mismatch in D63.

---

## Task 3 — A67-05 with A67-07: README and `requirements.txt` comments

**Step 3.1 — Write `README.md`** at the repo root. Keep it short and
plain (CLAUDE.md style). Include:
- **What the project is:** one or two sentences, pointing to SPEC.md.
- **Setup:** the Python version, creating `.venv`, and
  `pip install -r requirements.txt`. Note that eccodes is needed for GRIB
  decoding. Add the **libomp note** from session 67's audit: LightGBM on
  macOS needs the OpenMP runtime. Use the audit's own wording for the
  exact install step.
- **Running scripts:** always use `.venv/bin/python`, never a bare
  `python`, as session 67 asked.
- **Repo layout:** one line each for `scripts/`, `data/raw/`,
  `data/raw/diagnostics/`, `data/processed/`, `notes/` and `docs/`.
- **The documents:** SPEC (source of truth), STATUS, DECISIONS,
  DECISIONS-archive, RESULTS, CLAUDE, and one line on what each is for.
- **Raw data policy (D47):** raw GRIB is not in git. It can be re-fetched
  from the committed pull manifests under `data/raw/diagnostics/`.
- **Frozen scripts:** name the four, and say that they are never edited
  and that any re-run happens in a clean clone (D62.3, D62.6).

**No results, figures, MAEs or verdicts.** Point to RESULTS.md instead,
so there is no second source of truth.

**Step 3.2 — `requirements.txt`.** Fix only the out-of-date comments
that A67-07 names. Change no package, version or pin. If README now
covers a setup note, the comment may point to README instead of
repeating it.

**Step 3.3 — Check.** Show that `git diff requirements.txt` changes
comment lines only: every added or removed line starts with `#`, or is
blank.

---

## Task 4 — A67-08 with A68a-06: `.gitignore`

**Step 4.1 — Before editing,** record:
- `git ls-files | wc -l`;
- `git status --porcelain --ignored`, saved for comparison.

**Step 4.2 — Fix only the gaps the audits name:**
- a comment on the GRIB cache rule, citing D47;
- ignore `.claude/`;
- ignore scratch GRIB files, using the pattern the audit gives. **It must
  not catch the tracked diagnostic GRIB samples under
  `data/raw/diagnostics/`**, which stay tracked (D62.7, A67-13), or any
  new file placed there;
- remove the trailing slash on the cache rule, so it also matches a
  symlinked cache.

**Step 4.3 — Checks.** Paste the real output of each.
- `git ls-files | wc -l` is unchanged. Adding an ignore rule never
  untracks a file, and nothing is `git rm`'d.
- `git ls-files -ci --exclude-standard` lists which tracked files now
  match an ignore rule. Report the list. The expected result is none,
  apart from any the audit already flagged.
- `git check-ignore -v` confirms the GRIB cache path (including through
  the symlink, if one exists) and `.claude/` are ignored.
- `git check-ignore -v` confirms the Task 1 manifests and failure-CSV
  copies are **not** ignored.
- `git status --porcelain --ignored` is compared with Step 4.1, and every
  change is explained.
- `git status` stages no raw GRIB file.

---

## End of session

1. **Real output.** Paste the real output of every check above. Also save
   it to `notes/session-70-output.txt`.
2. **DECISIONS.md: append D63** ("Session 70 decision: repo fixes
   (A67-01, A67-06, A67-05/07, A67-08/A68a-06) done"). Record:
   - what was done under each item, with the new file paths;
   - the Task 1 reconciliation table, citing the archived entries its
     counts came from;
   - the `session46_backtest.py` mismatch from Task 2;
   - a "what this did not do" line: nothing deleted, no frozen script
     edited, no existing script edited, nothing scored, no GRIB decoded,
     no network.

   If the session stopped early, record only what was actually done.
3. **Overwrite STATUS.md** as a current-only snapshot (CLAUDE.md). Prune;
   do not append. Mark the session 70 items done. Keep session 71
   (A68a-01) and Q30/Q32 as they are. **End with the line:** "Next
   planning session: draft session 71 (network, data only: rebuild L, D,
   T and R for the same 45 station-days, A68a-01) per D62.8." If the
   session stopped early, make that line name the blocker instead.
4. **Consistency check.** Re-read SPEC, STATUS and DECISIONS. Report
   disagreements, duplicated headings and out-of-order entries. Report
   only; do not fix.
5. **Archive step.** Apply the D46 criterion. D62 stays live, because
   session 71 and Q30 (D62.7, A67-15) still need it. Move nothing else
   unless it clearly meets the criterion, and say why.
6. **Suggested commit message.** Write one out, then stop and wait for
   review. **Do not commit, add or push anything.**
