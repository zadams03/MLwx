# Handover — GFS temperature bias-correction project → richer-features phase

You are picking up a live, long-running project at the start of a new phase.
This document gives you the full context and the plan already agreed. It does
**not** replace the project's own files — those are the ground truth, and your
**first action** is to have the owner paste them (see "Do this first").

Read this whole document before doing anything.

---

## 0. Do this first (before any planning or building)

Ask the owner to paste, into the new chat, the current:
- **SPEC.md** — the source of truth for how the project works;
- **STATUS.md** — a snapshot of current state (overwritten each session);
- **RESULTS.md** — a standalone technical summary of all five airports;
- **DECISIONS.md** — the append-only log of every decision (D) and finding (F);
  and **DECISIONS-archive.md** if deep history is needed.

This handover carries the *plan and reasoning*; those files carry the
*authoritative current state*. Where they and this document ever disagree, the
**files win** (this handover is written 9 Sept 2026, just after session 30 —
things may have moved). Do not plan feature specifics or write any session
prompt until you have read the real files.

---

## 1. What the project is

A **MOS-style bias correction of GFS 2-metre temperature forecasts at individual
airports.** For each airport, at one fixed hour of the day, the model learns the
**residual** — observed temperature minus GFS's forecast — and adds the predicted
correction back to the raw forecast. It does **not** predict temperature
directly; it predicts *how wrong GFS characteristically is* at that place, which
turns out to be a low-dimensional, learnable thing.

The eventual ambition is a live daily tool that shows a corrected forecast for
the day ahead, but that is far off. The work so far has been proving the base
method travels and understanding where it works.

**Current model (the "3-feature" model), for context — confirm exact wording
from DECISIONS:** LightGBM gradient-boosted trees, objective `regression_l1`
(absolute error, to match the MAE metric), 300 trees, learning rate 0.05, 15
leaves, min 40 samples/leaf, seed 42, deterministic. **Three feature columns,
two real variables: forecast temperature, and season (day-of-year as sin/cos).**
That's it. This minimal model already beats raw GFS at four of five airports —
which is itself a notable result and tells you the base premise (local bias is
real and structured) holds.

---

## 2. Current state (as of session 30 — verify against the pasted files)

**Five airports done, under a strict rehearse → lock → single-sealed-test
discipline. Four pass, one fails.**

| airport | region | target hour (UTC) | verdict |
|---|---|---|---|
| EGLC (London City) | UK | 12:00 | PASS |
| LFPG (Paris CDG) | France | 12:00 | PASS |
| DSM (Des Moines) | US interior | 18:00 | PASS |
| YSDU (Dubbo) | Australia (S. hemisphere) | 02:00 | PASS |
| RNO (Reno, Nevada) | US mountain-valley | 20:00 | **FAIL** |

**The honest headline (use this framing, not the best single number):** across
the four passes, the correction beats raw GFS by **roughly 3–16% over eight
airport-years** (each airport has a rehearsal year and a test year). All five
airports were tested on the **same shared twelve months (2025-08→2026-07)** —
that shared test year is the one surviving caveat (see §4). The European margins
were partly inflated by a warm European summer that year; Des Moines and Dubbo
(independent weather) came in lower, which is the more honest read.

**Key findings established (all in DECISIONS/RESULTS):**
- The recipe travels across three continents, two hemispheres, three target
  hours, with no retuning — same recipe, only location and target hour change
  per airport.
- **Four distinct bias shapes** — EGLC warm-end, CDG calendar, DSM both, Dubbo
  one-season. The model adapts to each location's structure from the same three
  features; it is not applying a template.
- **Cross-hemisphere generalisation:** Dubbo's bias peaks in *its own* local
  summer (Dec–Feb), phase-shifted from the Northern airports. The day-of-year
  feature carries no hemisphere info, so this is genuine local learning.
- **The Reno failure, and why it matters — this is the motivating case for the
  richer-features phase.** Reno's error is a **near-constant bias buried under
  large day-to-day random scatter.** The systematic part is essentially just a
  constant offset, too small relative to the scatter for the correction to beat
  raw GFS; the model overfit that near-constant signal (25% in-sample gain
  collapsed to −3.1% out-of-sample). Crucially: **the failure was predicted in
  advance** (DECISIONS D44.12, before the sealed test opened) and Reno was
  **locked and tested unmodified** — not rescued. This is the project's integrity
  on display: the method was not changed to avoid a failure it expected.
  - The deeper lesson: **the method corrects *structured* bias, not *random*
    error.** Des Moines (hard but structured) passes; Reno (moderate but random)
    fails. Same-sized raw error, opposite outcomes.

