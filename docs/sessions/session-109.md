# Session 109: stage G, live product v1 (build and gate, not deployed)

Model: Opus. This is a long session. Every step has a check and a stop
condition: if a check fails, stop at that step, write what you found into
`notes/session-109-output.txt`, report, and wait. Do not work around a
failed gate.

## Read first

- STATUS.md; SPEC sections 2, 8 and 9.
- DECISIONS.md in full (live: D93, D102, F151).
- DECISIONS-archive.md, by number only: D72.4, D73.3, D73.4, D82.4, D82.7,
  D83, D86.5, D88, D89, D90.12, D95.2, D97, D98, D101.2, F138, F146,
  F147, F149.
- Scripts, read only (they are the reference to port, never edited):
  `session91_grib_pull.py`, `session96_stagec_table.py`,
  `session104_stagec_table_f025_048.py`, `session104_curve_cv.py`,
  `session106_claim_table.py`, `session106_claim_look.py`.

## Standing rules for this session

- No score of any kind on any row valid on or after 2026-08-01: no MAE,
  mean error or other aggregate of errors. The drift tracker's update is
  the only place an error on such a row is computed (D103.2).
- No existing script, data file, figure or `MLwx-*` folder is edited.
  SPEC.md, RESULTS.md, README.md and CLAUDE.md are not edited.
- Network is allowed only in Steps 5, 6 and 8, only to the AWS GFS
  archive and IEM.
- Long runs follow D86.5.
- No em-dashes in any new text.

## Steps

**Step 0. Preflight.** `git status --porcelain` shows only this prompt.
D102 and F151 are the last entries; no D103 or F152 exists in either
DECISIONS file. The test suite passes (51 tests, F151.5). Locate the
stage C inputs named in F138, F147 and F149 (pull folders, tables,
observation files, positions) and confirm each SHA-256 the record gives.
Stop on any mismatch.

**Step 1. Record D103.** Copy the block between the markers below into
DECISIONS.md at the bottom, mechanically (`sed`), and check it byte-equal
(`diff`, `cmp`). 0 em-dashes. Before any other edit.

