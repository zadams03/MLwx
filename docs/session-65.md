# Session 65 — D59 verdict, SPEC/RESULTS fold-in, archive pass (documentation only)

## Scope, in one paragraph

Documentation only. No code, no data, no model fit, no score. Nothing under
`scripts/` or `data/` is modified. The reserved year (2024-08-01..2025-07-31,
D51) and the sealed year (2025-08-01..2026-07-31, F94) are both spent; no
file from either is opened for scoring. You will: (1) append D59, the owner's
verdict on F109; (2) fold B+D,L,R,T into `SPEC.md` as a new section 8;
(3) add it to `RESULTS.md` as a new "Act three" section; (4) append F110
recording what changed; (5) archive the settled entries, **only after**
steps 2–3 are done; (6) overwrite STATUS.md. Content comes only from what
is already on record in DECISIONS/SPEC. Compute nothing new. If anything
here disagrees with a spec file, stop and flag it.

---

## Step 0 — Integrity check (report real output)

- `git status --porcelain` — expect only this untracked prompt file.
- **Read-only check for the 2026-27 year.** Report the maximum date present
  in every file under `data/processed/` (one line per file). The owner needs
  to know whether any row dated on or after 2026-08-01 exists anywhere. Do
  not open, fit on, or score any such row — report dates only.

## Step 1 — Append D59 to DECISIONS.md

Date heading `2026-09-23 — Session 65 decision: ...`. Write D59 in the
project's plain style with these numbered items. Do not soften or extend
the claims.

**D59.1 Result accepted.** The owner reviewed F109 and accepts it as
recorded. B+D,L,R,T passes the frozen bar (D58 item 7) at all five
airports: it beats both raw GFS and persistence on MAE everywhere. The
secondary read holds: 1.2377 vs 1.3170 airport-averaged MAE against plain B
(+6.02%). No ranking among airports is claimed. DSM's +1.94% is consistent
with D58 item 7's own expectation. RNO's +10.72% is descriptive only.

**D59.2 Feature-selection programme closed.** The programme (D51 reserve →
E1–E5, F97–F105, D52–D56 → combine sweep D57/F106 → lock D58 → build
F107/F108 → one look F109) is complete. No further feature family, variant,
or combination is tested under it. The reserved year is spent for this
programme and is not reused for any verdict. The in-code reserved-year
guard stays in place, untouched, as a permanent tripwire. It is not
retired.

**D59.3 Fold-in, with required caveats.** B+D,L,R,T goes into SPEC as a
new section 8, a third proven method alongside sections 1–6 and section 7.
None of the three erases the others (same spirit as D48.13). It becomes the
**default recipe** for any future airport work or pooling work, applied
unchanged and identically at every airport. Every new airport still needs
its own lock and single test. Any write-up of this result must carry these
caveats:
- (a) one year only;
- (b) this is the first look at the *selected set* on 2024-25, but B was
  already scored on that year descriptively in F96 (D58 item 8);
- (c) the section-8 margins (reserved year 2024-25) and the section-7
  margins (sealed year 2025-26) come from **different years** and must not
  be set side by side as like-for-like;
- (d) DSM's margin over B is small;
- (e) RNO's margin over B was not pre-registered.

**D59.4 Archive.** Once SPEC and RESULTS carry the content: archive F97–F109
and D52–D58. D51 and F96 stay live, because Q30's second-test-year branch
needs both word-for-word.

**D59.5 Q30 — options only. Q30 stays open.** A new fact changes the
options: **no untouched held-out year now remains.** The 2025-26 year is
spent (F94) and 2024-25 is spent (F109). The three branches:
- **A further airport.** Run it with B+D,L,R,T frozen unchanged. For a new
  airport, 2024-25 and 2025-26 have never been scored at that airport, and
  the recipe was selected without it. That makes this the cheapest
  genuinely out-of-sample test available now. It needs an airport choice:
  per D32, a harder type (coastal, tropical, or mountainous).
