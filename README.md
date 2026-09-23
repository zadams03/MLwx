# MLwx

This project learns the steady, repeated error (bias) that the GFS weather
model makes at one airport, then corrects for it. The target is the
temperature at one fixed hour of the day. **SPEC.md** is the source of truth
for how the project works. For results, see **RESULTS.md**.

## Setup

Python 3.12.2 on macOS (darwin, arm64). From the repo root:

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

- **eccodes** is needed to decode GRIB files (the GFS forecast files). The
  pinned `eccodes` package comes with the ecCodes library built in, so pip
  is enough. No system install is needed.
- **libomp.** LightGBM on macOS needs the OpenMP runtime library,
  `libomp.dylib`. It is not part of macOS, and pip cannot install it. The
  normal fix is Homebrew:

  ```
  brew install libomp
  ```

  Without Homebrew, the modelling scripts use a workaround instead. The
  pinned scikit-learn wheel ships its own `libomp.dylib`, and the scripts
  point the loader at it and restart once. See `requirements.txt` for
  details.

## Running scripts

Always run scripts with `.venv/bin/python`, never a bare `python` or
`python3`. The system Python does not have LightGBM, so the scripts fail
with it.

```
.venv/bin/python scripts/<script>.py
```

## Repo layout

- `scripts/` — one or more Python scripts per session, named `sessionNN_*.py`.
- `data/raw/` — raw downloads, never changed in place. Each raw file has a
  `.meta.txt` beside it with the pull date and exact query (SPEC 2.3).
- `data/raw/diagnostics/` — small diagnostic samples and the committed GRIB
  pull manifests.
- `data/processed/` — datasets and result tables built from the raw data.
- `notes/` — saved script output and audit reports.
- `docs/` — the session prompts, one per session.

## The documents

- **SPEC.md** — the source of truth for how the project should work. If
  code and SPEC disagree, SPEC is right.
- **STATUS.md** — a snapshot of where the project is now and what is next.
- **DECISIONS.md** — the live, append-only log of choices, findings and
  open questions.
- **DECISIONS-archive.md** — settled DECISIONS entries, moved there word for
  word. Entry numbers never change.
- **RESULTS.md** — a reader-facing summary of the results. SPEC beats it.
- **CLAUDE.md** — standing rules for every coding session.

## Raw data policy (DECISIONS D47)

The raw GRIB files (the gitignored cache `data/raw/grib`, about 20 GB) are
not in git. They can be fetched again from the public archive using the
committed pull manifests under `data/raw/diagnostics/`. Small raw pulls
are committed as normal.

## Frozen scripts

These four scripts are frozen and are never edited (DECISIONS D62.3):

- `scripts/session39_sealed_test.py`
- `scripts/session48_reserved_year.py`
- `scripts/session60_combine_design.py`
- `scripts/session62_reserved_confirm.py`

Some of them write to fixed, already-committed output files. So any re-run
must happen in a clean clone, never in the working repo (DECISIONS D62.6).
