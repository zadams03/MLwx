# Session 15 — DSM: generalise SPEC for per-airport hours, then the full pull

## What this session is

Two jobs, in order. First, **generalise SPEC** so it holds an open-ended list of
airports with a **per-airport target hour** — DSM breaks the current "12:00 UTC
at every airport" wording, and more airports are coming, so this is done to
scale, not patched. Second, **pull DSM's full history** and gap-map it, the same
job session 03b/10 did for EGLC/CDG.

The SPEC edits are the careful part and are done first so the pull runs against
an agreed spec. Both are in one session to stay lean, but the SPEC before/after
must be reported clearly for review.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply. **The meaning of the frozen evaluation bar (section 5)
must not change** — only the target-hour convention and the airport list
generalise. If any edit would alter what the bar requires, stop and flag it.

DECISIONS is append-only. The SPEC edits below are all authorised; make these
and only these.

---

## Part A — generalise SPEC (authorised edits only)

The guiding change: the **target hour becomes a per-airport fact** (like the
report minute already is), and **Stage 2 becomes "individual airports, 2+"**
rather than "the second airport", because the owner is adding more airports
before Stage 3 pooling (D32, and the owner's stated plan).

**A-1. §1 (what the project does).** The line "Every airport gets the same
treatment: the same target hour, the same split dates…" is no longer true —
the target hour now varies per airport. Reword so the shared things are the
split dates, the method, and the frozen bar, and the **target hour is chosen
per airport to sit at local midday** (see A-4). Update the airport list to add
DSM and reflect that EGLC and CDG have **passed** (F16, F30) and DSM is in
progress. Note more airports may follow.

**A-2. §3.4 airport table — add DSM and a target-hour column.**
- Add a **`target hour (UTC)`** column to the first table. Fill it: EGLC
  **12:00**, LFPG **12:00**, DSM **18:00**.
- Add DSM's row to both tables from session 14's verified values (F31–F37):
  network `IA_ASOS`, lat 41.534, lon −93.6531, elevation 294 m; grid point
  41.52945 / −93.63281, 285 m, 1.76 km away, −9 m mismatch; reports at `:54`;
  no second scheduled report (specials are genuinely unscheduled, F37); pairing
  offset at its 18:00 target = 6 minutes.
- Update the stage cells: EGLC `1 — passed`, LFPG `2 — passed`, DSM
  `2 — in progress`.

**A-3. §3.2 / §3.3 — note DSM.** The archive start (2021-03-24) and the
verify-on-contact checks now hold for DSM too (F31–F33): add DSM alongside EGLC
and CDG. (The 492-hour gap: whether DSM shares it is **not yet known** until
this session's pull — leave a "to be verified in this session's gap map"
marker, do not assume.)

**A-4. §4.1 (target) — the important edit: per-airport hour at local midday.**
Rewrite so the target is **one fixed hour per airport, chosen to sit at that
airport's local midday**, and stored in the airport table (3.4). Specifically:
- EGLC and CDG use **12:00 UTC** (local midday-to-early-afternoon in western
  Europe).
- DSM uses **18:00 UTC** = local standard noon (12:00 CST; 12:00 UTC would be
  06:00 local dawn — the exact hour the "why noon" reasoning rules out). D33.
- Keep the three "why local midday" reasons (daylight; stable/well-observed;
  avoids dawn/dusk) — they now justify *local* midday generally, not 12:00 UTC
  specifically.
- **Fold in D27 honestly:** this *is* the solar-standard-noon convention. D27
  had planned it for Stage 3; it is brought forward now because DSM needs it.
  State plainly that this means a DSM result reflects **location and target
  hour** changing together vs the European pair, so D26's "only the location
  changed" holds *within* western Europe (EGLC↔CDG) but not for DSM — DSM tests
  "does it travel to a different region at a comparable local time" (D33).

**A-5. §4.5 (pairing) — add DSM.** The rule is unchanged. Add DSM's `:54` /
6-minute-offset practical example alongside EGLC's and LFPG's. The pairing is
against each airport's **own** target hour now, not a global 12:00.

**A-6. §5.0 / §5.3 — generalise scope, preserve the bar.** Update the results
table: EGLC **PASSED**, LFPG **PASSED** (F30: corrected 1.208 vs raw 1.396 vs
persistence 2.300, 363 test days), DSM pending. §5.3 mentions "stage 2 is CDG";
generalise to "stage 2 is each further individual airport put to the same bar".
**Do not change what the bar requires** — raw GFS and persistence on MAE, per
airport, qualitative. Scope only.

**A-7. §6 (build order) — reframe Stage 2.** Change Stage 2 from "second airport
(CDG)" to **"individual airports (2 or more) — prove the recipe travels"**,
covering CDG, DSM and any further airports before pooling. Mark EGLC and CDG
passed, DSM in progress. Keep Stage 3 (pooling) noting the solar-noon switch is
**already in use from DSM** (cross-reference D27/D33). Resolve the stale
"in progress"/"pending" wording (Q24) as part of this.

Make **only** edits A-1 to A-7. If another SPEC change seems needed, log it as
an open question instead.

## Part B — pull DSM's full history (mirror session 03b/10)

Pull **2021-03-24 to 2026-07-31** for both sources at DSM, temperature-only
(D17 per airport).

**B-1. Forecast (Open-Meteo Previous Runs, `gfs_global`, DSM).**
`temperature_2m_previous_day1` at DSM's coordinates, yearly chunks, each saved
untouched in `data/raw/` with a `.meta.txt` (SPEC 2.3). Gentle; keep
retry/resume.

**B-2. Settle Q27 — `gfs_global` vs `gfs_seamless` at DSM.** Des Moines is
inside CONUS, so F6's Europe-only reasoning does **not** carry (a US mesoscale
model *could* enter `seamless`). Run the value-by-value comparison at DSM the
way F6 did for EGLC. Use `gfs_global` for the actual pull regardless (D16 pins
it); the comparison just records whether they differ at a CONUS point. Report
and close Q27.

