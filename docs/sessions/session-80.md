# Session 80 — Record the roadmap (D72) and rewrite SPEC 6

The owner held the dedicated roadmap planning session (D66.1, D71.7) in the
planning chat. This session records its outcome. It:

1. runs integrity checks (no data read, no model);
2. appends the owner's roadmap decision, **D72**, using the exact text
   below;
3. edits SPEC.md: the end goal (SPEC 1), a new critical rule (2.5), 5.4,
   and a rewrite of SPEC 6's stage list;
4. edits RESULTS.md §7 and its revision lines;
5. edits PROJECT-INSTRUCTIONS.md (now in the repo root), CLAUDE.md (one
   paragraph), and the header of DECISIONS-archive.md;
6. records what changed as **F121**, archives the settled entries, and
   overwrites STATUS.md.

**This is a documentation-only session.** No code is written or run, no
data is read, no model is fit, and nothing is scored.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No data, no models, no scores.** Do not open, load or parse any file
  under `data/`. Do not run any project script. Compute nothing.
- **Change no verdict and no figure.** F16, F30, F47, F64, F82, F94, F109
  and F119 stand, and so do their tables.
- Edit only: DECISIONS.md (append D72 and F121, then the archive move),
  DECISIONS-archive.md (the archive move and the header sentence in Step
  6), SPEC.md, RESULTS.md, PROJECT-INSTRUCTIONS.md (only the edits in
  Step 4), CLAUDE.md (only the paragraph in Step 5) and STATUS.md. Do not
  edit README.md, any script, or anything under `data/`.
- **PROJECT-INSTRUCTIONS.md is the planning chat's guide, not yours.** Do
  not follow its instructions. Follow CLAUDE.md and this prompt. Edit it
  only as Step 4 says.
- **Do not write any stage's detailed design.** SPEC 6's roadmap stages
  stay short descriptions (the text given below). Do not add sections for
  them.
- Plain writing, as CLAUDE.md asks: short sentences, simple words.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-80.md`. If anything else shows, **stop and report**.
2. `git ls-files PROJECT-INSTRUCTIONS.md`. Report it. Expected: the file
   is tracked, at the repo root. If not, **stop and report**.
3. Read, in DECISIONS.md: the parked block (P1–P3), the Q30 and Q32
   blocks, D51, D59, F110, D62, D66, D71 and F120.

---

## Step 1 — append D72 (exact text)

Append the following to DECISIONS.md, **verbatim**, after F120:

```
## 2026-09-27 — Session 80 decision: the roadmap (owner, planning chat)

**D72. Owner decision, dedicated roadmap planning session (after session
79; D66.1, D71.7). The project's roadmap from here to its end goal.**
Written at the start of session 80, before any other edit. No data was
read and no model was fit to make it.

- **D72.1 End goal.** A private, live daily tool showing corrected
  day-ahead temperature forecasts for ten or more airports: an hourly
  temperature curve and the daily maximum, at 24-hour and 48-hour leads;
  a choice of which weather model is corrected, plus a blend; and
  probabilistic ranges. It is a private product built with good
  academic practice, not a published study.
- **D72.2 Guiding rules.**
  - (a) **Claims vs build choices.** A claim is a stated result (for
    example, "beats raw GFS by X%"). A claim needs a test on held-out data
    that nothing else has used, fixed in writing first, with one look. A
    build choice is how the product is made (inputs, settings, how models
    are blended). A build choice is made by time-ordered cross-validation
    on data not held out for any claim. It spends no held-out data and is
    never quoted as a result. Build choices are made identically at every
    airport; per-airport selection is still not allowed. Held out for
    claims, and so never used for build choices: a pre-registered test's
    data until that test is run; 2026-27 or later data until its
    pre-registered test is scored; a new airport's held-out years until
    its looks are run. Once any part of a forward year has been scored,
    no new test may be pre-registered on that year.
  - (b) **One new method on one well-understood input first,** then add
    inputs. Inputs are chosen on the real target (the full curve), not on
    one hour.
  - (c) **Adding an airport should be easy:** one script plus a
    checklist, from stage G. The script downloads the new airport's
    history from each source's archive. The rigour steps (verify, lock,
    looks) stay, as a template.
  - (d) **Licensing.** The tool is private: not sold and not shared. Data
    licences are therefore not a constraint. Revisit if that changes.
