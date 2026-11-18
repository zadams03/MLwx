# Session 135: stage D opened on AIFS, the claim airports drawn, and the AIFS pull built and gated

Recommended model: Opus.

## Read first

- `CLAUDE.md` and `STATUS.md` in full.
- `DECISIONS.md` (live) in full.
- From `DECISIONS-archive.md`, by number only: D72.4, D72.6, D72.8, D82.7,
  D82.8, D89, D104.7, D107.3, D108.2, D108.3, D111.6, F123.2 and F123.3 (the
  AIFS rows only), F132.6, F153.6, F156.8, F156.9.
- `SPEC.md` sections 2.5, 5.2, 7.2, 8.1, 8.8 and 9.1 to 9.3 only.
- `scripts/session113_comparison_pull.py`: only the functions this session
  reuses, by line range (`get`, `s3_list`, `fetch_message`, `ecmwf_folder`,
  `ecmwf_file`, `ecmwf_index_lines`, `idx_parse`, `grib_meta`,
  `grid_signature`, `box_regular`, `pmap`, `write_csv_gz`).
- `scripts/session90_airport_check.py`: only `usable`, `load_reports`,
  `hour_of`, `local_day_counts` and `obs_counts`.

## Scope

This session records D130, draws stage D's six claim airports, writes the
AIFS pull, and runs its test chunk and gate. It does **not** run the full
pull (the owner does, by hand, D130.9), fit any model, compute any error or
score from any AIFS value, read any observation value other than to count
usable hours (D130.7(b)), read anything valid after 2026-07-31T23:00 UTC, or
touch MLwx-live, `src/mlwx/`, a frozen script, a pinned file or the GRIB
cache.

**May create:** `scripts/session135_aifs_draw.py`,
`scripts/session135_aifs_pull.py`, `tests/test_session135_aifs.py`,
`data/processed/session135_draw/` (its files),
`data/processed/session135_pull_test/` (the test chunk's files, a few MB at
most), `notes/session-135-output.txt`.
**May edit:** `DECISIONS.md`, `DECISIONS-archive.md` (archive step only),
`STATUS.md`, `scripts/README.md` (one row in the per-session map),
`tests/README.md` (one line).
Nothing else. SPEC, RESULTS, README, ANALYSIS, CLAUDE and
`docs/PROJECT-INSTRUCTIONS.md` are not changed.

**Network:** S3 listings and `.index` files under ECMWF's open-data bucket,
and messages by byte range, for Step 2's grid check and Step 5's test chunk
only. No IEM call (the observations are already saved). Nothing else.

## Step 0: start checks

HEAD is `9f22ade`; the tree is clean apart from this file (untracked); the
tests pass (`.venv/bin/python -m unittest discover -s tests`: 449, 1
skipped); SPEC 3.4's span is unchanged (STATUS gives its SHA-256).
**Stop** if any differs.

## Step 1: record D130

Append the D130 block below to `DECISIONS.md` (after F178) with `sed`, from
the line after `<!-- D130 start -->` to the line before `<!-- D130 end -->`.
Check it byte-equal with `diff` and `cmp`; count em-dashes (0). **Stop** if
not byte-equal. No other edit comes before this one.

<!-- D130 start -->
---

## 2026-11-17: Session 135 decision: F178 accepted, the redeploy, stage D opened on AIFS with its claim on new airports, and the claim airports' rule (owner, planning chat)

