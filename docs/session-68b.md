# Session 68b — Correctness audit, part 2: logic and leakage review (read-only)

## Context

This is the final audit session under D60.1 and D61. Sessions 66, 67 and
68a are done.

Session 68a showed that every headline figure reproduces exactly from the
committed code and data (163 of 163), and that B's features rebuild exactly
from the raw GRIB. Reproduction proves the code does what it did. **This
session checks that what it does is right**: no leakage, and faithful to
SPEC.

Read these before starting:

- `notes/audit-session-67.md` section 3 (the core pipeline map) and
  section 6;
- `notes/audit-session-68a.md`;
- D61.

## Scope (D61.1, D61.3)

**The headline pipeline only.** That means:

- the scripts behind F16/F30/F47/F64/F82, F94 and F109;
- their data builds, including the pull and decode scripts behind the
  tracked Open-Meteo and IEM inputs, the session 37/40 GRIB builds, the
  session 49/51/53/55 family derivations, `session63_reserved_year_build.py`,
  `session60_combine_design.py` (the selection manifest only) and the guards.

The E1–E5 and combine experiment scripts are out of scope.

**Read-only.** Exactly two files may be written:

1. a new `notes/audit-session-68b.md`, the report;
2. the overwritten STATUS.md.

There is no DECISIONS entry and no archive move (list candidates in the
report instead).

**No spent-year figure.** D61.1 says 68b recomputes nothing. Small data
checks are allowed, to support a finding. These may read date, key and
feature columns of any processed file, and they run from `/tmp`. But no
check may do any of the following on 2024-25 or 2025-26 rows:

- compute an error, an MAE or a skill score;
- run a model or produce a model output;
- compare a forecast with an observation.

Data checks that pair forecasts with observations may use training-window
rows only.

**No network.** No project script is run in the working repo. If running
project code helps, for example calling a committed function on a
training-window date, do it in a clean clone under `/tmp`, as in 68a.

**How to read the code.** The core set is large, so do not read whole files
top to bottom. For each checklist item below, find the functions that
implement it, using the session-67 map and grep, and read those. For the
five minimal-method scripts: review one fully, then diff the others against
it.

If this prompt disagrees with a spec file, stop and flag it.

---

## Step 0 — Starting state

Run `git status --porcelain`. The only expected output is the untracked
`docs/session-68b.md`.

## Step 1 — The review checklist

For **each** item, record four things:

- **the rule**: the SPEC or DECISIONS text it must match, quoted briefly;
- **the code**: file, function and lines, for every headline path it
  applies to (minimal, F94, F109, and the builds);
- **the verdict**: OK, FINDING or UNCERTAIN;
- **the evidence**: the code lines, plus any data-check output.

"Looks fine" is not evidence. Where a data check can confirm something, run
one.

### A. Time and leakage

1. **Forecast issue time.**
   - Every forecast value used for target day D must come from a run issued
     before D's target hour, under the lead-time convention: SPEC 7.2,
     D48.2/F89 for GRIB, and the minimal method's own source rule for
     Open-Meteo.
   - Check the code.
   - Data check, across all processed rows: `run_date` against
     `target_date`, and cycle and lead against the target hour, per
     airport. These are date columns only, so all windows are allowed.
