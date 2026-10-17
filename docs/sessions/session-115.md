# Session 115: D109 (an observation plausibility check before IFS; IFS moves to session 116) and the check at the 12 stage C airports

Recommended model: Sonnet.

## Read first

- STATUS.md and SPEC section 2 (always). SPEC sections 3 (truth data), 5.2 (the elevation adjustment) and 8.8 (G2 and G3: assigning reports to hours).
- DECISIONS.md, the live file, in full (this session records a decision).
- Archived entries, one at a time by line range, only when a step needs them: D82.8 (the daily maximum), D88 (the development table), D100 (the claim tables), F132.2 (IEM station ids).
- Files, when the step that uses them starts, docstrings and the functions used only: `src/mlwx/observations.py` (`finite_float`, `parse_reports`, `ReportSet`, the hour assignment), and whichever existing loaders give the stage C rows' raw GFS (elevation-adjusted, SPEC 5.2) and their observed values at the 12 airports (for example in `scripts/session112_analysis.py`). Say in the checkpoint which loaders were used.

## What this session is

A search earlier on 17 October 2026 found that the project has never checked the IEM/METAR temperatures for implausible values: any finite `tmpc` value is used as it comes. This session records D109 first, then flags and counts suspect hourly temperatures at the 12 airports that have stage C tables, with thresholds fixed below before any value is looked at, and reports how many flagged values reach the stage C rows and the daily maximum.

