# Session 43 — consolidation part 1: fold the proven 5-feature GRIB method into SPEC

## Where this sits

The GRIB build is complete and passed its sealed test (F94, 5/5). SPEC.md has been left
untouched since session 30 by design — it still describes only the original 3-feature Open-Meteo
method and calls Reno a failure. This session folds the now-proven **5-feature GRIB richer-features
method** into SPEC as a distinct, clearly-bounded addition, and updates Reno's status — **without
disturbing the original 3-feature method's description**, which stands as its own result.

This is **documentation only**: no code, no model, no data, no new figure. It edits `SPEC.md` and
refreshes `STATUS.md`. **RESULTS.md and the archive pass are the *next* session (44)** — SPEC is the
source of truth and must settle first, since RESULTS draws from it.

## Guiding principle — two methods, both true, cleanly separated

The project now has two proven methods, and SPEC should present them as such, not blur them:

- **The minimal method** (3 features, Open-Meteo source): the original, unchanged. Passes at 4/5,
  fails honestly at Reno (F82). Its SPEC sections (§1–§6 as written) stay intact.
- **The richer method** (5 features, GRIB source): a Reno-motivated extension. Passes at 5/5
  including Reno (F94). It differs from the minimal method in source, features, pipeline, and an
  elevation correction — enough that it belongs in **its own dedicated section**, cross-referencing
  the per-airport machinery it reuses (target hour, pairing, split dates, bar), rather than being
  woven through and muddling the minimal method.

Preserve the minimal method's text. Add the richer method alongside it. Reframe Reno as *failed the
minimal method, passed the richer one* — both true, neither erased.

## Standing rules that bind this session (SPEC §2)

- **Documentation only.** No code, model, data, or figure. Every number folded in is cited to its
  DECISIONS finding (D48, F85–F94) and must match it — recompute nothing.
- **Preserve, don't rewrite.** The minimal method's sections stay as they are except where Reno's
  status or a pointer genuinely needs updating. Do not restructure §1–§6 wholesale.
- **No result changes.** The minimal method's verdicts (F16/F30/F47/F64/F82) stand unchanged; the
  frozen bar is unchanged. This session records what happened, it does not re-judge anything.
- **You never commit.** Prepare changes and a suggested message.

---

## Task 1 — propose the SPEC structure first, then report it before editing

Read SPEC.md in full and propose, in the session output, exactly:
- **where the new richer-method section goes** (a dedicated section — e.g. a new §7, or a §4A —
  whichever fits the existing structure most cleanly) and its heading;
- **which existing spots get a light pointer or a status update** (expected: §1 airports list, the
  §2.1b leakage rule, §3.2 forecast source, the §5.0 results context, and the §6 Reno/stage-2
  bullet);
- **how Reno is reframed** (failed the minimal method F82 / passes the richer method F94).

Report this plan, then make the edits in the tasks below. (The owner reviews the plan and the diffs
together before committing — so the organizing choice is visible, not buried.)

## Task 2 — write the new richer-method section

A dedicated section describing the proven 5-feature GRIB method completely, drawing on D48 and
F85–F94:
- **Motivation:** Reno's 3-feature failure (F82) was systematic-vs-random (F79) — evidence the
  minimal feature set has a ceiling where bias is near-constant-plus-noise. The richer features test
  whether more physical information (cloud, wind) breaks that ceiling.
- **Features:** the 3 minimal features **+ `cloud_cover` (GRIB TCDC) + `wind_speed_10m`** (from
  GRIB 10 m u/v).
- **Source & pipeline (what differs from the minimal method):** GFS 0.25° **GRIB** from AWS
  `noaa-gfs-bdp-pds` — a genuine archived past forecast, leakage-safe (see §2.1b note) — not
  Open-Meteo; the F89 lead convention (`cycle = floor(HH/6)*6` on D−1, forecast-hour lead
  `= 24 + (HH mod 6)`); bilinear grid→point interpolation; and an **elevation/lapse-rate correction**
  (7.429 °C/km, applied as five frozen per-airport constants, D48.3) that matters at Reno and is
  negligible elsewhere.
