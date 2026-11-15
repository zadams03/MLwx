# Session 132: Gates C and D on the 12 record airports, AIFS and the NBM grid at the airport's own position, and whether the correction predicts GFS's next revision

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
Three small items from D125.9, each with its rules fixed in D127 before
any value is computed. All three are descriptive or gates: no verdict,
model, setting, rule, bar, product or live file changes. Recommended
model: Opus.

## Read first

- STATUS.md in full; SPEC section 2 and 3.4; the live DECISIONS.md in
  full.
- Archived, by line range: D107.2, D107.3, D108.3, D108.4, D115.6,
  D116.10, F152.6, F152.7, F154.6, F154.9, F155 (its opening and F155.7
  only), F156.2, F157 (its opening only).
- `scripts/session109_gates.py`: the docstring and lines from
  `# ---... Gate C` to the end.
- `scripts/session114_comparisons.py`: the docstring, the module
  constants (to about line 180), `Comp`, `Ours`, `run_hourly`,
  `run_dailymax` and `main`.
- `scripts/session119_ifs_check.py`: the docstring and how it builds
  IFS at the `iem` set (a model for Step 4, not imported).
- `../MLwx-stagec/analysis112/meta.txt` in full.

## Rules for this session

- **Writes:** only the scope list below, and temporary folders under
  `$TMPDIR` (kept, paths printed). Nothing is written under
  `data/processed/session114_comparisons/`, `src/`, `deploy/`,
  `figures/` or `../MLwx-stagec/`.
- **Network:** Step 3 only: the AWS GFS archive (Gate C) and IEM (Gate
  D). Steps 4 and 5 are offline. Before running a mode, read the code
  path it runs (including what it imports from sessions 112 and 113)
  and confirm it makes no network call and writes only where it should;
  note this in the checkpoint.
- **Imported scripts are never edited.** `session109_gates.py`,
  `session112_analysis.py`, `session113_comparison_pull.py` and
  `session114_comparisons.py` are imported read-only, each after its
  SHA-256 is checked equal to HEAD's blob (D116.10). A wrapper may set
  a module constant at run time; it never changes a function.
- **Spent data only.** Nothing valid after 2026-07-31T23:00 UTC is read
  or used; no 2026-27 value; nothing from MLwx-live's log, `obs/` or
  page; nothing from the 37 airports of F153.6 beyond Gate C/D's
  configuration count.
