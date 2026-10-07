# Session 36 — GRIB build, step 1: confirm back-extent + validate the pipeline

## This starts a multi-session sub-project

Building the deep GFS GRIB feature source is a small **multi-session sub-project**, not one
session. Its steps, in order: **(1 = this session)** confirm the fetchable back-extent and
prove the GRIB→point pipeline reproduces the existing Open-Meteo temperature; (2) add
cloud/wind on the same grid+lead and do the bulk historical pull; (3) join to observations
and re-run the richer-features experiment on the full window; (4) lock and open the sealed
year. **This session builds no final pipeline, pulls no bulk history, joins nothing, fits
nothing, and locks nothing.** It de-risks everything downstream and stops.

## Scope — one job, then stop

Two things, both cheap:
1. **Confirm the back-extent we can actually fetch** — the AWS bucket's true earliest date,
   and whether the 2015–2021 slice is cleanly reachable (NCAR ds084.1 was sunsetting early
   2026; confirm where the pre-2021 data now lives). This sizes the real prize (~11 years
   vs ~4.3).
2. **Prove the pipeline** — pull GRIB **temperature** for a small sample, interpolate
   grid→point at the five airports, reproduce the `previous_day1` 24h-ahead lead, and check
   the result matches the existing **Open-Meteo temperature** you already trust. Temperature
   first, because it is the one variable with a known-good reference to validate against —
   cloud/wind come only after the pipeline is proven.

Report both, and stop for review.

## Why temperature-first, and what "reproduce" means

The existing Open-Meteo temperature (validated across 35 sessions, 4 passing airports) is
the **answer key**. If our hand-rolled GRIB→point temperature lands close to it, the
interpolation and lead-time logic are correct, and we can trust them when we later add
cloud/wind (which have no such reference). If it does not match, we have found a bug on a
few sample days instead of after a multi-year, multi-variable pull. This session neither
advances the project's data nor changes the method — it is a validation gate.

## Standing rules that bind this session (SPEC §2)

- **Leakage / sealed year:** sample only dates ≤ 2025-07-31. The sealed test year
  (2025-08-01 → 2026-07-31) is never fetched or touched.
- **Validation samples must be where Open-Meteo also has data** — i.e. 2021-03-24 onward
  (Open-Meteo's floor). The pre-2021 GRIB cannot be validated against Open-Meteo (Open-Meteo
  lacks it); proving the pipeline on 2021+ is what licenses trusting it on 2015–2021.
- **Fetch light:** use `.idx` byte-range requests to pull only the temperature message
  needed — never whole ~500 MB GRIB files, never a date range beyond the small sample.
- **Raw is immutable, with provenance** (2.3): save sample GRIB extracts + any derived
  comparison table under `data/raw/diagnostics/session36/`, each with a `.meta.txt` (exact
  source URL/query + UTC pull time).
- **Read the existing Open-Meteo temperature for comparison only** — do not modify, re-pull,
  or overwrite any existing data.
- **You never commit.** Prepare changes and a suggested message for the owner.

## Reference — airports and existing setup

Five airports, positions and target hours per SPEC 3.4 (EGLC 12:00, LFPG 12:00, DSM 18:00,
YSDU 02:00, RNO 20:00 UTC). Existing forecast source is Open-Meteo `gfs_global` at
`previous_day1` — the 0.25° NCEP GFS — so the GRIB product to match is the **0.25° GFS**
(the AWS/NCAR archives session 35 already probed). Temperature variable in GRIB is
`TMP:2 m above ground` (confirm the exact label on contact).

---

## Task 1 — confirm the fetchable back-extent

- **AWS `noaa-gfs-bdp-pds`:** find its true earliest available date by listing (don't assume
  "2021" — probe it). Confirm the 0.25° product and the needed cycles/forecast hours are
  present at that floor.
- **2015–2021 slice:** check whether NCAR ds084.1 is still reachable (it was retiring early
  2026), and/or whether the pre-2021 0.25° history has migrated into the AWS bucket or
  another open archive. Report where — if anywhere — 2015–2021 is cleanly fetchable,
  credential-free.
- **State the confirmed usable window** plainly: is the real prize ~11 years (2015+), ~4.3
  years (2021+ only), or something between? **If it comes back materially worse than ~2015
  (e.g. 2021-only), flag it prominently** — it re-weights build-vs-lock — but still complete
  Task 2, since the pipeline is needed for any version of the build.

