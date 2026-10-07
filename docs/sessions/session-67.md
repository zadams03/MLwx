# Session 67 — Repo and code audit (read-only), second of three audit sessions

## Context

This session is part two of the audit ordered in D60.1:

- **Session 66 (done):** audit the documents. Report:
  `notes/audit-session-66.md`.
- **Session 67 (this one):** audit the repo and code, including a
  fresh-environment check.
- **Session 68:** audit correctness.

Triage and fixes follow after session 68.

For scale, the repo holds 68 files in `scripts/` (about 40,800 lines of
Python) and 877 tracked files. So this session is **script-driven**. Do not
read every script. Run scripted checks over all of them, and open a script
only to confirm a specific finding.

## Scope

This session is **read-only**. It **reports** findings and **fixes
nothing**.

Exactly two files in the repo may be written:

1. a new `notes/audit-session-67.md`, the findings report;
2. the overwritten STATUS.md.

There is **no** DECISIONS entry this session.

All check scripts, installed tools (such as `ruff`) and the fresh clone live
**outside the repo**, under `/tmp`. Nothing is installed into the project's
own `.venv`. Paste the full source of every check script into the report's
appendix.

The following are all ruled out:

- modifying any file under `scripts/`, `data/`, `docs/` or `notes/`, other
  than creating the new report;
- fitting any model;
- producing any MAE on 2024-25 or 2025-26.

Loading a processed file to count its rows, dates or keys is fine; that
reads data but scores nothing. The one allowed run of project code is Step 3.

**Frozen scripts** (listed in `notes/audit-session-66.md`, section 3): report
findings on them, but mark any suggested fix as "frozen — owner decision",
because editing one needs a decision first.

If this prompt disagrees with a spec file, stop and flag it.

---

## Step 0 — Starting state

Run `git status --porcelain` and report the result. The only expected output
is the untracked prompt file, `docs/session-67.md`.

## Step 1 — Inventory

1. **What git tracks.**
   - Give tracked file counts and total sizes per top-level folder.
   - List the 20 largest tracked files.
   - Flag every tracked file over 5 MB.
   - Flag any tracked raw GRIB or bulk raw data that D47 says must be
     gitignored.
2. **Ignored and untracked files.** Review `.gitignore` against D47. Report
   any files in the working tree that are untracked but not ignored, and any
   ignore rule that looks wrong or missing.
3. **Paths named in the docs.**
   - Extract every repo path mentioned in SPEC, RESULTS, STATUS, CLAUDE, live
     DECISIONS and `docs/*.md`: anything under `scripts/`, `data/`, `notes/`
     or `docs/`. For DECISIONS-archive.md, use a grep only; do not read it.
   - Report every path that does not exist in `git ls-files` or on disk.
   - A path whose file is gitignored by design (D47) is allowed. List those
     separately.
4. **Orphans.**
   - Check every tracked file in `scripts/`, `data/processed/` and `notes/`
     for a reference: its name should appear in at least one doc (the archive
     counts, by grep) or be used by another script.
   - Report the unreferenced files.
5. **Manifests and provenance** (D15, D47).
   - Find every provenance manifest.
   - For each file a manifest lists, check that the file exists, and check
     any checksum or row count the manifest states.
   - Report every mismatch.
6. **Processed data sanity.** For each file in `data/processed/`, report:
   - its row and column counts;
   - its minimum and maximum date;
   - any **duplicate key rows** (station and date, or whatever the file's
     natural key is);
   - any columns that are entirely null.

   This is a shape check only. Nothing is scored.

## Step 2 — Static code checks

1. **Compiles.** Run `python -m py_compile` on every script and report
   failures.
2. **Lint.** Run `ruff` from the `/tmp` install, with pyflakes-class rules
   (`F`) plus the defaults.
   - Report counts by rule.
   - List every F821 (undefined name) and F811 (redefinition) individually.
     These can be real bugs.
   - List unused imports as a count, not line by line.
