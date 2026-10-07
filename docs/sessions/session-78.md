# Session 78 — KSFO: the two pre-registered looks

Session 77 rehearsed KSFO and locked it (F118, D70). This session runs the
frozen look script **once**, unchanged, and records what it produces (F119).

It does four things, in order:
1. integrity checks (no model, no held-out value read);
2. a dry-run gate: the frozen script's `--dry-run` must still pass and its
   self-test must still reproduce the rehearsal exactly;
3. the looks: `--run-looks`, once;
4. records the result (F119), with no change to SPEC or RESULTS.

The owner's verdict, and any SPEC/RESULTS edits, come in a later session.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **Do not edit any script.** `scripts/session77_ksfo_looks.py` is frozen
  (D70.6). No edits, no "small fixes", no added prints. The same holds for
  every existing script, including `session62_reserved_confirm.py` and
  `session48_reserved_year.py`. If something seems wrong, stop and report.
- **`--run-looks` is run at most once, ever.** Never re-run it, for any
  reason, once it has started: not after a crash, not after a surprising
  number, not to capture output that was not saved. Both looks count as
  spent the moment the command is launched.
- **No tuning, no selection, no alternative variants** on either held-out
  year. Only what the frozen script itself computes. No extra models, no
  other feature sets, no re-scoring on other day sets beyond those the
  script prints, and no per-month or per-season breakdown of held-out
  errors.
- Do not touch the five earlier airports' data or verdicts. F94, F109 and
  every earlier verdict stand.
