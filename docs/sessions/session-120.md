# Session 120: the project health check, audit part 1 (the code)

A routine health check (D112.2 item 3). Nothing is suspected to be wrong.
The aim is evidence: every check that passes is recorded as OK, and the
known items are pinned to exact files and lines so the fix sessions are
small. This session is read-only: it fixes nothing.

## Read first

- STATUS.md in full; SPEC section 2.
- The live DECISIONS.md in full (this session records a decision).
- Archived entries, by number (grep as CLAUDE.md says): D62.3(a), D73.8,
  D90.4, D90.5, D90.6, D91.3, D91.4, D93.8, D93.9, D98.2, D102.3, D105.5,
  D105.6, D105.7, F129.7.
- Live entries the steps cite: D112.2, D112.4, D112.6, D113.2, D113.6(e),
  D113.7, F160.9(4), F161.2, F161.8, F161.10, F162.3, F162.9(6).

## Limits (D114.4 to D114.6, binding in every step)

- No existing tracked file is edited, except DECISIONS.md, DECISIONS-archive.md
  and STATUS.md in Step 1 and the end steps.
- Frozen scripts are never edited (D62.3(a)). They are run only in offline
  guard or gate modes that read no data valid on or after 2026-08-01.
- No 2026-27 value is read or scored. No MLwx-live observation snapshot is
  opened beyond counting lines. No error is computed (D105.6). The MLwx-live
  log is read only for its airport, cycle, lead, issue time, commit, model and
  version columns, as F161 did.
- Network only in Steps 8 and 9, and only as D114.5 lists.
- A script mode is run only if it writes nothing, or writes only into a
  temporary folder (`mktemp -d`) outside the repo. A mode that would write into
  the repo, needs the GRIB cache, needs the network outside Steps 8 and 9, or
  reads a 2026-27 file is not run; it is listed with the reason.
- Any single run longer than 30 minutes is stopped and listed as "not run:
  over 30 min".

## Steps

### Step 0. Start state

Record `git rev-parse HEAD`, `git status --porcelain` (must be clean apart from
this prompt file), Python and package versions in `.venv`, and run
`python3 -m unittest discover -s tests` in the venv.
Check: tests OK (181 expected). Stop if the tree is not clean or a test fails.

### Step 1. Record D114

Append the block below to DECISIONS.md with `sed`, byte-equal (`diff` and
`cmp`), 0 em-dashes, and add D114 to the Live index with the line
`- D114: F162 accepted, the layout baseline, and the project health check's plan and audit limits.`
Stop if it is not byte-equal.

```
---

## 2026-10-21: Session 120 decision: F162 accepted, the layout baseline, and the project health check's plan and audit limits (owner, planning chat)

**D114. Owner decisions, planning chat (after session 119's commit): F162 accepted; the layout baseline for the health check; the health check's plan; and the audit's limits.** Written at the start of session 120, before any other edit. No 2026-27 value has been read or scored.

- **D114.1 F162 accepted,** with its readings (F162.9). F162.9(6)'s two extra decode fetches are made in session 120.
- **D114.2 The layout baseline (owner).** The health check checks the layout against D91.3, which replaced D90.5 (D91.4), not against D90.5 as D109.8 and D112.2 say. Each folder or root file added after D91.3 is traced to the entry that added it. D109.8 is answered as a reading.
- **D114.3 The health check's plan.** It is a routine check, not a response to a suspected fault. Session 120 audits the code (MLwx and MLwx-live). Session 121 audits the record (SPEC, STATUS, DECISIONS, RESULTS, ANALYSIS, README, CLAUDE, PROJECT-INSTRUCTIONS and the Project-knowledge sync). Fix sessions follow, planned from the two registers, each with its own entry; the README update (D112.2 item 4) is last. Scripts that need the GRIB cache are run in a fix session when the owner attaches the drive.
- **D114.4 The audit's limits.** Read-only: no existing tracked file is fixed or edited, apart from the session's own record steps. Frozen scripts are never edited (D62.3(a)) and are run only in offline guard or gate modes that read no data valid on or after 2026-08-01; their SHA-256 values are checked against the recorded ones. No 2026-27 value is read or scored; no MLwx-live observation snapshot is read beyond line counts; no error is computed (D105.6).
- **D114.5 Network (session 120).** A fresh clone of MLwx-live into a temporary folder; `gh` run lists and run logs for MLwx-live; one fetch of the public page; and two byte-range fetches for F162.9(6), by D113.7's method, judged by D113.6(e)'s mark. Nothing is pushed and no workflow is triggered.
- **D114.6 The GRIB cache.** The drive is not attached for session 120. A script mode that needs the cache is listed as "not run: needs cache".
- **D114.7 The register.** Each audit session writes a register with one row per item checked: id, area, file, what was checked, result, severity (OK, cosmetic, stale, wrong, blocks), proposed fix, and four flags: the fix would touch a record file (never edited, D90.4, D90.6); a frozen script; the live test (D105.5(k)); or needs an owner ruling. Rows that pass are kept as OK.
- **D114.8 Live index.** Removed: none. Added: D114 and F163 (F163 when it is written).
```

### Step 2. Layout

List tracked files (`git ls-files`) by top-level folder and root file. Check
them against D91.3. Trace every addition after D91.3 (at least `src/`,
`tests/`, `deploy/`, `ANALYSIS.md`, `docs/sessions/`, `docs/commits/`) to the
entry that added it (grep the two DECISIONS files). List untracked and ignored
items (`.DS_Store`, `.pytest_cache`, `__pycache__`, `.claude/`, `.venv`) and
whether `.gitignore` covers each.
Check: every tracked top-level item is either in D91.3 or traced. An item
with no entry is a register row, not a stop.