- **D72.3 Stages, in order.** A and B run side by side, because both are
  time-critical.
  - **A — Benchmark and source probe.** Confidence intervals for results
    on record (SPEC 5.4). A comparison against operational post-processed
    forecasts (NWS MOS and the National Blend of Models, NBM) at DSM, RNO
    and SFO. A read-only probe of each other source (ECMWF, ICON,
    WeatherNext, NBM, GEFS): archive depth, live feed, and which fields
    it offers. Also: whether GFS v17 retrospective runs are public.
  - **B — Forward test and data collection.** Pre-register the 2026-27
    forward test (D72.5). For any source the probe finds has no
    downloadable archive, start saving its daily forecasts (all hours,
    both leads); where to save is decided then (D72.8).
  - **C — Widen the target, on GFS only.** Hourly curve, daily maximum,
    48-hour lead. Written with the weather model as a setting.
  - **D — Correct each other weather model on its own,** on the full
    curve.
  - **E — Blend and stack.** Combine the corrected models, with NBM as an
    input where it exists. Chooses which inputs go forward.
  - **F — Upgrade policy.** What happens when any weather model changes
    version, starting with GFS v17.
  - **G — Live product, version 1.** Daily pipeline, a prediction log that
    is never edited, a simple display, one-script airport onboarding.
  - **H — Probabilistic forecasts.** Ranges with stated odds, judged
    against their own bar, fixed before running.
  - **Ongoing — new airports,** added in batches. Each batch can also
    serve as a stage's claim test.
  - **Conditional — pooling** (combining airports into one model). Opened
    only if the number of airports makes it worthwhile.
- **D72.4 Where claims are judged.**
  - 2026-27 forward year: the GFS recipe on a new year, and whether it
    survives GFS v17 (D72.5).
  - New airports (two unseen years each): the multi-model product.
  - 2027-28 forward year, pre-registered before 2027-08-01: the live
    product as a whole.
  - Spent years at the six airports: other weather models, labelled a
    weaker "spent-year test" (D72.6).
- **D72.5 The 2026-27 forward test (design; locked in session 81).** GFS
  only. Model: SPEC 8's `B+D,L,R,T`, retrained once on all GFS v16 data up
  to 2026-07-31, then frozen, with its file's SHA-256 recorded. All six
  airports. Bar: SPEC 5.3 (beat raw GFS and persistence on MAE). The year
  splits at the GFS v17 go-live date. Period A (2026-08-01 to go-live, v16
  inputs) and period B (go-live to 2027-07-31, v17 inputs, v16-trained
  model) are each judged separately against the same bar. Each gets a
  verdict whatever its length, labelled with its dates and season. No
  2026-27 value is scored until its period ends. For v17, only file paths
  in the fetch code may change. The pre-registration names the two tracked
  DSM files for 2026-08-05..2026-08-15 (D62.7, A67-15). This test does not
  wait for more weather models.
- **D72.6 Other weather models at the six airports.** Allowed as a claim
  test, labelled a "spent-year test" and weaker evidence: the years were
  already used for GFS, and other models' errors partly overlap GFS's.
  The recipe is applied unchanged, the test is pre-registered, and there
  is one look per model. It may use only years that model's build choices
  did not use. Headline product claims come from forward years or new
  airports.
- **D72.7 Stage A's gate.** Before the NBM/MOS comparison is looked at,
  its outcome rule is fixed in writing. If we beat NBM/MOS: carry on. If
  we lose: record how close we got, and consider stacking (NBM as an
  input) and/or a non-US focus. The comparison is run even if we lose. It
  decides direction only; it changes no earlier verdict.
