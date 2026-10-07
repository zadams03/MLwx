# Session 47 — feature-family availability probe (radiation, upper-air, moisture, pressure, precip)

## What this session is

A cheap **availability probe** — the same shape as sessions 31 and 35 — to find out which new GRIB
feature families exist, under what exact labels, at the forecast lead the project uses, and how far
back. It answers "what can we even use" so the feature-experiment ordering can be planned on facts
rather than guesses. It **builds nothing, models nothing, pulls no bulk data, derives no feature,
and picks no ordering** — it produces a feature-availability map and stops.

The GRIB build unlocked a whole space the minimal method never had — in particular **upper-air /
vertical structure**, which was blocked on Open-Meteo (F85 found it wasn't available leakage-safe
there) but which GRIB carries at every pressure level. This probe scopes that space.

## Standing rules that bind this session (SPEC §2)

- **Probe, don't pull or model.** Byte-range `.idx` checks on a handful of sample GRIB files —
  never bulk history, no model, no feature engineering, no experiment.
- **Verify on contact.** Confirm each variable by its actual presence in the GRIB inventory and by
  a real (non-null) value fetched from a sample message — not by assuming it exists.
- **Forecast fields at the project's lead.** The features that matter are GFS *forecasts* at the
  `previous_day1`-equivalent lead (cycle `floor(HH/6)*6` on D−1, forecast hour `24 + (HH mod 6)`,
  F89) — the same leakage-safe basis as cloud/wind. Confirm availability *at that forecast lead*,
  not merely at analysis time.
- **v16 floor.** Back-extent is reported against 2021-03-24 (v16); note if a variable reaches
  further back, but flag that pre-2021-03-24 is v15 and excluded (D48.7).
- **Sample outside the sealed test year.** Use dates ≤ 2025-07-31 for the value checks (the sealed
  year isn't needed to establish availability).
- **Raw is immutable, with provenance** (2.3): save any sample extracts under
  `data/raw/diagnostics/session47/` with `.meta.txt`.
- **You never commit.** Prepare changes and a suggested message.

## Reference — the candidate families and variables

Probe these, by family. GRIB2 short names are candidates — **report the exact label/level actually
found**, as session 35 did with the model-name spellings. Confirm the level and whether the field
is **instantaneous** at the valid hour or **time-averaged / accumulated** over the forecast period
(this matters for how a feature would be used and must be recorded).

- **Radiation** (high-value: the local-noon target's actual heating mechanism): `DSWRF` (downward
  shortwave), `USWRF`, `DLWRF` (downward longwave), `ULWRF`, and cloud *layers* `LCDC`/`MCDC`/`HCDC`
  (low/mid/high cloud, vs the `TCDC` total already used). Note the averaging window for the flux
  fields explicitly.
- **Upper-air / vertical structure** (GRIB-unlocked; strategically the most interesting):
  `TMP` at 925 / 850 / 700 hPa; `HGT` at 500 / 850 hPa; `UGRD`/`VGRD` at 850 hPa; `RH` at 850 hPa.
  Confirm these are genuine forecast fields at the 24h-ish lead, not analysis-only — this is the
  exact thing that was unavailable leakage-safe on Open-Meteo, so it's the headline check.
- **Moisture:** `RH:2 m`, `DPT:2 m` (dew point), `SPFH:2 m` (specific humidity), `PWAT`
  (precipitable water). Note that dew-point-vs-temperature spread is derivable from fields you
  already have plus these — but only report ingredient availability; derive nothing.
- **Pressure / synoptic:** `PRMSL` (mean sea-level pressure), `PRES:surface`. (Pressure *tendency*
  would be derived from consecutive fields later — just confirm the base fields.)
- **Precipitation** (of interest for Reno): `APCP` (accumulated precip), `PRATE` (precip rate),
  `SNOD` (snow depth) / `WEASD`. Note accumulation windows.

---

## Task 1 — build the availability map

For a small sample of dates — at least the **v16 floor (2021-03-24)** and a **recent pre-test date**
(e.g. 2025-06-15), all outside the sealed year — pull the `.idx` inventory of the relevant GRIB
files (at the cycle/forecast-hour the lead convention selects) and, for each candidate variable:
- record the **exact GRIB label and level** as it appears (or that it's absent);
- confirm a **real non-null value** by byte-range-fetching one message (the F35 method);
- record whether it's **present at both dates** (i.e. back to the v16 floor) or only recently;
- record whether it's **instantaneous or averaged/accumulated**, and over what window.

One location's grid is enough to establish that a variable exists in the files (the inventory is
global); spot-check a value at one or two airports' grid points. Don't pull all five, don't pull a
date range.

## Task 2 — report the map, by family

A table per family: variable · exact GRIB label/level · present at v16 floor? · present recent? · at
the 24h forecast lead? · instantaneous/averaged (+window) · notes. Then a one-paragraph read per
family: is it **available and clean** (usable as-is), **available but awkward** (e.g. averaging
window needs care), or **absent**. Call out the **upper-air** result specifically — whether the
pressure-level fields GRIB is expected to carry are genuinely there at the forecast lead, since that
family is the one the GRIB build was supposed to unlock.

**Do not rank or order the families for experiments** — that's the next planning step, and it should
be done with this map in hand, not pre-empted here.

## What NOT to do

- **Do not pull bulk/date-range data, model anything, engineer or derive any feature, or run any
  experiment** — this is availability only.
- **Do not decide the experiment ordering** (E1/E2/…), or which family to try first — report the
  map; the ordering is planned separately with the map in view.
- **Do not use any data before 2021-03-24** (v15) as available — report back-extent honestly against
  the v16 floor.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not commit.**
- **Do not exceed scope** — the availability map, nothing else.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the per-family availability tables and reads (Task 2), with the upper-air result
   called out.
2. **Append one DECISIONS finding** (append-only; next sequential — check the tail, likely **F97**):
   the feature-availability map — which families/variables exist, their exact labels/levels, the
   back-extent, and the instantaneous-vs-averaged nature of each. Note explicitly that no ordering
   was decided and no feature was pulled or built.
3. **Refresh STATUS.md** to record session 47 and that the feature-availability map now exists,
   feeding the feature-experiment planning.
4. **Save** sample extracts + `.meta.txt` under `data/raw/diagnostics/session47/`.
5. **Archive step (routine):** move any entry that became settled per the criterion (likely none —
   a probe settles nothing). Check and state.
6. **Consistency check:** new DECISIONS number next-sequential and unique; every "present" claim
   traces to a saved extract; no bulk pull, no model, no feature built; no sample from the sealed
   year; `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only expected files.
7. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the body,
   `--` not em-dashes, short body — then **stop and wait for the owner's review.**
