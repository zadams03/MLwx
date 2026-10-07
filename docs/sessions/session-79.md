# Session 79 — KSFO: record the owner's verdict and fold KSFO into SPEC and RESULTS

Session 78 ran KSFO's two pre-registered looks once. Both passed (F119).
The owner has reviewed F119 and accepts it as a PASS. This session:

1. runs integrity checks (no data read, no model);
2. appends the owner's verdict, **D71**, using the exact text below;
3. folds KSFO into SPEC.md, and fixes the carried SPEC wording items
   (B1–B5, C1–C3 from `notes/session-77-review.txt`);
4. folds KSFO into RESULTS.md;
5. fixes CLAUDE.md item E1 (commit messages);
6. records what changed as **F120**, archives the settled entries, and
   overwrites STATUS.md.

**This is a documentation-only session.** No code is written or run
against data, no model is fit, and nothing is scored.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No data, no models, no scores.** Do not open, load or parse any file
  under `data/`. The only exception is Step 0's SHA-256 check, which reads
  bytes only. Do not run any project script. Every number you write must
  come from DECISIONS.md (F118, F119, D70, D71) or from SPEC.md as it
  stands. Compute nothing new, except the one arithmetic check in Step 1,
  which uses only recorded numbers.
- **Change no verdict and no figure** for EGLC, LFPG, DSM, YSDU or RNO.
  F16, F30, F47, F64, F82, F94 and F109 stand, and so do their tables.
- KSFO's margins are **not** added to F109's five-airport table, and not
  added to its airport-averaged secondary read (+6.02%). KSFO gets its own
  table.
- Edit only: DECISIONS.md (append D71 and F120, then the archive move),
  DECISIONS-archive.md (the archive move only), SPEC.md, RESULTS.md,
  CLAUDE.md (item E1 only) and STATUS.md. Do not edit README.md, any
  script, or anything under `data/`. Do not edit PROJECT-INSTRUCTIONS.md.