- No row dated 2026-08-01 or later is touched (none should exist).
- No network calls.
- Do not modify `SPEC.md`, `RESULTS.md`, `README.md` or `CLAUDE.md`. Do not
  write anything under `data/raw/`. The only writes under `data/processed/`
  are the two files the frozen script itself writes (D70.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks (no model, no held-out value read)

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-78.md`, since session 77 is committed. If `scripts/` or
   `data/processed/` show any change, **stop and report**.
2. `git diff HEAD -- scripts/session77_ksfo_looks.py` must be empty. Report
   `git log -1 --format=%H -- scripts/session77_ksfo_looks.py`.
3. Report the SHA-256 of each file below and compare it with the locked
   value. **Any mismatch: stop and report.**
   - `scripts/session77_ksfo_looks.py`:
     `e4ec113b0dcbc936550b382ffbcdd55d3049878c8b13d74cd83e867a6b3247c1`
     (D70.6)
   - `data/processed/session76_ksfo_features.csv`:
     `f228301edd2c155bf1062dfb57f5e83ef0ce17050151bcdcf5e9983b2bc3e5c9`
     (D70.2)
   - `data/processed/session76_ksfo_observations.csv`:
     `b987dd4fad6d1baabefd5a15e31df8260e696b4193f4296d31eebb99c027736c`
     (D70.2)
   - `scripts/session62_reserved_confirm.py`:
     `9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4`
     (D70.2)
4. Confirm, by path check only, that neither
   `data/processed/session78_ksfo_looks_grid.csv` nor
   `data/processed/session78_ksfo_looks_predictions.csv` exists. If either
   exists, **stop and report**.
5. Read D67, D69, D70 and F118 in `DECISIONS.md`.

---

## Step 1 — the dry-run gate

Run once, saving the full real output:

```
python scripts/session77_ksfo_looks.py --dry-run 2>&1 | tee notes/session-78-dryrun-output.txt
```

**Pass criterion.** The script's own checks pass (hashes, station, G15
columns, the KSFO held-out guard, counts as D70.3), and the self-test on the
`2023-24` fold reproduces F118.5's five MAEs exactly:
- raw 1.3061369863013699
- persistence 1.715659340659341
- mean-bias 1.250037292844142
- B 1.2922832710768244
- B+D,L,R,T 1.174587228071113

Print these side by side with the dry-run's values.

**If the dry-run raises, or any value differs: STOP. Do not run
`--run-looks`.** Report exactly what happened. Do not diagnose by editing
anything. The looks are **not** spent. The owner decides the next step.

---

## Step 2 — the looks (only if Step 1 passed)

Run once, unchanged, saving the full real output:

```
python scripts/session77_ksfo_looks.py --run-looks 2>&1 | tee notes/session-78-looks-output.txt
```

- If the script's own guard stops it **before any model is fit or any
  held-out MAE is printed**: stop and report. Such a trip is about dates and
  counts only, so the looks are **not** spent. Any fix is the owner's call.
- If it fails **after** any held-out MAE was computed or printed: the looks
  are spent. Do not re-run. Report everything that was produced.

---

## Step 3 — read-only checks on what was written

No model is fit in this step.

1. Report the SHA-256 and row count of each output file. Expected
   prediction rows: 364 (look A) + 365 (look B) = 729, unless the script's
   documented layout says otherwise (then report its layout).
2. **Independent re-score.** In a separate process, recompute each look's
   rung MAEs from `session78_ksfo_looks_predictions.csv` (G24, the same day
   bases as D70.4). They must equal the printed values to full precision.
   A mismatch is reported, not fixed. This is a check of arithmetic only:
   nothing is selected, and no new day set or breakdown is scored.

---

## Step 4 — report the result (real numbers only)

From the saved output, report:

1. **Per-look table:** n test, persistence days, and MAE for raw GFS (GRIB),
   persistence, mean-bias reference, `B` (canonical) and `B+D,L,R,T`
   (record order). Full precision and 4 dp.
2. **The bar (D70.4), per look:** does `B+D,L,R,T` beat raw GFS (GRIB)
   **and** persistence on MAE? PASS or FAIL, with the margin (°C and %)
   against each.
3. **The overall reading (D67.3, D70.4):** pass (both looks pass), split
   (one passes, one fails) or fail (neither). Set it beside the
   pre-registered expectation, "pass in both years" (D70.8), and say plainly
   whether it matched.
4. **Secondary read (D70.5), per look:** margin = canonical `B` MAE minus
   record-order `B+D,L,R,T` MAE, read against the band
   0.037704595173481126 °C. Use D67.5's three wordings exactly.
5. **Descriptive only:** the common-day re-score, as the script prints it.
6. Whatever the outcome, report it as is. Lead with the bar verdict. Do not
   re-frame toward a better number.

---

## End-of-session steps (CLAUDE.md), then stop

1. Write the **real output** of every step to `notes/session-78-output.txt`
   (the dry-run and looks outputs are also kept in their own files).
2. **Append F119** to `DECISIONS.md`, dated 2026-09-26 (or the real date):
   the KSFO looks finding. It records:
   - Step 0 (hashes, git state, output files absent beforehand);
   - the dry-run gate and self-test comparison;
   - the per-look table, the bar verdict per look, the overall reading, and
     whether it matched the expectation;
   - the band read per look and the common-day re-score (descriptive);
   - Step 3's checks and the output files' SHA-256 values;
   - **required framing:**
     - these were the two pre-registered looks (D67.3, D70), run once, and
       will not be repeated;
     - the result is for the recipe at a sea-mixed grid point (37.5% sea
       weight, F117.3) and **is not directly comparable with the five
       earlier airports**, whose reproduction gates passed; the gate is
       recorded as failed, explained by a difference between the sources
       (D69, D70.9);
     - look B's training includes 2024-25, by design (D70.3);
   - a "What this did not do" list (no script edited, no re-run, nothing
     tuned or selected, no SPEC/RESULTS edit, no network, nothing
     committed; F109, F94 and every earlier verdict stand).

   If the session stopped at Step 0, 1 or 2 without a look, F119 records
   that instead and states that the looks are **not** spent.
3. **Archive: archive nothing this session.** D67, D69, D70 and F115–F118
   stay live until the owner's verdict on F119.
4. **Overwrite STATUS.md** as a current-only snapshot (prune, do not
   append):
   - KSFO's looks are run (or, if not, what blocked them), with the overall
     reading and the D70.9 framing. Delete the "`--run-looks` has not been
     run" wording.
   - Q30 and Q32 stay open, unchanged. Carried items stay as they are
     (GFS v17 unchanged; SPEC wording B1–B5, C1–C3 and CLAUDE.md E1 still
     waiting for a session that edits SPEC or CLAUDE.md).
   - End with a **"Next planning session"** line: "Review session 78 and
     decide the owner's verdict on F119. Then plan session 79: record the
     verdict and fold KSFO into SPEC and RESULTS (with the carried SPEC
     wording items B1–B5, C1–C3 and CLAUDE.md E1). After that, hold the
     roadmap planning session (D66.1)."
5. **Consistency check:** re-read CLAUDE, SPEC, STATUS and DECISIONS. Report
   disagreements, duplicated headings, out-of-order entries and unresolved
   citations. Note that SPEC still describes KSFO as "locked, not yet
   tested"; that is expected until session 79, so list it but do not fix it.
   Report only.
6. **Do not write a commit message file, and do not commit.** The planning
   chat writes `docs/commit-78.txt` after review. Stop and wait for the
   owner's review.
