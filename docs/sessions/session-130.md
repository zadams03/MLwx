# Session 130: an independent code review of everything that runs live or judges a result

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
This session is a **read-only review** with fresh eyes. It reads the code
that runs live (the live tool, its workflow, the MOSMIX saver) and the
code that will judge a result (stage B's build and scoring path, and the
live test's frozen scoring script), and writes a findings register. It
fixes nothing: every fix is planned in session 131. It also assesses the
outside scheduler, reopened by D124.3. Recommended model: the strongest
available.

Review stance: assume nothing is right because it passed before. Look
for what would silently give a wrong number, lose data, score something
that should not be scored, or stop working when GFS v17 arrives. Read
the code, not its docstrings' claims about itself. Every finding cites
file and line, and says how it was confirmed (read, test, run).

## Read first

- STATUS.md in full; SPEC section 2; SPEC section 9; the live
  DECISIONS.md in full.
- Archived, one entry at a time by line range, as each area needs them:
  D73 (all), D77.6, D79, D97.4 to D97.7, D98.10, D100.5, D103 (all, live),
  D105 (all, live), D112.4, D112.6, D117.5, D118.2 to D118.4, F152.7,
  F152.8, F154.7, F166, D122.3 to D122.6, D123, F172.
- The code under review, in full (Steps 3 to 7 list it).
- `notes/session-121-register.csv`: its header and two rows only, for the
  register's format.

## Rules for this session

- **Read-only.** No existing file under `scripts/`, `src/`, `tests/`,
  `deploy/`, `data/` or `figures/` is edited. A finding is never fixed
  here, even when the fix looks one line long.
- **Allowed to run:** the test suite; stage B's three `--guard-check`
  modes; `session129_live_score.py --inventory` on a fresh clone of
  MLwx-live; small throwaway scripts in a `mktemp -d` folder that call
  the code under review on synthetic inputs, to confirm a suspected bug
  (keep each such script's text in the output file). Nothing else is run.
- **No live observation (D105.5(l), D105.6, D123.2).** Nothing valid on or
  after 2026-10-12 is fetched from IEM or opened from MLwx-live's `obs/`.
  No error, MAE or difference involving a live forecast is computed.
  `session129_live_score.py --score` is never run.
- **Network:** GitHub only: fresh clones of the public `zadams03/MLwx-live`,
  and the public Actions run list of MLwx-live through GitHub's API
  (`gh run list` or `gh api`, read-only), for Step 8. `zadams03/MLwx-mosmix`
  is private; review its template here, not the deployed repository.
- **Severity,** one per finding: **critical** (could change a verdict,
  score a row that should not be scored, lose data for good, or break
  the live tool), **major** (wrong but caught, or wrong only in a case
  that has not happened yet, such as v17), **minor** (robustness,
  clarity, a missing test), **note** (worth knowing, no change), **efficiency** (Step 8b only).
- **Frozen code (D62.3(a), D116.10, D123.2).** A finding in a frozen
  script (`session86_forward_build.py`, `session87_forward_score.py`,
  `session87_forward_competitors.py`, `session129_live_score.py`, and the
  others `tests/test_frozen_scripts.py` lists) is still recorded; its
  proposed fix names a route that leaves the script unedited (a new
  script, a wrapper, or an owner's ruling recorded before the look), and
  says whether the fix would have to be in place before that script's
  look.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md,
notes/session-130-register.csv (new), notes/session-130-output.txt (new).

## Steps

**Step 1. Start checks.** HEAD is `3bf156f`; the tree is clean apart from
this prompt. Tests: 333 OK (1 skipped). SPEC 3.4's span SHA-256
`a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
Stage B's three `--guard-check` modes pass. Stop if any check fails.

**Step 2. Record D124.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-14: Session 130 decision: F172 accepted, the MOSMIX saver deployed, the outside scheduler reopened, and an independent code review (owner, planning chat)

**D124. Owner decisions, planning chat (after session 129's commit): F172 accepted; the MOSMIX saver's deployment recorded; the outside scheduler reopened under D118.4; and session 130's read-only code review.** Written at the start of session 130, before any other edit. No 2026-27 value has been read or scored, and no observation valid on or after 2026-10-12 has been read.

- **D124.1 F172 accepted,** with its 19 readings (F172.3) as written. `session129_live_score.py` is frozen from commit `3bf156f` (D123.2).
- **D124.2 The MOSMIX saver is deployed (owner, by hand, 2026-11-14).** Private repository `zadams03/MLwx-mosmix`, created empty; the five template files copied from `deploy/mlwx-mosmix/` at `73370ed` and pushed to `main`; Actions given read and write permission; one run by hand was green. It created the Release with tag `mosmix-2026-11` (title "MOSMIX_L 2026-11") holding tar assets, and committed `manifest/2026-11.csv`. Saving starts from the issues on DWD's server at that run; earlier days are lost, as D81.5 accepts.
- **D124.3 The outside scheduler is reopened (D118.4).** Cycle 2026-11-09 06z was issued 12.82 h after its cycle (F172), above D118.4's 12 h mark. Nothing was lost (D112.4). Session 130 assesses the options with numbers; the owner decides in session 131's entry.
- **D124.4 Session 130's scope.** A read-only review, as a findings register, of: the live tool (`src/mlwx/` and the workflow template `deploy/mlwx-live/`); the MOSMIX saver template; stage B's build and scoring path (`session86_forward_build.py`, its wrapper `session129_stageb_gate.py`, `session87_forward_score.py`, `session87_forward_competitors.py`); and the live test's scoring script (`session129_live_score.py`). Readiness for GFS v17 is checked in each. Nothing is fixed; fixes are planned in session 131, each finding in a frozen script by a route that leaves it unedited (D116.10). No logged value, model or live file changes, so D105.5(k) is not engaged.
- **D124.5 Live index.** Removed (archived): D123 and F172, which are settled (D123.2's freeze is carried by D124.1). Added: D124 and F173 (F173 when it is written). After session 130: D93, D103, D105, D118, D124, F173.
```

**Step 3. The live tool** (`src/mlwx/`, all modules; `deploy/mlwx-live/`).
Check at least: the GFS fetch and its guard (identity keys, grid, what
happens on a mismatch; D103.7, D103.10); the four grid points, weights
and elevation constant against the records; the features against the
record's build (SPEC 8.8); that the model files loaded are the ones whose
SHA-256 is held (D103.5); the tracker (D97.4 to D97.7, D103.6: only
errors valid before the cycle, ascending valid time, each error once,
weight 0.02, which errors update which cell, what happens after a missed
or late cycle); the runner's catch-up and order (F152.8, D112.4: can a
cycle ever be issued twice, out of order, or from a stale state?); the
write-once log and its failure modes; the state file (100 stops kept,
F172.3(9)); the daily maximum per local day for all 49 time zones,
clock-change days included (D98.10); the observation pairing
(`ReportSet(live=True)`, F152.7); the page (no accuracy figure,
D103.2); the workflow template against D105.9 and D117.5 (the skip
rule, the push check, the pinned commit). **v17:** walk through exactly
what the tool does on the first v17 cycle, today, with no code change:
does the guard stop it, is the stop final, do later cycles keep
stopping, would anything be logged under a wrong label?

**Step 4. The MOSMIX saver template** (`deploy/mlwx-mosmix/`). The file
check (D122.4), write-once, the manifest and asset order, a partial
failure mid-run (uploaded tars with no manifest row: what does the next
run do?), the first-run edge when `manifest/` does not yet exist, the
freshness rule's blind spot (F171.9(2)), and the Release asset limits
(assets per Release, size) over a month.

**Step 5. Stage B's path.** `session86_forward_build.py --build` (the
mode stage B uses), the wrapper, `session87_forward_score.py` and
`session87_forward_competitors.py`, against D73, D77.6 and D79. Check:
the date windows and the v16/v17 split (D73.3); the guards that stop
any 2026-27 value being read early; persistence and the day sets
(D73.5); ties (D79.2); margins (D79.1); how period B's inputs would be
built after v17 (D73.4, D79.6); what the scripts need that may no
longer exist (paths, files, the drive, the network sources and their
formats, NAM MOS ended, NBM versions); and the hold rule (D73.8). Run
the three `--guard-check` modes again and say what they do and do not
cover.

**Step 6. The live test's scoring script** (`session129_live_score.py`),
against D105.5 (a) to (l), D123 and F172.3's readings. Fresh eyes on:
the period and group windows; the common sets; persistence (the cycle as
reference); the daily maximum's cycle (D98.10(b)); the write-once check;
the refusals of `--score`; the snapshot comparison; output paths and
write-once; anything that would make `--score` stop at the look for a
reason that can be foreseen now (for example, a log file form that the
inventory accepts today but the 2027 look would reject). Run
`--inventory` on a fresh clone of MLwx-live and compare with F172.5.

**Step 7. Tests.** For each area above, list what the tests cover and
the gaps that matter (a rule with no test that would catch its
breaking). A gap is a finding (usually minor).

**Step 8. The outside scheduler (D124.3).** From MLwx-live's public
history and its Actions run list (read-only): every cycle's issue lag
since the 2026-10-27 redeploy (D118.2), the distribution (median, 90th
percentile, maximum, and the count above 6, 9 and 12 h), and when the
late ones happened (hour of day, day of week); the scheduled runs that
GitHub did not start. Then set out the options with their costs, risks
and what each needs from the owner: (a) keep as is; (b) more schedule
slots in the workflow; (c) an outside trigger calling
`workflow_dispatch` (for example a free cron service, with a
fine-grained token limited to MLwx-live's Actions); (d) any other
option you find. No recommendation is binding; the owner decides in
session 131's entry.

**Step 8b. Efficiency (a light pass).** Time, without changing any
code: the test suite; one live runner cycle re-issued from a fresh
MLwx-live clone into a `mktemp -d` folder with `--now` set to a past
cycle's issue time (as F154.4's dry run did; IEM may be called only for
observations valid before 2026-10-12, so pick a cycle whose tracker
lookups are all before that date, or skip this run and profile by
reading the code); and any check mode that takes more than a few
minutes. Name the slow parts (fetch, decode, feature build, model load,
prediction, write, page) and, for each, a possible speed-up. Each is a
finding with severity **efficiency**, id prefix EF, and says whether the
speed-up would change any output (a logged value, a score, a file's
bytes). Only speed-ups that leave every output byte-identical are
proposed for session 131; frozen scripts are not proposed for any.

**Step 9. The register.** `notes/session-130-register.csv`, with the
columns of `notes/session-121-register.csv`, plus `line`, `confirmed_by`
(read, test or run) and `fix_before` (the look or event the fix must
precede, or "none"). One row per check made, including the checks that
passed (result OK, severity blank), so the register shows what was
looked at. Ids by area: LT (live tool), WF (workflow), MS (MOSMIX), SB
(stage B), LS (live scoring), TE (tests), SC (scheduler), EF (efficiency). Then, in the
output file, a proposed grouping of the findings into fix work for
session 131, ordered by severity, each group saying which files it
would touch and whether it engages D105.5(k) (a change that alters a
logged value).

**Step 10. Final checks.** No file outside the scope list changed (`git
status --porcelain`). Tests: 333 OK (1 skipped), unchanged. No `obs/`
file opened; no observation valid on or after 2026-10-12 read: say so,
with the count of `obs/` files opened (0).

## End of session (CLAUDE.md)

1. **F173**, at most about 40 lines: counts of checks and findings by
   area and severity; every critical and major finding in one line each,
   with its id; the scheduler numbers and options in brief; the
   proposed grouping for session 131 in brief; readings for the owner;
   what was not done; pointers to the register and the output file.
2. **Overwrite STATUS.md** as a current snapshot: the review is done;
   its findings wait for session 131; the scheduler is reopened (D124.3);
   the MOSMIX saver is live (D124.2); the order of D122.2. End with:
   `**Next planning session:** Review session 130 and commit; the
   planning chat syncs Project knowledge (D118.8); the owner rules on
   the scheduler; then session 131, the fixes (D122.2).`
3. **Archive step:** make D124.5's index changes, add F173, then
   `python3 scripts/archive_decisions.py --apply --session 130`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a summary of at most 30 lines; report the
   same summary in chat. Then stop and wait for review. Do not commit.
