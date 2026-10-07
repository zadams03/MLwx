# Session 93: D85, the Release after run 2, and a diagnosis of the 2022-11 failure

Session 92 is reviewed, committed and pushed. The owner then ran
2021-03 alone, and then 2021-04..2026-07, on GitHub Actions. The owner
reports that every month succeeded except 2022-11, which failed twice
in the pull step on a broken message body in cycle 2022-11-29T18 (D85.3).

This session is **diagnosis only**. It:

1. records **D85** before any other edit or network call;
2. checks the Release holds every month but 2022-11 (Step 2);
3. finds exactly which messages around the failure are broken, and how
   (Steps 3 and 4);
4. checks the same messages on a second NOAA mirror (Step 5);
5. records **F135** and does the end-of-session steps.

How 2022-11 is then handled is the owner's decision (D86), made after
review. This session fixes nothing, publishes nothing, and changes no
existing code.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements for
  new code.
- **Nothing from 2026-27.** Only the GFS cycles named in Step 3 are
  requested.
- **Network.** Only: (a) unauthenticated reads of the GitHub REST API
  for this repository's Release; (b) `.idx` files, HEAD requests and
  byte-range GETs on `noaa-gfs-bdp-pds.s3.amazonaws.com` for the
  Step 3 cycles; (c) the same on the Step 5 mirror, for the Step 3
  cycles only. No whole GRIB file is downloaded. No other host.
- **No observations, no scores.** No forecast value printed or decoded
  beyond what the session 91 checks themselves do.
- **No accounts or credentials.** No token, no `gh`.
- **No installs. No push, no workflow run, no Release change.**
- **Downloaded bytes are not kept.** They live only in memory or in one
  temporary directory outside the repo (`mktemp -d`), deleted at the end.
- **Writes.** Only: the new file `scripts/session93_diagnose.py`;
  `notes/session-93-output.txt`; and the DECISIONS.md and STATUS.md
  edits the steps give. Nothing under `data/` and nothing in
  `/Users/zacharyadams/Coding Projects/MLwx-pull/` is changed.
- **Do not edit any existing script or the workflow.** The diagnosis
  script may import from `scripts/session91_grib_pull.py` so that its
  byte ranges and checks are exactly the pull's.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**.

---

## Step 0: integrity checks

1. `git status --porcelain`. Expected: only `?? docs/session-93.md`.
   Anything else: stop and report.
2. Confirm DECISIONS.md's last entries are D84 and F134, and that no D85
   or F135 exists in DECISIONS.md or DECISIONS-archive.md.
3. SHA-256 against F134: `scripts/session91_grib_pull.py`,
   `scripts/session92_verify_chunk.py`,
   `.github/workflows/stagec-grib-pull.yml`. Any difference: stop and
   report.
4. Read D83, D84, F133 and F134; and `scripts/session91_grib_pull.py`
   in full, especially how it builds byte ranges from the `.idx`, how
   it retries, and what "broken body" tests.
5. Print the installed Python and package versions you use.

---

## Step 1: record D85 (before any other edit or any network call)

