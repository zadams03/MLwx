# docs/session-58.md — the staged E5 (precipitation) experiment (a reading, not a verdict)

You have already read `CLAUDE.md`, then `SPEC.md`, `STATUS.md`, and
`DECISIONS.md` in full. This prompt is self-contained; where it and a spec
file disagree, stop and flag it (do not guess).

Stay strictly within this scope. Stop at the end-of-session steps and wait
for review. **Do not commit anything.**

---

## 1. What this session is

Run the staged **E5 (precipitation)** experiment: a clean **B vs B+P** read
of whether the one precipitation feature built in session 57 (F104,
`precip_rate_mmh`) adds skill on top of the frozen 5-feature GRIB baseline,
across the three non-reserved `EXPERIMENT_FOLDS` (D51).

This is a **learning experiment, not a sealed-bar test.** It reports a grid
and a summary — **no pass/fail, no adopt/park verdict.** The E5 family call
is the owner's review decision in the *next* session (session 59, D56), not
this one. Mirror the shape of session 56's E4 experiment (F103) exactly,
adapted to two variants instead of four.

E5 is the **last** family in the feature-selection programme.

## 2. Two variants only — NOT a four-variant grid

Session 57's Step 0 (F104) established that E5 carries **effectively one
feature**: `precip_rate_mmh` and the raw `apcp_cumulative_mm` differ only by
a fixed per-airport scale (a monotone transform), and LightGBM tree splits
are invariant to a monotone per-feature transform — so to a tree they are the
**same feature**. There is therefore no meaningful raw-vs-resolved contrast to
test, unlike E1–E4. **Do not reintroduce Pv / v variants** — they would be
identical to B+P by construction.

- **B** — the frozen 5-feature GRIB set (SPEC 7.2: elevation-corrected GRIB
  forecast temperature, `season_sin`, `season_cos`, `cloud_cover`,
  `wind_speed_10m`), **REFIT on these three folds.** This is B and only B —
  **not** B+L / B+D / B+T / B+R. The measurement baseline is unchanged
  (D52–D55): every family in the sweep is measured against the frozen
  5-feature B, never against an adopted feature.
- **B+P** — B plus `precip_rate_mmh` (one continuous feature, **no
  transform** — no log1p, no binary wet/dry flag; a decoded zero is a real,
  kept dry-forecast value, per F104).

Both variants use the unchanged LightGBM settings (D21.4 / D48.6). **No
per-airport feature selection** — identical features at every airport, in
both variants, RNO included.

## 3. Inputs

Read the two committed session-57 output files (F104), unchanged. Do **not**
re-pull, re-decode, or re-derive any precipitation field.

- `data/processed/session57_v16_window_with_precip.csv` (6,128 rows) —
  carries the training span and the 2022-23 / 2023-24 fold test spans.
- `data/processed/session57_sealed_window_with_precip.csv` (1,826 rows) —
  carries the 2025-26 fold's test span.

Read **per-airport** across all five (EGLC, LFPG, DSM, YSDU, RNO), with
**DSM as the diagnostic** (F96: most headroom, cloud/wind already marginal
there).

## 4. Folds — the three non-reserved `EXPERIMENT_FOLDS` (D51)

Import `EXPERIMENT_FOLDS` and `assert_reserved_year_excluded` from
`scripts/session48_reserved_year.py` — do not redefine either. The three
folds:

```
label      train                    test
2022-23    2021-03-24..2022-07-31   2022-08-01..2023-07-31
2023-24    2021-03-24..2023-07-31   2023-08-01..2024-07-31
2025-26    2021-03-24..2024-07-31   2025-08-01..2026-07-31   (train truncated at 2024-07-31)
```

The 2024-08-01..2025-07-31 **reserved confirmation year (D51) is never
loaded, trained on, tested on, or scored — at all, this session.** The
2025-26 fold's training window stops at 2024-07-31 on purpose, before the
reserved year begins.

## 5. Two sanity checks — run BOTH before any model is fit

Neither is optional; both must run and pass before a single fit.

**5a. Reserved-year guard.** Call `assert_reserved_year_excluded()` on all
three `EXPERIMENT_FOLDS` entries before any data is loaded (expect no
raise). After loading, run a defensive per-row scan of the loaded data for
any 2024-08-01..2025-07-31 date (expect 0). Report both results.

**5b. Feature-integrity check — on every row, not a spot check.** Confirm
that `precip_rate_mmh == apcp_cumulative_mm / precip_window_hours` at every
row, where the since-start window is **24 h at EGLC / LFPG / DSM** and
**26 h at YSDU / RNO** (F104). Use the stored `precip_window_hours` column if
the file carries one; otherwise use the per-airport constant. Allow a small
float tolerance for the 3-decimal stored values (e.g. 1e-3 mm/h). Report the
max absolute difference per airport. This guards against a silently
mis-joined or mis-scaled precip column before it can bias the read.

