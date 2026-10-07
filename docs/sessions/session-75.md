# Session 75 — Q33: how much does column order move the fit? (descriptive only)

## What this session is

Session 74 (F114) found that changing **only the order of the input
columns** moved RNO's B+D,L,R,T reserved-year MAE by 0.0038 °C (1.2703 to
1.2742). That logged Q33: how large is this fit-to-fit wobble, compared
with the margins on record, especially the small ones such as DSM's
B+D,L,R,T-over-B margin (+1.94%, 0.0279 °C, SPEC 8.6 (d))?

This session measures that wobble, **descriptively**, on two folds whose
test years were never held out. It also records three owner decisions from
the planning chat.

**Standing of this session.** It is a description, not a verdict. It
cannot change any verdict, claim or figure on record. F109 stands. Nothing
is selected, tuned or adopted on these results. No row dated 2024-08-01 or
later is used anywhere — not the reserved year (2024-25, spent, F109), not
the sealed year (2025-26, spent, F94), and nothing from 2026-27.

Offline. No data pull. No existing script is edited, frozen or not.

---

## Step 0 — Integrity check (read-only)

1. `git status --porcelain`. Expect only this session prompt untracked.
   Report the output.
2. Read the LightGBM settings the record uses (`LGB_PARAMS` in
   `scripts/session62_reserved_confirm.py`, l.131–146; D21.4/D48.6).
   Report them in full. State whether **any** setting makes a fit random
   — for example `bagging_fraction` < 1 with `bagging_freq` > 0,
   `feature_fraction` / `colsample_bytree` < 1, or any other sampling
   setting. This decides whether Task 2c runs.
3. Confirm the two folds from `scripts/session48_reserved_year.py`'s
   `EXPERIMENT_FOLDS` (D51):
   - `2022-23`: train 2021-03-24..2022-07-31, test 2022-08-01..2023-07-31
   - `2023-24`: train 2021-03-24..2023-07-31, test 2023-08-01..2024-07-31

   Pass both through `assert_reserved_year_excluded()` (import only; do
   not edit the script) and report that neither raises. The third fold in
   that list (`2025-26`) tests the spent sealed year and is **not used**.

If anything here disagrees with this prompt or with SPEC, stop and report.
Do not guess.

---

## Step 1 — Write D66 into DECISIONS.md BEFORE any fit

