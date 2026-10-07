# Session 61 — run the pre-registered combine-phase sweep (D57)

## Scope (one session, one scope)

Run the combine-phase feature-selection sweep **exactly as pre-registered in
DECISIONS D57**, using the frozen manifest `scripts/session60_combine_design.py`.
Fit the 14-variant ladder on the three non-reserved `EXPERIMENT_FOLDS`, run the
guards, apply the mechanical selection rule with its joint backstop, and
**report the grid**. Nothing more.

**This session does not:** produce a verdict; pick the final feature set as a
decision (that is the session-62 owner review); read the reserved 2024-25 year
(D51); modify `SPEC.md` or `RESULTS.md`; commit anything; add, drop, or redefine
any variant, feature, threshold, or rule beyond what the manifest already fixes.

**Binding order of authority.** DECISIONS D57 and SPEC are the frozen design.
This prompt is the execution checklist. If this prompt and D57/SPEC ever appear
to disagree, **stop and flag it — do not guess.**

---

## Before loading any data — reserved-year and reuse guards

1. **Import, do not redefine.** Use `scripts/session60_combine_design.py` for
   the folds, the 14-variant ladder, `CANDIDATE_FEATURES` (including `D`'s
   stored raw column `dewpoint_depression_t2m` **plus its frozen one-line
   transform** `max(dewpoint_depression_t2m, 0)` per D53/F100 — apply that
   transform exactly, derive nothing else), and the frozen parameters
   `TAU_SKILL` (0.4%), `ROW_COST_GUARD_FRAC` (5%), and `DROP_ORDER`
   (`T`,`P`,`R`,`L`,`D`). The manifest imports session 48's `EXPERIMENT_FOLDS`
   and reserved-year guard — inherit those, do not re-create them.

2. **Reserved-year guard first.** Clear `assert_reserved_year_excluded()` on all
   three folds **before loading any data**. Then, after loading, run the
   defensive per-row scan confirming **zero** reserved-year rows
   (2024-08-01..2025-07-31). Report both. Note on record that the 2025-26 fold
   **does** test on the sealed year (2025-08-01..2026-07-31, F94) by design —
   that is descriptive reuse, not a fresh verdict look.

3. **Reuse committed columns.** Reuse the committed feature columns from the
   E1–E5 build sessions. Do **not** rebuild, re-decode, or re-derive any
   feature.

---

## The run

4. **One complete-case row set for the whole sweep.** Before fitting any
   variant, build a single complete-case dataset over all seven candidate
   features' underlying columns (`L`,`D`,`T`,`R`,`P`,`rh`,`plev`, where
   `plev` = `t850`,`t925`,`t700`). Every variant is fit and scored on identical
   rows within each (airport, fold). Rows still differ across airports and
   across folds — that is expected. **No** per-variant or core-vs-parked row
   split.

5. **Row-cost guard.** Per airport per fold, report how many rows the
   complete-case mask drops versus a B-only mask. If that exceeds
   `ROW_COST_GUARD_FRAC` (5%) at **any** airport-fold, **halt and report** —
   do not proceed to fitting. (Not expected to trip; F105.)

6. **Fit the 14-variant ladder** on the three folds over that single
   complete-case row set: B (refit); the five single-adds B+L / B+D / B+T /
   B+R / B+P; the full adopted set B+LDTRP; its five leave-one-out variants; and
   the two parked-option adds B+LDTRP+rh and B+LDTRP+plev. Frozen LightGBM
   settings (D21.4/D48.6), identical features at every airport, no per-airport
   selection. Metric: MAE as skill percent vs B, at **grand-overall** (mean
   across 15 airport-folds), **per-fold** (airport-averaged), and **per-airport**
   (fold-averaged).

7. **Integrity checks (report each):**
   - **(i)** Per-row feature-integrity check on the assembled table — every
     feature column matches its committed source file within tolerance, checked
     on every row (the same check F105 ran). Report pass/fail and max abs diff.
   - **(ii)** Internal-consistency check on the join — the refit-B 2025-26 fold
     must reproduce F94/F96/F99–F105's raw-GFS and persistence MAE and row
     counts at every airport, within rounding. Report the comparison.
   - **(iii)** Report the pairwise-correlation matrix among the candidate
     features up front, so the danger-zone drop decisions are visible.

