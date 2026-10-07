# STATUS.md: where the project is right now

_This file is a snapshot, overwritten each session. It is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 7 October 2026, after session 98b._

---

## Session 98b: repository cleanup for outside readers (D91, F140)

Session 98 stopped at its reference gate (F140.1); D91 accepted the stop
and replaced its layout. Session 98b recorded D91 and F140. No model
experiment was run and no build choice was made. Full output:
`notes/session-98b-output.txt`.

- **One move (D91.3):** `PROJECT-INSTRUCTIONS.md` is now
  `docs/PROJECT-INSTRUCTIONS.md`, byte for byte. Every other file stays
  where it is, because scripts read the record files and `notes/` there
  (D91.2). CLAUDE.md and the guide's own table now say `docs/`.
- **SPEC 6 (D90.8):** the stage C bullet points to D88 and D89.
- **libomp (D90.9): passed.** Homebrew 7.0.8, libomp 23.1.3. With the
  loader shim bypassed, `session97_stagec_cv.py --gate` gave F109's six
  values 6 of 6, and EGLC's `--score` was byte-equal to the committed
  rows. So scripts from session 99 on may import lightgbm directly.
  `requirements.txt` comments updated; package lines unchanged.
- **Figures:** `figures/headline_mae.svg` and `figures/skill_intervals.svg`,
  drawn by `scripts/session98b_figures.py`, repeatable byte for byte.
- **README files:** the root README rewritten; new READMEs in `scripts/`,
  `data/`, `docs/` and `notes/`.

---

## Where the project is right now

**The project has three independently-tested, proven methods for
correcting GFS's local bias at an airport (SPEC sections 5.0, 7.5, 8.7;
RESULTS.md). F109 stands. KSFO passes the selected-features method on
both of its pre-registered looks (F119, D71).** No untouched held-out
year remains at any of the six development airports (D71.1).

**The end goal (D82.2).** A private, live tool for ten or more airports
that corrects every GFS run (four a day), as each run arrives, into an
hourly temperature curve out to the forecast horizon, plus the daily
maximum. The horizon is 24 hours first and 48 hours later. Then a choice of
which weather model is corrected, plus a blend, and probabilistic ranges.

**The roadmap (D72; SPEC 6).** Stage A is done. Stage B runs. Stage C is
open: its design is set (D82, D83), its f000 to f024 GRIB pull is complete
and checked (D87, F137), its development table is built and gated (D88,
F138), D89 fixes the cross-validation rules, and the curve's baseline is
fit and scored by cross-validation (F139, accepted in D90.1). Its open
build choices (D82.5) come next, under D89.6, starting in session 99
(D90.3). Then stages D to H. New airports are an ongoing track, and
pooling is conditional.

