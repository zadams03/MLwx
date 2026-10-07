# Session 56 — the staged E4 (radiation) experiment

Read `CLAUDE.md`, `SPEC.md`, `STATUS.md`, and the live `DECISIONS.md` in full
before starting, per CLAUDE.md's own routine. This session runs one
experiment and reports a grid. **It is a LEARNING experiment, not a
sealed-bar test: it reports MAE and skill-vs-B, not a pass/fail verdict. The
E4 family call — what to adopt — is the owner's review decision in the NEXT
session (session 57), not made here.** No model is fit on, and no row is read
from, the reserved 2024-08-01..2025-07-31 confirmation year (D51) at any
point.

This mirrors session 50 (E1, F99), session 52 (E2, F100), and session 54
(E3, F101) exactly in shape. Where those sessions' own experiment scripts are
a correct template, follow them. There is no verdict-recording task at the
top of this session: E4's build (F102) ran last session but its experiment
has not — so the E4 verdict is recorded at the top of session 57, not now.

---

## Preamble — a one-line cosmetic cleanup before the experiment (do first)

F102 recorded a known cosmetic bug in `scripts/session55_radiation_pull.py`:
its Step-0 printed decision summary mis-describes the intermediate f022 file
as itself needing de-accumulation against a nonexistent "f020" file. F102 is
explicit that this is a **console-narration artifact only** — the actual
pull/join code (`build_combos`, `process_combo`, `build_joined`) never treats
f022 as a top-level combo and fetched exactly the right messages throughout;
no computed value is or was affected.

Fix the print-loop text so the summary no longer describes the phantom f020
de-accumulation, so the artifact isn't carried forward into any later reuse
of the script. **This is a text/print-statement fix only** — do not change
any data-path logic (`build_combos`, `process_combo`, `build_joined`, the
lead/window arithmetic, or the fetch counts). After the edit, confirm by
re-reading the changed lines that only narration text changed, and state that
plainly. Do not re-run the session-55 pull — the committed session-55 output
files are correct and are the inputs to this experiment. This cleanup does
not alter F102 (its numbers stand); note the fix in this session's own
finding.

---

## What to run

Fit four feature variants on the three non-reserved `EXPERIMENT_FOLDS`
defined in `scripts/session48_reserved_year.py` (2022-23, 2023-24, and the
truncated 2025-26), reusing session 55's committed output files
(`data/processed/session55_v16_window_with_radiation.csv` and
`data/processed/session55_sealed_window_with_radiation.csv`) unchanged. Pull
no new data.

**The four variants — all on D21.4/D48.6's unchanged LightGBM settings, no
per-airport feature selection, identical features at all five airports:**

- **B** — the frozen 5-feature set (`temp`, `season_sin`, `season_cos`,
  `cloud_cover`, `wind_speed_10m`), REFIT on these three folds. Pure frozen
  baseline — it does NOT include E1's `lapse_rate_t2_t850`, E2's
  `dewpoint_depression_t2m_floored`, or E3's `pressure_tendency_3h_hpa`. Per
  D52/D53/D54, every E-family is measured against pure B; adopted features
  enter only at the later combine phase.
- **B+R** — B plus the resolved radiation feature `dswrf_2h_wm2` (the single
  physically-consistent 2-hour-window shortwave feature F102 built).
- **B+Rv** — B+R plus the two raw de-accumulation-endpoint columns
  `dswrf_ave_to_lead_wm2` and `dswrf_ave_to_lead_minus2_wm2`.
- **B+v** — B plus those two raw endpoint columns, WITHOUT the resolved
  `dswrf_2h_wm2`.

