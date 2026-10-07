# docs/session-59.md — record the E5 (precipitation) family verdict (D56), and run the STATUS housekeeping pass

You have already read `CLAUDE.md`, then `SPEC.md`, `STATUS.md`, and
`DECISIONS.md` in full. This prompt is self-contained; where it and a spec
file disagree, stop and flag it (do not guess).

Three tasks, all documentation only — **no model is fit, no data is
touched, no figure is computed** (every number below is copied from and
cited to F105). Stay strictly within this scope. Stop at the end-of-session
steps and wait for review. **Do not commit anything.**

The reserved 2024-08-01..2025-07-31 confirmation year (D51) is not read,
loaded, or touched in any way this session.

---

## Task 1 — append the E5 verdict, DECISIONS D56 (verbatim, DECISIONS.md only)

Append the block below to the true end of `DECISIONS.md`, **verbatim**,
under its own dated heading, exactly as session 57 appended D55. Do **not**
edit any existing entry. This is the owner's verdict from review of F105 —
a file append only: no code, no `SPEC.md` or `RESULTS.md` edit, no new
figure.

After appending, run `grep -n '^## ' DECISIONS.md` and confirm the new D56
heading is the last one and that no D/F number is duplicated.

Append exactly this, starting with the heading line:

```
## 2026-09-21 — Session 59 decision: the E5 (precipitation) family verdict, from the owner's review of F105

**D56. Verdict: E5's adopted contribution to the eventual combine-phase sweep baseline is
the single feature `precip_rate_mmh` (the `B+P` variant) — the mean since-forecast-start
precipitation rate F104 built. Nothing is parked. Unlike E1 (D52) and E2 (D53), there is
no separate raw physical variable to weigh: F104 established E5 carries effectively one
feature (the raw cumulative total `apcp_cumulative_mm` is a monotone transform of the
rate, the same feature to a tree), so there is nothing to hold back as a combine-phase
candidate.**

**Rationale, kept plain.** `precip_rate_mmh` adds +1.3% grand-overall skill over the
frozen 5-feature baseline B (F105) — a real, mostly-positive result, above E3 (+0.9%) and
below E4 (+1.9%), the second-weakest family in the sweep. It is adopted because the signal
is genuine, physically motivated, and lands where the programme cares most. RNO shows the
family's strongest and most fold-robust benefit by a wide margin (+3.7%, positive in every
fold: +2.9% / +4.8% / +3.4%), consistent with the Sierra Nevada front (D42) making
precipitation timing informative there. DSM, the diagnostic, shows a small but fold-robust
positive signal (+0.6%, positive in all three folds) — the first family since E1/E2 to add
anything at all at DSM, where E3 (F101) and E4 (F103) both left it flat or negative.

**Honest caveats, recorded not hidden.** The strength is mid-low. EGLC's and LFPG's
fold-averaged benefit is carried by the earlier/thinnest folds and reverses to
flat-or-negative in the most recent fold(s) — the fold-quality caution F96/D52–D55 already
established for the 2022-23 and 2025-26 folds, not a defect unique to precipitation. YSDU
is flat (-0.0%) with no consistent sign across folds — the family's weakest airport. A
known mild cross-airport inconsistency stands (F104/F105): the since-start accumulation
window is 24h at EGLC/LFPG/DSM and 26h at YSDU/RNO, so `precip_rate_mmh` is a mean over
spans of slightly different length at different airports — carried forward as a limitation
the combine phase should be aware of, not a reason to withhold adoption. The family stays
net-positive in the most recent 2025-26 fold (+0.8%), matching E4's shape rather than E3's
reversal.

**On-record observation for the combine phase (NOT a parked candidate).** Precipitation's
benefit is uneven and concentrated: strong and durable at RNO, small but consistent at
DSM, thin-fold-carried at EGLC/LFPG, flat at YSDU. The combine phase should expect
precipitation to pull its weight mainly at RNO and DSM, and should watch the EGLC/LFPG
recent-fold softness when the adopted features are swept together. Grid:
`data/processed/session58_e5_experiment_grid.csv`.

**This is provisional.** Like every family in the sweep, `precip_rate_mmh` is confirmed
only when the single final feature set is checked on the reserved year once, at the finish
line (D51) — not now.

**E5 is the last family — the feature-selection sweep is now complete.** All five families
have a verdict against the same frozen 5-feature baseline B. Adopted into the eventual
combine-phase sweep baseline: `lapse_rate_t2_t850` (D52), `dewpoint_depression_t2m_floored`
(D53), `pressure_tendency_3h_hpa` (D54), `dswrf_2h_wm2` (D55), and `precip_rate_mmh`
(D56). Parked combine-phase candidates (separate raw variables held back for the sweep, not
in the baseline): RNO's raw pressure-level temperatures (D52) and relative humidity (D53).
E3, E4 and E5 parked nothing.

**Measurement baseline note.** No family remains to measure against B — E5 closes the
sweep. Adopted features enter together only at the combine phase, not before. Cites F105.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`. Did not fit any
model or compute any new figure — every number above is copied from and cited to F105. Did
not touch the reserved 2024-08-01..2025-07-31 confirmation year.
```

---

## Task 2 — prune STATUS.md to a true current-only snapshot (housekeeping A)

`STATUS.md` has grown to an accumulating per-session log (2,900+ lines back
to ~session 35), which contradicts its own header and CLAUDE.md's definition
of it as a snapshot. Rewrite it as a genuine current-only snapshot. Its full
history is preserved in git and in `DECISIONS.md`, so pruning loses nothing.

**Base every fact in the new file on the current STATUS.md and DECISIONS.md —
do not invent, restate a figure from memory, or re-derive anything.** Keep
only:

1. The standard header (snapshot note, "history in git").
2. **Where the project is right now**, stated compactly:
   - The E1–E5 feature-selection sweep is **complete**: all five families
     have a verdict against the frozen 5-feature baseline B.
   - Adopted into the eventual combine-phase sweep baseline: `lapse_rate_
     t2_t850` (D52), `dewpoint_depression_t2m_floored` (D53), `pressure_
     tendency_3h_hpa` (D54), `dswrf_2h_wm2` (D55), `precip_rate_mmh` (D56).
   - Parked combine-phase candidates: RNO's raw pressure-level temperatures
     (D52), relative humidity (D53).
   - The measurement baseline B is unchanged; the reserved 2024-25 year
     (D51) is still untouched; the sealed-year GRIB verdict (F94) and every
     minimal-method verdict (F16/F30/F47/F64/F82) stand exactly as reported.
   - One short line noting STATUS was pruned to current-only this session and
     that pre-session history lives in git and DECISIONS.md.
3. The **"Next planning session" line** (see Task 2's Next line below).
4. **Live open questions only** — carry over the current STATUS.md's own
   live Q30 (remaining branches: a further airport; a second test year;
   stage 3 pooling) and Q32 wording as it stands; do not re-open anything
   already closed.

**Drop** every per-session historical write-up (the session-by-session
narrative sections). Do not summarise them into the new file — they are in
git and DECISIONS.md by number.

**The new "Next planning session" line must read (adjust the session number
only if the current STATUS uses a different next index):**

> **Next planning session: session 60 — design and open the combine phase:
> sweep the five adopted features (D52–D56) together on the three
> non-reserved `EXPERIMENT_FOLDS` (D51), with the two parked candidates (D52,
> D53) as sweep options, to choose a single final feature set; that one set
> is then confirmed on the reserved 2024-25 year (D51) exactly once, at the
> finish line. The E1–E5 sweep and the STATUS housekeeping are both done.**

---

## Task 3 — add the standing "current-only" rule (housekeeping B)

So STATUS never bloats again, add a plain standing rule in two files:

- **`CLAUDE.md`**, in the "End of every session" section (step 2, the STATUS
  overwrite): state that overwriting STATUS.md means **pruning it to a
  current-only snapshot** — present state, the immediate next action, and
  live open questions only — **never appending that session's write-up to an
  accumulating log.** Its history lives in git and DECISIONS.md.
- **`PROJECT-INSTRUCTIONS.md`**, in section 6 (STATUS is the handoff
  document): add the same rule in the planning-side voice — a fresh planning
  chat should inherit a lean current-only STATUS, so each session's STATUS
  overwrite prunes rather than accumulates.

Keep the wording plain and short. Do not restructure either file beyond
adding these rules.

---

## End-of-session steps

1. **Consistency check** (CLAUDE.md): re-read `SPEC.md`, `STATUS.md`,
   `DECISIONS.md`, `CLAUDE.md`, and `PROJECT-INSTRUCTIONS.md` and report
   anything that disagrees, any duplicated heading, and any log entry out of
   order — report only, do not fix silently. Confirm specifically that the
   pruned STATUS's stated adopted/parked feature lists match D52–D56 exactly.
2. **Archive step** (CLAUDE.md): move any DECISIONS.md entries that became
   settled this session to the archive, per the archive criterion. (D52–D56
   and F96–F105 remain live inputs to the now-opening combine phase, so
   expect nothing to qualify — if so, say so explicitly.)
3. Paste the full diff of every changed file so the prune can be reviewed
   line by line.
4. **Stop and wait for review. Commit nothing.**

## Scope guardrails — do NOT

- Do not fit any model, compute any MAE/skill/figure, or load any dataset —
  every number is copied from and cited to F105.
- Do not read, load, or touch the reserved 2024-08-01..2025-07-31 year (D51).
- Do not edit `SPEC.md` or `RESULTS.md`.
- Do not edit any existing DECISIONS.md entry — D56 is an append only.
- Do not summarise the dropped STATUS history into the new snapshot; it lives
  in git and DECISIONS.md.
- Do not re-open or re-word any closed open question; carry live Q30/Q32
  wording across unchanged.