**Stage B: the 2026-27 GFS forward test (D73, F122, D77.6, D79), unchanged.**
It is pre-registered, its models are frozen, and all three 2026-27 scripts
exist and passed their gates (F128, F129). **None has been run.** Order, per
period, after the period ends and its observations are in: build
(`scripts/session86_forward_build.py --build`), fetch
(`scripts/session87_forward_competitors.py --fetch`), score
(`scripts/session87_forward_score.py --score`). The first operational v17
cycle and the NBM and MAV version labels come from DECISIONS entries written
first (D79.4; period A's NBM label must name v5.0.15, D78.6). Period B needs a
later build mode and D73.4's v17 entry. Arguments and outputs are in F128.6
and F129.6. The hold rule (D73.8) stands: no 2026-27 value is scored before
its period has ended.

**MOSMIX (D81.2 to D81.5).** Daily saves of MOSMIX_L single-station files,
all four issues, at EGLC (P0478), LFPG (07157), DSM (72546), RNO (72488) and
KSFO (72494), run on GitHub Actions and committed to a separate private
repository. **The saver session has not been run and no saver exists.** Days
before it starts are lost, which is accepted. No MOSMIX test is
pre-registered. F132 records which airports have a MOSMIX station within 10
km; the saver session decides whether the list grows.

**Stage C.**
- **Design (D82.3 to D82.8, D83.2 to D83.5).** Every GFS cycle, forecast
  hours 0 to 24 first (25 to 48 later, by an additive pull with the same
  script, starting at cycle 2021-03-22T12, the first GFS v16 run, D84.2).
  Raw values at the four grid points around each airport, ten fields,
  2021-03-24T00 to 2026-07-31T23 UTC only, by monthly chunk on GitHub
  Actions, published as Release files. The pull list is 51 airports (D82.6's
  47 plus LFPG, DSM, YSDU, RNO); development airports at SPEC 3.4's grid
  point, the others at IEM's position. Daily maximum: local day, 22 of 24
  usable hours.
- **The pull (F133 to F137).** `scripts/session91_grib_pull.py` (SHA-256
  `b52ffc2e...2f1f`, with the whole-file fallback, F136),
  `data/processed/session91_pull_airports.csv` and
  `.github/workflows/stagec-grib-pull.yml` (`804b6d35...02a6`), with the
  verify step (`scripts/session92_verify_chunk.py`, `7b59a5c2...af6a`).
  The Release `stagec-grib-pull-v1` holds all 195 assets (65 months x 3,
  1.26 GB); all 195 are in `MLwx-pull/` (outside the repo), each equal to
  its Release digest, and every check passed (F137). Committed inventory:
  `data/processed/session95_pull_inventory.csv` (`7177b661...b70a`).
- **The development table (D88.3, F138).** Six development airports, every
  cycle, forecast hours 0 to 24: 195,600 rows per airport, in
  `MLwx-stagec/` beside the repo (not tracked, D88.8). Leads 0 to 2 stay
  in, incomplete, counted (D88.6). The gate passed at EGLC, LFPG and DSM
  lead 24 (5,861 station-days, exact equality). Script
  `scripts/session96_stagec_table.py` (`40b63d00...6eee`); meta
  `data/processed/session96_stagec_dev_table.meta.txt` (every table file's
  SHA-256; unchanged at session 98b, F140.10).
- **The rules for build choices (D89).** Three time-ordered folds with
  expanding training windows, test years 2023-24, 2024-25 and 2025-26
  (D89.3). Metric: MAE of the hourly temperature on leads 3 to 24, on the
  common row set; headline is the unweighted mean of the six airport MAEs
  (D89.5). A challenger replaces the incumbent only if the headline is
  lower by more than 1 percent, the airport MAE is lower at 4 or more of 6,
  and the fold-level MAE is lower in 2 or more of 3 (D89.6). For D82.5's
  model-structure comparisons the incumbent is D88.4's baseline (D89.7).
  One choice for the whole curve and every airport (D89.8).
- **The curve's baseline (D88.4), fit and scored (F139).** SPEC 8's
  `B+D,L,R,T` with the record's settings, one model per airport, fold,
  cycle hour and lead 3 to 24 (1,584 fits). The fitting-code gate passed
  (D89.9), again at session 98b without the shim (F140.7). Its scores are
  build-choice scores, not results (SPEC 2.5), and are in F139 only.
  Script `scripts/session97_stagec_cv.py`
  (`987ab6ba...1f91`); folds, scores and meta in
  `data/processed/session97_stagec_cv_*`. No model is saved.
- **Claim batch (D82.7, F132): EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN.**
  Held-out window 2024-08-01..2026-07-31; looks fixed at stage C's lock.
- **Not decided (D82.5).** One model per lead with the cycle hour as an
  input, or one model with lead and hour as inputs, each against the
  baseline under D89.6, one at a time (D89.10); the daily maximum read off
  the curve or its own model (its metric is fixed in its own entry first,
  D89.8); stage C's claim design (bar, looks, lead bands), at the lock.
  Bias drift follows D81.10(b).
- **Open item: MMMX (D83.4).** It reports at scattered minutes, so it has
  almost no usable observations under the 15-minute rule. It needs its own
  handling or to be dropped (a later decision). It stays in the pull.

**Stage A: done.** Source probe (F123), ICON route check (F124, D76.2),
confidence intervals (F125), NBM/MOS comparison (F127, band MIXED),
direction decision (D78.1, option (d)).

---

## Open questions (live)

- **Session 98b's readings (F140.11), for the owner to confirm.** In
  brief: `brew` was run by full path (not on the session shell's PATH);
  two libomp copies load without the shim (Homebrew's and scikit-learn's),
  and the gate still passed; the session 83 output's SHA-256 is pinned
  from the committed file, since the record holds none; the figure script
  was changed twice after its first run (width; its own em-dash check);
  2022-01 was checked after it was published, so the README does not say
  every month was checked first; the frozen-script list includes
  `session77_ksfo_looks.py` and the three stage B scripts; the data credits
  as written (MAV's own terms not fetched).
- **RESULTS.md section 7's roadmap paragraph is out of date** (it lists
  stage C as later work and ends at stage B's pre-registration). Not in
  this session's scope; reported only.
- **D72.12 and D90.5 to D90.6** place `PROJECT-INSTRUCTIONS.md` at the
  root or under `audit/`. They are record entries, not edited; they
  resolve through D91.4.

---

## Carried items

- **GFS v17 (D90.2, D91.7).** As of 2026-10-07 (planning-chat check) there
  is still no Service Change Notice for GFS v17; the newest SCN listed is
  SCN 26-89 (2 October 2026). EMC's GFSv17 evaluation page gives the
  implementation as Q1 FY27 (October to December 2026; D84.6). With 30
  days' notice the earliest go-live is about 6 November 2026. Re-check at
  each planning session. The go-live date sets period A's length. PNS
  26-30's statement that the 0.25 degree GRIB2 files remain is to be
  confirmed against the SCN (D73.4).
- **libomp (D90.9, F140.7).** The gate passed, so scripts from session 99
  on may import lightgbm directly, without the shim. Scripts that import a
  record script still run its shim, which is harmless. scikit-learn stays
  pinned.
- **Later work (D90.12).** A `tests/` folder after stage C's first D82.5
  comparison; a `src/` package only at stage G. Neither is created empty.
- **EGLC position note (D81.6).** DWD's cfg places P0478 west of the
  airport; F132.5 confirms the station is 7.69 km away as listed and 2.47 km
  with the sign flipped. This matters only for a later MOSMIX comparison.
- **MOSMIX matching and fairness (D80.4).** Any matching rule for a MOSMIX
  comparison is the owner's later decision. MOSMIX uses current station
  observations as predictors (F130.5).
- **Open item D78.2 (bias drift).** A correction that adapts to recent bias
  is a candidate build choice for stage C, tested by time-ordered
  cross-validation, identically at every airport. Nothing is decided.
- **Workflow wording (D85.1).** The workflow's header comment and the
  publish step's name still describe the old gating; cosmetic, left as is.
- **Laptop sleep (D86.5).** Long local sessions run with the laptop kept
  awake.
- **Stage A/B uncertainties still open.**
  - the v17 go-live date;
  - how complete Open-Meteo's Single Runs archive is for `icon_global`, and
    the timing at hours 18 to 23 (F124.2; kept open for stage D by D76.2);
  - retention periods not measured (WeatherNext; ICON beyond DWD's
    statement);
  - model-version histories marked unknown in F123.3;
  - whether GFS v17 retrospective runs are public (none found as of
    2026-09-28, F123.6);
  - whether MOSMIX appears in PAMORE, and whether any third party holds past
    MOSMIX issues (F130.2).

---

## Next

**Next planning session:** Review session 98b. If it passed, the owner commits and pushes and sets the GitHub About box; then plan session 99: the first of D82.5's alternatives against the baseline, under D89.6. Re-check GFS v17.
