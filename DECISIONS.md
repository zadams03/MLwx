# DECISIONS.md — the project's memory of *why*

This is the live log. New entries are added at the bottom, and no entry is
ever edited or deleted. Entries outside the Live index move verbatim to
DECISIONS-archive.md (D93.8). Each entry is dated.

It records choices made, why they were made, open questions, and findings.

## Live index

<!-- live-index-start -->
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
- D102: F150 accepted, its framing, the GRIB cache, stage G next, and a smaller live log.
- F151: session 108's finding (stage C's result folded in, figures, README files).
<!-- live-index-end -->

Every entry not listed here is in DECISIONS-archive.md, unchanged and still
binding. Entry numbers never change, so every citation resolves in one of the
two files. This list changes only through an owner's DECISIONS entry; a
session adds its own new entries (D93.8).

---

## 2026-10-09: Session 99 decision: F141 accepted, the session order, and a workflow overhaul (owner, planning chat)

**D93. Owner decisions, planning chat (after session 98c): F141 accepted,
three carried items, GFS v17, the session order, and a workflow overhaul
that cuts the reading cost of each session.** Written at the start of
session 99, before any other edit. No 2026-27 value has been read or
scored.

- **D93.1 F141 accepted,** with all nine F141.7 readings.
- **D93.2 The invocation.** The claude.ai Project instructions and section
  4 of `docs/PROJECT-INSTRUCTIONS.md` both give D92.4's invocation, with
  `docs/sessions/session-NN.md` (planning-chat check, 2026-10-09).
- **D93.3 lightgbm.** From D90.9 and F140.7, new scripts may import
  lightgbm directly, with no libomp shim.
- **D93.4 RESULTS.md section 7.** Its roadmap paragraph is out of date
  (F140, F141). It is fixed once, in the session that closes D82.5's
  model-structure comparisons, so that it is edited with their outcome.
  Until then it stays an open item.
- **D93.5 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-09, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-91 (6 October 2026).
  With 30 days' notice the earliest go-live is about 8 November 2026. Also:
  SCN 26-47 (updated) now ends NAM MOS on 3 November 2026, not 14 October
  as D77.1 and F127's correction give. NAM MOS was already excluded
  (D77.1), so nothing changes.
- **D93.6 Session order (amends D90.3).** Session 99 is this workflow
  overhaul. The first of D82.5's alternatives against the baseline
  (D89.10) moves to session 100. Its open choices (which alternative
  first, the rule if both alternatives beat the baseline, the model
  settings, and how the cycle hour is encoded) are fixed in session 100's
  own entry, before any score. Nothing else in D89 changes.
- **D93.7 Why the archive step stopped working.** DECISIONS.md had grown
  to 343,813 bytes (about 4,100 lines), against 773 lines after D46, and
  the archive was last changed on 2026-09-29. The end-of-session archive
  step existed, but: (a) its criterion kept any entry still cited by
  STATUS or by a live entry, and each new entry cites recent ones, so
  recent entries never became movable; (b) its default was "when in
  doubt, keep live" (D46); (c) Claude Code applied it alone each session,
  often by repeating an earlier session's reasons, and the planning-chat
  review accepted "nothing moved" without checking the file's size; (d)
  finding entries copied full tables already held in the output files.
  The step checked a criterion but never its outcome. D93.8 to D93.10
  replace it with an explicit list and a size limit checked every
  session.
