# Session 129: the live test's scoring script, and stage B's gate wrapper

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
This session writes the script that will one day judge the live test
(D105.5), gates it on spent data and synthetic logs, and commits it
before any observation valid on or after 2026-10-12 is read (D105.5(l)).
It also builds the deferred wrapper for session 86's gate (D118.10). It
scores nothing live: no observation valid on or after 2026-10-12 is read,
fetched or opened, and no error is computed from MLwx-live's log, its
`obs/` snapshots or its page (D105.6). Recommended model: the strongest
available.

## Read first

- STATUS.md in full; SPEC section 2; SPEC section 9; the live
  DECISIONS.md in full (D105.5 to D105.7 above all).
- Archived, one entry at a time by line range: D79.1, D79.2, D96.3,
  D97.4 to D97.7, D98.10, D100 (all), F150, F152.7, F152.8, D103.8,
  D116.3, D116.10, F122.3, F122.5, F128.
- `scripts/session106_claim_look.py` in full (the look's scoring rules:
  `persistence_k`, `hourly_persistence`, `observed_max`,
  `persistence_day`, `daily_persistence`, `margin`, `half_pass`,
  `look_pass`, and how the daily maximum is read off the curve).
- `src/mlwx/observations.py`, `src/mlwx/dailymax.py`,
  `src/mlwx/prediction_log.py`, `src/mlwx/config.py` in full.
- `scripts/session86_forward_build.py`: its module docstring, `run_gate`,
  `plumbing` and every DECISIONS lookup (around line 860), by line range.
