# Session 37 — GRIB build, step 2: RNO elevation fix + cloud/wind pull on the v16 window

## Where this sits

Step 2 of the GRIB build sub-project. Step 1 (session 36) validated the GRIB→point
temperature pipeline at 4/5 airports and diagnosed RNO's failure as an elevation issue.
This session fixes RNO, pulls the full feature set (temperature + cloud cover + 10 m wind
speed) over the training window, and validates the new variables against Open-Meteo where a
reference exists. It **joins nothing to observations, fits no model, opens no sealed year,
and locks nothing** — it produces a validated GRIB feature dataset and stops. Step 3 (join +
re-run the richer-features experiment) and step 4 (lock + sealed test) come later.

## The window — v16 only (2021-03-24 onward), by design

Train the build on **2021-03-24 → 2025-07-31 only.** GFS v16.0 became operational
2021-03-22; the AWS bucket reaches back to 2021-01-01, but everything before 2021-03-22 is
**GFS v15 — a different model version with potentially different bias.** A bias-correction
model must not be trained across a model-version boundary, so the ~82 pre-v16 days are
**deliberately excluded**. This window also matches Open-Meteo's own floor (2021-03-24, two
days after the v16 launch), so it introduces no heterogeneity beyond what the existing
validated temperature results already span (v16.x throughout, incl. the minor v16.3 update).

## Scope — three things, then stop

1. **Fix RNO** — add the elevation/lapse-rate downscaling session 36 identified, and
   re-validate that GRIB temperature now reproduces Open-Meteo at **all five** airports.
2. **Pull the feature set** — temperature, `cloud_cover`, `wind_speed_10m`, from GRIB over
   the v16 window at all five airports, on the same grid + lead + downscaling pipeline.
3. **Validate the new variables** — cross-check GRIB cloud/wind against Open-Meteo on the
   period where both exist (2024-01-19 → 2025-07-31), the same known-good-reference gate that
   validated temperature.

Then assemble the validated GRIB feature dataset for the training window and stop for review.

## Standing rules that bind this session (SPEC §2)

- **Sealed test year untouched.** Pull nothing past 2025-07-31. The sealed-year feature pull
  is deferred to lock (step 4), so the one-shot stays genuinely sealed.
- **v16 only** — no data before 2021-03-24 enters the dataset (see above).
- Forecast source `gfs_global` 0.25°, `previous_day1` lead convention from session 36
  (F89): cycle `floor(HH/6)*6` on day D−1, lead `24 + (HH mod 6)`, per airport target hour.
- **Drop-count-report, never fill** (2.2): report null/missing counts per variable per
  airport; never interpolate a gap.