**Reno's result stands — no re-run, no retroactive change.** Any richer-features
work is a *new method* evaluated fresh, not a re-scoring of Reno's locked model.

---

## 3. The working discipline (this is the project's whole value — preserve it)

The project's credibility comes from a rigorous, self-imposed discipline. You
must uphold it. The key rules (full versions in SPEC section 2 and CLAUDE.md):

- **Two-role separation, deliberately kept:** the planning chat (you) *thinks,
  decides, and writes session prompts*; **Claude Code** *executes* them in the
  repo; the **owner reviews and commits by hand**. You never touch the repo. This
  separation is a feature — it is what produces the pre-registered bars and the
  "stop and flag" catches. (The owner considered folding planning into Claude
  Code and we decided against it precisely to preserve this firewall. Do not
  suggest collapsing it.)
- **One session, one scope.** Each session prompt does exactly one well-defined
  job and stops for review. Out-of-scope items get logged, not acted on.
- **The frozen bar.** Success = corrected MAE beats **both raw GFS and
  persistence** over a held-out test year, per airport. Qualitative, **no numeric
  margin**, fixed *before* any model runs. It is never changed to fit a result.
- **Rehearse, then one look.** Each airport: build/tune on a *validation* year
  carved from training (the "rehearsal"), then **lock** the exact recipe in
  writing (a D-entry), then open the **sealed test year exactly once** and run
  the locked recipe. The test year is opened one time; the result stands, pass
  or fail. Deviation mid-test is a stop signal.
- **No leakage, ever.** Time-based splits only; anything fitted (model,
  climatology, mean-bias) uses training data only; the test year is never seen
  until the single look. (Note: early verify-on-contact samples touched a few
  test-year values for *format* checks only — recorded honestly as "no test-year
  data influenced any model or choice"; from Dubbo on, verification samples come
  from outside the test year.)
- **Drop-count-report, never fill.** Missing data is dropped and counted, never
  interpolated.
- **Raw data is immutable, with provenance.** Every raw pull is saved untouched
  with a `.meta.txt` recording the exact query and pull time.
- **DECISIONS.md is append-only.** Decisions (D) and findings (F) are never
  edited or deleted — superseding entries are appended. A one-time authorised
  restructure moved settled material to DECISIONS-archive.md (nothing lost).
- **Files are the truth; the agent works from pasted files, not memory.** The
  owner enforces this. When you need current state to write a session, ask for
  the file rather than guessing. (Ask only when you genuinely need it — not
  reflexively.)
- **Commit discipline:** Claude Code never commits. It prepares changes and a
  suggested commit message; the owner reviews and commits by hand. You provide
  commit commands *after* a session has run and been reviewed, never before.

Data-hygiene facts worth knowing (all in SPEC/DECISIONS):
- Forecast data: **Open-Meteo Previous Runs API**, model string pinned to
  **`gfs_global`** (not `gfs_seamless` — they diverge sharply inside the US,
  e.g. by up to 16°C at Reno; the pin prevents silently correcting a non-GFS
  model). Archive starts **2021-03-24**. The `previous_day1` offset is a
  *nominal* 24h lead that actually sweeps ~24–30h.
- Truth data: **IEM ASOS/METAR**, per airport, routine on-the-hour report,
  paired to the forecast hour within 15 minutes (D14), converted to Celsius.
- A single **492-hour forecast gap** (2023-12-30→2024-01-19) is shared by four
  of the five airports (Dubbo is the exception, with its own scattered gaps) —
  it's an archive property, entirely in the training window, dropped and counted.
- **Target-hour convention:** each airport targets **local standard noon**
  (daylight-saving ignored, so a fixed UTC hour per airport) — EXCEPT EGLC and
  LFPG, which both use **12:00 UTC** by a *deliberate earlier choice* (to change
  only the location between them), which is local noon at London and ~1pm at
  Paris. (There is a known wording error in RESULTS.md that misexplains this as
  all-local-noon — see §6.)

