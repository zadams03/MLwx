# Session 39 — GRIB build, step 4a: lock the 5-feature recipe (no sealed data touched)

## What this session is

The **lock**. It writes the frozen 5-feature recipe into DECISIONS in full, and freezes the
exact sealed-test script — **before any sealed-year data is seen** — exactly as Reno was
handled (D44 locked the recipe in writing, then F82 tested it once). After this session and
your commit, the recipe is frozen: the sealed test (session 40) becomes purely mechanical, with
nothing left to choose once sealed data is in view.

**This session touches no sealed-year data, runs no test, and produces no sealed-year figure.**
It is documentation + a frozen script. Its whole purpose is to remove every post-hoc degree of
freedom, so the one-shot is honest.

## Why the recipe must be complete here

The frozen-bar discipline only means something if nothing is decided after seeing the sealed
year. So the locked recipe must pin down **every** choice — features, source, pipeline, model,
window, bar, evaluation, and the advance expectations — leaving the test session zero
decisions. If any detail is left open, this lock has failed its job.

## Standing rules that bind this session (SPEC §2)

- **The sealed test year (2025-08-01 → 2026-07-31) is not pulled, loaded, or referenced as
  data anywhere.** No sealed-year figure is computed. The lock is written blind to it.
- **No SPEC/RESULTS change.** The 5-feature method folds into SPEC only *after* it passes its
  sealed test — same discipline that kept Reno's method out of SPEC until proven. This session
  writes a DECISIONS entry and a frozen script, nothing more.
- **Append-only** DECISIONS; **archive-as-you-go** in the roundup.
- **You never commit.** Prepare changes and a suggested message; the owner reviews and commits
  the lock by hand.

---

## Task 1 — write the locked-recipe DECISIONS entry

Append a new decision (next sequential D-number — check the tail of live DECISIONS.md, likely
**D48**) that specifies the frozen 5-feature method **completely**. It must state, unambiguously:

**The method being locked:** the 5-feature richer-features MOS model, GRIB source, to be
sealed-tested once per airport against the frozen bar.

**Features (exact):**
- `forecast_temp_c` — GRIB GFS 2 m temperature, elevation/lapse-rate corrected at
  **7.429 °C/km** (grid-vs-station gap, session 37/F90), bilinear-interpolated to each airport's
  established grid point, at the `previous_day1` lead.
- `season_sin`, `season_cos` — sin/cos(2π · year_fraction(date)).
- `cloud_cover` — GRIB `TCDC` (entire atmosphere), same grid→point, same lead.
- `wind_speed_10m` — sqrt(UGRD² + VGRD²) at 10 m, same grid→point, same lead.

**Source & pipeline (exact):** GFS 0.25° GRIB from AWS `noaa-gfs-bdp-pds`; lead convention
`cycle = floor(HH/6)*6` on day D−1, forecast-hour lead `= 24 + (HH mod 6)` for target hour HH
(F89); bilinear grid→point; the 7.429 °C/km elevation downscaling applied to temperature at all
five airports.

**Target:** residual = observed temperature (IEM METAR, ±15 min pairing, SPEC 4.5) − GRIB
forecast temperature, at the airport's target hour. Corrected forecast = GRIB forecast +
predicted residual.

**Model (exact, identical at every airport, no per-airport tuning):** LightGBM
`objective=regression_l1, n_estimators=300, learning_rate=0.05, num_leaves=15,
min_child_samples=40, random_state=42, deterministic=True, n_jobs=1`.

**Training window:** 2021-03-24 → 2025-07-31 (v16), trained in full (no inner split — the
CV/rehearsal is done; the sealed run trains on the whole training window).

**Sealed test year:** 2025-08-01 → 2026-07-31, opened **once** per airport.

**Airports:** EGLC, LFPG, DSM, YSDU, RNO — each a single sealed look.

**The bar (frozen, qualitative — the existing SPEC 5 bar, unchanged):** the 5-feature corrected
forecast has lower MAE than **both** raw GFS **and** persistence on the sealed year, per airport.
No numeric margin.

**What is reported on the sealed year:** raw GFS, persistence, 3-feature, and 5-feature MAE per
airport; the 5-feature verdict against the bar; and the 5-vs-3-feature comparison on the true
held-out year (the richer-features claim).

**Pre-registered expectations (record before the test, à la D44.12):** from the full-window CV
(F91), we expect 5-feature to beat raw GFS and persistence at all five airports; 5-feature to
beat 3-feature at all five; **LFPG to pass** (recovered on the full window after failing on the
short one); and **Reno to pass** (the rescue signal, +12.7% in CV). State these plainly so the
sealed test is a genuine confirmation-or-refutation.

**What must not change after seeing sealed data:** no re-tuning, no feature/window/rate change,
no re-run, no retroactive adjustment. The result stands exactly as tested, pass or fail, per
airport (as Reno's did, D44.10/11).

## Task 2 — freeze the sealed-test script

Write the exact script the sealed test will run — train 3-feature and 5-feature on the full
training window, then evaluate raw GFS, persistence, 3-feature, and 5-feature on the sealed year,
applying the bar per airport — and **freeze it** (commit it as the locked test). The point is
that the test code is fixed before sealed data is seen.
- **Do not run it against sealed data, and do not pull sealed-year features.** Verify only that
  the script parses/imports and its logic matches the D48 recipe (a code review + import check,
  not a full run). Its sealed-year data path must point at data that will be pulled in session 40,
  not fetched now.
- Assert in the script that it refuses to run if handed any date outside the specified sealed
  window, and that the training path excludes the sealed year — a self-guard for the one-shot.

## What NOT to do

- **Do not pull, load, or compute anything on the sealed test year.** The lock is written blind.
- **Do not run the sealed test** or produce any sealed-year figure.
- **Do not leave any recipe detail unspecified** — no post-lock degrees of freedom.
- **Do not modify `SPEC.md` or `RESULTS.md`** — the method folds into SPEC only after it passes.
- **Do not commit.**
- **Do not exceed scope** — this session is the recipe entry + the frozen script, nothing else.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the full D48 recipe as written, and confirm the frozen test script parses and
   matches it (with the self-guard against sealed-window violations).
2. **DECISIONS:** D48 appended (append-only, next-sequential, verified unique). This entry stays
   live — it is the frozen recipe the sealed test executes against.
3. **Refresh STATUS.md** to record session 39: the 5-feature recipe is locked; the sealed test
   (session 40) is the next and final step of the build; the one-shot is now frozen.
4. **Archive step (routine):** move any entry that became settled this session to
   `DECISIONS-archive.md` per the criterion (likely none — a lock settles nothing yet; F89/F90/F91
   are all still live). Check and state.
5. **Consistency check:** D48 next-sequential and unique; **no sealed-year data was pulled or any
   sealed figure computed** (verify — the script did not fetch sealed data); the recipe leaves no
   detail unspecified; `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only DECISIONS.md,
   STATUS.md, and the frozen test script (plus docs) — no data files.
6. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the
   body, `--` not em-dashes, short body — then **stop and wait for the owner's review.** The lock
   is not real until you review and commit it; only then is session 40 (the sealed test) run.