**Step 2. The package `src/mlwx/`** (D103.3). Port, do not redesign:
config per weather model (only `gfs`: source, field map with each GRIB
message's identity keys, cycle hours, leads 0 to 48, version table with
v16 only), the four-point extraction and arithmetic (D82.4, D88.5), the
feature builder, the observation pairing (D88.7), the baseline fit
(SPEC 9.3, section 8's settings and column order), the drift tracker
(D97.5, D97.6) and the daily maximum read-off (D98.10). Standard library,
numpy and lightgbm only, unless something already in `requirements.txt`
is needed. Tests in `tests/test_live.py`, offline, temp folders only.
Check: suite passes.

**Step 3. Gates against the record, with the package's code only.**
- Gate A: rebuild the development tables (leads 0 to 24 and 25 to 48) and
  the six claim tables from the committed pull extracts and observation
  files. Each must equal the recorded table exactly (by SHA-256 where the
  record gives one, otherwise every value at full precision).
- Gate B: reproduce F147's hourly curve scores (leads 3 to 48) and
  F147.6's daily maximum scores, per airport and headline, at full
  precision, at the development airports. This is a build-choice
  reproduction (SPEC 2.5); the claim look is not run (D101.2).
Stop if either fails.

**Step 4. Product refit** (D103.5). The 12 airports, every complete-case
row valid up to 2026-07-31. Fit twice in separate processes: models must
be identical. Save them outside the repo in
`../MLwx-live-build/models/`, with a manifest (file, SHA-256) and one
SHA-256 over the manifest. Report the total size and apply D103.5's 50 MB
rule (say which storage applies; do not upload anything). Hold the
manifest SHA-256 as a constant in the package (D98.2), checked by a test.

**Step 5. Live GFS adapter.** Port the byte-range fetch (`session91`),
including the guard of D103.10: every message's identity keys and the
grid are checked against the field map before any value is used; a
mismatch or missing field makes the cycle issue nothing. Gate C: fetch
three cycles from inside the pull window (one each from 2021, 2023 and
July 2026, cycle hours chosen by the session and listed) for the 12
airports, leads 0 to 48, from the live archive. Every value must equal
the pull's extract exactly. Also test the guard offline with an altered
message key (must stop).

**Step 6. Live observation adapter.** IEM routine reports. Gate D:
re-fetch one month inside the training window for the 12 airports; the
values used for pairing must equal those in the committed observation
files. Report any difference in the raw rows separately from the pairing
result.

**Step 7. Log, tracker state, page and runner.**
- Log (D103.8): `log/YYYY/MM/gfs_YYYYMMDDHH.csv`, one file per cycle for
  all airports, written once; the writer refuses to overwrite an
  existing file.
- Tracker state: one file, updated each run; each cell records the last
  valid time applied so no error is used twice; starts at b = 0
  (D103.6). Errors are the baseline's, from log rows whose observation
  has arrived and is valid before the cycle starts.
- Page: one static HTML file (standard library only, like
  `session108_figures.py`): per airport, the latest cycle's raw GFS and
  corrected curve, the daily maxima, and a status line (cycle, GFS
  version, issue time, any stop, "drift warming up" while a cell has
  fewer than 50 errors, "not validated on v17" when the version is v17).
  No accuracy figure anywhere.
- Runner: processes every cycle of the past 24 hours that is available
  and not yet logged, in time order.
Tests for each part (offline). Check: suite passes.

**Step 8. Dry run.** Run the runner once against the live archive and IEM
into a `mktemp -d` folder, on the latest available cycle, from a fresh
tracker state. Check: one log file, all 12 airports, leads 3 to 48, b = 0
everywhere, page builds. Report a short table of the corrected curve at
leads 3, 24 and 48 per airport beside raw GFS. Nothing scored. Delete
nothing from the temp folder; give its path.

**Step 9. Live repo files, not deployed.** In `deploy/mlwx-live/`: the
GitHub Actions workflow (four schedules, about cycle + 4 h 10 min UTC,
plus manual trigger; checks out this repo at a pinned commit given as a
placeholder for session 110; installs pinned requirements; runs the
runner; commits log and state; publishes the page to GitHub Pages), its
requirements file, and a README for the live repo (what it is, that the
log is never edited, link back to MLwx). Check the workflow parses as
YAML. Do not create any remote repo or push anything.

**Step 10. Record F152** (findings, D93's length rule): each gate's
result, the model size and storage, the dry run, readings for the owner,
what was not done.

## Scope

May create: `src/mlwx/**`, `tests/test_live.py`, `deploy/mlwx-live/**`,
`scripts/session109_gates.py` (if the gates need a script),
`notes/session-109-output.txt`, `../MLwx-live-build/**`, temp folders.
May edit: DECISIONS.md, DECISIONS-archive.md, STATUS.md, and
`requirements.txt` only if Step 2 needs it (report why). Nothing else.

## End of session

CLAUDE.md's end-of-session steps, with:
- the archive step per D103.12;
- STATUS.md overwritten as a current-only snapshot, ending with a "Next
  planning session" line: review session 109; then plan session 110
  (owner creates MLwx-live; deploy; first live runs; onboarding script
  and the other 39 airports);
- the consistency-check findings written into the output file, not only
  reported in chat.
Do not commit and do not write a commit message.

## D103 (copy exactly)

<!-- D103 start -->
## 2026-10-12: Session 109 decision: F151 accepted, and stage G's design (owner, planning chat)

**D103. Owner decisions, planning chat (after session 108): F151
accepted, and stage G's design (D102.4), recorded before any build.**
Written at the start of session 109, before any other edit. No value on
or after 2026-08-01 has been scored. Stage G makes no claim (D102.5).

- **D103.1 F151 accepted,** with its four F151.8 readings as written.
- **D103.2 What v1 is.** For every GFS cycle, a corrected 2 m
  temperature curve at leads 3 to 48 and, for each local calendar day
  wholly inside those leads, its maximum read off the curve, by SPEC
  9.3's method unchanged. GFS only. No accuracy figure is computed or
  shown for any period until a test on it is pre-registered (D102.5).
  The drift tracker's errors are an input, not a score.
- **D103.3 The weather model is a setting.** The code is a package,
  `src/mlwx/`, in this repo (D90.12), with a config per weather model:
  data source and fetch, field map, cycle hours, leads and a version
  table. v1 has only `gfs`. A new model adds a config and an adapter,
  not a rebuild.
- **D103.4 Airports.** v1 runs the 12 airports with stage C tables: the
  development airports (EGLC, LFPG, DSM, YSDU, RNO, KSFO) and the claim
  airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN). The rest of D83's
  product list is added later by a one-script onboarding tool.
- **D103.5 Product models.** Refit once at each v1 airport by SPEC 9.3's
  structure and section 8's settings, on every complete-case row valid
  up to 2026-07-31, spent years and the claim airports' look years
  included. This is a build step, not a test: nothing is scored, and
  stage C's look is not run again (D101.2). The models are then frozen;
  v1 does no retraining. Storage: if the whole set is under 50 MB, it is
  committed to the live repo; otherwise it is one Release asset there.
  Either way its SHA-256 is held as a constant (D98.2), and every log
  row cites it.
- **D103.6 Drift tracker.** As D97.5 and D97.6: per airport, cycle hour
  and lead, weight 0.02, updated only by the baseline's own errors whose
  observation is valid before the cycle starts, in ascending valid time,
  each error once. Every tracker starts at b = 0 at the first live cycle
  (D97.7's rule), so early forecasts equal the baseline. Observations:
  IEM routine reports, the nearest within 15 minutes of the valid hour
  (D88.7).
- **D103.7 Live data.** GFS from the same AWS archive, by the same
  byte-range method and at the same four grid points and weights per
  airport as the pull (D82.4); observations from IEM. On any fetch error
  or missing field, that cycle issues nothing, and the page says so.
- **D103.8 The prediction log.** One file per cycle, for all airports,
  written once and never edited. Each row: airport, cycle, lead, valid
  time, raw GFS, baseline, b, corrected value, GFS version, model
  SHA-256, code commit and issue time. A correction is a new file, never
  an edit. Git history is the proof.
- **D103.9 Where it runs.** A separate public repo, zadams03/MLwx-live.
  A GitHub Actions workflow runs four times a day after each cycle lands
  and also catches up any cycle of the past 24 hours missing from the
  log. It checks out this repo's code at a pinned commit, commits the
  log and tracker state, and publishes a static page with GitHub Pages:
  the curve and daily maxima per airport, the GFS version and a status
  line. Public because, on the free plan, public repos get unlimited
  Actions minutes and Pages, and a timestamped, never-edited log is
  forward evidence. This repo receives no automated commits.
- **D103.10 GFS v17 (owner's choice: continue under narrow mapping).**
  Every row carries the GFS version from the config's version table: v16
  until the first operational v17 cycle is recorded in a DECISIONS
  entry. Before a cycle is used, a guard checks every GRIB message's
  identity keys and the grid against the field map; any mismatch stops
  that cycle (D103.7). After v17 starts, the pipeline keeps running only
  under D73's narrow mapping: a fetch may change only if the physical
  quantity is identical, recorded in DECISIONS first. The models are not
  retrained, and the page marks v17 forecasts as not validated.
  Retraining and upgrade policy stay in stage F (D102.4). A 2027-28
  claim (D72.4) would then be on v17; stage F decides how it is framed.
- **D103.11 Plan.** Session 109: this entry; the package; gates that
  reproduce stage C's tables and F147's scores at the development
  airports; the product refit; live GFS and observation adapters, gated
  against committed data; the log, tracker state, page and runner; one
  dry run on the latest real cycle into a temporary folder; the live
  repo's files, written but not deployed; F152. Session 110: the owner
  creates MLwx-live; deployment; the first live runs checked; the
  onboarding script and the remaining airports.
- **D103.12 Live index.** Removed (archived): D102 and F151, which are
  settled. Added: D103 and F152. After session 109: D93, D103, F152.
<!-- D103 end -->
