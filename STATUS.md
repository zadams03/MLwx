# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 9 October 2026, after session 101._

---

## Session 101: tests, RESULTS section 7, and the f025 to f048 pull prepared (D95, F144)

Full output: `notes/session-101-output.txt`.

- **D95** recorded: the model-structure question is closed (the baseline
  stays), and the order of the next steps is set.
- **RESULTS.md section 7**'s roadmap bullet updated (D93.4 done).
- **`tests/`** added (D90.12, D95.8): offline `unittest` checks of the
  leakage guards, the archive tool and recorded figures (F139, F143.6,
  F122.4 at EGLC). Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  discover -s tests -v`.
- **The pull script's cycle floor (D95.5):** no cycle before 2021-03-22T12
  is planned or requested. The 0-24 plan is byte-for-byte unchanged. The
  25-48 plan: 7,826 cycles, 187,768 files, 1,877,680 messages.
- **The workflow's `hours` input (D95.6):** `0-24` (default, unchanged
  behaviour) or `25-48` (Release `stagec-grib-pull-f025-048`). Not run.
- **D95.7's gate was not run.** Session 91's `--gate` looks for F122.3's
  training-set SHA-256 in DECISIONS.md, but F122 is in the archive since
  session 99, so the gate stops with an error before any comparison. The
  fix needs a script edit this session did not allow; the owner chose to
  stop. **The f025 to f048 pull is not ready until the gate passes.**

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
  rules (D89), the baseline scored (F139); the structure question closed,
  the baseline stays (D94, F143, D95.2). The f025 to f048 pull is prepared
  (F144) but its local gate has not run (D95.7). Then, per D95.4: bias
  drift (session 102), then leads 25 to 48 and the daily maximum (its
  metric fixed first, D89.8). The claim batch (D82.7: EDDM, KORD, CYYZ,
  ZGSZ, ZUCK, NZWN) is judged at stage C's lock.
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **The gate's lookup (F144.6, reading 1).** How session 91's `--gate`
  should find F122.3's SHA-256 now that F122 is archived (for example,
  read both DECISIONS files, or check the file against a fixed value). Any
  script that finds an entry by text in DECISIONS.md may have the same
  problem; no other script was surveyed.
- **D95.4's order.** The owner's Actions run of 2022-01 at `25-48` waited on
  the gate. Whether session 102 fixes the gate and runs it before bias
  drift is the owner's call.
- **F144.6's other readings**, for the owner to confirm.

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

**Next planning session:** Review session 101. Step 6 (the local test chunk and D95.7's gate) did not run: session 91's `--gate` cannot find F122.3 in DECISIONS.md. If the rest passed, the owner commits and pushes (`git commit -F docs/commits/commit-101.txt`) and the planning chat syncs Project knowledge. Then decide how the gate finds F122.3 and plan a session that makes that fix and runs the test chunk through the gate. Only after it passes does the owner run the workflow with `hours` = `25-48` for month 2022-01 alone, then for 2021-03..2026-07 once that month's verify step has passed. Plan session 102: bias drift (D95.4), or the gate fix first, as the owner decides.
