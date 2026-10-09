# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 9 October 2026, after session 102._

---

## Session 102: the gate fixed and passed (D96, F145)

Full output: `notes/session-102-output.txt`.

- **D96** recorded. **Session 91's `--gate`** now checks the training set
  against a fixed F122.3 value (`TRAINING_SET_SHA256`); a test checks that
  value against the record. The plans for hours 0-24 and 25-48 are unchanged.
- **The workflow** has its own Release notes text for `25-48` (D96.4). Not
  run; YAML and GitHub expressions untested.
- **Tests:** 3 added (record lookups for sessions 91 and 87); 24 in all.
- **D95.7's test chunk and gate:** hours 21-48, three dates, 3,360 of 3,360
  messages ok. **GATE PASSED**, 18 of 18 station-days, exact equality. The
  f025 to f048 pull is ready to run.
- **D96.3:** session 86's `--gate` can no longer be re-run (it reads
  DECISIONS.md only); its `--build` mode, which stage B uses, is unaffected.

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
- **Stage C.** Design (D82), development table (D88, F138), build-choice
  rules (D89), the baseline scored (F139); the structure question closed,
  the baseline stays (D94, F143, D95.2). The f025 to f048 pull passed its
  local gate (F145). Next, per D96.5: the owner runs it, then bias drift
  (session 103), then leads 25 to 48 and the daily maximum (session 104,
  its metric fixed first, D89.8). The claim batch (D82.7: EDDM, KORD, CYYZ,
  ZGSZ, ZUCK, NZWN) is judged at stage C's lock.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **Other scripts that find entries in DECISIONS.md by text (F145.6).**
  `session92_verify_chunk.py` (`--gate`, local only) and
  `session95_check_release.py` read F122 and F133 to F136 values from
  DECISIONS.md, so they fail or may fail since the archive move. Not fixed.
  Whether `session95_check_release.py` still runs is unchecked.
- **F145.6's other readings**, for the owner to confirm.

---

## Carried items

- **GFS v17 (D93.5, D93.15).** A weekly scheduled task checks for the
  Service Change Notice and alerts the owner. The go-live date sets
  period A's length.
- **lightgbm (D93.3).** New scripts may import lightgbm directly, with no
  libomp shim. scikit-learn stays pinned.
- **Frozen scripts (D62.3(a), restated in D93.8)** are never edited.
- **Later work (D90.12).** A `src/` package only at stage G.
- **MOSMIX notes (D80.4, D81.6, F130.5, F132.5).** Matching rule is the
  owner's later decision; EGLC station position note.
- **Laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 102 (the gate passed). The owner commits and pushes (`git commit -F docs/commits/commit-102.txt`), the planning chat syncs Project knowledge, and the owner runs the workflow with `hours` = `25-48` for 2022-01 alone, then 2021-03..2026-07 once that month's verify step has passed. Then plan session 103, bias drift (D96.5).
