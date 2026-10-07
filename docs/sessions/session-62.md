# Session 62 — Lock the final feature set and freeze the reserved-year confirmation (no reserved-year data read)

## What this session is

The combine-phase sweep (D57 / F106) ran, and the owner review of that grid is
complete. The single final feature set has been chosen:

> **Final set = B + D, L, R, T** — the frozen 5-feature GRIB baseline B
> (SPEC section 7) plus moisture **D**, lapse rate **L**, shortwave radiation
> **R**, and pressure tendency **T**. Precipitation **P** is dropped; neither
> parked option (`rh`, `plev`) is adopted. This is the mechanical rule's own
> output under D57, confirmed unchanged in the session-62 owner review.

This session is the **lock step** of the finish line, run under the same
*lock-before-you-look* discipline as the sealed test (D48 → sessions 39/40).
Its whole job is to freeze that recipe in writing and commit a frozen,
self-guarded confirmation script — **as a pre-registration artifact, before the
reserved 2024-25 year is opened.** The single reserved-year run is the *next*
session (63), not this one.

**Hard scope guard, read this twice:** this session does **not** read, load,
fit, or score a single row of the reserved year (2024-08-01 .. 2025-07-31,
D51). No MAE on the reserved year is computed anywhere. If any step would
require opening the reserved year, stop and surface it instead.

---

## Background you need (self-contained — do not assume chat context)

- **B** is the proven, frozen 5-feature GRIB recipe (SPEC section 7): the
  reference model, never modified; the four selected features enter only on
  top of B.
- **The four selected features**, each already built, committed, and
  integrity-checked in the E1–E5 sessions and re-verified by the session-61
  combine sweep (F106, max abs diff 0.0 vs committed sources):
  - **D** = `dewpoint_depression_t2m_floored` — the stored raw column
    `dewpoint_depression_t2m` with the D53/F100 floor transform
    `max(dewpoint_depression_t2m, 0)` applied (this changes exactly 1 of 7,952
    rows; the raw column is what is committed, the floor is applied in-code).
  - **L** = the E1 lapse-rate feature.
  - **R** = `dswrf_2h_wm2` (E4 radiation).
  - **T** = `pressure_tendency_3h_hpa` (E3 pressure/synoptic).
- **`P`, `rh`, `plev` are NOT in the final set** and must not appear anywhere
  in the confirmation recipe.
- **The reserved year (D51):** 2024-08-01 .. 2025-07-31, held out of the entire
  feature-selection programme. E1–E5 and the combine sweep ran only on the
  three non-reserved `EXPERIMENT_FOLDS`; the reserved year was never touched by
  any of them. The reserved-year guard `assert_reserved_year_excluded()` lives
  in `scripts/session48_reserved_year.py` and raises if a fold's train *or*
  test window overlaps the reserved year.
- **The one authorized use:** D51 permits the reserved year to be opened
  **exactly once**, to confirm the single pre-chosen final set. That one use is
  session 63. This session only *prepares* it.

---

## Task 1 — Record the lock as DECISIONS entry D58

Append **D58** to `DECISIONS.md` (append-only; new entry at the bottom, dated).
It must pin the confirmation recipe completely enough that session 63 has zero
open choices. Include all of the following:

1. **The final set:** B + D, L, R, T, chosen in the session-62 owner review of
   F106. State that it is the D57 mechanical rule's own output, confirmed
   unchanged. Cite D57 / F106.

2. **The two interpretation calls, confirmed** (so the record is closed on
   them): (i) keep/drop votes averaged over the four non-DSM airports — the
   only coherent reading of "DSM is never a keep/drop vote"; (ii) `plev`'s
   adoption test used all five airports per its explicit D57 override — and
   this was outcome-neutral, since `plev` failed on magnitude alone (−0.26pp).

3. **The exact feature resolution:** session 63 reuses the identical
   `CANDIDATE_FEATURES` resolution (source file, column, and any transform) for
   **D, L, R, T** that the session-60 manifest / session-61 sweep used —
   including the D floor transform exactly as pinned. **No feature is rebuilt,
   re-decoded, or re-derived.** `P`, `rh`, `plev` are excluded.

4. **The confirmation fold** (deterministic date arithmetic):
   ```
   train  2021-03-24 .. 2024-07-31
   test   2024-08-01 .. 2025-07-31   (the reserved year — the one authorized look)
   ```
   All five airports (EGLC, LFPG, DSM, YSDU, RNO), frozen LightGBM settings
   (D21.4 / D48.6, same as B), no per-airport feature selection.

5. **Complete-case rule (D57 carried-forward):** build the complete-case row
   set over **only the final-set features' underlying columns** (the columns
   backing D, L, R, T) — drop and count any rows missing any of them, so the
   confirmation matches how the set was selected. **Pre-registered expectation:
   0 rows dropped** (F106 found the seven-feature complete-case set identical to
   the B-only rows, so the four-feature subset drops nothing either); if it is
   not 0, report the count honestly — it is outcome-orthogonal.

6. **What is scored, per airport:** raw-GFS MAE, persistence MAE, refit-B MAE,
   and refit-(B+D,L,R,T) MAE, on the reserved-year test set — so both the bar
   and the four features' added value are visible.

