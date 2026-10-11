# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 October 2026, after session 104._

---

## Session 104: the f025 to f048 pull, the curve to 48 hours, the daily maximum (D98, F147)

Full output: `notes/session-104-output.txt`.

- **D98** recorded: F146 accepted, D97.1 closed (scripts hold recorded
  values as constants, checked by tests; D98.2), and every choice of this
  session, fixed before any score.
- **The f025 to f048 pull** is downloaded (`MLwx-pull-f025-048/`, 195
  files) and passed every check: 187,768 (cycle, hour) keys, check failed
  0, idx missing 0.
- **The development table for leads 25 to 48** is built (six new files in
  `MLwx-stagec/`) and gated at YSDU, RNO and KSFO at lead 26. The first gate
  stopped on one cell (YSDU 2021-03-24, pressure tendency, input before the
  pull window); the owner accepted it by a ruling at the stop (F147.3).
- **The curve's gates** reproduced F139, F146 and F109 (YSDU, RNO at lead
  26) exactly.
- **Scores (build choices, not results, SPEC 2.5).** Hourly headline at
  leads 3 to 48: raw GFS 1.5315, baseline 1.1161, curve 1.0892. Daily
  maximum headline: raw GFS 1.3622, baseline 1.0543, curve 1.0338.
- **Incumbents:** the curve (the baseline plus D97's correction) for the
  hourly curve; its read-off maximum for the daily maximum (D98.8,
  D98.10(g)). No build choice was made in session 104.

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
  The hold rule (D73.8) stands. Session 86's `--gate` cannot be re-run
  (D96.3); `--build` is unaffected.
- **Stage C.** Development tables for leads 0 to 24 (F138) and 25 to 48
  (F147); build-choice rules (D89), with the hourly metric over leads 3 to
  48 (D98.8) and the daily maximum's metric (D98.10). The curve is the
  baseline plus the bias-drift correction (D95.2, D97.8). The claim batch
  (D82.7: EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN) is judged at stage C's lock.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **F147.8's readings**, for the owner to confirm. In brief: at leads 25 to
  48 the correction does not help EGLC; the read-off daily maximum runs
  low at YSDU, RNO and KSFO (mean error +0.14 to +0.23 degrees C); each
  airport's daily maximum comes from one cycle hour; the first `--score`
  run stopped on a bug in the new script's cross-check, fixed, and the
  re-run's scores file is byte-equal.

---

## Carried items

- **GFS v17 (D93.5, D93.15).** A weekly scheduled task checks for the
  Service Change Notice and alerts the owner. The go-live date sets
  period A's length.
- **lightgbm (D93.3).** New scripts may import lightgbm directly, with no
  libomp shim. scikit-learn stays pinned.
- **Frozen scripts (D62.3(a), restated in D93.8)** are never edited.
- **Recorded values in scripts (D98.2).** Never found by searching
  DECISIONS text; held as constants and checked by a test.
- **Later work (D90.12).** A `src/` package only at stage G.
- **MOSMIX notes (D80.4, D81.6, F130.5, F132.5).** Matching rule is the
  owner's later decision; EGLC station position note.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 104. The owner commits and pushes (`git commit -F docs/commits/commit-104.txt`) and the planning chat syncs Project knowledge. Then plan session 105, the next stage C step (D98.13).
