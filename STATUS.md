# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 9 October 2026, after session 99._

---

## Session 99: workflow overhaul (D93, F142)

D93 accepted F141 and set a new workflow. Session 99 recorded D93 and F142.
No model experiment was run and no build choice was made. Full output:
`notes/session-99-output.txt`.

- **Live index (D93.8).** DECISIONS.md now opens with a Live index: D47,
  D73, D77, D79, D82, D88, D89, F139, D93 and F142. Every other entry is in
  DECISIONS-archive.md, verbatim and still binding. 40 spans moved; all
  four checks of the move passed (F142.4).
- **Size limit (D93.9).** DECISIONS.md is 55,597 bytes after the archive
  step (it was 343,813). Above 80,000 bytes is a finding.
- **The archive script.** `scripts/archive_decisions.py` (new, SHA-256
  `25813993...11e8`) runs at the end of every session: `--apply --session
  NN`, then `--citations`. Every citation resolves (169 of 169).
- **CLAUDE.md** replaced: Read first sections (D93.16), guardrails
  (D93.11), small context (D93.12), finding length (D93.10).
  **PROJECT-INSTRUCTIONS.md** edited: read by need, Project-knowledge sync
  by the planning chat (D93.15), review from the output summary, session
  design (new section 11).
- **The invocation (D93.16)** is fixed: "Carry out the session defined in
  docs/sessions/session-NN.md: first read what its Read first section
  lists, then do its steps, staying strictly within its scope. Stop at the
  end-of-session steps and wait for my review. Do not commit anything."

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
  rules (D89), and the curve's baseline scored by cross-validation (F139,
  the incumbent, D89.7). Next: D82.5's model-structure alternatives against
  the baseline under D89.6, one at a time (D89.10). Session order: session
  100 runs the first (D93.6).
- **MOSMIX (D81.2 to D81.5).** No saver exists yet; days before it starts
  are lost, which is accepted.
- **Open item MMMX (D83.4).** Almost no usable observations under the
  15-minute rule; a later decision.

---

## Open questions (live)

- **Session 99's readings (F142.6), for the owner to confirm.** In brief:
  the new CLAUDE.md has no em-dashes; the archive's new section starts
  after two `---` lines; the D1 to D12 and F88 pointer spans moved; some
  older wording was left (the planning guide's "re-upload" lines, the
  archive header's D46 criterion, DECISIONS.md's "append-only" header);
  the first `--apply` call was blocked by the auto-mode permission check
  and run again after a backup.
- **RESULTS.md section 7's roadmap paragraph is out of date** (D93.4). It
  is fixed in the session that closes D82.5's model-structure comparisons.

---

## Carried items

- **GFS v17 (D93.5, D93.15).** A weekly scheduled task checks for the
  Service Change Notice and alerts the owner. Planning chats do not
  re-check. The go-live date sets period A's length.
- **lightgbm (D93.3).** New scripts may import lightgbm directly, with no
  libomp shim. scikit-learn stays pinned.
- **Frozen scripts (D62.3(a), restated in D93.8)** are never edited.
- **Later work (D90.12).** A `tests/` folder after stage C's first D82.5
  comparison; a `src/` package only at stage G.
- **MOSMIX notes (D80.4, D81.6, F130.5, F132.5).** Matching rule is the
  owner's later decision; EGLC station position note.
- **Bias drift (D78.2, D81.10(b)).** A candidate build choice for stage C;
  nothing decided.
- **Workflow wording (D85.1)** and **laptop sleep (D86.5)**: unchanged.

---

## Next

**Next planning session:** Review session 99. If it passed, the owner commits and pushes (`git commit -F docs/commits/commit-99.txt`) and the planning chat syncs Project knowledge (PROJECT-INSTRUCTIONS section 5: STATUS, DECISIONS, CLAUDE, PROJECT-INSTRUCTIONS, and DECISIONS-archive, which is new there). Then plan session 100: fix D93.6's four choices in its D entry, then run the first of D82.5's alternatives against the baseline under D89.6.
