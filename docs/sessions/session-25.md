# Session 25 — open airport #5 (a mountain-valley airport) and verify on contact

## What this session is

Four flat/temperate airports have passed — all places where GFS is already
reliable. Airport #5 tests something new: a **genuinely terrain-affected
mountain-valley airport**, where GFS's coarse grid cannot resolve the terrain
and its local bias should be **large**. The question is whether the correction
delivers its biggest wins where the raw model is worst — the method's actual
selling point.

This is a **verify-on-contact** session, mirroring session 19, **before** any
full pull, SPEC design, or modelling. It confirms the airport is usable, settles
its target hour, and — new for a mountain airport — measures the **grid-point
altitude mismatch**, which will be large and matters a lot here.

Do **not** pull the full dataset, build, train, write SPEC design, or edit SPEC.
Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, DECISIONS.md in full (and
DECISIONS-archive.md only if deep history is needed). Critical rules (SPEC 2)
apply — especially 2.2 and 2.3.

## Choosing the station — hard but not pathological (confirm on contact)

The brief is a **broad mountain-valley US airport**: genuinely terrain-affected
and high-altitude, but **not** a pathological narrow-valley case where GFS's grid
point describes an essentially different location and the bias becomes
unlearnable noise. Good candidates: **Bozeman (KBZN)** or **Reno (KRNO)** —
mountain-valley, high, terrain-affected, but broad enough to be interpretable.
Avoid extreme narrow-valley cases like Aspen.

US so IEM's record is pristine — the point is to make **terrain the only new
variable**, not data quality.

**Pick the best candidate:** query IEM station metadata for the candidates,
choose the one that (a) exists with authoritative coordinates and elevation,
(b) reports temperature routinely and hourly, (c) is genuinely mountainous but
broad-valley. Report which you picked, its elevation, and why. Use IEM's own
metadata coordinates for the forecast pull.

## The target hour — compute it (local-standard-noon convention, D27/D33)

Confirm the station's standard-time offset from IEM metadata and compute
**local standard noon in UTC** (DST ignored, per the convention). US Mountain
Time is UTC−7 (so ~19:00 UTC); US Pacific is UTC−8 (so ~20:00 UTC) — but
**confirm from the station's actual timezone**, don't assume. Report the hour.

## The mountain-specific check — grid-point altitude mismatch (important)

At the flat airports the forecast grid point sat within a few metres of the
airport's elevation. At a mountain airport it may be **hundreds of metres off**,
because Open-Meteo's smoothed grid-cell elevation cannot resolve the valley.
**Measure and report the mismatch explicitly** (airport elevation vs grid-point
elevation). This matters because a large fixed altitude offset produces a large,
roughly-constant bias — which the mean-bias reference will partly capture. Flag
that the mean-bias comparison will be the one to watch at evaluation: ML beating
it well means terrain-dependent structure was learned; ML barely beating it
means the bias is mostly a fixed altitude offset.

## Preamble — record the opening decisions (append to DECISIONS)

- **D40 — fifth airport opened (a mountain-valley airport).** Rationale: the
  first hard/terrain-affected case, testing whether the correction delivers its
  biggest wins where GFS is worst. US for pristine data so terrain is the only
  new variable. Broad-valley not pathological, so the bias stays interpretable.
- **D41 — its target hour is local standard noon = (the confirmed UTC hour).**
  Same convention as all airports (D33). Record that, like DSM and Dubbo, this
  airport changes location and target hour vs the European pair (D33 caveat).
- **Set expectations honestly (record as a note):** GFS is expected to be
  **much worse** here (raw MAE possibly 2–4°C+, not the ~1.2–1.8 of the flat
  airports). A big correction is the exciting outcome; a modest win, or finding
  the three features (temperature + season) are not enough for terrain-driven
  bias, is equally informative and may be the airport that motivates richer
  features (cloud, wind) later. This is a genuine test of the minimal feature
  set, not just another confirmation.

## Part A — verify the forecast source

- Open-Meteo **Previous Runs API**, model **`gfs_global`**,
  `temperature_2m_previous_day1`, at the station's coordinates.
- Pull a **small sample from OUTSIDE the test year** — a few weeks in **2024**
  (Q29 fix). Report the grid point (lat/lon, distance, **elevation** — the key
  mountain figure).
- Probe around **24 March 2021** to confirm archive reach. Report yes/no.
- Run the `gfs_global` vs `gfs_seamless` comparison at this point (out-of-test-
  year window). DSM (F40) showed they differ inside CONUS, and this is a CONUS
  mountain point where a high-resolution model in `seamless` could differ even
  more — so this check matters. Use `gfs_global` regardless (D16); report the
  result.
- Save samples untouched with `.meta.txt`, or mark throwaway — keep provenance.

## Part B — verify the truth source

- IEM ASOS/METAR for the chosen station and network (US `**_ASOS`).
- Small sample from outside the test year (same 2024 window).
- Units/timezone: confirm `tz=Etc/UTC` returns UTC and the temperature field
  converts to Celsius as the pipeline does (US Fahrenheit-derived, like DSM).
- **Report timing:** minute(s) past the hour, hourly cadence (US ASOS usually
  `:53`/`:54`). Report whether D14 applies at the computed target hour.
- Count gaps (drop-count, 2.2) — do not fill.

## Part C — what to report

Paste **real output**:
- which station chosen, its elevation, and why; coordinates used;
- **grid point distance AND elevation mismatch** (the key mountain figure);
- confirmed local-standard-noon UTC hour with the offset check;
- archive-reaches-2021 yes/no; the `gfs_global` vs `gfs_seamless` result;
- units/timezone confirmation; report cadence and timing;
- gap counts; a plain read: is this airport usable the same way, and how large
  is the raw GFS error looking versus the flat airports (rough sense only, from
  the out-of-test-year sample — not a test-year figure).

## What NOT to do

- Do not pull the full dataset; do not build/train/join/evaluate.
- Do not write SPEC design or edit SPEC.
- Do not sample from inside the test year (2025-08-01 on) — Q29 fix.
- Do not fill missing data; drop and count.
- Do not touch or re-run the four existing airports.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: airport #5 (mountain) opened and verified; next is its SPEC
   row + full pull, if the data checks out (flag the altitude mismatch and any
   cadence concern).
2. Append findings to DECISIONS (and D40, D41). Note the Q29 fix was applied.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
