# Session 123: fix group (3), MLwx-live

**Model:** Opus. **Network:** read-only, as D117.8. **GRIB cache:** not needed.

## Read first

- `CLAUDE.md` and `STATUS.md` in full.
- `DECISIONS.md`: D105 (D105.5 (k), D105.6, D105.7, D105.9), D112.4 to
  D112.8, D116.10, F163.8, F163.10, and D117 once Step 1 has added it.
- `DECISIONS-archive.md`, by entry only: F161.8, F161.10, F161.11.
- `notes/session-120-output.txt`: the MLwx-live section only (F163.8's
  detail, including the Node.js 24 majors it lists).
- Every file under `deploy/mlwx-live/` in full.
- `scripts/session118_live_audit.py` in full.

## Scope

May create or edit only:

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`
- `deploy/mlwx-live/.github/workflows/live.yml`, `deploy/mlwx-live/README.md`
- `scripts/session123_live_lag.py` (only if Step 2 needs it)
- `data/processed/session123_runs.csv`, `data/processed/session123_cycles.csv`
- `tests/test_live_template.py`
- `notes/session-123-output.txt`

Never touched: `src/`, frozen scripts, any script whose SHA-256 is
recorded elsewhere (D116.10), the owner's `../MLwx-live`,
`../MLwx-live-build`, SPEC, RESULTS, ANALYSIS, the READMEs outside
`deploy/mlwx-live/`. Nothing is installed. No 2026-27 value is read or
scored; MLwx-live's `obs/` files are counted by lines only; no error is
computed (D105.6). Nothing is pushed and no workflow is triggered.

## Steps

**Step 0. Start.** Record HEAD, check the tree is clean, run
`.venv/bin/python -m unittest discover -s tests` (expect 185 OK), and
record DECISIONS.md's byte size. Stop if the tree is not clean or any test
fails.

**Step 1. Record D117.** Append the block below to DECISIONS.md with
`sed` from this file, check it byte-equal (`diff` and `cmp`) and count
em-dashes (expect 0). Stop on any difference.

```
---

## 2026-10-27: Session 123 decision: F165 accepted, fix group (3) for MLwx-live, and the issue-lag re-measure (owner, planning chat)

