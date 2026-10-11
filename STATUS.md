# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 October 2026, after session 106._

---

## Session 106: stage C's lock, the claim tables and the look script (D100, F149)

Full output: `notes/session-106-output.txt`.

- **D100** recorded: F148 accepted, stage C locked, and its claim test
  pre-registered on the six claim airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK,
  NZWN), before any of their held-out data was read.
- **The claim tables** are built (twelve files in `MLwx-stagec/`) and
  checked: the builder reproduces F138's and F147's rows exactly; every
  rebuild is byte-equal. The training-row sanity check (raw GFS, before
  2024-08-01) found no gross value.
- **The look script** (`scripts/session106_claim_look.py`) passed its gate
  at the development airports: look A reproduces session 104's 2024-25 fold
  exactly (3,312 cells, 2,190 days). Its guard check passed. **The look has
  not been run.**
- **Expectation (D100.7), stated before any held-out value is seen:** both
  outputs (hourly curve and daily maximum) pass at all six airports in both
  looks.
- SPEC section 9 (stage C, at its lock) is written; SPEC 6 and RESULTS 7
  are updated.

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
- **Stage C: locked (D100, SPEC 9).** The curve is the baseline plus the
  bias-drift correction; the daily maximum is its read-off maximum. The
  claim tables are built and checked, and the look script is gated and not
  run (F149). The look, run once, is session 107's (D100.12).
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **F149.6's readings**, for the owner to confirm. In brief: (1) a
  deviation: `--look` was run once from the command line without its flag
  and refused before reading anything; (2) the claim elevation constants
  use the unrounded height difference (rounding it first would change ZGSZ
  and NZWN in the 4th decimal); (3) D100 does not say what happens if a bar
  half has no rows (the script treats it as not passing); the owner may
  want to rule before the look; (4) to (7) as written.

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

**Next planning session:** Review session 106. The owner commits and pushes (`git commit -F docs/commits/commit-106.txt`) and the planning chat syncs Project knowledge. Then plan session 107: stage C's look on the six claim airports, run once (D100.12).
