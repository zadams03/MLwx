# Session 31 — data-availability probe for richer features (confirm-and-extend F7)

## Scope — one job, then stop

A pure **data-availability probe** on the Open-Meteo Previous Runs API, confirming
and extending F7/D17 for the richer-features phase. This session **settles what
feature data exists and how far back**, at the `previous_day1` offset, at all five
airports. It **builds nothing, joins nothing, fits nothing, evaluates nothing, and
computes no forecast or error figure.** Report the three findings and stop at the
end-of-session steps for the owner's review.

Three open items, all in one pass:

1. Pin the cloud/wind archive start date to the day (confirm the ~2024-01-19
   hypothesis).
2. First-ever probe of 925/850 hPa temperature on this API/offset — the
   strategically important one; report clearly whether it is free, unavailable, or a
   separate-source project.
3. Replicate availability across all five airports, US sites included, sampled
   outside the sealed test year.

## Standing rules that bind this session (SPEC §2)

- **Sample only outside the sealed test year** (2025-08-01 → 2026-07-31). Every probe
  date must be ≤ 2025-07-31 (from-Dubbo-onward convention, F49).
- Forecast source pinned to **`models=gfs_global`** (D16); the **`previous_day1`**
  offset only.
- **Drop-count-report, never fill** (SPEC 2.2): report present / null / rejected per
  variable per date; never interpolate or invent a value.
- **Raw is immutable, with provenance** (SPEC 2.3): save every probe response
  untouched under `data/raw/diagnostics/session31/`, each with a `.meta.txt`
  recording the exact query URL and pull time (UTC).
- A variable is **"present"** for a date only if it returns **non-null real values** —
  not merely HTTP 200 (F7 convention: "72/72 present" vs "0/72 — all null").

## Reference — airports (positions from SPEC 3.4; Open-Meteo snaps to its own grid)

| code | lat | long |
|---|---|---|
| EGLC | 51.5053 | 0.0553 |
| LFPG | 49.0153 | 2.5344 |
| DSM  | 41.534  | -93.6531 |
| YSDU | -32.2167 | 148.5747 |
| RNO  | 39.4839 | -119.7711 |

Endpoint: `https://previous-runs-api.open-meteo.com/v1/forecast`
Query shape: `?latitude=<lat>&longitude=<long>&hourly=<var>_previous_day1&models=gfs_global&start_date=<d>&end_date=<d>&timezone=UTC`

---

## Task 1 — pin the cloud/wind start date to the day

Known (F7/D17): `cloud_cover` and `wind_speed_10m` are all-null at 2021-03-24 and
present by 2024-07-01; D17 hypothesises they begin where the 492-hour forecast gap
ends (**2024-01-19 12:00 UTC**).

- At **EGLC**, find the first non-null hour for `cloud_cover_previous_day1` and
  `wind_speed_10m_previous_day1` exactly. Bracket then step day-by-day across
  2023-12-20 → 2024-02-01. Report the first real hour for each variable.
- State plainly whether that first hour **equals the gap end (2024-01-19 12:00 UTC)**,
  precedes it, or follows it.
- Confirm the same first-real-value date at the other four airports with a **targeted
  check a few days either side of the EGLC result** — not a full re-scan. Flag any
  airport that differs.
- In the same scan, co-probe `dew_point_2m` and `relative_humidity_2m` and report
  their start dates too. These are wave-two features — **informational only, they
  gate nothing in this phase** — but the scan is free, so capture them now.

## Task 2 — 925/850 hPa temperature: first-ever probe (give this real care)

Upper-air temperature has **never been probed** on this project. Settle which of three
it is:
- **(a) free** — on the Previous Runs API at `previous_day1`, reaching back far enough
  to be usable;
- **(b) unavailable** — rejected, or accepted-but-all-null everywhere;
- **(c) separate-source** — exists on Open-Meteo but not on this API/offset, so it
  would need the archive/GRIB route (a real second-source engineering lift).

