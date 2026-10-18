# Session 117: D111 (F159 accepted, no observation cleaning rule, the owner's IFS pull recorded, IFS's daily maximum rule) and the IFS comparisons

Recommended model: Opus.

## Read first

- STATUS.md and SPEC section 2 (always).
- DECISIONS.md, the live file, in full (this session records a decision). D107, D108, D110, F157 and F159 in particular.
- Archived entries, one at a time by line range, only when a step needs them: F156 (the pull and its checks), D98.10, D82.8.
- Files, when the step that uses them starts: `scripts/session114_comparisons.py` (its docstring, `SOURCES["ifs"]`, `Comp`, the daily maximum functions and `main`; run, never edited); `scripts/session113_comparison_pull.py` (docstring and the IFS check code only, read only); `data/processed/session113/ifs_meta.txt`; `ANALYSIS.md` Part 1 and Part 2's "D107.9 and D108: comparisons" section.
- The owner's pull log `~/mlwx-ifs-pull.log` (outside the repo), read only, in Step 0 only.

## What this session is

D111 is recorded first. It accepts F159, records the owner's decision that no observation cleaning rule is adopted, records the owner's IFS hand pull (D108.2), and fixes IFS's daily maximum rule before any IFS value is read. Then the session checks the pull, compares IFS with the curve using session 114's script unchanged (D108.7, D110.2), adds IFS to the field guide, and records F160.

**Descriptive only (D107.2).** Nothing is selected or tuned. No value valid after 2026-07-31T23:00 UTC is read. Nothing from the 37 airports of F153.6, the MLwx-live repo or any 2026-27 file is read. No network access; nothing is installed; if a needed package is missing, stop. `data/processed/session113/work/` (empty, untracked) is not touched.

Write a checkpoint line to `notes/session-117-output.txt` after each step (D93.11). Stop rather than work around a failed check. Scripts print short summaries; full tables go to files (D93.12).