**Flag and count only.** No raw or processed file is changed. No value is removed, replaced or filled. No model is fitted. No error metric (MAE or any other) is computed with or without the flagged values, and nothing is scored. Nothing valid after 2026-07-31T23:00 UTC is read. No network access; nothing is installed; if a needed package is missing, stop. The untracked `data/processed/session113/work/` (the owner's IFS hand pull) is not read, moved or touched.

Write a checkpoint line to `notes/session-115-output.txt` after each step (D93.11). Stop rather than work around a failed check. The script prints short summaries; full tables go to files (D93.12).

## Scope: the only files this session may create or edit

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`
- `scripts/session115_obs_check.py` (new)
- `data/processed/session115_obs_check/` (new folder and files)
- `notes/session-115-output.txt` (new)

Everything else is out of scope, including SPEC.md, RESULTS.md, ANALYSIS.md, README.md, CLAUDE.md, `docs/PROJECT-INSTRUCTIONS.md`, every existing script, every file in `data/raw/`, every existing file in `data/processed/`, the files in `../MLwx-stagec/` (read only), every model folder, `src/mlwx/`, `tests/` and `requirements.txt`. Anything worth changing there is reported as an open item.

## Steps

### Step 0: Preflight

- `git status` is clean apart from this session file and the untracked `data/processed/session113/work/`. HEAD is session 114's commit (its title is the first line of `docs/commits/commit-114.txt`).
- The Live index lists D93, D103, D105, D106, D107, D108 and F157. No D109 or F158 exists in either DECISIONS file. None of this session's new paths exists.
- The raw IEM routine files for the 12 airports (IEM ids EGLC, LFPG, DSM, YSDU, RNO, SFO, EDDM, ORD, CYYZ, ZGSZ, ZUCK, NZWN) covering 2021-03-24 to 2026-07-31 exist in `data/raw/`; list them. Any file the session reads from `../MLwx-stagec/` matches the SHA-256 in its meta file, where one exists. Stop on any mismatch.
- `numpy` imports; record its version. Record DECISIONS.md's byte size.

Stop if any check fails.

### Step 1: Record D109

Append the block below to DECISIONS.md, byte-equal (copy it with `sed` from this file, then check with `diff` and `cmp`), and add D109 to the Live index. Count em-dashes in the block: must be 0.

~~~markdown
---

## 2026-10-17: Session 115 decision: an observation plausibility check at the 12 stage C airports before IFS; IFS moves to session 116 (owner, planning chat)

**D109. Owner decisions, planning chat (after session 114's commit): a read-only plausibility check of the IEM hourly temperatures at the 12 airports with stage C tables, run as session 115 before the IFS comparisons; its checks and thresholds fixed here before any value is looked at; IFS moved to session 116.** Written at the start of session 115, before any other edit. No observation has been examined for this check.

- **D109.1 Why.** A read-only search (17 October 2026, planning chat) found no plausibility check of the observations anywhere in the project: the readers reject non-finite and missing values (SPEC 8.7 build rule 2, G2) and handle repeated timestamps (F138.8 item 6, F152.7), but any finite `tmpc` value is used as reported. Observations are the truth for every target, the daily maximum (D82.8) and the live drift tracker.
- **D109.2 Session numbers.** Session 115 is this check. The IFS work of D108.7 becomes session 116, unchanged; D108.2 stands.
- **D109.3 Data.** The committed raw IEM routine files (`data/raw/iem_asos_<id>_*_routine.csv`) for EGLC, LFPG, DSM, YSDU, RNO, KSFO, EDDM, KORD, CYYZ, ZGSZ, ZUCK and NZWN, valid 2021-03-24T00:00 to 2026-07-31T23:00 UTC. Reports are read with the project's own reader and assigned to hours by SPEC 8.8 G2 and G3, so the series checked is the hourly series the stage C rows use. Nothing valid later is read (D73.8, D105).
- **D109.4 The checks, fixed before any value is looked at.** On each airport's hourly series:
  (a) **Out of range:** a value below -60.0 or above 60.0 degrees C.
  (b) **Spike:** an hour h whose value differs from both h-1 and h+1 by more than 10.0 degrees C in the same direction; or two consecutive hours h and h+1 that both differ from h-1 and from h+2 by more than 10.0 degrees C in the same direction. A missing neighbour means the test cannot be made at that hour; such hours are counted, not flagged.
  (c) **Stuck sensor:** a run of 24 or more consecutive hours with the same value; a missing hour breaks the run. Every hour in such a run is flagged.
  (d) **Extreme residual:** observation minus raw GFS greater than 10.0 degrees C in either direction, where raw GFS is the median of every elevation-adjusted raw GFS value (SPEC 5.2) valid at that hour in the stage C rows, leads 3 to 48. An hour with no raw GFS value is counted, not flagged.
  A value may carry several flags; each check is counted separately, and the union is counted once.
- **D109.5 Exposure.** For each airport and check, and for the union: flagged hours that are a target in the stage C rows (development table or claim table), split before 2024-08-01 and from 2024-08-01; and flagged hours that set a usable day's daily maximum under D82.8.
- **D109.6 Limits.** Flag and count only. No file in `data/raw/` or any existing processed file is changed; no value is removed, replaced or filled; no model is fitted; no error metric is computed with or without the flagged values. Any rule for excluding observations comes later, in its own entry, as a D89 build choice made on the development airports, and is not chosen by its effect on any spent year's score. Thresholds are not changed after the values are seen; a reading that a threshold looks wrong goes to the owner as a reading.
- **D109.7 Next.** If the flags are rare and explained, the 51-airport check is planned without urgency. If they are frequent, or reach many targets or daily maxima, the check of all 51 airports (all are trained on) comes before session 116. The owner decides at review.
- **D109.8 Note for the project health check (owner).** The repo uses a root layout (`docs/`, `notes/`, DECISIONS at the root), not the `research/` and `audit/` layout recorded in D90.5. Recorded here so it is not lost; it is examined in the planned health-check session, not here.
- **D109.9 Live index.** Removed: none. Added: D109 and F158. After session 115: D93, D103, D105, D106, D107, D108, D109, F157, F158.
~~~

Stop if the block is not byte-equal.

### Step 2: The script and its self-checks

Write `scripts/session115_obs_check.py` with modes `--check`, `--flag` and `--exposure`. Import, read only, from `src/mlwx/observations.py` and the existing loaders; write new code only where no function exists, and say which in the checkpoint. The thresholds of D109.4 are constants at the top of the script.

- `--check` (synthetic, no real value): each of D109.4 (a) to (d) on made-up series, including a one-hour spike, a two-hour spike, a large step that does not reverse (not flagged), a missing neighbour (counted, not flagged), a 23-hour run (not flagged), a 24-hour run (flagged), a run broken by a missing hour, and a residual of exactly 10.0 (not flagged); the guard refusing any valid time after 2026-07-31T23:00 UTC.
- Gate (real data, no flag computed): the hourly series built for each airport has the same number of usable hours, and the same usable daily-maximum days, as the stage C rows and D82.8 days already on record for that airport (compare with the counts in the existing tables or meta files; name which). Stop on any mismatch.

Stop if any check or the gate fails.

### Step 3: Flag (`--flag`)

Run D109.4 at the 12 airports. Write `data/processed/session115_obs_check/flags.csv` (one row per flagged hour: airport, valid time UTC, value, each check's flag, the neighbours' values for (b), run length for (c), the raw GFS median and residual for (d)) and `counts.csv` (per airport and check: usable hours, hours that could not be tested and why, flagged hours, and the rate per 10,000 usable hours; the same for the union). Each file gets a `.meta.txt` with inputs, SHA-256 and the run time.

### Step 4: Exposure (`--exposure`)

D109.5 per airport and check, to `exposure.csv`. Also, descriptive only: the 10 largest |residual| hours per airport and every out-of-range hour, listed in the output file with their neighbours, so the owner can judge them. No score of any kind.

### Step 5: F158

Record F158 (at most about 40 lines, D93.10): D109 recorded; the self-checks and gate; per check and airport, flagged hours and rates (claim airports first, development airports flagged); the union; exposure to targets (before and from 2024-08-01) and to daily maxima; a plain reading of whether the flags look like real sensor faults, real weather (fronts, foehn, sea breezes) or threshold artefacts, labelled as a reading, not a ruling; readings for the owner, including anything that bears on D109.7's choice; what was not done; pointers.

## End of session

As CLAUDE.md, with:

- STATUS.md overwritten as a current-only snapshot. Its last line: "**Next planning session:** Review session 115 and commit. Then decide from F158 whether the 51-airport observation check comes before session 116 (D109.7); session 116 is the IFS comparisons (D108.7, D109.2), after the owner's hand IFS pull (D108.2)."
- The archive step with D109.9's Live index, `--citations`, DECISIONS.md's byte size, and the scope-list check against this file's scope.
- `notes/session-115-output.txt` begins with the summary of at most 30 lines, then the checkpoints and full detail, including the end-of-session consistency checks.

Do not commit anything. Stop and wait for review.
