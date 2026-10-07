# Session 52 — the E2 moisture experiment: fit the moisture variants on the three non-reserved folds and read the result (a reading, not a verdict)

Read CLAUDE.md, SPEC.md, STATUS.md and the live DECISIONS.md in full first, as
every session does. This prompt is self-contained; where it cites a rule or a
past result by number (Dxx / Fxx / SPEC 7.x), that citation is the authority. If
this prompt and a spec file disagree, stop and flag it rather than guess.

---

## Context (where the programme is)

The feature-selection programme adds one physical feature-family at a time onto
the frozen 5-feature GRIB baseline B (SPEC 7), to learn each family's standalone
marginal contribution before any families are combined. The governing rules
(D51, D52):

1. **Each family is measured against the same frozen 5-feature baseline B**
   (`temp`, `season_sin`, `season_cos`, `cloud_cover`, `wind_speed_10m`),
   individually — not against a baseline that has already absorbed an earlier
   family. B is refit on each fold; only its feature set is frozen.
2. **The reserved year 2024-08-01..2025-07-31 (D51) is never touched** — no
   pull, load, join, or score — until one final feature set is confirmed on it
   once, at the very end.
3. **Same features at every airport, always** — no per-airport feature selection.

**E1 (upper-air) is done and its verdict recorded** (D52): its adopted feature is
`lapse_rate_t2_t850`; that adoption is provisional and enters only at the later
combine phase, so it does **not** change B for this session.

**E2 (moisture) is the current family. Its data build is finished** (session 51):
`relative_humidity_2m`, `dew_point_2m`, `specific_humidity_2m` (all 2 m) and the
derived `dewpoint_depression_t2m` are joined onto the existing 5-feature dataset
at `data/processed/session51_v16_window_with_moisture.csv` and
`session51_sealed_window_with_moisture.csv`, validated (0 join drops, 0 nulls,
Magnus self-check tight). **This session fits the experiment** — the same
build-then-experiment split E1 used (session 49 built, session 50 fit), and the
direct analogue of session 50 / F99.

**This is a LEARNING experiment, not a sealed-bar test.** It reports a grid, not
a pass/fail verdict. The E2 family verdict is made by the owner in review next
session, exactly as the E1 verdict was.

---

## Task 1 — Sanity checks before any model is fit (mirror F99's own "First" block)

Print the real result of each; if any would fail, STOP before loading data.

1. **Reserved-year guard on all three folds.** Run
   `scripts/session48_reserved_year.py`'s `assert_reserved_year_excluded()` on
   each of the three `EXPERIMENT_FOLDS` (2022-23, 2023-24, truncated 2025-26)
   before any data is loaded. No fold may touch 2024-08-01..2025-07-31.
2. **Moisture-feature integrity check, on every row (not a spot check).** On both
   session-51 output files, verify `dewpoint_depression_t2m` equals
   `t2m_raw − dew_point_2m` (to the stored precision) at every row, and that the
   three moisture columns are non-null everywhere. Report max absolute
   reconstruction difference per airport (expect ~0).
3. **Apply and document the depression floor.** Exactly one row carries a
   physically-impossible negative depression — DSM 2024-01-26, −0.003 °C at
   RH 100 % (session 51's sanity check). Construct the modeling feature as
   `max(dewpoint_depression_t2m, 0)`. Keep the original column intact as the
   audit trail; apply the floor only in the feature matrix. This is a deliberate,
   documented choice (dew point cannot physically exceed air temperature; the one
   negative value is a saturation-boundary decode artifact) and is immaterial to
   any result — report how many rows it changed (expected: 1) so it is on the
   record, not silent.

---

## Task 2 — Fit the four moisture variants on the three non-reserved folds

Fit four variants at every airport on each of the three `EXPERIMENT_FOLDS`
(5 airports × 3 folds × 4 variants = a 60-row grid), the exact shape F99 used.
All four use the **unchanged D21.4 / D48.6 LightGBM settings** — nothing tuned
per airport, nothing tuned between variants — and expanding-window,
out-of-fold test MAE, same as F99.

**The four variants** (naming parallels E1: `D` = the derived depression,
`v` = the raw moisture fields):

- **B** — the frozen 5-feature set, **refit on these three folds** (not a reuse
  of F94/F96, which were fit on different windows).
- **B+D** — B plus `dewpoint_depression_t2m` (floored; one added feature).
- **B+Dv** — B+D plus the raw moisture fields (see the design choice below).
- **B+v** — B plus the raw moisture fields, **without** the derived depression.

**DESIGN CHOICE — what the raw moisture set `v` contains.** The default here,
mirroring E1's `v = {t850, t925, t700}` (three raw fields, one of which — t850 —
also feeds the derived lapse rate), is:

