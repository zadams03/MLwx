# Session 95: D87, download and check all 65 months of the stage C pull

Session 94 (the whole-file fallback, F136) is reviewed, committed and
pushed. The owner then ran 2022-11 alone on GitHub Actions; its verify
step passed and it was published. The Release `stagec-grib-pull-v1`
now holds all 195 assets (65 months x 3), so the f000 to f024 pull is
complete. Only 2022-01 has been downloaded and checked locally (F134).
This session:

1. records **D87** (the owner's decisions), before any other edit or
   any network call;
2. lists the Release and **downloads** every month not yet held locally
   into `MLwx-pull/`, checking each file against the Release digest
   (Steps 2 and 3);
3. checks every month's **meta** and runs the **verifier** (13 checks
   and `--ranges`) on all 65 months (Step 4);
4. checks the **totals across all months** against the full plan, and
   that the "ok (whole file)" messages are exactly F135's 27 files
   (Step 5);
5. runs the **extended gate** on every month at EGLC, LFPG and DSM
   (Step 6);
6. writes a committed **inventory** of the Release (Step 7);
7. records what it found as **F137**, and does the end-of-session steps.

It does not run the workflow, push, change the Release, or pull any
GRIB.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements for
  new code.
- **Nothing from 2026-27.** No GFS request at all. Nothing valid after
  2026-07-31T23:00 UTC is read.
- **Network.** Only: unauthenticated reads of the GitHub REST API for
  this repository's Release, and unauthenticated downloads of that
  Release's own assets (each asset's `browser_download_url`, following
  GitHub's redirect). No other host. No GRIB request.
- **No observations.** Read no observation file and no IEM data. From
  `session81_training_set.csv` read only the columns the verifier's
  `--gate` already reads (F134.4: an explicit list of nine columns).
- **No scores.** Compute no error, MAE, bias or skill of anything.
- **No forecast value printed**, except: per-field minimum and maximum
  from `--ranges` and Step 5.4, and, if the gate finds a mismatch, that
  row's new and committed values in full.
- **No accounts or credentials.** No token, no `gh`, no sign-in.
- **No installs.** Use what is installed.
- **No push, no workflow run, no Release change.**
- **`MLwx-pull/`** (`/Users/zacharyadams/Coding Projects/MLwx-pull/`,
  outside the repo): the only change allowed is adding the downloaded
  asset files. Never modify, overwrite, move or delete an existing file
  there, including the three 2022-01 files. Download each file to a
  temporary name in `MLwx-pull/` and rename it to its asset name only
  after its SHA-256 equals the Release digest; delete any temporary
  file left at the end.
- **Negative tests** (Step 5.5) work on copies in one temporary
  directory outside the repo (`mktemp -d`), deleted at the end.
- **Writes.** Only: the new script `scripts/session95_check_release.py`;
  the new files `data/processed/session95_pull_inventory.csv` and its
  `.meta.txt`; the asset files in `MLwx-pull/`;
  `notes/session-95-output.txt`; and the DECISIONS.md and STATUS.md
  edits the steps give. No other file under `data/` is created or
  changed. Do not touch `data/models/`.
- **Do not edit any existing script**, including
  `scripts/session91_grib_pull.py` and `scripts/session92_verify_chunk.py`.
  The new script may import from them, or call the verifier as a
  subprocess, so the plan, the checks and the gate arithmetic stay
  identical.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- Keep the laptop awake for the long steps (D86.5), for example by
  running them under `caffeinate -i`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-95.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D86 and F136, and that
   no D87 or F137 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm `scripts/session95_check_release.py` and
   `data/processed/session95_pull_inventory.csv` do not exist. Check
   SHA-256 of: `scripts/session91_grib_pull.py` and
   `scripts/session92_verify_chunk.py` against F136;
   `.github/workflows/stagec-grib-pull.yml` against F134 and F136
   (`804b6d35...02a6`); `data/processed/session91_pull_airports.csv`
   against F133; `data/processed/session81_training_set.csv` against
   F122.3. Any difference: stop and report.
4. List `MLwx-pull/` with sizes. Expected: exactly the three 2022-01
   files, with F134.1's SHA-256. Anything else: stop and report.
5. Report free disk space on the volume holding `MLwx-pull/`. If it is
   under 5 GB, stop and report.
6. Read: D83, D84, D86, F133 to F136 in DECISIONS.md; SPEC 3.4 and 8.7;
   `scripts/session91_grib_pull.py` and `scripts/session92_verify_chunk.py`
   in full.
7. Print the installed Python and package versions you use.

---

## Step 1: record D87 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 95 decision: F136 accepted, the 2022-11 run, and the all-months check (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D87. Owner decisions, planning chat (after session 94): F136
accepted, the 2022-11 run, the pull complete, and the all-months
check.** Written at the start of session 95, before any other edit or
network call. No 2026-27 value has been read or scored.

- **D87.1 F136 accepted.** The owner accepts F136 and all twelve
  F136.8 readings.