- `scripts/session122_gates.py` (how D116.3's wrapper swapped a lookup).
- `../MLwx-stagec/analysis112/meta.txt` in full.

## Rules for this session

- **No live observation (D105.5(l), D105.6).** Nothing valid on or after
  2026-10-12T00:00 UTC is fetched from IEM or opened from MLwx-live's
  `obs/`. The `--inventory` mode (Step 5) reads MLwx-live's `log/`,
  `state/` and git history only; it lists `obs/` file names and never
  opens one. No error, MAE or difference involving a live forecast is
  computed or printed.
- **Reuse, not re-implement, where the rule is already code.** Import
  session 106's scoring functions and `mlwx`'s pairing and daily-maximum
  code. Where a rule must be new code, say so in the checkpoint and test
  it. No existing script, test, data file, model, `src/` or `deploy/`
  file is edited; session 86 and session 106 are not edited (D62.3(a),
  D116.10).
- Network: GitHub only, for a fresh clone of the public
  `zadams03/MLwx-live` (Step 5). Nothing else.
- Synthetic logs and other large intermediates go into `mktemp -d`
  folders outside the repo and are deleted at the end (keep their
  SHA-256 in the output file).

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md,
scripts/session129_live_score.py (new),
scripts/session129_stageb_gate.py (new),
tests/test_session129_live_score.py (new),
tests/test_session129_stageb_gate.py (new), tests/README.md (two lines:
the new test files, and session 127's missing one),
data/processed/session129_gate/ (new; small gate result files only),
notes/session-129-output.txt.

## Steps

**Step 1. Start checks.** HEAD is session 128's commit (read it from
`git log -1`; its title starts "Session 128"); the tree is clean apart
from this prompt. Tests: all OK (report the count). SPEC 3.4's span
SHA-256 `a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
`../MLwx-stagec/analysis112/`: each `pred_`, `obs_` and `refs_` file of
the six claim airports has the SHA-256 in `meta.txt`. Stage B's three
`--guard-check` modes pass (F167.5). Stop if any check fails.

**Step 2. Record D123.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-14: Session 129 decision: F171 accepted, the live test's scoring script and its gates, and session 86's gate wrapper (owner, planning chat)

**D123. Owner decisions, planning chat (after session 128's commit): F171 accepted; how the live test's scoring script (D105.5(l)) is built and gated before any live observation is read; and session 86's gate wrapper (D118.10).** Written at the start of session 129, before any other edit. No 2026-27 value has been read or scored, and no observation valid on or after 2026-10-12 has been read.

- **D123.1 F171 accepted,** with its readings.
- **D123.2 The script.** `scripts/session129_live_score.py` implements D105.5 exactly and adds no rule. Where D105.5 refers to an earlier rule, the script imports the code that implements it: session 106's persistence, observed-maximum, margin and pass functions (D100.5, D79.1, D79.2), and `mlwx`'s live pairing (`ReportSet(live=True)`, F152.7) and daily-maximum reading (D98.10). Persistence is the look's, with the cycle as its reference time. It is committed before it reads any observation valid on or after 2026-10-12, and from then on it is not edited (D62.3(a)); a fix goes in a new script under D116.10, recorded in DECISIONS before its look.
- **D123.3 Its modes.** `--inventory LIVE_CLONE` (D105.5(a) and (h), no observation: every log file added once and never changed or deleted in MLwx-live's history; per airport and period, cycles with and without a log file, with the state file's reasons; each cycle's issue lag; rows issued after their valid time, by lead); `--gate` (D123.4); and `--score LIVE_CLONE --period A|B --first-v17-cycle YYYYMMDDHH|none` (the look). `--score` refuses to run unless: the script file equals its committed version (`git diff --quiet`) and its SHA-256 is printed; the period's last valid hour plus 7 days is in the past (D105.5(f)); the `--first-v17-cycle` value is a cycle hour after 2026-10-12T12; and `--inventory` passes in the same run. It fetches the period's observations fresh from IEM, from early enough for every persistence value, and reports their agreement with the `obs/` snapshots only after the scores are written.
- **D123.4 The gates, fixed before the script is run on anything.** (a) Reproduction: synthetic logs in MLwx-live's format (D103.8), built from session 112's regenerated claim predictions (`../MLwx-stagec/analysis112/`, which reproduce F150 exactly, F155.7(6)), with periods set to stage C's looks and observations taken from the same folder's `obs_` files (the record's pairing, injected in place of the live fetch), must reproduce `data/processed/session107_claim_scores.csv` and `session107_claim_verdicts.csv` exactly: every n and MAE at full precision, every margin and verdict, both outputs, both halves. (b) Synthetic cases, as tests: a log file changed or deleted in history stops `--score`; a second file for one cycle is reported, never scored; the v17 boundary splits rows and local days by their cycle; nothing valid after 2027-07-31T23:00 is used; a tie fails; a day whose observed or forecast maximum is at a local-day edge is counted and scored separately under D105.5(i); a missing cycle and a late row are counted, never dropped; the 12 and the 37 are reported as separate groups. (c) The real inventory on a fresh clone of MLwx-live, no observation read.
- **D123.5 Session 86's gate (D118.10, D116.3).** `scripts/session129_stageb_gate.py` runs `session86_forward_build.py --gate` with its DECISIONS lookups replaced at run time by constants (F122.3's training-set SHA-256 as `session91_grib_pull.py`'s `TRAINING_SET_SHA256`; F122.5's values held in the wrapper), each checked by a test against both DECISIONS files. Session 86 is not edited. It is run once in this session if its inputs are present; if it needs the GRIB drive and the drive is not mounted, the wrapper and its tests are committed and the run waits for the session that prepares stage B's run.
- **D123.6 Not changed.** D105.5's rules, D73, D77.6, the live tool, its models and its log. No logged value changes, so D105.5(k) is not engaged.
- **D123.7 Live index.** Removed (archived): D122 and F171, which are settled (D122.2's order is carried in STATUS). Added: D123 and F172 (F172 when it is written). After session 129: D93, D103, D105, D118, D123, F172.
```

**Step 3. Design note (in the output file, before any code).** Write,
point by point against D105.5 (a) to (l), how the script implements each
item, naming the imported function or the new code for each. List every
place where D105.5 leaves a choice open (for example, how persistence's
days back are counted when a cycle is issued late, which cycles' rows
count toward a local day, what happens to a row whose model SHA-256 or
code commit changes mid-period). For each, write the reading taken and
why it follows from D105.5 or the rule it cites. If any reading would be
a new rule rather than a reading, **stop and report it to the owner in
chat** before writing code; the owner rules and the ruling is quoted in
F172.

**Step 4. Write the script and gate (a).** Build
`session129_live_score.py` with the three modes. Build the synthetic
logs for gate (a) in a temporary folder: one file per cycle, all six
claim airports, columns and number formats exactly as MLwx-live's log
(take one real log file's header and number format as the template, no
values). Run `--gate`: it writes, to `data/processed/session129_gate/`,
the recomputed scores and verdicts and a comparison file, and prints
PASS or FAIL. **Stop on any difference**; report it with the first ten
differing cells; do not adjust the script to force a match without
reporting why the difference arose.

**Step 5. Gate (c), the real inventory.** Clone
`https://github.com/zadams03/MLwx-live` fresh into a temporary folder and
run `--inventory` on it. Report: the clone's HEAD; log files found and
the write-once result; per group (12 and 37) the first cycle, the cycle
count with and without a log file and the reasons; the issue lag's
median, maximum and the five latest cycles' lags; rows issued after
their valid time by lead (leads 3 and 4 are expected). Confirm in the
output file that no file under `obs/` was opened (for example by
printing the count of `obs/` names listed and the count opened, which
must be 0). Delete the clone.

**Step 6. Tests.** `tests/test_session129_live_score.py`: gate (b)'s
cases on tiny synthetic logs and observations; `--score`'s refusals
(dirty file, period not ended, bad `--first-v17-cycle`, failed
inventory) without any network; the script never reads an `obs/` file in
`--inventory`. All pass.

**Step 7. Session 86's wrapper.** Build `session129_stageb_gate.py` and
`tests/test_session129_stageb_gate.py` per D123.5. Read session 86's
`run_gate` and `plumbing` to list what the gate needs (files, the drive,
network). If everything it needs is present, run the wrapper once and
compare its result with F128's, field by field. If it needs the drive
and `/Volumes/MY PASSPORT/` is not mounted, say so in chat and ask the
owner whether to plug it in; if not, record that the run waits.

**Step 8. tests/README.md.** Add one line each for the two new test
files and for `tests/test_session127_figures.py`, in plain words.

**Step 9. Final checks.** Tests: Step 1's count plus the new ones, all
OK. SPEC.md unchanged; 3.4's span hash unchanged. No file outside the
scope list changed. 0 em-dashes in added lines and new files. Record the
SHA-256 of both new scripts. Confirm again: no observation valid on or
after 2026-10-12 was read, and no `obs/` file was opened.

## End of session (CLAUDE.md)

1. **F172**, at most about 40 lines: the design note's open readings and
   any owner rulings; gate (a)'s result (counts compared, differences);
   the inventory's counts; the tests; session 86's wrapper and whether it
   ran; both scripts' SHA-256; every check with PASS or FAIL; readings
   for the owner; what was not done; pointer to
   `notes/session-129-output.txt`.
2. **Overwrite STATUS.md** as a current snapshot: the live test's
   scoring script is written, gated and (once committed) frozen;
   stage B's gate wrapper exists; the order of D122.2. End with:
   `**Next planning session:** Review session 129 and commit; the
   planning chat syncs Project knowledge (D118.8); then session 130, the
   independent code review (D122.2).`
3. **Archive step:** make D123.7's index changes, add F172, then
   `python3 scripts/archive_decisions.py --apply --session 129`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a summary of at most 30 lines; report the
   same summary in chat. Then stop and wait for review. Do not commit.
