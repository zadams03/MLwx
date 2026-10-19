# Session 118: an audit of MLwx-live's runs, and two workflow fixes

Model: Opus. Network: read-only (a clone of zadams03/MLwx-live, `gh` reads of
its Actions runs and logs, one fetch of the public page). Nothing is pushed
anywhere, and no workflow is triggered.

## Read first

- `CLAUDE.md`, `STATUS.md` and the live `DECISIONS.md`, in full.
- SPEC section 2 (critical rules).
- From the archive, by number only: D104.4.
- `src/mlwx/runner.py` in full; `deploy/mlwx-live/.github/workflows/live.yml`
  in full.

## Purpose

Find out whether anything has gone wrong in the live runs since 12 Oct
2026, and close the faults the planning chat found by reading the code:

1. **Stale checkout.** A run that waits in the concurrency queue checks out
   the commit that was latest when it was triggered, not when it starts. It
   then works from an old log and state (the likely cause of the 17 Oct
   rebase conflict).
2. **A push that fails silently.** The push loop
   (`for i in 1 2 3; do git push && break; git pull --rebase; done`) ends
   green if the third push fails and the pull after it succeeds. Nothing is
   pushed, the page still publishes, and a later run issues the same cycle
   again with a later issue time.
3. **The "latest only" box.** On a manual run it jumps over earlier cycles,
   which the runner then marks "tracker order" for good (runner.py, D104.4).
4. **Late scheduled runs.** The runner catches up every cycle of the past 24
   hours in time order, so a cycle is lost only if no run happens for about
   20 hours (cycle + 4 h 10 to cycle + 24 h). Shorter gaps only make the
   page late.

**No error is computed (D105.6).** No observation is compared with any
forecast, baseline or corrected value; the snapshot files are counted, not
read for values. The page is read only for the cycle and issue time it shows.

## Scope list (the only files this session may create or edit)

- `DECISIONS.md` (D112, F161, the Live index; archive moves per D93.8)
- `DECISIONS-archive.md` (archive moves only)
- `STATUS.md`
- `deploy/mlwx-live/.github/workflows/live.yml`
- `scripts/session118_live_audit.py` (new)
- `data/processed/session118_runs.csv`, `data/processed/session118_cycles.csv` (new)
- `notes/session-118-output.txt` (new)

Temporary work (the clone, the push test repos) goes under `/tmp/` and is
listed in the output file. Nothing under `src/`, `tests/` or the owner's
local `../MLwx-live` folder is touched.

---

## Step 0: start state

`git status --porcelain` shows only `?? docs/sessions/session-118.md`. No
`session118_*` file exists under `scripts/`, `data/processed/` or `notes/`.
Run the test suite (`pytest -q`); it passes (181 tests, F160 or STATUS).
Run `gh auth status`; it reports a logged-in account.
**Stop** if any of these differs.

## Step 1: record D112

Append the D112 block below to `DECISIONS.md`, byte-equal (check with
`diff` against the block extracted from this prompt), and update the Live
index as D112.10 says. 0 em-dashes in the new text.
**Stop** on any difference.

