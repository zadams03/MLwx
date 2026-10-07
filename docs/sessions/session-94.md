# Session 94: D86, a whole-file fallback in the pull, and its gate

Session 93 found that 27 GRIB files in 2022-11 (cycles 2022-11-29T18,
2022-11-30T00 and 2022-11-30T06) have `.idx` files that do not match
them, so every byte range taken from those indexes is broken (F135).
The GRIB files themselves look whole. The owner chose to recover them
(D86.2). This session:

1. records **D86** before any other edit or network call;
2. adds a **whole-file fallback** to `scripts/session91_grib_pull.py`
   (Step 2) and teaches the verifier its new status (Step 3);
3. proves the **normal path is unchanged** (Step 4);
4. **gates** the fallback byte-for-byte against the normal path on
   healthy files, and tries it on two broken files (Step 5);
5. records **F136** and does the end-of-session steps.

It does not run the workflow or publish anything. The owner runs
2022-11 on Actions after review (D86.4).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements.
- **Nothing from 2026-27.** Only the GFS files named in Steps 4 and 5
  are requested.
- **Network.** Only `noaa-gfs-bdp-pds.s3.amazonaws.com`: `.idx` files,
  byte ranges and whole-file GETs for the files in Steps 4 and 5. No
  other host. About 2.2 GB in all.
- **No observations, no scores.** No forecast value printed, except a
  mismatch in Step 4 or 5, reported in full.
- **No accounts, credentials, installs, push, workflow run or Release
  change.**
- **Downloaded bytes are not kept**: memory only, or one temporary
  directory outside the repo (`mktemp -d`), deleted at the end.
- **Writes.** Only: the edits to `scripts/session91_grib_pull.py` and
  `scripts/session92_verify_chunk.py` that Steps 2 and 3 give; the new
  file `scripts/session94_fallback_gate.py`;
  `notes/session-94-output.txt`; and the DECISIONS.md and STATUS.md
  edits the steps give. Do not edit the workflow. Nothing under
  `data/` or in `/Users/zacharyadams/Coding Projects/MLwx-pull/` is
  changed.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**.

---

## Step 0: integrity checks

1. `git status --porcelain`. Expected: only `?? docs/session-94.md`.
   Anything else: stop and report.
2. Confirm DECISIONS.md's last entries are D85 and F135, and no D86 or
   F136 exists in DECISIONS.md or DECISIONS-archive.md.
3. SHA-256 against F134 and F135: `scripts/session91_grib_pull.py`,
   `scripts/session92_verify_chunk.py`,
   `.github/workflows/stagec-grib-pull.yml`,
   `scripts/session93_diagnose.py`. Any difference: stop and report.
4. Read D83 to D85, F133 to F135, `scripts/session91_grib_pull.py` and
   `scripts/session92_verify_chunk.py` in full. Report, citing lines,
   exactly what session 91's per-message check tests (which ecCodes
   keys, against what), and where "broken body" is raised.
5. Print the installed Python and package versions you use.

---

## Step 1: record D86 (before any other edit or any network call)