## Scope: the only files this session may create or edit

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`, `ANALYSIS.md`
- New files from `scripts/session114_comparisons.py --hourly --source ifs` and `--dailymax --source ifs` in `data/processed/session114_comparisons/` (only files whose names contain `ifs`; no existing file there is changed)
- `data/processed/session117_ifs/` (new folder: `--match` run with `--trial-dir`, and this session's own tables)
- `scripts/session117_ifs_guide.py` (new)
- `notes/session-117-output.txt` (new)

Everything else is out of scope, including SPEC.md, RESULTS.md, README.md, CLAUDE.md, `docs/PROJECT-INSTRUCTIONS.md`, every existing script (session 113's and 114's are run or imported, never edited), every existing file in `data/processed/` (including `session113/` and the existing `session114_comparisons/` files), `figures/`, every model folder, `src/mlwx/`, `tests/` and `requirements.txt`. Anything worth changing there is reported as an open item.

## Steps

### Step 0: Preflight and the pull check

- `git status` is clean apart from this session file and the untracked, empty `data/processed/session113/work/`. HEAD is session 116's commit (its title is the first line of `docs/commits/commit-116.txt`).
- The Live index lists D93, D103, D105, D106, D107, D108, D109, D110, F157, F158 and F159. No D111 or F160 exists in either DECISIONS file. None of this session's new paths exists, and no file in `session114_comparisons/` contains `ifs` except the AIFS ones (`aifs`).
- `scripts/session113_comparison_pull.py` matches `S113_SCRIPT_SHA256` in session 114's script; `scripts/session114_comparisons.py` is unchanged since session 114's commit (`git diff --stat 8ad82d4 -- scripts/session114_comparisons.py` is empty).
- The pull (D108.2), from `ifs_meta.txt`, the manifest and `ifs_gaps.csv`, without reading any temperature value: every file's SHA-256 and row count equals the meta file's; the override text names D108.2; the airports and windows are D107.5's. Per month and parameter (`2t`, `mx2t3`), count the cycle-steps expected, the messages kept and the gaps by reason, and check that kept plus gaps equals expected in every month. Confirm or explain the owner's three items: (1) 2024-02 has 1,808 `2t` messages for 1,856 cycle-steps (the planning chat counted 48 "not listed" gaps, from 2024-02-28T06Z; say which cycles); (2) value rows per message are 12 in 2023 and 18 from 2024-08 (the planning chat's reading: the development airports' two position sets only, 6 x 2, before the claim windows start, then 12 + 6; confirm from the rows, not the path); (3) "gaps equals units" in every month (say what the script means by it). Count `mx2t3` per month by reason (the planning chat's reading of the gap file: no message to 2024-11; rejected by the script's check, detail `shortName max_2t`, from 2025-02 to 2026-02; kept 2024-09 to 2025-02 in part and 2026-02 to 2026-07); confirm or correct.
- The pull log, read only: per run, the start, end, exit code, and counts of HTTP 503 or other errors, and any sign of a run stopped mid-write (the owner stopped one with `pkill`). Check that no chunk is written twice and that the manifest has no duplicate message for a cycle, step and parameter. Nothing from the log is copied into the repo apart from these counts in the output file.
- `numpy`, `lightgbm` and `matplotlib` import; record their versions. Record DECISIONS.md's byte size.

Stop if any check fails, or if the mx2t3 counts differ materially from D111.4's description (then report and wait).

### Step 1: Record D111

Append the block below to DECISIONS.md, byte-equal (copy it with `sed` from this file, then check with `diff` and `cmp`), and add D111 to the Live index. Count em-dashes in the block: must be 0.

~~~markdown
---

## 2026-10-18: Session 117 decision: F159 accepted, no observation cleaning rule, the owner's IFS pull recorded, and IFS's daily maximum rule fixed before any IFS value is read (owner, planning chat)

**D111. Owner decisions, planning chat (after session 116's commit): F159 accepted; no cleaning rule for the historical observations; the owner's IFS hand pull recorded (D108.2); IFS's daily maximum rule fixed, amending D108.4(b) for IFS; and how session 114's script is run for IFS.** Written at the start of session 117, before any other edit. No IFS temperature value has been read or scored. The planning chat read the pull's meta file and gap counts by month and reason (no values) before writing D111.4.

- **D111.1 F159 accepted,** with its readings. Session 116's exposure counts read each table row's lead as a row label to keep D109.5's definition of a target; this is accepted (no forecast value was read).
- **D111.2 No cleaning rule (owner).** The historical observations are accepted as they are: no rule for excluding observations is adopted, and none is proposed now. D109.6 stands, and every table, model and verdict is unchanged. A spike and range guard for live observations comes later, as a stage G fix and in the live test's scoring script, each in its own DECISIONS entry before it acts on any value (D110.7). Whether any rule can apply to stage B's test stays as D110.7 says.
- **D111.3 The IFS pull (owner, by hand, 2026-10-16 to 2026-10-18).** `scripts/session113_comparison_pull.py --pull ifs`, unchanged, at 8 requests at once throughout, with the override text of D108.2, over several runs: the first ended with exit 2 (26 of 36 months done); reruns met HTTP 503 throttling from ECMWF; an overnight run reached 31 of 36; two more finished it, the last with exit 0. One run was stopped by the owner with `pkill`. The meta file was written at 2026-10-18T16:15:52Z. The owner's log (`~/mlwx-ifs-pull.log`, outside the repo) is read only by session 117, for counts. Session 117 checks the pull before any value is read (D108.2).
- **D111.4 IFS's daily maximum (amends D108.4(b) for IFS only).** Primary: the highest of IFS's own 3-hourly 2 m temperature steps inside the local day, labelled "3-hourly steps", as session 114's script does (F157.7(1)). Why: IFS's maximum field (mx2t3) exists for only part of the window. It has no message up to 2024-11, and the pull's identity check rejected it from 2025-02 to 2026-02 (the GRIB short name reads `max_2t`; those values were not kept). A primary on mx2t3 would score a minority of days, in a few seasons, and not the same days at every airport. The steps exist on every pulled day. Second, descriptive: mx2t3, the highest of its 3-hour windows wholly inside the local day, on the days where it exists, with the curve and IFS's steps rescored on exactly those days. The formal test (D108.4(e)) uses the primary. The pull is not rerun for mx2t3; that is a reading for later.
- **D111.5 How it is run.** Session 114's script, unchanged (D108.7, D110.2): `--hourly --source ifs` and `--dailymax --source ifs` write their new IFS files to `data/processed/session114_comparisons/`, seed 114; `--match` is run with `--trial-dir data/processed/session117_ifs/`, because `match_counts.csv` is written once, and its non-IFS rows must equal the committed `match_counts.csv`. D107.9, D108.3 and D108.4 (with D111.4) apply. IFS goes into ANALYSIS.md by a new script that reads only those tables.
- **D111.6 Uses of spent data.** As D107.3: once scored here, IFS's test years at the 12 airports count as used for IFS.
- **D111.7 Next.** After session 117: the owner groups the MLwx folders under one parent folder, by hand, with no renaming and the planning chat's checklist; then the direction brainstorm in a new planning chat.
- **D111.8 Live index.** Removed (archived): D109, F158 and F159, which are settled. Added: D111 and F160. After session 117: D93, D103, D105, D106, D107, D108, D110, D111, F157, F160.
~~~

Stop if the block is not byte-equal.

### Step 2: Match (`--match`, trial folder)

Run `scripts/session114_comparisons.py --match --trial-dir data/processed/session117_ifs/`. Check that every non-IFS row of the new `match_counts.csv` equals the committed `data/processed/session114_comparisons/match_counts.csv` (TXN labels apart, which `--docs` filled there; report how they differ). Report IFS's paired hourly rows and D98.10 days per airport and test year, unpaired ones by reason, and the IFS cycle counts per test year against the pull's counts from Step 0 (session 114's F156.4 table has no IFS entry; say how the script handles that). Also count, per airport and test year, D98.10 days with an mx2t3 value.

Stop if any non-IFS row differs.

### Step 3: Hourly (`--hourly --source ifs`)

Run it. Report per airport (claim airports first): MAE of the curve, raw GFS and IFS on the paired rows, skill of the curve against IFS pooled with its interval, and the formal test with Benjamini-Hochberg across the 12; the grid (0.4, 0.25) and elevation labels' rows and MAE (D108.3: no elevation treatment on the 0.4 degree and Ni 1439 grids; "terrain from a later date" from 2024-02-03 to 2024-12-02).

### Step 4: Daily maximum (`--dailymax --source ifs`)

Run it. Report, per D111.4: primary (3-hourly steps) MAE and skill with intervals and the formal test; the curve sampled at IFS's 3-hourly steps against IFS (as F157.7(2) did for AIFS); and the mx2t3 subset descriptively (days, the curve, IFS steps and mx2t3 on the same days). Say whether the script's output already holds the mx2t3 subset comparison on common days; if not, compute it in `scripts/session117_ifs_guide.py` from the written tables and say so.

### Step 5: The field guide (`scripts/session117_ifs_guide.py`)

New script, modes `--render` and `--verify`. It reads only the IFS tables of Steps 2 to 4 (and, for comparison wording, the committed session 114 tables). `--render` edits ANALYSIS.md: every "pending (D108.2)" cell and the two "ECMWF IFS is pending (D108.2)" sentences in Part 1 replaced with IFS's figures in the same format as the other sources (item 1's short version: one clause on IFS; item 4's tables 2a and 2b and its formal-test lines); Part 2 gets new tables after E9, numbered E10 onward: IFS paired rows and days, hourly, hourly formal tests, daily maximum, its formal tests, the every-cycle table, and the mx2t3 subset, each with its file and labels (grid, elevation, "3-hourly steps", D111.4). No other text of ANALYSIS.md changes. `--verify`: every IFS number in ANALYSIS.md equals its table (mismatches must be 0), no em-dash in the edited text, and a `diff` of ANALYSIS.md against HEAD shows only the IFS edits. No figure is made (session 114's figures exclude IFS; reported as an open item).

Stop if `--verify` fails.

### Step 6: F160

Record F160 (at most about 40 lines, D93.10): D111 recorded; the pull check and the owner's three items; the match gate; IFS's hourly and daily maximum results per airport in ranges, claim airports first, with the formal tests' counts; the sampled-at-steps reading; the mx2t3 subset; grid and elevation segments; readings for the owner, labelled as readings (including whether the mx2t3 rejection is worth a later rerun, and any place where IFS changes the field guide's standing against competitors); what was not done (figures, mx2t3 rerun); pointers.

## End of session

As CLAUDE.md, with:

- STATUS.md overwritten as a current-only snapshot. The open question on an observation cleaning rule, the table-reader lead question and IFS's daily maximum rule are closed (D111.1, D111.2, D111.4). Its last line: "**Next planning session:** Review session 117 and commit. Then the owner groups the MLwx folders under one parent folder by hand (D111.7, the planning chat's checklist); then the direction brainstorm in a new chat."
- The archive step with D111.8's Live index, `--citations`, DECISIONS.md's byte size, and the scope-list check against this file's scope.
- `notes/session-117-output.txt` begins with the summary of at most 30 lines, then the checkpoints and full detail, including the end-of-session consistency checks.

Do not commit anything. Stop and wait for review.
