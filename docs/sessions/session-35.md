# Session 35 — GFS GRIB source feasibility probe (availability only, no build)

## Scope — one job, then stop

Decide whether a **real GFS forecast archive in GRIB form** can give cloud cover and
10 m wind speed back to ~2021 — closing the ~1.5-year feature gap that F85 pinned and
that session 33's CV showed is the binding constraint on the richer-features result. This
is an **availability-and-cost probe only**, the same shape as session 31: it establishes
what exists, how far back, at what lead time, and how hard it would be to align — and
then **stops**. It **builds no pipeline, downloads no bulk history, decodes no full
dataset, trains nothing, joins nothing.**

The output is a **go/no-go feasibility verdict** for the owner: is a deep GRIB source
**cheap enough to be worth building** (→ build it, then lock the richer method on the full
~4.3-year window), or **costly/unavailable enough** that the pragmatic move is to lock the
richer method on the short ~1.5-year window and accept LFPG's caveat.

## Why this, why now

Session 33 established the features carry real out-of-fold value at 4/5 airports
(including a positive Reno signal), and that the short window — not the features — is what
holds the result back (LFPG can't beat raw GFS on 1.5 years; margins are thin elsewhere).
The one clean way to a full-strength, one-shot sealed test is cloud/wind back to 2021. The
only leakage-safe source for that is a **genuine archived GFS forecast** (NOT ERA5
reanalysis, which assimilates observations and would leak). Before committing to that
build, this probe checks it's actually feasible — cheap-probe-before-expensive-build, the
discipline that's paid off three sessions running.

## Standing rules that bind this session (SPEC §2)

- **Leakage safety is the whole point.** Any candidate source must provide a *genuine past
  forecast* at a fixed lead time (the 24 h-ahead value as issued), not an analysis or
  reanalysis. Reanalysis (ERA5 and similar) is **excluded** and does not count as a hit.
- **Probe, don't build.** Fetch at most a handful of single-cycle sample files to prove a
  point — never a bulk date range. No decoding of a full series, no storage of history.
- **Sample outside the sealed test year** (≤ 2025-07-31) for any value you actually pull.
- **Raw is immutable, with provenance** (2.3): save any sample file untouched under
  `data/raw/diagnostics/session35/` with a `.meta.txt` (exact source URL/query + UTC pull
  time). If a source needs credentials you don't have, record that as a finding — do not
  attempt to obtain them.
- **You never commit.** Prepare changes and a suggested message for the owner.

## Reference — what has to be true for a source to be usable

The richer method needs, per airport, the **GFS forecast of `cloud_cover` and
`wind_speed_10m` valid at the target hour, issued ~24 h earlier** (the `previous_day1`
equivalent), back to ~2021-03-24, at the five airport points (SPEC 3.4). A source is only
a "go" if it can deliver that leakage-safely and be aligned to the existing
temperature/observation rows.

---

## Task 1 — identify the candidate GFS forecast archives

Survey the realistic sources of archived GFS **forecast** GRIB2 (not analysis, not
reanalysis). Cover at least:
- **NOAA NODD / cloud archives** (the GFS buckets on AWS/Google/Azure open-data) — how far
  back does forecast history reach, and does it include the sub-daily cycles and forecast
  lead hours needed?
- **NOMADS / NCEI** archived GFS products.
- Any well-established mirror of historical GFS GRIB.

For each: earliest forecast date available, whether it carries the needed variables
(total cloud cover, 10 m wind components u/v) at surface, the archived forecast lead
hours, cycle frequency, access method (HTTP/S3/API), and whether credentials are needed.
Report as a short comparison, not prose.

## Task 2 — confirm the two variables exist in the GRIB, back to ~2021

For the single most promising source, **fetch one or two individual sample GRIB2 files**
(one recent pre-test date, one near 2021-03-24) and confirm by inspecting their inventory
(e.g. the `.idx`/grib inventory, or a light `wgrib2 -s` / `pygrib` listing) that they
contain:
- total cloud cover,
- 10 m U and 10 m V wind (from which wind speed is derived),
at a **24 h forecast lead** from a cycle that would be valid at a target hour.

Report the exact GRIB variable/level names found. Do **not** download a date range — one
or two files is the whole of what this task needs.

## Task 3 — the alignment-cost assessment (the part that decides "worth it")

The reason this project's pipeline is clean is that Open-Meteo handed back
point-interpolated values at a fixed offset. A raw GRIB source reintroduces the work
Open-Meteo did for us. Assess, concretely, the cost of getting from GRIB to a row that
joins the existing data:
- **Grid → point:** GFS GRIB is a lat/long grid; the airports are points. What
  interpolation is needed, and does it match how Open-Meteo picked its grid point (so the
  new cloud/wind align with the existing `gfs_global` temperature)? Note any mismatch risk.
- **Lead-time / cycle bookkeeping:** which cycle + forecast hour reproduces the
  `previous_day1` (24 h-ahead, valid at target hour) definition, per airport target hour?
- **Volume / time:** rough size and fetch time to pull ~4.3 years of the needed cycles for
  five points (order-of-magnitude, to judge feasibility — not a plan to do it now).
- **Failure modes:** archive gaps, format changes over 2021→2025, variable-name drift.

## Task 4 — feasibility verdict (report, do not decide)

Give a clear, evidence-backed one-paragraph verdict in one of three shapes:
- **GO-CHEAP** — a source carries both variables back to ~2021 and alignment is
  tractable; recommend building it before locking.
- **GO-COSTLY** — available but the alignment/volume lift is substantial; lay out the cost
  so the owner can weigh it against locking the short window.
- **NO-GO** — not leakage-safely available back to 2021; the short-window lock is the
  realistic path.
State the verdict; **flag the build-vs-lock decision for the owner rather than taking it.**

---

## What NOT to do

- **Do not build any pipeline, download any bulk/date-range history, or decode a full
  dataset.** One or two sample files, no more.
- **Do not use ERA5 or any reanalysis** as a candidate — it leaks and is out of scope.
- **Do not pull any sample from inside the sealed test year** (2025-08-01 → 2026-07-31).
- **Do not train, join, fit, or evaluate anything**, and do not modify the existing
  feature or temperature data.
- **Do not decide build-vs-lock** — report the feasibility verdict and flag it.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not commit.**
- **Do not exceed scope** — log anything else as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Tasks 1–4: the source comparison, the confirmed GRIB variable names with the
   two sample dates, the alignment-cost assessment, and the feasibility verdict.
2. **Append one DECISIONS finding** (append-only; check the tail of live DECISIONS.md for
   the next sequential number — likely **F88**). Record the candidate sources, what the
   sample files proved about variable availability back to ~2021, the alignment cost, and
   the GO-CHEAP / GO-COSTLY / NO-GO verdict. **Flag — do not decide — the owner's
   build-vs-lock choice.**
3. **Refresh STATUS.md** to record session 35 and its verdict.
4. **Save** any sample GRIB files + `.meta.txt` provenance under
   `data/raw/diagnostics/session35/`.
5. **Archive step (now routine):** move any entry that became settled this session to
   `DECISIONS-archive.md` per the criterion. (Likely none this session — a probe rarely
   settles an existing entry — but check and state so.)
6. **Consistency check:** the new DECISIONS number is next-sequential and unique; every
   claim traces to a source checked or a sample file saved; no sample came from the sealed
   test year; STATUS and DECISIONS agree; `SPEC.md` and `RESULTS.md` unmodified
   (`git status` to confirm only expected files changed).
7. **Write a suggested commit message** — short title line is fine (keep the body brief to
   avoid shell-paste trouble; detail lives in F88) — then **stop and wait for the owner's
   review.**
