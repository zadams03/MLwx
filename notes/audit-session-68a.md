# Session 68a — Correctness audit, part 1: reproduce the record (read-only)

Scope: part three of the audit ordered by DECISIONS D60.1. The owner has
split that part into 68a (this session: reproduce the recorded results, and
rebuild a small sample of features from the raw GRIB) and 68b (the logic and
leakage review, not part of this session). See DECISIONS D61.

This session reports and fixes nothing. Every "suggested fix" below is for a
later fix session. A fix that touches a **frozen** script is marked "frozen
— owner decision".

How the work was run. All project code ran inside a clean clone,
`/tmp/audit68a/clone`, cloned from the working repo at HEAD
`9dc426c3ff2422ae4b1bfeba1a11185ecc708f83`. The clone got its own `.venv`,
built from `requirements.txt` with Python 3.12.2, the same way session 67
did it. `pip freeze` equals the 19 pins exactly. Every check script lives
in `/tmp/audit68a/`, and its full source is in the Appendix. Nothing was
fetched over the network apart from the pip install that the documented
setup requires. `/tmp` is temporary, so every output that matters is copied
into this report.

Section 2 (the pre-registered list and the sample rule) was written to this
file **before** any project code ran. It is reproduced below unchanged.
Only the draft note at the top of the file was dropped when the rest of
the report was assembled around it.

---

## 1. Summary

**Gate (Step 0).** Stopped at the gate, as the prompt requires. Four texts
forbid a re-run if read literally: D48.13 ("no re-run … whatever the
result"), F94 ("no re-run"), D51 ("exactly once"), and SPEC 8.4 ("run once,
and only once", which describes what happened). A second issue: D60.2 names
only F94 and F109, but the prompt also re-runs the five minimal-method
scripts. The owner ruled on both before any run. D60.2 overrides the four
texts for one verification run in 68a only. Coverage is extended to
F16/F30/F47/F64/F82 on the same terms. No verdict, claim or figure changes
whatever the run shows. Recorded as D61.4 and D61.5. The minimal-method
locks (D21.10, D31.10, D35.10, D39.10, D44.10) forbid only "a quiet
re-run". This run was announced in advance and cannot change a verdict.

**Step 2, reproduction: 163 of 163 figures match, 0 mismatches.**
- All seven scripts ran once, unchanged, and exited 0.
- Every script's full output is identical to its committed record, apart
  from the "run at" timestamp. For F94, one printed line also differs: it
  carries the machine's absolute path (A68a-04).
- Both result CSVs came out byte-identical to the committed copies:
  `session40_sealed_test_summary.csv` (F94) and
  `session63_reserved_confirm_grid.csv` (F109).
- The confirm run's stdout is identical to
  `notes/session-64-confirm-output.txt`.
- Every verdict reproduces: F16, F30, F47 and F64 PASS; F82 FAIL; F94 PASS
  at all five airports; F109 PASS at all five airports.

**Step 3, sample rebuild from the raw GRIB.**
- **B: 315 of 315 values match, 0 mismatches.** That is 45 station-days
  times 7 columns: forecast temperature (with the elevation correction as
  built), cloud cover and wind speed, plus four bookkeeping columns
  (target_hour, run_date, cycle, lead).
- Elevation terrain check: 5 of 5 match.
- Season features: 9 of 9 dates agree across the two committed scoring
  paths. They are date arithmetic, not built from the GRIB, and no
  processed CSV stores them.
- **L, D, T and R were not rebuilt** (option b). No raw GRIB bytes for them
  exist on disk, so a rebuild would need the network (A68a-01).
- The elevation constants' own derivation (`session37_elevation_fix.py`
  `main()`) was not re-run either. It always fetches over the network
  (A68a-02).
- The working repo's GRIB cache was not modified. 62,570 files and the
  listing checksum `dc9dff9a…664b7` were the same before and after.

**Findings by severity:**
- must-fix: 0
- should-fix: 1
- cosmetic: 4
- uncertain: 1
- total: 6

No finding is a wrong number.

---

## 2. Pre-registered comparison list and sample rule

Written before any project code was run in this session.

### 2.1 Step 2 — what is compared, for every script