(Same derived-alone / derived+raw / raw-alone three-way contrast E1/E2/E3
used, so "does the resolved feature carry the family, or do the raw endpoints
add something" reads the same way.) Note the E4 `v` set differs in KIND from
E1–E3's: E1–E3's raw fields were independent physical variables, whereas E4's
raw endpoints are the two accumulation values the resolved feature is
DERIVED from — so `B+Rv` and `B+v` here test whether the model does better
with the raw energy endpoints than with the clean 2-hour rate. Report that
framing so the grid is read correctly.

## The specific question this experiment answers (state it in the output)

`cloud_cover` is ALREADY in the frozen baseline B, and cloud is the dominant
control on how much shortwave reaches the ground (F97's own note: cloud
proxies much of shortwave). So E4 is specifically a test of whether radiation
adds skill BEYOND the cloud feature already present — a marginal-over-cloud
test, not a from-scratch test. A small or null B+R result is a plausible,
honest outcome (radiation largely redundant with cloud), not a failure.
Frame the result this way, DSM read as the diagnostic airport (F96: most
headroom, where cloud/wind were already marginal).

## Two sanity checks before any model is fit (mirror F99/F101's own)

1. **Reserved-year guard.** Run `assert_reserved_year_excluded()` on all
   three `EXPERIMENT_FOLDS` before any data is loaded; STOP if any raises.
   Add a defensive per-row scan confirming zero reserved-year rows loaded.
2. **Feature-resolution check, on every row (not a spot check).** For the
   three lead-24 airports (EGLC, LFPG, DSM), verify F102's own
   de-accumulation identity holds on every row:
   `dswrf_2h_wm2 == (dswrf_ave_to_lead_wm2*6 - dswrf_ave_to_lead_minus2_wm2*4) / 2`
   within a rounding tolerance; for the two lead-26 airports (YSDU, RNO),
   verify `dswrf_2h_wm2 == dswrf_ave_to_lead_wm2` (native 2-hour window, used
   directly). Report max abs difference per airport. STOP if any airport
   exceeds tolerance — this re-confirms the committed session-55 files are the
   ones being read.

## Internal-consistency signal to report (mirror F99/F101's)

The `2025-26` fold's `B` variant is the refit frozen 5-feature baseline.
Report its raw-GFS and persistence MAE and row counts against F94/F96/F99/
F100/F101's own figures per airport — a free confirmation the pipeline
reproduces the frozen recipe. Report only; not a gate.

## What to report

Exactly the two tables sessions 50/52/54 produced:

- A full grid: 5 airports × 3 folds × 4 variants (60 rows) —
  `data/processed/session56_e4_experiment_grid.csv`.
- A summary: fold-averaged-per-airport, airport-averaged-per-fold, and
  grand-overall levels (36 rows) —
  `data/processed/session56_e4_experiment_summary.csv`.

In the printed output, lead with the grand-overall table (mean MAE across all
15 airport-folds per variant, delta vs B, skill vs B) and the fold-averaged
per-airport table (skill vs B for B+R, B+Rv, B+v at each airport), the same
two tables F99/F100/F101 led with. State plainly where E4's max grand-overall
skill sits relative to E1 (+2.0%), E2 (+4.1%), and E3 (+0.9%). Do NOT make
the family call — report the grid and stop.

## What this session must not do

Fit any model on, or read any row of, the reserved 2024-08-01..2025-07-31
confirmation year. Do any per-airport feature selection. Measure against
anything other than pure frozen B. Pull any new data — reuse session 55's
committed files only. Change any data-path logic in
`scripts/session55_radiation_pull.py` (the preamble is a print-text fix
only). Touch the E5 (precipitation) family. Modify `SPEC.md` or `RESULTS.md`.
Compute any pass/fail verdict or make the family adoption call. Commit
anything.

## End of session

1. Paste the real output (actual grid and summary numbers, and a one-line
   confirmation of the print-only cleanup), not a description of them.
2. Run the standard three-file consistency check (SPEC/STATUS/DECISIONS) and
   report anything that disagrees — do not fix silently.
3. Archive step: check whether anything in the live `DECISIONS.md` is now
   settled per the archive criterion; move it mechanically if so, otherwise
   report "none."
4. Record the experiment as a new DECISIONS finding (the next F-number), same
   shape as F99/F100/F101 — a reading, not a verdict — and note the print-only
   cleanup within it. Overwrite `STATUS.md` to reflect this session, ending
   with a **"Next planning session"** line naming session 57's job: the
   owner's E4 family verdict (recorded as the next D-number), then build and
   validate the E5 (precipitation) feature set — the LAST family — flagged as
   awkward for the same reason radiation was (a lead-dependent accumulation
   window needing resolution to a consistent feature) PLUS sparsity
   (precipitation is mostly zero), so its Step 0 must settle both the window
   handling and how the mostly-zero distribution is represented.

Script name: `scripts/session56_e4_experiment.py`. Full real output:
`notes/session-56-e4-experiment-output.txt`.