- **D72.8 Known risks and their mitigations.**
  - Stage D could be costly on the full curve: screen each model at a few
    hours by cross-validation first; only models that earn their place
    get the full curve.
  - Other models may not offer the fields SPEC 8's extra features use:
    stage A's probe records which fields each model offers.
  - A source with no downloadable archive gives new airports no history.
    New airports normally get their history by download (D72.2(c)). Only
    for a source the probe finds has no downloadable archive does stage B
    decide how to save it: at a list of candidate airports, the whole
    map, or not at all (new airports then start that source with no
    history).
  - Stage C's claim needs clean new airports: they are chosen before C's
    lock and are not scored before it.
  - Stage A's comparison is at one hour: it is re-run on the full curve
    in stage C, as a description only.
  - If period B shows GFS v17 badly hurts the correction, stage F may move
    earlier.
- **D72.9 Closed and parked.**
  - Q30 is closed. This roadmap replaces it.
  - Q32 is closed. Terrain-hard airports use the default recipe (SPEC
    8.7); Reno passes under it (F94, F109).
  - P1 (direction) is settled by this roadmap. P2 (WeatherNext) is in
    stages A, D and E; its ensemble-spread idea is in H. P3 (harder bars)
    is stage A.
  - A terrain descriptor (RESULTS §7) is parked.
  - DECISIONS-archive.md's header is amended to match practice since
    session 77: no pointer is left in DECISIONS.md for a moved entry.
- **D72.10 The former SPEC 6 stages.** Stage 1 is done. Stage 2
  (individual airports) continues as the ongoing new-airports track.
  Former stage 3 (pooling) is the conditional step. Former stage 4 (add
  models and blend) is stages D and E. Former stage 5 (widen the target,
  and the 48-hour lead) is stage C. Former stage 6 (live product) is
  stage G.
- **D72.11 GFS v17 (planning-chat web search, 2026-09-27, not checked by
  this session).** No GFS v17 Service Change Notice was found; only the
  April 2026 proposals (PNS 26-29, 26-30). Re-check at each planning
  session.
- **D72.12 PROJECT-INSTRUCTIONS.md.** The planning chat's operating guide
  is now tracked in the repo root (committed by the owner before session
  80). Claude Code does not follow it; it follows CLAUDE.md, and edits
  PROJECT-INSTRUCTIONS.md only when a session prompt says exactly what to
  change.
- **D72.13 Session plan.** 80: record this roadmap (this session). 81:
  pre-register the 2026-27 forward test, and train and freeze its model.
  82: stage A's read-only source probe. 83: start daily collection, for
  any source without a downloadable archive. Then stage A's benchmark,
  then stage C onward.