- **D87.2 A note on session 94's Step 0.** `docs/session-94.md` was
  written before session 93 was committed, so it was committed with
  session 93 and session 94's Step 0 found a clean tree (F136.1).
  Harmless; nothing else was affected.
- **D87.3 The 2022-11 run.** After session 94 was committed and
  pushed, the owner ran 2022-11 alone on GitHub Actions with the
  whole-file fallback. The verify step passed 13 of 13 checks and the
  month was published. Statuses (owner's report from the job log): ok
  29,370; absent by design 360; ok (whole file) 270; idx missing 0;
  check failed 0. The owner reports the 270 messages are exactly
  F135's 27 broken files, so 2022-11-29T12 (flagged by dynamical.org,
  F131.2) was not affected. Session 95 confirms this from the files.
- **D87.4 The pull is complete.** The Release "Stage C GRIB pull"
  (`stagec-grib-pull-v1`) holds all 195 assets (65 months x 3). Its web
  page shows 197 because GitHub adds two "Source code" archives. The
  stage C f000 to f024 pull is complete.
- **D87.5 Session 95 checks all 65 months.** It downloads every asset
  not held locally into `MLwx-pull/` (outside the repo), checks each
  against the Release digest and its meta, runs the verifier on every
  month, checks the totals against the full plan, and runs the
  extended gate on every month at EGLC, LFPG and DSM (lead 24). It
  writes a committed inventory of the Release,
  `data/processed/session95_pull_inventory.csv`.
- **D87.6 GFS v17 (planning-chat check, 2026-10-05, not checked by
  this session).** The NWS notices page lists SCN 26-88 (2 October
  2026) as the newest Service Change Notice; none is for GFS v17. With
  30 days' notice, the earliest go-live is about 4 November 2026.