> **`v = {relative_humidity_2m, specific_humidity_2m, dew_point_2m}`** — all
> three pulled raw fields, with `dew_point_2m` appearing in `v` just as `t850`
> appeared in E1's `v` while also feeding the derived feature.

This keeps E2 structurally identical to E1 and makes B+D-vs-B+v answer the same
"does handing the model the derived difference beat making it reconstruct that
difference from raw fields" question. (If the owner instead wants `v` limited to
`{relative_humidity_2m, specific_humidity_2m}`, treating dew point purely as the
depression's input, that is a one-line change — but it breaks the clean E1
parallel and is not the default.)

Also report, for B+D and B+v, the per-airport LightGBM feature importances (the
same diagnostic F99 reported), so the derived-vs-raw story can be read directly.

---

## Task 3 — Read and report (a reading, not a verdict)

Write the grid and the summary, then report the reads plainly. Do **not** issue a
pass/fail verdict or adopt any feature — that is the owner's review next session.

- **Tables:** `data/processed/session52_e2_experiment_grid.csv` (60 rows:
  station, fold, variant, n_train, n_test, raw_mae, persist_mae, mae,
  delta_vs_B, skill_vs_B_pct — the same columns as
  `session50_e1_experiment_grid.csv`) and
  `data/processed/session52_e2_experiment_summary.csv`
  (fold-averaged-per-airport, airport-averaged-per-fold, and grand-overall).
- **Report in the session output:** grand-overall skill vs B for each variant;
  the fold-averaged-per-airport skill-vs-B table (the F99-shaped table); and the
  staged read — (a) does `dewpoint_depression_t2m` alone (B+D) capture most of
  the family's benefit; (b) do the raw fields add anything on top (B+Dv vs B+D);
  (c) does the derived form beat the raw fields alone (B+D vs B+v).
- **DSM is the diagnostic**, not a gate (F96: most headroom there; F99: upper-air
  did help there). Report its per-variant read explicitly. But the **primary
  criterion is lower MAE across airports** — average and per-airport — which is
  the deliverable's actual goal.
- **Per-fold caution.** Report the per-fold spread, not only fold-averages: F96
  and the E1 review both showed a single fold (2025-26 especially) can be
  unrepresentative, so note any airport where a fold-averaged result is carried
  by one fold.
- **Free internal-consistency check (as F99 did).** Confirm the 2025-26 fold's B
  variant reproduces F94/F96's own raw-GFS and persistence MAE and row counts at
  every airport — a check that the pipeline is a correct reproduction of the
  frozen recipe. Report the comparison.

---

## Scope guardrails (hold these)

- **This session fits models on the three non-reserved folds only.** It computes
  no sealed-bar verdict and adopts no feature.
- **Reserved year (2024-08-01..2025-07-31) is never touched.**
- **B is measured with its frozen 5-feature set** — E1's `lapse_rate_t2_t850` is
  NOT added to the baseline (D52); it enters only at the combine phase.
- **SPEC.md and RESULTS.md are not modified.**
- **No per-airport feature selection** — identical variants at all five airports.
- **One scope, this scope.** Anything outside it that looks worth doing goes to
  DECISIONS.md as an open question, not acted on.

---

## End-of-session steps (required)

1. Paste the **real output** — actual numbers, not a description.
2. **Consistency check:** re-read CLAUDE.md, SPEC.md, STATUS.md and live
   DECISIONS.md; report any disagreement, duplicated heading, or out-of-order
   entry. Report only — do not fix silently.
3. **Archive step:** move any DECISIONS.md entry that became settled this session
   to DECISIONS-archive.md, per the archive criterion — mechanically, verbatim.
   (The new E2 finding is a live input to an open programme; expect nothing newly
   archivable, but check.)
4. **Overwrite STATUS.md** as the fresh snapshot, and **end it with a "Next
   planning session" line**: *session 53 — open, for the owner's review: the E2
   moisture family verdict from this session's grid, then (if E2 is adopted into
   the combine-phase baseline) the start of the next family's build (E3,
   pressure/synoptic — lead with the derived tendency, per the roadmap).*
5. **Prepare all changes and write out a single suggested commit message as
   plain text** (title line plus a full multi-paragraph body; no double quotes
   and no apostrophes in the body; `--` not em-dashes), then **stop and wait for
   review.** Do not commit, add, or push — the owner reviews and commits by hand.
   Write the message as text under a clear heading; do not run any command at
   this step.
