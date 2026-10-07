# Session 68a — Correctness audit, part 1: reproduce the record (read-only)

## Context

This is the third part of the audit ordered in D60.1:

- **Session 66 (done):** audit the documents.
- **Session 67 (done):** audit the repo and code.
- **Session 68:** audit correctness. The owner has now split it into two
  sessions:
  - **68a (this one)** reproduces the recorded results and rebuilds a small
    sample of features from the raw GRIB.
  - **68b** is the logic and leakage review of the core pipeline. It is not
    part of this session.

Triage and fixes follow after 68b.

Read `notes/audit-session-67.md` sections 3 and 6 before starting. Section 3
is the core pipeline map. Section 6.1 is binding on this session.

## Scope

**Hard rules for this session:**

1. **Every run of project code happens in a clean clone under `/tmp`.**
   Nothing runs in the working repo (section 6.1 of the session-67 report,
   A67-02, A67-03). Frozen scripts write fixed output paths that are
   committed files, and those writes must land only in the clone.
2. **Each reproduction runs exactly once**, unchanged. Do not re-run to
   "check", and do not change any setting, variant or metric. D60.2 permits
   this recompute once. It is not a verdict and not a new look, and every
   recorded verdict stands whatever it shows.
3. **No network fetches.** If a run needs data the clone lacks, report that
   as a finding. Do not fetch it and do not work around it.
4. **No project file is edited.** Exactly three files in the working repo
   may be written:
   - a new `notes/audit-session-68a.md`, the report;
   - one appended DECISIONS entry, D61 (Step 1);
   - the overwritten STATUS.md.
5. **Mismatches are reported, not investigated.** A mismatch is a must-fix
   finding for triage and for 68b. Do not debug it here.

Check scripts and harnesses live in `/tmp`. Paste their full source into the
report's appendix.

You may open a single archived DECISIONS entry by number (F16, F30, F47,
F64, F82, F109 and so on) to read its recorded figures. Do not read the
archive in full.

If this prompt disagrees with a spec file, stop and flag it.

---

## Step 0 — Starting state and the D60.2 gate

1. Run `git status --porcelain`. The only expected output is the untracked
   `docs/session-68a.md`.
2. **Gate (D60.2).** Read SPEC section 2 and any other rule text in CLAUDE.md,
   SPEC or the live DECISIONS that could bear on re-running code on 2025-26
   or 2024-25.
   - If any wording forbids a verification recompute, **stop here**. Quote
     the wording and wait for the owner.
   - Otherwise, quote the relevant rules and state why D60.2's
     verification-only recompute is consistent with them.

## Step 1 — Append D61 (records the split; before any run)

Add a dated heading, `2026-09-23 — Session 68a decision: ...`, then write
D61 with these items:

- **D61.1** Session 68 (D60.1) is split in two:
  - 68a: reproduction of the recorded results, plus a sample rebuild of
    features from the raw GRIB;
  - 68b: the logic and leakage review of the core pipeline (the
    session-67 map).

  D60.2's single permitted recompute takes place in 68a only. 68b does not
  recompute any spent-year figure.
- **D61.2** The sample rebuild (Step 3) reads the local gitignored GRIB cache
  read-only and writes only inside the `/tmp` clone. It builds data only: it
  fits nothing and scores nothing.
- **D61.3** The 68b review covers the headline pipeline only, meaning the
  scripts behind F16/F30/F47/F64/F82, F94 and F109 and their data builds. It
  does not cover the E1–E5 or combine experiment scripts. The reason: the
  one reserved-year look (F109) confirmed the chosen set, so a bug in an
  experiment script would have changed which features were chosen, not
  whether the confirmed set passes.

## Step 2 — Reproduce the recorded results (in the clone)

1. **Set up the clone.**
   - Run `git clone` from the local repo into `/tmp` and record HEAD.
   - Set up the environment exactly as session 67 did, from
     `requirements.txt`, with Python 3.12.2.
   - Run everything with the clone's own `.venv/bin/python`.
2. **Pre-registered expectation, written down before any run.**
   - For every script, figure and airport, list what will be compared.
     That means every recorded MAE (raw GFS, persistence, and each model
     rung), the pass/fail result, and the row counts (n_train, n_test and
     the drop counts), with the recorded value and its DECISIONS source.
   - Expectation: exact match to the fourth decimal place for MAEs, and
     exact match for counts and verdicts.
   - Put this list in the report **before** the results section.