Append this entry to DECISIONS.md, dated 2026-09-24 (or today's date),
under the heading "Session 75 decision: planning-chat decisions and the
Q33 pre-registration". Write it before any model is fit. Use plain
language; the content is below.

**D66. Owner decisions, planning chat (after session 74).**

**D66.1 Q30 sequencing (Q30 stays open).** The owner chose this order:
(1) Q33, measured descriptively (this session); (2) a further airport
under the frozen B+D,L,R,T recipe (Q30 branch (i), D59.5), with the airport
and its test design still to be chosen; (3) a dedicated roadmap planning
session, because SPEC 6's stage list is out of date. Pooling is deferred.
The 2026-27 forward test (Q30 branch (ii)(i)) is deferred until the GFS
v17 date is known (D66.2).

**D66.2 GFS v17 status (planning-chat research, not checked by this
session).** NWS Public Information Statements 26-29 and 26-30 (April 2026)
propose GFS v17 (a ~9 km, coupled model) for October 2026, marked
tentative. They say a Service Change Notice will be issued 30 days before
go-live, and that folder structure and file names will change. As of
2026-09-24 the NWS notice list shows no such notice. Why it matters: the
recipe is trained on GFS v16 only (D48.7). If v17 goes live during
2026-27, most of that year would be v17 forecasts, so a 2026-27 test would
ask a different question (does a v16-trained correction survive a model
upgrade?) rather than repeat F109 on a new year. The new-airport branch is
unaffected: all its data (2021–2026) is v16. Future GRIB pulls of v17 data
may need path and `.idx` changes. To be re-checked at each planning
session.

**D66.3 Q33 pre-registration.** Descriptive only (see "Standing" above).
- **Data.** The `2022-23` and `2023-24` folds of D51's `EXPERIMENT_FOLDS`,
  all five airports. The same committed feature files, transforms,
  complete-case rule, target, settings and API as the record (SPEC 8.1,
  8.3, 8.8: G14, G17, G19, G20). Any row dated 2024-08-01 or later is
  removed at load, before any matrix is built, and the count removed is
  reported.
- **Models.** `B` (5 columns) and `B+D,L,R,T` (9 columns).
- **What varies: column order only.**
  - B+D,L,R,T: 100 orderings drawn with `numpy.random.default_rng(75)`,
    duplicates redrawn, **plus** two anchors — the record order (SPEC 8.8
    G15) and session 73's order (B, then L, D, T, R). 102 in total.
  - B: all 120 orderings of its 5 columns.
  - If Step 0.2 found any random setting: also 10 seed values (0–9) at the
    record order, for both models, reported separately. Otherwise not run.
- **What is reported,** per airport and per fold:
  - min, max, range and standard deviation of MAE for B and for
    B+D,L,R,T, in °C and as % of the record-order MAE;
  - the **win share**: over every (B+D,L,R,T ordering, B ordering) pair,
    the fraction where B+D,L,R,T has the lower MAE;
  - the record-order margin over B (record-order B+D,L,R,T vs canonical-
    order B), for reference.
- **Reading rule, fixed now.** Win share 100% → "B+D,L,R,T beats B by
  more than the column-order spread, on this fold". 0% → "B beats
  B+D,L,R,T by more than the spread". Anything else → "within the
  column-order spread". Stated per airport, per fold. No other reading is
  added after the results are seen.
- **Scale comparison (rough, different year).** A table setting F109's
  own margins over B (SPEC 8.5: EGLC 0.0853, LFPG 0.0916, DSM 0.0279,
  YSDU 0.0387, RNO 0.1530 °C) and F114's 0.0038 °C shift beside each
  airport's B+D,L,R,T MAE range on each fold. Labelled: F109 is 2024-25,
  these folds are 2022-23 and 2023-24, and the training windows are
  shorter (495 and 860 days against F109's 1,226), so this is a guide to
  scale only.
- **What it cannot do.** Change any verdict, claim or figure; select or
  adopt anything; touch any row dated 2024-08-01 or later.

---

## Step 2 — The fits

New script: `scripts/session75_order_spread.py`. Outputs go to
`data/rebuild/session75/` (new folder) and the full printed output to
`notes/session-75-output.txt`. Do not write to any existing file under
`data/`.

Reuse existing code by **importing** it read-only where that is clean
(session 73's and session 74's functions, or the record script's own
helpers, as session 74 did). Do not edit or copy-and-modify any existing
script. SPEC 8.7's build requirements apply to the new code where
relevant (non-finite values rejected and counted; no writes to committed
record files).

**2a — Anchor and determinism check (before the spread).**
- Fit B+D,L,R,T at the record order and B at its canonical order, on both
  folds, at all five airports. Report n_train, n_test and MAE (full
  precision and 4 dp).
- Repeat the record-order B+D,L,R,T fit once in a separate process and
  confirm the predictions are identical (maximum absolute difference).
- Search DECISIONS-archive.md (F105, F106, D57, D58) and the committed
  CSVs for a recorded MAE for the **same model, same fold, same airport
  and same column order**. If one exists, report whether it matches at
  4 dp. If one exists and does not match, **stop before 2b** and report —
  do not hunt. If none exists at the same column order, say so plainly
  and continue.

**2b — The spread.** Run exactly the orderings in D66.3. No other fit.

**2c — Seeds.** Only if Step 0.2 found a random setting. Otherwise
report "not run: no random setting".

---

## Step 3 — Write F115 into DECISIONS.md

Record the results as **F115**, per the D66.3 reporting list and reading
rule, with the real numbers. Include:
- the per-airport, per-fold table (B spread, B+D,L,R,T spread, win share,
  reading);
- the scale-comparison table with its caveat;
- the anchor and determinism results from 2a;
- a one-paragraph plain-language answer to Q33, using only the pre-set
  reading rule;
- "What this did not do" (no verdict changed, F109 stands, nothing
  selected, no row on or after 2024-08-01 used, no script edited, no data
  pulled).

Q33 is then **answered descriptively** and closed in F115. F115 stays live
(the new-airport pre-registration will cite it).

---

## Documents

- **SPEC.md, RESULTS.md, README.md, CLAUDE.md: not edited.**
- **Carried item (write into STATUS, do not act on it):** SPEC 7.2 glosses
  bilinear interpolation as "weighted by distance", which could be read as
  inverse-distance weighting. SPEC 8.8 G6 says standard bilinear, not
  inverse distance. Fold a one-line clarification of SPEC 7.2 into the next
  session that edits SPEC. (Session 74's consistency check: a tension, not
  a conflict.)

---

## End of session (CLAUDE.md)

1. Paste the real output (actual numbers).
2. **Overwrite STATUS.md** as a current-only snapshot. It must include:
   - current state (F109 stands; Q33 answered descriptively in F115);
   - live open questions: Q30 (open; sequencing per D66.1), Q32
     (unchanged);
   - the carried SPEC 7.2 item above;
   - GFS v17: re-check the NWS notice list at each planning session
     (D66.2);
   - and end with this line, filled in:
     **"Next planning session: review F115. Then plan the new airport
     (Q30 branch (i)): the owner chooses the airport (or a candidate
     screen) and the test design (one look on 2025-26, or two pre-
     registered looks on 2024-25 and 2025-26). After the airport, hold a
     dedicated roadmap planning session. Roadmap session inputs: P1–P3,
     Q30 (2026-27, pooling), Q32, SPEC 5.4, RESULTS §7 terrain
     descriptor, SPEC stages 4–6, GFS v17 (D66.2)."**
3. Consistency check: re-read CLAUDE, SPEC, STATUS and DECISIONS; report
   anything that disagrees, any duplicated heading, any entry out of
   order. Report only.
4. Archive step: apply the D46 criterion. D65 (session 74's
   pre-registration, now carried out) is a likely candidate; report what
   moved and why, mechanically and verbatim. Keep D66 and F115 live.
5. Write the suggested commit message. **Do not commit.** Stop and wait
   for review.
