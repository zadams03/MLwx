# Session 72 — end-to-end clean-room rebuild of F109 at RNO, part 1 of 2: data

**Type:** network + offline build. **No model is fit and nothing is scored.**

## Why

The audit (D62) showed that every recorded figure reproduces and that the
feature inputs rebuild from raw GRIB on samples (B 315/315, L/D/T/R 180/180,
F111). It did not independently re-implement the whole chain: observations,
pairing, features, row set, model fit and MAE. The owner has chosen to do
that for one result before Q30: **F109 (`B+D,L,R,T`, reserved year) at RNO.**
- **Session 72 (this one):** write the pre-registration, pull the missing raw
  data, and build RNO's full training and test tables from the docs alone.
- **Session 73:** fit, score, and then compare every stage with the record.

## Step 0 — Pre-registration (do this first, before opening any data file)

Append the entry below to DECISIONS.md **verbatim**, dated today, as the next
free D number (D64 is expected; check the live file and the archive). Print
it. Do not change its wording. If you think any part is wrong or impossible,
stop and report instead.

> **D64. Pre-registration: clean-room end-to-end rebuild of F109 at RNO
> (sessions 72–73). Owner decision, planning chat.**
>
> **D64.1 Purpose and status.** A verification only. It re-implements the
> F109 pipeline at RNO from the documentation and compares every stage with
> the record. **It cannot change any verdict, claim or figure on record**
> (same standing as D61.4's verification re-runs). The reserved year
> (2024-08-01 to 2025-07-31) stays spent; its observations are read and it
> is scored only to reproduce F109, never to select, tune or decide
> anything.
>
> **D64.2 The target.** SPEC 8: RNO, `B+D,L,R,T`, train 2021-03-24 to
> 2024-07-31, test 2024-08-01 to 2025-07-31, the frozen LightGBM settings
> (D21.4/D48.6), the complete-case rule (8.3), and the three rungs raw GFS
> (elevation-adjusted GRIB, 5.2), persistence (on its pre-registered day
> basis, 8.5) and the model. Recorded values: F109 (RNO raw GFS 1.6135,
> persistence 2.7563, B 1.4272, B+D,L,R,T 1.2742) and the committed files
> they come from.
>
> **D64.3 Clean-room rule.** The rebuild code is written from CLAUDE.md,
> SPEC.md, DECISIONS.md, DECISIONS-archive.md and raw data only (the files
> under `data/raw/`, their sidecars, and the GRIB cache). Until session 73's
> comparison step it must not read, import or copy anything under
> `scripts/`, `data/processed/` or `notes/`, and must not use git to view
> them. Every file opened is logged. Where the docs are silent or ambiguous,
> the session records the gap as a finding, states the choice it made and the
> alternatives, and continues; it stops only if no reasonable reading exists.
> A documentation gap is itself a result of this check.
>
> **D64.4 Match rule.** Exact at the recorded precision, stage by stage:
> observations and targets, pairing and day set, each feature column, the
> complete-case row set and counts, raw GFS and persistence values, model
> predictions (where recorded), and each MAE (at F109's 4 decimals). No
> tolerance. If every input matches but the fitted model's output does not,
> that is reported as a separate category (fit determinism), not as a data
> error.
>
> **D64.5 On a mismatch.** Report it in full. Nothing is fixed, re-run to
> pass, or tuned in sessions 72–73. The owner triages any mismatch in a later
> session.
>
> **D64.6 Raw inputs.** Observations: the committed raw files. B: the
> existing GRIB cache (bytes already verified, D62.1, F111). L, D, T, R: a
> full re-pull for RNO's training and test windows, since their bytes were
> never kept (A68a-01); kept in the gitignored cache with a committed
> manifest (D47, SPEC 2.3).

## Standing rules for this session

- **Clean room (D64.3).** Keep a read log: every file path opened, in order.
  Print it at the end. Do not open `scripts/`, `data/processed/` or `notes/`.
- No model is fit. No MAE, skill, error or verdict figure is computed or
  printed. Row counts are allowed.
- No existing file is edited except DECISIONS.md and STATUS.md. No file is
  deleted. No existing file under `data/raw/` is changed. No existing script
  is edited or imported. SPEC.md, RESULTS.md, README.md and CLAUDE.md are not
  edited.
- Gaps are counted and reported, never filled (SPEC 2.2).

## Step 1 — The recipe, from the docs

Write out in plain words, with the SPEC section or DECISIONS entry for each
point, everything needed to build RNO's tables:
- observations: source, station, target hour, pairing rule (SPEC 3, 4.1,
  4.5 — use the nearest report, as SPEC 4.5 requires);
- B: fields, cycle and lead, grid point and interpolation, the elevation
  correction and its frozen RNO constant (SPEC 7, D48);
- L, D, T, R: fields, levels, leads, derivation and any transform (SPEC 8.1,
  8.2, F98–F102, F107, F111);
- the windows and the complete-case rule (SPEC 8.3);
- persistence's day basis (SPEC 8.5).

List every gap or ambiguity, the choice you made, and the alternatives.

## Step 2 — Pull L, D, T, R (network)

- From the recipe, list every GRIB message needed for RNO over
  2021-03-24 to 2025-07-31. Print the count and the estimated size (roughly
  15,000 messages and 13 GB are expected; if yours differs by more than 20%,
  explain why before pulling).
- Fetch by byte range from `noaa-gfs-bdp-pds` into
  `data/raw/grib/session72/`, with a `.meta.txt` sidecar per message (URL,
  byte range, pull time UTC, size, SHA-256). Make the pull resumable. One
  retry per failure; failures are logged, never filled.
- Commit a manifest and a failure log to `data/raw/diagnostics/session72/`.
  `git check-ignore` must confirm that the cache is ignored and the manifest
  and log are not.

## Step 3 — Build (offline, new code only)

- New scripts named `scripts/session72_*.py`. They import no existing
  script.
- Build, into `data/rebuild/session72/`:
  - the observation/target table (every day in both windows, with the
    chosen report's time and value);
  - the feature table (every day in both windows, B plus every L, D, T, R
    column and their intermediates, plus the raw GFS rung value);
  - the persistence table (previous-day observation, where one exists).
- Missing values stay missing. Report, per table and per window: rows,
  missing counts per column, and the complete-case row count.
- Compare those counts only with counts **stated in the docs** (for example
  F107's 365 of 365 reserved-year rows, and any training-window counts in
  D48, D58 or F109). Report agreements and differences. Do not open any
  committed data file to compare.

## End of session

1. Save the full real output to `notes/session-72-output.txt`, including the
   read log, and paste the real numbers in chat. (Writing to `notes/` is
   allowed; reading it is not.)
2. Append one DECISIONS entry at the next free F number (F112 is expected):
   the recipe with sources, every documentation gap and the choice made, the
   pull (counts, failures, pull dates), the build counts, the doc-count
   comparison, and what the session did not do.
3. Overwrite STATUS.md as a pruned, current-only snapshot, ending with:
   "Next planning session: draft session 73 (fit, score and stage-by-stage
   comparison, D64)."
4. Consistency check of the four files; report only.
5. Archive step per D46; report what moved, or that nothing did.
6. `git status --porcelain`; confirm no `.grib2` file is staged or
   untracked, only DECISIONS.md and STATUS.md changed among tracked files,
   and nothing was deleted.
7. Suggested commit message. **Do not commit.** Stop and wait for review.