2. **No feature sees the future or an observation.**
   - For every model input (B's five, plus L, D, T and R), confirm it is
     built only from forecast fields of that same run.
   - Confirm no observed value enters any feature.
3. **Persistence.**
   - Confirm it is the observation at the target hour on D−1, exactly as
     SPEC defines it, and never D.
   - Confirm how days with a missing D−1 value are handled, and that this
     matches the persistence-subset notes in F94 and F109.
4. **Train/test split.**
   - Check the boundaries in code against SPEC 4.3 (the minimal method and
     F94) and D58 item 4 (F109).
   - Confirm whether each boundary is inclusive or exclusive, that the
     windows don't overlap, and that no test-window row can enter training.
   - Check which date the split filters on (`target_date` or `run_date`),
     and whether that date is UTC or local.
5. **Fitting touches training rows only.**
   - Confirm there is no normalisation, imputation, encoding or feature
     construction that uses statistics from test rows or from the full
     dataset.
   - Confirm there is no target-derived feature.
6. **Same rows for every compared score.**
   - For each result, confirm that raw GFS, persistence and every model
     rung are scored on the rows the record says.
   - Where the rows differ (the persistence subset), confirm the record says
     so, and that the pass/fail comparison uses the rows SPEC 5.3 requires.
7. **Guards.**
   - Confirm the reserved-year guard (`session48_reserved_year`) and the D48
     window self-guard are called on every path that must be guarded, and
     that they would actually fire.
   - Test the guards on synthetic dates in the clone. Do not use real
     spent-year data.

### B. Targets and pairing

8. **Target hour** per airport (SPEC 4.1).
   - Check whether it is in UTC or local time, and how daylight saving is
     handled.
   - Check that it is consistent between observations, forecasts and
     persistence.
9. **Pairing** (SPEC 4.5, D14). This covers the ±15-minute window, rounding
   to the hour, and the A67-12 difference between "nearest" and
   "last-wins".
   - Session 67 counted one tie day in the whole record, with no effect.
     Confirm the logic is otherwise faithful to SPEC.
10. **Units and missing values.**
    - Check °C against K on every path, and that parsing of the IEM `tmpc`
      field and of Open-Meteo nulls is correct.
    - Confirm missing values are dropped and counted, never zero-filled.

### C. Feature builds

11. **Grid and interpolation.**
    - Check the longitude convention (0–360 or −180–180) at every airport.
      EGLC sits near 0° longitude, and DSM and RNO are west of Greenwich.
    - Check the latitude order, and that bilinear interpolation uses the
      four correct surrounding grid points.
    - Data check: print each airport's four grid-point coordinates and
      weights on one training date.
12. **Cycle and lead selection** (`cycle_and_lead`).
    - Check lead 24 against lead 26 per airport, given its target hour.
    - Confirm this is the same logic in the B build and in all four family
      builds.
13. **Elevation correction** (D48.3/F90).
    - Check the formula, its sign and lapse rate, the terrain height used,
      and that it applies to surface temperature only.
    - Check whether L's `t2` is the corrected or the uncorrected value, and
      whether that matches F98.
14. **Each added feature's derivation**, against its own finding:
    - L = t2 − t850: check the sign and units;
    - D: check the dew-point depression definition and the floor
      (D58 item 3);
    - T: check the 3-hour pressure tendency, which two fields it uses, and
      its sign;
    - R: check the de-accumulation arithmetic for the 2-hour window at the
      lead-24 and lead-26 airports (F102), including the division by hours.
15. **Season features.** Check `year_fraction`, leap years, and the sin/cos
    phase. Confirm the same formula is used on every path.
16. **The reserved-year build.** Confirm that
    `session63_reserved_year_build.py` uses the same derivation as the
    family pulls. F108 records a proof; verify that the proof's method
    supports its claim.

### D. Model and scoring

17. **LightGBM settings.** Confirm they match D21.4 and D48.6 exactly on
    every headline path. Also check the random seed and the determinism
    settings, and how many threads are used.
18. **Feature order and columns.** Confirm the model gets exactly the
    locked feature list, in the same order at fit and at predict, and that
    no stray column (a date or station field) enters.
19. **Scoring.**
    - Check the MAE formula and the skill-margin formula.
    - Check the airport-averaged figure: is it a mean of the MAEs or a
      pooled MAE, and which one does the record claim?
    - Check the pass/fail rule against the frozen bar (SPEC 5.3, D58
      item 7).

### E. Consistency across copies

20. **The five minimal-method scripts.** Diff them to verify session 67's
    claim that they are identical apart from print text. List every
    non-print difference.
21. **Copied functions on the headline path.** For every function name used
    on more than one headline path, confirm the copies are identical, or
    explain each difference and whether it matters.
22. **Carried-over items.** Give a disposition for each:
    - A67-04 (stale preflight text);
    - A67-12 (pairing);
    - A67-14 (`r.get`): can a missing feature ever reach the model silently
      on the F109 path?

## The report: `notes/audit-session-68b.md`

1. **Summary.** Counts of OK, FINDING and UNCERTAIN across the 22 items, and
   findings by severity. The severities are:
   - **must-fix**: leakage, a SPEC violation that affects a figure, or a
     wrong number;
   - **should-fix**: a SPEC/code disagreement with no effect, or fragile
     code;
   - **cosmetic**;
   - **uncertain**.
2. **The checklist.** One block per item, in the four-part format above.
3. **Findings as a plain list**, one block each:

   ```
   A68b-nn | severity | file:line
   evidence: ...
   suggested fix: ...
   ```

   Mark any suggested fix to a frozen script as "frozen — owner decision".
4. **Clean items**, listed explicitly.
5. **Archive candidates**, listed only.
6. **Appendix.** Data-check sources and raw outputs.

## End of session

1. Paste into chat, **as plain text with no tables**:
   - the summary;
   - every FINDING and UNCERTAIN item, in full;
   - the findings list.
2. Overwrite STATUS.md as a current-only snapshot. It should say:
   - the three-part audit is complete, with the paths of all four reports
     (66, 67, 68a, 68b);
   - triage is next;
   - Q30 is deferred;
   - Q32 is unchanged.

   It must end with a "Next planning session" line: owner review of the
   session-68b report, then triage of all findings from the four audit
   reports into must-fix, should-fix and leave-alone, recorded in one
   DECISIONS entry, followed by fix sessions.
3. Run `git status` and show that only `notes/audit-session-68b.md` (new)
   and STATUS.md changed.
4. Write a suggested commit message. Do not commit anything.
