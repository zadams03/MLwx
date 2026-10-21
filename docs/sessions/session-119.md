# Session 119: is IFS's cold error a reading fault?

Model: Opus. Network: read-only, only Step 3's byte-range fetches from
ECMWF's open-data bucket on AWS (at most 24 messages, URLs taken from
`ifs_manifest.csv.gz`). No other network.

## Read first

- `CLAUDE.md`, `STATUS.md` and the live `DECISIONS.md`, in full.
- SPEC section 2 (critical rules) and section 5.2 (the elevation
  treatment).
- From the archive, by number only: D107.2, D107.3, D107.5, D107.9 (these
  move to the archive in this session's end steps; read them where they
  are).
- `data/processed/session113/ifs_meta.txt` and `aifs_meta.txt`.
- `scripts/session114_comparisons.py`: only the parts that load the IFS and
  AIFS rows, apply the elevation treatment, pair with the curve's rows and
  observations, and compute MAE and mean error. Do not read the rest.

## Purpose

F160 found IFS cold (mean error, observation minus forecast, +0.39 to
+1.15 C at 10 of 12 airports), worse than raw GFS hourly at 5 of 12, and
its daily maximum low. F160.9(2) asked whether part of that comes from the
open-data product or how we read it. This session checks, with each
test's fault mark fixed in D113 before any value is seen. It is
descriptive only (D107.2): IFS's test years are already spent (D111.6),
nothing is selected or tuned, and no existing figure, table or ANALYSIS.md
line changes. If a fault mark shows, the owner rules (D112.3).

## Scope list (the only files this session may create or edit)

- `DECISIONS.md` (D113, F162, the Live index, archive moves)
- `DECISIONS-archive.md` (archive moves only)
- `STATUS.md`
- `scripts/session119_ifs_check.py` (new)
- `data/processed/session119_ifs/` (new folder and its files)
- `notes/session-119-output.txt` (new)

Fetched GRIB bytes go under `/tmp/` and are deleted at the end (listed in
the output file). No existing script, data file, `ANALYSIS.md`, SPEC,
RESULTS, README, `src/` or `tests/` is touched. Session 114's and 117's
scripts may be imported read-only, never edited.

---

## Step 0: start state

`git status --porcelain` shows only `?? docs/sessions/session-119.md`. No
`session119_*` file or folder exists under `scripts/`, `data/processed/`
or `notes/`. In the venv, `python3 -m unittest discover -s tests` runs 181
tests, OK (F161.1). The 15 IFS pull files' SHA-256 equal `ifs_meta.txt`'s.
**Stop** if any of these differs.

## Step 1: record D113

Append the D113 block below to `DECISIONS.md`, byte-equal (`diff` and
`cmp` against the block extracted from this prompt), 0 em-dashes, and
update the Live index as D113.9 says. **Stop** on any difference.

```
---

## 2026-10-20: Session 119 decision: F161 accepted, the redeploy, the mx2t3 rerun dropped, and the IFS reading check fixed before any value is seen (owner, planning chat)

**D113. Owner decisions, planning chat (after session 118's commit and the redeploy): F161 accepted; the redeploy recorded; a ruling on the doubled 17 Oct cycle; D112.6's amendments named; the mx2t3 rerun dropped; and the IFS reading check, with each test's fault mark fixed before any value is seen.** Written at the start of session 119, before any other edit. No 2026-27 value has been read or scored. No IFS value has been read by the planning chat beyond the pull files' headers.

- **D113.1 F161 accepted,** with its readings (F161.10), which go to the project health check (D112.2).
- **D113.2 The redeploy (D112.8, owner, by hand, 2026-10-20).** MLwx-live commit `0d77fb0`: `.github/workflows/live.yml` copied from the template, with `MLWX_COMMIT` `d6ca3e4e9bd79d55ffbdfd1cc7a9a5d6e21747bb` and `MODELS_TAG` `gfs-models-49` unchanged; `diff` against the template showed only those two lines. Manual run 39488813037 went green at 2026-10-20T20:04Z and its push landed (`0d77fb0..7b4a349`). D112.8's interim rule is lifted.
- **D113.3 The doubled 17 Oct cycle (owner's ruling on D112.7).** 2026-10-17T18z was issued twice, but only the first-issued file exists on main (F161.4). It has no effect on the live test: D105.5 scores the first-issued file only.
- **D113.4 Amendments.** D112.6 amends D105.2 (the job also fails when a push did not land) and D105.4 (the schedule is `15,40 * * * *`).
- **D113.5 The mx2t3 rerun is dropped (owner).** F160.9(3) is closed: descriptive only, unlikely to change any standing (F160.6), and a further hand pull. D111.4 stands.
- **D113.6 The IFS reading check (session 119).** Descriptive (D107.2), on IFS's spent test years (D111.6), on the pull of D111.3 and the rows and pairing of D108.4(a) with D108.3's positions and treatment. Mean error is observation minus forecast (positive is cold). Hourly rows only. Raw GFS (as SPEC 5.2) and AIFS (from 2025-02-25T06Z) are scored on exactly the same rows as references. A count is "at most airports" when it is at least 7 of 12 (or at least 4 of 6 where only the development airports apply). Fault marks, fixed now:
  (a) T1, height. Mark: removing the elevation treatment brings IFS's mean error within 0.2 C of zero at most airports; or, across the 12 airports, the Spearman correlation between IFS's mean error and its mean elevation adjustment (C) is at least 0.7 in size; or any IFS terrain height at a position differs from GFS's terrain height there by more than 300 m.
  (b) T2, position. Mark: at most of the 6 development airports, IFS's mean error at the airport's own position (`iem` set) is at least 0.3 C nearer zero than at GFS's position (`gfs` set).
  (c) T3, timing. Mark: pairing IFS with the observation 3 hours later, or 3 hours earlier, lowers its MAE at most airports; or the slope of IFS's error on the observed temperature trend (the observation at t+1 h minus at t-1 h, per hour) is at least twice the size of raw GFS's at most airports. The same is computed for raw GFS and AIFS as controls. Mean error by local hour is reported without a mark.
  (d) T4, product changes. Mark: IFS's mean error steps by at least 0.5 C, after removing the same calendar step in the other test years, at a reading boundary (2024-02-01 grid change; 2024-12-03 own terrain) at most airports with data on both sides, with no step of that size at the IFS model-version dates.
  (e) T5, decoding. Mark: any fetched message whose SHA-256 differs from the manifest, whose decoded parameter, units, date, time, step or grid differ from its rows, or whose four values at the positions file's points differ from the stored v1 to v4 in any bit.
  If no mark shows, IFS's cold error is recorded as the model's, as read under D108.3, and F160 stands. If a mark shows, it is recorded and the owner rules under D112.3. Nothing is re-scored in session 119 either way.
- **D113.7 Network.** T5 fetches by byte range, from the manifest's URLs, at most 24 messages; nothing else.
- **D113.8 Plan.** Session 119: this entry, the check, F162. Then the project health check's audit (D112.2 item 3).
- **D113.9 Live index.** Removed (archived): D106, D107 and D110, which are settled (D106's and D107's plans are carried out and recorded; D110's check is done and its live guard is restated in D111.2). Added: D113 and F162. After session 119: D93, D103, D105, D108, D111, D112, D113, F157, F160, F161, F162.
```