- **Stop rules.** Any failed check or gate stops the session at that
  step; report and wait. Do not work around it.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md, ANALYSIS.md (append only:
no existing line changes), scripts/session132_gates_cd.py,
scripts/session132_iem_rows.py, scripts/session132_revision.py,
scripts/README.md, tests/test_session132.py, tests/README.md,
data/processed/session132_iem/ (new folder),
data/processed/session132_revision/ (new folder),
notes/session-132-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `fe53604` (title starts "Session
131b:"); the tree is clean apart from this prompt. Tests: `.venv/bin/python -m unittest discover -s tests`, all
OK (STATUS says 400, 1 skipped; report the count). SHA-256 at HEAD:
`session109_gates.py` `8ac5a567fb4356db61136db4db7783eae381500a2f0314ad9d5a08cee726f59b`,
`session112_analysis.py` `bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab`,
`session114_comparisons.py` `5ff60d328b2a0489de4173c989a5a9a8472b6bdb5ce6cc4c70d7bd543b2ddc52`.
The 12 prediction files equal `meta.txt`'s SHA-256. Stop if any check
fails.

**Step 2. Record D127.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-15: Session 132 decision: F175 accepted, the redeploy and the models' move recorded, and the rules for Gates C and D, the iem-position rows and D115.6's question (owner, planning chat)

**D127. Owner decisions, planning chat (after session 131b's commit and the owner's steps): F175 accepted; the redeploy, the models' move to the private repository and the MOSMIX update recorded; the rules of session 132's three items, fixed before any value is computed; and Live index changes.** Written at the start of session 132, before any other edit. No 2026-27 value has been read or scored.

- **D127.1 F175 accepted,** with its readings. Reading (3) no longer applies: the token has no expiry (D127.2(c)).
- **D127.2 The redeploy and the models' move (owner, by hand, 2026-11-15; covers D125.8, D126.3 and D126.4).** (a) MLwx-live commit `b836748`, pushed at about 16:00Z: the template of session 131b's commit, `MLWX_COMMIT` `dad68db3ccbdfa930b7af6220d6df585a3cea2bd` (session 131), `MODELS_TAG` `gfs-models-49`; the template's `.gitignore` and README copied. Manual run 43733122333, 16:01:36Z to 16:05:04Z: green; every step succeeded, including the empty-token check and the download from the private repository; it issued a cycle and published the page. From this redeploy `code_commit` changes; D125.8 says how the live test treats the rows after it. (b) The private repository `zadams03/MLwx-models` holds Release `gfs-models-49`, whose `gfs-models.tar` has D105.2's SHA-256 (`e30f8fb99e275fd410bcc37a41686deb26bf61ccb658cb0acbb419da9769f284`), checked before upload and again on a fresh download. F175.4's step 1 ("no README") was wrong: a Release cannot be made in an empty repository (HTTP 422, "Repository is empty"), so one README commit was made first. (c) The token: fine-grained, named "MLwx-live models read", Contents read-only on `zadams03/MLwx-models` only, no expiry (owner's choice), stored as MLwx-live's secret `MODELS_TOKEN`. (d) MLwx-live's fork pull request workflows need approval for all outside contributors. (e) Removed after the green run: MLwx-live's Releases `gfs-models-49` and `gfs-models-12` and their tags (the API lists no releases and no tags; the old download URL returns 404), and the cache `gfs-models-gfs-models-49`; the cache `gfs-models-private-gfs-models-49` remains. (f) Public signals on 2026-11-14 as D126.2.
- **D127.3 MLwx-mosmix updated (owner, 2026-11-15).** Session 131's `saver.py`, `save.yml` and `README.md` copied (MLwx-mosmix commit `09418d0`, 16:23:59Z); one manual run, green.
- **D127.4 Gates C and D on the 12 record airports (F154.9(4)).** `session109_gates.py`'s Gates C and D loop over every configured airport (49), but the record's pull extracts and the gates' design cover the 12 airports of D103.4. A new script, `scripts/session132_gates_cd.py`, imports `session109_gates.py` read-only (SHA-256 `8ac5a567fb4356db61136db4db7783eae381500a2f0314ad9d5a08cee726f59b`), sets its module's `AIRPORTS` to its own `RECORD_AIRPORTS` (the 12) at run time, and runs `run_gate_c` and `run_gate_d` unchanged (D116.10). Gate C passes as F152.6: the guard's offline demonstration behaves, and at each of the three cycles every value equals the pull's extract, with no empty pull cell and no status difference. Gate D passes as F152.7 (owner's rulings 1 and 2 at session 109's stop): no pairing difference for any reason other than a repeated timestamp with different values. They test today's `src/mlwx/` (after session 131's changes) against the record. A failure is reported, not fixed; the owner rules. Network: the AWS GFS archive and IEM only.
- **D127.5 AIFS and the NBM grid at the airport's own position (descriptive, D107.2; D121.2(3)).** (a) Everything as D108.3, D108.4 and session 114's code, except one thing: at the six development airports the competitor is read at the `iem` position set (the airport's own position) in place of the `gfs` set. AIFS's elevation treatment uses its terrain at the `iem` points (`aifs_terrain.csv`'s `iem` rows) and the same station elevation; the NBM grid has no treatment, as before. The curve and raw GFS are unchanged: they stay at GFS's own position (SPEC 3.4). (b) Sources: AIFS (six development airports) and the NBM grid (KDSM, KRNO, KSFO); hourly and daily maximum (D98.10's days primary, every cycle descriptive), as session 114's `--hourly` and `--dailymax`. (c) Method: a new script, `scripts/session132_iem_rows.py`, imports `session114_comparisons.py` read-only (SHA-256 `5ff60d328b2a0489de4173c989a5a9a8472b6bdb5ce6cc4c70d7bd543b2ddc52`), sets its `OUT_DIR` and, for the six development airports, its `SET` to `iem` at run time, and runs its `run_hourly` and `run_dailymax` for `aifs` and `nbm` unchanged, seed 114, into `data/processed/session132_iem/`. (d) Gate first: the same four runs with `SET` unchanged, into a temporary folder: every table equals session 114's committed file of the same name byte for byte (18 files). Then, after the `iem` runs: every row for a claim airport equals session 114's committed row, except the Benjamini-Hochberg columns of the `_dm.csv` files, which depend on the whole family. Either check failing stops the session. (e) Summary (`summary.csv`): per development airport, source and output, the competitor's n, MAE and mean error at the `gfs` set (session 114's tables) and at the `iem` set (this session's), the curve's MAE on each set's paired rows, the pooled skill, and the formal test's direction and Benjamini-Hochberg result in each family. (f) Reading, fixed now: the position matters at an airport when the competitor's pooled MAE changes by at least 0.05 C between the sets; counted, never judged. Nothing in ANALYSIS.md's Part 1 or Part 2, or in RESULTS.md, changes in this session; the owner decides later whether their captions change.
- **D127.6 D115.6's question: does the curve's correction predict GFS's next revision? (descriptive, D107.2).** (a) Rows: every row of session 112's regenerated predictions (`../MLwx-stagec/analysis112/pred_<ICAO>.csv.gz`, each equal to `meta.txt`'s SHA-256) at the 12 airports whose `status` is `scored` or `extra` (the curve has a value), valid at or before 2026-07-31T23:00 UTC. No observation is used. (b) Pairing: a row (airport, cycle c, lead L, valid time v) pairs with the row of the same airport at cycle c + 6 h, lead L - 6, the same v, when that row is also in (a) and has the same `period`. So L runs from 9 to 48. Rows that do not pair are counted by reason (no next cycle in the file; next row not in (a); a different period). (c) Quantities: the correction k = curve - raw_gfs at c; the revision r = raw_gfs(c + 6 h, v) - raw_gfs(c, v) (the elevation constant cancels); also k_base = baseline - raw_gfs and b = curve - baseline at c, so k = k_base + b. (d) Statistics per airport, pooled over its periods and per period: n; Pearson's and Spearman's correlation of k and r; the ordinary least squares slope and intercept of r on k; the sign agreement share over pairs with k and r both non-zero (the zero counts reported); mean |r| (raw GFS at c as a forecast of the next raw GFS) against mean |r - k| (the curve at c as that forecast), and their ratio; Spearman's correlation of r with k_base and with b. (e) Intervals: 95 % percentile intervals by a block bootstrap over cycle UTC dates (every pair whose c falls on one UTC date together), 2,000 resamples, one generator `numpy.random.default_rng(132)`, airports in session 112's order (`AIRPORTS`), statistics in (d)'s order. (f) Breakdowns, point values only: the lead at c (9 to 24, 25 to 48); the cycle hour; the tercile of |k|, edges from that airport's own |k| values. (g) Reading, fixed now: at an airport the correction points the way GFS next revises when the interval of Spearman's correlation of k and r lies wholly above 0. Counted of 12; "most airports" is at least 7 of 12. Sizes are described, not judged. Nothing changes because of it; any use (for example as an input in stage E or H) needs its own entry.
- **D127.7 Where results go.** Tables in `data/processed/session132_iem/` and `data/processed/session132_revision/`, each with a meta file (script SHA-256, versions, run time). ANALYSIS.md gains one section appended at its end, "Part 4. Additions after session 114", with D127.5's summary and D127.6's headline table, each labelled descriptive; no existing line of ANALYSIS.md changes.
- **D127.8 Plan.** Session 132: this entry; Gates C and D; the `iem` rows; D115.6's question; tests for the three scripts; ANALYSIS.md's Part 4; F176. Then session 133: stage H's design and build choices (D125.9). A GFS v17 Service Change Notice goes ahead of either.
- **D127.9 Live index.** Removed (archived): D126 and F175, which are settled (the move and redeploy are recorded here and carried in STATUS). Added: D127 and F176 (F176 when it is written). After session 132: D93, D103, D105, D118, D127, F176.
```

**Step 3. Gates C and D (D127.4).** Write `scripts/session132_gates_cd.py`
with modes `--count` (offline: prints how many airports
`session109_gates.AIRPORTS` holds and that `RECORD_AIRPORTS` is the 12
of D103.4, by ICAO), `--gate-c` and `--gate-d`. Run `--count`, then
`--gate-c`, then `--gate-d`. Report each gate's summary lines (values
compared, not equal, empty pull cells, status differences; pairing
equal, by design, other) and PASS or FAIL. If a gate fails, stop.

**Step 4. The `iem` rows (D127.5).** Write `scripts/session132_iem_rows.py`
with modes `--gate` (D127.5(d)'s first check, into a temporary folder),
`--run` (the four `iem` runs, then the claim-airport check) and
`--summary` (`summary.csv` and the counts of D127.5(f)). Run them in that
order. Report per development airport and source, hourly and daily
maximum: the competitor's MAE at each set, the curve's, and the formal
test's direction in each family; and how many airports pass D127.5(f)'s
0.05 C mark.

**Step 5. D115.6's question (D127.6).** Write `scripts/session132_revision.py`
with modes `--check` (synthetic data only: the pairing across cycles,
across a period boundary and with a missing next row; the sign share
with zeros; the bootstrap's blocks), `--pairs` (counts only, by reason,
no statistic) and `--stats`. Run them in that order; tables per
D127.6(d) to (f) in `data/processed/session132_revision/`. Report the
per-airport headline (n, Spearman's correlation with its interval, the
slope, the sign share, the mean |r| against mean |r - k|) and D127.6(g)'s
count.

**Step 6. Tests and documents.** `tests/test_session132.py`: the
wrapper's airport list is the 12 record airports; the three imported
scripts' SHA-256 equal D127's values; the revision script's pairing and
sign share on made-up rows. `tests/README.md` and `scripts/README.md`'s
per-session map gain one line each (plain words, D121.4). ANALYSIS.md:
append Part 4 (D127.7), labelled descriptive, plain; check by `diff`
against HEAD that only lines after the old last line were added.

**Step 7. Final checks.** All tests OK (report the count); scope list
against `git status --porcelain`; nothing under the folders the rules
name changed; 0 em-dashes in added lines; nothing read valid after
2026-07-31T23:00 UTC.

## End of session (CLAUDE.md)

1. **F176**, at most about 40 lines (D93.10): the three items' numbers
   a decision needs, every gate and check with PASS or FAIL, readings
   for the owner (anything the rules left open and how it was read),
   what was not done, and the pointer to the output file.
2. **Overwrite STATUS.md** (current only, pruned): record the redeploy
   and the models' move as done (D127.2), the MOSMIX update as done
   (D127.3); the three items' outcome in a few lines; drop the open
   question on F175.6. End with: `**Next planning session:** Review
   session 132 and commit; then plan session 133, stage H's design and
   build choices (D125.9), including whether to pre-register a range test
   on 2026-27 while no 2026-27 value has been scored (D121.2(4)).`
3. **Archive step:** make D127.9's index changes, add F176, then
   `python3 scripts/archive_decisions.py --apply --session 132`.
4. **Checks:** `--citations`; byte size of DECISIONS.md (under 80,000);
   scope list against `git status --porcelain`.
5. **Output file** `notes/session-132-output.txt` starts with a summary
   of at most 30 lines and a checkpoint line per step; report it in
   chat. Then stop and wait for review. Do not commit.