- **A second test year.** This is now only possible in one of two ways:
  - (i) a **live, forward-looking test on 2026-27**
    (2026-08-01..2027-07-31), pre-registered before any of its data is
    scored, and scored once after the year ends. This depends on Step 0
    confirming that no 2026-27 row has been scored.
  - (ii) a written rule for reusing an already-seen year, which gives
    weaker evidence.
- **Pooling (SPEC stage 3).** This is the largest build. With five
  locations, location-describing features have few examples to learn from,
  and pooling was previously judged premature.

**Planning-chat recommendation (not a decision, and the owner has not
chosen):** open a further airport under the frozen B+D,L,R,T recipe now.
In parallel, pre-register 2026-27 as a forward-looking test year (a small
documentation step) so that its clock is running. Defer pooling.

## Step 2 — SPEC.md: add section 8

Add `## 8. The selected-features GRIB method (a third, proven method)` after
section 7. Do not alter sections 1–7, except to change any literal text
that says the project has "two" methods, where that text is now wrong.
Report each such edit. Section 8 covers the following, each point cited:

- **What it is.** Section 7's B plus D, L, R, T. Use D58 item 3's table for
  the exact columns, source files and transforms, including D's floor.
  P, `rh` and `plev` are excluded.
- **What is unchanged from section 7.** List it, citing F98/F100/F101/F102
  for the source and lead of each family. Do not assume anything; state
  only what those entries say.
- **Training window, fold, settings, complete-case rule.** From D58 items
  4–5: the frozen LightGBM settings, and the same features at every airport.
- **How it was chosen.** The selection protocol, briefly: the D51 reserve,
  staged family tests on EXPERIMENT_FOLDS only, D57's mechanical rule,
  D58's lock, one look.
- **Result.** F109's per-airport table: raw, persistence, B, final, and the
  three margins.
- **Caveats.** D59.3 (a)–(e).
- **Status.** It is the default recipe for future airport and pooling work
  (D59.3).

## Step 3 — RESULTS.md

- Update the intro paragraph from "two" methods to three, and add
  "revised after session 65".
- Insert a new `## 6. Act three: the selected-features method`. Cover:
  - why the programme was run;
  - the protocol (the reserve, then selection, then one look);
  - the F109 table;
  - the D59.3 caveats, stated plainly.

  Lead with the bar result, then the secondary +6.02%. Do not headline
  RNO's number.
- Renumber the old section 6 to section 7 and fix any in-file references
  to it. Update its bullets:
  - "One shared test year" → B+D,L,R,T was tested on a different year
    (2024-25), but each method still rests on one year, and no untouched
    year remains.
  - The richer-features bullet: upper-air information has now been tried
    (L adopted).
  - Parked directions: Q30 per D59.5.

  Everything must be cited. Compute nothing new.

## Step 4 — Append F110

A short documentation finding listing exactly what changed in SPEC,
RESULTS and DECISIONS, and which entries were archived.

## Step 5 — Archive (only after Steps 2–4)

Move F97–F109 and D52–D58 to DECISIONS-archive.md: mechanically, verbatim,
and in order. Keep D51, F96, D59 and F110 live. Report the before and after
line counts of both files.

## End of session

1. Paste the real output of Step 0 and the archive line counts.
2. Show the full text of new SPEC section 8 and new RESULTS section 6.
3. Overwrite STATUS.md as a current-only snapshot. It should include:
   - three proven methods;
   - the programme closed;
   - no untouched held-out year remains;
   - Q30 open per D59.5;
   - Q32 unchanged.

   It must end with a "Next planning session" line: owner review of session
   65's documentation changes, then the owner chooses a Q30 branch (see the
   D59.5 recommendation).
4. Run the consistency check across CLAUDE, SPEC, STATUS and DECISIONS.
   Report only.
5. Write a suggested commit message. Do not commit anything.