Steps:

- **The variable string is uncertain — try multiple candidate spellings and report
  each outcome verbatim** (accepted+values / accepted+null / HTTP-rejected with the
  exact error text), the way F6 handled model-name spellings. Try at minimum
  `temperature_925hPa_previous_day1` and `temperature_850hPa_previous_day1`, plus the
  obvious variants the docs suggest (casing, any pressure-level parameter form).
- For any spelling returning real values, establish **how far back** it reaches using
  the temperature date ladder: 2021-03-24, 2023-07-01, 2024-07-01, and a recent
  pre-test date (e.g. 2025-06-15). Report present/null counts per date. **Note
  explicitly whether upper-air reaches further back than cloud/wind** — if 925/850 hPa
  runs to 2021 while cloud/wind starts 2024, that materially changes the two-tier
  design for Reno, so call it out.
- Run at **all five airports**, calling out **DSM and RNO** specifically: upper-air on
  a CONUS-capable provider is exactly where availability or model identity could
  differ (cf. the `gfs_seamless` divergence, F40). For any returned upper-air data,
  confirm it is genuinely GFS under the `gfs_global` pin, not a silent CONUS-model
  swap.
- End Task 2 with a **one-line verdict — free / unavailable / separate-source — plus
  the evidence behind it.**

## Task 3 — five-airport availability table

For a recent pre-test anchor (e.g. 2025-06-10 → 2025-06-12), tabulate **present /
null / rejected** for each of `temperature_2m` (control), `cloud_cover`,
`wind_speed_10m`, `dew_point_2m`, `relative_humidity_2m`, `temperature_925hPa`,
`temperature_850hPa` — all at `previous_day1` — at every airport. This is the
at-a-glance "what's available where" table for the phase.

---

## What NOT to do

- **Do not build, join, fit, or evaluate anything.** No feature matrix, no model, no
  MAE, no skill score, no corrected forecast. This session only measures availability.
- **Do not touch the sealed test year.** No probe date may fall in 2025-08-01 →
  2026-07-31, for any airport, for any variable.
- **Do not modify `SPEC.md` or `RESULTS.md`.** (The deferred RESULTS.md EGLC/LFPG
  wording fix is for the next docs session, not this one.)
- **Do not decide the richer-features design.** If the upper-air result forces a
  design choice (e.g. two-tier window vs a second source), **flag it as a question for
  the owner** in the DECISIONS draft — do not resolve it here.
- **Do not fill, interpolate, or "clean" any null.** Report it as null and count it.
- **Do not commit.** Prepare changes and a suggested message only.
- **Do not exceed this scope.** Anything else worth doing gets logged as a question,
  not acted on.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report the three findings** clearly in the session output: cloud/wind exact start
   date and whether it matches the gap end; the upper-air verdict with per-spelling and
   per-date evidence; the five-airport availability table.
2. **Append one DECISIONS finding** (append-only). Check the tail of DECISIONS.md for
   the next sequential number first — likely **F85** — and use whatever is actually
   next. Include all three results, cite the probe files saved, and flag any owner
   question the upper-air result raises rather than deciding it.
3. **Refresh STATUS.md** to record session 31's result. Also note that STATUS's prior
   "SPEC §1 Reno still reads in-progress" item is now **stale** — SPEC §1 already reads
   "failed".
4. **Save all probe responses** untouched under `data/raw/diagnostics/session31/`, each
   with its `.meta.txt` (exact query URL + UTC pull time).
5. **Consistency check** before stopping: the new DECISIONS number is the next
   sequential one; every figure reported traces to a probe file just saved; STATUS and
   DECISIONS agree; and `SPEC.md` and `RESULTS.md` are unmodified (`git status` to
   confirm only STATUS.md, DECISIONS.md, and the new `data/raw/diagnostics/session31/`
   files changed).
6. **Write a suggested commit message** (do not run it). Then **stop and wait for the
   owner's review.** Commit commands come only after review.
