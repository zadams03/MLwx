# Session 19 — open airport #4 (inland eastern Australia) and verify on contact

## What this session is

Three airports (EGLC, CDG, DSM) have passed, but all three were tested on the
**same twelve months**. Airport #4 continues broadening the evidence and builds
toward eventual pooling. It is a **Southern Hemisphere** airport — genuinely
independent weather **and flipped seasons** — chosen inland and temperate so
GFS stays reliable and the airport stays well-behaved.

This is a **verify-on-contact** session, mirroring session 14 for DSM, **before**
any full pull, SPEC design, or modelling. It confirms the airport is usable and
settles its target hour.

Do **not** pull the full dataset, build, train, write SPEC design, or edit SPEC.
Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — especially 2.2 (drop-count-report) and 2.3 (provenance).

## Choosing the station (confirm on contact — do not assume)

The region is **inland eastern Australia**, temperate and flat-ish (not
coastal, not alpine). Likely candidates: **Canberra (YSCB)** or **Dubbo
(YSDU)**. IEM carries global stations, typically under an **`AU__ASOS`**-style
network.

**First, confirm the station exists and pick the best one:** query IEM's
station metadata for the candidate(s) and choose the one that (a) exists on IEM
with authoritative coordinates, (b) reports temperature routinely, and (c) is
inland/temperate. Report which you picked and why. Use IEM's own metadata
coordinates for the forecast pull.

## The target hour — compute it, do not assume

Eastern Australia's standard offset is **UTC+10** (ignore daylight saving, per
D27/D33's convention). So local standard noon (12:00) is **02:00 UTC** — a
third distinct target hour after 12:00 (Europe) and 18:00 (DSM). **Confirm on
contact:** read the chosen station's timezone from IEM metadata, verify the
standard-time offset, and report the local-standard-noon UTC hour. (Note: parts
of eastern Australia observe DST and parts do not — use the **standard** offset
regardless, per the convention, and report which state/timezone the station is
in.)

## Preamble — record the opening decisions (append to DECISIONS)

- **D36 — fourth airport opened (inland eastern Australia).** Rationale:
  Southern Hemisphere, independent weather, flipped seasons — broadens the
  evidence beyond the Northern Hemisphere and stress-tests the season-based bias
  features; inland/temperate so GFS stays reliable. Continues the "individual
  airports (2+)" stage (D34) and accumulates toward eventual pooling.
- **D37 — its target hour is local standard noon = (the confirmed UTC hour,
  expected 02:00 UTC).** Same local-midday principle as all airports (D33); a
  third distinct UTC hour. Record that, like DSM, this airport changes location
  and target hour vs the European pair — the same honest caveat (D33).

## Part A — verify the forecast source

- Open-Meteo **Previous Runs API**, model **`gfs_global`**,
  `temperature_2m_previous_day1`, at the station's coordinates.
- Pull a **small sample from OUTSIDE the sealed test year** — e.g. a few weeks
  in **2024** (NOT July 2026). This is the **Q29 fix**: keep verification wholly
  clear of test-year data so the "test year never seen" claim stays literally
  true. Report the grid point returned (lat/lon, distance, elevation).
- Separately, probe around **24 March 2021** to confirm the archive reaches back
  as far as it does elsewhere (F1/F20/F33). Report yes/no.
- **Q30-adjacent — the `gfs_seamless` check:** Australia is outside CONUS, but
  DSM (F40) showed the Europe-only reasoning does not travel. Run the value-by-
  value `gfs_global` vs `gfs_seamless` comparison at this point (using an
  out-of-test-year window). Use `gfs_global` for everything regardless (D16);
  the comparison just records whether they differ here. Report and note.
- Save samples untouched in `data/raw/` with `.meta.txt`, or mark as throwaway
  probes — keep provenance.

## Part B — verify the truth source (non-US checks)

- IEM ASOS/METAR for the chosen station and network.
- Pull a small recent sample **from outside the test year** (same 2024 window).
- **Units/timezone:** confirm `tz=Etc/UTC` returns UTC and the temperature field
  the pipeline already converts to Celsius works here — Australian METARs report
  whole-degree Celsius natively, so confirm the conversion still lands correctly
  and report a few values.
- **Report timing:** check what minute(s) past the hour the station reports at,
  and whether it reports **hourly or less often** (non-US stations sometimes
  report every 30 min or only every 3 hours — this is the key risk for a
  non-US, non-European airport). Report the cadence and whether D14 pairing
  applies as-is at the ~02:00 UTC target.
- Count gaps in the sample (drop-count, 2.2) — do not fill.

## Part C — what to report

Paste **real output**:
- which station chosen and why; coordinates used; grid point (distance, elev);
- confirmed local-standard-noon UTC hour, with the timezone/offset check;
- archive-reaches-2021 yes/no;
- the `gfs_global` vs `gfs_seamless` result at this point;
- units/timezone confirmation; **report cadence and timing** (the main risk);
- gap counts; a plain read: is this airport usable the same way the others were,
  or does its report cadence need handling?

## What NOT to do

- Do not pull the full dataset; do not build/train/join/evaluate.
- Do not write SPEC design or edit SPEC.
- Do not sample from inside the test year (2025-08-01 onward) — Q29 fix.
- Do not fill missing data; drop and count.
- Do not touch or re-run EGLC, CDG or DSM.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: airport #4 opened and verified on contact; next is its SPEC
   row + full pull, if the data checks out (flag if report cadence needs care).
2. Append findings to DECISIONS (and D36, D37). Note this session applied the
   Q29 fix (verification sampled outside the test year).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