## Step 2: the reproduction gate

Write `scripts/session119_ifs_check.py`. Its pairing step builds IFS's
hourly rows (both outputs of D108.3: with and without the elevation
treatment), raw GFS's and AIFS's on the same rows, and the observations,
importing session 114's functions where possible. Gate: with the treatment,
its per-airport IFS MAE and mean error over the rows F160.4 used equal the
committed `data/processed/session114_comparisons/hourly_ifs.csv` exactly,
and its row counts equal F160.3's. Confirm the mean error's sign from that
file. **Stop** if any value or count differs.

## Step 3: T5, decoding (network)

Choose the messages before fetching, deterministically: for each grid label
in `ifs_manifest.csv.gz`, its `2t` messages at step 24 of the 00z cycle on
the first, middle and last dates that label covers (up to 24 in all; fewer
if a label is short, counted). For each: fetch the byte range, check the
SHA-256 against the manifest, decode with eccodes (the venv's), and check
shortName, units, date, time, step and the grid against the label; then
read the four points of each airport and position set from the positions
file and compare with every stored row of that message. List each message
and its result. Delete the fetched bytes at the end. A fetch that fails
twice is counted and reported, not guessed.

## Step 4: T1 to T4

Compute D113.6(a) to (d) exactly as written, for IFS, with raw GFS and
AIFS as controls where D113.6 says. Write every table to
`data/processed/session119_ifs/` (one file per test, per airport rows, with
n), and in the output file state each mark as SHOWN or NOT SHOWN with the
numbers that decide it. Do not change a threshold, a window or a row set
after seeing a value; a reading that a threshold looks wrong goes to the
owner as a reading. **Stop** if any computation needs data valid after
2026-07-31T23:00 UTC, any 2026-27 file, MLwx-live, or the 37 airports of
F153.6.

## Step 5: findings

In the output file: each mark SHOWN or NOT SHOWN; the summary per D113.6's
last sentence; what the local-hour profile and the controls show (readings);
anything else odd (open questions, not fixed).

## Step 6: record F162

Append F162 to `DECISIONS.md`: heading
`## 2026-10-20: Session 119 finding: the IFS reading check`, a bold lead
sentence (what was done, descriptive, network used, run date, versions),
then F162.1 D113 recorded; F162.2 the gate; F162.3 T5; F162.4 to F162.7 T1
to T4 with each mark's outcome; F162.8 the outcome under D113.6; F162.9
readings; F162.10 what was not done; F162.11 pointers. Within D93's
finding-length rule. Update the Live index line for F162.

## End of session

Follow CLAUDE.md's end-of-session steps, including:

- the scope-list check;
- the archive step by the Live index (D93.8), which moves D106, D107 and
  D110; DECISIONS.md under 80,000 bytes (D93.9), with the byte count;
- the consistency-check findings written into
  `notes/session-119-output.txt`;
- STATUS.md overwritten as a current-only snapshot: stage G records the
  redeploy (D113.2); the open questions drop the mx2t3 rerun (D113.5) and
  the doubled-cycle item, and replace F160.9(2)'s item with F162's outcome;
  the carried items drop D112.8's interim rule. It ends with:

  **Next planning session:** Review session 119 and commit. If F162 shows a
  fault mark, the owner rules under D112.3 first. Then the project health
  check's audit (D112.2 item 3), then its fixes, ending with the README
  update.

Stop and wait for review. Do not commit anything.