- **Raw is immutable, with provenance** (2.3): save GRIB extracts under `data/raw/grib/` (or
  the project's chosen path) with `.meta.txt` (source URL/query + UTC pull time) per batch.
- **Validate against Open-Meteo as the answer key** wherever a reference exists (temperature
  2021-03-24+; cloud/wind 2024-01-19+). Read existing Open-Meteo data for comparison only —
  never modify or overwrite it.
- **The GRIB-derived dataset is new and clearly separated** from the existing Open-Meteo
  data — do not overwrite or merge into the existing files.
- **You never commit.** Prepare changes and a suggested message.

---

## Task 1 — RNO elevation fix, then re-validate all five (the gate)

- Implement the elevation/lapse-rate downscaling: correct the grid-cell temperature to the
  station elevation using the grid-vs-station elevation gap (grid orography from the GRIB
  surface-height field; station elevations known per airport). Standard lapse rate is
  ~6.5 °C/km, but **match Open-Meteo empirically** — try the plausible lapse rate / method and
  pick the one that best reproduces Open-Meteo at RNO, documenting it (as with the lead
  convention in session 36).
- **Apply the same downscaling consistently at all five airports** (Open-Meteo applies it
  everywhere; the flat-terrain airports simply have a small gap). Re-run the session-36
  reproduction check at all five and confirm **RNO now PASSES and EGLC/LFPG/DSM/YSDU still
  PASS** (sub-degree, unbiased). This is the gate — if RNO doesn't come into tolerance, report
  the residual and the likely cause rather than proceeding to bulk pull.

## Task 2 — pull the feature set over the v16 window

For all five airports, over **2021-03-24 → 2025-07-31**, at each airport's target hour and
the `previous_day1` lead:
- pull `TMP:2 m` (with the Task-1 downscaling), `TCDC` (total cloud cover), and
  `UGRD`/`VGRD:10 m` (from which `wind_speed_10m = sqrt(u² + v²)` is derived) — confirm exact
  GRIB labels on contact;
- byte-range-fetch the needed messages via `.idx` (don't download whole files);
- save extracts with provenance; drop-count-report any missing/null hours.

This is a real multi-year pull (order ~10³–10⁴ byte-range requests) — script it, loop over
dates, and be polite to the source (reasonable concurrency). It runs as a script, so length
is fine; just report totals and drops at the end.

## Task 3 — validate cloud/wind against Open-Meteo on the overlap

On **2024-01-19 → 2025-07-31** (where Open-Meteo also has cloud/wind, F85), per airport,
compare the GRIB-derived `cloud_cover` and `wind_speed_10m` against Open-Meteo's:
- report mean|diff| and any systematic offset per variable per airport;
- note any definitional mismatch (e.g. GRIB `TCDC` "entire atmosphere" vs Open-Meteo's cloud
  field; wind derived from u/v vs Open-Meteo's `wind_speed_10m`);
- verdict PASS/FAIL per variable per airport. A close match licenses trusting the pipeline for
  the pre-2024 period where no Open-Meteo reference exists.

## Task 4 — assemble the validated GRIB feature dataset

Assemble temperature + cloud_cover + wind_speed_10m, all GRIB-derived, over the v16 training
window, one row per airport-day at the target hour, saved as clearly-labelled processed data
(distinct from the existing Open-Meteo files). Report per-airport row counts and drop counts.
**Do not join to observations and do not fit anything** — that is step 3.

---

## What NOT to do

- **Do not use any data before 2021-03-24** (pre-v16 / GFS v15) — the window starts at the
  v16 boundary, by design.
- **Do not pull or touch the sealed test year** (2025-08-01 → 2026-07-31).
- **Do not join to observations, fit any model, run any experiment, or lock anything** — this
  session produces a validated feature dataset only.
- **Do not download whole GRIB files** — byte-range the needed messages.
- **Do not overwrite or merge into existing Open-Meteo data** — the GRIB dataset is separate;
  read Open-Meteo for comparison only.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not commit.**
- **Do not exceed scope** — log anything else as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Task 1 (the downscaling method + five-airport re-validation, RNO now PASS),
   Task 3 (cloud/wind overlap validation), and Task 4 (dataset row/drop counts, window).
2. **Append one DECISIONS finding** (append-only; next sequential — check the tail of live
   DECISIONS.md, likely **F90**): the v16-only window decision and why (exclude pre-v16 v15
   days), the elevation-downscaling method, the five-airport temperature re-validation, the
   cloud/wind overlap validation, and the assembled dataset. Flag anything unresolved for the
   owner rather than deciding it.
3. **Refresh STATUS.md** to record session 37 and the state of the GRIB build.
4. **Save** raw GRIB extracts + `.meta.txt` provenance and the processed dataset under their
   chosen paths.
5. **Archive step (routine):** move any entry that became settled this session to
   `DECISIONS-archive.md` per the criterion (F88/F89 are likely still live — the build cites
   them — but check and state so).
6. **Consistency check:** new DECISIONS number next-sequential and unique; every figure traces
   to a saved extract, the comparison, or the dataset; **no data from before 2021-03-24 or
   inside the sealed test year** (verify the date bounds in code); STATUS and DECISIONS agree;
   `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only expected files.
7. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the
   body, `--` not em-dashes (so it pastes cleanly); keep the body short, detail lives in F90 —
   then **stop and wait for the owner's review.**
