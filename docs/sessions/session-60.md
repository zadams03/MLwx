# docs/session-60.md — combine phase: design and pre-registration (no model fit)

## What this session is

The E1--E5 feature-selection sweep is complete. Five features were adopted, one
per family, each measured against the frozen 5-feature GRIB baseline B (SPEC
section 7):

- `L` = `lapse_rate_t2_t850` (D52)
- `D` = `dewpoint_depression_t2m_floored` (D53)
- `T` = `pressure_tendency_3h_hpa` (D54)
- `R` = `dswrf_2h_wm2` (D55)
- `P` = `precip_rate_mmh` (D56)

Two candidates were parked, not adopted, for the combine phase:

- `rh` = `relative_humidity_2m` (D53)
- `plev` = the three raw pressure-level temperatures `t850`, `t925`, `t700`
  (D52)

The **combine phase** sweeps these together on the three non-reserved
`EXPERIMENT_FOLDS` (D51) to select **one single final feature set**, which is
then confirmed on the reserved 2024-25 year exactly once, at the finish line
(D51).

**This session does the design only. It fits no model, loads no data rows, and
computes no MAE.** Its whole job is to pre-register the combine-sweep method in
writing and in code *before* the run (session 61) — the same "lock before you
look" discipline (SPEC 2.4) that session 48 applied when it reserved the
confirmation year (D51). The run is session 61; the owner-review verdict that
picks the set is session 62; the reserved-year confirmation is the finish line
after that.

**Scope is strict.** Write the design (a new DECISIONS entry D57), create one
manifest module, run one header-only pre-flight check, and update STATUS. Do
**not** fit anything, do **not** read any data rows, do **not** touch the
reserved year or the sealed year, do **not** modify SPEC.md or RESULTS.md, and
do **not** commit.

---

## Step 1 — Create the frozen manifest module

Create `scripts/session60_combine_design.py`. This is the frozen spec-in-code
that session 61 will import, so it cannot drift from what is pre-registered
here. It defines constants and runs a schema-only pre-flight; it fits nothing
and loads no data rows.

It must:

1. **Import, do not re-implement**, from `scripts/session48_reserved_year.py`:
   `EXPERIMENT_FOLDS`, `RESERVED_YEAR_START`, `RESERVED_YEAR_END`, and
   `assert_reserved_year_excluded()`. The combine sweep reuses session 48's
   fold definitions and reserved-year guard exactly. Do not redefine them.

2. Define `CANDIDATE_FEATURES` — a mapping from each short name (`L`, `D`, `T`,
   `R`, `P`, `rh`, `plev`) to its committed source file, its exact column
   name(s), and the deciding entry it comes from (D52--D56 for the adopted
   five; D53/D52 for the two parked). `plev` maps to three columns
   (`t850`, `t925`, `t700`). **These columns are reused as already built and
   committed by the E1--E5 build sessions. Nothing is rebuilt, re-decoded, or
   re-derived.**

3. Define `VARIANT_LADDER` — an ordered list of `(variant_name, feature_set)`,
   with `feature_set` given as short names on top of B. Exactly these 14
   variants, no more, no fewer:

   ```
   B                      (control, refit)
   B+L   B+D   B+T   B+R   B+P            (5 single-adds)
   B+LDTRP                                (full adopted set)
   B+DTRP  B+LTRP  B+LDRP  B+LDTP  B+LDTR (5 leave-one-out from full)
   B+LDTRP+rh   B+LDTRP+plev             (2 parked-option adds on top of full)
   ```

4. Define the pre-registered constants:
   - `TAU_SKILL = 0.004` — the minimum practical skill change (0.4%) that
     counts as "clearly worse / clearly better", fold-averaged. See D57.
   - `ROW_COST_GUARD_FRAC = 0.05` — the complete-case row-cost guard (see D57).
   - `DROP_ORDER = ['T', 'P', 'R', 'L', 'D']` — weakest-adopted-family first,
     the fixed tie-break for backward elimination (see D57).

5. Provide a **header-only pre-flight** function that, for every entry in
   `CANDIDATE_FEATURES`, confirms the source file exists and contains the named
   column(s). Read headers only (e.g. zero rows) — load no data rows, fit
   nothing. Print a table of file / column / present-or-missing. If any file or
   column is missing, raise with a clear message. This de-risks the manifest so
   a typo in a column name is caught now, not at run time.

Run the module once and paste its **real pre-flight output** (the file/column
table), per CLAUDE.md's end-of-session rule. Full output to
`notes/session-60-preflight-output.txt`.

---

## Step 2 — Write the design into DECISIONS.md as D57

Append this entry (date it, keep the numbering). This is the binding
pre-registration; session 61 executes exactly this and nothing else.

