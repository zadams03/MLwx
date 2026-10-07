# Session 08 — open Stage 2 (CDG) and verify it on contact

## What this session is

Stage 1 passed (F16). This opens **Stage 2 — a second airport, Paris Charles
de Gaulle (CDG)** — whose job is to prove the recipe travels: the same method
that worked at London City, run at a genuinely different location, with only
the **location** changed.

This first Stage 2 session is a **verify-on-contact** check, mirroring
session 01 for EGLC. It confirms both data sources carry CDG and are usable,
**before** any full pull, SPEC design, or modelling.

Do **not** pull the full dataset. Do **not** build or train anything. Do
**not** write the Stage 2 SPEC design yet (that comes once the data is
verified). Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — especially 2.2 (drop-count-report) and 2.3 (raw data
immutable + provenance).

## What we already know about CDG (confirm on contact, do not assume)

- ICAO code **LFPG**; IATA CDG. On IEM in the **`FR__ASOS`** network.
- Approx coordinates **49.010°N, 2.548°E**, elevation **~119 m** (much higher
  than EGLC's ~5 m — a genuinely different setting, which is the point).
- Use the authoritative coordinates from IEM's own station metadata for the
  forecast pull, and report exactly what you used.

## Preamble — record the Stage 2 opening decisions (append to DECISIONS)

- **D26 — Stage 2 opened: second airport CDG/LFPG.** Target: temperature at
  **12:00 UTC** at LFPG — the **same fixed hour as Stage 1**, kept identical on
  purpose so Stage 2 changes only the location. Method, feature set (D19),
  train/test split dates (D13), pairing rule (D14), missing-data rule (2.2),
  and the frozen bar (SPEC 5.3) are all **reused unchanged** from Stage 1,
  pending verification that CDG's data supports them.
- **D27 — target-hour convention for Stage 3 (noted, not acted on).** When
  airports are pooled at Stage 3, the target hour will switch from a fixed UTC
  hour to **solar-standard-noon**: each airport's local standard-time noon,
  with daylight-saving deliberately ignored so the target stays a fixed UTC
  hour per airport all year (no seasonal jump) while the sun sits comparably
  across airports. Not applied to Stage 2 — recorded now so the decision is
  made deliberately when pooling needs it.

## Part A — verify the forecast source for CDG

- Open-Meteo **Previous Runs API**, model **`gfs_global`**,
  `temperature_2m_previous_day1`, at CDG's coordinates.
- Pull a **small recent sample** (e.g. a few weeks) to confirm the API works
  and see the grid point returned (report its lat/lon, distance from the
  airport, and elevation — the EGLC grid point was ~4 km off; CDG's may differ).
- Make a **separate** small request around **24 March 2021** to confirm the
  archive reaches back as far as it does for EGLC (F1). Report plainly whether
  early-2021 data comes back.
- Save samples untouched in `data/raw/` with a `.meta.txt` each (SPEC 2.3), or
  clearly mark them as throwaway probes — your call, but keep provenance.

## Part B — verify the truth source for CDG

- IEM ASOS/METAR, station **LFPG**, network `FR__ASOS`.
- Pull a small recent sample over the **same period** as Part A.
- **Critically: check CDG's report timing.** EGLC reports at `:50` (and `:20`),
  which is why D14 pairs the `:50` report with the on-the-hour forecast. CDG
  may report at different minutes past the hour. Report **what minute(s) past
  the hour LFPG reports at**, so we know whether D14's pairing rule applies
  as-is or needs adapting for Stage 2. This is the key CDG-specific unknown.
- Count gaps in the sample (drop-count-report, 2.2) — do not fill.

## Part C — what to report

Paste **real output**, not descriptions:
- the CDG coordinates used and the forecast grid point returned (distance,
  elevation);
- whether the forecast archive returns data around 24 March 2021 (yes/no);
- the shape of each sample (rows, columns, date range);
- **LFPG's report timing** — which minute(s) past the hour — and whether the
  D14 `:50` pairing rule applies as-is or needs adapting;
- gap counts in each sample;
- a plain first read: is CDG's data usable for Stage 2 the same way EGLC's was?

## What NOT to do

- Do not pull the full multi-year dataset (that is the next session).
- Do not build, train, join, or evaluate anything.
- Do not write the Stage 2 SPEC design yet.
- Do not fill missing data; drop and count.
- Do not touch or re-run anything from Stage 1.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: Stage 2 is open; this session verified CDG on contact;
   next is the Stage 2 SPEC design + full pull (if the data checks out), or a
   decision if it does not.
2. Append the verification findings to DECISIONS (and D26, D27). Note any new
   open questions (e.g. if the pairing rule needs adapting for CDG).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
