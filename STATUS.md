# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 October 2026, after session 105._

---

## Session 105: two daily-maximum challengers (D99, F148)

Full output: `notes/session-105-output.txt`.

- **D99** recorded: F147 accepted, and both challengers fixed before any
  score.
- **The reproduction** passed: F147.6's daily-maximum scores (at 4
  decimals, by an owner ruling at a stop: no full-precision line had been
  recorded, F148.1), the day list and the raw GFS maximum, 0 mismatches.
- **Test 1 (build-choice scores, not results, SPEC 2.5).** A daily-maximum
  model of its own (challenger 1): headline 1.0642 against the curve's
  1.0338; worse at all six airports and all three folds. Not passed.
- **Test 2 (build-choice scores, not results).** The curve's read-off
  maximum plus a daily drift correction: headline 1.0306 against 1.0338
  (0.315 percent lower), lower at 2 of 6 airports and 2 of 3 folds. Not
  passed.
- **Incumbents:** the daily maximum stays the curve's read-off maximum
  (D98.10(g)). The hourly incumbent is unchanged: the curve (the baseline
  plus D97's correction).

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. No untouched held-out year remains
at any of the six development airports (D71.1). End goal: a private, live
tool for ten or more airports that corrects every GFS run into an hourly
curve plus the daily maximum (D82.2).

- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79; now archived,
  still binding).** Pre-registered, models frozen, all three scripts gated
  (F128, F129). **None has been run.** Per period, after it ends: build,
  fetch, score. The hold rule (D73.8) stands. Session 86's `--gate` cannot
  be re-run (D96.3); `--build` is unaffected.
- **Stage C.** Development tables for leads 0 to 24 (F138) and 25 to 48
  (F147); build-choice rules (D89), with the hourly metric over leads 3 to
  48 (D98.8) and the daily maximum's metric (D98.10). The curve is the
  baseline plus the bias-drift correction (D95.2, D97.8); the daily maximum
  is its read-off maximum (F148). The claim batch (D82.7: EDDM, KORD, CYYZ,
  ZGSZ, ZUCK, NZWN) is judged at stage C's lock.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **F148.9's readings**, for the owner to confirm. In brief: challenger 1
  runs high at five airports; challenger 2 removes most of the mean error
  but its gain is far under 1 percent; "from the first pull cycle" read as
  days whose first hour is on or after 2021-03-24T00:00; the training-day
  rule was moved into a function after the first run, and the re-run's days
  file is byte-equal.
- **Session 104's output file** holds no full `--score` log, so its
  full-precision daily-maximum headline was never recorded; F148.2 now
  records it.

---

## Carried items

- **SPEC 6 and RESULTS 7 (D99.12).** They get the daily maximum's outcome
  (F148) with the next session that edits them.
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

**Next planning session:** Review session 105. The owner commits and pushes (`git commit -F docs/commits/commit-105.txt`) and the planning chat syncs Project knowledge. Then plan session 106, the next stage C step.
