# Session 64 — the single authorized confirmation look at the reserved year

## Purpose

Run the frozen confirmation of the locked final feature set (D58: B + D, L,
R, T) on the reserved year 2024-08-01..2025-07-31 (D51), **once**. This is
the one authorized look. Session 63 closed the data gap that blocked it
(D58 item 11, F107), and its join arithmetic was verified (F108).

The session has a hard gate: first re-run `preflight()` and prove it still
reproduces session 61 exactly. **Only if that passes** do you run
`--confirm`, once, unchanged.

## Hard scope guard (read before anything else)

- **Do not edit any script.** In particular, `scripts/session62_reserved_confirm.py`
  is frozen as it stands after F107's documented pre-look wiring. No edits,
  no "small fixes", no added prints. If something seems wrong, stop and report.
- **`--confirm` is run at most once, ever.** Never re-run it, for any
  reason, after it has started — not after a crash, not after a surprising
  number, not to capture output you forgot to save. The look counts as spent
  the moment the command is launched.
- **No tuning, no selection, no alternative variants** on the reserved year.
  Only what `run_confirm()` itself computes.
- **Do not touch the sealed year** (2025-08-01..2026-07-31, F94).
- Do not modify `SPEC.md` or `RESULTS.md`. Do not archive any DECISIONS
  entry. Do not commit anything.

## Step 0 — pre-look integrity checks (no model, no data read)

1. `git status --porcelain` — report it. Everything except this prompt file
   (`docs/session-64.md`) should be clean. If `scripts/` or `data/processed/`
   show uncommitted changes, **stop and report**.
2. `git diff HEAD -- scripts/session62_reserved_confirm.py` must be empty
   (the script is exactly as committed after session 63). Record
   `git log -1 --format=%H -- scripts/session62_reserved_confirm.py` and the
   file's SHA-256. Report both.
3. Confirm the four files in `RESERVED_FAMILY_FILES` exist
   (`data/processed/session63_reserved_window_with_{upper_air,moisture,pressure,radiation}.csv`),
   by path check only.

If any check fails: stop, report, do not proceed.

## Step 1 — re-run preflight() (the gate)

Run the script with no arguments, exactly as session 62 did, saving the full
real output:

```
python scripts/session62_reserved_confirm.py 2>&1 | tee notes/session-64-preflight-output.txt
```

Then, in a separate read-only step (no model fit), compare the preflight's
2023-24 dry-run figures against **both**:

- session 61's `B+LDTR` rows for fold 2023-24 in
  `data/processed/session61_combine_sweep_grid.csv`, and
- session 62's own `notes/session-62-preflight-output.txt`.

For each of the five airports (EGLC, LFPG, DSM, YSDU, RNO), print raw-GFS
MAE, persistence MAE and B+D,L,R,T MAE from each source side by side.

**Pass criterion:** every figure matches session 61 to the fourth decimal
place, at all five airports (the same standard D58 recorded for session 62).
Also report the dry-run's train/test row counts per airport and confirm no
reserved-year row entered the 2023-24 dry-run.

**If preflight raises, or any figure fails to match: STOP. Do not run
`--confirm`.** Report exactly what happened. Do not diagnose by editing the
script. The owner decides the next step.

## Step 2 — the look (only if Step 1 passed)

Run once, unchanged, saving the full real output:

```
python scripts/session62_reserved_confirm.py --confirm 2>&1 | tee notes/session-64-confirm-output.txt
```

- If `run_confirm()`'s own pre-fit guard trips (row counts, day-set
  reconciliation) **before any model is fit or any MAE is printed**: stop and
  report. Per D58 item 9 such a trip is outcome-orthogonal and fixable, but
  the fix is the owner's call — not this session's.
- If it fails **after** any reserved-year MAE was computed or printed: the
  look is spent. Do not re-run. Report everything that was produced.

## Step 3 — report the result (real numbers only)

From the saved output, report:

1. **Per-airport table** on the reserved year: raw-GFS MAE, persistence MAE,
   refit-B MAE, refit-(B+D,L,R,T) MAE, and the scored-row counts for each
   (expected 365 complete-case rows per airport; persistence on its own
   usable-previous-day subset, SPEC 2.1d). Report any day-set mismatch
   plainly (F93 pattern).
2. **The bar (D58 item 7):** does B+D,L,R,T beat **both** raw GFS **and**
   persistence at **all five** airports? State PASS or FAIL, and for each
   airport the margin against each baseline.
3. **Secondary read:** airport-averaged MAE, B+D,L,R,T vs plain B, as a %
   skill. Give per-airport B vs B+D,L,R,T too, as description only — no
   per-airport 5-beats-B claim was pre-registered (DSM variation expected).
4. Whatever the outcome, report it as is. No re-framing toward a better
   number; lead with the bar verdict.

## Step 4 — end-of-session steps (CLAUDE.md), then stop

1. **Append a new DECISIONS entry, F109** — the reserved-year confirmation
   finding. Include: Step 0 checks; the preflight re-run result against
   session 61 (and session 62); the confirmation table; the bar verdict; the
   secondary read. Required framing:
   - Describe the script as **"unchanged since the documented pre-look
     wiring (F107)"** — not "byte-identical since session 62".
   - Include D58 item 8's honesty caveat: the reserved year was seen once
     before, descriptively, for baseline B only (F96); this is the first
     look at the selected set B+D,L,R,T. Neither overclaim blindness nor
     understate that.
   - State that this was the single authorized look (D51) and will not be
     repeated.
   - If the session stopped at Step 0, 1 or 2 without a look, F109 records
     that instead, and states the look is **not** spent.
2. **Overwrite STATUS.md** as a current-only snapshot (prune, do not
   append). It must end with a **"Next planning session"** line: owner
   review of F109 and the verdict decision (and, if the look did not happen,
   what blocked it).
3. **Consistency check:** re-read CLAUDE, SPEC, STATUS, DECISIONS; report
   disagreements, duplicate headings, out-of-order entries. Report only.
4. **Archive step: archive nothing this session.** D52–D58 and F106–F108
   stay live until the owner's verdict on F109.
5. Write out a suggested commit message. **Do not commit.** Stop and wait
   for review.