**B-3. Truth (IEM ASOS, DSM, `IA_ASOS`).** Same period, yearly chunks,
provenance each. Routine `:54` report is the truth (F34). Respect the
1-second throttle. Keep temperature as the designated field; convert to Celsius
as the pipeline already does (F35).

## Part C — full gap map (structural; test set sealed)

Same as session 03b/10:
- for each series, total rows, total missing, **where gaps fall** (dates +
  length of each run);
- **does DSM's forecast series have the 492-hour gap** (2023-12-30 to
  2024-01-19)? Answer explicitly — same window, different, or none.
- **Handle Q26:** the `:54` reporting makes the first hour of each yearly chunk
  look missing (a request-boundary artefact, not a real gap). Count real gaps
  correctly — don't let the six chunk-boundary artefacts inflate the map; note
  them separately.
- days lost at the **18:00 UTC** target specifically (drop-count, 2.2, nothing
  filled).
- **Test set sealed:** for 2025-08-01 onward, structural checks only — no value
  summaries, no plots. Training-window value-range sanity check (Celsius) is fine.

---

## What to report at the end

- the before/after of each SPEC edit (A-1 to A-7), and the airport table as
  written;
- confirmation the frozen bar's *meaning* is unchanged (scope/convention only);
- for each DSM series: total rows, date coverage, chunk count;
- the gap map, the explicit 492-hour-gap answer, and the Q26 artefact handling;
- the Q27 `gfs_global` vs `gfs_seamless` comparison result;
- days lost at the 18:00 UTC target; the training-window value-range check;
- the new DECISIONS entries.

## What NOT to do

- Do not join the series, build, train, or evaluate anything (that is the next
  session — DSM's join and rehearsal).
- Do not change the meaning of the frozen bar (section 5) — scope only.
- Do not explore or summarise the *values* in the test window (2025-08-01 on).
- Do not edit SPEC beyond A-1 to A-7. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: SPEC now carries a per-airport target hour and an
   open-ended airport list; DSM's data is pulled and gap-mapped; next is DSM's
   join + validation rehearsal (mirroring session 11), test year sealed.
2. Append to DECISIONS: the SPEC generalisation decision, the pull totals, the
   gap-map findings (the 492-hour answer), the Q27 comparison result, and the
   Q26 artefact note. Mark Q24, Q25, Q26, Q27 closed as resolved.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