> **D57. The combine-phase sweep is pre-registered here, before the run
> (session 61), and enforced by the `scripts/session60_combine_design.py`
> manifest. It sweeps the five adopted features (D52--D56) together, with the
> two parked candidates (D52, D53) as options, on the three non-reserved
> `EXPERIMENT_FOLDS` (D51), to select one single final feature set. That set is
> then confirmed on the reserved 2024-25 year exactly once, at the finish line
> (D51). No model was fit and no data row was read this session — design only
> (the same setup-only shape as D51/session 48).**
>
> **Baseline and harness.** Frozen baseline B is the proven 5-feature GRIB
> recipe (SPEC section 7); it is never modified, and features enter only on top
> of B. The harness is identical to E1--E5: the three non-reserved
> `EXPERIMENT_FOLDS` (2022-23, 2023-24, 2025-26-truncated, D51), all five
> airports (EGLC, LFPG, DSM, YSDU, RNO), the frozen LightGBM settings
> (D21.4/D48.6), and no per-airport feature selection (identical features at
> every airport). Metric: MAE, reported as skill percent vs B, at grand-overall
> (mean across the 15 airport-folds), per-fold (airport-averaged), and
> per-airport (fold-averaged) — the same three reads as every E-session.
>
> **The variant ladder (14 variants, frozen in the manifest).** B (refit); the
> five single-adds B+L / B+D / B+T / B+R / B+P; the full adopted set B+LDTRP;
> the five leave-one-out variants from the full set; and the two parked-option
> adds B+LDTRP+rh and B+LDTRP+plev (`plev` = `t850`,`t925`,`t700`). A compact,
> pre-registered ladder is used rather than a blind 2^5 subset sweep: it holds
> the number of comparisons down (less chance the "winner" is a fold-fluke,
> which matters because only one reserved-year look protects the pick), and
> each rung answers a specific keep/drop question, so the result is
> interpretable, not just a bare winner.
>
> **One complete-case row set for the whole selection.** Before any variant is
> fit, build a single complete-case dataset over all seven candidate features
> (`L`,`D`,`T`,`R`,`P`,`rh`,`plev` — i.e. their underlying columns). Within each
> (airport, fold) every variant is fit and scored on identical rows; rows still
> differ across airports and across folds, which is expected. There is no
> per-variant or core-vs-parked row split — that would break the "same rows for
> every variant" guarantee exactly where it matters. **Row-cost guard:** the run
> reports, per airport per fold, how many rows the complete-case mask drops
> versus a B-only mask; if that exceeds `ROW_COST_GUARD_FRAC` (5%) at any
> airport-fold, the run halts and reports rather than proceeding, and the owner
> decides in planning. (Not expected to trip: session 58/F105 found these GRIB
> fields present wherever B is.) Honest consequence: B refit on this masked set
> is not row-identical to F94, so its MAE here is not cross-comparable to F94's
> — expected, do not cross-read the two.
>
> **The "clearly worse" thresholds, fixed before the run.** Judged on relative
> skill percent, not absolute degrees (MAE runs ~1.0--1.6 degC across airports,
> so one degree would mean different things at different airports; percent is
> how every family result was reported). A feature's contribution is read two
> ways, each where it is reliable: **magnitude** — removing it must worsen the
> fold-averaged (airport-averaged) skill by at least `TAU_SKILL` (0.4%, about
> half the weakest adopted family, E3's +0.9%); and **robustness** — removal
> must be worse in all three folds by sign (no fold where the feature looks
> unhelpful). The full magnitude is not required in every fold — the thin
> 2022-23 fold is noisy and would randomly fail good features (F96/D52--D55
> fold-quality caution). All keep/drop reads are at the airport-averaged level;
> per-airport and per-fold figures stay diagnostic. **DSM is read as a
> diagnostic only** (F96: most headroom, cloud/wind already marginal there) —
> it is never a keep/drop vote.
>
> **The selection rule (mechanical, applied by session 61 after the grid is in).**
> (1) Start from the full set B+LDTRP. (2) Leave-one-out: a feature is kept if
> removing it worsens fold-averaged skill by at least `TAU_SKILL` *and* is worse
> in all three folds by sign; otherwise it is a candidate to drop. (3)
> **Correlated-feature handling — never drop a correlated batch at once.** If two
> or more features are flagged droppable together, drop only one — the one whose
> removal does the least fold-averaged damage — resolving ties by `DROP_ORDER`
> (`T`,`P`,`R`,`L`,`D`, weakest family first). Then re-measure leave-one-out on
> the reduced set: a partner that was masked by the just-dropped feature may now
> clear the bar and be kept. Repeat until nothing is flagged droppable. This
> defeats the known trap where two overlapping features each look redundant only
> because the other is present. (4) The survivors are the core set. (5) Parked
> options: test B+core+rh and B+core+plev, each adopted only if it adds at least
> `TAU_SKILL` fold-averaged and helps in all three folds by sign, airport-
> averaged; `plev` must clear the bar airport-averaged across all five airports
> (the recipe-travels tax — an RNO-only gain does not qualify, which is why it
> was parked, not adopted). (6) Ties go to the smaller set. (7) No per-airport
> selection; DSM diagnostic only. Cloud cover is inside frozen B and is never
> dropped, so any feature that overlaps a B feature (e.g. `rh`/`R` vs cloud) is
> only ever judged on what it adds *given* B — the correct question.
>
> **Joint backstop, with stop-and-surface.** Leave-one-out reads each feature
> given all the others, so the exact set the rule lands on may never have been
> fit as a whole. So after the rule selects a set, refit that exact set on the
> three folds and confirm: (a) it beats B by at least `TAU_SKILL` fold-averaged,
> worse-by-sign in no fold; and (b) it is not meaningfully worse than the full
> B+LDTRP model (within `TAU_SKILL`). If either check fails — evidence of
> over-pruning or a joint loss — **session 61 halts and surfaces the failure
> with the full grid. It does not auto-unwind and does not auto-pick a set.**
> The owner resolves it in the session-62 review. No unsupervised selection of
> the final recipe.
>
> **Integrity and reuse guards session 61 must run.** (i) Reuse the committed
> feature columns from the E1--E5 build sessions; do not rebuild, re-decode, or
> re-derive any feature. (ii) Per-row feature-integrity check on the assembled
> table: every feature column matches its committed source file within
> tolerance, checked on every row (the same check F105 ran); report pass/fail
> and max abs diff. (iii) Internal-consistency check on the join: the refit-B
> 2025-26 fold must reproduce F94/F96/F99--F105's raw-GFS and persistence MAE
> and row counts at every airport, within rounding; report the comparison. (iv)
> Report the pairwise-correlation matrix among the candidate features up front,
> so the reviewer can see which drop decisions sit in the danger zone.
>
> **Reserved-year and sealed-year discipline.** The reserved 2024-25 year
> (2024-08-01..2025-07-31, D51) is not read at all — not this session, not in
> the session-61 run. All selection is on the three non-reserved folds only.
> Note explicitly: the 2025-26 fold does test on the sealed year
> (2025-08-01..2026-07-31, F94), by design — D51 built the folds this way, with
> training truncated so they never reach the reserved year — and that is
> descriptive reuse, not a fresh verdict look. The single confirmation at the
> finish line is on the **reserved 2024-25 year**, once, after the set is
> frozen; it is never a second look at 2025-26. Session 61 must clear
> `assert_reserved_year_excluded()` on all three folds before loading any data,
> and run a defensive per-row scan confirming zero reserved-year rows (same as
> the E-sessions). Carried forward for the finish line: when the frozen set is
> confirmed on 2024-25, apply the same complete-case rule over the *final* set's
> features (drop and count rows missing any final-set feature), so the
> confirmation matches how the set was selected.
>
> **What this decision did not do.** Did not fit any model or compute any MAE.
> Did not read any data row, from the reserved year, the sealed year, or any
> other year — the pre-flight reads headers only. Did not modify SPEC.md or
> RESULTS.md. Nothing was committed. Manifest:
> `scripts/session60_combine_design.py` (new). Pre-flight output:
> `notes/session-60-preflight-output.txt`.

---

## End-of-session steps

1. Paste the **real pre-flight output** from step 1 (the file/column table) —
   actual result, not a description.
2. **Overwrite STATUS.md**, pruning to a current-only snapshot (present state,
   the immediate next action, live open questions only — never an accumulating
   log). It should record that the combine sweep is designed and pre-registered
   (D57) and the manifest built, with the reserved year still untouched. End it
   with this exact handoff line:

   > **Next planning session: session 61 — run the pre-registered combine sweep
   > (D57): fit the 14-variant ladder on the three non-reserved
   > `EXPERIMENT_FOLDS` over the single complete-case row set, run the row-cost
   > guard and the integrity checks, apply the selection rule with the joint
   > backstop, and report the grid — no verdict, no reserved-year read. The
   > session-62 owner review then picks the single final feature set.**

3. **Consistency check:** re-read SPEC.md, STATUS.md, and DECISIONS.md and
   report anything that disagrees, any duplicated heading, and any entry out of
   order. Report only — do not fix silently.
4. **Archive pass:** move any DECISIONS.md entries that became settled this
   session to DECISIONS-archive.md, per the archive criterion — mechanically,
   verbatim. (Likely nothing this session; report if so.)
5. **Stop and wait for review. Do not commit.**