- **D93.8 The live file (replaces D46's criterion).** DECISIONS.md opens
  with a Live index: the entries in force for current work. The owner
  changes the index only through a DECISIONS entry; a session adds its own
  new entries to it. At the end of every session, every entry not in the
  index moves verbatim to DECISIONS-archive.md, by
  `scripts/archive_decisions.py`. Being cited elsewhere is not a reason to
  keep an entry live: a citation resolves by number in either file, and an
  archived entry is still binding. The index after session 99: D47, D73,
  D77, D79, D82, D88, D89, F139, D93 and F142. D62 is archived; its rule
  that frozen scripts are never edited (D62.3(a)) stands, restated here:
  `session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py` and `session62_reserved_confirm.py` are
  never edited.
- **D93.9 Size limit.** Every session reports the byte size of
  DECISIONS.md after its archive step. Above 80,000 bytes is a
  consistency finding that the next planning session must act on.
- **D93.10 Finding entries.** A finding is at most about 40 lines: what
  was done, the numbers a decision needs, readings for the owner, what was
  not done, and a pointer to the output file. Full tables, lists and logs
  stay in `notes/session-NN-output.txt`, which begins with a summary of at
  most 30 lines.
- **D93.11 Long sessions and their guardrails.** Sessions may be longer
  and cover more, so that fewer sessions pay the start-up reading. In
  return each prompt lists the files the session may create or edit,
  checked against `git status` before the end steps; Claude Code writes a
  checkpoint line after each step, stops rather than works around a failed
  check, and after any mid-session compaction re-reads CLAUDE.md, the
  prompt and its checkpoints before going on.
- **D93.12 Keeping context small.** Claude Code does not print large files
  or outputs into the conversation; scripts print short summaries and
  write full tables to files; the archive is never read in full, only one
  entry at a time by line range.
- **D93.13 The planning side** (`docs/PROJECT-INSTRUCTIONS.md`). The
  planning chat reads its guide and STATUS in full; SPEC, CLAUDE and
  DECISIONS by targeted search unless the session being planned edits
  them; DECISIONS-archive.md is uploaded to Project knowledge for search
  only; the GFS v17 check is the weekly task of D93.15; reviews start
  from the output file's summary and checkpoints.
  Related work is combined into fewer, fuller sessions, and the planning
  chat recommends a Claude Code model for each.
- **D93.14 Session 99's plan.** Record this entry; replace CLAUDE.md; edit
  `docs/PROJECT-INSTRUCTIONS.md`; add the Live index; move every entry
  outside it to the archive with a checked script; check that every
  citation still resolves; record F142. No model, data file or existing
  script is touched.
- **D93.15 Two planning-side automations.** (a) A weekly scheduled task
  (Mondays, 08:57 London time) searches for a GFS v17 Service Change
  Notice and alerts the owner only when it finds one. Planning chats no
  longer re-check v17; a D entry mentions v17 only when the task has
  found a notice. (b) After the owner commits and pushes a reviewed
  session, the planning chat copies the changed files into claude.ai
  Project knowledge itself, from the linked computer, without their
  contents entering the chat (`docs/PROJECT-INSTRUCTIONS.md` section 5).
  The owner no longer re-uploads by hand, except when the planning chat
  reports that a sync failed.
- **D93.16 What each session reads, and the invocation (replaces
  D92.4's).** Each session prompt begins with a Read first section that
  lists what Claude Code reads before the steps: files in full, SPEC
  sections, and DECISIONS entries by number, live or archived. STATUS.md
  and SPEC section 2 are always read. With no list, the default is
  STATUS.md, SPEC section 2 and the live DECISIONS.md in full. A step
  that needs something not read reads just that part and notes it in its
  checkpoint. CLAUDE.md is loaded automatically and is not read again. So
  the invocation is fixed: "Carry out the session defined in
  docs/sessions/session-NN.md: first read what its Read first section
  lists, then do its steps, staying strictly within its scope. Stop at
  the end-of-session steps and wait for my review. Do not commit
  anything." Each session starts in a fresh Claude Code conversation (a
  new terminal or `/clear`): carrying a finished session's context into
  the next costs more than the short start-up read and blurs the review
  boundary.

---

## 2026-10-12: Session 108 decision: F150 accepted, its framing, the GRIB cache, stage G next, and a smaller live log (owner, planning chat)

**D102. Owner decisions, planning chat (after session 107): F150 accepted
with its readings, how stage C's result is described, the GRIB cache's new
place, stage G brought forward, and a smaller Live index.** Written at the
start of session 108, before any other edit. No 2026-27 value has been read
or scored. Nothing in D100 or F150 changes, and nothing is refit or
re-scored.

- **D102.1 F150 accepted,** with its three F150.6 readings as written.
- **D102.2 How the result is described (descriptive, D100.8; not a new
  test).** The frozen curve passes at 6 of 6 new airports in both held-out
  years for both outputs, and almost all of the gain over raw GFS comes
  from the baseline. In session 107's output file, the curve's MAE was
  above the baseline's (no drift correction) in 6 of 12 hourly and 5 of 12
  daily airport-look cells. So the drift correction helps when GFS's bias
  shifts and is roughly neutral otherwise. The one clear exception is KORD
  look B, hourly: the baseline's mean error was -0.41 degrees C and the
  curve's -0.05, and the correction gave about a third of the gain over
  raw GFS (MAE: raw GFS 1.3307, baseline 1.2566, curve 1.2214).
- **D102.3 The GRIB cache has moved.** The gitignored cache
  `data/raw/grib/` (about 39 GB, 62,572 files, D47) was moved by the owner
  off the laptop to an external drive, at
  `/Volumes/MY PASSPORT/MLwx-grib-cache/`. No current or stage B script
  reads it. Only finished scripts from sessions 37 to 89 do, so those
  cannot be re-run without the drive. Its manifests stay committed. The
  README's size of "about 20 GB" is corrected.
- **D102.4 Stage G comes next (changes D72.3's order only).** After stage
  C, the next stage is G, live product version 1, on GFS only, built with
  the weather model as a setting (as stage C was) so that later models plug
  in without a rebuild. Its design, including how it handles GFS v17, is
  set in a planning conversation and recorded in its own DECISIONS entry
  before any build. Stages D, E, F and H keep their scope and follow it,
  in that order; stage F still covers every model's version changes.
  Reasons: stage C's method has passed its claim; a never-edited
  prediction log gives forward evidence from now on; the ECMWF archives
  are shallow (F123) and deepen while we wait; GFS v17's earliest go-live
  is about November 2026.
- **D102.5 Unchanged.** Stage B (D73, its hold rule and scripts); the
  rule that no 2026-27 value is scored before its test is pre-registered;
  D72.4's 2027-28 forward year as the place for the live product's claim.
  Stage G makes no claim until one is pre-registered.
- **D102.6 README and figures.** Session 108 brings README.md and
  data/README.md up to date with stage C's result and the order in
  D102.4, and draws two descriptive figures from session 107's committed
  files: per-airport MAE of raw GFS and the curve in each look, for both
  outputs; and MAE by lead per airport. Nothing is averaged across
  airports.
- **D102.7 A smaller live file.** To cut what each session reads, the
  Live index after session 108 is D93, D102 and F151. Archived (still
  binding, cited by number): D82, D88, D89 and D98 (stage C's design,
  restated in SPEC 9 where it matters), D100, D101 and F150 (folded into
  SPEC 9 and RESULTS 7). From now on the index holds only D93, the newest
  session's own entries, and any entry a running stage needs open; a
  session's Read first section names other entries by number.
- **D102.8 SPEC and RESULTS.** Session 108 updates SPEC 6 and 9 and
  RESULTS 7 with the text in its prompt.
- **D102.9 Plan.** Session 108: this entry; SPEC and RESULTS; the figures;
  the README files; a read-only list of which scripts open SPEC.md or
  DECISIONS.md (to show whether SPEC can be shortened safely later); F151.
  Next: stage G's design, in the next planning conversation.

---

## 2026-10-12: Session 108 finding: stage C's result folded in, two figures, README files, and which scripts read the record

**F151. D102 was recorded first. Stage C's result (F150) was folded into SPEC 6 and 9, RESULTS 7 and the README files, two descriptive figures were drawn from session 107's committed files, and a read-only list was made of which scripts open SPEC.md or DECISIONS. No model was refit or re-scored; no claim airport table, `MLwx-*` folder, `/Volumes/` path or 2026-27 value was read; no network. Full real output: `notes/session-108-output.txt`.**

- **F151.1 D102.** Recorded first, byte-equal to the prompt's block (61 lines, `diff` and `cmp`), 0 em-dashes.
- **F151.2 SPEC and RESULTS (D102.8).** SPEC: section 6's order sentence (a), stage C bullet (b), stage G bullet (c); section 9.5's result paragraph (d). RESULTS 7: stage C "done" (e), the roadmap bullet's result text (f), the footer line (g). Each old text found exactly once; nothing else changed in either file.
- **F151.3 README files (D102.6).** README.md: sections 1, 2 (retitled "Headline results", stage C subsection first, F109 content unchanged under its own heading, one caveats bullet), 4 (one paragraph), 5 (stage C done, G next, then D, E, F, H), 7 (GRIB cache, no drive path) and one clause in section 6's figures row. data/README.md: the `grib` line, `MLwx-pull-f025-048/`, the claim airports' tables. Numbers copied from F150, SPEC 9.5 and D102; nothing averaged across airports.
- **F151.4 Figures.** `scripts/session108_figures.py` (`dc42002b124024c43c1e5d1e35030d99f4a3c90acd1fafa842f6d376cc7e558c`), standard library only, three input SHA-256 values held as constants (F150.4, D98.2). `figures/stagec_headline.svg` (`14dc9372c605ab5123564efc4c08c6961ea4142a3cf1ff5b7928ad8713ee296d`) and `figures/stagec_mae_by_lead.svg` (`1721cd2164a86d36de72fbedc93dd7fc4b5a2ba111087d5ab04522fb08742ee3`). Gate 1: 24 of 24 raw GFS halves, 100 x (1 - curve / raw) at 2 decimals equals F150.2: PASS. Gate 2: pooling by-lead values over cycle hours and leads reproduces the hourly raw GFS half's n exactly and both MAEs within 1e-9, 12 of 12 airport-looks: PASS. Two runs into `mktemp -d` folders were byte-equal.
- **F151.5 Test.** One case added to `tests/test_stagec.py` (the script's three SHA-256 constants equal F150.4's): passes. Suite: 51 tests, all pass.
- **F151.6 Which scripts read the record (Step 5, read only).** SPEC.md is opened by path by 6 scripts (session86, session87_forward_competitors, session87_forward_score, session89, session91, archive_decisions) and reached by 2 more through imports (session96, session104_f025_048). 5 of these search its text, all for section 3.4's airport table (fixed start and end text and two column names); the archive tool only scans it for citation numbers. 3 of the 5 are frozen. Several scripts search DECISIONS text; those for F122 to F135 already cannot resolve in the live file (D96.3, D98.2).
- **F151.7 `data/raw/grib/`** (Step 0): absent (does not exist), as D102.3 expects.
- **F151.8 Readings for the owner.** (1) The figures script also hash-checks the days file, as the prompt's three-constant test requires, but reads no value from it. (2) README.md grew by about 2 KB; section 2 holds the result and the other sections are about the same length. (3) The README's section 6 figures row now names the new script, a clause the prompt did not list. (4) SPEC could be shortened later if section 3.4's table, its heading line and "Notes on the table:" stay as they are (F151.6).
- **F151.9 What was not done.** No SPEC or RESULTS edit beyond Step 3; no existing script, data file or figure edited; nothing committed and no commit message written.