- **Do not change any stage status in SPEC 6** (stage 2 stays "IN
  PROGRESS"; stages 3–6 stay as they are). That is for the roadmap
  planning session.
- Plain writing, as CLAUDE.md asks: short sentences, simple words.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-79.md`. If anything else shows, **stop and report**.
2. Report the SHA-256 of each file below and compare it with F119.4. Any
   mismatch: **stop and report**.
   - `data/processed/session78_ksfo_looks_grid.csv`:
     `48c9ceb740146cd1b9ea6d4b3d4da4c719dd4b4852043725c56f506717fb166c`
   - `data/processed/session78_ksfo_looks_predictions.csv`:
     `b4b46adc266ecb5475f253e5b20d02c6505d02af2bd578426095d6ef7f8ad78e`
3. Read, in DECISIONS.md: D66, D67, D69, D70, F118 and F119. Read
   `notes/session-77-review.txt`, section 4 (items B1–B5, C1–C4, E1).

---

## Step 1 — append D71 (exact text)

First check this arithmetic, using only the recorded values below, and
report the result to 4 dp. It must round to −0.4172:

```
(1587 × 0.1846862003780719 − 1223 × 0.36381439084219136) / 364
```

(Training means from F119.3; counts from D70.3. Look B's training is look
A's training plus look A's 364 test rows.) If it does not match, **stop
and report**.

Then append the following to DECISIONS.md, **verbatim**, after F119:

```
## 2026-09-27 — Session 79 decision: the owner's verdict on F119 (KSFO)

**D71. Owner decision, planning chat (after session 78): F119 is accepted
as a PASS. KSFO passes the frozen bar (SPEC 5.3) under the unchanged
`B+D,L,R,T` recipe (SPEC 8), on both of its pre-registered looks.** Written
at the start of session 79, before any SPEC or RESULTS edit. No data was
read and no model was fit to make it.

- **D71.1 Verdict.** PASS, as pre-registered ("pass in both years",
  D70.8). Both looks are spent and will not be repeated (F119.5). With
  KSFO's two held-out years (2024-08-01..2026-07-31) now used, no
  untouched held-out year remains at any of the six airports.
- **D71.2 Headline.** The number to lead with is look A's margin over raw
  GFS (GRIB): 1.2576 vs 1.4263 °C, +11.83% (F119.3). It is the smallest of
  the four bar margins. Look B's +20.16% over raw GFS is always quoted
  with D71.3.
- **D71.3 Look B's raw-GFS year.** Look B's raw GFS (GRIB) MAE, 1.7321 °C,
  is well above look A's (1.4263) and both rehearsal folds' (1.4423 and
  1.3061, F118.5). In look B, persistence (1.7172) edges raw GFS, so
  persistence is the binding half of the bar there: margin 0.3342 °C
  (+19.46%), against 0.3491 °C (+20.16%) over raw GFS (F119.3).
- **D71.4 KSFO's bias is not stable from year to year.** The mean-bias
  reference is worse than raw GFS (GRIB) in both looks (A 1.5000 vs
  1.4263; B 1.7747 vs 1.7321; F119.3). In rehearsal it beat raw GFS on
  both folds (1.3833 vs 1.4423; 1.2500 vs 1.3061; F118.5). The two
  training means in F119.3 (look A +0.3638 °C over 1,223 rows; look B
  +0.1847 °C over 1,587 rows; D70.3) imply a 2024-25 mean(obs − raw GFS)
  of about −0.42 °C, against about +0.36 °C before it. This is arithmetic
  on recorded values, not a new score. `B+D,L,R,T` still beat raw GFS in
  both looks. This is read as insight only: nothing is selected, tuned or
  changed on it.
- **D71.5 Framing (D70.9), carried by every write-up.** KSFO's result is
  for the recipe at a sea-mixed grid point (37.5% sea weight, F117.3). It
  is not directly comparable with the five earlier airports, whose
  reproduction gates passed. KSFO's gate is recorded as failed, explained
  by a difference between the sources (D69). Look B's training includes
  2024-25, by design (D70.3). KSFO's margins are not added to F109's
  five-airport table or to its airport-averaged secondary read (+6.02%).
- **D71.6 Number of looks (SPEC wording).** The five earlier airports each
  had one look per method. KSFO had two, pre-registered, each judged
  separately (D67.3, D70.3, D70.4). SPEC now states the general rule: a
  new airport's number of looks, their windows, and how their verdicts
  combine are fixed in writing in its lock, before any of its held-out
  values are read. When an airport has more than one look, it passes only
  if every look passes; anything else is recorded as a split or a fail
  (as D70.4 did for KSFO). This records existing practice. It changes no
  earlier result.
- **D71.7 Q30 order (D66.1).** The further-airport step is done (KSFO).
  Next is the dedicated roadmap planning session. Pooling and the 2026-27
  forward test stay deferred (D66.2, D67.8, D69.6).
- **D71.8 GFS v17 (planning-chat research, 2026-09-27, not checked by this
  session).** The NWS notice list still shows no GFS v17 Service Change
  Notice. The latest SCN is still SCN26-87 (22 Sep 2026).
- **D71.9 Session 79 plan.** Record D71; fold KSFO into SPEC and RESULTS;
  fix the session-77 review items B1–B5, C1–C3 and E1; record the edits
  as F120; archive D67, D69, D70 and F115–F119.
```

---

## Step 2 — SPEC.md edits

Draft the wording yourself, following the requirements below. Keep
existing text wherever it is still true. Every KSFO figure must match
F119.3 exactly (4 dp as F119 gives them).

**A. KSFO's result (the fold-in).**
1. **SPEC 1, KSFO bullet.** Stage 2, **passes the selected-features
   method** on both of its pre-registered looks (DECISIONS F119, D71) —
   see section 8. Keep "the project's first coastal airport" and the gate
   sentence. Add a short pointer to the D71.5 framing.
2. **SPEC 3.4 airport table, SFO's stage cell.** Change "2 — locked, not
   yet tested" to "2 — passed (selected-features method)". (This also
   settles review item C4.)
3. **SPEC 6, KSFO bullet.** Heading becomes "— passed (selected-features
   method)". Replace "Its two looks run once, in session 78" with the
   result: both looks pass (F119), the owner's verdict (D71), and the
   headline look-A margin over raw GFS. Keep the rest.
4. **SPEC 8.5.** After the five-airport paragraphs, add a separate block
   headed **KSFO (added later; DECISIONS F119, D71)**. Include a two-row
   table (look A 2024-25, look B 2025-26) with: n test, raw GFS (GRIB)
   MAE, persistence MAE, B MAE, B+D,L,R,T MAE, and % vs raw GFS, vs
   persistence and vs B (vs B: +7.08% and +5.62%, F119.3). Note the day
   basis (persistence on 363 of 364 days in look A, 365 of 365 in look B).
   Say both looks pass, the overall reading is PASS as pre-registered, and
   the band read (D70.5) holds in both looks. Say plainly that these rows
   are not part of the five-airport table or its +6.02% average.
5. **SPEC 8.6.** Add a caveat **(f)** for KSFO carrying D71.2–D71.5 in
   brief: the headline is look A's +11.83%; look B's raw-GFS year was
   unusually poor and persistence bound there; KSFO's mean bias changed
   sign between years; the sea-mixed grid-point framing; look B's
   training includes 2024-25.

**B. Review items B1–B5 (one look vs two), per D71.6.** Rewrite each so it
is true for both designs: one look at each of the five earlier airports,
two at KSFO, and, for a future airport, whatever its lock fixes in
writing before any held-out value is read. State D71.6's combining rule
once, in the most natural place (SPEC 5.0 or 5.3): with more than one
look, the airport passes only if every look passes; anything else is
recorded as a split or a fail.
- B1: SPEC 1, paragraph 3 ("judged once on that airport's own test year").
- B2: SPEC 5.0 ("one look at its own sealed test year"; "judged once per
  airport").
- B3: SPEC 4.3 (the per-airport rehearsal "validation year"). Say that
  KSFO's rehearsal used the 2022-23 and 2023-24 folds, because 2024-25
  was one of its looks (D67.4).
- B4: SPEC 6, "Further airports" bullet ("... lock, test once").
- B5: SPEC 8.7 ("its own lock and single test").

**C. Review items C1–C3 (statements scoped to the five earlier
airports).** Make each one's scope explicit, so a reader does not apply
it to KSFO by mistake.
- C1: SPEC 7 intro ("passed at every airport") — scope it to section 7's
  five airports.
- C2: SPEC 7.2 (model terrain "negligible at four airports but 275 m at
  Reno") — scope it to section 7's five, and note KSFO's gap of 93.47 m
  (SPEC 3.4).
- C3: SPEC 5.2 (unadjusted-GRIB margins "cannot be measured now, because
  both held-out years are spent") — scope the reason to the five earlier
  airports, and add that at KSFO no unadjusted rung was registered (D70),
  so it was not measured there either.

**D. Also update** any other SPEC line that still says KSFO is "locked"
or "not yet tested", or that says no untouched held-out year remains "at
the five airports" where six is now true. List each such line in F120.

---

## Step 3 — RESULTS.md edits

1. **Intro paragraph.** Add "revised after session 79" to the revision
   line. Add one or two sentences: a sixth airport, KSFO, has since passed
   the selected-features method on two pre-registered looks, with the
   D71.5 framing, see section 6.5.
2. **New section 6.5, "A sixth airport: San Francisco (KSFO)".** Keep it
   short. Cover: why KSFO (first coastal airport, D67); the gate failure
   and the owner's decision (F116, F117, D69); the rehearsal and lock
   (F118, D70); the two-look design (D67.3); the result table (as SPEC
   8.5's KSFO block); the headline (D71.2); D71.3 and D71.4 stated
   plainly; the D71.5 framing. Cite every number.
3. **Section 6.4's closing sentence** ("every new airport still needs its
   own lock and single test") — make it consistent with D71.6.
4. **Section 7.** In the "no untouched year" bullet, add that KSFO's two
   held-out years are now also used (D71.1). Update the last bullet
   ("Parked directions") so it states the current position: the owner's
   order is D66.1; the further-airport step is done (KSFO, D71.7); the
   next step is a roadmap planning session; pooling and 2026-27 stay
   deferred (D66.2). Remove wording that is no longer true ("None of the
   three has begun", "not yet a decision").
5. **Footer.** Add the session 79 revision (DECISIONS F120).

---

## Step 4 — CLAUDE.md item E1

Replace the body of the "Commit discipline" section with exactly:

```
Claude Code **never** commits, adds, or pushes to version control. It
prepares all changes, then stops. It does not write a commit message:
after reviewing the session, the planning chat writes it to
`docs/commit-NN.txt`, and the owner commits by hand with
`git commit -F docs/commit-NN.txt`. Nothing enters the project's history
without a person looking first.
```

Change nothing else in CLAUDE.md.

---

## End-of-session steps (CLAUDE.md), then stop

1. **Append F120** to DECISIONS.md, after D71: "Documentation only. What
   changed in SPEC.md, RESULTS.md and CLAUDE.md in session 79". List every
   edit by section, as D70.10 did, and name which review item (B1–B5,
   C1–C3, E1) each one settles. Include Step 0's results and the Step 1
   arithmetic. End with a "What this did not do" list (no data read, no
   script run, no model, no score, no stage status changed, no earlier
   verdict or figure changed, KSFO not added to F109's table or average,
   nothing committed).
2. **Archive step.** Move D67, D69, D70, F115, F116, F117, F118 and F119
   (each with its dated heading) to DECISIONS-archive.md, mechanically and
   verbatim, per CLAUDE.md. D66, D71 and F120 stay live. If any of the
   eight fails the archive criterion (for example, STATUS's "Next" needs
   it word for word), leave it live and say why.
3. **Overwrite STATUS.md** as a current-only snapshot (prune, do not
   append):
   - Headline: three proven methods; F109 stands; KSFO, a sixth airport,
     passes the selected-features method on two pre-registered looks (F119,
     D71), with the headline number (D71.2) and the D71.5 framing.
   - No untouched held-out year remains at any of the six airports (D71.1).
   - Q30: KSFO step done (D71.7); next is the roadmap planning session.
     Q32 unchanged.
   - Carried items: GFS v17, updated to the 2026-09-27 check (D71.8).
     Roadmap planning inputs as before (P1–P3, Q30 (2026-27, pooling),
     Q32, SPEC 5.4, RESULTS §7 terrain descriptor, SPEC stages 4–6, GFS
     v17), plus KSFO's D71.4 bias finding. **Remove** the "SPEC wording
     left for the owner" item (settled by F120).
   - End with this **"Next planning session"** line: "Review session 79.
     Then hold the dedicated roadmap planning session (D66.1, D71.7), using
     the roadmap planning inputs listed above."
4. **Write `notes/session-79-output.txt`** containing, copied
   mechanically (cat / sed / git), not retyped:
   - Step 0's output and the Step 1 arithmetic;
   - D71 and F120, verbatim, from DECISIONS.md;
   - `git diff SPEC.md`, `git diff RESULTS.md`, `git diff CLAUDE.md`;
   - the new STATUS.md in full;
   - the list of entries moved to the archive, with a check that each
     moved entry appears in DECISIONS-archive.md byte for byte;
   - the consistency check (next item).
5. **Consistency check.** Re-read CLAUDE, SPEC, STATUS and DECISIONS.
   Report disagreements, duplicated headings, out-of-order entries and
   unresolved D/F/Q citations (in either file). Search SPEC and RESULTS
   for any remaining "not yet tested", "locked" (about KSFO), "single
   test", "test once" and "judged once", and report each hit and whether
   it is still true. Report only; do not fix.
6. **Do not write a commit message file, and do not commit.** Stop and
   wait for the owner's review.
