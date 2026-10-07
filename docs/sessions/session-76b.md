# Session 76b — KSFO reproduction-gate diagnostic (Q34)

> **Amendment (2026-09-26, owner-approved, after the Step 0.2 stop and before
> any check ran).** The first run stopped correctly at Step 0.2: session 76
> kept no raw GRIB (fetch-decode-discard, F116.3 and F116.8). This prompt
> wrongly assumed it had. The owner approves this substitution:
>
> - **Wherever this prompt says "session 76's raw GRIB messages", use the
>   cached copies** under `data/raw/grib/` (sessions 37/40) and
>   `data/raw/grib/session72/`, **but only a cached file whose SHA-256
>   matches session 76's manifest row for that message**, and **only for
>   target dates before 2024-08-01**. The first run's check (17,150 of 17,150
>   match; 2022-11-30 absent in both) is accepted. Re-verify each file's hash
>   at load, and skip and report any file that does not match. Do not use it.
> - **No further listing, counting or reading of any file whose run or
>   target date falls in 2024-08-01..2026-07-31.** Every file selection is
>   filtered by date before it is opened or listed.
> - Everything else in this prompt is unchanged: no re-pull (except B.2's
>   single `LAND:surface` message and C's documentation and API calls), no
>   observations, no model fit, the gate is not re-run, and D68.2's reading
>   stands.
> - **F117 must record:** this substitution and the hash evidence; and the
>   first run's disclosure that Step 0.2 listed file names and counts in the
>   caches that include held-out-year run dates. Those were other airports'
>   files; no value was decoded.
> - Continue from Step 0.3. Step 0.1 is not repeated; git status would now
>   show `?? docs/session-76b.md` and `?? notes/session-76b-output.txt`.

Session 76 found that KSFO's reproduction gate failed (F116.5): our
elevation-adjusted GRIB temperature runs 3.3 °C colder than Open-Meteo on
average, and the gap is strongly seasonal (about −0.2 °C in December, −6.1 °C
in July). Q34 asks what happens to KSFO.

This session **does not decide Q34**. It gathers the evidence the owner needs
to decide it, through three checks:
- **A.** Is the session 76 pipeline correct? It re-decodes RNO from the same
  GRIB files and compares against the record.
- **B.** What do the four 0.25° grid points around KSFO look like?
- **C.** Which GFS product does Open-Meteo's `gfs_global` temperature come
  from?

The owner decides Q34 in planning after reviewing this session.

**No model is fit. No MAE, bias, residual or any
forecast-minus-observation statistic is computed. No observation is read.**

---

## Standing rules for this session

- SPEC section 2 applies in full.
- Nothing changes F109, F94, F116's gate result, or any verdict, claim or
  figure on record. **The gate is not re-run, re-scored or re-labelled.**
- **No row dated 2026-08-01 or later is touched.**
- **KSFO's held-out years (2024-08-01..2026-07-31, D67.6) stay closed.** Every
  diagnostic uses target dates **before 2024-08-01 only**. From the held-out
  years, nothing may be read, not even counts.
- Existing scripts, including every `session76_` script, are never edited.
  New code goes in new files with a `session76b_` prefix. It may import
  functions from the `session76_` scripts read-only; that is the point of
  Check A.
- Nothing under `data/processed/` is written or changed. Outputs go to
  `data/rebuild/session76b/` or `data/raw/diagnostics/session76b/`.
- Nothing is pulled in bulk. The only network calls allowed are those in
  B.2 and C.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks (no network)

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-76b.md`, since session 76 is committed.
2. Confirm that session 76's raw GRIB messages are still on disk (gitignored,
   D47). Report their location, file count and total size. Check that each
   message is a full global 0.25° field (it is not a point extract), so that
   any grid point can be decoded from it.
   **Stop rule:** if the raw messages are gone, or are not global fields,
   stop and report. Do not re-pull.
3. Read F116, Q34 and D67 in `DECISIONS.md`, and F89 and F90 in
   `DECISIONS-archive.md`.

---

## Step 1 — record the owner's decision (D68), before any check runs

Append this entry to `DECISIONS.md`, dated 2026-09-26:

**D68. Owner decision, planning chat (after session 76): diagnose KSFO's
gate failure before deciding Q34.**

- **D68.1** Session 76b runs three diagnostics (A, B, C below) before Q34 is
  decided. Q34 stays open until the owner decides it in planning.
- **D68.2 Pre-registered reading (written before any diagnostic ran).**
  - **If A fails:** a pipeline bug is indicated. KSFO is paused. The next
    step is a fix, to the pipeline only and never to the recipe, followed by a
    rebuild and a fresh run of the gate.
  - **If A passes and B or C explains the gap:** planning will recommend
    recording the gate as "failed, explained by a difference between the
    sources" (no override), and continuing KSFO under the unchanged recipe.
    "Explains the gap" means either of:
    - the summer spread across the four grid points is of the same order as
      the GRIB-versus-Open-Meteo gap; or
    - Open-Meteo's `gfs_global` temperature comes from a different GFS
      product than our 0.25° files.
  - **If A passes but nothing explains the gap:** the owner chooses between
    dropping KSFO and diagnosing further.
- **D68.3 Session plan.** The plan becomes: 76b diagnostic; then, if KSFO
  proceeds, 77 rehearsal and lock, and 78 the two looks (D67.7, shifted by
  this diagnostic).
- **D68.4 Planning-chat research (2026-09-26, not checked by this session).**
  Open-Meteo lists its GFS model as "NCEP GFS Global 0.11°/0.25°". Its GFS
  documentation says that the high-resolution GFS013 product lacks some
  variables, so the standard GFS025 model is used for those. KSFO's returned
  grid point (37.54637, −122.34375) does not lie on the 0.25° grid. Check C
  tests this.

---

## Check A — pipeline check on RNO (no network)

Using **session 76's own decode and interpolation code** (imported read-only
from the `session76_` scripts, with only the station parameters changed),
decode **RNO** from session 76's raw GRIB messages. KSFO and RNO share the
cycle (18z), the lead (f026), and f023 for T, so the messages are the same.
Use RNO's grid point, target hour and elevation constant exactly as the
record has them (SPEC 3.4; `session37_elevation_correction_params.csv`).

Compare every field that both hold against RNO's record rows on
**2021-03-24..2024-07-31**:
- B fields: `grib_features_v16_window.csv`;
- L, D, T and R underlying columns: the `session49`, `session51`,
  `session53` and `session55` `v16_window` files.

Report, per field:
- the rows compared;
- the rows that differ at the record's stored precision;
- the largest absolute difference;
- whether the set of missing days matches (2022-11-30 is expected missing in
  both).

**Pass = zero differing rows in every field.** On any difference, list the
first ten differing rows and continue with B and C (they are descriptive).
Do not attempt a fix.

---

## Check B — the four 0.25° grid points around KSFO

B.1 **Weights (no network).** Report the bilinear weight of each of the four
surrounding grid points at KSFO's Open-Meteo grid point, as session 76's code
computes them. Report the single nearest grid point.

B.2 **Land/sea mask (one small network call).** Fetch the single
`LAND:surface` message from the same run as session 76's HGT diagnostic
(20240609 18z f026), by byte range, saved to
`data/raw/diagnostics/session76b/` with `.meta.txt`. Report the land value at
each of the four points. No other pull.

B.3 **Temperatures at each point (no network, before 2024-08-01 only).**
Decode `TMP:2 m` at each of the four points from the retained raw messages,
with no interpolation and no elevation constant. Report, per calendar month
(and per year):
- the mean at each point;
- the bilinear blend (it should equal session 76's `temperature_grib_c`;
  check this);
- the mean of Open-Meteo minus each point, and Open-Meteo minus the blend.
  Use session 76's raw Open-Meteo files and the same identical-row set as
  F116.5.

This compares a forecast with a forecast. No observation is used.

---

## Check C — which GFS product Open-Meteo uses (small network calls)

1. Fetch Open-Meteo's GFS documentation page(s) and its Previous Runs API
   documentation. Record, with the pull date, what they say about:
   - which GFS product (`GFS013`/0.11° or `GFS025`/0.25°) supplies
     `temperature_2m` under `gfs_global`;
   - whether the Previous Runs API offers a **0.25°-only** GFS model option.
2. **Only if** a documented 0.25°-only GFS option exists in the Previous Runs
   API, with `temperature_2m_previous_day1` back to 2021:
   - pull it at KSFO for **2021-03-24..2024-07-31**;
   - report its returned grid point;
   - report mean |diff| and mean diff against session 76's
     `temperature_grib_c` (before the elevation constant) and `temp` (after),
     on identical rows.

   This is a descriptive comparison. **It is not a re-run of the gate** and
   does not change F116.5.

   If no such option is documented, skip C.2 and say so. Do not guess model
   names.

---

## Step 2 — record the finding (F117)

Append **F117** to `DECISIONS.md`. It records:
- the Step 0 confirmation;
- Check A's per-field table and its pass or fail;
- Check B's weights, land values and monthly tables;
- Check C's documentation findings (and C.2 if run);
- which D68.2 branch the evidence points to, described as evidence for the
  owner and not as a decision;
- the new files;
- a "What this did not do" list.

It changes no verdict, claim or figure. F116.5's gate result stands, and Q34
stays open.

---

## End-of-session steps (CLAUDE.md)

1. Write the **real output** of every step to `notes/session-76b-output.txt`.
2. **Archive:** move any entry this session settled, per D46. D67, D68, F115,
   F116, F117 and Q34 stay live. Report before/after line counts.
3. **Overwrite STATUS.md** as a current-only snapshot. Keep these carried
   items:
   - session 76's consistency items 1–4 (SPEC wording about KSFO and
     airport counts);
   - the GFS v17 re-check.

   Add, for the lock if KSFO proceeds: "raw GFS at KSFO is heavily biased
   relative to Open-Meteo, so beating raw is expected to be easy; persistence
   is the binding part of the bar. State this in the lock's expectations. The
   bias against observations is first measured in rehearsal."

   End with a **"Next planning session"** line: review session 76b; the owner
   decides Q34 using D68.2. If KSFO proceeds, draft session 77 (rehearsal on
   the 2022-23 and 2023-24 folds, the band per D67.5, and the lock, including
   SPEC 5.2's KSFO constant and a KSFO-specific held-out guard).
4. **Consistency check:** re-read CLAUDE, SPEC, STATUS and DECISIONS. Report
   disagreements, duplicated headings and out-of-order entries. Report only.
5. **Do not write a commit message file, and do not commit.** The planning
   chat writes `docs/commit-76b.txt` after review. Stop and wait for the
   owner's review.