```
---

## 2026-10-19: Session 118 decision: the order of the next work, and an audit of the live runs with workflow fixes (owner, planning chat)

**D112. Owner decisions, planning chat (direction brainstorm after session 117): the order of the next work, a read-only audit of MLwx-live's runs, and three workflow fixes.** Written at the start of session 118, before any other edit. No 2026-27 value has been read or scored.

- **D112.1 F160 accepted,** with its readings (F160.9), which stay open items.
- **D112.2 The order of the next work.** (1) This session, then the owner's redeploy. (2) IFS close-out: a check of whether IFS's cold error (F160.9) comes from the open-data product or the reading method, and the mx2t3 rerun accepting `max_2t` (F160.9(3)), each in its own entry. (3) The project health check (D109.8): an audit first, then fix sessions, in as many sessions as it needs, covering everything: the layout against D90.5, old paths, every verify and check script, stage B's frozen scripts after the folder move, the tests, consistency of SPEC, STATUS and DECISIONS, the Project-knowledge sync, and session 114's open items (F160.9(4)), the IFS figures included. (4) A README update, last in the health check. (5) Then the longer-term plan: stage B's timing, stages D, E, F and H, ANALYSIS.md's Part 3 candidates 6 and 7, rows at the airport's own position for the gridded sources, Gates C and D, WeatherNext, and whether to build a MOSMIX saver.
- **D112.3 The IFS check (planning chat's note, not fixed).** A difference from AIFS alone does not show a reading fault, since AIFS may remove IFS's own biases. The check looks for a reading fault's marks: error growing with the height gap between grid point and airport; a daily cycle shifted by local hour; a step at the 0.4 to 0.25 degree change. AIFS is a secondary reference only. If a fault is found, whether IFS is re-read and re-scored as an error correction is the owner's ruling, made when that session is planned.
- **D112.4 What a late run costs (runner.py).** The runner issues every cycle of the past 24 hours not yet logged, in time order. A cycle is lost only if no run happens between cycle + 4 h 10 min and cycle + 24 h. A shorter gap delays the page and the issue time only; the issued values do not depend on the run time beyond which observations had arrived.
- **D112.5 The audit (session 118).** Read-only: a fresh clone of MLwx-live and its Actions runs and logs. For every cycle from 2026-10-12 12z to the latest available at the audit: logged once, all leads, issue lag, snapshot present, stop list. For every run: trigger, created and start times, commit checked out against main's head at its start, result, and the cycles its log says it issued. It answers whether any cycle was lost, issued twice, or issued from a stale checkout, and whether any push failed silently. The page's shown cycle is compared with the log's latest. No error is computed (D105.6).
- **D112.6 The workflow fixes (template, `deploy/mlwx-live/.github/workflows/live.yml`).** (a) This repo's checkout takes `ref: main`, so a queued run starts from the latest commit. (b) The commit step fails the job, before the page is published, unless the push landed (local HEAD equals `origin/main` after a fetch); a failed rebase is aborted and also fails the job. (c) The manual run's `latest_only` input is removed; the runner's `--latest-only` flag stays for dry runs. (d) The schedule becomes `15,40 * * * *`: a cycle is available from cycle + 4 h 10 min, and the owner wants the page as fresh as possible. An outside scheduler is considered only if issue lags stay long after the redeploy.
- **D112.7 The live test (D105.5(k)).** None of D112.6 changes a logged forecast value; it can change issue times only. The live test treats every row unchanged. If the audit finds a cycle issued twice, a log file changed after it was first written, or a cycle lost, session 118 records it and the owner decides how D105.5 treats it.
- **D112.8 The redeploy (owner, after session 118's commit).** The owner copies the template into MLwx-live with `MLWX_COMMIT` and `MODELS_TAG` unchanged from the deployed values (no code change). The deployed values are recorded in the next session's entry. Until then: no manual run between :35 and :55 past the hour, and "latest only" left unticked.
- **D112.9 Plan.** Session 118: this entry, the audit, the fixes, F161. Then the redeploy, then D112.2's item 2.
- **D112.10 Live index.** Removed: none. Added: D112 and F161 (F161 when it is written).
```

## Step 2: the clone and the template gate

Clone `https://github.com/zadams03/MLwx-live` into a new `/tmp/` folder.
Record its HEAD commit and time. Compare its `.github/workflows/live.yml`
with the template: they must differ only in the two `SET-AT-DEPLOY` lines
(D105.9). Record the deployed `MLWX_COMMIT` and `MODELS_TAG`.
**Stop** if any other line differs.

## Step 3: the audit script

Write `scripts/session118_live_audit.py`. It reads the clone and `gh` output
only, writes the two CSVs, and prints a short summary (CLAUDE.md D93.12).

**(a) Runs.** `gh run list --repo zadams03/MLwx-live --workflow live.yml
--limit 1000 --json databaseId,event,status,conclusion,createdAt,startedAt,updatedAt,headSha`.
For each run: the main head at `startedAt` (the latest commit on the clone's
`main` with committer date at or before `startedAt`), and whether `headSha`
is older (a stale checkout). For each run, read its log
(`gh run view <id> --repo zadams03/MLwx-live --log`, parsed in the script,
never printed) for: the cycles the runner says it issued (`issued N rows to
...`), its final summary line and exit code, and whether the push step
pushed, retried, hit a rebase conflict, or ended without pushing. A log no
longer available is counted, not guessed. One row per run in
`data/processed/session118_runs.csv`.

**(b) Cycles.** Every cycle hour (00, 06, 12, 18 UTC) from 2026-10-12 12z
to the latest cycle available at the clone's HEAD time
(`runner.available_cycles` rule). For each: the log file present or not,
the commits that added or changed it (`git log --follow --diff-filter`), row
count, airports, leads 3 to 48 complete, the `issued` value(s), issue lag
(issued minus cycle), the snapshot file present and its row count, any
stop-list entry with its reason, and which runs' logs claim to have issued
it. One row per cycle in `data/processed/session118_cycles.csv`.

**(c) Cadence.** Scheduled runs per UTC day (against 24 expected before the
redeploy); each scheduled run's delay (`createdAt` minus the latest :40 slot
at or before it; flag any delay that could be over 60 minutes as
ambiguous); gaps between consecutive runs of any trigger (median, 90th
percentile, maximum); any gap over 20 hours.

