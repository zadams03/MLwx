# Session 40 — GRIB build, step 4b: the sealed test (one look, stands as reported)

## What this session is

The **verdict**. The recipe is frozen (D48, session 39) and the test script is frozen. This
session opens the sealed year for the 5-feature method, runs the frozen script **once**, and
reports the result. This is the single look — **whatever it says, it stands: no re-run, no
re-tuning, no adjustment after seeing the numbers**, exactly as Reno's failure stood (F82,
D44.10/11). A pre-registered expectation (D48.12) that turns out wrong is a finding to report
plainly, not a thing to fix.

The integrity of the whole build rests on this session changing nothing about the method now
that the answer is in view. Execute D48 exactly; report; stop.

## Standing rules that bind this session (SPEC §2)

- **One look, and it stands.** After the numbers are seen: no re-run, no re-tune, no feature/
  window/constant change, no "try again." Report the result as-is, per airport.
- **The recipe and the script are frozen.** Do not modify `scripts/session39_sealed_test.py`
  or the D48 recipe. This session produces the sealed feature file the frozen script expects,
  then runs it unchanged.
- **Guards stop, they don't get worked around.** If a D48 self-guard trips (training row-count
  mismatch, sealed scored-days exceeding the D48.8 ceiling, out-of-window date, missing file),
  **stop and report** — do not edit around it.
- **Sealed pull uses the identical frozen pipeline** — same GRIB source, F89 lead convention,
  bilinear interpolation, and the five frozen elevation constants (D48.3). No new choices.
- **Raw is gitignored (D47).** The sealed GRIB raw goes under the gitignored raw path; commit
  only the processed sealed feature file, the results, and provenance.
- **No SPEC/RESULTS change this session.** Folding the (proven or not) method into SPEC and
  writing up RESULTS is a *separate* consolidation session — same discipline as session 30. This
  session pulls, tests, and records the finding only.
- **You never commit.** Prepare changes and a suggested message.

---

## Task 1 — pull the sealed-year features (frozen pipeline)

Pull temperature, `cloud_cover`, and `wind_speed_10m` from GRIB over **2025-08-01 → 2026-07-31**
for all five airports, at each airport's target hour and the `previous_day1` lead — using the
**identical** pipeline from step 2 / D48: `gfs_global` 0.25° from AWS, F89 lead convention,
bilinear grid→point, and the five frozen elevation constants (D48.3) applied to temperature.
- Byte-range fetch; save raw under the gitignored raw path with `.meta.txt` provenance.
- Drop-count-report any missing/null hours.
- Produce the processed sealed feature file at exactly the path the frozen script expects
  (`SEALED_GRIB_PATH`).
- **Respect the D48.8 scored-day ceiling:** the sealed pull may score fewer days than the
  existing-recipe history (363/363/365/347/365), never more. If it would score more, stop and
  report — that signals a pairing inconsistency.

## Task 2 — ensure sealed-year observations are available

The truth is the same IEM METARs the existing sealed tests used (D3/D14, ±15 min pairing).
Reuse the existing sealed-year observations if present; if not, pull them from IEM under the
unchanged rules. Do not alter the pairing rule.

## Task 3 — run the frozen script, once, unchanged

Run `scripts/session39_sealed_test.py` as-is against the sealed feature file. It trains
3-feature and 5-feature on the full training window and evaluates raw GFS, persistence,
3-feature, and 5-feature on the sealed year, applying the D48.11 bar per airport.
- If it completes: capture its full output verbatim.
- If a **self-guard** trips: report which guard and the values — that is the guard doing its job;
  stop, do not work around it.
- If it fails on an **unforeseen bug** (not a guard): stop and report the error for the owner to
  decide — do **not** silently patch frozen code after sealed data is in view, as that would
  compromise the one-shot.

## Task 4 — report the verdict (straight, whatever it is)

Report, per airport: raw GFS, persistence, 3-feature, and 5-feature MAE on the sealed year;
skill vs raw GFS; the **5-feature verdict against the bar** (beats both raw GFS and persistence
→ PASS, else FAIL); and the **5-vs-3-feature** comparison on the true held-out year.

Then compare against the **pre-registered D48.12 expectations** (pass at all five, including LFPG
recovered and Reno rescued): state where reality matched the prediction and where it diverged.
A correctly pre-registered result is strong evidence; a divergence is an honest finding — report
either plainly, with no adjustment to the method.

---

## What NOT to do

- **Do not re-run, re-tune, or adjust anything after seeing the results.** One look, it stands.
- **Do not modify the frozen script or the D48 recipe** — not the features, model, window,
  elevation constants, or bar.
- **Do not work around a tripped self-guard** — stop and report.
- **Do not pull or touch any date outside the sealed window** (2025-08-01 → 2026-07-31) for the
  test data.
- **Do not commit the raw GRIB** (gitignore per D47) — processed + provenance + results only.
- **Do not modify `SPEC.md` or `RESULTS.md`** — consolidation is a separate session.
- **Do not commit.**
- **Do not exceed scope** — this session pulls the sealed features, runs the frozen test, and
  reports. Nothing else.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Task 4 in full: the per-airport table, each airport's PASS/FAIL, the 5-vs-3
   comparison, and the match/divergence against D48.12's pre-registration.
2. **Append one DECISIONS finding** (append-only; next sequential — check the tail of live
   DECISIONS.md, likely **F92**): the sealed-test results, the per-airport verdicts, the
   5-vs-3 comparison, and how they compared to the pre-registered expectations. State plainly
   that this was the single locked look and the result stands. If any airport failed or diverged
   from D48.12, record it straight — no softening, no re-run.
3. **Refresh STATUS.md** to record session 40 and the sealed-test outcome; note that the
   SPEC/RESULTS consolidation is the next (documentation-only) session.
4. **Save** the sealed feature file, results tables, and `.meta.txt` provenance under
   `data/processed/`; raw under the gitignored raw path.
5. **Archive step (routine):** move any entry that became settled this session to
   `DECISIONS-archive.md` per the criterion — but F89/F90/F91 are likely still live until the
   consolidation session folds them into RESULTS/SPEC, so probably nothing moves yet. Check and
   state.
6. **Consistency check:** new DECISIONS number next-sequential and unique; the frozen script was
   run unchanged (confirm no diff to `session39_sealed_test.py`); the sealed pull stayed within
   2025-08-01 → 2026-07-31 and respected the D48.8 ceiling; the training window was unchanged;
   `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only the expected files (no raw GRIB
   staged).
7. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the
   body, `--` not em-dashes, short body (detail in F92) — then **stop and wait for the owner's
   review.**
