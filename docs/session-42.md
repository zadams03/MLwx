# Session 42 — the sealed test, clean run (one look, stands as reported)

## What this session is

The **verdict**, for real this time. Session 40 pulled and decoded the sealed-year GRIB features
cleanly; session 41 verified the extra days were benign and corrected the mis-specified D48.8
guard (F93). Nothing else about the recipe changed. This session runs the frozen sealed-test
script **once** against the already-pulled sealed features and reports the result.

This is the single authorised look (D48.13). **Whatever it says, it stands: no re-run, no
re-tune, no adjustment after seeing the numbers.** A pre-registered expectation (D48.12) that
turns out wrong is a finding to report plainly. The integrity of the whole build rests on this
session changing nothing now that the answer is in view — it executes, reports, and stops.

## Standing rules that bind this session (SPEC §2)

- **One look, and it stands.** After the numbers are seen: no re-run, no re-tune, no change to
  features/model/window/constants/bar, no "try again." Report as-is, per airport.
- **The recipe and script are frozen.** Do not modify `scripts/session39_sealed_test.py` (beyond
  the F93 guard correction already committed) or the D48 recipe. Confirm the script is unchanged
  since the F93 commit (`git diff` empty against it) before running.
- **Reuse session 40's sealed feature file** (`data/processed/grib_features_sealed_window.csv`)
  and the existing sealed-year observations — **pull nothing new**. The pull was already clean;
  re-pulling is out of scope.
- **Guards stop, they don't get worked around.** The corrected ceiling should now pass. If any
  *other* self-guard trips (out-of-window date, training row-count, missing file), stop and
  report — do not edit around it. If it fails on an unforeseen bug, stop and report for an owner
  decision; do not silently patch frozen code with sealed data in view.
- **No SPEC/RESULTS change this session.** Folding the (proven or not) method into SPEC and
  writing up RESULTS is a *separate* consolidation session. This session tests and records only.
- **Raw is gitignored (D47).** No new raw anyway. **You never commit.**

---

## Task 1 — run the frozen script, once, unchanged

Confirm `scripts/session39_sealed_test.py` is unchanged since the F93 commit, then run it as-is
against `data/processed/grib_features_sealed_window.csv`. It trains 3-feature and 5-feature on the
full training window and evaluates raw GFS, persistence, 3-feature, and 5-feature on the sealed
year, applying the D48.11 bar per airport.
- If it completes: capture its full output verbatim.
- If a self-guard trips or it errors on an unforeseen bug: stop and report — do not work around it,
  do not patch.

## Task 2 — confirm scoring consistency (the one check flagged from F93)

The extra days exist because **persistence is scoreable on fewer days than the forecast rungs**
(it needs yesterday's observation). Confirm the bar is judged on a consistent, fair day basis,
matching how the existing airports (F16/F30/F47/F64/F82) were scored:
- each pairwise comparison uses the days on which **both** members are defined — 5-feature-vs-
  persistence on the days persistence is defined; 5-feature-vs-raw-GFS on the days both are
  defined;
- report, per airport, the day count used in each comparison, so it's explicit and comparable to
  the old airports' scoring.
This should already be what the SPEC scoring logic does (the frozen script uses it unchanged) —
the task is to **confirm and report it**, not to change anything. If the script instead scores
the rungs on mismatched day sets in a way that makes the bar comparison unfair, stop and report
rather than accepting the verdict.

## Task 3 — report the verdict (straight, whatever it is)

Report, per airport: raw GFS, persistence, 3-feature, and 5-feature MAE on the sealed year; skill
vs raw GFS; the **5-feature verdict against the bar** (beats both raw GFS and persistence → PASS,
else FAIL); and the **5-vs-3-feature** comparison on the true held-out year.

Then compare against the **pre-registered D48.12 expectations** (pass at all five, including LFPG
recovered and Reno rescued): state where reality matched the prediction and where it diverged. A
correctly pre-registered result is strong evidence; a divergence is an honest finding — report
either plainly, with no adjustment to the method.

---

## What NOT to do

- **Do not re-run, re-tune, or adjust anything after seeing the results.** One look, it stands.
- **Do not modify the frozen script (beyond the committed F93 fix) or the D48 recipe.**
- **Do not re-pull the sealed features** — reuse session 40's file.
- **Do not work around a tripped guard or patch an unforeseen bug** — stop and report.
- **Do not modify `SPEC.md` or `RESULTS.md`** — consolidation is a separate session.
- **Do not commit.**
- **Do not exceed scope** — run the frozen test, confirm scoring consistency, report. Nothing else.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Task 3 in full: the per-airport table, each airport's PASS/FAIL, the 5-vs-3
   comparison, the per-comparison day counts (Task 2), and the match/divergence against D48.12.
2. **Append one DECISIONS finding** (append-only; next sequential — check the tail of live
   DECISIONS.md, likely **F94**): the sealed-test results, per-airport verdicts, the 5-vs-3
   comparison, scoring-consistency confirmation, and how they compared to the pre-registration.
   State plainly this was the single locked look and the result stands. Record any failure or
   divergence straight — no softening, no re-run.
3. **Refresh STATUS.md** to record session 42 and the sealed-test outcome; note that the
   SPEC/RESULTS consolidation is the next (documentation-only) session.
4. **Save** the results tables under `data/processed/` with provenance.
5. **Archive step (routine):** move any entry that became settled per the criterion — F89/F90/F91
   likely stay live until the consolidation session folds them into RESULTS/SPEC; check and state.
6. **Consistency check:** new DECISIONS number next-sequential and unique; the frozen script was
   run unchanged since the F93 commit (confirm via diff); the test used only the sealed-window
   file (no re-pull, nothing outside 2025-08-01 → 2026-07-31); training window unchanged; scoring
   consistent per Task 2; `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only expected
   files.
7. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the
   body, `--` not em-dashes, short body (detail in F94) — then **stop and wait for the owner's
   review.**