## 6. Internal-consistency reproduction check

As F99–F103 each did: confirm the **2025-26 fold's B variant** (refit
5-feature baseline, trained on one fewer year than F94 because training may
not reach the reserved year) reproduces the raw-GFS and persistence MAE and
row counts of F94 / F96 / F99 / F100 / F101 / F103 closely at every airport.
Report the comparison. This confirms the join, features, and model settings
are a correct reproduction of the frozen recipe before the B+P read is
trusted.

## 7. Outputs

- Script: `scripts/session58_e5_experiment.py` (new).
- Full real output (actual numbers, not a description): `notes/
  session-58-e5-experiment-output.txt`.
- `data/processed/session58_e5_experiment_grid.csv` — 30 rows (5 airports ×
  3 folds × 2 variants), MAE per cell.
- `data/processed/session58_e5_experiment_summary.csv` — fold-averaged
  per-airport (10 rows), airport-averaged per-fold (6 rows), and
  grand-overall (2 rows).

## 8. What to report (mirror F103's shape, two variants)

Report descriptively, with the numbers, **no verdict**:

- **Grand overall** — mean MAE across all 5 airports × 3 folds (n=15
  airport-folds per variant), for B and B+P, with delta vs B and skill vs B.
- **Fold-averaged per airport** — B+P skill vs B at each of the five
  airports.
- **E5's max grand-overall skill placed against E1–E4**, plainly: E1 max
  +2.0% (B+Lv, F99), E2 max +4.1% (B+Dv, F100), E3 max +0.9% (B+T, F101),
  E4 max +1.9% (B+Rv, F103). State where E5 sits.
- **The specific question, read with the numbers.** This is a
  marginal-over-existing-features test — does precipitation add skill on top
  of B? Read it honestly airport by airport, calling out **DSM (the
  diagnostic)** specifically: does precipitation add anything there, or
  (like E3/E4) leave it flat once cloud/wind are already in the model?
- **Per-fold spread.** Airport-averaged per fold for both variants. Flag the
  thinnest fold (2022-23, per F96/D52–D55's established caution) and state
  explicitly whether B+P **reverses to negative in the most recent 2025-26
  fold** the way E3 (F101) did, or stays positive like E4 (F103).
- Note the **known cross-airport inconsistency** already on record (F104):
  the since-start window is 24 h at three airports and 26 h at two, so
  `precip_rate_mmh` is a mean over slightly different spans — reported, not
  papered over.

## 9. End-of-session steps

1. Paste the **real output** — actual numbers, not a description.
2. Append a new finding **F105** to `DECISIONS.md` documenting this E5
   experiment (the two-variant grid, both sanity-check results, the
   reproduction check, and the descriptive read) — a **finding, not a
   verdict**. Mirror F103's structure. End it with a "What this session did
   not do, on purpose" paragraph (no model fit on the reserved year, no
   pass/fail computed, no per-airport selection, no SPEC/RESULTS edit,
   nothing committed).
3. Overwrite `STATUS.md` as the current-only snapshot. Its **"Next planning
   session" line must read: session 59 — record the E5 (precipitation)
   family verdict (DECISIONS D56) from the owner's review of F105; with that,
   the whole E1–E5 family sweep has a verdict and the housekeeping session
   (then the combine phase / reserved-year finish line) is next.**
4. Run the **consistency check** (CLAUDE.md): re-read SPEC / STATUS /
   DECISIONS and report anything that disagrees, any duplicated heading, and
   any log entry out of order. Report only — do not fix silently.
5. Run the **archive step** (CLAUDE.md): move any DECISIONS.md entries that
   became settled this session to the archive, per the archive criterion —
   mechanically, verbatim. (If nothing qualifies, say so.)
6. **Stop and wait for review. Commit nothing.**

## 10. Scope guardrails — do NOT

- Do not read, load, train on, test on, or score any row of the reserved
  2024-08-01..2025-07-31 year (D51).
- Do not compute any pass/fail, adopt, or park decision — that is session
  59's job (D56).
- Do not add a third or fourth variant, or any Pv / v variant.
- Do not add `lapse_rate_t2_t850` (D52), `dewpoint_depression_t2m_floored`
  (D53), `pressure_tendency_3h_hpa` (D54), or `dswrf_2h_wm2` (D55) to B — B
  stays the frozen 5-feature set only.
- Do not do any per-airport feature selection.
- Do not re-pull, re-decode, or re-derive any precipitation field; reuse
  session 57's committed outputs unchanged.
- Do not touch `SPEC.md` or `RESULTS.md`.
- Do not touch the sealed-year verdicts (F94) or any minimal-method verdict.