---

## The selection rule (apply mechanically, after the grid is in — D57)

All keep/drop reads are at the **airport-averaged** level; per-airport and
per-fold figures stay diagnostic. **DSM is diagnostic only — never a keep/drop
vote.** Read magnitude on the fold-averaged (airport-averaged) skill and
robustness on sign across all three folds.

8. Start from the full set **B+LDTRP**.
9. **Leave-one-out:** keep a feature if removing it worsens fold-averaged skill
   by at least `TAU_SKILL` (0.4%) **and** is worse in all three folds by sign;
   otherwise it is a candidate to drop. (Full magnitude is **not** required in
   every fold — the thin 2022-23 fold is noisy; F96/D52–D55.)
10. **Correlated-feature safeguard — never drop a correlated batch at once.** If
    two or more features are flagged droppable together, drop only **one** — the
    one whose removal does the least fold-averaged damage, resolving ties by
    `DROP_ORDER`. Then re-measure leave-one-out on the reduced set (a partner
    masked by the just-dropped feature may now clear the bar). Repeat until
    nothing is flagged droppable. The survivors are the **core set**.
11. **Parked options:** test B+core+rh and B+core+plev. Adopt each only if it
    adds at least `TAU_SKILL` fold-averaged **and** helps in all three folds by
    sign, airport-averaged. `plev` must clear the bar airport-averaged **across
    all five airports** (the recipe-travels tax — an RNO-only gain does not
    qualify).
12. Ties go to the **smaller** set. No per-airport selection. Cloud cover is
    inside frozen B and is never dropped.

---

## Joint backstop — stop and surface, never auto-pick (D57)

13. After the rule lands on a set, **refit that exact set** on the three folds
    and confirm:
    - **(a)** it beats B by at least `TAU_SKILL` fold-averaged, worse-by-sign in
      no fold; **and**
    - **(b)** it is **not** meaningfully worse than the full B+LDTRP model
      (within `TAU_SKILL`).
14. If **either** check fails, **halt and surface** the failure with the full
    grid. Do **not** auto-unwind, do **not** auto-pick a set. The owner resolves
    it in the session-62 review.

---

## Output

- Report the full 14-variant grid (all three reads), the correlation matrix, the
  row-cost table, both integrity checks, the reserved-year guard results, the
  step-by-step selection trace, and the joint-backstop outcome.
- **Paste the real output** — actual numbers, not a description of them.
- **No verdict. No reserved-year read.** The single final feature set is the
  session-62 owner review's call.
- New script: `scripts/session61_combine_sweep.py`. Grid CSV under
  `data/processed/`. Full real output under `notes/`.

---

## End-of-session steps

1. Paste the real check output (numbers, not prose).
2. **Overwrite STATUS.md — prune to a current-only snapshot** (present state,
   immediate next action, live open questions only; do **not** append this
   session's write-up to a log). End it with a **"Next planning session"** line:
   *session 62 — owner review of the combine-sweep grid; pick the single final
   feature set, which is then confirmed once on the reserved 2024-25 year at the
   finish line (D51).* If the joint backstop halted, say so plainly in STATUS and
   in that line.
3. Append the session-61 entry to **DECISIONS.md** (the sweep result / finding),
   citing D57. Do not record a family or final-set verdict — report the grid and
   the set the mechanical rule produced (or the backstop halt).
4. **Consistency check:** re-read SPEC, STATUS, DECISIONS; report any
   disagreement, duplicated heading, or out-of-order entry. Report only — do not
   fix silently.
5. **Archive step:** move any newly-settled DECISIONS entries to
   DECISIONS-archive.md per the archive criterion — mechanically, verbatim.
6. Write the suggested commit message, then **stop and wait for review. Do not
   commit.**