**D117. Owner decisions, planning chat (after session 122's commit): F165 accepted; the order of the remaining fix sessions; the issue-lag re-measure; the outside scheduler left open; MLwx-live's template changes and how the live test treats them; session 123's scope; and Live index changes.** Written at the start of session 123, before any other edit. No 2026-27 value has been read or scored.

- **D117.1 F165 accepted,** with its readings (F165.11).
- **D117.2 Order (owner).** Fix group (3) now. Then groups (7) and (9) together in one session, whose planning rules on SP05, SP07, SP08, PI07 with PK10, DE03 and S06. Group (4) when the drive is attached. Group (6), the README, last (D115.7).
- **D117.3 The issue lag (F163.8, D112.6(d)).** Re-measured read-only, from the redeploy's check run 39488813037 (2026-10-20) to the latest cycle available at session 123, by D112.5's method and with F161.8's measures, scheduled and manual runs reported apart. Owner ruling: the 2026-10-21 18z cycle was issued by a manual run and counts as manual; so does any other cycle the run log shows issued by a manual run (2026-10-22 12z, run 39815698496). No error is computed (D105.6).
- **D117.4 The outside scheduler stays open.** The owner rules on it in a later entry, after reading D117.3's figures. Nothing is built for it in session 123.
- **D117.5 Template changes (`deploy/mlwx-live/`).** (a) The six actions of F161.10(4) move to their first major whose `action.yml` runs on Node.js 24, each confirmed from that tag. (b) `setup-python`'s version is pinned to `3.12.15`, the version every run has used (F161.10(5), F163.8). (c) A run whose only change in the tree is the value of `last_run.at` in `state/tracker_gfs.json` commits nothing, pushes nothing and does not publish the page, and exits 0. Any other change (a log or obs file, a stop, a change of `last_run.status`) keeps D112.6(b)'s commit, push, check and page unchanged. Why narrowed: `page.py` reads `last_run.status` to show the "waiting" note, and a stopped cycle is recorded in `state/` only (session 123, Step 3). (d) The template README's stale lines (F163.8) are brought into line with D112.6 and this entry. `MLWX_COMMIT` and `MODELS_TAG` stay as deployed, and nothing under `src/` changes.
- **D117.6 The live test (D105.5(k)).** No model changes, and no code that writes a logged value: the runner and models are those already pinned and Python is the version already used; (c) stops only commits that change `last_run.at` alone, which no code reads (session 123, Step 3). The live test treats every row unchanged. Cost: on a run that skips, the page's build time is not refreshed.
- **D117.7 The redeploy (owner, after session 123's commit).** The owner copies the template's workflow and README into MLwx-live with `MLWX_COMMIT` and `MODELS_TAG` unchanged. The deployed values are recorded in the next session's entry. D112.8's rule on manual runs holds until then.
- **D117.8 Network (session 123).** A fresh clone of MLwx-live into a temporary folder; `gh` run lists and run logs for MLwx-live; read-only `gh api` calls for the six actions' tags and their `action.yml`; one fetch of the public page. Nothing is pushed and no workflow is triggered.
- **D117.9 Plan.** Session 123: this entry, the re-measure, the template changes and their checks, a test of the template, F166. Then the owner's redeploy, then groups (7) and (9).
- **D117.10 Live index.** Removed: none. Added: D117 and F166 (F166 when it is written).
```

**Step 2. The issue lag (D117.3).** Make a fresh clone of MLwx-live in a
temporary folder. Before running `session118_live_audit.py`, check under
D116.10 whether its SHA-256 is recorded by another script, a test or a
meta file, and report it. If it can measure the new window unchanged
(by its own arguments), run it; otherwise write
`scripts/session123_live_lag.py`, which imports it and does not change
it. Write `data/processed/session123_runs.csv` and
`session123_cycles.csv`. Report, for the window, with the 2026-10-21 18z
cycle counted as manual:
- scheduled runs against :15 and :40 slots (count and %), per UTC day;
- delay to the latest slot (median, max); gaps between runs (median,
  90th percentile, max);
- issue lag per cycle (median, 90th percentile, min, max), all cycles
  and scheduled-issued only;
- cycles lost, issued twice, log or obs files changed after first
  written; commits that changed only `state/`;
- the Python version each run used;
- the page's shown cycle against the log's latest.
Put F161.8's and F163.8's figures beside them. **Stop** if any cycle was
lost or issued twice, or any log or obs file changed after it was
written (D112.7: the owner rules).

**Step 3. What a run that issues nothing changes (D117.6).** In the
clone, for every commit since the redeploy that touches only `state/`,
report which keys changed. In MLwx at `d6ca3e4` (the pinned commit),
find every reader of `last_run`, in `src/` and in the workflow. **Stop**
before Step 4(c) if any such commit changes anything besides
`last_run.at`, or if any code reads `last_run.at`; report and wait for
the owner. (Revised after the first run stopped here: `page.py` reads
`last_run.status` only, which D117.5(c) now keeps.) Also
report, as a reading only, whether the page shows anything that changes
when a run issues nothing.

**Step 4. Template changes (D117.5).** Edit
`deploy/mlwx-live/.github/workflows/live.yml` and
`deploy/mlwx-live/README.md` only.
- (a) For each of the six actions, confirm by `gh api` the first major
  tag whose `action.yml` has `runs.using: node24`, and use it. Record
  each tag in the output file. Stop if any has no such major.
- (b) `python-version: "3.12.15"`. Stop if Step 2 found any run on a
  different version.
- (c) After the runner, decide whether the only change in the tree
  (tracked and untracked) is the value of `last_run.at` in
  `state/tracker_gfs.json`, comparing the file with `HEAD`'s copy with
  that one key removed from both (Python's standard library only). If
  so, or if nothing changed: no commit, no push, the page steps are
  skipped, the job ends green. Otherwise the existing commit, push,
  check and page run unchanged. Keep the job's failure rule (runner exit code 3)
  unchanged.
- (d) README: correct the stale lines F163.8 names (l.65 to 68 against
  D112.6) and anything else now untrue (airport count 49, the schedule,
  (c)). Facts only; no accuracy figure.
Checks: YAML parses (any parser already in `.venv` or the system; do not
install one); the diff holds only (a) to (d) and keeps the two
`SET-AT-DEPLOY` lines. Then re-run F161.11's push test on the new step,
in temporary repos, with `bash -e` and GitHub's flags: (i) only `last_run.at`
changed: exit 0, no commit, page skipped; (i-b) `last_run.status`
changed to "waiting", nothing else: commit, push and page run;
(i-c) a stop added to `state/`, no log file: commit, push and page run;
(ii) a new log file, non-conflicting push: exit 0, HEAD equals the
remote; (iii) conflicting push first: exit 1, rebase aborted; (iv) every
push rejected: exit 1 after 3 tries; (v) nothing changed at all: exit 0,
page skipped. Stop on any wrong result.

**Step 5. Test.** Add `tests/test_live_template.py` (unittest): the
workflow's cron is `15,40 * * * *`; `python-version` is `3.12.15`; each
of the six actions is at the major recorded in Step 4(a) (held as
constants, D98.2); the two `SET-AT-DEPLOY` lines are present; the skip
condition of Step 4(c) is present and, run on synthetic state files, skips
on a `last_run.at`-only change and does not skip on a `last_run.status`
change or an added stop. Run the full suite (expect 185 plus
the new tests, all OK).

**Step 6. F166.** At most about 40 lines (D93.10): Steps 0 to 5's
results, Step 2's headline figures beside F161.8's and F163.8's, the six
action tags, readings for the owner (including the issue lag as input to
D117.4), what was not done, and pointers.

## End of session

Follow CLAUDE.md's end-of-session steps 1 to 5 with session number 123.
STATUS.md: fix group (3) is prepared, not yet live; the redeploy (D117.7)
is the next owner action; the outside scheduler is an open ruling with
Step 2's figures. It ends with: **Next planning session:** Review session
123 and commit; the owner redeploys MLwx-live (D117.7); then plan fix
groups (7) and (9) together, with the rulings of D117.2. The
consistency-check findings go into `notes/session-123-output.txt`, not
only the chat. Stop and wait for the owner's review. Do not commit.