7. **Pre-registered expectations, fixed now, before the look:**
   - **The bar (the deliverable):** B+D,L,R,T beats **both** raw GFS **and**
     persistence on MAE at **all five** airports.
   - **Secondary read:** B+D,L,R,T beats plain B on the airport-averaged MAE.
     Per-airport variation is expected and allowed — especially at **DSM**,
     where the added features are marginal (F96); do **not** pre-register a
     per-airport 5-beats-B claim.
   - The run reports the outcome against these expectations whatever it is; all
     results are reported; there is no re-run and no tuning after the look.

8. **The honesty caveat for the writeup, stated plainly:** the reserved year
   was seen **once, descriptively, for baseline B only**, in F96's multi-year
   backtest — but the **feature-selection** (which features to add) never
   touched it (E1–E5 and the combine sweep ran only on non-reserved folds). So
   this is a genuine first look at the *selected set* on 2024-25. Frame it as
   such; do not overclaim blindness we do not have, and do not claim the year
   is fully unseen.

9. **One-look discipline:** run once, unchanged. A guard that trips on
   something outcome-orthogonal (row counts / scored-day-set reconciliation,
   as in F92/F93) may be corrected and re-committed *before* the look, because
   no MAE is seen — but the features, model, fold, and bar never change.

10. **What D58 did not do:** did not open the reserved year, fit any model, or
    compute any reserved-year MAE (this session is lock-only). Did not modify
    `SPEC.md` or `RESULTS.md`.

---

## Task 2 — Build and freeze the confirmation script (do not run it on the reserved year)

Create `scripts/session62_reserved_confirm.py` — the frozen, self-guarded
confirmation script that session 63 will run **once, unchanged**. It must:

- **Define the confirmation fold** (train / test dates above) and mark it, in
  code and comment, as the **single authorized reserved-year use** citing D51.
- **Keep the D51 guard intact for everything else:** call
  `assert_reserved_year_excluded()` on any *other* fold the script touches
  (e.g. the dry-run fold in the pre-flight below), and only the named
  confirmation fold is exempt. A stray fold that touches the reserved year must
  still raise.
- **Assemble the final-set feature matrix** by reusing the committed columns +
  the pinned D transform (Task 1.3), apply the complete-case rule over the
  D/L/R/T columns (Task 1.5), refit B and B+D,L,R,T on the train window, and
  score raw GFS / persistence / B / B+D,L,R,T on the test window — but this
  scoring path runs against the **reserved year only when invoked in session
  63**, never in this session.
- **Reconcile the scored-day set across all four rungs** (raw / persistence /
  B / B+DLRT) as F93 established, and treat any row-count mismatch as
  outcome-orthogonal.
- **Print pass/fail against the pre-registered expectations** (Task 1.7).

### Pre-flight this session (no reserved-year data)

Run only the outcome-orthogonal, non-reserved parts, to prove the machinery
before the look:

- **Header / date checks:** the D/L/R/T source columns exist; the fold dates
  are correct; the guard authorizes exactly the confirmation fold and raises on
  the three deliberately reserved-year-touching folds (mirror D51's own
  guard-verification pattern).
- **Column-integrity check:** each of D, L, R, T matches its committed source
  (report max abs diff; expect 0.0), reusing F106's own check.
- **Machinery dry-run on an already-seen, non-reserved fold** (use the
  **2023-24** `EXPERIMENT_FOLD`, train 2021-03-24..2023-07-31 / test
  2023-08-01..2024-07-31 — already used descriptively, so no new look is
  spent): assemble features, apply the complete-case rule, refit B and
  B+D,L,R,T, and produce MAE — purely to shake out plumbing bugs end-to-end.
  This spends no reserved-year look and computes nothing on 2024-25.
- Write the pre-flight output to `notes/session-62-preflight-output.txt`.

**Do not run the confirmation fold. Do not read reserved-year rows. No
2024-25 MAE is produced this session.**

---

## Integrity / discipline checklist (must all hold)

- Reserved year 2024-25 never opened; no reserved-year row read, no
  reserved-year MAE computed.
- Sealed year 2025-26 (F94) and all prior verdicts (F16/F30/F47/F64/F82, F94,
  D52–D57) untouched and unrestated.
- No feature rebuilt, re-decoded, or re-derived; committed columns reused.
- `P`, `rh`, `plev` absent from the recipe.
- `SPEC.md` and `RESULTS.md` untouched.
- No archiving of DECISIONS entries this session — D52–D57 / F106 stay live;
  they are load-bearing for the pending session-63 confirmation.

---

## End-of-session steps

1. Confirm D58 is appended to `DECISIONS.md` and the frozen script +
   pre-flight output exist.
2. Overwrite `STATUS.md` as a lean current-state snapshot (prune, do not
   append per the standing rule): the final set is locked (D58), the
   confirmation script is frozen and pre-flighted, reserved year still
   untouched. End STATUS with a **"Next planning session"** line:

   > **Next planning session: session 63 — run the frozen reserved-year
   > confirmation (`scripts/session62_reserved_confirm.py`) once, unchanged, on
   > the 2024-25 fold. This is the single authorized look (D51); report the
   > verdict against D58's pre-registered expectations.**

3. Print a concise summary: D58's key pins, the pre-flight results (guard
   behaviour, column max abs diff, dry-run MAE on 2023-24), and an explicit
   confirmation that no reserved-year data was touched.
4. **Stop and wait for review. Do not commit anything.**
