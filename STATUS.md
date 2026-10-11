# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 October 2026, after session 107._

---

## Session 107: stage C's look on the six claim airports, run once (D101, F150)

Full output: `notes/session-107-output.txt`.

- **D101** recorded: F149 accepted with three rulings (the flagless refusal
  accepted; the elevation constants stay as built; a bar half with no rows
  would count as not passing).
- **The look was run once** (`--look --confirm-look 107`, unchanged), after
  the pre-look checks held (script and twelve table hashes equal to F149's).
- **Result (F150), not yet reviewed:**
  - Hourly curve: passes at 6 of 6 new airports in both held-out years;
    smallest margin +8.216 % (+0.1093 degrees C), KORD, look B, against raw
    GFS.
  - Daily maximum: passes at 6 of 6 new airports in both held-out years;
    smallest margin +2.589 % (+0.0297 degrees C), KORD, look B, against raw
    GFS.
  - D100.7's expectation was met. No half had no rows.
- SPEC 9 and RESULTS 7 are not yet updated with the result (D101.5).

---

## Where the project is right now

Three proven methods for correcting GFS's local bias at an airport (SPEC
5.0, 7.5, 8.7; RESULTS.md). F109 stands. No untouched held-out year remains
at any of the six development airports (D71.1). End goal: a private, live
tool for ten or more airports that corrects every GFS run into an hourly
curve plus the daily maximum (D82.2).

- **Stage A:** done.
- **Stage B: the 2026-27 GFS forward test (D73, D77.6, D79; archived,
  still binding).** Pre-registered, models frozen, all three scripts gated
  (F128, F129). **None has been run.** Per period, after it ends: build,
  fetch, score. The hold rule (D73.8) stands. Session 86's `--gate` cannot
  be re-run (D96.3); `--build` is unaffected.
- **Stage C: locked (D100, SPEC 9); its look has been run (F150).** The
  curve is the baseline plus the bias-drift correction; the daily maximum is
  its read-off maximum. Both outputs pass at 6 of 6 claim airports in both
  looks. The look is not run again (D101.2). The result is folded into SPEC
  9 and RESULTS 7 after the owner's review.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **F150's readings**, for the owner: (1) both narrowest margins are at
  KORD, look B, against raw GFS (descriptive figures in F150.6); (2) the
  persistence subsets were slightly smaller than the common sets (0 to 235
  rows, 0 to 3 days); (3) the look also ran the tracker self-check inside
  itself, as built. The output file also records, as descriptive only, that
  the curve's MAE was above the baseline's (no drift correction) in 6 of 12
  hourly and 5 of 12 daily airport-look cells.

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

**Next planning session:** Review session 107. The owner commits and pushes (`git commit -F docs/commits/commit-107.txt`) and the planning chat syncs Project knowledge. Then plan session 108: the owner's ruling on F150 and folding stage C's result into SPEC 9 and RESULTS 7.