## Task 2 — set up a GRIB reader

The environment has no GRIB decoder (session 35 checked). Install one (`cfgrib`/`eccodes`,
`pygrib`, or `wgrib2` — whichever is cleanest here) and confirm it reads a sample message.
Record what was installed.

## Task 3 — pull temperature samples (byte-range, small)

Pick a small validation sample, all ≤ 2025-07-31 and within Open-Meteo's era (≥ 2021-03-24):
- a recent contiguous stretch (e.g. ~2 weeks around mid-2025), and
- a short early stretch (e.g. ~3–5 days near 2021) to confirm the pipeline works at both ends
  of the archive era.

For each sample day and each airport's target hour, byte-range-fetch (via `.idx`) the GFS
**2 m temperature** message(s) needed to form the `previous_day1` value. Save extracts with
provenance.

## Task 4 — grid→point interpolation + lead-time convention

- **Interpolation:** bilinear-interpolate the 0.25° grid to each airport's exact lat/long
  (SPEC 3.4). Note the four grid points used per airport.
- **Lead-time:** determine which cycle (00/06/12/18 UTC) + forecast hour reproduces the
  `previous_day1` (≈24 h-ahead, valid at the target hour) definition, per airport target
  hour — including the awkward YSDU (02:00) and RNO (20:00) cases. **Discover it empirically
  if needed:** try the plausible cycle+step combinations and see which best reproduces
  Open-Meteo's values — the match itself reveals and confirms the convention. Document the
  chosen convention per airport; this becomes the rule the bulk pull will use.

## Task 5 — reproduce-the-results check (the gate)

Per airport, compare the GRIB-derived temperature against the existing Open-Meteo
temperature over the sample: report mean absolute difference, max difference, and whether any
difference is systematic (an offset) or scatter. Judge each airport **PASS / FAIL**:
- **PASS** = differences are small and explainable by grid-point choice (sub-degree mean,
  no large systematic bias) — the pipeline is validated.
- **FAIL** = large or systematic differences — name the likely cause (wrong grid points,
  wrong cycle/lead, unit/label error) so step 2 can fix it before scaling up.
Give an overall verdict: is the GRIB→point pipeline proven, or does it need a fix first?

---

## What NOT to do

- **Do not pull cloud or wind this session** — temperature only, because only temperature has
  the Open-Meteo answer key to validate against.
- **Do not do the bulk / multi-year pull**, and do not fetch whole GRIB files — byte-range
  the needed messages only.
- **Do not build the final feature pipeline, join to observations, or fit any model.**
- **Do not touch the sealed test year**, and do not sample outside Open-Meteo's era for the
  reproduction check.
- **Do not modify, re-pull, or overwrite any existing data** — read Open-Meteo temperature for
  comparison only.
- **Do not modify `SPEC.md` or `RESULTS.md`**, and **do not lock** anything.
- **Do not commit.**
- **Do not exceed scope** — log anything else as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Task 1 (confirmed back-extent + prize size), Task 4 (interpolation + the
   per-airport lead convention discovered), and Task 5 (per-airport reproduction PASS/FAIL +
   overall verdict). Note what GRIB reader was installed.
2. **Append one DECISIONS finding** (append-only; next sequential number — check the tail of
   live DECISIONS.md, likely **F89**): the confirmed fetchable window, the interpolation +
   lead-time convention, and the reproduction verdict. If the back-extent came back worse than
   ~2015, flag the build-vs-lock re-weight for the owner (do not decide it).
3. **Refresh STATUS.md** to record session 36 and that the GRIB build sub-project has begun.
4. **Save** sample GRIB extracts + the comparison table under `data/raw/diagnostics/session36/`
   with `.meta.txt` provenance.
5. **Archive step (routine):** move any entry that became settled this session to
   `DECISIONS-archive.md` per the criterion (likely none — a step-1 probe settles nothing —
   but check and state so).
6. **Consistency check:** new DECISIONS number next-sequential and unique; every figure traces
   to a saved extract or the comparison table; no sample from the sealed test year; STATUS and
   DECISIONS agree; `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only the expected
   files.
7. **Write a suggested commit message** — short title line, brief body (to avoid shell-paste
   trouble; detail lives in F89) — then **stop and wait for the owner's review.**
