# Session 92: D84, verify the 2022-01 Actions extract, and a verify step in the pull workflow

Session 91 built and gated the stage C GRIB pull (F133); it is reviewed,
committed and pushed. The owner then ran month 2022-01 on GitHub
Actions: it succeeded, and the Release holds its three files, which the
owner downloaded to `/Users/zacharyadams/Coding Projects/MLwx-pull/`
(outside the repo). This session:

1. records **D84** (the owner's decisions), before any other edit or any
   network call;
2. checks the 2022-01 files' **integrity** against the Release and their
   meta (Step 2);
3. writes a **chunk verifier** script and checks the 2022-01 extract's
   **completeness and values** against the plan (Steps 3 and 4);
4. runs an **extended gate** on the whole month at the lead-24
   development airports (Step 5);
5. measures **speed and size** and projects the rest of the pull (Step 6);
6. adds the verifier to the **workflow** as a step before upload, so a
   bad month is never published (Step 7, D84.4);
7. records what it found as **F134**, and does the end-of-session steps.

It does not run the workflow, push, or start any further month. The
owner does that after review (D84.5).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements for
  new code.
- **Nothing from 2026-27.** No GFS request at all this session, and
  nothing valid after 2026-07-31T23:00 UTC is read.
- **No GRIB downloads.** The only network use is unauthenticated reads of
  the GitHub REST API for this repository's Release (Step 2). No other
  host.
- **No observations.** Read no observation file and no IEM data. From
  `session81_training_set.csv` read only the key columns and the seven
  gate columns (Step 5), with an explicit column list; never load an
  observation or target column.
- **No scores.** Compute no error, MAE, bias or skill of anything.
- **No forecast value printed**, except: per-field minimum and maximum in
  Step 4, and, if the gate finds a mismatch, that row's new and committed
  values in full.
- **No accounts or credentials.** No token, no `gh`, no sign-in.
- **No installs.** Use what is installed.
- **No push, no workflow run, no Release change.**
- **The 2022-01 files are read-only.** Never modify, move or delete
  anything in `/Users/zacharyadams/Coding Projects/MLwx-pull/`. Negative
  tests (Step 4.3) work on copies in one temporary directory outside the
  repo (`mktemp -d`), deleted at the end.
- **Writes.** Only: the new file `scripts/session92_verify_chunk.py`; the
  edit to `.github/workflows/stagec-grib-pull.yml` that Step 7 gives;
  `notes/session-92-output.txt`; and the DECISIONS.md and STATUS.md
  edits the steps give. No file under `data/` is created or changed.
  Do not touch `data/models/`.
- **Do not edit any existing script**, including
  `scripts/session91_grib_pull.py`. The verifier may **import** from
  `scripts/session91_grib_pull.py` (it is the pull itself, so importing
  keeps the plan and the gate arithmetic identical) or copy from it,
  citing lines.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-92.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D83 and F133, and that no
   D84 or F134 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm `scripts/session92_verify_chunk.py` does not exist. Check
   SHA-256 against F133 of: `scripts/session91_grib_pull.py`,
   `.github/workflows/stagec-grib-pull.yml`,
   `.github/grib-pull-requirements.txt` and
   `data/processed/session91_pull_airports.csv`; and of
   `data/processed/session81_training_set.csv` against F122.3. Any
   difference: stop and report.
4. List `/Users/zacharyadams/Coding Projects/MLwx-pull/` with sizes.
   Expected: `gfs_points_2022-01.csv.gz`, `manifest_2022-01.csv.gz`,
   `chunk_2022-01.meta.txt`. If any is missing or named differently,
   stop and report. Report any other file there, and do not use it.
5. Read: D47, D83, F128.2, F133 in DECISIONS.md; SPEC 3.4, 7.2, 8.7 and
   8.8; `scripts/session91_grib_pull.py` in full; the workflow in full.
6. Print the installed Python and package versions you use.

---

## Step 1: record D84 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 92 decision: F133 accepted, the first Actions month, and the bad-month check (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D84. Owner decisions, planning chat (after session 91): F133
accepted, the f025 to f048 start cycle, the first Actions month, the
bad-month check, the next run, and GFS v17.** Written at the start of
session 92, before any other edit or network call. No 2026-27 value
has been read or scored.

- **D84.1 F133 accepted.** The owner accepts F133 and all fourteen
  F133.9 readings.
- **D84.2 The f025 to f048 pull starts at cycle 2021-03-22T12.** GFS
  v16 began with the 12z run of 2021-03-22 (NWS SCN 21-20, updated, 18
  March 2021). Cycles 2021-03-22T00 and T06 are GFS v15 and are not
  used. This settles F133.9's note.
- **D84.3 The first Actions month.** After session 91 was committed
  and pushed, the owner ran month 2022-01 on GitHub Actions. The run
  succeeded in 8 min 25 s (the run time GitHub shows). The Release
  "Stage C GRIB pull" holds its three files, which the owner downloaded
  to `/Users/zacharyadams/Coding Projects/MLwx-pull/`, outside the
  repo. Session 92 verifies them (D83.5(g)).
- **D84.4 The bad-month check (owner's choice, option b).** Today a
  month whose messages are mostly "check failed" would publish with
  empty values (never filled, but not flagged). So a verifier runs in
  the workflow after the chunk and before upload. It fails the month,
  and nothing is published, if: any count differs from the plan
  (cycles, files, messages, rows); any message is "check failed"; any
  message is "absent by design" other than DSWRF, TMAX and TMIN at
  f000, or any of those is not; any key is duplicated; an ok message
  has an empty or non-finite value; a non-ok message has any value; or
  the meta's SHA-256 values do not match the files. "idx missing"
  messages do not fail the month: they are published, left empty, and
  their count is printed in the job log. Because the pull is
  resumable, a failed month is retried by starting the run again.
- **D84.5 The next run.** After session 92 is reviewed and committed,
  the owner runs month 2021-03 alone: it is the partial first month
  (from 2021-03-23T00, 840 files) and the first live test of the
  verify step. If it succeeds and its verify step passed, the owner
  starts 2021-04 to 2026-07 (2022-01 is already published and is
  skipped).
- **D84.6 GFS v17 (planning-chat check, 2026-10-04, not checked by
  this session).** The planning chat could not load the NWS notices
  page; a web search found no GFS v17 Service Change Notice. EMC's
  GFSv17 evaluation page (last updated 5 June 2026) gives the
  implementation as Q1 FY27 (October to December 2026). With 30 days'
  notice, the earliest go-live is about 3 November 2026.
```

---

## Step 2: integrity against the Release and the meta

1. SHA-256 and size of the three local files.
2. Read `chunk_2022-01.meta.txt` in full and put it in the output file.
   Check: its two data-file SHA-256 values equal the local files'; its
   script SHA-256 equals F133's final script SHA-256; its positions
   SHA-256 equals the committed positions file's; its arguments are
   `--month 2022-01 --hours 0-24` (report the workers used). Report the
   Python and package versions it records.
3. GitHub REST API, unauthenticated: read the Release for this
   repository (`zadams03/MLwx`) with tag `stagec-grib-pull-v1` (F133.4).
   Report its title and its assets (name, size, and `digest` where the
   API gives one). Check the three assets' sizes and digests equal the
   local files'. If the API gives no digest, report that and compare
   sizes only. Any difference: stop and report.

---

## Step 3: the chunk verifier

Write `scripts/session92_verify_chunk.py`. It must:

1. Take `--dir DIR --month YYYY-MM --hours A-B` and verify that month's
   three files in `DIR`. Standard library only (plus what
   `session91_grib_pull.py` itself imports), so it runs in the workflow
   with the pinned install.
2. Take the expected counts from the session 91 plan logic (imported or
   copied), not typed in: cycles, files, messages, and the
   absent-by-design set.
3. Apply exactly D84.4's fail rules, each as a named check, printing for
   each check its expected and found counts and PASS or FAIL. Print the
   "idx missing" count. Exit with status 0 only if every check passes.
4. Read the manifest and points files fully; reconcile them (a points
   row's cells for a field are filled exactly when that cycle, hour and
   field's manifest status is ok).
5. Have a separate `--ranges` option (local use only, never a fail
   rule) that prints, per field, the count of values, the minimum and
   maximum, and the count outside these broad bounds: t2m, d2m, t850,
   tmax2m, tmin2m 150 to 350 K; tcdc 0 to 100 %; u10, v10 -100 to 100
   m/s; prmsl 85,000 to 110,000 Pa; dswrf 0 to 1,500 W/m2. It also
   checks every value cell reads back with `float` and `repr` to the
   identical string (D83.5(c)) and reports the count that do not.

If the files' layout or the manifest's way of recording "idx missing"
makes any D84.4 rule ambiguous, stop and report.

---

## Step 4: verify 2022-01

1. Run the verifier on the 2022-01 files with `--hours 0-24`. Expected
   from the plan: 124 cycles, 3,100 files, 30,628 messages (124 x 247),
   372 "absent by design", 158,100 points rows (3,100 x 51). Report
   every check. Confirm these expected numbers equal the plan's own
   output; if the plan gives different numbers, report both and use the
   plan's.
2. Run `--ranges` and report it.
3. **Negative tests** on copies in the temporary directory. Each must
   make the verifier exit non-zero with the right check failing, and
   the untouched copy must pass:
   (a) one manifest row's status changed to "check failed";
   (b) one points row deleted;
   (c) one points row duplicated;
   (d) one value cell emptied in an ok message;
   (e) one value cell filled in an "absent by design" message;
   (f) one manifest row's status changed from "absent by design" to ok;
   (g) the meta's points SHA-256 changed by one character.
   Copies are re-gzipped as the script writes them; for (a) to (f) also
   update the copied meta's SHA-256 values so only the intended check
   fails. Report each result.

---

## Step 5: the extended gate (whole month, lead-24 airports)

Using the session 91 gate arithmetic (imported from, or copied with
lines cited from, `session91_grib_pull.py`; same operation order as
F133.7), rebuild the seven columns `temperature_grib_c`, `cloud_cover`,
`wind_speed_10m`, `dewpoint_depression_t2m_floored`,
`lapse_rate_t2_t850`, `pressure_tendency_3h_hpa` and `dswrf_2h_wm2` at
the three lead-24 development airports, at each airport's own cycle and
lead (F128.2: EGLC and LFPG 12z lead 24; DSM 18z lead 24), for every
target date whose cycle lies in 2022-01: target dates 2022-01-02 to
2022-02-01, so up to 93 station-days.

- Compare with `session81_training_set.csv`, exact equality, no
  tolerance. Report a pass table by column and by airport.
- Report separately: station-days with no committed row (not a failure)
  and station-days that could not be rebuilt because a needed message
  is not ok (must be 0; otherwise report which).
- **If any value differs, report it in full and stop. Do not change the
  arithmetic to make it pass.**
- YSDU, RNO and KSFO use lead 26, which an f000 to f024 extract does not
  hold, so they are not gated here. Say so in F134.
- This is the first check that the Linux ecCodes build on Actions
  decodes exactly as the owner's Mac did.

---

## Step 6: speed and size

From the meta (and D84.3's 8 min 25 s, which includes job setup):
seconds of the chunk itself, files per second, bytes downloaded and MB
per second, kept size of the three files. Then project, **marked as
estimates**: the remaining 64 months at four in parallel (D83.5(f)),
total wall time, total bytes downloaded, total kept size, and the
Release's asset count when complete (65 x 3). Use each month's own file
count from the plan, not 2022-01's for every month. Compare with F133.8's
estimates.

---

## Step 7: the verify step in the workflow

Edit `.github/workflows/stagec-grib-pull.yml` only to add one step in the
per-month job, after the chunk step and before any Release creation or
upload: run
`python scripts/session92_verify_chunk.py --dir <the chunk's out dir> --month <m> --hours 0-24`.
If it exits non-zero the job fails and nothing is uploaded. Change
nothing else in the workflow. Show the diff in full. If PyYAML is
installed, parse the workflow and report it valid; otherwise report
"not parsed". Report the new SHA-256. The step itself is first tested
live by the owner's 2021-03 run (D84.5).

---

## Step 8: records

1. **F134** in DECISIONS.md, after D84, under a dated heading
   `## <run date>: Session 92 finding: the 2022-01 Actions extract and the verify step`.
   It gives, with real findings only:
   - the Step 0 to 2 results (local, meta and Release checks);
   - the verifier's checks on 2022-01, the ranges summary, the read-back
     count, and the negative tests;
   - **the extended gate result**, and the lead-26 airports not gated;
   - speed and size, measured, then the projection marked as estimates;
   - the workflow edit and its SHA-256, and the verifier's SHA-256;
   - every reading made where this prompt is silent, listed for the
     owner to confirm;
   - requests made (API reads only), and confirmation the temporary
     directory was deleted;
   - a "what this did not do" list: no GRIB request; no observation
     read; no score; nothing from 2026-27; no forecast value printed
     beyond the ranges summary and any gate mismatch; no push, workflow
     run or Release change; no token; nothing in `MLwx-pull/` changed;
     no file under `data/` changed; no existing script edited; nothing
     installed; nothing committed.

   Keep F134 compact: full listings go in the output file.
2. Save the full real output as `notes/session-92-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Keep what session 91's STATUS holds (end goal, roadmap,
   stage B unchanged, MOSMIX, stage C design and claim batch, not
   decided, MMMX, carried items, stage A/B uncertainties), updated:
   - the pull's state: 2022-01 published and verified (or not), the
     verify step added (D84.4), the next run 2021-03 (D84.5);
   - F133.9's readings are accepted (D84.1), so that open question is
     removed; the f025 to f048 first-cycle question is settled (D84.2)
     and removed;
   - GFS v17: D84.6 replaces D83.7 as the latest check.

   STATUS must end with: "**Next planning session:** Review session 92
   and the extended gate. If it passed, the owner commits and pushes,
   runs 2021-03 alone on GitHub Actions and checks its verify step
   passed (D84.5), then starts 2021-04..2026-07; then plan the session
   that downloads and checks all 65 months. Re-check GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-92-output.txt`** as
   well as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78, F128, D79, F129, D80, F130, D81, F131, D82, F132, D83,
   F133, D84 and F134 stay live. Report what moved and why, or that
   nothing did.
5. Confirm the temporary directory was deleted, confirm the three files
   in `MLwx-pull/` still have their Step 2 SHA-256, and run
   `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
