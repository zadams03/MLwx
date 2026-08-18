# Session 14 — open Des Moines (DSM) and verify it on contact

## What this session is

Stage 2 proved the recipe travels within western Europe (EGLC, CDG). But F30
flagged that both were tested on the **same twelve months** and, being ~330 km
apart, largely the **same regional summer** — so the two wins lean on one
weather year seen twice. This opens a **third airport in a different weather
region** to start addressing that: **Des Moines, Iowa (DSM)** — flat,
continental US interior, where GFS is reliable and IEM's record is at its
cleanest, and whose summers are uncorrelated with western Europe's.

This first DSM session is a **verify-on-contact** check, mirroring session 08
for CDG, **before** any full pull, SPEC design, or modelling. It also settles
the one thing that is genuinely different about DSM: the **target hour**.

Do **not** pull the full dataset. Do **not** build or train anything. Do
**not** write DSM's SPEC design yet. Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — especially 2.2 (drop-count-report) and 2.3 (raw data
immutable + provenance).

## What we already know about DSM (confirm on contact, do not assume)

- IEM station **DSM**, network **`IA_ASOS`** (Iowa — IEM's home network).
- US interior, flat, continental. Use the authoritative coordinates and
  elevation from IEM's own station metadata for the forecast pull, and report
  exactly what you used.

## The target-hour change — the key DSM-specific point

DSM is in US Central Time (standard offset **UTC−6**). So **12:00 UTC is
06:00 local** at DSM — near dawn and the coldest, most stable part of the day,
and exactly the transition zone the European airports' 12:00 UTC was chosen to
avoid. Testing DSM at 12:00 UTC would change the *time of day* as well as the
region, confounding the "does it travel?" question.

The owner's decision (Option B): **DSM's target hour is local-standard-noon**,
i.e. 12:00 Central Standard Time = **18:00 UTC**, with daylight-saving
deliberately ignored so it stays a fixed UTC hour all year (this is D27's
solar-standard-noon convention, brought forward for DSM). This keeps "local
midday" constant across airports.

**Confirm on contact:** DSM's standard-time offset is UTC−6, so local-standard-
noon is **18:00 UTC** year-round. Report the check. (At 18:00 UTC, local clock
time is 12:00 CST in winter, 13:00 CDT in summer — midday-to-early-afternoon,
matching how 12:00 UTC sat for the European airports.)

## Preamble — record the opening decisions (append to DECISIONS)

- **D32 — third airport opened: Des Moines (DSM).** Rationale: flat continental
  US interior, GFS-reliable, IEM home network (cleanest data), a genuinely
  different weather region from western Europe — chosen to attack the F30
  weather-year caveat (EGLC and CDG share one western-European summer; DSM's is
  uncorrelated). The owner's plan is "temperate and well-behaved first, then
  ramp up difficulty", so DSM is the easy off-continent step before harder,
  more independent airports and before Stage 3 pooling.
- **D33 — DSM's target hour is local-standard-noon (18:00 UTC), not 12:00 UTC.**
  Reason above. This brings D27's convention forward for DSM. **Honest
  consequence, recorded plainly:** DSM changes **both** the location and the
  target hour versus EGLC/CDG, so D26's "only the location changed" does not
  strictly hold for DSM. Holding *local midday* constant is the more meaningful
  thing to fix for a cross-region test than holding the UTC hour constant.
  Chosen on principle, before any DSM data was seen.

## Part A — verify the forecast source for DSM

- Open-Meteo **Previous Runs API**, model **`gfs_global`**,
  `temperature_2m_previous_day1`, at DSM's coordinates.
- Pull a **small recent sample** (a few weeks) to confirm the API works and see
  the grid point returned (report its lat/lon, distance from the airport,
  elevation).
- Make a **separate** small request around **24 March 2021** to confirm the
  archive reaches as far back as it does for EGLC/CDG (F1, F20). Report plainly.
- Save samples untouched in `data/raw/` with a `.meta.txt` each (SPEC 2.3), or
  clearly mark them as throwaway probes — but keep provenance.

## Part B — verify the truth source for DSM (US-specific checks)

- IEM ASOS/METAR, station **DSM**, network `IA_ASOS`.
- Pull a small recent sample over the **same period** as Part A.
- **Units and timezone (US-specific):** confirm the existing request approach
  (`tz=Etc/UTC`, temperature via the same field EGLC/CDG used) returns DSM data
  **in UTC** and in the **same temperature field and units** the pipeline
  already converts to Celsius. The goal is that DSM needs **no** new units or
  timezone handling — confirm this rather than assume it. Report the field used
  and a few converted values as a sanity check.
- **Report timing:** check what minute(s) past the hour DSM reports at (US ASOS
  routine METARs are often at `:53`). Report it, and whether the D14 pairing
  rule applies as-is for an **18:00 UTC** target (nearest routine report within
  15 minutes).
- Count gaps in the sample (drop-count-report, 2.2) — do not fill.

## Part C — what to report

Paste **real output**, not descriptions:
- DSM coordinates used and the forecast grid point returned (distance, elev);
- confirmation local-standard-noon = **18:00 UTC** (UTC−6 standard offset);
- whether the forecast archive returns data around 24 March 2021 (yes/no);
- the shape of each sample (rows, columns, date range);
- **units/timezone confirmation** — that DSM needs no new handling;
- **DSM's report timing**, and whether D14 applies as-is at the 18:00 UTC
  target;
- gap counts in each sample;
- a plain first read: is DSM usable for the recipe the same way EGLC/CDG were?

## What NOT to do

- Do not pull the full multi-year dataset (that is the next session).
- Do not build, train, join, or evaluate anything.
- Do not write DSM's SPEC design or edit SPEC (the target-hour generalisation
  into the per-airport table comes in the design/pull session).
- Do not fill missing data; drop and count.
- Do not touch or re-run anything from EGLC or CDG.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: DSM opened as the third airport; this session verified it
   on contact; next is DSM's SPEC design (generalise the target hour into the
   per-airport table, add DSM's row at 18:00 UTC) + full pull, if the data
   checks out.
2. Append the verification findings to DECISIONS (and D32, D33). Note any new
   open questions (e.g. if report timing or units need adapting). Note this
   partially addresses Q24 (what opens next).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
