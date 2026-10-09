# tests/: quick offline checks (DECISIONS D90.12, D95.8)

These tests use Python's standard `unittest`, plus the packages the project
already has installed. Nothing new is installed.

Run them from the repo root:

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

They make no network call, never write inside the repo (only to temporary
folders, deleted after), and finish in seconds.

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
- F122.4's gate at EGLC: the `B+D,L,R,T` model refit on F109's training
  rows gives the recorded MAE exactly, using the functions in
  `scripts/session81_freeze_forward_models.py`.

## Notes

- Some record scripts restart Python on import to set a library path
  (a "libomp shim"). The tests set the shim's variable
  `MLWX_LIBOMP_PATH_SET` first, so no restart happens; lightgbm loads
  without it (D93.3).
- Record scripts that run work when imported (for example
  `session07_test.py` to `session29_test.py`) are never imported here.
- A test that fails is a finding to report, not something to work around.