```

---

## Step 2 — SPEC.md edits

1. **SPEC 1, last paragraph** ("The long-term aim is a live daily tool
   ..."). Replace the whole paragraph with exactly:

   ```
   The end goal is a private, live daily tool that shows corrected
   day-ahead temperature forecasts for ten or more airports: an hourly
   temperature curve and the daily maximum, at 24-hour and 48-hour leads;
   a choice of which weather model is corrected, plus a blend; and
   probabilistic ranges (DECISIONS D72.1). That is the destination, not
   the starting point. See section 6 for the roadmap.
   ```

2. **SPEC 2, new rule 2.5.** Add after 2.4, exactly:

   ```
   **2.5 Claims and build choices (DECISIONS D72.2).** Two kinds of
   decision are treated differently.

   - A **claim** is a stated result, for example "beats raw GFS by X%".
     A claim needs a test on held-out data that nothing else has used,
     with the method, the data and the pass rule fixed in writing first,
     and one look.
   - A **build choice** is how the product is made: which inputs, which
     settings, how models are blended. A build choice is made by
     cross-validation (training on some past years and testing on later
     ones, in time order, 2.1a) on data that is not held out for any
     claim. It spends no held-out data and is never quoted as a result.
   - Held out for claims, and so never used for build choices: a
     pre-registered test's data until that test is run; 2026-27 or later
     data until its pre-registered test is scored; and a new airport's
     held-out years until its looks are run.
   - Once any part of a forward year has been scored, no new test may be
     pre-registered on that year.
   - Build choices are made identically at every airport. Choosing
     features or settings per airport is still not allowed.
   ```

3. **SPEC 5.4, second paragraph** ("They are **optional and block
   nothing.** ..."). Keep it, and add after it, exactly:

   ```
   **They are now scheduled as part of roadmap stage A** (section 6,
   DECISIONS D72.3): confidence intervals for the results on record, and
   a comparison against operational post-processed forecasts. They change
   no earlier verdict. Stage A's own gate (DECISIONS D72.7) decides the
   project's direction, not any airport's pass or fail.
   ```

   Change nothing else in section 5.

4. **SPEC 6.**
   - Heading: "## 6. Build order (each stage opens only when the previous
     one passes)" → "## 6. Build order and roadmap (DECISIONS D72)".
   - Intro paragraph: replace "**Stages 3 to 6 are intentionally left as
     short descriptions only.**" and the rest of that paragraph with:
     "**The roadmap stages after stage 2 are intentionally left as short
     descriptions only** (DECISIONS D72). Do **not** write out their
     detailed design until the owner opens each one. If a session tries
     to fill in a later stage early, treat it as a warning sign and stop."
     Keep the paragraph's first sentence (about stages 1 and 2).
   - Stage 1: unchanged.
   - Stage 2: heading "IN PROGRESS" → "ONGOING (the new-airports track,
     DECISIONS D72.3)". Keep every airport bullet exactly as it is.
   - Stage 2's "Further airports may follow before stage 3" bullet:
     change "before stage 3" to "at any point in the roadmap". Add one
     sentence at its end: "From stage G, adding an airport should take one
     script plus a checklist, and the script downloads its history
     (DECISIONS D72.2)." Keep the rest.
   - Replace the four bullets for stages 3, 4, 5 and 6, and the italic
     closing paragraph, with exactly:

   ```
   **The roadmap after stage 2 (DECISIONS D72).** The end goal is set out
   in section 1. Stages run in this order. Stages A and B run side by
   side, because both are time-critical.

   - **Stage A — benchmark and source probe.** Confidence intervals for
     the results on record (5.4). A comparison against operational
     post-processed forecasts (NWS MOS and the National Blend of Models,
     NBM) at DSM, RNO and SFO; its outcome rule is fixed in writing before
     it is looked at (DECISIONS D72.7). A read-only probe of each other
     source (ECMWF, ICON, WeatherNext, NBM, GEFS): archive depth, live
     feed, and which fields it offers.
   - **Stage B — forward test and data collection.** Pre-register the
     2026-27 forward test of section 8's recipe on GFS, split at the GFS
     v17 go-live date (DECISIONS D72.5). For any source with no
     downloadable archive, start saving its daily forecasts, all hours and
     both leads; where to save is decided then (DECISIONS D72.8).
   - **Stage C — widen the target, on GFS only.** An hourly temperature
     curve, the daily maximum, and the 48-hour lead. Written with the
     weather model as a setting.
   - **Stage D — correct each other weather model on its own,** on the
     full curve, screening each at a few hours first.
   - **Stage E — blend and stack.** Combine the corrected models, with NBM
     as an input where it exists. This chooses which inputs go forward.
   - **Stage F — upgrade policy.** What happens when any weather model
     changes version, starting with GFS v17.
   - **Stage G — live product, version 1.** A daily pipeline, a
     prediction log that is never edited, a simple display, and
     one-script airport onboarding.
   - **Stage H — probabilistic forecasts.** Ranges with stated odds,
     judged against their own bar, fixed before running.
   - **Pooling (conditional).** Combining airports into one model with
     location-describing features. Opened only if the number of airports
     makes it worthwhile. It inherits the solar-standard-noon target hour
     already in use (4.1, DECISIONS D27, D33).

   The former stages 3 to 6 are replaced (DECISIONS D72.10): former stage
   3 (pooling) is the conditional step; former stage 4 (add models and
   blend) is stages D and E; former stage 5 (widen the target, and the
   48-hour lead) is stage C; former stage 6 (live product) is stage G.

   *(The roadmap stages have no sections of their own yet, and will not
   until the owner opens them. Stage 2 needs no section of its own,
   however many airports it comes to hold: the sections above are written
   per airport, so opening one means adding a row to the airport table,
   not adding a design.)*
   ```

5. **Other stale references.** Search SPEC.md for "stage 3", "stage 4",
   "stage 5", "stage 6" (any case), "Q30" and "Q32". For each hit outside
   the text written above: if it names a former stage by number, update
   it to the new name (per D72.10) without changing its meaning; if it
   cites Q30 or Q32 as open, update it to closed (D72.9). If a hit is
   historical (it describes what was true at the time), leave it. List
   every hit and what you did in F121.

---

## Step 3 — RESULTS.md edits

1. **Intro paragraph.** Add "revised after session 80" to the revision
   line. Nothing else in the intro.
2. **Section 7, first bullet.** At its end, after "remains untested", add:
   " It is parked (DECISIONS D72.9)."
3. **Section 7, last bullet** ("Parked directions, and the current
   position"). Replace the whole bullet with exactly:

   ```
   - **The roadmap.** The owner has set a roadmap to a private, live daily
     tool (DECISIONS D72; SPEC 6). Next are a comparison against
     operational post-processed forecasts and a probe of other weather
     models' data (stage A), and a pre-registered forward test of the
     selected-features recipe on 2026-27, split at the GFS v17 go-live
     date (stage B). Widening the target to a full daily curve and the
     48-hour lead, correcting and blending other weather models, and the
     live product itself are later stages (C–G). Probabilistic forecasts
     follow (H). Pooling is conditional.
   ```

4. **Footer.** Add "and after session 80 (DECISIONS F121)" to the
   revision list.

---

## Step 4 — PROJECT-INSTRUCTIONS.md edits (only these)

1. **Header note.** Directly after the title line ("# ML Weather —
   Planning-Chat Operating Guide"), insert exactly:

   ```
   > **For Claude Code:** this file is the operating guide for the
   > claude.ai planning chat. Claude Code does not follow it. Claude Code
   > follows CLAUDE.md, and edits this file only when a session prompt
   > says exactly what to change.
   ```

2. **§2 table, the "Project memory" row.** Change "Durable reasoning,
   preferences, the roadmap and its rationale" to "Durable reasoning and
   preferences (the roadmap itself is SPEC 6 and DECISIONS D72)".
3. **§2 table, new row.** Add, after the `CLAUDE.md` row:

   ```
   | `PROJECT-INSTRUCTIONS.md` | This guide: how planning chats work. Kept in the repo root | Planning side only. Claude Code does not follow it; it edits it only when a session prompt says exactly what to change |
   ```

4. **§5, the list of files to re-upload.** After the `CLAUDE.md` line,
   add:

   ```
   - `PROJECT-INSTRUCTIONS.md` — only when a session edited it.
   ```

5. **§9.** After the "Lock before you look" bullet, add exactly:

   ```
   - **Claims vs build choices (D72.2, SPEC 2.5).** Only a stated result
     needs a frozen, pre-registered, one-look test. Build choices are made
     by time-ordered cross-validation on data not held out for any claim,
     identically at every airport, and are never quoted as results.
   - **Forward years.** Once any part of a forward year (e.g. 2026-27) has
     been scored, no new test may be pre-registered on it.
   ```

Change nothing else in PROJECT-INSTRUCTIONS.md. If any anchor text above
is not found, **stop and report**.

---

## Step 5 — CLAUDE.md edit (only this)

In "The three files", after the RESULTS.md bullet (the second on-demand
file), add this paragraph, exactly:

```
**PROJECT-INSTRUCTIONS.md** (repo root) is the operating guide for the
claude.ai planning chat. Claude Code does not follow it and does not read
it routinely. Claude Code follows this file. It edits
PROJECT-INSTRUCTIONS.md only when a session prompt says exactly what to
change.
```

Change nothing else in CLAUDE.md.

---

## Step 6 — DECISIONS-archive.md header

Find the header sentence that says a pointer is left in DECISIONS.md for
each moved section. Replace it with: "Since session 77, no pointer is left
in DECISIONS.md for a moved entry. An entry's number always resolves in
whichever of the two files holds it (DECISIONS D46, D72.9)." Report the
before and after text in F121. If no such sentence exists, **stop and
report**.

---

## End-of-session steps (CLAUDE.md), then stop

1. **Append F121** to DECISIONS.md, after D72: "Documentation only. What
   changed in SPEC.md, RESULTS.md, PROJECT-INSTRUCTIONS.md, CLAUDE.md and
   DECISIONS-archive.md in session 80". List every edit by section, with
   Step 0's results and Step 2.5's hit list. End with a "What this did not
   do" list (no data read, no script run, no model, no score, no stage
   design written, no earlier verdict or figure changed, CLAUDE.md changed
   only by Step 5's paragraph, nothing committed).
2. **Archive step.** Move these to DECISIONS-archive.md, mechanically and
   verbatim, each with its dated heading, per CLAUDE.md:
   - the "2026-08-16 — Parked items" block: its heading and P1–P3 only.
     **D17 and F7, which follow it, stay live.** Move up to, not
     including, the `---` line before D17;
   - the Q30 block ("2026-08-18 — Open question raised by session 18") and
     its update ("2026-08-19 — Q30 status update");
   - the Q32 block ("2026-08-20 — Open question raised by session 27");
   - both session 65 blocks (D59 and F110);
   - the session 75 block (D66).

   These stay live: D17, F7, D46, D47, F96, D51, D62 (D62.7 is needed by
   session 81), D71, F120, D72 and F121. If any listed entry fails the
   archive criterion (for example, STATUS's "Next" needs it word for word),
   leave it live and say why.
3. **Overwrite STATUS.md** as a current-only snapshot (prune, do not
   append):
   - Headline: three proven methods; F109 stands; KSFO passes the
     selected-features method on two looks (F119, D71), with D71.2's
     headline and D71.5's framing, as now.
   - No untouched held-out year remains at any of the six airports
     (D71.1).
   - The roadmap is set (D72; SPEC 6): stages A–H in brief, one line each.
   - Open questions: none live. Q30 and Q32 are closed (D72.9).
   - Carried items: GFS v17, updated to D72.11 (re-check each planning
     session; earliest possible go-live late October 2026, D69.6).
     Uncertainties stages A–B will answer: other sources' archive depth
     and fields; whether GFS v17 retrospective runs are public; the v17
     go-live date (sets period A's length).
   - Remove the "Roadmap planning inputs" and "Archive pointers" items
     (settled by D72).
   - End with this **"Next planning session"** line: "Review session 80.
     Then draft session 81: pre-register the 2026-27 GFS forward test and
     train and freeze its model (D72.5, D72.13)."
4. **Write `notes/session-80-output.txt`** containing, copied
   mechanically (cat / sed / git), not retyped:
   - Step 0's output;
   - D72 and F121, verbatim, from DECISIONS.md;
   - `git diff SPEC.md`, `git diff RESULTS.md`,
     `git diff PROJECT-INSTRUCTIONS.md`, `git diff CLAUDE.md`;
   - the header of DECISIONS-archive.md, before and after;
   - the new STATUS.md in full;
   - the list of entries moved to the archive, with a check that each
     moved entry appears in DECISIONS-archive.md byte for byte;
   - the consistency check (next item).
5. **Consistency check.** Re-read CLAUDE, SPEC, STATUS and DECISIONS.
   Report disagreements, duplicated headings, out-of-order entries and
   unresolved D/F/Q citations (in either file). Search SPEC, RESULTS,
   STATUS, CLAUDE and PROJECT-INSTRUCTIONS for "stage 3" to "stage 6" (any
   case), "Q30", "Q32", "P1", "P2", "P3" and "roadmap planning session";
   report each hit and whether it is still true. Report only; do not fix.
6. **Do not write a commit message file, and do not commit.** Stop and
   wait for the owner's review.