Append the code block below to the end of `DECISIONS.md`, under a dated
heading
`## <run date>: Session 93 decision: F134 accepted, run 2, and the 2022-11 failure (owner, planning chat)`,
with a `---` separator before it. Copy it **mechanically** (for example
`sed` on this file's line range) and check it byte-equal with `diff`.
Report the line range.

```
**D85. Owner decisions, planning chat (after session 92): F134
accepted, the remaining months run, and the 2022-11 failure.** Written
at the start of session 93, before any other edit or network call. No
2026-27 value has been read or scored.

- **D85.1 F134 accepted.** The owner accepts F134 and all nine F134.7
  readings. The workflow's header comment and the publish step's name
  still describe the old gating (F134.7 item 9); cosmetic, left as is.
- **D85.2 The remaining months.** After session 92 was committed and
  pushed, the owner ran 2021-03 alone on GitHub Actions, then
  2021-04..2026-07. The owner reports every month succeeded except
  2022-11. Session 93 checks the Release (Step 2).
- **D85.3 The 2022-11 failure.** Month 2022-11 failed in the pull
  step, twice, with "CHUNK FAILED, NOTHING WRITTEN", so nothing was
  published for it. First run: DownloadError on
  gfs.20221129/18/atmos/gfs.t18z.pgrb2.0p25.f003, bytes
  417821939-418699246, "failed after 5 retries: broken body (no GRIB
  or 7777 marker)"; files done 2895 of 3000; requests idx 2912,
  message 28599; retries 85; 463 s. Second run (the owner's rerun of
  2022-11 alone): the same error on the same cycle's f002, bytes
  419336616-420214434; files done, requests and retries identical
  (2895, 2912, 28599, 85); 534 s. Identical counts on a different
  file point to a persistent fault in that cycle rather than a
  transient network error.
- **D85.4 Session 93 is diagnosis only.** It finds which messages are
  broken and how, and whether a second NOAA mirror holds them intact.
  The handling of 2022-11 is decided after review (D86). Options the
  planning chat raised: (a) take only the broken messages from the
  mirror, if its bytes are good; (b) a new status, "broken in
  archive", for those messages, left empty and published with their
  count, as "idx missing" is.
```

---

## Step 2: the Release after run 2

GitHub REST API, unauthenticated: the Release with tag
`stagec-grib-pull-v1` (`zadams03/MLwx`). Report: asset count (expected
192 = 64 months x 3); for each month in the plan, whether its three
files are present; any month missing (expected: only 2022-11); any asset
not named for a plan month; any asset whose state is not "uploaded".
Asset names and sizes go in the output file; the summary in F135. Do
not download any asset.

---

## Step 3: which messages are broken (S3)

Write `scripts/session93_diagnose.py`. For each of the five cycles
2022-11-29T18, 2022-11-30T00, 2022-11-30T06, 2022-11-30T12 and
2022-11-30T18 (the cycles at and after the stop, which the failed runs
may not have reached), and each hour f000 to f024:

1. GET the `.idx` (report if missing). HEAD the GRIB file and record its
   Content-Length (report if missing).
2. Build each of the ten fields' byte ranges exactly as session 91 does.
   Report every range whose end is beyond the file's Content-Length.
3. For each message session 91 would request, GET its byte range once
   (no retry loop beyond session 91's own, if imported) and apply
   session 91's checks. Classify each as: ok; broken, and how (no
   "GRIB" at the start, no "7777" at the end, short body: bytes
   received vs expected); or a request error (HTTP status).
4. For each broken message, record: the first and last 16 bytes in hex;
   the GRIB edition and total length that its first 16 bytes give, if
   they start with "GRIB"; and whether the four bytes "GRIB" occur
   anywhere in the body, and at what offset. Nothing else is decoded.
5. Report a table: per cycle and hour, ok / broken / error counts; then
   the full list of broken messages (cycle, hour, field, range, kind).
   Report the total and whether it is consistent with D85.3's 85
   retries (for example, 17 broken messages x 5 tries).

If a cycle beyond 2022-11-29T18 also has broken messages, report it;
do not widen the cycles further.

---

## Step 4: the broken file in more detail

For each broken file only (a file with at least one broken message):

1. Compare the `.idx` line count with the other hours of the same cycle.
2. Check whether its messages' ranges are contiguous and end at the
   file's Content-Length (last message's end), as on a healthy file.
3. For one broken message per file, GET a window of 4,096 bytes around
   its start and report the offsets of any "GRIB" and "7777" markers in
   that window, so the review can see if the `.idx` offsets are shifted.

Report only. Do not try to repair or reinterpret any range.

---

## Step 5: the second mirror

NOAA's GFS archive is also published on Google Cloud. Try
`https://storage.googleapis.com/global-forecast-system/` with the same
path as S3 (`gfs.YYYYMMDD/HH/atmos/gfs.tHHz.pgrb2.0p25.fFFF` and its
`.idx`) for the broken files from Step 3. If that path gives 404 or an
error, report it and stop this step: do not search for other hosts.

If it is reachable, for each broken file:

1. GET the mirror's `.idx`; report whether it is byte-identical to S3's.
   HEAD the mirror's file; compare Content-Length with S3's.
2. For each message broken on S3, GET the mirror's range (from the
   mirror's own `.idx`) and apply session 91's checks. Report ok or
   broken.
3. For three messages that are ok on S3 in the same cycle, GET the same
   ranges on the mirror and report whether the bytes are identical
   (SHA-256 of each).

---

## Step 6: records

1. **F135** in DECISIONS.md, after D85, under
   `## <run date>: Session 93 finding: the Release after run 2 and the 2022-11 broken cycle`.
   It gives, real findings only: Step 0; the Release check; the broken
   message table and list; the Step 4 detail; the mirror result; the
   script's SHA-256; requests made per host and bytes downloaded;
   readings made where this prompt is silent, listed for the owner; and
   a "what this did not do" list (nothing published or pushed, no
   workflow run, no existing code changed, no file under `data/`
   changed, no value decoded beyond session 91's checks, nothing from
   2026-27, no observation, no score, nothing installed, temporary
   directory deleted, nothing committed). Keep F135 compact; full
   listings go in the output file.
2. Save the full real output as `notes/session-93-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended), keeping session 92's structure, updated: the pull's
   state (all months but 2022-11 published, per Step 2), the 2022-11
   fault (F135), and the handling decision as an open question (D85.4).
   STATUS must end with: "**Next planning session:** Review session 93
   and decide how 2022-11 is handled (D86). Re-check GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only, in chat and in `notes/session-93-output.txt`.
4. Archive step, per CLAUDE.md. D72, D73, F122, D77 to D85 and F127 to
   F135 stay live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted and run
   `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
