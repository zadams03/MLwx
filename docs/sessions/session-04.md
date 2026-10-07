# Session 04 — join, build, and validate (test year stays sealed)

## What this session is

This is the first modelling session. It joins the two series, looks at the
bias in the training data, and builds the stage 1 correction model — then
judges it on a **practice ("validation") year taken from inside the training
period**. The real held-out test year is **not touched at all** this session.

Why the practice year: the sealed test year (2025-08-01 to 2026-07-31) may be
looked at only **once**, at the very end, or it stops being an honest test
(rule 2.4). So we rehearse the whole evaluation on a training-internal year
first. The single real-test look happens in a later session, once the method
is locked.

**A good result this session does NOT mean stage 1 has passed.** It means the
method is ready for the one real-test evaluation later. Say it that way.

## Scope

Do only what is listed here, then stop. Do **not** touch the test year. Do
**not** tune or try model variants (build the one agreed model). Do **not**
declare the frozen bar passed (that is the later sealed-test session).

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply throughout — this session leans hard on 2.1 (no leakage),
2.2 (drop-count-report), 2.4 (frozen bar).

---

## Preamble — two authorised edits

**P-1. SPEC 4.1 — name the target hour (authorised edit).** The owner has
chosen **12:00 UTC**, on principle, before seeing any model or performance.
Edit SPEC 4.1 to state the target is the temperature at **12:00 UTC**, and
record the reasoning: 12:00 UTC is during daylight (it captures the daytime
heating GFS tends to mis-handle), it is a stable, well-observed time, and it
avoids the fast-swinging dawn/dusk hours where the `:50`-vs-`:00` pairing would
matter most. This is the only SPEC edit this session.

**P-2. Correct F1 (append to DECISIONS).** Session 01's F1 concluded the
archive is "continuous from that start". F8 later found a 492-hour gap, so that
is wrong. Append a short correction (a new finding) noting F1's continuity
claim is superseded by F8 — the archive is not continuous. Do not alter F1
itself (append-only).

Also record these decisions (append to DECISIONS):
- **D18 — the validation approach.** Inner-training = 2021-03-24 to
  2024-07-31. Validation year = 2024-08-01 to 2025-07-31 (mirrors the real
  test's Aug–Jul shape). The real test year stays sealed until a later
  session. Anything fit for baselines or the model uses **inner-training
  only**.
- **D19 — the stage 1 feature set (minimal).** Features are the **forecast
  temperature** and the **season** (day-of-year, encoded as sin/cos so
  December and January sit next to each other). Hour-of-day is not a feature
  (the target hour is fixed). No recent-observation feature is included, to
  keep the "we are correcting the forecast" story clean; it may be revisited
  later if needed.

---

## Part A — join the two series at 12:00 UTC

- From each series keep only the **12:00 UTC** target hour.
- Pair by the D14 rule: the forecast valid at 12:00 UTC with the routine
  `:50` observation nearest that hour (in practice 11:50 UTC). If no report
  falls within 15 minutes, drop that day and count it (2.2).
- The result is one row per day: date, forecast temperature, observed
  temperature.
- The **target** the model learns is the residual **observed − forecast**
  (SPEC 4.2). The corrected forecast is later forecast + predicted residual.
- Report rows kept and rows dropped (with reasons) for each of:
  inner-training, validation year. Do **not** build or report anything for the
  test year — filter it out entirely at load time.

## Part B — look at the bias, inner-training only

On **inner-training data only**, show how the raw bias (observed − forecast)
behaves (this addresses Q11):
- its overall mean and spread;
- how it varies with the forecast temperature (e.g. binned averages) — is the
  cold tail really more biased?
- how it varies with season (by month or day-of-year band).
Keep this to inner-training. Do **not** look at the validation year's values
here (it is a stand-in for the sealed test — judge the model on it, don't
explore it), and never the test year.

## Part C — build the model and evaluate on the validation year

**Model:** a gradient-boosted tree (LightGBM), modest fixed settings, a fixed
random seed for reproducibility. Fit on **inner-training only**, predicting the
residual from the D19 features. Build the **one** agreed model — do not tune,
grid-search, or try variants this session.

**Evaluate all methods on the same validation-year days** (a fair, common set:
days that have a paired row and also the previous day's observation for
persistence — drop and count the rest). Report MAE (°C) for each:
- **Raw GFS** — the forecast itself.
- **Persistence** — the previous day's 12:00 observation (past only, 2.1d).
- **Climatology** — the day-of-year seasonal average, computed from
  **inner-training only** (2.1c).
- **Mean-bias reference** — the forecast plus GFS's average bias, that average
  taken from **inner-training only**. (This is the sanity check: if the ML
  barely beats this, the bias is just a constant offset and the model isn't
  earning its keep.)
- **ML-corrected** — forecast + predicted residual.

Then state plainly:
- does ML-corrected beat **raw GFS** on validation MAE, and by how much;
- does it beat **persistence**;
- does it beat the **mean-bias reference** (i.e. is it learning structure, not
  just a constant);
- a short look at what the model used (feature importances) as a sanity check.

Frame all of this as a **validation rehearsal**, not the frozen-bar result.

---

## What to report at the end

Paste **real output**, not descriptions:
- join row counts kept/dropped (inner-training and validation);
- the inner-training bias summary (Part B);
- the validation-year MAE table for all five methods;
- the plain yes/no on beating raw GFS, persistence, and the mean-bias
  reference, with margins;
- feature importances;
- the SPEC 4.1 before/after and the new DECISIONS entries.

## What NOT to do

- Do not touch, load, evaluate, or explore the test year (2025-08-01 onward).
- Do not tune the model or try variants — build the one agreed model.
- Do not declare the frozen bar (SPEC 5) passed — that is the later session.
- Do not fill missing data; drop and count (2.2).
- Do not use the validation year or test year to fit climatology, the
  mean-bias reference, any encoder, or the model (inner-training only).
- Do not edit SPEC beyond P-1. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: what this session did, and that the next session is the
   **single sealed-test evaluation**, to be run only if the owner judges the
   validation result good enough to lock the method.
2. Ensure DECISIONS carries the F1 correction, D18, D19, and the validation
   results as a finding. Note Q10 (the 492-hour gap falls in inner-training,
   dropped and counted) and Q11 (bias structure) addressed.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
