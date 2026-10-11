# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 October 2026, after session 103._

---

## Session 103: the bias-drift test (D97, F146)

Full output: `notes/session-103-output.txt`.

- **D97** recorded: F145 accepted, the f025 to f048 pull, the commit
  history, and every choice of the bias-drift test, fixed before any score.
- **The test passed (a build choice, not a result, SPEC 2.5).** The
  challenger is the baseline plus a decaying average of its own recent
  errors (w = 0.02, D97.4). D89.6: headline 1.0498 to 1.0190 (2.93 percent
  lower), lower at 6 of 6 airports and in 3 of 3 folds. So, under D97.8,
  the curve becomes the baseline plus this correction, identically at every
  airport, cycle hour and lead. EGLC's gain is tiny (about 0.000007
  degrees C); KSFO's is the largest (F146.7).
- **The baseline refit** reproduced F139 exactly, twice (cells 3,168 of
  3,168).
- **PROJECT-INSTRUCTIONS.md section 8** now says commit messages never
  include a Co-Authored-By or Claude-Session line (D97.3).

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
  rules (D89), the baseline scored (F139); the structure stays the
  baseline (D95.2); the bias-drift correction added to it (D97.8, F146).
  The f025 to f048 pull has run: its Release
  `stagec-grib-pull-f025-048` holds 195 files (three for each of 65
  months), not yet downloaded or checked together (D97.2). Next (D97.11):
  session 104. The claim batch (D82.7: EDDM, KORD, CYYZ, ZGSZ, ZUCK,
  NZWN) is judged at stage C's lock.
- **Commit history.** On 2026-10-09 the owner removed Co-Authored-By and
  Claude-Session lines from every commit message on `main` and
  force-pushed; commit IDs from session 73 on changed, file contents did
  not (D97.3).
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **Scripts that find entries in DECISIONS.md by text (D97.1).**
  `session92_verify_chunk.py` (`--gate`, local only) and
  `session95_check_release.py` read F122.3 and F133 to F136 from
  DECISIONS.md by text, and session 95's script is fixed to the 0-24
  Release. Neither is used by the workflow. Dealt with when session 104 is
  planned.
- **F146.7's readings**, for the owner to confirm.

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

**Next planning session:** Review session 103. The owner commits and pushes (`git commit -F docs/commits/commit-103.txt`) and the planning chat syncs Project knowledge. Then plan session 104 (D97.11): download and check the f025 to f048 pull (with D97.1's open item), extend the development table and the curve to leads 25 to 48 (with the bias-drift correction, which passed), fix the daily maximum's metric in its own entry (D89.8), and score it.