- **Window:** trained on **2021-03-24 → 2025-07-31, GFS v16 only** (GFS v16 went operational
  2021-03-22; pre-v16 data is a different model version and is deliberately excluded), same sealed
  year as the minimal method.
- **Model:** identical LightGBM settings (D21.4) — nothing tuned per airport; only cloud and wind
  are added.
- **Validation done before the sealed test:** GRIB temperature reproduces Open-Meteo temperature at
  5/5 airports (source-swap clean, ≤0.062 °C); cloud/wind cross-checked against Open-Meteo on the
  overlap; full-window blocked CV showed the 5-feature model beats the 3-feature model out-of-fold
  at all five airports (F91).
- **Lock and sealed test:** recipe frozen in writing before the sealed year was opened (D48, with
  pre-registered expectations D48.12); the single look passed at **5/5** (F94), matching the
  pre-registration exactly.
- **The controlled evidence that richer features help** is the 5-feature-vs-3-feature comparison on
  identical elevation-corrected temperature (they differ *only* in cloud and wind) — note this
  explicitly, since it is the clean, source-and-baseline-independent measure.
- Cross-reference the per-airport machinery it reuses unchanged (target hour §4.1, pairing §4.5,
  split dates §4.3, bar §5.3).

## Task 3 — update Reno's status and add the pointers

- **§1 airports list:** Reno's line — from "stage 2, failed" to something like "failed the minimal
  3-feature method (F82); passes the richer 5-feature method (F94) — see §[new]." Keep it honest and
  brief.
- **§6 Reno / stage-2 bullet:** add that the richer method later passed Reno (F94), pointing to the
  new section; the minimal-method failure record (F82) stays as written.
- **§2.1b (leakage rule):** add that the GRIB archive used by the richer method is an equally
  leakage-safe source — genuine archived past forecasts at a fixed lead, no future-stitching — so
  the rule's intent holds for it too. Do not remove the Open-Meteo guidance (the minimal method uses
  it).
- **§3.2 / §5.0:** add a light pointer to the new section (and, at §5.0, note that the richer method
  has its own results, without overwriting the minimal-method results table). The richer-method
  results table itself can live in the new section or be deferred to RESULTS — pick the cleaner and
  say which.
- Keep every edit minimal and pointed; do not rewrite surrounding prose that doesn't need it.

## What NOT to do

- **Do not rewrite or delete the minimal method's sections** — preserve them; touch only Reno's
  status and the specific pointers.
- **Do not change any DECISIONS finding, any verdict, or the frozen bar.**
- **Do not overclaim Reno.** The richer method passes Reno, but the clean evidence for "richer
  features help" is the 5-vs-3 comparison; the raw-GFS-margin caveat (GRIB's raw baseline differs
  from Open-Meteo's) belongs in RESULTS (session 44) — in SPEC, just state the method and its verdict
  accurately without inflating it.
- **Do not touch `RESULTS.md`** — that is session 44.
- **Do not run the archive pass** — session 44 does it, once SPEC and RESULTS both carry the
  headlines.
- **Do not commit.**
- **Do not exceed scope** — SPEC edits + STATUS refresh only.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the Task 1 structure plan, then the before/after of every SPEC edit (the way D45
   recorded its edits), so the owner reviews organizing choice and diffs together.
2. **DECISIONS:** append a short entry (next sequential D-number — check the tail, likely **D49**)
   recording this SPEC consolidation and what changed. This stays live.
3. **Refresh STATUS.md** to record session 43 and that RESULTS + archive is session 44.
4. **Consistency check:** every folded-in figure matches its DECISIONS source; SPEC is internally
   consistent (no section now contradicts another; the minimal-method sections are intact; Reno's
   status is consistent across §1, §5, §6 and the new section); all `(Dxx)`/`(Fxx)` citations
   resolve; `RESULTS.md` is unmodified; `git status` shows only `SPEC.md`, `STATUS.md`, `DECISIONS.md`
   (and docs) changed — no code or data.
5. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the body,
   `--` not em-dashes, short body — then **stop and wait for the owner's review.**