```

---

## Step 2: the Release

GitHub REST API, unauthenticated, for `zadams03/MLwx`, tag
`stagec-grib-pull-v1`. Page the asset list if needed. Report the number
of API requests used.

1. Report the Release's title, draft and prerelease flags, and asset
   count. Expected: 195 assets. Check: every plan month 2021-03 to
   2026-07 has exactly its three files (`gfs_points_<m>.csv.gz`,
   `manifest_<m>.csv.gz`, `chunk_<m>.meta.txt`); no asset is named for
   a month outside the plan; no other asset; every asset's state is
   "uploaded"; every asset has a `digest`. Any difference: stop and
   report.
2. The three 2022-01 assets' sizes and digests must still equal F134.1
   and the local files. Any difference: stop and report.
3. Report the total size, and by file kind, against F135.2's 192-asset
   totals.

---

## Step 3: download

In `scripts/session95_check_release.py`, download each of the 192
assets not held locally (every month but 2022-01) into `MLwx-pull/`:

1. Download to a temporary name; check its size and SHA-256 against
   the Release; only then rename it to the asset name. On a mismatch or
   a network error, retry at most twice. A file that still fails: stop
   and report.
2. Never overwrite an existing file. If a target name already exists,
   stop and report.
3. Report: files downloaded, bytes, time, retries. At the end, list
   `MLwx-pull/` and confirm it holds exactly 195 files, every one's
   SHA-256 equal to its Release digest, and no temporary file.

---

## Step 4: every month's meta and the verifier

For each of the 65 months:

1. **Meta.** Its two data-file SHA-256 values equal the local files';
   its positions SHA-256 equals the committed positions file's; its
   arguments are `--chunk --month <m> --hours 0-24`. Report its script
   SHA-256. Expected: 2022-11 has F136's `b52ffc2e...2f1f`; every other
   month has F133's `72c263b2...652e`. Any other value: report it and
   stop. Report per month (table in the output file): run start and
   end, chunk seconds, workers, retries, HTTP 404 count, bytes
   downloaded, whole-file requests and bytes where the meta records
   them, and the Python, eccodes and ecCodes library versions.
2. **Verifier.** Run `scripts/session92_verify_chunk.py --dir <MLwx-pull>
   --month <m> --hours 0-24` (the edited verifier, F136). Report per
   month: exit code, checks passed of 13, and the "idx missing" and
   "ok (whole file)" counts. Any month with a failed check: report it
   in full and stop.
3. **Ranges.** Run `--ranges` on every month. Report per month the
   count of values outside the bounds and the read-back mismatch count
   (both expected 0), and per field the overall minimum and maximum
   across all months. Any value outside the bounds or any read-back
   mismatch: report it (month, cycle, hour, field, airport) and stop.

---

## Step 5: totals across all months

In the new script, using the plan logic imported from
`session91_grib_pull.py` for the whole window (not typed in):

1. The union over all 65 months equals the full plan, by key set and by
   count: cycles, files (cycle and hour), manifest rows (cycle, hour,
   field), messages (not absent by design), points rows (cycle, hour,
   airport). F133.5 gives 7,828 cycles, 195,600 files and 1,932,528
   messages; points rows are expected to be 9,975,600 (195,600 x 51).
   If the plan's own numbers differ, report both and use the plan's.
2. No key appears in more than one month, and every key sits in the
   month of its cycle's initialisation date (D83.5(b)).
3. Status totals across all months: ok, ok (whole file), absent by
   design, idx missing, check failed. Expected: ok (whole file) exactly
   270; check failed 0.
4. **The whole-file messages.** The set of (cycle, hour) with any "ok
   (whole file)" message must equal F135.3's 27 broken files exactly:
   2022-11-29T18 f002, f003, f009, f011, f012, f013, f017, f018, f022,
   f023, f024; 2022-11-30T00 f002, f005, f007, f008, f010, f011, f013,
   f016, f020; 2022-11-30T06 f002, f003, f004, f005, f007, f020, f024.
   Each of these files has all ten fields "ok (whole file)", and no
   other message anywhere has that status. Confirm every 2022-11-29T12
   message is ok. Report per field the minimum and maximum of the
   whole-file values, beside 2022-11's minimum and maximum for its
   normal ok values, using `--ranges`' bounds (count outside expected
   0).
5. **Negative tests** of the new script, on copies in the temporary
   directory: (a) one copied file with one byte changed must fail the
   digest check; (b) the totals check run with one month's manifest
   left out must fail on the missing keys. Report each.

---

## Step 6: the extended gate, every month

Run the verifier's own `--gate` (F134.4, F136.8 reading 9) on every
month: EGLC and LFPG 12z lead 24, DSM 18z lead 24, every target date
whose cycle lies in that month. Exact equality, no tolerance.

1. Report per month and in total: station-days compared, equal,
   mismatched, with no committed row, and not rebuilt; and a pass table
   by column and by airport over all months.
2. **Not rebuilt.** The last target date, 2026-08-01, needs valid times
   after 2026-07-31T23, which the pull does not hold. If the gate
   reports those station-days (2026-07 only) as not rebuilt for that
   reason alone, record them as outside the window, not a failure, and
   list them. Any other station-day not rebuilt: report it and stop.
3. **No committed row** is not a failure; report the count per airport
   and list the dates in the output file. Report whether any gated
   station-day uses an "ok (whole file)" message, and if so whether it
   had a committed row.
4. **If any value differs, report it in full and stop. Do not change
   the arithmetic to make it pass.**
5. YSDU, RNO and KSFO use lead 26, which an f000 to f024 extract does
   not hold, so they are not gated. The 45 other airports have no
   committed record. Say both in F137.

---

## Step 7: the inventory

Write `data/processed/session95_pull_inventory.csv`: one row per
Release asset, 195 rows, sorted by month then file name, with columns
`month`, `asset`, `bytes`, `sha256` (equal to the Release digest and
the local file), `script_sha256` and `run_start_utc` (both from that
month's meta). Write it so equal content gives equal bytes. Write
`data/processed/session95_pull_inventory.csv.meta.txt` in the style of
the positions file's meta: what it is, the Release tag, the date the
Release was read, the script that wrote it and its SHA-256, and the
row count. Report both files' SHA-256.

---

## Step 8: records

1. **F137** in DECISIONS.md, after D87, under
   `## <run date>: Session 95 finding: all 65 months downloaded and checked`.
   Real findings only: Step 0; the Release (Step 2); the download;
   the meta and verifier results; the ranges; the totals and the
   whole-file check; the negative tests; **the extended gate result**
   and what is not gated; the inventory and its SHA-256; the new
   script's SHA-256; requests and bytes; readings made where this
   prompt is silent, listed for the owner; and a "what this did not
   do" list (no GRIB request; no observation read beyond the gate's
   columns; no score; nothing from 2026-27; no forecast value printed
   beyond the ranges and any gate mismatch; no push, workflow run or
   Release change; no token; nothing in `MLwx-pull/` changed except
   the added assets; no file under `data/` changed except the two new
   inventory files; no existing script edited; nothing installed;
   nothing committed). Keep it compact; full listings go in the output
   file.
2. Save the full real output as `notes/session-95-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended), keeping session 94's structure, updated: the pull is
   complete and all 65 months are downloaded and checked (or not), with
   the gate result (D87, F137); 2022-11 is no longer pending; F136.8's
   readings are accepted (D87.1), so that open question is removed;
   GFS v17: D87.6 replaces D84.6 as the latest check. STATUS must end
   with: "**Next planning session:** Review session 95. If it passed,
   the owner commits and pushes; then plan stage C's next step (the
   open build choices of D82.5 and what they need first). Re-check GFS
   v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only, in chat and in `notes/session-95-output.txt`.
4. Archive step, per CLAUDE.md. D72, D73, F122, D77 to D87 and F127 to
   F137 stay live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted, confirm `MLwx-pull/`
   holds exactly the 195 assets with their Release SHA-256 and nothing
   else, and run `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