---

## 4. The richer-features plan (agreed in the planning conversation — this is
what the new phase is)

**Goal:** test whether adding physically-motivated forecast variables improves
the correction beyond temperature-plus-season, and specifically whether it helps
where the base method struggles (Reno).

### 4a. Feature selection — settled, deliberately minimal

**First wave: cloud cover + 10-metre wind speed.** Same two features at *every*
airport. Rationale (rooted in the MOS literature and two reference docs the owner
supplied):
- **Cloud cover** — the dominant lever on near-surface temperature error. Clear
  skies drive strong radiative heating by day and cooling by night; GFS's
  grid-averaged cloud is often locally wrong, directly causing temperature error.
- **10m wind speed** — distinguishes turbulent mixing from radiative decoupling.
  Calm nights let cold air pool at the surface (large, structured error); wind
  mixes it away.

**Why kept minimal — this is critical and non-negotiable:** with only ~1,500
rows per airport, an irrelevant feature does **not** get cleanly ignored by the
trees. On finite data, random-but-useless features occasionally look predictive,
the model splits on them, and that is **overfitting** — exactly what sank Reno
with only three features. So: **features must earn their place on physics
*before* inclusion; feature-importances only *confirm*, never *discover*.** "Add
everything and let the model sort it out" is a big-data instinct that will
*degrade* results at this scale. Use the **same feature set at every airport**
and let each airport's model down-weight what doesn't matter locally — do **not**
hand-pick features per airport (selecting features on your own training data is
itself overfitting).

**Explicitly deferred / excluded (with reasons):**
- **Dewpoint / humidity** — wave two. Well-motivated (fog, nighttime floor) but
  lower marginal value at a *daytime* target hour.
- **Upper-air temperature (925/850 hPa) — the important one, scoped carefully.**
  Physically the single most valuable feature for *inversion / mountain* sites
  (i.e. essentially just Reno among the five). BUT: (a) it likely is **not
  available** on Open-Meteo's Previous Runs API at the day-offset — this must be
  checked; (b) getting it elsewhere means a **second data source**, which
  reintroduces grid/lead-time alignment problems, muddies the clean "we correct
  one model" story, and is a real engineering lift (raw GRIB decoding).
  **Decision: do NOT switch architecture for upper-air now.** It is a *targeted
  future Reno experiment* ("does upper-air rescue the one terrain airport?"), not
  a first-wave feature. Only consider a second source if a focused Reno rescue
  later justifies it.
- **Recent-bias / lagged-error features** — deliberately out. They blur into the
  persistence baseline, muddy the "correct the forecast" story, and carry leakage
  risk.
- **Elevation-mismatch, station ID, coastal distance, land cover, neighbouring
  grid cells** — these are **pooling-phase** features (constant-per-airport or
  pooling-specific; useless in a single-airport model). Their feature list is
  already mapped from the two reference docs for when pooling arrives. Not now.

### 4b. The binding constraint — data availability (the real crux, NOT yet
resolved)

Cloud and wind are almost certainly only in the archive **from ~2024**, while
temperature runs 2021–2025. So you likely **cannot** just add them to the
existing 4-year setup — you'd have ~1.5 years of feature-complete data.

**The very first task of this phase is an empirical data-availability check** on
the Open-Meteo Previous Runs API at the `previous_day1` offset: which of {cloud
cover, 10m wind, dewpoint/RH, **925/850 hPa temperature**} exist, and **how far
back**. This can only be answered by hitting the live API (a Claude Code task).
The upper-air result specifically decides whether it's free, unavailable, or a
separate-source project.

