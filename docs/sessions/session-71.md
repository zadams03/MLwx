# Session 71 — rebuild L, D, T and R for the audit's 45 station-days (A68a-01)

**Type:** network, data only. **Assigned by:** DECISIONS D62.3(c), D62.5, D62.8.

## Why

Audit 68a rebuilt 315 of 315 sampled `B` values from the raw GRIB (D62.1),
but could not check the four selected features L, D, T and R. Their build
scripts fetch, decode and delete the bytes in one step, so nothing was left
to check offline (A68a-01). This session fetches the bytes again for the
same 45 station-days, rebuilds L, D, T and R, and checks them against the
committed values.

## Standing rules for this session (D62)

- Data only. No model is fit and nothing is scored. No MAE, skill or
  verdict figure is computed or printed.
- The pull date and exact query are recorded with every raw file (SPEC 2.3).
- No file is deleted. No existing file under `data/raw/` is changed.
- No frozen script is edited (`session39_sealed_test.py`,
  `session48_reserved_year.py`, `session60_combine_design.py`,
  `session62_reserved_confirm.py`). **No existing script of any kind is
  edited**, including the L, D, T and R build scripts.
- SPEC.md, RESULTS.md, README.md and CLAUDE.md are not edited.
- A mismatch is a finding. Report it; do not fix it, re-tune anything, or
  change the sample to make it pass.

## Scope

### Step 1 — Recover the sample and the recipe (read only, no network)

1. Read `notes/audit-session-68a.md`, in particular A68a-01 and section 4.2.
   Recover the **exact** 45 station-days audit 68a sampled. Print them as a
   table (station, target date, and which committed file(s) hold that row).
   **If the list cannot be recovered exactly from the repo, stop here and
   report.** Do not choose a new sample.
2. Read the build scripts for L, D, T and R (the session 49, 51, 53 and 55
   scripts, and the session 63 reserved-window build, SPEC 8.1, F107). Use
   them **only as the recipe**: which GRIB fields, levels, cycles and leads;
   grid points and interpolation; any elevation correction; how each feature
   is derived (L's `t2 - t850`, D's dew-point depression, T's 3-hour
   tendency, R's 2-hour DSWRF window and de-accumulation at the lead-24
   airports, F102). Write the recipe out in plain words, per feature, in the
   output, with the script line numbers it came from. If any part is
   ambiguous, stop and report rather than guess.
3. List every GRIB message needed (URL, byte range source, field, level,
   cycle, lead) and print the total count and an estimated download size.
   Then continue.

### Step 2 — Pull (network)

- Fetch each message by byte range from the same source the build scripts
  used (`noaa-gfs-bdp-pds`, SPEC 7.2), using the `.idx` files to find the
  ranges, as those scripts do.
- Save each message under `data/raw/grib/session71/` (gitignored by D47).
  Beside each one, write a `.meta.txt` sidecar with the URL, the byte range,
  the pull time in UTC, the file size and its SHA-256.
- A failed fetch gets one retry. A message that still fails is logged and
  its values are counted as missing — never filled (SPEC 2.2).
- Write a committed manifest (one row per message, sorted, the same fields as
  the sidecars) and a failure log to `data/raw/diagnostics/session71/`.
- Run `git check-ignore` on a sample of the cached files (must be ignored)
  and on the manifest and failure log (must not be).

### Step 3 — Independent rebuild (the verdict)

- New script: `scripts/session71_ldtr_rebuild.py`. Write **new** decode and
  derivation code from the Step 1 recipe. Do not import or copy functions
  from the build scripts. It reads only the cached bytes from Step 2 — no
  network — so it can be re-run offline.
- Rebuild, for each of the 45 station-days, the four committed columns
  `lapse_rate_t2_t850`, `dewpoint_depression_t2m` (the unfloored committed
  column, not the SPEC 8.1 transform), `pressure_tendency_3h_hpa` and
  `dswrf_2h_wm2`. Where the committed files also carry the intermediate
  columns these are built from (for example `t850`, `t925`, `t700`, the dew
  point, the two pressures), rebuild and check those too, and report them
  separately.

### Step 4 — Compare

- Compare each rebuilt value with the value in every committed file that
  holds that station-day (the session 49/51/53/55 v16 and sealed windows,
  and the session 63 reserved windows, SPEC 8.1).
- **Pass rule: an exact match at the recorded precision.** Round the rebuilt
  value to the number of decimals stored in that column of that file, and
  compare it with the stored value. There is no tolerance.
- Report: the per-feature and per-airport pass counts (for example "L: 45 of
  45"); the total over the four features (out of 180); the intermediate
  columns separately; and, for any mismatch, the station, date, file,
  column, stored value, rebuilt value and difference.

### Step 5 — Diagnostic only: the original functions on the same bytes

This step does not decide anything; Step 4 is the verdict. Run it only if the
original build scripts' decode/derive functions can be imported **without
editing any script** and **without triggering a network call, a file write
or a file delete**. If so, run them on the Step 2 cached bytes and report how
their output compares with (a) the Step 3 rebuild and (b) the committed
values. This separates a bytes difference from a logic difference. If the
functions cannot be used safely that way, skip this step and say why.

## End of session

1. Save the full real output to `notes/session-71-output.txt` and paste the
   real numbers (not a description) in chat.
2. Append one DECISIONS.md entry at the next free number (check the live
   file and the archive; F110 is expected). It records the sample, the
   recipe, the pull (message count, failures, pull dates), the pass counts,
   every mismatch, the Step 5 result, and what the session did not do.
3. Overwrite STATUS.md as a pruned, current-only snapshot. It must end with
   a "Next planning session" line. If Step 4 is 180 of 180, that line is: the
   owner chooses a Q30 branch (D62.8). If there is any mismatch or missing
   value, that line is: the owner triages the session 71 finding before Q30.
4. Consistency check: re-read CLAUDE.md, SPEC.md, STATUS.md and DECISIONS.md
   and report anything that disagrees, any duplicated heading and any entry
   out of order. Report only.
5. Archive step: move any DECISIONS entries that meet the D46 criterion, verbatim
   and mechanically. Report what moved and why, or that nothing did.
6. Checks: `git status --porcelain` output; confirm that no `.grib2` file is
   staged or untracked, that no existing file changed except STATUS.md and
   DECISIONS.md (and DECISIONS-archive.md if step 5 moved anything), and that
   no file was deleted.
7. Write a suggested commit message. **Do not commit.** Stop and wait for
   review.
