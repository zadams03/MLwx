# Session 27 — Reno join and validation rehearsal (test year sealed)

## What this session is

The first modelling session for Reno, mirroring session 22 for Dubbo. It joins
Reno's two series at its target hour, looks at Reno's bias, and runs the
**already-locked method** — judged on Reno's **validation year**. Reno's sealed
test year is **not touched**.

The method is locked. For Reno, **the location and the target hour change**
(20:00 UTC = local noon, D41/D42) — nothing else. No model, feature or setting
is re-chosen; this applies the recipe to Reno.

**What Reno tests — the terrain question.** Reno is the first genuinely
terrain-hard airport (valley against the Sierra Nevada front — foehn, downslope
warming, cold-air drainage). All four prior airports were places GFS handles
well. The question here is whether the correction delivers its **biggest** win
where the raw model is worst — the method's actual selling point — or whether
the three simple features (temperature, season) are **not enough** to capture
terrain-driven bias, which would be the airport that motivates richer features
(cloud, wind) later. **Both outcomes are informative.** Do not assume Reno is
hard: session 26 found its training-window range no wider than the flat
airports; whether GFS is actually worse at the 20:00 target is what this session
finds out.

**A good (or poor) result here does NOT mean Reno has passed or failed.** It is
the rehearsal; the sealed test is later.

## Scope

Do only what is listed here, then stop. Do **not** touch Reno's test year. Do
**not** tune or vary the method. Do **not** declare the frozen bar passed.

Before starting, read SPEC.md, STATUS.md, DECISIONS.md in full (archive only if
needed). Critical rules (SPEC 2) apply — 2.1, 2.2, 2.4. As earlier rehearsals
did, prove in code that the method matches the locked recipe (only Reno's
location and its 20:00 UTC target hour differ).

---

## Part A — join Reno's two series at 20:00 UTC

- From each Reno series keep only the **20:00 UTC** target hour (Reno's local
  noon, D42).
- Pair by D14: Reno reports at `:55`, so the 20:00 forecast pairs with the
  19:55 report — a **5-minute offset**, within tolerance. If no report falls
  within 15 minutes, drop and count (2.2).
- One row per day: date, forecast, observation, residual (observed − forecast).
- Split by D18: inner-training **2021-03-24 to 2024-07-31**, validation
  **2024-08-01 to 2025-07-31**. Filter the test year (2025-08-01 on) out at load.

**Reconcile the drops against session 26's gap map** (F74–F77): the 492-hour
gap costs its days in inner-training, plus the 3 observation-side days it found,
all training. State the expected inner-training and validation drops **before**
counting, then confirm the actual join matches. A count that will not reconcile
is a stop signal.

## Part B — look at Reno's bias, inner-training only

On **inner-training only**, show Reno's raw bias (observed − forecast):
- overall mean and spread — **is it larger than the flat airports' ~1.2–2.0
  mean |bias|?** This is the first real sign of whether Reno is genuinely hard.
- how it varies with forecast temperature (binned);
- how it varies with season — **look especially at winter**, when cold-air
  drainage and downslope (foehn) effects are strongest and the terrain
  hypothesis most expects a large, structured bias.

**Compare to the four prior airports:** EGLC warm-end (F13), CDG calendar (F28),
DSM both (F43), Dubbo one-season calendar (F62). Where does Reno's sit, and is
it **bigger**? A terrain-driven bias might be larger and less cleanly tied to
temperature or plain season than any so far — that would itself be the finding.

Keep this to inner-training; do not explore the validation year's values.

## Part C — run the locked method and evaluate on Reno's validation year

**Model:** the locked recipe — LightGBM, `objective=regression_l1`, 300 trees,
lr 0.05, 15 leaves, min 40 samples/leaf, seed 42, deterministic; features the
D19 set (forecast temperature + season sin/cos). Fit on Reno **inner-training
only**, predicting the residual. Nothing tuned. Confirm two runs byte-identical.

**Evaluate all methods on the same Reno validation-year days** (common set: a
paired row plus the previous day's observation for persistence — drop and count
the rest). Report MAE (°C):
- Raw GFS
- Persistence (past only, 2.1d)
- Climatology (Reno inner-training only, 2.1c)
- Mean-bias reference (Reno inner-training mean bias only)
- ML-corrected

Then state plainly:
- does ML-corrected beat raw GFS on Reno's validation MAE, and by how much;
- does it beat persistence;
- **does it beat the mean-bias reference, and by how much — the key number for
  Reno.** Beating it well means the model learned **terrain-dependent
  structure**, not just a fixed altitude/valley offset. Barely beating it means
  the mountain's bias is mostly a constant the simple features can't improve on
  — a genuine, honest finding that would point toward richer features.
- the per-season breakdown (is the win concentrated in winter, as the terrain
  hypothesis predicts?);
- feature importances (does the model lean on temperature, season, or split
  differently here?).

**Compare to the four prior rehearsals:** EGLC 1.165 (~6%), CDG 1.377 (~3.5%),
DSM 1.466 (~16%), Dubbo 1.283 (~8%). Is Reno's raw GFS error **larger** (the
terrain showing up), and is the correction's win **bigger or smaller**? Frame as
"does the correction shine where GFS struggles?", reported straight — a big win,
a modest win, or "the simple features aren't enough here" are all legitimate,
informative outcomes.

Frame all of this as a **validation rehearsal**, not the frozen-bar result.

---

## What to report at the end

Paste **real output**:
- confirmation the method matches the lock (only Reno's location + 20:00 hour
  differ);
- join counts kept/dropped per period, reconciled against session 26's gap map;
- Reno's inner-training bias summary — its size vs the flat airports, its
  winter behaviour, compared to the four prior shapes;
- the Reno validation-year MAE table for all five methods;
- the plain yes/no on beating raw GFS, persistence, and (the key one) the
  mean-bias reference, with margins;
- the per-season breakdown and feature importances;
- an explicit Reno-vs-others comparison: is raw GFS worse here, is the win
  bigger, did the simple features suffice;
- confirmation Reno's test year was not touched.

## What NOT to do

- Do not touch, load, evaluate, or explore Reno's test year (2025-08-01 on).
- Do not tune or vary the model — apply the locked recipe.
- Do not declare the frozen bar (section 5) passed — that is the later session.
- Do not fill missing data; drop and count (2.2).
- Do not use the validation or test year to fit anything (inner-training only
  for the model, climatology, and the mean-bias figure).
- Do not edit SPEC. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: the Reno rehearsal result (and whether it looks
   terrain-hard or not), and that the next session is Reno's method-lock-and-
   sealed-test (the D39-equivalent for Reno), following the same two-session
   split. If the rehearsal shows the simple features clearly fail at Reno, note
   that as a candidate finding for the owner to weigh (it may motivate richer
   features), but still proceed to lock/test — the bar is judged as-is.
2. Append the Reno rehearsal result to DECISIONS as a finding (the numbers, the
   comparison to the four prior airports, the bias shape, the terrain read).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