**D130. Owner decisions, planning chat (after session 134's commit): F178 accepted; the owner's redeploy recorded; stage D opened, starting with ECMWF AIFS; where and how its claim is judged; the rule for drawing its claim airports; the AIFS pull; the next sessions; and Live index changes.** Written at the start of session 135, before any other edit. No AIFS value has been read at any airport outside the 12 record airports, and no value valid on or after 2026-08-01 has been scored in any test.

- **D130.1 F178 accepted,** with its readings (F178.8, F178.9) as STATUS lists them.
- **D130.2 The redeploy (owner, by hand, 2026-11-16, not by a session).** MLwx-live commit `afc970b` (00:12Z) sets `MLWX_COMMIT` `9f22ade38e56230ac9d9ff6e6fb13a05da9f262d` (session 134), keeps `MODELS_TAG` `gfs-models-49`, and copies the template README. The scheduled run at 00:18Z (MLwx-live `b7f27ef`) issued 2026-11-15 18z with `code_commit` `9f22ade` on all 2,254 rows. The owner checked the page: the 8-in-10 bands and the "not yet verified" label show at the 12 airports, and there is no "not available" line. The live test treats every row after the redeploy exactly as before it (D129.10).
- **D130.3 Stage D opened (D72.3, D72.8), starting with ECMWF AIFS Single.** Stage D corrects one weather model on its own, from its own fields; GFS is not an input. Combining models is stage E. A GFS v17 notice still goes first (D129.11).
- **D130.4 Where AIFS's claim is judged: new airports (D72.4), one look.** AIFS's operational archive starts on 2025-02-26 (F123.3), so two unseen years per airport cannot exist. Owner's choice: the look is the year 2025-08-01 to 2026-07-31 at six new airports, with each airport's models refit at the start of every calendar month on all earlier data only (an expanding window). The first months are trained on about five months of February to July data; this is stated with any result. AIFS v2 (with IFS 50r1) went live on 2026-05-12, inside the year; it is labelled, not split. No forward test on 2026-27 is pre-registered now.
- **D130.5 What the claim covers (owner's choices).** The hourly curve at AIFS's own 6-hourly steps (leads 6 to 48), against raw AIFS and persistence. The daily maximum is scored descriptively only: taken from four steps a day it runs low, so beating raw AIFS would say little. There is no claim against corrected GFS in stage D: the GFS product models at these airports were fitted on these years (D104.7, F153.6), and combining is stage E's question; any GFS reference in stage D is descriptive. The bar's exact form, the metric, the look script and every remaining detail are fixed at the lock (session 137), before any claim-airport row is scored.
- **D130.6 Framing, recorded now.** The claim airports' observations to 2026-07-31 were used to fit the GFS product models and were counted by session 116's check (D110). They have never been scored for any claim, and no AIFS value has been read there. A result is labelled "new airports for AIFS".
- **D130.7 The claim airports: rules fixed before any check is run.**
  (a) Pool: the 37 airports onboarded in session 110 (F153.6), minus LFPB (D82.7(a)): 36 airports, listed in session 90's table (`data/processed/session90_airports.csv`).
  (b) Eligible: the airport's saved hourly observations (`data/raw/iem_asos_*`) give a usable daily maximum (D82.8) on at least 90 percent of local days in 2025-02-26 to 2026-07-31, and on at least 90 percent of local days in 2025-08-01 to 2026-07-31. A local day counts only if it starts on or after 2025-02-26T00:00 UTC and ends on or before 2026-07-31T23:59 UTC. Counted with session 90's functions, unchanged. Also: the airport's four grid points in `data/processed/session91_pull_airports.csv` must lie on AIFS's 0.25 degree grid (D130.8). Only counts of usable hours are read; no value is read as an error.
  (c) Strata and sizes, in this order, from session 90's `stratum` column: Europe 1; North America 2; Asia 2; South 1.
  (d) Draw: Python's `random.Random(20261117)`, one generator for the whole draw. For each stratum in (c)'s order, `sample` its eligible airports, sorted by ICAO code, for its size. A shortfall is filled as D82.7(d) says. Record the Python version. The draw runs once; neither the seed nor any eligibility result is changed after it.
- **D130.8 Positions and treatment.** Every airport keeps the four grid points and bilinear weights its GFS table uses (`session91_pull_airports.csv`), read on AIFS's 0.25 degree grid, which must hold the same points (longitudes compared modulo 360). Elevation treatment as GFS's (SPEC 5.2, D108.3), with AIFS's own surface geopotential.
- **D130.9 The AIFS pull.** ECMWF open data, `aifs-single/0p25/oper/`, from 2025-02-26 00z; no experimental files. Cycles 00, 06, 12 and 18; steps 0 to 48 every 6 hours; only steps valid on or before 2026-07-31T23:00 UTC. Fields: 2 m temperature, 2 m dewpoint, total cloud cover, 10 m u and v wind, temperature at 850 hPa, mean sea level pressure, surface pressure, surface downward shortwave radiation, and surface geopotential (step 0). Kept unrounded at the four points of 18 airports: the 12 record airports and the six drawn. Whole messages by byte range from the `.index`, each checked against its plan (parameter, level, units, run, step, grid), its SHA-256 recorded; a failed check is a gap with a reason, never a value. The full pull is run by the owner by hand, outside any session, as D108.2 did for IFS; session 135 builds it, runs a test chunk and gate, and estimates its cost. How AIFS's 6-hourly fields map onto `D`, `L`, `R` and `T` (GFS's tendency is over 3 h and its radiation over 2 h) is fixed by an owner ruling in session 136's entry, before any screening.
- **D130.10 The next sessions.** 136: check the owner's pull; the feature mapping; screening by cross-validation at the six development airports (D72.8, D89), the recipe otherwise unchanged. 137: the lock. 138: the look, run once. Opus unless the owner chooses otherwise.
- **D130.11 Live index.** Removed (archived): D129 and F178, which are settled (D129's range test stays binding from the archive and is carried in STATUS; F178 is accepted). Added: D130 and F179 (F179 when it is written). After session 135: D93, D103, D105, D118, D130, F179.
<!-- D130 end -->

## Step 2: the grid check and eligibility

New script `scripts/session135_aifs_draw.py`, modes `--eligible` and
`--draw`, importing session 90's functions read-only (session 90's script is
not edited).

(a) Grid: fetch one AIFS 2 m temperature message (2025-03-01 00z, step 6),
read its grid's coordinates only, and check every point in
`session91_pull_airports.csv` for the 36 pool airports and the 12 record
airports lies on it (D130.8). Record the grid signature.
(b) Eligibility (D130.7(b)) for the 36 pool airports: usable days and
percentages in both windows, and the grid result. Write
`data/processed/session135_draw/eligibility.csv` with a `.meta.txt`
(SHA-256, Python version, inputs).

**Check:** 36 rows; every record airport's points on the grid. **Stop** if a
record airport fails the grid check, or any pool airport's observation files
are missing.

## Step 3: the draw, once

`--draw` applies D130.7(c) and (d) to `eligibility.csv`, prints the draw as
it happens, and writes `data/processed/session135_draw/draw.csv` with its
meta file. Report the eligible counts per stratum and the six airports.
Do not run it again. **Stop** if it cannot produce six airports.

## Step 4: the pull script

New script `scripts/session135_aifs_pull.py`, importing session 113's helpers
read-only (session 113's script is not edited). Modes:
- `--plan`: list the cycles and messages D130.9 needs for the 18 airports,
  by month, from the S3 listings and `.index` files; write the plan.
- `--pull --months A..B [--workers N] [--outdir DIR]`: fetch by month
  chunk; a finished chunk is skipped; write through `*.partial` files then
  rename; back off on HTTP 503 as session 113 does (F156.9(8)).
- `--verify`: the checks of D130.9 on everything pulled; gaps by reason,
  cycle hour and month; kept plus gaps equals planned.
- `--gate`: Step 5's gate.

Guards (tested in Step 6): no cycle before 2025-02-26 00z; no step valid
after 2026-07-31T23:00 UTC; only the 18 airports of D130.9 (the 12 plus
`draw.csv`'s six); no experimental folder. Output per airport like session
113's (`airport, cycle, step, valid_utc, param, level, v1..v4, units, msg`),
plus a manifest and meta file.

## Step 5: the test chunk and gate

Run the pull on: 2025-03-01 (four cycles), 2026-05-20 (four cycles, after
AIFS v2), and 2026-07-30 00z to 2026-07-31 18z (eight cycles, to exercise
the end guard), into `data/processed/session135_pull_test/`. Then
`--verify` and `--gate`:
(a) At the six development airports, where session 113's `gfs` position set
uses the same four points as `session91_pull_airports.csv`, the new 2 m
temperature values equal session 113's stored `v1` to `v4` for the same
cycles and steps, in every bit (values compared, nothing scored). Report
where the points differ instead.
(b) Five messages chosen at random (seed 135) fetched again: SHA-256 equal.
(c) Every planned message is kept or is a gap with a reason.
(d) Every field of D130.9 is present in both AIFS versions, with its names
and units recorded per version; any change between versions is a reading.
(e) No row valid after 2026-07-31T23:00 UTC.
**Stop** if (a), (b), (c) or (e) fails.

## Step 6: cost, the owner's command, and tests

(a) From the plan and the test chunk's rate: messages, bytes, and hours at 8
workers. Give the exact command(s) for the owner's hand pull: an output
folder outside the repo, chunks by month, safe to re-run, and the
`--verify` to run afterwards.
(b) `tests/test_session135_aifs.py`: the guards of Step 4; the draw
function reproduces `draw.csv` from `eligibility.csv`; the longitude mapping
of D130.8; a gap is never written as a value. Run the full suite.

## End-of-session steps (CLAUDE.md)

Write **F179** (at most about 40 lines): eligibility counts per stratum, the
six drawn airports, the gate results, the cost estimate, the owner's
command, readings (including any field that changes at AIFS v2), and what
was not done. Then CLAUDE.md's five end-of-session steps, with D130.11's
Live index changes in the archive step (`--session 135`). STATUS's "Next
planning session" line: review session 135 and commit; the owner runs the
AIFS pull by hand; then plan session 136 (pull check, the feature-mapping
ruling, screening). Write the consistency-check findings into
`notes/session-135-output.txt`. Stop and wait for review. Do not commit.