**Pre-registered expectation.** Every figure below matches its recorded
value exactly, at the precision the record carries: the fourth decimal
place where the record has four decimals (F94's summary CSV, F109), and the
recorded precision where the record has only three (F16, F30, F47, F64,
F82, and F94's DECISIONS table). Counts and verdicts match exactly. D60.2
asks for a match "to the fourth decimal place". The minimal-method scripts
print MAE to three decimals only, and their DECISIONS entries record three.
A fourth decimal cannot be read from a single unchanged run of those
scripts, so for them the check is at three decimals (see section 5).

**A second, stronger check for every script.** Each script's full output is
diffed against its committed output file. Expected: identical, apart from
the "run at" timestamp line. Where a script writes a CSV (F94, F109), the
CSV is diffed against the committed copy at full stored precision.
Expected: byte-identical.

Minimal method, sealed test year 2025-08-01..2026-07-31, one script per
airport. Each line: MAE (degC) for raw GFS, persistence, climatology,
mean-bias reference, ML-corrected; then counts; then verdict.

- **EGLC**, `session07_test.py`, source F16 (DECISIONS-archive.md:1251).
  MAE 1.242 / 2.096 / 2.972 / 1.234 / 1.040. Training kept rows 1,569.
  Test paired rows 364. Test days dropped 1 (2025-11-21). Scored days 363.
  Mean training bias -0.1479. Closer than raw GFS 221 of 363.
  Verdict PASS (beats raw GFS and persistence).
- **LFPG**, `session13_test.py`, source F30 (DECISIONS-archive.md:2763).
  MAE 1.396 / 2.300 / 3.774 / 1.389 / 1.208. Training kept rows 1,569
  (1,204 inner + 365 validation). Test paired rows 364. Test days dropped 1
  (2026-07-08, off-hour report). Scored days 363. Mean training bias
  -0.0600. Closer than raw GFS 213 of 363. Verdict PASS.
- **DSM**, `session18_test.py`, source F47 (DECISIONS-archive.md:4870).
  MAE 1.815 / 4.003 / 5.030 / 1.760 / 1.700. Training kept rows 1,571.
  Test paired rows 365. Test days dropped 0. Scored days 365. Closer than
  raw GFS 195 of 365. Verdict PASS.
- **YSDU**, `session24_test.py`, source F64 (DECISIONS-archive.md:6765).
  MAE 1.251 / 2.669 / 3.143 / 1.238 / 1.210. Training kept rows 1,553
  (1,193 + 360). Test paired rows 356. Test observation-side drops 9.
  Scored days 347. Verdict PASS.
- **RNO**, `session29_test.py`, source F82 (DECISIONS-archive.md:8673).
  MAE 1.414 / 2.490 / 4.027 / 1.500 / 1.458. Training kept rows 1,568
  (1,203 + 365). Test paired rows 365. Test days dropped 0. Scored days 365.
  Verdict FAIL (does not beat raw GFS; beats persistence).

Richer 5-feature GRIB method, `session39_sealed_test.py` (no arguments),
source F94 (DECISIONS.md:265) and its summary CSV
`data/processed/session40_sealed_test_summary.csv` (cited by F94). Each
line: train_rows, test_rows, MAE raw GFS (GRIB), persistence, 3-feature,
5-feature (four decimals, from the CSV; F94's table rounds these to three),
verdict.

- EGLC: 1589, 364, 1.2536, 2.0964, 1.0367, 1.0000, PASS
- LFPG: 1589, 364, 1.3822, 2.3003, 1.1775, 1.1561, PASS
- DSM:  1590, 365, 1.7334, 4.0029, 1.6940, 1.6358, PASS
- YSDU: 1573, 356, 1.3167, 2.6686, 1.2834, 1.1786, PASS
- RNO:  1587, 365, 1.5116, 2.4901, 1.4551, 1.3460, PASS

Selected-features method, `session62_reserved_confirm.py --confirm`,
source F109 (DECISIONS-archive.md:13480) and its recorded output
`notes/session-64-confirm-output.txt`, reserved year 2024-08-01..2025-07-31.
Each line: n_train, n_test, no_obs_dropped, no_prev, MAE raw GFS (GRIB),
persistence, B, B+D,L,R,T (four decimals), verdict vs raw / vs persistence.

- EGLC: 1225, 364, 1, 1, 1.2362, 2.2259, 1.0861, 1.0008, PASS / PASS
- LFPG: 1224, 365, 0, 0, 1.4091, 2.5233, 1.3285, 1.2369, PASS / PASS
- DSM:  1225, 365, 0, 0, 1.7043, 4.1081, 1.4402, 1.4123, PASS / PASS
- YSDU: 1213, 360, 5, 5, 1.4897, 2.5775, 1.3030, 1.2643, PASS / PASS
- RNO:  1222, 365, 0, 0, 1.6135, 2.7563, 1.4272, 1.2742, PASS / PASS
- Bar verdict: ALL FIVE AIRPORTS PASS. Secondary read: airport-averaged
  MAE 1.2377 vs B 1.3170 (beats B).
- Grid CSV `data/processed/session63_reserved_confirm_grid.csv`:
  byte-identical to the committed copy.

### 2.2 Step 3 — sample rule

Fixed before building: the first, middle and last day of each window.
"Middle" is day index floor((N-1)/2) counted from the window's first day.

- training 2021-03-24..2024-07-31 (N = 1,226): 2021-03-24, 2022-11-26,
  2024-07-31
- reserved 2024-08-01..2025-07-31 (N = 365): 2024-08-01, 2025-01-30,
  2025-07-31
- sealed 2025-08-01..2026-07-31 (N = 365): 2025-08-01, 2026-01-30,
  2026-07-31

All five airports: 9 dates x 5 airports = 45 station-days. If a chosen date
is missing from the cache or was dropped by a recorded failure log, the next
available day is used and the substitution is reported.

Tolerance: agreement to the processed CSV's stored precision, stated per
column in section 4.

---

## 3. Step 2 results — one line per figure

Each script ran once, from the clone root, as `.venv/bin/python
scripts/<script>.py`. The F109 run added `--confirm`. That is each
script's own documented invocation: F94's script refuses any argument
(`session39_sealed_test.py:438`), and F109's entry point takes only
`--confirm` (`session62_reserved_confirm.py:740–743`). Wall-clock times:
session07 24.0 s (this includes the one-time libomp restart and first
import), session13 1.5 s, session18 1.3 s, session24 1.3 s, session29
1.3 s, session39 2.6 s, session62 `--confirm` 3.1 s.

### 3.1 Per-figure comparison

Produced by `compare_step2.py` (Appendix 7.2). "Recorded" values are the
pre-registered ones in section 2.1.

```
-- EGLC  session07_test.py  (F16)
EGLC MAE Raw GFS                                     recorded 1.242      recomputed 1.242      match
EGLC MAE Persistence                                 recorded 2.096      recomputed 2.096      match
EGLC MAE Climatology                                 recorded 2.972      recomputed 2.972      match
EGLC MAE Mean-bias reference                         recorded 1.234      recomputed 1.234      match
EGLC MAE ML-corrected                                recorded 1.040      recomputed 1.040      match
EGLC training kept rows                              recorded 1569       recomputed 1569       match
EGLC test paired rows                                recorded 364        recomputed 364        match
EGLC test days dropped                               recorded 1          recomputed 1          match
EGLC scored days                                     recorded 363        recomputed 363        match
EGLC verdict                                         recorded PASS       recomputed PASS       match
EGLC mean training bias                              recorded -0.1479    recomputed -0.1479    match
EGLC closer than raw GFS                             recorded 221 of 363 recomputed 221 of 363 match
-- LFPG  session13_test.py  (F30)
LFPG MAE Raw GFS                                     recorded 1.396      recomputed 1.396      match
LFPG MAE Persistence                                 recorded 2.300      recomputed 2.300      match
LFPG MAE Climatology                                 recorded 3.774      recomputed 3.774      match
LFPG MAE Mean-bias reference                         recorded 1.389      recomputed 1.389      match
LFPG MAE ML-corrected                                recorded 1.208      recomputed 1.208      match
LFPG training kept rows                              recorded 1569       recomputed 1569       match
LFPG test paired rows                                recorded 364        recomputed 364        match
LFPG test days dropped                               recorded 1          recomputed 1          match
LFPG scored days                                     recorded 363        recomputed 363        match
LFPG verdict                                         recorded PASS       recomputed PASS       match
LFPG mean training bias                              recorded -0.0600    recomputed -0.0600    match
LFPG closer than raw GFS                             recorded 213 of 363 recomputed 213 of 363 match
-- DSM  session18_test.py  (F47)
DSM MAE Raw GFS                                      recorded 1.815      recomputed 1.815      match
DSM MAE Persistence                                  recorded 4.003      recomputed 4.003      match
DSM MAE Climatology                                  recorded 5.030      recomputed 5.030      match
DSM MAE Mean-bias reference                          recorded 1.760      recomputed 1.760      match
DSM MAE ML-corrected                                 recorded 1.700      recomputed 1.700      match
DSM training kept rows                               recorded 1571       recomputed 1571       match
DSM test paired rows                                 recorded 365        recomputed 365        match
DSM test days dropped                                recorded 0          recomputed 0          match
DSM scored days                                      recorded 365        recomputed 365        match
DSM verdict                                          recorded PASS       recomputed PASS       match
DSM closer than raw GFS                              recorded 195 of 365 recomputed 195 of 365 match
-- YSDU  session24_test.py  (F64)
YSDU MAE Raw GFS                                     recorded 1.251      recomputed 1.251      match
YSDU MAE Persistence                                 recorded 2.669      recomputed 2.669      match
YSDU MAE Climatology                                 recorded 3.143      recomputed 3.143      match
YSDU MAE Mean-bias reference                         recorded 1.238      recomputed 1.238      match
YSDU MAE ML-corrected                                recorded 1.210      recomputed 1.210      match
YSDU training kept rows                              recorded 1553       recomputed 1553       match
YSDU test paired rows                                recorded 356        recomputed 356        match
YSDU test days dropped                               recorded 9          recomputed 9          match
YSDU scored days                                     recorded 347        recomputed 347        match
YSDU verdict                                         recorded PASS       recomputed PASS       match
-- RNO  session29_test.py  (F82)
RNO MAE Raw GFS                                      recorded 1.414      recomputed 1.414      match
RNO MAE Persistence                                  recorded 2.490      recomputed 2.490      match
RNO MAE Climatology                                  recorded 4.027      recomputed 4.027      match
RNO MAE Mean-bias reference                          recorded 1.500      recomputed 1.500      match
RNO MAE ML-corrected                                 recorded 1.458      recomputed 1.458      match
RNO training kept rows                               recorded 1568       recomputed 1568       match
RNO test paired rows                                 recorded 365        recomputed 365        match
RNO test days dropped                                recorded 0          recomputed 0          match
RNO scored days                                      recorded 365        recomputed 365        match
RNO verdict                                          recorded FAIL       recomputed FAIL       match
-- F94  session39_sealed_test.py  (summary CSV, 4 dp)
EGLC train_rows                                      recorded 1589       recomputed 1589       match
EGLC test_rows                                       recorded 364        recomputed 364        match
EGLC raw_mae                                         recorded 1.2536     recomputed 1.2536     match
EGLC persist_mae                                     recorded 2.0964     recomputed 2.0964     match
EGLC f3_mae                                          recorded 1.0367     recomputed 1.0367     match
EGLC f5_mae                                          recorded 1.0000     recomputed 1.0000     match
EGLC verdict                                         recorded PASS       recomputed PASS       match
LFPG train_rows                                      recorded 1589       recomputed 1589       match
LFPG test_rows                                       recorded 364        recomputed 364        match
LFPG raw_mae                                         recorded 1.3822     recomputed 1.3822     match
LFPG persist_mae                                     recorded 2.3003     recomputed 2.3003     match
LFPG f3_mae                                          recorded 1.1775     recomputed 1.1775     match
LFPG f5_mae                                          recorded 1.1561     recomputed 1.1561     match
LFPG verdict                                         recorded PASS       recomputed PASS       match
DSM train_rows                                       recorded 1590       recomputed 1590       match
DSM test_rows                                        recorded 365        recomputed 365        match
DSM raw_mae                                          recorded 1.7334     recomputed 1.7334     match
DSM persist_mae                                      recorded 4.0029     recomputed 4.0029     match
DSM f3_mae                                           recorded 1.6940     recomputed 1.6940     match
DSM f5_mae                                           recorded 1.6358     recomputed 1.6358     match
DSM verdict                                          recorded PASS       recomputed PASS       match
YSDU train_rows                                      recorded 1573       recomputed 1573       match
YSDU test_rows                                       recorded 356        recomputed 356        match
YSDU raw_mae                                         recorded 1.3167     recomputed 1.3167     match
YSDU persist_mae                                     recorded 2.6686     recomputed 2.6686     match
YSDU f3_mae                                          recorded 1.2834     recomputed 1.2834     match
YSDU f5_mae                                          recorded 1.1786     recomputed 1.1786     match
YSDU verdict                                         recorded PASS       recomputed PASS       match
RNO train_rows                                       recorded 1587       recomputed 1587       match
RNO test_rows                                        recorded 365        recomputed 365        match
RNO raw_mae                                          recorded 1.5116     recomputed 1.5116     match
RNO persist_mae                                      recorded 2.4901     recomputed 2.4901     match
RNO f3_mae                                           recorded 1.4551     recomputed 1.4551     match
RNO f5_mae                                           recorded 1.3460     recomputed 1.3460     match
RNO verdict                                          recorded PASS       recomputed PASS       match
EGLC raw_mae (F94 table, 3 dp)                       recorded 1.254      recomputed 1.254      match
EGLC persist_mae (F94 table, 3 dp)                   recorded 2.096      recomputed 2.096      match
EGLC f3_mae (F94 table, 3 dp)                        recorded 1.037      recomputed 1.037      match
EGLC f5_mae (F94 table, 3 dp)                        recorded 1.000      recomputed 1.000      match
LFPG raw_mae (F94 table, 3 dp)                       recorded 1.382      recomputed 1.382      match
LFPG persist_mae (F94 table, 3 dp)                   recorded 2.300      recomputed 2.300      match
LFPG f3_mae (F94 table, 3 dp)                        recorded 1.177      recomputed 1.177      match
LFPG f5_mae (F94 table, 3 dp)                        recorded 1.156      recomputed 1.156      match
DSM raw_mae (F94 table, 3 dp)                        recorded 1.733      recomputed 1.733      match
DSM persist_mae (F94 table, 3 dp)                    recorded 4.003      recomputed 4.003      match
DSM f3_mae (F94 table, 3 dp)                         recorded 1.694      recomputed 1.694      match
DSM f5_mae (F94 table, 3 dp)                         recorded 1.636      recomputed 1.636      match
YSDU raw_mae (F94 table, 3 dp)                       recorded 1.317      recomputed 1.317      match
YSDU persist_mae (F94 table, 3 dp)                   recorded 2.669      recomputed 2.669      match
YSDU f3_mae (F94 table, 3 dp)                        recorded 1.283      recomputed 1.283      match
YSDU f5_mae (F94 table, 3 dp)                        recorded 1.179      recomputed 1.179      match
RNO raw_mae (F94 table, 3 dp)                        recorded 1.512      recomputed 1.512      match
RNO persist_mae (F94 table, 3 dp)                    recorded 2.490      recomputed 2.490      match
RNO f3_mae (F94 table, 3 dp)                         recorded 1.455      recomputed 1.455      match
RNO f5_mae (F94 table, 3 dp)                         recorded 1.346      recomputed 1.346      match
-- F109  session62_reserved_confirm.py --confirm  (4 dp)
EGLC n_train                                         recorded 1225       recomputed 1225       match
EGLC n_test                                          recorded 364        recomputed 364        match
EGLC no_obs_dropped                                  recorded 1          recomputed 1          match
EGLC no_prev                                         recorded 1          recomputed 1          match
EGLC raw                                             recorded 1.2362     recomputed 1.2362     match
EGLC persist                                         recorded 2.2259     recomputed 2.2259     match
EGLC B                                               recorded 1.0861     recomputed 1.0861     match
EGLC B+DLRT                                          recorded 1.0008     recomputed 1.0008     match
EGLC vs_raw                                          recorded PASS       recomputed PASS       match
EGLC vs_persist                                      recorded PASS       recomputed PASS       match
LFPG n_train                                         recorded 1224       recomputed 1224       match
LFPG n_test                                          recorded 365        recomputed 365        match
LFPG no_obs_dropped                                  recorded 0          recomputed 0          match
LFPG no_prev                                         recorded 0          recomputed 0          match
LFPG raw                                             recorded 1.4091     recomputed 1.4091     match
LFPG persist                                         recorded 2.5233     recomputed 2.5233     match
LFPG B                                               recorded 1.3285     recomputed 1.3285     match
LFPG B+DLRT                                          recorded 1.2369     recomputed 1.2369     match
LFPG vs_raw                                          recorded PASS       recomputed PASS       match
LFPG vs_persist                                      recorded PASS       recomputed PASS       match
DSM n_train                                          recorded 1225       recomputed 1225       match
DSM n_test                                           recorded 365        recomputed 365        match
DSM no_obs_dropped                                   recorded 0          recomputed 0          match
DSM no_prev                                          recorded 0          recomputed 0          match
DSM raw                                              recorded 1.7043     recomputed 1.7043     match
DSM persist                                          recorded 4.1081     recomputed 4.1081     match
DSM B                                                recorded 1.4402     recomputed 1.4402     match
DSM B+DLRT                                           recorded 1.4123     recomputed 1.4123     match
DSM vs_raw                                           recorded PASS       recomputed PASS       match
DSM vs_persist                                       recorded PASS       recomputed PASS       match
YSDU n_train                                         recorded 1213       recomputed 1213       match
YSDU n_test                                          recorded 360        recomputed 360        match
YSDU no_obs_dropped                                  recorded 5          recomputed 5          match
YSDU no_prev                                         recorded 5          recomputed 5          match
YSDU raw                                             recorded 1.4897     recomputed 1.4897     match
YSDU persist                                         recorded 2.5775     recomputed 2.5775     match
YSDU B                                               recorded 1.3030     recomputed 1.3030     match
YSDU B+DLRT                                          recorded 1.2643     recomputed 1.2643     match
YSDU vs_raw                                          recorded PASS       recomputed PASS       match
YSDU vs_persist                                      recorded PASS       recomputed PASS       match
RNO n_train                                          recorded 1222       recomputed 1222       match
RNO n_test                                           recorded 365        recomputed 365        match
RNO no_obs_dropped                                   recorded 0          recomputed 0          match
RNO no_prev                                          recorded 0          recomputed 0          match
RNO raw                                              recorded 1.6135     recomputed 1.6135     match
RNO persist                                          recorded 2.7563     recomputed 2.7563     match
RNO B                                                recorded 1.4272     recomputed 1.4272     match
RNO B+DLRT                                           recorded 1.2742     recomputed 1.2742     match
RNO vs_raw                                           recorded PASS       recomputed PASS       match
RNO vs_persist                                       recorded PASS       recomputed PASS       match
bar verdict                                          recorded ALL FIVE AIRPORTS PASS recomputed ALL FIVE AIRPORTS PASS match
airport-averaged MAE, B+D,L,R,T                      recorded 1.2377     recomputed 1.2377     match
airport-averaged MAE, B                              recorded 1.3170     recomputed 1.3170     match

TOTAL: 163 match, 0 MISMATCH
```

### 3.2 Whole-output comparison

In the clone, `git diff` after all seven runs showed changes in exactly
these committed files and lines, and nothing else:

```
diff --git a/notes/session-07-check-output.txt b/notes/session-07-check-output.txt
-run at        : 2026-08-17 15:45:54 local
+run at        : 2026-09-23 11:43:51 local
diff --git a/notes/session-13-check-output.txt b/notes/session-13-check-output.txt
-run at        : 2026-08-18 01:26:14 local
+run at        : 2026-09-23 11:43:53 local
diff --git a/notes/session-18-check-output.txt b/notes/session-18-check-output.txt
-run at        : 2026-08-18 21:07:40 local
+run at        : 2026-09-23 11:43:54 local
diff --git a/notes/session-24-check-output.txt b/notes/session-24-check-output.txt
-run at        : 2026-08-19 12:26:02 local
+run at        : 2026-09-23 11:43:55 local
diff --git a/notes/session-29-check-output.txt b/notes/session-29-check-output.txt
-run at        : 2026-08-20 12:53:02 local
+run at        : 2026-09-23 11:43:57 local
diff --git a/notes/session40-sealed-test-output.txt b/notes/session40-sealed-test-output.txt
-run at        : 2026-09-12 09:41:21 local
+run at        : 2026-09-23 11:44:02 local
-Wrote summary: /Users/zacharyadams/Coding Projects/MLwx/data/processed/session40_sealed_test_summary.csv
+Wrote summary: /private/tmp/audit68a/clone/data/processed/session40_sealed_test_summary.csv
```

- **Minimal method.** For each of the five scripts, the output file is
  identical to the committed file apart from the `run at` line. The
  captured stdout is identical to the file the script's own `Tee` wrote.
- **F94.** `notes/session40-sealed-test-output.txt` differs only in `run
  at` and in the absolute path printed by `Wrote summary:` (A68a-04).
  `data/processed/session40_sealed_test_summary.csv` is byte-identical
  (`git diff --quiet` passes).
- **F109.** `data/processed/session63_reserved_confirm_grid.csv` is
  byte-identical, at full float precision. The captured stdout, minus the
  `time` lines, is identical to `notes/session-64-confirm-output.txt`.

### 3.3 Writes to committed paths (for triage)

Every write below landed in the clone only. The working repo was not
touched (see the `git status` in section 6).

- `session07_test.py` writes `notes/session-07-check-output.txt`
  (committed). The same pattern holds for `session13_test.py`,
  `session18_test.py`, `session24_test.py` and `session29_test.py`, each
  writing its own `notes/session-NN-check-output.txt` (all committed).
  Each script writes its own session's record, so a re-run in the working
  repo would replace the record with a copy that differs only in the
  timestamp.
- `session39_sealed_test.py` writes `notes/session40-sealed-test-output.txt`
  and `data/processed/session40_sealed_test_summary.csv` (both committed).
  This is already A67-02.
- `session62_reserved_confirm.py --confirm` writes
  `data/processed/session63_reserved_confirm_grid.csv` (committed). This is
  already A67-03. It writes no output text file of its own (A68a-05).

### 3.4 Determinism (read from the code)

All seven scripts pass the same LightGBM settings: `random_state=42`,
`deterministic=True`, `n_jobs=1` (one thread) and `force_row_wise=True`,
with `subsample=1.0` and `colsample_bytree=1.0` (no row or column
sampling). No script uses any other random source (`np.random`,
`random.seed`, shuffling, bagging and `PYTHONHASHSEED` are absent; checked
by grep). Places in the code:

- `session07_test.py:126–130`
- `session13_test.py:137–141`
- `session18_test.py:148–152`
- `session24_test.py:165–169`
- `session29_test.py:174–178`
- `session39_sealed_test.py:140–144`
- `session62_reserved_confirm.py:141–145`

Nothing was re-run to test determinism. That the outputs are identical to
records made weeks apart is consistent with these settings.

---

## 4. Step 3 results — grouped by feature

### 4.1 Setup

- The clone's `data/raw/grib` is a symbolic link (symlink) to the working
  repo's `data/raw/grib/`. The committed decode code opens those files
  read-only (`open(path, "rb")`). No other gitignored raw folder is needed.
  B's decode reads only `data/raw/grib/` plus the tracked
  `session37_elevation_correction_params.csv`.
- Cache before the step: 62,570 files; SHA-256 of the sorted listing (path,
  size, modification time)
  `dc9dff9ac22c0ca843b4372b181a3533e272ae87d29c7a2e825fdab69bd664b7`.
  After the step: 62,570 files, same checksum. **Unchanged.**
- **Code used.** `rebuild_step3.py` (Appendix 7.3) imports the clone's
  `session37_decode.py` (for training and reserved dates, which both sit
  in `grib_features_v16_window.csv`) and `session40_decode.py` (for sealed
  dates). It calls each module's own `decode_row()` once per sampled
  station-day, with the module's own `load_elevation_corrections()`. No
  logic was copied or changed.
- The two modules' `decode_row`, `bilinear_value`, `grib_files_for` and
  `cycle_and_lead` have identical source, and their `AIRPORTS` tables are
  equal. `load_elevation_corrections` differs only in its docstring (an
  AST comparison with the docstring removed gives identical code).
- **Substitutions: none.** None of the nine sample dates is in
  `session37_pull_failures.csv` (24 rows, all for run dates 2022-11-29/30),
  `session40_pull_failures.csv` (0 rows), or either processed drop log
  (`grib_features_v16_window_drops.csv`: DSM 2022-11-30, YSDU 2022-12-01,
  RNO 2022-11-30; sealed: 0 rows). All 45 station-days decoded, and all 45
  have a CSV row.
- **Stored precision.** Every B value column (`temperature_grib_c`,
  `cloud_cover_grib_pct`, `wind_speed_grib_kmh`) has at most 3 decimals in
  both CSVs. The build writes `round(x, 3)`. **Tolerance: the rebuilt
  `round(x, 3)` must equal the stored value exactly.** The bookkeeping
  columns (target_hour, run_date, cycle, lead) are integers or dates and
  must match exactly as strings.

### 4.2 B — per value

```
== target_hour (45 station-days) ==
  training EGLC 2021-03-24  csv        12  rebuilt        12  match
  training LFPG 2021-03-24  csv        12  rebuilt        12  match
  training DSM  2021-03-24  csv        18  rebuilt        18  match
  training YSDU 2021-03-24  csv         2  rebuilt         2  match
  training RNO  2021-03-24  csv        20  rebuilt        20  match
  training EGLC 2022-11-26  csv        12  rebuilt        12  match
  training LFPG 2022-11-26  csv        12  rebuilt        12  match
  training DSM  2022-11-26  csv        18  rebuilt        18  match
  training YSDU 2022-11-26  csv         2  rebuilt         2  match
  training RNO  2022-11-26  csv        20  rebuilt        20  match
  training EGLC 2024-07-31  csv        12  rebuilt        12  match
  training LFPG 2024-07-31  csv        12  rebuilt        12  match
  training DSM  2024-07-31  csv        18  rebuilt        18  match
  training YSDU 2024-07-31  csv         2  rebuilt         2  match
  training RNO  2024-07-31  csv        20  rebuilt        20  match
  reserved EGLC 2024-08-01  csv        12  rebuilt        12  match
  reserved LFPG 2024-08-01  csv        12  rebuilt        12  match
  reserved DSM  2024-08-01  csv        18  rebuilt        18  match
  reserved YSDU 2024-08-01  csv         2  rebuilt         2  match
  reserved RNO  2024-08-01  csv        20  rebuilt        20  match
  reserved EGLC 2025-01-30  csv        12  rebuilt        12  match
  reserved LFPG 2025-01-30  csv        12  rebuilt        12  match
  reserved DSM  2025-01-30  csv        18  rebuilt        18  match
  reserved YSDU 2025-01-30  csv         2  rebuilt         2  match
  reserved RNO  2025-01-30  csv        20  rebuilt        20  match
  reserved EGLC 2025-07-31  csv        12  rebuilt        12  match
  reserved LFPG 2025-07-31  csv        12  rebuilt        12  match
  reserved DSM  2025-07-31  csv        18  rebuilt        18  match
  reserved YSDU 2025-07-31  csv         2  rebuilt         2  match
  reserved RNO  2025-07-31  csv        20  rebuilt        20  match
  sealed   EGLC 2025-08-01  csv        12  rebuilt        12  match
  sealed   LFPG 2025-08-01  csv        12  rebuilt        12  match
  sealed   DSM  2025-08-01  csv        18  rebuilt        18  match
  sealed   YSDU 2025-08-01  csv         2  rebuilt         2  match
  sealed   RNO  2025-08-01  csv        20  rebuilt        20  match
  sealed   EGLC 2026-01-30  csv        12  rebuilt        12  match
  sealed   LFPG 2026-01-30  csv        12  rebuilt        12  match
  sealed   DSM  2026-01-30  csv        18  rebuilt        18  match
  sealed   YSDU 2026-01-30  csv         2  rebuilt         2  match
  sealed   RNO  2026-01-30  csv        20  rebuilt        20  match
  sealed   EGLC 2026-07-31  csv        12  rebuilt        12  match
  sealed   LFPG 2026-07-31  csv        12  rebuilt        12  match
  sealed   DSM  2026-07-31  csv        18  rebuilt        18  match
  sealed   YSDU 2026-07-31  csv         2  rebuilt         2  match
  sealed   RNO  2026-07-31  csv        20  rebuilt        20  match

== run_date (45 station-days) ==
  training EGLC 2021-03-24  csv 2021-03-23  rebuilt 2021-03-23  match
  training LFPG 2021-03-24  csv 2021-03-23  rebuilt 2021-03-23  match
  training DSM  2021-03-24  csv 2021-03-23  rebuilt 2021-03-23  match
  training YSDU 2021-03-24  csv 2021-03-23  rebuilt 2021-03-23  match
  training RNO  2021-03-24  csv 2021-03-23  rebuilt 2021-03-23  match
  training EGLC 2022-11-26  csv 2022-11-25  rebuilt 2022-11-25  match
  training LFPG 2022-11-26  csv 2022-11-25  rebuilt 2022-11-25  match
  training DSM  2022-11-26  csv 2022-11-25  rebuilt 2022-11-25  match
  training YSDU 2022-11-26  csv 2022-11-25  rebuilt 2022-11-25  match
  training RNO  2022-11-26  csv 2022-11-25  rebuilt 2022-11-25  match
  training EGLC 2024-07-31  csv 2024-07-30  rebuilt 2024-07-30  match
  training LFPG 2024-07-31  csv 2024-07-30  rebuilt 2024-07-30  match
  training DSM  2024-07-31  csv 2024-07-30  rebuilt 2024-07-30  match
  training YSDU 2024-07-31  csv 2024-07-30  rebuilt 2024-07-30  match
  training RNO  2024-07-31  csv 2024-07-30  rebuilt 2024-07-30  match
  reserved EGLC 2024-08-01  csv 2024-07-31  rebuilt 2024-07-31  match
  reserved LFPG 2024-08-01  csv 2024-07-31  rebuilt 2024-07-31  match
  reserved DSM  2024-08-01  csv 2024-07-31  rebuilt 2024-07-31  match
  reserved YSDU 2024-08-01  csv 2024-07-31  rebuilt 2024-07-31  match
  reserved RNO  2024-08-01  csv 2024-07-31  rebuilt 2024-07-31  match
  reserved EGLC 2025-01-30  csv 2025-01-29  rebuilt 2025-01-29  match
  reserved LFPG 2025-01-30  csv 2025-01-29  rebuilt 2025-01-29  match
  reserved DSM  2025-01-30  csv 2025-01-29  rebuilt 2025-01-29  match
  reserved YSDU 2025-01-30  csv 2025-01-29  rebuilt 2025-01-29  match
  reserved RNO  2025-01-30  csv 2025-01-29  rebuilt 2025-01-29  match
  reserved EGLC 2025-07-31  csv 2025-07-30  rebuilt 2025-07-30  match
  reserved LFPG 2025-07-31  csv 2025-07-30  rebuilt 2025-07-30  match
  reserved DSM  2025-07-31  csv 2025-07-30  rebuilt 2025-07-30  match
  reserved YSDU 2025-07-31  csv 2025-07-30  rebuilt 2025-07-30  match
  reserved RNO  2025-07-31  csv 2025-07-30  rebuilt 2025-07-30  match
  sealed   EGLC 2025-08-01  csv 2025-07-31  rebuilt 2025-07-31  match
  sealed   LFPG 2025-08-01  csv 2025-07-31  rebuilt 2025-07-31  match
  sealed   DSM  2025-08-01  csv 2025-07-31  rebuilt 2025-07-31  match
  sealed   YSDU 2025-08-01  csv 2025-07-31  rebuilt 2025-07-31  match
  sealed   RNO  2025-08-01  csv 2025-07-31  rebuilt 2025-07-31  match
  sealed   EGLC 2026-01-30  csv 2026-01-29  rebuilt 2026-01-29  match
  sealed   LFPG 2026-01-30  csv 2026-01-29  rebuilt 2026-01-29  match
  sealed   DSM  2026-01-30  csv 2026-01-29  rebuilt 2026-01-29  match
  sealed   YSDU 2026-01-30  csv 2026-01-29  rebuilt 2026-01-29  match
  sealed   RNO  2026-01-30  csv 2026-01-29  rebuilt 2026-01-29  match
  sealed   EGLC 2026-07-31  csv 2026-07-30  rebuilt 2026-07-30  match
  sealed   LFPG 2026-07-31  csv 2026-07-30  rebuilt 2026-07-30  match
  sealed   DSM  2026-07-31  csv 2026-07-30  rebuilt 2026-07-30  match
  sealed   YSDU 2026-07-31  csv 2026-07-30  rebuilt 2026-07-30  match
  sealed   RNO  2026-07-31  csv 2026-07-30  rebuilt 2026-07-30  match

== cycle (45 station-days) ==
  training EGLC 2021-03-24  csv        12  rebuilt        12  match
  training LFPG 2021-03-24  csv        12  rebuilt        12  match
  training DSM  2021-03-24  csv        18  rebuilt        18  match
  training YSDU 2021-03-24  csv         0  rebuilt         0  match
  training RNO  2021-03-24  csv        18  rebuilt        18  match
  training EGLC 2022-11-26  csv        12  rebuilt        12  match
  training LFPG 2022-11-26  csv        12  rebuilt        12  match
  training DSM  2022-11-26  csv        18  rebuilt        18  match
  training YSDU 2022-11-26  csv         0  rebuilt         0  match
  training RNO  2022-11-26  csv        18  rebuilt        18  match
  training EGLC 2024-07-31  csv        12  rebuilt        12  match
  training LFPG 2024-07-31  csv        12  rebuilt        12  match
  training DSM  2024-07-31  csv        18  rebuilt        18  match
  training YSDU 2024-07-31  csv         0  rebuilt         0  match
  training RNO  2024-07-31  csv        18  rebuilt        18  match
  reserved EGLC 2024-08-01  csv        12  rebuilt        12  match
  reserved LFPG 2024-08-01  csv        12  rebuilt        12  match
  reserved DSM  2024-08-01  csv        18  rebuilt        18  match
  reserved YSDU 2024-08-01  csv         0  rebuilt         0  match
  reserved RNO  2024-08-01  csv        18  rebuilt        18  match
  reserved EGLC 2025-01-30  csv        12  rebuilt        12  match
  reserved LFPG 2025-01-30  csv        12  rebuilt        12  match
  reserved DSM  2025-01-30  csv        18  rebuilt        18  match
  reserved YSDU 2025-01-30  csv         0  rebuilt         0  match
  reserved RNO  2025-01-30  csv        18  rebuilt        18  match
  reserved EGLC 2025-07-31  csv        12  rebuilt        12  match
  reserved LFPG 2025-07-31  csv        12  rebuilt        12  match
  reserved DSM  2025-07-31  csv        18  rebuilt        18  match
  reserved YSDU 2025-07-31  csv         0  rebuilt         0  match
  reserved RNO  2025-07-31  csv        18  rebuilt        18  match
  sealed   EGLC 2025-08-01  csv        12  rebuilt        12  match
  sealed   LFPG 2025-08-01  csv        12  rebuilt        12  match
  sealed   DSM  2025-08-01  csv        18  rebuilt        18  match
  sealed   YSDU 2025-08-01  csv         0  rebuilt         0  match
  sealed   RNO  2025-08-01  csv        18  rebuilt        18  match
  sealed   EGLC 2026-01-30  csv        12  rebuilt        12  match
  sealed   LFPG 2026-01-30  csv        12  rebuilt        12  match
  sealed   DSM  2026-01-30  csv        18  rebuilt        18  match
  sealed   YSDU 2026-01-30  csv         0  rebuilt         0  match
  sealed   RNO  2026-01-30  csv        18  rebuilt        18  match
  sealed   EGLC 2026-07-31  csv        12  rebuilt        12  match
  sealed   LFPG 2026-07-31  csv        12  rebuilt        12  match
  sealed   DSM  2026-07-31  csv        18  rebuilt        18  match
  sealed   YSDU 2026-07-31  csv         0  rebuilt         0  match
  sealed   RNO  2026-07-31  csv        18  rebuilt        18  match

== lead (45 station-days) ==
  training EGLC 2021-03-24  csv        24  rebuilt        24  match
  training LFPG 2021-03-24  csv        24  rebuilt        24  match
  training DSM  2021-03-24  csv        24  rebuilt        24  match
  training YSDU 2021-03-24  csv        26  rebuilt        26  match
  training RNO  2021-03-24  csv        26  rebuilt        26  match
  training EGLC 2022-11-26  csv        24  rebuilt        24  match
  training LFPG 2022-11-26  csv        24  rebuilt        24  match
  training DSM  2022-11-26  csv        24  rebuilt        24  match
  training YSDU 2022-11-26  csv        26  rebuilt        26  match
  training RNO  2022-11-26  csv        26  rebuilt        26  match
  training EGLC 2024-07-31  csv        24  rebuilt        24  match
  training LFPG 2024-07-31  csv        24  rebuilt        24  match
  training DSM  2024-07-31  csv        24  rebuilt        24  match
  training YSDU 2024-07-31  csv        26  rebuilt        26  match
  training RNO  2024-07-31  csv        26  rebuilt        26  match
  reserved EGLC 2024-08-01  csv        24  rebuilt        24  match
  reserved LFPG 2024-08-01  csv        24  rebuilt        24  match
  reserved DSM  2024-08-01  csv        24  rebuilt        24  match
  reserved YSDU 2024-08-01  csv        26  rebuilt        26  match
  reserved RNO  2024-08-01  csv        26  rebuilt        26  match
  reserved EGLC 2025-01-30  csv        24  rebuilt        24  match
  reserved LFPG 2025-01-30  csv        24  rebuilt        24  match
  reserved DSM  2025-01-30  csv        24  rebuilt        24  match
  reserved YSDU 2025-01-30  csv        26  rebuilt        26  match
  reserved RNO  2025-01-30  csv        26  rebuilt        26  match
  reserved EGLC 2025-07-31  csv        24  rebuilt        24  match
  reserved LFPG 2025-07-31  csv        24  rebuilt        24  match
  reserved DSM  2025-07-31  csv        24  rebuilt        24  match
  reserved YSDU 2025-07-31  csv        26  rebuilt        26  match
  reserved RNO  2025-07-31  csv        26  rebuilt        26  match
  sealed   EGLC 2025-08-01  csv        24  rebuilt        24  match
  sealed   LFPG 2025-08-01  csv        24  rebuilt        24  match
  sealed   DSM  2025-08-01  csv        24  rebuilt        24  match
  sealed   YSDU 2025-08-01  csv        26  rebuilt        26  match
  sealed   RNO  2025-08-01  csv        26  rebuilt        26  match
  sealed   EGLC 2026-01-30  csv        24  rebuilt        24  match
  sealed   LFPG 2026-01-30  csv        24  rebuilt        24  match
  sealed   DSM  2026-01-30  csv        24  rebuilt        24  match
  sealed   YSDU 2026-01-30  csv        26  rebuilt        26  match
  sealed   RNO  2026-01-30  csv        26  rebuilt        26  match
  sealed   EGLC 2026-07-31  csv        24  rebuilt        24  match
  sealed   LFPG 2026-07-31  csv        24  rebuilt        24  match
  sealed   DSM  2026-07-31  csv        24  rebuilt        24  match
  sealed   YSDU 2026-07-31  csv        26  rebuilt        26  match
  sealed   RNO  2026-07-31  csv        26  rebuilt        26  match

== temperature_grib_c (45 station-days) ==
  training EGLC 2021-03-24  csv    11.198  rebuilt    11.198  match
  training LFPG 2021-03-24  csv    14.007  rebuilt    14.007  match
  training DSM  2021-03-24  csv     6.523  rebuilt     6.523  match
  training YSDU 2021-03-24  csv     23.54  rebuilt     23.54  match
  training RNO  2021-03-24  csv     8.754  rebuilt     8.754  match
  training EGLC 2022-11-26  csv    12.158  rebuilt    12.158  match
  training LFPG 2022-11-26  csv     9.842  rebuilt     9.842  match
  training DSM  2022-11-26  csv    10.384  rebuilt    10.384  match
  training YSDU 2022-11-26  csv    27.797  rebuilt    27.797  match
  training RNO  2022-11-26  csv     9.203  rebuilt     9.203  match
  training EGLC 2024-07-31  csv    27.384  rebuilt    27.384  match
  training LFPG 2024-07-31  csv    24.269  rebuilt    24.269  match
  training DSM  2024-07-31  csv    33.785  rebuilt    33.785  match
  training YSDU 2024-07-31  csv    13.212  rebuilt    13.212  match
  training RNO  2024-07-31  csv    32.415  rebuilt    32.415  match
  reserved EGLC 2024-08-01  csv    27.041  rebuilt    27.041  match
  reserved LFPG 2024-08-01  csv    28.629  rebuilt    28.629  match
  reserved DSM  2024-08-01  csv    27.538  rebuilt    27.538  match
  reserved YSDU 2024-08-01  csv    14.112  rebuilt    14.112  match
  reserved RNO  2024-08-01  csv    34.169  rebuilt    34.169  match
  reserved EGLC 2025-01-30  csv     6.517  rebuilt     6.517  match
  reserved LFPG 2025-01-30  csv     5.923  rebuilt     5.923  match
  reserved DSM  2025-01-30  csv     8.765  rebuilt     8.765  match
  reserved YSDU 2025-01-30  csv    35.518  rebuilt    35.518  match
  reserved RNO  2025-01-30  csv     8.729  rebuilt     8.729  match
  reserved EGLC 2025-07-31  csv    20.349  rebuilt    20.349  match
  reserved LFPG 2025-07-31  csv    25.463  rebuilt    25.463  match
  reserved DSM  2025-07-31  csv    22.863  rebuilt    22.863  match
  reserved YSDU 2025-07-31  csv    13.579  rebuilt    13.579  match
  reserved RNO  2025-07-31  csv     28.07  rebuilt     28.07  match
  sealed   EGLC 2025-08-01  csv    19.695  rebuilt    19.695  match
  sealed   LFPG 2025-08-01  csv     23.34  rebuilt     23.34  match
  sealed   DSM  2025-08-01  csv    21.517  rebuilt    21.517  match
  sealed   YSDU 2025-08-01  csv    14.327  rebuilt    14.327  match
  sealed   RNO  2025-08-01  csv    29.216  rebuilt    29.216  match
  sealed   EGLC 2026-01-30  csv     9.459  rebuilt     9.459  match
  sealed   LFPG 2026-01-30  csv     8.262  rebuilt     8.262  match
  sealed   DSM  2026-01-30  csv   -11.131  rebuilt   -11.131  match
  sealed   YSDU 2026-01-30  csv    38.235  rebuilt    38.235  match
  sealed   RNO  2026-01-30  csv    12.709  rebuilt    12.709  match
  sealed   EGLC 2026-07-31  csv    24.743  rebuilt    24.743  match
  sealed   LFPG 2026-07-31  csv     29.04  rebuilt     29.04  match
  sealed   DSM  2026-07-31  csv    25.883  rebuilt    25.883  match
  sealed   YSDU 2026-07-31  csv    15.183  rebuilt    15.183  match
  sealed   RNO  2026-07-31  csv    34.043  rebuilt    34.043  match

== cloud_cover_grib_pct (45 station-days) ==
  training EGLC 2021-03-24  csv     100.0  rebuilt     100.0  match
  training LFPG 2021-03-24  csv    40.058  rebuilt    40.058  match
  training DSM  2021-03-24  csv     100.0  rebuilt     100.0  match
  training YSDU 2021-03-24  csv    34.456  rebuilt    34.456  match
  training RNO  2021-03-24  csv     100.0  rebuilt     100.0  match
  training EGLC 2022-11-26  csv    95.277  rebuilt    95.277  match
  training LFPG 2022-11-26  csv    98.357  rebuilt    98.357  match
  training DSM  2022-11-26  csv    99.713  rebuilt    99.713  match
  training YSDU 2022-11-26  csv       0.0  rebuilt       0.0  match
  training RNO  2022-11-26  csv      2.11  rebuilt      2.11  match
  training EGLC 2024-07-31  csv    13.267  rebuilt    13.267  match
  training LFPG 2024-07-31  csv    74.838  rebuilt    74.838  match
  training DSM  2024-07-31  csv       0.0  rebuilt       0.0  match
  training YSDU 2024-07-31  csv       0.0  rebuilt       0.0  match
  training RNO  2024-07-31  csv       0.0  rebuilt       0.0  match
  reserved EGLC 2024-08-01  csv     9.301  rebuilt     9.301  match
  reserved LFPG 2024-08-01  csv    16.805  rebuilt    16.805  match
  reserved DSM  2024-08-01  csv     4.203  rebuilt     4.203  match
  reserved YSDU 2024-08-01  csv       0.0  rebuilt       0.0  match
  reserved RNO  2024-08-01  csv     6.997  rebuilt     6.997  match
  reserved EGLC 2025-01-30  csv       0.0  rebuilt       0.0  match
  reserved LFPG 2025-01-30  csv     100.0  rebuilt     100.0  match
  reserved DSM  2025-01-30  csv    53.804  rebuilt    53.804  match
  reserved YSDU 2025-01-30  csv     0.177  rebuilt     0.177  match
  reserved RNO  2025-01-30  csv       0.0  rebuilt       0.0  match
  reserved EGLC 2025-07-31  csv     100.0  rebuilt     100.0  match
  reserved LFPG 2025-07-31  csv     100.0  rebuilt     100.0  match
  reserved DSM  2025-07-31  csv     3.919  rebuilt     3.919  match
  reserved YSDU 2025-07-31  csv     100.0  rebuilt     100.0  match
  reserved RNO  2025-07-31  csv     3.021  rebuilt     3.021  match
  sealed   EGLC 2025-08-01  csv    71.139  rebuilt    71.139  match
  sealed   LFPG 2025-08-01  csv    87.357  rebuilt    87.357  match
  sealed   DSM  2025-08-01  csv    43.777  rebuilt    43.777  match
  sealed   YSDU 2025-08-01  csv    22.572  rebuilt    22.572  match
  sealed   RNO  2025-08-01  csv      2.52  rebuilt      2.52  match
  sealed   EGLC 2026-01-30  csv     100.0  rebuilt     100.0  match
  sealed   LFPG 2026-01-30  csv    96.198  rebuilt    96.198  match
  sealed   DSM  2026-01-30  csv     100.0  rebuilt     100.0  match
  sealed   YSDU 2026-01-30  csv       5.0  rebuilt       5.0  match
  sealed   RNO  2026-01-30  csv    98.568  rebuilt    98.568  match
  sealed   EGLC 2026-07-31  csv     0.398  rebuilt     0.398  match
  sealed   LFPG 2026-07-31  csv    27.639  rebuilt    27.639  match
  sealed   DSM  2026-07-31  csv    53.141  rebuilt    53.141  match
  sealed   YSDU 2026-07-31  csv       0.0  rebuilt       0.0  match
  sealed   RNO  2026-07-31  csv       0.0  rebuilt       0.0  match

== wind_speed_grib_kmh (45 station-days) ==
  training EGLC 2021-03-24  csv    15.432  rebuilt    15.432  match
  training LFPG 2021-03-24  csv     11.16  rebuilt     11.16  match
  training DSM  2021-03-24  csv    24.031  rebuilt    24.031  match
  training YSDU 2021-03-24  csv    21.862  rebuilt    21.862  match
  training RNO  2021-03-24  csv      3.09  rebuilt      3.09  match
  training EGLC 2022-11-26  csv    19.447  rebuilt    19.447  match
  training LFPG 2022-11-26  csv    12.552  rebuilt    12.552  match
  training DSM  2022-11-26  csv    21.823  rebuilt    21.823  match
  training YSDU 2022-11-26  csv     5.222  rebuilt     5.222  match
  training RNO  2022-11-26  csv     6.192  rebuilt     6.192  match
  training EGLC 2024-07-31  csv    15.614  rebuilt    15.614  match
  training LFPG 2024-07-31  csv     6.339  rebuilt     6.339  match
  training DSM  2024-07-31  csv    16.056  rebuilt    16.056  match
  training YSDU 2024-07-31  csv     8.457  rebuilt     8.457  match
  training RNO  2024-07-31  csv    12.051  rebuilt    12.051  match
  reserved EGLC 2024-08-01  csv     9.185  rebuilt     9.185  match
  reserved LFPG 2024-08-01  csv    14.183  rebuilt    14.183  match
  reserved DSM  2024-08-01  csv    24.456  rebuilt    24.456  match
  reserved YSDU 2024-08-01  csv     6.718  rebuilt     6.718  match
  reserved RNO  2024-08-01  csv     9.324  rebuilt     9.324  match
  reserved EGLC 2025-01-30  csv    14.927  rebuilt    14.927  match
  reserved LFPG 2025-01-30  csv    20.268  rebuilt    20.268  match
  reserved DSM  2025-01-30  csv     7.564  rebuilt     7.564  match
  reserved YSDU 2025-01-30  csv    12.254  rebuilt    12.254  match
  reserved RNO  2025-01-30  csv      1.37  rebuilt      1.37  match
  reserved EGLC 2025-07-31  csv    12.932  rebuilt    12.932  match
  reserved LFPG 2025-07-31  csv    14.133  rebuilt    14.133  match
  reserved DSM  2025-07-31  csv     21.09  rebuilt     21.09  match
  reserved YSDU 2025-07-31  csv    13.905  rebuilt    13.905  match
  reserved RNO  2025-07-31  csv     6.365  rebuilt     6.365  match
  sealed   EGLC 2025-08-01  csv    17.279  rebuilt    17.279  match
  sealed   LFPG 2025-08-01  csv    20.418  rebuilt    20.418  match
  sealed   DSM  2025-08-01  csv    15.826  rebuilt    15.826  match
  sealed   YSDU 2025-08-01  csv    16.802  rebuilt    16.802  match
  sealed   RNO  2025-08-01  csv     9.827  rebuilt     9.827  match
  sealed   EGLC 2026-01-30  csv     11.22  rebuilt     11.22  match
  sealed   LFPG 2026-01-30  csv    16.465  rebuilt    16.465  match
  sealed   DSM  2026-01-30  csv    20.967  rebuilt    20.967  match
  sealed   YSDU 2026-01-30  csv     5.497  rebuilt     5.497  match
  sealed   RNO  2026-01-30  csv     2.237  rebuilt     2.237  match
  sealed   EGLC 2026-07-31  csv    10.537  rebuilt    10.537  match
  sealed   LFPG 2026-07-31  csv    10.257  rebuilt    10.257  match
  sealed   DSM  2026-07-31  csv    12.282  rebuilt    12.282  match
  sealed   YSDU 2026-07-31  csv    14.057  rebuilt    14.057  match
  sealed   RNO  2026-07-31  csv     8.054  rebuilt     8.054  match

missing / not decodable: none
B TOTAL: 315 match, 0 MISMATCH
```

### 4.3 Elevation constants — terrain interpolation check

`session37_elevation_fix.py`'s `main()` always re-fetches the terrain
(HGT:surface) message over the network for four airports (A68a-02), so it
was not run. As a partial check that needs no network, the harness called
that script's own `bilinear_value()` on the tracked terrain files
(`data/raw/diagnostics/session37/…_hgt_surface_{EGLC,LFPG,DSM,YSDU}_diagnostic.grib2`
and `data/raw/diagnostics/session36/…_RNO_diagnostic.grib2`). It compared
the result, rounded to the params CSV's 2 decimals, with `orog_interp_m`
in `session37_elevation_correction_params.csv`. The lapse-rate fit and the
`correction_c` arithmetic in `main()` were **not** re-run. `decode_row()`
above used the committed `correction_c` values as built.

```
== elevation-fix terrain check (committed bilinear_value on tracked HGT files) ==
  EGLC file gfs_20250610_t12z_f024_hgt_surface_EGLC_diagnostic.grib2  csv orog_interp_m    37.47  rebuilt    37.47  match
  LFPG file gfs_20250610_t12z_f024_hgt_surface_LFPG_diagnostic.grib2  csv orog_interp_m    86.15  rebuilt    86.15  match
  DSM  file gfs_20250610_t18z_f024_hgt_surface_DSM_diagnostic.grib2  csv orog_interp_m   270.11  rebuilt   270.11  match
  YSDU file gfs_20250610_t00z_f026_hgt_surface_YSDU_diagnostic.grib2  csv orog_interp_m   312.12  rebuilt   312.12  match
  RNO  file gfs_20250610_t18z_f026_hgt_surface_RNO_diagnostic.grib2  csv orog_interp_m  1619.08  rebuilt  1619.08  match
```

### 4.4 Season features (date arithmetic, not built from the GRIB)

`season_sin` and `season_cos` are not stored in any processed CSV. A
header scan of all 48 files under `data/processed/` found no `season`
column. They are computed at scoring time from the date. There is no
stored value to compare against, so the check compares the two committed
scoring paths on the nine sample dates: `session39_sealed_test.features_5()`
(F94) and `session62_reserved_confirm.make_feature_vector()` (F109).
`year_fraction()` has identical source in both. Step 2's exact
reproductions already cover these values end to end.

```
== season features: session39 features_5 vs session62 make_feature_vector ==
  year_fraction() source identical in s39 and s62: True
  training 2021-03-24  year_fraction 0.224658  s39 sin +0.987349 cos +0.158559  s62 sin +0.987349 cos +0.158559  match
  training 2022-11-26  year_fraction 0.901370  s39 sin -0.580800 cos +0.814046  s62 sin -0.580800 cos +0.814046  match
  training 2024-07-31  year_fraction 0.579235  s39 sin -0.477536 cos -0.878612  s62 sin -0.477536 cos -0.878612  match
  reserved 2024-08-01  year_fraction 0.581967  s39 sin -0.492548 cos -0.870285  s62 sin -0.492548 cos -0.870285  match
  reserved 2025-01-30  year_fraction 0.079452  s39 sin +0.478734 cos +0.877960  s62 sin +0.478734 cos +0.877960  match
  reserved 2025-07-31  year_fraction 0.578082  s39 sin -0.471160 cos -0.882048  s62 sin -0.471160 cos -0.882048  match
  sealed   2025-08-01  year_fraction 0.580822  s39 sin -0.486273 cos -0.873807  s62 sin -0.486273 cos -0.873807  match
  sealed   2026-01-30  year_fraction 0.079452  s39 sin +0.478734 cos +0.877960  s62 sin +0.478734 cos +0.877960  match
  sealed   2026-07-31  year_fraction 0.578082  s39 sin -0.471160 cos -0.882048  s62 sin -0.471160 cos -0.882048  match
SEASON TOTAL: 9 match, 0 MISMATCH
```

### 4.5 L, D, T and R — not rebuilt (option b)

- **What was checked.** The local cache holds only B's four variables:
  7,821 files each of `tmp2m`, `tcdc`, `ugrd10m` and `vgrd10m`. No
  pressure-level temperature, dew point, sea-level pressure or shortwave
  radiation GRIB exists anywhere under `data/raw/`. The only other tracked
  `.grib2` files are session 35/36/37 diagnostic samples.
- **Why they cannot be rebuilt.** Each family's `process_combo()` fetches a
  byte range over the network, writes it to a scratch file, decodes it and
  deletes it in the same function:
  - `session49_upper_air_pull.py:208` (L)
  - `session51_moisture_pull.py:215` (D)
  - `session53_pressure_pull.py:349` (T)
  - `session55_radiation_pull.py:469` (R)

  Their docstrings say "No raw GRIB2 bytes survive past this function".
  `session63_reserved_year_build.py:147–227` calls those same functions for
  the reserved year.
- **What this means.** Decode cannot be separated from fetch without
  editing the scripts, and fetch needs the network, which this session
  forbids. Option (a), a full build, also needs the network. So option (b)
  was taken: **L, D, T and R are recorded as not rebuilt, for all three
  windows.** See A68a-01.

---

## 5. Findings

A68a-01 | should-fix | scripts/session49_upper_air_pull.py:208, scripts/session51_moisture_pull.py:215, scripts/session53_pressure_pull.py:349, scripts/session55_radiation_pull.py:469 (all reused by scripts/session63_reserved_year_build.py:147–227)
evidence: The four added features behind F109 (L, D, T, R) cannot be checked against their raw source offline. Each `process_combo()` fetches, decodes and deletes the GRIB bytes in one function ("No raw GRIB2 bytes survive past this function"; the session 51 docstring gives disk space as the reason, citing F98). The local cache holds only B's four variables. So Step 3 could not rebuild a single L, D, T or R value, and this session's evidence that the processed family CSVs are correct builds rests only on (a) Step 2's exact reproduction from those CSVs and (b) the committed pull manifests (0 FAIL rows, A67 Step 1.5). Neither shows that a value in `session{49,51,53,55}_*_with_*.csv` or `session63_reserved_window_with_*.csv` equals what the GRIB holds. B, by contrast, was rebuilt exactly (315 of 315).
suggested fix: owner decision. One option is a later session with network permission. It would call each family's committed `process_combo()` for the same 45 sampled station-days (Step 3.2's rule), without writing any processed file, and compare with the stored values. This needs no script edit, since `process_combo()` is importable and returns values. It is a new network fetch from a live archive, so the pull date should be recorded (SPEC 2.3).

A68a-02 | uncertain | scripts/session37_elevation_fix.py:187–196, 246
evidence: `main()` fetches the HGT:surface message for EGLC, LFPG, DSM and YSDU over the network every time it runs, even though the four files it would write are already tracked under `data/raw/diagnostics/session37/`. It then overwrites those files, their sidecars and `session37_elevation_correction_params.csv` (line 246). So the five frozen elevation constants (D48.3) cannot be re-derived offline, and a re-run in the working repo would overwrite tracked raw files. This session checked only the terrain interpolation step, by calling the script's own `bilinear_value()` on the tracked files (5 of 5 match to the CSV's 2 decimals). The lapse-rate fit and the `correction_c` values were not re-derived. The constants are frozen by D48.3 and have been used unchanged since, so this may not matter. Whether a full offline re-derivation is wanted is the owner's call.
suggested fix: none needed if the constants stay frozen. If a re-derivation is wanted: a harness that imports the script and calls its own `evaluate()` and the gap arithmetic on the tracked files, run in a clone.

A68a-03 | cosmetic | scripts/session07_test.py:782–783 (and the matching MAE-table print in session13/18/24/29_test.py)
evidence: D60.2's pre-registered expectation is a match "to the fourth decimal place". The minimal-method scripts print MAE to three decimals, and F16/F30/F47/F64/F82 record three. So for those five airports the fourth decimal could not be read from a single unchanged run. The check was made at three decimals, and on the whole output (identical to the committed record apart from the timestamp). F94's summary CSV (4 dp) and F109 (4 dp and a full-precision grid CSV) were checked at four decimals and at full precision respectively.
suggested fix: none needed. Note it at triage so "fourth decimal" is read as "recorded precision" for the minimal method.

A68a-04 | cosmetic | scripts/session39_sealed_test.py:485 (frozen); notes/session40-sealed-test-output.txt:173
evidence: `print(f"\nWrote summary: {SUMMARY_CSV}")` prints an absolute path, so the committed F94 record contains the machine's home-directory path (`/Users/zacharyadams/Coding Projects/MLwx/...`). Any run elsewhere changes that line. In this session's clone run it read `/private/tmp/audit68a/clone/...`, the only non-timestamp difference in any of the seven outputs.
suggested fix: frozen — owner decision. No change needed for correctness. If the output file is ever regenerated, a relative path would keep it machine-neutral.

A68a-05 | cosmetic | scripts/session62_reserved_confirm.py:646–737 (frozen)
evidence: `run_confirm()` prints its result to stdout only. Unlike `preflight()` (`OUT_PREFLIGHT`, `Tee`), it writes no output text file. The committed record of the look, `notes/session-64-confirm-output.txt`, was therefore captured outside the script in session 64. This session's captured stdout is identical to it. The record reproduces, but how it was made is not visible in the script.
suggested fix: frozen — owner decision. A sentence in DECISIONS noting that the confirm output file was captured outside the script is enough.

A68a-06 | cosmetic | .gitignore:36
evidence: the rule `data/raw/grib/` has a trailing slash, so it matches a directory only. When the cache path is a symbolic link, as in this session's clone, git shows it as untracked (`?? data/raw/grib`) instead of ignoring it. A later `git add -A` in a checkout set up that way would commit the link. It would not commit the data, but it would commit a machine-specific absolute path.
suggested fix: change the rule to `data/raw/grib` (no trailing slash), which matches both. This fits alongside A67-08's `.gitignore` edits.

---

## 6. Clean checks

- **Step 0.** `git status --porcelain` at start: only `?? docs/session-68a.md`.
- **Step 0 gate.** Searched CLAUDE.md, SPEC.md and live DECISIONS.md (grep for re-run, only once, exactly once, run once, single or one look, re-judge, re-test, re-score, not reused). Also opened the archived D21.10, D31.10, D35.10, D39.10, D44.10 and D48.13 by number. No other rule text bears on a re-run. SPEC section 2 (2.1a–2.1d, 2.2, 2.3, 2.4) forbids nothing here. The run changes no split, fills no gap, touches no raw file, and moves no bar.
- **Environment.** Python 3.12.2. `pip freeze` equals `requirements.txt`'s 19 pins exactly. The libomp restart shim loaded LightGBM first time in every script run.
- **Step 2.** 7 of 7 scripts exited 0, with no guard tripped. That includes F94's training-row reconciliation, sealed-row ceiling and in-window assertions, and F109's reserved-year and gap guards.
- **Step 2.** 163 of 163 figures match. All outputs are identical apart from timestamps (and A68a-04's path). Both result CSVs are byte-identical.
- **Step 3.** 315 of 315 B values match. 5 of 5 terrain interpolations match. 9 of 9 season-feature dates agree. No substitutions were needed.
- **Step 3.** The working repo's cache is unchanged (count and checksum). No `__pycache__` file was written in the working repo this session (`find scripts/__pycache__ -newer docs/session-68a.md` is empty).
- **Working repo writes.** Only the three permitted files: `notes/audit-session-68a.md` (new), `DECISIONS.md` (D61 appended) and `STATUS.md` (overwritten).
- **One harness hiccup, not a project finding.** The first run of `rebuild_step3.py` was wrapped in `/usr/bin/time`. That is a macOS system-protected binary, so it strips `DYLD_LIBRARY_PATH`. The harness therefore stopped at the LightGBM import in its season section, after the B and terrain sections had finished and printed. The season section was split out unchanged into `season_step3.py` and run without the wrapper. B and the terrain check were not re-run. This harness decodes and compares only: it fits nothing, scores nothing, and is not one of Step 2's once-only reproductions.

**Archive candidates (for triage; no move made, per D61.6).** By the D46
criterion:
- **D49, F95 and D50** (the session 43–45 consolidation records). Their
  headlines are in SPEC §7 and RESULTS §5. STATUS.md no longer cites them,
  and no live open question needs their wording.
- **F94** stays live for now. 68b's review of `session39_sealed_test.py`
  (its persistence day-set note, Task 2) may need its exact wording.
- **D61** stays live: it defines 68b's scope.

---

## 7. Appendix — check scripts and raw output

All scripts live in `/tmp/audit68a/`. Raw run outputs are
`/tmp/audit68a/run_<script>.txt`. The clone is `/tmp/audit68a/clone`.

### 7.1 Shell steps

````bash
# Session 68a -- shell steps. Working repo = "/Users/zacharyadams/Coding Projects/MLwx".
# Step 0
git status --porcelain
grep -n -i -E "re-run|rerun|re-ran|only once|exactly once|run once|once only|single authorised|single look|one look|one authorised|re-judg|re-test|re-score|never re|not reused" CLAUDE.md SPEC.md DECISIONS.md
# (archived D21.10, D31.10, D35.10, D39.10, D44.10, D48.13 opened by number with grep -n + sed -n)
# Step 2.1 clone and environment
mkdir -p /tmp/audit68a && cd /tmp/audit68a
git clone -q "/Users/zacharyadams/Coding Projects/MLwx" clone && cd clone
git rev-parse HEAD                      # 9dc426c3ff2422ae4b1bfeba1a11185ecc708f83
python3 --version                       # Python 3.12.2
python3 -m venv .venv && .venv/bin/python -m pip install -q -r requirements.txt
.venv/bin/python -m pip freeze > /tmp/audit68a/pip_freeze.txt
grep -E '^[a-zA-Z].*==' requirements.txt | sort -f > /tmp/audit68a/pins.txt
sort -f /tmp/audit68a/pip_freeze.txt | diff /tmp/audit68a/pins.txt - && echo "PINS MATCH FREEZE"
# Step 2.3 runs, once each, in order, from the clone root
for s in session07_test session13_test session18_test session24_test session29_test; do
  /usr/bin/time -p .venv/bin/python scripts/$s.py > /tmp/audit68a/run_$s.txt 2>&1; done
/usr/bin/time -p .venv/bin/python scripts/session39_sealed_test.py > /tmp/audit68a/run_session39_sealed_test.txt 2>&1
/usr/bin/time -p .venv/bin/python scripts/session62_reserved_confirm.py --confirm > /tmp/audit68a/run_session62_confirm.txt 2>&1
# Step 2.4 whole-output comparison (in the clone)
git status --porcelain; git diff --stat; git diff -U0
git diff --quiet HEAD -- data/processed/session40_sealed_test_summary.csv data/processed/session63_reserved_confirm_grid.csv && echo CSVS_IDENTICAL
grep -v -E "^(real|user|sys) " /tmp/audit68a/run_session62_confirm.txt | diff - "<repo>/notes/session-64-confirm-output.txt" && echo CONFIRM_OUTPUT_IDENTICAL
for s in 07 13 18 24 29; do grep -v -E "^(real|user|sys) " /tmp/audit68a/run_session${s}_test.txt | diff -q - notes/session-$s-check-output.txt; done
python3 /tmp/audit68a/compare_step2.py > /tmp/audit68a/compare_step2_output.txt
# Step 3.1 cache before, link, (build), cache after
G="<repo>/data/raw/grib"
find "$G" -type f | wc -l
find "$G" -type f -exec stat -f "%N %z %m" {} + | sort | shasum -a 256
ln -s "$G" /tmp/audit68a/clone/data/raw/grib
MLWX_LIBOMP_PATH_SET=1 DYLD_LIBRARY_PATH=/tmp/audit68a/clone/.venv/lib/python3.12/site-packages/sklearn/.dylibs \
  /usr/bin/time -p clone/.venv/bin/python rebuild_step3.py > rebuild_step3_output.txt 2>&1
  # ^ stopped at the season section: /usr/bin/time strips DYLD_LIBRARY_PATH (see section 6)
MLWX_LIBOMP_PATH_SET=1 DYLD_LIBRARY_PATH=/tmp/audit68a/clone/.venv/lib/python3.12/site-packages/sklearn/.dylibs \
  clone/.venv/bin/python season_step3.py > season_step3_output.txt 2>&1
find "$G" -type f | wc -l
find "$G" -type f -exec stat -f "%N %z %m" {} + | sort | shasum -a 256
# checks on the working repo
find scripts/__pycache__ -newer docs/session-68a.md
git status --porcelain
````

### 7.2 `compare_step2.py`

````python
#!/usr/bin/env python3
"""Session 68a Step 2.4 -- compare each recomputed figure with its recorded value.

Reads only the clone's recomputed outputs (under /tmp/audit68a). Recorded values
are typed in from the pre-registration (notes/audit-session-68a.md section 2.1),
which copied them from DECISIONS F16/F30/F47/F64/F82 (archive), F94 and its
summary CSV, and F109 (archive) / notes/session-64-confirm-output.txt.
Writes nothing but stdout.
"""
import csv
import re
from pathlib import Path

T = Path("/tmp/audit68a")
CLONE = T / "clone"

lines = []
n_match = n_mis = 0


def cmp(label, recorded, got):
    global n_match, n_mis
    ok = (str(recorded) == str(got))
    if ok:
        n_match += 1
    else:
        n_mis += 1
    lines.append(f"{label:<52} recorded {str(recorded):<10} recomputed {str(got):<10} "
                 f"{'match' if ok else 'MISMATCH'}")


# ---------------------------------------------------------------- minimal method
MINIMAL = {
    # station: (script, finding, [raw, persist, clim, meanbias, ml], train, paired, dropped, scored, verdict)
    "EGLC": ("session07_test", "F16", ["1.242", "2.096", "2.972", "1.234", "1.040"], 1569, 364, 1, 363, "PASS"),
    "LFPG": ("session13_test", "F30", ["1.396", "2.300", "3.774", "1.389", "1.208"], 1569, 364, 1, 363, "PASS"),
    "DSM":  ("session18_test", "F47", ["1.815", "4.003", "5.030", "1.760", "1.700"], 1571, 365, 0, 365, "PASS"),
    "YSDU": ("session24_test", "F64", ["1.251", "2.669", "3.143", "1.238", "1.210"], 1553, 356, 9, 347, "PASS"),
    "RNO":  ("session29_test", "F82", ["1.414", "2.490", "4.027", "1.500", "1.458"], 1568, 365, 0, 365, "FAIL"),
}
EXTRA = {  # figures also recorded in the findings
    "EGLC": [("mean training bias", "-0.1479"), ("closer than raw GFS", "221 of 363")],
    "LFPG": [("mean training bias", "-0.0600"), ("closer than raw GFS", "213 of 363")],
    "DSM":  [("closer than raw GFS", "195 of 365")],
    "YSDU": [],
    "RNO":  [],
}
METHODS = ["Raw GFS", "Persistence", "Climatology", "Mean-bias reference", "ML-corrected"]


def first_int(pat, text):
    m = re.search(pat, text, re.M)
    return int(m.group(1).replace(",", "")) if m else None


for st, (script, fid, maes, tr, paired, dropped, scored, verdict) in MINIMAL.items():
    lines.append(f"-- {st}  {script}.py  ({fid})")
    text = (T / f"run_{script}.txt").read_text()
    # the main MAE table is the one whose rows end in YES / no / the claim
    for meth, rec in zip(METHODS, maes):
        m = re.search(rf"^    {re.escape(meth)} +([0-9.]+) +\S+ +\S+ +\S+ +(YES|no|the claim)\s*$", text, re.M)
        cmp(f"{st} MAE {meth}", rec, m.group(1) if m else None)
    cmp(f"{st} training kept rows", tr, first_int(r"this session, training window kept rows\s*:\s*([\d,]+)", text))
    cmp(f"{st} test paired rows", paired, first_int(r"paired rows kept\s*:\s*([\d,]+)", text))
    cmp(f"{st} test days dropped", dropped, first_int(r"days dropped\s*:\s*([\d,]+)", text))
    cmp(f"{st} scored days", scored, first_int(r"days every method is scored on\s*:\s*([\d,]+)", text))
    box = re.search(r"^\s*\*  (.+?)\.\s+\*\s*$", text, re.M).group(1)
    got_verdict = "FAIL" if "NOT PASS" in box else ("PASS" if "PASSES" in box else box)
    cmp(f"{st} verdict", verdict, got_verdict)
    for name, rec in EXTRA[st]:
        if name == "mean training bias":
            m = re.search(r"mean training-window bias \(observed - forecast\): ([+-][0-9.]+)", text)
        else:
            m = re.search(r"days the correction was closer than raw GFS : (\d+ of \d+)", text)
        cmp(f"{st} {name}", rec, m.group(1) if m else None)

# ---------------------------------------------------------------- F94
lines.append("-- F94  session39_sealed_test.py  (summary CSV, 4 dp)")
F94 = {
    "EGLC": ("1589", "364", "1.2536", "2.0964", "1.0367", "1.0000", "PASS"),
    "LFPG": ("1589", "364", "1.3822", "2.3003", "1.1775", "1.1561", "PASS"),
    "DSM":  ("1590", "365", "1.7334", "4.0029", "1.6940", "1.6358", "PASS"),
    "YSDU": ("1573", "356", "1.3167", "2.6686", "1.2834", "1.1786", "PASS"),
    "RNO":  ("1587", "365", "1.5116", "2.4901", "1.4551", "1.3460", "PASS"),
}
cols = ["train_rows", "test_rows", "raw_mae", "persist_mae", "f3_mae", "f5_mae", "verdict"]
with open(CLONE / "data/processed/session40_sealed_test_summary.csv") as f:
    got = {r["station"]: r for r in csv.DictReader(f)}
for st, rec in F94.items():
    for c, v in zip(cols, rec):
        cmp(f"{st} {c}", v, got[st][c])
# F94's DECISIONS table (3 dp) against the recomputed output table
text = (T / "run_session39_sealed_test.txt").read_text()
F94_3DP = {"EGLC": ("1.254", "2.096", "1.037", "1.000"), "LFPG": ("1.382", "2.300", "1.177", "1.156"),
           "DSM": ("1.733", "4.003", "1.694", "1.636"), "YSDU": ("1.317", "2.669", "1.283", "1.179"),
           "RNO": ("1.512", "2.490", "1.455", "1.346")}
for st, rec in F94_3DP.items():
    g = got[st]
    for c, v in zip(["raw_mae", "persist_mae", "f3_mae", "f5_mae"], rec):
        cmp(f"{st} {c} (F94 table, 3 dp)", v, f"{float(g[c]):.3f}")

# ---------------------------------------------------------------- F109
lines.append("-- F109  session62_reserved_confirm.py --confirm  (4 dp)")
F109 = {
    "EGLC": ("1225", "364", "1", "1", "1.2362", "2.2259", "1.0861", "1.0008", "PASS", "PASS"),
    "LFPG": ("1224", "365", "0", "0", "1.4091", "2.5233", "1.3285", "1.2369", "PASS", "PASS"),
    "DSM":  ("1225", "365", "0", "0", "1.7043", "4.1081", "1.4402", "1.4123", "PASS", "PASS"),
    "YSDU": ("1213", "360", "5", "5", "1.4897", "2.5775", "1.3030", "1.2643", "PASS", "PASS"),
    "RNO":  ("1222", "365", "0", "0", "1.6135", "2.7563", "1.4272", "1.2742", "PASS", "PASS"),
}
keys = ["n_train", "n_test", "no_obs_dropped", "no_prev", "raw", "persist", "B", "B+DLRT", "vs_raw", "vs_persist"]
text = (T / "run_session62_confirm.txt").read_text()
for st, rec in F109.items():
    m = re.search(rf"^{st}: (.*)$", text, re.M)
    kv = dict(p.split("=", 1) for p in m.group(1).split())
    for k, v in zip(keys, rec):
        cmp(f"{st} {k}", v, kv.get(k))
cmp("bar verdict", "ALL FIVE AIRPORTS PASS",
    "ALL FIVE AIRPORTS PASS" if "ALL FIVE AIRPORTS PASS" in text else "other")
m = re.search(r"airport-averaged MAE ([0-9.]+) vs B ([0-9.]+)", text)
cmp("airport-averaged MAE, B+D,L,R,T", "1.2377", m.group(1))
cmp("airport-averaged MAE, B", "1.3170", m.group(2))

print("\n".join(lines))
print(f"\nTOTAL: {n_match} match, {n_mis} MISMATCH")
````

### 7.3 `rebuild_step3.py`

````python
#!/usr/bin/env python3
"""Session 68a Step 3 -- rebuild a fixed sample of B features from the raw GRIB
cache with the COMMITTED decode code, and compare with the processed CSVs.

Run with the clone's own interpreter:
    MLWX_LIBOMP_PATH_SET=1 DYLD_LIBRARY_PATH=<clone sklearn .dylibs> \
        /tmp/audit68a/clone/.venv/bin/python /tmp/audit68a/rebuild_step3.py

- Imports scripts/session37_decode.py (training + reserved dates: both lie in
  grib_features_v16_window.csv) and scripts/session40_decode.py (sealed dates)
  from the clone, and calls their own decode_row() once per sampled
  station-day, with the elevation constants from their own
  load_elevation_corrections(). No logic is copied or changed.
- The clone's data/raw/grib is a symlink to the working repo's cache, opened
  read-only by the committed bilinear_value() ('rb').
- Also calls session37_elevation_fix.bilinear_value() on the tracked HGT
  diagnostic files (no network) and compares with orog_interp_m in the
  committed params CSV.
- Season features: not stored in any processed CSV. Compares the two committed
  scoring paths (session39 features_5, session62 make_feature_vector).
- Fits nothing, scores nothing, writes nothing but stdout.
"""
import csv
import sys
from datetime import date
from pathlib import Path

CLONE = Path("/tmp/audit68a/clone")
sys.path.insert(0, str(CLONE / "scripts"))

import session37_decode as s37          # noqa: E402
import session40_decode as s40          # noqa: E402

PROC = CLONE / "data" / "processed"
SAMPLE = {
    "training": [date(2021, 3, 24), date(2022, 11, 26), date(2024, 7, 31)],
    "reserved": [date(2024, 8, 1), date(2025, 1, 30), date(2025, 7, 31)],
    "sealed":   [date(2025, 8, 1), date(2026, 1, 30), date(2026, 7, 31)],
}
BUILDER = {"training": s37, "reserved": s37, "sealed": s40}
CSVFILE = {"training": "grib_features_v16_window.csv",
           "reserved": "grib_features_v16_window.csv",
           "sealed": "grib_features_sealed_window.csv"}
COLS = ["target_hour", "run_date", "cycle", "lead",
        "temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]


def load_csv(name):
    with open(PROC / name) as f:
        return {(r["station"], r["target_date"]): r for r in csv.DictReader(f)}


def decimals(s):
    return len(s.split(".")[1]) if "." in s else 0


csvs = {n: load_csv(n) for n in set(CSVFILE.values())}

# stored precision per column (max digits after the point, over the whole file)
print("== stored precision per column (max decimals over the whole file) ==")
for name, rows in sorted(csvs.items()):
    for c in ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]:
        print(f"  {name:36s} {c:22s} {max(decimals(r[c]) for r in rows.values())}")

# identical decode code in both builders?
import inspect                           # noqa: E402
for fn in ["decode_row", "bilinear_value", "grib_files_for", "cycle_and_lead", "load_elevation_corrections"]:
    same = inspect.getsource(getattr(s37, fn)) == inspect.getsource(getattr(s40, fn))
    print(f"  session37 vs session40 {fn}(): {'identical source' if same else 'DIFFERENT source'}")
print(f"  AIRPORTS identical: {s37.AIRPORTS == s40.AIRPORTS}")

results = {c: [] for c in COLS}
n_match = n_mis = 0
missing = []
for window, dates in SAMPLE.items():
    mod = BUILDER[window]
    elev = mod.load_elevation_corrections()
    rows = csvs[CSVFILE[window]]
    for d in dates:
        for st, (hour, lat, lon) in mod.AIRPORTS.items():
            key = (st, d.isoformat())
            rebuilt, err = mod.decode_row(st, hour, lat, lon, d, elev[st])
            if rebuilt is None or key not in rows:
                missing.append((window, st, d, err, key in rows))
                continue
            stored = rows[key]
            for c in COLS:
                rv = rebuilt[c]
                sv = stored[c]
                if isinstance(rv, float):
                    ok = rv == float(sv)          # both are round(x, 3) values
                    rv_s = repr(rv)
                else:
                    ok = str(rv) == sv
                    rv_s = str(rv)
                n_match += ok
                n_mis += (not ok)
                results[c].append(f"  {window:8s} {st:4s} {d}  csv {sv:>9s}  rebuilt {rv_s:>9s}  "
                                  f"{'match' if ok else 'MISMATCH'}")

for c in COLS:
    print(f"\n== {c} ({len(results[c])} station-days) ==")
    print("\n".join(results[c]))
print(f"\nmissing / not decodable: {missing if missing else 'none'}")
print(f"B TOTAL: {n_match} match, {n_mis} MISMATCH")

# ---------------------------------------------------------------- elevation terrain check
import session37_elevation_fix as fix   # noqa: E402
print("\n== elevation-fix terrain check (committed bilinear_value on tracked HGT files) ==")
params = {r["station"]: r for r in csv.DictReader(open(CLONE / "data/raw/diagnostics/session37/session37_elevation_correction_params.csv"))}
hgt = {"RNO": fix.RNO_EXISTING_HGT}
for st in ["EGLC", "LFPG", "DSM", "YSDU"]:
    hour = fix.AIRPORTS[st][0]
    cyc, lead = fix.cycle_and_lead(hour)
    hgt[st] = fix.DIAG37 / f"gfs_{fix.SAMPLE_RUN_DATE}_t{cyc:02d}z_f{lead:03d}_hgt_surface_{st}_diagnostic.grib2"
for st, (hour, lat, lon, grid_elev) in fix.AIRPORTS.items():
    orog = fix.bilinear_value(hgt[st], lat, lon, "orog")
    orog = orog[0] if isinstance(orog, tuple) else orog
    ok = round(orog, 2) == float(params[st]["orog_interp_m"])
    print(f"  {st:4s} file {hgt[st].name}  csv orog_interp_m {params[st]['orog_interp_m']:>8s}  "
          f"rebuilt {round(orog, 2):>8}  {'match' if ok else 'MISMATCH'}")

# ---------------------------------------------------------------- season features
import session39_sealed_test as s39     # noqa: E402
import session62_reserved_confirm as s62  # noqa: E402
print("\n== season features: session39 features_5 vs session62 make_feature_vector ==")
print(f"  year_fraction() source identical in s39 and s62: "
      f"{inspect.getsource(s39.year_fraction) == inspect.getsource(s62.year_fraction)}")
n_s_ok = n_s_bad = 0
for window, dates in SAMPLE.items():
    for d in dates:
        r = {"date": d, "fc": 0.0, "cloud": 0.0, "wind": 0.0}
        a39 = s39.features_5([r])[0]
        v62 = s62.make_feature_vector(r, ["season_sin", "season_cos"])
        v62 = list(v62)
        ok = (a39[1] == v62[0]) and (a39[2] == v62[1])
        n_s_ok += ok
        n_s_bad += (not ok)
        print(f"  {window:8s} {d}  year_fraction {s39.year_fraction(d):.6f}  "
              f"s39 sin {a39[1]:+.6f} cos {a39[2]:+.6f}  s62 sin {v62[0]:+.6f} cos {v62[1]:+.6f}  "
              f"{'match' if ok else 'MISMATCH'}")
print(f"SEASON TOTAL: {n_s_ok} match, {n_s_bad} MISMATCH")
````

### 7.4 `season_step3.py`

````python
#!/usr/bin/env python3
"""Session 68a Step 3 (season part) -- split out of rebuild_step3.py after that
run stopped at the lightgbm import (/usr/bin/time stripped DYLD_LIBRARY_PATH).
Same code as the season section there, unchanged. Fits nothing, writes nothing."""
import inspect
import sys
from datetime import date
from pathlib import Path

CLONE = Path("/tmp/audit68a/clone")
sys.path.insert(0, str(CLONE / "scripts"))

SAMPLE = {
    "training": [date(2021, 3, 24), date(2022, 11, 26), date(2024, 7, 31)],
    "reserved": [date(2024, 8, 1), date(2025, 1, 30), date(2025, 7, 31)],
    "sealed":   [date(2025, 8, 1), date(2026, 1, 30), date(2026, 7, 31)],
}

import session39_sealed_test as s39     # noqa: E402
import session62_reserved_confirm as s62  # noqa: E402
print("\n== season features: session39 features_5 vs session62 make_feature_vector ==")
print(f"  year_fraction() source identical in s39 and s62: "
      f"{inspect.getsource(s39.year_fraction) == inspect.getsource(s62.year_fraction)}")
n_s_ok = n_s_bad = 0
for window, dates in SAMPLE.items():
    for d in dates:
        r = {"date": d, "fc": 0.0, "cloud": 0.0, "wind": 0.0}
        a39 = s39.features_5([r])[0]
        v62 = s62.make_feature_vector(r, ["season_sin", "season_cos"])
        v62 = list(v62)
        ok = (a39[1] == v62[0]) and (a39[2] == v62[1])
        n_s_ok += ok
        n_s_bad += (not ok)
        print(f"  {window:8s} {d}  year_fraction {s39.year_fraction(d):.6f}  "
              f"s39 sin {a39[1]:+.6f} cos {a39[2]:+.6f}  s62 sin {v62[0]:+.6f} cos {v62[1]:+.6f}  "
              f"{'match' if ok else 'MISMATCH'}")
print(f"SEASON TOTAL: {n_s_ok} match, {n_s_bad} MISMATCH")
````

### 7.5 `rebuild_step3_output.txt`, header lines (precision and source identity)

```
== stored precision per column (max decimals over the whole file) ==
  grib_features_sealed_window.csv      temperature_grib_c     3
  grib_features_sealed_window.csv      cloud_cover_grib_pct   3
  grib_features_sealed_window.csv      wind_speed_grib_kmh    3
  grib_features_v16_window.csv         temperature_grib_c     3
  grib_features_v16_window.csv         cloud_cover_grib_pct   3
  grib_features_v16_window.csv         wind_speed_grib_kmh    3
  session37 vs session40 decode_row(): identical source
  session37 vs session40 bilinear_value(): identical source
  session37 vs session40 grib_files_for(): identical source
  session37 vs session40 cycle_and_lead(): identical source
  session37 vs session40 load_elevation_corrections(): DIFFERENT source
  AIRPORTS identical: True
```

### 7.6 F109 `--confirm` raw output (`run_session62_confirm.txt`)

```
==========================================================================================
SESSION 63 -- THE SINGLE AUTHORIZED RESERVED-YEAR CONFIRMATION (D51/D58). Running once, unchanged.
==========================================================================================
EGLC: n_train=1225 n_test=364 no_obs_dropped=1 no_prev=1 raw=1.2362 persist=2.2259 B=1.0861 B+DLRT=1.0008 vs_raw=PASS vs_persist=PASS
LFPG: n_train=1224 n_test=365 no_obs_dropped=0 no_prev=0 raw=1.4091 persist=2.5233 B=1.3285 B+DLRT=1.2369 vs_raw=PASS vs_persist=PASS
DSM: n_train=1225 n_test=365 no_obs_dropped=0 no_prev=0 raw=1.7043 persist=4.1081 B=1.4402 B+DLRT=1.4123 vs_raw=PASS vs_persist=PASS
YSDU: n_train=1213 n_test=360 no_obs_dropped=5 no_prev=5 raw=1.4897 persist=2.5775 B=1.3030 B+DLRT=1.2643 vs_raw=PASS vs_persist=PASS
RNO: n_train=1222 n_test=365 no_obs_dropped=0 no_prev=0 raw=1.6135 persist=2.7563 B=1.4272 B+DLRT=1.2742 vs_raw=PASS vs_persist=PASS

BAR VERDICT (D58 pre-registered expectation 7): ALL FIVE AIRPORTS PASS
SECONDARY READ: B+D,L,R,T airport-averaged MAE 1.2377 vs B 1.3170  (beats B)
real 3.11
user 2.65
sys 0.18
```

### 7.7 Minimal-method and F94 raw outputs

These are 450–813 lines each and identical to the committed files apart
from the lines in section 3.2. Final lines:

```
--- run_session07_test.txt (450 lines), last 3:

STAGE 1: PASSED   ML-corrected test-year MAE = 1.040 degC against raw GFS 1.242 and persistence 2.096
This output is saved at notes/session-07-check-output.txt

--- run_session13_test.txt (624 lines), last 3:

STAGE 2: PASSED   ML-corrected test-year MAE = 1.208 degC against raw GFS 1.396 and persistence 2.300
This output is saved at notes/session-13-check-output.txt

--- run_session18_test.txt (810 lines), last 3:

DSM: PASSED   ML-corrected test-year MAE = 1.700 degC against raw GFS 1.815 and persistence 4.003
This output is saved at notes/session-18-check-output.txt

--- run_session24_test.txt (813 lines), last 3:

DUBBO: PASSED   ML-corrected test-year MAE = 1.210 degC against raw GFS 1.251 and persistence 2.669
This output is saved at notes/session-24-check-output.txt

--- run_session29_test.txt (792 lines), last 3:

RENO: DID NOT PASS   ML-corrected test-year MAE = 1.458 degC against raw GFS 1.414 and persistence 2.490
This output is saved at notes/session-29-check-output.txt

--- run_session39_sealed_test.txt (179 lines), last 3:
==============================================================================
This is the one authorised look at the sealed test year for the 5-feature GRIB recipe (D48.13), per airport. The result stands exactly as reported above -- no re-tuning, no re-run, no retroactive adjustment. It does not alter any airport's existing sealed-test verdict under the existing 3-feature/Open-Meteo recipe (F16/F30/F47/F64/F82).
This output is saved at notes/session40-sealed-test-output.txt
```

### 7.8 `assemble_report.py` (builds this file)

````python
#!/usr/bin/env python3
"""Assemble notes/audit-session-68a.md from report_prose.md, the pre-registration
already written to the report (section 2, kept verbatim), and the raw outputs."""
import re, subprocess
from pathlib import Path
T = Path("/tmp/audit68a")
REPO = Path("/Users/zacharyadams/Coding Projects/MLwx")
report = REPO / "notes" / "audit-session-68a.md"
cur = report.read_text()
start = cur.index("## 2. Pre-registered")
end = cur.find("\n---\n\n## 3.", start)
prereg = (cur[start:end] if end != -1 else cur[start:]).rstrip() + "\n"
prose = (T / "report_prose.md").read_text()

rb = (T / "rebuild_step3_output.txt").read_text()
b_part = rb[rb.index("== target_hour"):rb.index("missing / not decodable")]
b_tail = rb[rb.index("missing / not decodable"):rb.index("== elevation-fix")].strip()
elev = rb[rb.index("== elevation-fix"):rb.index("Traceback")].strip()
head = rb[:rb.index("== target_hour")].strip()
season = (T / "season_step3_output.txt").read_text().strip()
gitdiff = subprocess.run(["git", "diff", "-U0"], cwd=T / "clone", capture_output=True, text=True).stdout
gitdiff = "\n".join(l for l in gitdiff.splitlines() if l.startswith(("diff ", "-run", "+run", "-Wrote", "+Wrote")))
tails = []
for s in ["session07_test", "session13_test", "session18_test", "session24_test", "session29_test", "session39_sealed_test"]:
    lines = [l for l in (T / f"run_{s}.txt").read_text().splitlines() if not re.match(r"^(real|user|sys) ", l)]
    tails.append(f"--- run_{s}.txt ({len(lines)} lines), last 3:\n" + "\n".join(lines[-3:]))
subs = {
    "PREREG": prereg.strip(),
    "STEP2": (T / "compare_step2_output.txt").read_text().strip(),
    "GITDIFF": gitdiff.strip(),
    "STEP3B": (b_part.strip() + "\n\n" + b_tail),
    "ELEV": elev,
    "SEASON": season,
    "SHELL": (T / "shell_steps.sh").read_text().strip(),
    "COMPARE": (T / "compare_step2.py").read_text().strip(),
    "REBUILD": (T / "rebuild_step3.py").read_text().strip(),
    "SEASONPY": (T / "season_step3.py").read_text().strip(),
    "REBUILDHEAD": head,
    "CONFIRM": (T / "run_session62_confirm.txt").read_text().strip(),
    "TAILS": "\n\n".join(tails),
    "ASSEMBLER": (T / "assemble_report.py").read_text().strip(),
}
for k, v in subs.items():
    assert "{{" + k + "}}" in prose, k
    prose = prose.replace("{{" + k + "}}", v)
assert not any("{{" + k + "}}" in prose.split("### 7.8")[0] for k in subs)
report.write_text(prose)
print(f"wrote {report} ({len(prose.splitlines())} lines)")
````
