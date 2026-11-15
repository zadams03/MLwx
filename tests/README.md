# tests/: quick offline checks (DECISIONS D90.12, D95.8)

These tests use Python's standard `unittest`, plus the packages the project
already has installed. pytest is not installed, and the suite stays on
unittest (D116.2). Nothing new is installed.

Run them from the repo root:

```
.venv/bin/python -m unittest discover -s tests
```

They make no network call, never write inside the repo (only to temporary
folders, deleted after), and finish in under a minute.

## What they cover

`test_guards.py`: the guards that keep future data out (leakage guards).

- The 2026-27 guard in `scripts/session97_stagec_cv.py`: refuses a valid
  time of 2026-08-01T00:00, allows 2026-07-31T23:00.
- `check_gate_date` in `scripts/session86_forward_build.py`: refuses
  2026-08-01, allows 2026-07-31 (F128.4).
- The session-48 reserved-year guard: refuses a fold that trains or tests
  inside 2024-08-01..2025-07-31, passes the three `EXPERIMENT_FOLDS` (D51).
- The stage C pull script `scripts/session91_grib_pull.py`: refuses a cycle
  after 2026-07-31T18 and a valid time after 2026-07-31T23, and any cycle
  before 2021-03-22T12, the first GFS v16 run (D84.2, D95.5).

`test_record.py`: the archive tool and figures already on record.

- `scripts/archive_decisions.py` on temporary copies of both DECISIONS
  files: `--plan` runs; `--apply` passes its four checks, including a
  byte-for-byte rebuild of the original; a second `--apply` moves nothing.
  `--citations` on the real files finds no unresolved entry. DECISIONS.md is
  under 80,000 bytes (D93.9).
- F139's headline MAEs (baseline and raw GFS), rebuilt from the committed
  cell scores, within 1e-12.
- Session 100's baseline score rows equal session 97's (F143.6).
- Record lookups (D96.2, D96.3): session 91's fixed `TRAINING_SET_SHA256`
  equals F122.3 in the two DECISIONS files and the committed training set;
  session 87's `manifest.json` pattern finds F122.5's one value, which equals
  the committed file, and F122.5's table has all six airports.
- F122.4's gate at EGLC: the `B+D,L,R,T` model refit on F109's training
  rows gives the recorded MAE exactly, using the functions in
  `scripts/session81_freeze_forward_models.py`.

`test_session127_figures.py`: the README figure script's input files, its gate, and the values and dates it holds.

`test_session129_live_score.py`: the live test's scoring script on small made-up logs and observations: its history check, periods, counts, bar and refusals (D123.4(b)).

`test_session129_stageb_gate.py`: the constants in session 86's gate wrapper against both DECISIONS files and the committed files, and session 86's own lookups run against them (D123.5).

`test_pinned_files.py`: the seven files the live test's frozen scoring script imports or reads, held at their bytes at commit 3bf156f, and all 49 airports kept (D125.4).

`test_stageb_rules.py`: stage B's rules through the frozen scripts' own code on made-up numbers: a tie fails, the day basis, "no verdict (0 days)", the split at a first GFS v17 cycle, the rows file's date checks; and the three `--guard-check` modes exit 0 (D73, D79).

`test_session131_stageb.py`: stage B's build check on drop logs written by session 86's own code with fake requests, and the constants in the stage B scoring wrapper against both DECISIONS files and the committed models (D125.5).

`test_session132.py`: session 132's three scripts: the gates wrapper runs on the 12 record airports, the scripts it and the position wrapper import have the fingerprints held for them, and the revision script pairs rows across cycles and counts sign agreement correctly on made-up rows (D127).

`test_session133.py`: session 133's range comparison on made-up values: the interval score, tables built only from earlier years, each part of the choice rule failing on its own, the swap of a crossed range, the tercile edges, and the fingerprints of the three scripts it imports (D128).

`test_mosmix_saver.py`: the MOSMIX saver template with a fake DWD server: the listing, the file check, saving once, the manifest, the freshness rule for all stations and for each one, retries, the station list, and the workflow (its commit step run in a temporary repository, with and without `manifest/`) (D122).

## Notes

- Some record scripts restart Python on import to set a library path
  (a "libomp shim"). The tests set the shim's variable
  `MLWX_LIBOMP_PATH_SET` first, so no restart happens; lightgbm loads
  without it (D93.3).
- Record scripts that run work when imported (for example
  `session07_test.py` to `session29_test.py`) are never imported here.
- A test that fails is a finding to report, not something to work around.