**Three candidate approaches to the short-window problem, to choose AFTER the
check confirms actual dates:**
1. Train the richer model on the short (2024-on) window only — clean but
   data-poor; a weak result would be confounded ("features didn't help" vs "not
   enough data").
2. Find a deeper source for the features (research task; own subtleties).
3. **Two-tier same-window comparison** — train *both* the 3-feature and the
   richer model on the *same* 2024-on window, so the comparison is fair (same
   data, different features) even if absolute numbers are lower. **This is the
   planning chat's lean** — the cleanest *experiment*, even if not the most
   *powerful* model.

### 4c. Experiment design — settled in shape

- Frame it as a **baseline ladder** (from the owner's docx, which is good): raw
  GFS → + mean bias → current 3-feature model → + physical features. Measure the
  gain of *each rung*.
- Headline comparison: **richer model vs the frozen 3-feature result**, per
  airport. Also vs raw GFS (does the richer correction pass the bar — especially
  at Reno).
- This is a **new method**, so it needs its **own rehearse → lock → sealed-test
  cycle per airport**, judged against the **same frozen bar**. You **cannot**
  re-score the existing locked models with new features — that would change a
  locked recipe. (It's a parallel evaluation track, not a quick re-run.)
- **Reno is the diagnostic:** does cloud/wind rescue it, or is its error
  genuinely irreducible? *Either answer is valuable* — a rescue proves the
  failure was feature-limited; no rescue proves the error is random, a sharp
  finding about the method's ceiling.
- **Watch the in-sample-vs-validation gap hard** — more features = more
  overfitting rope. The discipline gets *more* important, not less.

---

## 5. The broader sequence (after richer features — plan of record, unchanged)

1. **Richer features (this phase)** — evaluate cloud+wind across the existing
   airports.
2. **A few more airports**, chosen to *test the new features* (fog-prone /
   cloud-variable / terrain sites, so the features get a fair test) — not just
   more flat airports (diminishing returns; the "does it travel" question is
   answered).
3. **Blend models** (ECMWF / ICON / Google WeatherNext) — the novel,
   portfolio-distinctive piece. Works at a single airport; does not need many
   airports. This was deliberately moved *ahead* of airport-pooling in the plan.
4. **Airport-pooling** — only once the airport count is high enough to matter
   (pooling's value is data-poor airports borrowing from similar data-rich ones;
   pointless at 5). Its feature list (elevation-mismatch, station ID, etc.) is
   already mapped.
5. **Later:** widen the target (full hourly curve, 48h lead), then the live
   product.

Also parked and available (owner's choice, not urgent): a **second/different
test year** to kill the last shared-test-year caveat — though note the validation
and test years are already different years and both positive, giving partial
two-year evidence. Diminishing value; a training-size confound makes a clean
third-year test awkward.

---

## 6. Loose ends to carry in (small, flag to the owner)

- **RESULTS.md wording fix (owner asked for this in the next Claude Code
  session):** RESULTS.md currently says all five airports' hours differ "because
  local noon is a different UTC hour at each longitude." That is wrong for the
  European pair: EGLC and LFPG share 12:00 UTC by a *deliberate choice* (to change
  only location between them), which is local noon at London and ~1pm at Paris —
  NOT Paris's local noon (which would be 11:00 UTC). DSM/Dubbo/Reno do use each
  airport's own local-standard-noon. Fix the sentence so it distinguishes the two.
- **SPEC section 1's airport list** still reads Reno "stage 2, in progress" — a
  separate spot from the 3.4 table that session 30 fixed. It needs "failed" too.
  A small authorised edit for the next SPEC-touching session.
- **Commit state:** confirm with the owner whether session 30's changes are
  committed. (Everything through session 29 is committed; session 30 was awaiting
  the owner's commit at the time this handover was written.)

---

## 7. How to run this phase (the immediate next moves)

1. Have the owner paste SPEC / STATUS / DECISIONS / RESULTS (§0). Read them.
   Reconcile anything in this handover against them; files win.
2. Confirm the plan in §4 with the owner (it's agreed, but they may want to
   adjust now that a fresh chat is looking at it).
3. **Write the first session prompt: the data-availability check** (§4b) — a
   Claude Code session that probes the Previous Runs API for cloud, wind,
   dewpoint, and 925/850 hPa temperature at the `previous_day1` offset, reports
   which exist and how far back, at all five airports' locations, sampling
   **outside the test year**. It builds and evaluates nothing — it just settles
   what data exists. Fold in the two small §6 fixes if it's convenient and in
   scope, or leave them for a dedicated SPEC session.
4. From that result, choose the data approach (§4b options 1–3) with the owner,
   then design the richer-features experiment (§4c) as its own session(s).

Keep session prompts tight, one scope each, and always stop for the owner's
review. Provide commit commands only after a session has run and been reviewed.
Preserve the discipline in §3 above all — it is the project's whole worth.