3. **Hard-coded paths.**
   - Grep for absolute paths, such as `/Users/`.
   - Find output paths that name a **different session number** from the
     script's own. This is the `OUT_PREFLIGHT` pattern that F109 found.
   - Report each instance, and say whether that script can overwrite a
     committed file belonging to another session.
4. **Dependencies.**
   - Check whether a requirements or lock file exists, whether its versions
     are pinned, and whether the Python version is recorded anywhere.
   - Collect every third-party import across all scripts (by parsing each
     script, the "AST" method) and compare that set against the requirements.
   - Report anything imported but not listed, and anything listed but never
     imported.
5. **Duplicated and drifting code.**
   - Parse every function definition in every script.
   - Report functions that appear with an **identical body in 3 or more
     scripts**. This is duplication: a candidate for a shared module later.
   - More important: report functions that have the **same name but
     different bodies** across scripts, especially names to do with loading,
     pairing, persistence, splitting, fitting or scoring. This is drift, and
     it is a possible correctness risk.
   - For each drifting name, give a one-line description of how the bodies
     differ. Open the scripts only for this.
6. **The core pipeline map** (this feeds session 68).
   - Identify which scripts produce the recorded headline results: the
     minimal-method sealed tests (F16/F30/F47/F64/F82), F94 and F109.
   - Identify the shared code paths they rely on: data join, pairing,
     persistence, and the train/test split.
   - Produce a short map of script → role → the result it produces.
   - Session 68 will review exactly this set, so be accurate. Use the docs
     and grep, and read scripts only as needed.
7. **Tests.** Report whether any automated tests exist, and whether they run.
   Report the guard functions (such as the reserved-year guard) and where
   each is called.

## Step 3 — Fresh-environment check (in `/tmp`, not the repo)

1. Clone the repo into `/tmp` with `git clone` from the local path.
2. Set up the environment **only as the repo itself documents it**.
   - If no setup is documented, that is a finding. Then attempt it from the
     requirements file, and record exactly what you did.
   - Report the Python version used, the install output summary, and any
     failures.
3. In the clone, run `python -m py_compile` on all scripts.
4. In the clone, run `scripts/session62_reserved_confirm.py` with **no
   arguments**. That is `preflight()` only. **Never `--confirm`.**
   - Its hard-coded output file is written inside the `/tmp` clone, which is
     harmless.
   - Compare its 2023-24 machinery dry-run table against the session-61,
     session-62 and session-64 table recorded in F109, to the fourth decimal
     place, at all five airports.
   - If it fails because gitignored data is missing from a clean clone,
     report that as a finding. Do not work around it.
5. Report the libomp or interpreter behaviour seen in session 64, if it
   recurs.

## The report: `notes/audit-session-67.md`

Use the same structure as session 66.

1. **Summary.** Counts by severity.
2. **Findings as a plain list, not a table.** One block per finding:

   ```
   A67-nn | severity | file:line
   evidence: ...
   suggested fix: ...
   ```

   Severity is **must-fix** (wrong, broken, a correctness risk, or not
   reproducible), **should-fix** (stale, fragile or misleading), or
   **cosmetic**. Mark anything you are unsure about as **uncertain**, with
   your reasoning.
3. **The core pipeline map** from Step 2.6.
4. **Clean checks.** List every check that came back clean, stated
   explicitly.
5. **Appendix.** The source of every check script, plus the raw output. For
   very long outputs, give a summary and the path to the full output under
   `/tmp`.

## End of session

1. Paste into chat, **as plain text with no tables**:
   - the report's summary;
   - the findings list;
   - the core pipeline map;
   - the Step 3 result.
2. Overwrite STATUS.md as a current-only snapshot. It should say:
   - sessions 66 and 67 are done, with their report paths;
   - session 68 is next;
   - Q30 is deferred;
   - Q32 is unchanged.

   It must end with a "Next planning session" line: owner review of the
   session-67 report, then drafting session 68 (correctness audit) using the
   core pipeline map, including a decision on whether its size warrants
   subagents.
3. Run `git status` and show that only `notes/audit-session-67.md` (new) and
   STATUS.md changed.
4. Write a suggested commit message. Do not commit anything.