Append the code block below to the end of `DECISIONS.md`, under a dated
heading
`## <run date>: Session 94 decision: F135 accepted and 2022-11 recovered by a whole-file fallback (owner, planning chat)`,
with a `---` separator before it. Copy it **mechanically** (for example
`sed` on this file's line range) and check it byte-equal with `diff`.
Report the line range.

```
**D86. Owner decisions, planning chat (after session 93): F135
accepted, and 2022-11 recovered by a whole-file fallback.** Written at
the start of session 94, before any other edit or network call. No
2026-27 value has been read or scored.

- **D86.1 F135 accepted.** The 27 broken files in 2022-11 have `.idx`
  files that do not match them; the GRIB files themselves end in 7777
  as whole files should. The Google Cloud mirror holds identical
  copies, so option (a) of D85.4 is ruled out.
- **D86.2 Recover, do not leave empty (option c).** When a file's
  `.idx` ranges give a persistently broken body, the pull downloads
  that whole file, finds its messages by walking the GRIB headers
  (not the `.idx`), and takes all ten of the file's fields from it,
  each selected by session 91's own per-message check. Those messages
  get the new manifest status "ok (whole file)", so they stay
  visible. Option (b) of D85.4 (leave them empty) is not chosen. The
  fallback is used only for a persistently broken body; network
  errors and "idx missing" are handled as before.
- **D86.3 The gate.** Before use, the fallback must give byte-identical
  messages and identical points rows to the `.idx` path on healthy
  files, and the normal path must give identical output before and
  after the edit.
- **D86.4 The next run.** After session 94 is reviewed and committed,
  the owner runs 2022-11 alone on GitHub Actions. It is published only
  if the verify step passes. Cycle 2022-11-29T12 (flagged by
  dynamical.org, F131.2, unchecked by session 93) is covered by that
  run.
- **D86.5 Laptop sleep.** Session 93's last two cycles were only partly
  checked because the owner's laptop slept. Long local sessions run
  with the laptop kept awake.
```

---

## Step 2: the fallback in `scripts/session91_grib_pull.py`

Edit the script so that:

1. **Trigger.** When a message's byte range still gives a broken body
   (no "GRIB" at the start or no "7777" at the end) after session 91's
   retries, the file goes to the fallback instead of raising. Network
   errors, HTTP errors and missing `.idx` behave exactly as before.
2. **Whole file.** GET the whole file, with session 91's retry policy;
   check the bytes received equal its Content-Length. At most **one**
   whole file is held at a time across all workers (a lock), and in
   memory only.
3. **Walk the headers.** From byte 0: require "GRIB" and edition 2,
   read the 8-byte total length (section 0), require "7777" at that
   message's end, and step to the next. The walk must end exactly at
   the file's last byte. If any of this fails, every planned message
   of that file is "check failed" (so the verifier fails the month).
4. **Select.** For each of the file's planned fields, apply session
   91's own per-message check to every walked message. Exactly one
   must pass: that message is used, through the same decode and
   point-extraction code as the normal path, with status
   "ok (whole file)". If none or more than one passes, that field is
   "check failed". "Absent by design" fields stay so.
5. **All ten from the whole file.** Once a file falls back, all of its
   planned fields come from the whole file, including any already read
   by range.
6. **Records.** Count fallback files, their bytes, and "ok (whole
   file)" messages in the progress stats, the closing summary and the
   meta file.

If session 91's per-message check does not test enough keys to pick
exactly one message for each field (for example it does not test the
step range of TMAX, TMIN or DSWRF), stop and report. Do not widen the
check yourself.

Change nothing else. Show the full diff.

---

## Step 3: the verifier

Edit `scripts/session92_verify_chunk.py` only so that "ok (whole file)"
is a valid status, treated as ok by every value check, and its count is
printed beside "idx missing". It never fails a month by itself. Show
the full diff. Rerun the session 92 negative tests on copies of the
2022-01 files in `MLwx-pull/` (in the temporary directory) plus one
new one: a copy with one ok row's status changed to "ok (whole file)"
must pass; a copy with an invented status must still fail.

---

## Step 4: the normal path is unchanged

Write `scripts/session94_fallback_gate.py`. It loads the committed
(HEAD) version of `session91_grib_pull.py` (via `git show` into the
temporary directory) and the edited one, and runs both through their
normal `.idx` path on three healthy files: 2022-11-29T18 f000, f001
and f010. Pass rule: identical manifest rows and identical points rows
(string-equal), and no file falls back. Report it.

---

## Step 5: the fallback gate

1. **Healthy files**, 2022-11-29T18 f000 and f001: run the fallback
   path on purpose (forced, gate only). For every planned field, the
   selected message's bytes must be byte-identical (SHA-256) to the
   `.idx` range's bytes, and the points rows identical to Step 4's.
   Report the walk (message count, ends at last byte) and a table per
   field.
2. **Broken files**, 2022-11-29T18 f002 and 2022-11-30T06 f024: run the
   edited pull's normal entry point on each file and confirm it falls
   back by itself. Report: the walk; per field, the number of walked
   messages that pass the check (must be exactly one) and the status
   given. Print no values.
3. Any failure: report in full and stop. Do not change the check or
   the walk to make it pass.

---

## Step 6: records

1. **F136** in DECISIONS.md, after D86, under
   `## <run date>: Session 94 finding: the whole-file fallback and its gate`.
   Real findings only: Step 0 (including what session 91's check
   tests); the two diffs and the new SHA-256 values of the edited and
   new scripts; the verifier tests; the Step 4 and 5 results; requests
   and bytes; readings made where this prompt is silent, listed for
   the owner; and a "what this did not do" list. Keep it compact; full
   listings in the output file.
2. Save the full real output as `notes/session-94-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended), keeping session 93's structure, updated: the fallback
   (D86, F136), the 2022-11 run as next (D86.4), the open handling
   question removed. STATUS must end with: "**Next planning session:**
   Review session 94. If it passed, the owner commits and pushes, runs
   2022-11 alone on GitHub Actions and checks its verify step passed
   (D86.4); then plan the session that downloads and checks all 65
   months. Re-check GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only, in chat and in `notes/session-94-output.txt`.
4. Archive step, per CLAUDE.md. D72, D73, F122, D77 to D86 and F127 to
   F136 stay live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted and run
   `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