### Step 3. Old paths

`git grep -n` for the old repo path (`Coding Projects/MLwx` not followed by
`-all`) and for any other `/Users/` path. Expect 48 files. For each file
record its class: record (DECISIONS, archive, `docs/sessions/`,
`docs/commits/`, `notes/`: never edited), frozen script, or live code,
config or doc; and whether the path is used at run time (a run would break)
or is text only.
Check: count reported; if it is not 48, report the difference, do not stop.

### Step 4. Script inventory

For every Python file in `scripts/`, `src/` and `deploy/` (and any shell or
workflow file): its modes (argparse flags), which are verify, check, gate or
guard modes, what it reads by path (SPEC or DECISIONS text in particular,
F151.6), whether it is frozen (D62.3(a), D93.8), and whether each mode needs
the cache, the network or 2026-27 data. Write it to
`data/processed/session120_audit/scripts.csv`.
For each frozen script, compute its SHA-256 and compare with its recorded
value (F129.7 and each frozen script's own entry).
Check: every script has a row; every frozen script's SHA-256 equals its
recorded value. A mismatch is a "blocks" row and is reported at once in
chat, but the session continues.

### Step 5. Run the checks

Run every mode Step 4 marks as a verify, check, gate or guard mode that the
Limits allow, including `scripts/session114_comparisons.py --verify` and
`scripts/archive_decisions.py --citations`. For each: command, exit code,
time, PASS or FAIL, and the first failing line. For session 114's
`--verify`, give the exact cause of the Part 1 failure. Stage B's frozen
scripts: their offline guard modes only, checking they still run after the
folder move. Every mode not run is listed with its reason.
Check: a table of every eligible mode. Any FAIL other than session 114's
known one is a register row; report it in chat; do not fix.

### Step 6. Tests and environment

Run the suite (as Step 0). Record whether `pytest` is in `.venv`, which
areas `tests/` covers and which have no test, and `requirements.txt`
against `pip freeze` in the venv (missing, extra, version differences).
Check: tables written. No install.

### Step 7. Session 114's open items (F160.9(4))

Pin each item to exact files and lines: `part1.md` and
`part2_comparisons.md` out of date (what differs from ANALYSIS.md); no IFS
figure; `subdaily_max` not checking that every window is present; no IFS
entry in `F156_4`. For each, say what a fix would change and whether it
touches a record file.
Check: four register rows, each with file and line references.

### Step 8. MLwx-live (network, D114.5)

Fresh clone into a temporary folder; record HEAD. Then:
- `diff` the deployed `.github/workflows/live.yml` against the template
  `deploy/mlwx-live/.github/workflows/live.yml`: only the two
  `SET-AT-DEPLOY` lines may differ (D113.2).
- Stale text in the template and the deployed repo: `deploy/mlwx-live/README.md`
  line 65 (":40 hourly") and any other text that disagrees with D112.6.
- The actions forced from Node.js 20 (F161.10(4)): each action and the
  version it uses, and the current major version that runs on Node.js 24
  (from the `gh` logs' warnings and the actions' own repos).
- `setup-python`'s version and what the runs used.
- How many runs since the redeploy (run 39488813037) committed only the
  state's `last_run`.
- Since the redeploy, by F161.8's method: scheduled runs per slot (:15 and
  :40 counted apart), gaps between runs, and issue lag per cycle; and, by
  F161.3's method, any cycle lost or issued twice since 2026-10-19T12z.
  Note how few days of data there are.
- One fetch of the public page: its latest cycle against the log's latest.
Check: each item a register row. No push, no workflow run.

### Step 9. T5's two extra fetches (F162.9(6))

Using `scripts/session119_ifs_check.py`'s decode functions imported
read-only (the script is not edited), fetch 2 messages from the main 0.25
degree grid: one on its first 00z date and one on its last, at the step
nearest 24 h that exists on each date. Fix the two picks in the new script
before fetching. Judge them by D113.6(e)'s mark. Delete the bytes after.
Check: 2 fetches, mark shown or not shown. A mark is reported in chat at
once and goes to the owner (D112.3).

### Step 10. Register and finding

Write `notes/session-120-register.csv` (D114.7's columns), one row per
item checked in Steps 2 to 9, OK rows included. Group the non-OK rows into
proposed fix sessions (which can share a session, which need the cache,
which need an owner ruling, which touch the live test), in the output file.
Then write F163 (at most about 40 lines, CLAUDE.md): counts by severity, the
known items confirmed, anything new, the proposed grouping, readings for the
owner, what was not done, and pointers.

## Scope list

May create or edit only:
- `DECISIONS.md` (D114, F163, Live index), `DECISIONS-archive.md` (archive step), `STATUS.md`
- `scripts/session120_audit.py` (new)
- `data/processed/session120_audit/` (new)
- `notes/session-120-output.txt`, `notes/session-120-register.csv` (new)
- temporary folders outside the repo (deleted at the end)

## End of session

Follow CLAUDE.md's end-of-session steps. STATUS's "Next planning session"
line: review session 120 and commit; then plan session 121, the audit of the
record (D114.3). The consistency-check findings go into the output file too.
Stop and wait for review. Do not commit.
