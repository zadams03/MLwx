# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 9 October 2026, after session 100._

---

## Session 100: the curve's model structure, A and B (D94, F143)

D94 fixed the rules for D82.5's two model-structure alternatives before
any score. Session 100 checked the baseline, scored both alternatives
against it by cross-validation, and applied D94.6. These are build-choice
scores, never results (SPEC 2.5). Full output:
`notes/session-100-output.txt`.

- **Gate.** The baseline refit reproduced F139 exactly: 3,168 of 3,168
  cells, the headline and the six airport counts.
- **Scores (headline MAE, degrees C).** Baseline 1.0498; A (one model
  per lead, cycle hour as an input) 1.0480; B (one model per airport,
  lead and cycle hour as inputs) 1.0908.
- **D89.6.** A against the baseline: not passed (headline 0.17 percent
  lower, under the 1 percent bar; 4 of 6 airports; 1 of 3 folds). B
  against the baseline: not passed (worse at 5 of 6 airports and in all
  3 folds).
- **Chosen structure (D94.6): the baseline stays.** One model per
  airport, cycle hour and lead (D88.4). This is a build choice, not a
  result.
- **Wording fixes (F142.6)** made in PROJECT-INSTRUCTIONS.md, the
  DECISIONS.md header and the archive header.

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. No untouched held-out year remains
at any of the six development airports (D71.1). End goal: a private, live
tool for ten or more airports that corrects every GFS run into an hourly
curve plus the daily maximum (D82.2).

- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79).**
  Pre-registered, models frozen, all three scripts gated (F128, F129).
  **None has been run.** Per period, after it ends: build, fetch, score.
  The hold rule (D73.8) stands.
- **Stage C.** Design (D82), development table (D88, F138), build-choice
  rules (D89), the baseline scored (F139), and D82.5's model-structure
  comparisons done (D94, F143): the baseline stays. Still open: D94.5's
  follow-up (larger settings for pooled models, the owner's decision),
  the daily maximum (its metric fixed first, D89.8), bias drift
  (D81.10(b)), and the claim design at stage C's lock.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **F143.7's readings, for the owner to confirm.** In brief: the gate
  checks this script's own fold loop (built on session 97's functions);
  the scores file's `method` column repeats the model name; the
  descriptive A-against-B line prints "PASS"; run times in the meta were
  passed by hand.
- **D94.5's follow-up.** B did not beat the baseline. Whether a later
  session tests larger settings for pooled models is the owner's
  decision; any such test is its own build choice, in its own entry.
- **RESULTS.md section 7's roadmap paragraph is out of date** (D93.4).
  D93.4 ties its fix to the session that closes D82.5's model-structure
  comparisons; whether that is now, or after D94.5's follow-up, is the
  owner's call.

---

## Carried items

- **GFS v17 (D93.5, D93.15).** A weekly scheduled task checks for the
  Service Change Notice and alerts the owner. The go-live date sets
  period A's length.
- **lightgbm (D93.3).** New scripts may import lightgbm directly, with no
  libomp shim. scikit-learn stays pinned.
- **Frozen scripts (D62.3(a), restated in D93.8)** are never edited.
- **Later work (D90.12).** A `tests/` folder after stage C's first D82.5
  comparison (now done); a `src/` package only at stage G.
- **MOSMIX notes (D80.4, D81.6, F130.5, F132.5).** Matching rule is the
  owner's later decision; EGLC station position note.
- **Bias drift (D78.2, D81.10(b)).** A candidate build choice for stage C;
  nothing decided.
- **Workflow wording (D85.1)** and **laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 100. If it passed, the owner commits and pushes (`git commit -F docs/commits/commit-100.txt`) and the planning chat syncs Project knowledge. Then plan the next stage C step: the owner decides D94.5's follow-up (B did not pass); then the daily maximum (its metric fixed in its own entry first, D89.8) and the `tests/` folder (D90.12).