3. **Run each once, in this order, capturing the full output:**
   - the minimal method: `session07_test.py` (EGLC, F16),
     `session13_test.py` (LFPG, F30), `session18_test.py` (DSM, F47),
     `session24_test.py` (YSDU, F64) and `session29_test.py` (RNO, F82);
   - the richer method: `session39_sealed_test.py` (F94);
   - the third method: `session62_reserved_confirm.py --confirm` (F109).

   Use each script's own documented invocation, as recorded in its DECISIONS
   entry or in the script itself.
4. **Compare.** Give one line per figure: recorded value, recomputed value,
   and match or MISMATCH. For each script, say whether it wrote to a path
   that is committed in the working repo. The write happens in the clone,
   but record it for triage.
5. **Determinism.** Record any random seed or determinism setting each
   script uses, as read from the code. Do not re-run to test determinism.

## Step 3 — Rebuild a small sample of features from the raw GRIB (in the clone)

The aim is to check that the processed feature CSVs are correct builds from
the raw GRIB. Step 2 only proves results reproduce from those CSVs, so this
step closes that gap.

1. **Make the cache available to the clone.**
   - Symlink or point the clone at the working repo's `data/raw/grib/`,
     read-only. If the scripts use other gitignored raw folders, treat those
     the same way.
   - Confirm that nothing in the working repo's cache is modified. Compare
     the file count and a checksum of the listing before and after the step.
2. **Choose the sample.**
   - Pick the dates with a fixed rule, stated before building: the first,
     middle and last day of each window. The windows are:
     - training, 2021-03-24..2024-07-31;
     - reserved, 2024-08-01..2025-07-31;
     - sealed, 2025-08-01..2026-07-31.
   - Use all five airports, which gives 45 station-days.
   - If a chosen date is missing from the cache, or was dropped by the
     recorded failure logs, take the next available day. Report the
     substitution.
3. **Which features to cover:**
   - B's five GRIB-derived values, from the session 37/40 build: forecast
     temperature, with the elevation correction as built, `cloud_cover` and
     `wind_speed_10m`;
   - L, D, T and R from the family builds: the session 49/51/53/55 files
     for training and sealed dates, and the session 63 reserved files for
     reserved dates.
   - The season features are simple date arithmetic. Check them, but note
     that they are not built from the GRIB.
4. **Use the committed code, not a re-implementation.**
   - Import and call the committed pull, decode and derive functions from
     the clone's scripts on the sampled files. Wrap them in a harness that
     selects the dates; do not change the logic.
   - If a script cannot be called for a subset without editing it, report
     that and choose one of these, stating which:
     - (a) run that stage's full build in the clone, but only if it needs no
       network and the run time is reasonable (say so if it is over about 30
       minutes);
     - (b) skip that stage, and record it as not rebuilt.
   - Do not re-implement a derivation to compare against. That would test
     the new code, not the committed build.
5. **Compare** each rebuilt value against the processed CSV value for the
   same station, date and column.
   - Pre-registered tolerance: agreement to the CSV's stored precision.
     State that precision per column.
   - Report every value, grouped by feature, as match or MISMATCH with
     both numbers.

## The report: `notes/audit-session-68a.md`

1. **Summary.** The gate result, and counts of matches and mismatches for
   Step 2 and Step 3. Findings are counted by severity as before (must-fix,
   should-fix, cosmetic, uncertain).
2. **Pre-registered comparison list** (Step 2.2) and the sample rule
   (Step 3.2).
3. **Step 2 results**, one line per figure.
4. **Step 3 results**, grouped by feature.
5. **Findings as a plain list**, one block each:

   ```
   A68a-nn | severity | file:line
   evidence: ...
   suggested fix: ...
   ```

6. **Clean checks**, listed explicitly.
7. **Appendix.** Harness sources and raw outputs. For long outputs, give a
   summary plus the path under `/tmp`.

## End of session

1. Paste into chat, **as plain text with no tables**:
   - the gate result;
   - the summary;
   - every MISMATCH line, if any;
   - the findings list;
   - any stage that was not rebuilt.
2. Overwrite STATUS.md as a current-only snapshot. It should say:
   - sessions 66, 67 and 68a are done, with their report paths;
   - 68b is next;
   - Q30 is deferred;
   - Q32 is unchanged.

   It must end with a "Next planning session" line: owner review of the
   session-68a report, then drafting session 68b (logic and leakage review
   of the headline pipeline), using the session-67 map and any 68a
   mismatches.
3. Run `git status` and show that only `notes/audit-session-68a.md` (new),
   DECISIONS.md (D61) and STATUS.md changed in the working repo.
4. Write a suggested commit message. Do not commit anything.