**(d) The page.** Fetch https://zadams03.github.io/MLwx-live/ once; record
the cycle and issue time it shows and whether they match the latest logged
cycle and its `issued` value.

Checks: every run in (a) has a row; every cycle in (b) has a row; the
counts in the summary add up. **Stop** if the script reads any value from a
snapshot or computes any difference between an observation and a forecast.

## Step 4: findings

In the output file, answer each question with numbers, citing run IDs and
cycles:

1. Was any cycle lost (not logged and not a tracker-order skip before
   2026-10-12 12z)? Why?
2. Was any cycle issued by more than one run, or any log file changed after
   it was first added?
3. Did any run check out a stale commit? What happened in each (including
   the 17 Oct failure)?
4. Did any push fail silently (the run ended green, its log shows a cycle
   issued, and that run's commit is not on main)?
5. Was the "latest only" box ever used, and did it skip a cycle?
6. Scheduled cadence and issue lag: runs per day, delays, gaps, issue lag
   per cycle (median and maximum).
7. Does the page match the log?
8. Anything else the audit found that is wrong or odd (reported as an
   open question, not fixed).

If the answer to 1, 2 or 4 is yes, still make Step 5's fixes (they stop it
happening again), and report it at the top of the output file for the
owner, who decides how the live test treats it (D112.7).

## Step 5: the template fixes (D112.6)

Edit only `deploy/mlwx-live/.github/workflows/live.yml`:

- (a) add `ref: main` to the checkout of this repo;
- (b) rewrite the push in the commit step so that: a push is tried up to 3
  times with `git pull --rebase` between tries; a failed rebase is aborted
  (`git rebase --abort`) and ends the loop; afterwards `git fetch origin
  main` runs, and the step exits 1 with a clear message unless local HEAD
  equals `origin/main`. The step runs before the page steps, so a failed
  push stops the page from publishing;
- (c) remove the `latest_only` input from `workflow_dispatch` and the
  `--latest-only` line from the runner step (`workflow_dispatch:` stays,
  with no inputs);
- (d) set the schedule to one line, `- cron: "15,40 * * * *"`;
- update the header comment to match (no em-dashes); nothing else changes.

Checks: the file parses as YAML (PyYAML if installed; otherwise
`python -c` with a minimal check recorded); `diff` against the original
shows only these changes.

**Push test.** In `/tmp/`, a bare repo and two clones. Extract the commit
step's `run` block from the edited template (with PyYAML if installed, else
by its lines), and run it with `bash -e` in clone A in three cases:
(i) clone B pushed a non-conflicting commit first: the step rebases,
pushes, exits 0, and HEAD equals `origin/main`;
(ii) clone B pushed a conflicting change to the same file first: the rebase
is aborted, the step exits 1;
(iii) the bare repo's `pre-receive` hook rejects every push: the step exits
1.
Also (iv) nothing to commit: exits 0. The step's `git add log state` and
`obs` line are kept; the test creates those folders.
**Stop** if any case gives the wrong exit code.

## Step 6: record F161

Append F161 to `DECISIONS.md`: heading
`## 2026-10-19: Session 118 finding: the live runs audited, and the workflow fixes`,
a bold lead sentence (what was done, read-only, no error computed,
network used, run date, Python version), then numbered points: F161.1
D112 recorded; F161.2 the clone and template gate (deployed values);
F161.3 to F161.10 Step 4's answers 1 to 8; F161.11 the template diff and
the push test results; F161.12 what this did not do. Keep within D93's
finding-length rule. Update the Live index line for F161.

## End of session

Follow CLAUDE.md's end-of-session steps, including:

- the scope-list check (`git status --porcelain` against the list above);
- the archive check by the Live index (D93.8) and DECISIONS.md under
  80,000 bytes (D93.9), with the byte count;
- the consistency-check findings written into
  `notes/session-118-output.txt`;
- STATUS.md overwritten as a current-only snapshot: stage G's line notes the
  fixes are in the template and await the owner's redeploy (D112.8); the
  carried items add D112.8's interim rule; the open questions drop the
  concurrency and cron items, and add anything F161.10 raises. It ends with:

  **Next planning session:** Review session 118 and commit; then the owner
  redeploys MLwx-live from the template (D112.8), one step at a time. Then
  D112.2's order: the IFS close-out (the reading-fault check and the mx2t3
  rerun), the project health check (audit, then fixes, ending with the
  README update), then the longer-term plan.

Stop and wait for review. Do not commit anything.
