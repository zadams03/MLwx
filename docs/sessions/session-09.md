# Session 09 — generalise SPEC to multiple airports (Stage 2 design)

## What this session is

Stage 2 is open (D26), so SPEC must stop describing a one-airport project and
start describing a **per-airport** one that cleanly holds EGLC (Stage 1, done)
and CDG (Stage 2), and extends to more airports later. This session makes that
change — **documentation only**.

**No data pulled. No model. No join.** This is a careful edit of proven SPEC
sections, so it is kept separate from the CDG pull (which is the next session)
to make review clean.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply. **The meaning of the frozen evaluation bar must not
change** — only its *scope* generalises to "per airport". If any edit would
alter what the bar requires, stop and flag it.

DECISIONS is append-only. The SPEC edits below are all authorised; make these
and only these.

---

## The guiding idea

One set of rules, parameterised by airport. Shared things (data sources, the
method, the split dates, the pairing rule, the missing-data rule, the bar)
stay stated once. Per-airport things (ICAO code, network, coordinates, grid
point, report timing, and each airport's result) live in a small **airport
table** that grows by one row per airport.

Each airport gets the **same treatment**: same 12:00 UTC target, same D13 split
dates, same rehearse-on-a-validation-year-then-single-sealed-test discipline
(D18), same frozen bar judged once on that airport's own test year.

## The authorised edits

**E-1. §1 (what the project does).** Change the singular "The airport is London
City (EGLC)" so the project is described as correcting GFS bias at airports —
currently **EGLC (Stage 1, passed)** and **CDG (Stage 2, in progress)** — with
more to follow. Keep it plain and short.

**E-2. §3 (data sources) — add the airport table.** The sources are shared
(IEM for truth; Open-Meteo Previous Runs API, `gfs_global`, for forecasts).
Add a per-airport table with one row per airport, columns:
- ICAO code; IEM network; airport lat/lon/elevation (authoritative, from IEM);
- forecast grid point (lat/lon/elevation, distance from airport);
- report timing (minute past the hour the station reports at).
Fill both rows from verified values:
- **EGLC** — network GB__ASOS; 51.5053 N, 0.0553 E, 5 m; grid ~4.33 km off;
  reports at `:50` (and a scheduled `:20`).
- **LFPG** — network FR__ASOS; 49.0153 N, 2.5344 E, 109 m; grid 3.44 km off,
  no height mismatch; reports at `:00` (and a scheduled `:30`). (F17–F19.)

**E-3. §3.2 — keep the archive facts, note they hold for both airports.** The
24 March 2021 start and the single 492-hour forecast gap are stated already
for EGLC. Note that CDG's archive also begins 2021-03-24 (F20); whether CDG has
its own forecast gap is **not yet known** and will be checked in the pull
session (leave a clear "to be verified" marker rather than assuming).

**E-4. §4.1 (target).** Generalise to: temperature at **12:00 UTC** at each
airport — the same fixed hour for all, so cross-airport comparison changes only
the location (D26). Note the future switch to solar-standard-noon at Stage 3
(D27).

**E-5. §4.5 (pairing).** State the rule generally: each 12:00 UTC forecast is
paired with the station's nearest report to the hour; if none falls within
15 minutes, the day is dropped and counted (2.2). Move the EGLC-specific "`:50`,
ten minutes earlier" detail into the airport table (E-2) — the general rule
does not name a minute. Note CDG reports on the hour, so it pairs exactly.

**E-6. §4.3 (split dates).** Confirm these are shared across airports: the D13
dates apply to every airport (CDG's archive supports them, F20). No change to
the dates themselves.

**E-7. §5 (evaluation) — generalise scope, not meaning.** The metric, the
baselines, and the bar are unchanged. State that they apply **per airport**:
each airport has its own train/validation/test split on the shared dates, and
the bar (beat raw GFS and persistence on MAE over that airport's test year) is
judged once per airport. Record EGLC's result as the Stage 1 record (F16:
corrected 1.040 vs raw GFS 1.242, a pass). CDG's result is pending.

**E-8. §5.4 (deeper evaluation) — resolve the stale wording (Q18).** It
currently says "parked until stage 1 passes"; Stage 1 has passed. The owner's
decision: the deeper evaluation (skill score, significance, cross-season
robustness) stays **optional and is not a blocker** — Stage 1 passed cleanly
and its season breakdown already gave partial robustness evidence. Reword so it
reads as an available option, not a required gate. Record as a decision.

**E-9. §6 (build order).** Mark **Stage 1 done** and **Stage 2 in progress**.
Update the closing note so it no longer says stages 2–6 are all empty — Stage 2
is open and its design now lives in the generalised sections above. Leave
Stages 3–6 as short descriptions still (do not design them).

## Also record (append to DECISIONS)

- **D28** — SPEC generalised to a multi-airport structure (Option A), chosen
  now while there are only two airports, to set up Stage 3 pooling cleanly.
- **D29** — the Q18 resolution (deeper evaluation optional, not a blocker).
- **Q19 resolved** — at CDG, take the drops from off-hour reports; do **not**
  adapt the pairing rule for CDG only, as that would weaken the "only the
  location changed" claim. Record and close.

## What to report at the end

- the before/after of each SPEC edit (E-1 to E-9);
- the airport table as written;
- confirmation the frozen bar's *meaning* is unchanged (only scope generalised);
- the new DECISIONS entries.

## What NOT to do

- Do not pull any data or build/join/train anything.
- Do not change the meaning of the frozen bar (SPEC 5) — scope only.
- Do not design Stages 3–6.
- Do not edit SPEC beyond E-1 to E-9.
- Do not change or delete existing DECISIONS entries (append only).
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: SPEC is now multi-airport; next is the CDG full pull +
   gap map (with the Q20 `gfs_global` confirmation and Q21 gap check folded in).
2. Ensure DECISIONS carries D28, D29, and the Q19 closure.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
