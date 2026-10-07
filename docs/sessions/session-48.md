# Session 48 — reserve the 2024–25 confirmation year (setup only, no experiments)

## What this session is

A small **discipline-setup** session. Before any feature experiment runs, it formally **reserves the
2024–25 test year (2024-08-01 → 2025-07-31) as an untouchable confirmation set** — carved out and
recorded so that every feature experiment that follows is run on the *other* years only, and the
final chosen model can be confirmed once, cleanly, on a year that played no part in choosing it.

**This session runs no experiment, fits no feature model, and reads no result on the reserved year.**
It sets the boundary and stops. The boundary is committed *before* the thing it constrains exists —
so no later experiment can accidentally see the reserved year.

## Why this, and why first

The F96 backtest already used every year 2022–2026 descriptively, so there is no untouched year left
to confirm a *selected* feature set on. Feature selection is itself a form of choosing-on-data, so it
needs a clean held-out year — reserved now, before experiments, or the whole feature programme has no
honest finish line (RESULTS §6; the same one-look logic as the sealed test). The owner chose
**2024–25** deliberately: it is feature-complete for every family (F97) and a solid middle year (not
the thin 2022–23, and distinct from the 2025–26 sealed year), so a final confirmation on it is
meaningful.

## The rule being locked

- **The 2024–25 year is reserved.** No feature experiment, backtest run, or model selection may use
  it — for training *or* evaluation — until the very end, when a single pre-chosen final feature set
  is confirmed on it once.
- **It is not the sealed year and does not touch it.** The 2025–26 sealed verdict (F94) stands
  untouched; this is a *separate* held-out year for the *feature-selection* programme.
- **Reserved means unseen.** Its role is confirmation only; peeking at it during the search — even to
  "check" — reintroduces exactly the selection bias the reservation exists to prevent.

## Standing rules that bind this session (SPEC §2)

- **Setup only** — no experiment, no feature model fit, no result computed on 2024–25.
- **No new data pull** — this reorganises how existing folds are used; it acquires nothing.
- **You never commit.** Prepare changes and a suggested message.

---

## Task 1 — record the reservation as a decision

Append a DECISIONS decision (next sequential D-number — check the tail, likely **D50** or **D51**;
use whatever is actually next) that states the reservation plainly and bindingly:
- **2024–25 (2024-08-01 → 2025-07-31) is the reserved confirmation year** for the feature-selection
  programme — held out of all feature experiments (train and test) until a single final feature set
  is confirmed on it once;
- it is distinct from and does not disturb the 2025–26 sealed year (F94) or any minimal-method
  verdict;
- the confirmation rule: experiments run on the non-reserved years; the winner is chosen there;
  then the one pre-committed final model is evaluated on 2024–25 exactly once, and that result
  stands as reported;
- state that this exists to prevent selection bias from the feature search, and cite F96 (the
  backtest that used all years) as the reason a fresh year had to be carved out.

## Task 2 — make the harness exclude it by construction

Adjust the backtest / experiment harness (the F96 machinery) so that feature experiments **cannot**
touch 2024–25 — the reserved year is excluded from both the training pool and the evaluation folds
for any feature-experiment run, so exclusion is enforced in code, not left to discipline.
- Concretely: the experiment folds become the rolling-origin years **minus** 2024–25 — i.e. tests on
  2022–23, 2023–24, and 2025–26, with each fold trained only on prior non-reserved data (and 2024–25
  never in a training pool for an experiment either, so a later confirmation on it is genuinely
  out-of-sample).
- Add a guard that refuses to run a feature experiment if the reserved year appears in its train or
  test set — the same "stop rather than allow" discipline as the sealed-year guards.
- **Verify the guard by construction only** (it raises on a reserved-year date) — do **not** run any
  actual feature experiment or compute any 2024–25 result to test it.

Note the honest cost in the report: excluding 2024–25 leaves the experiments with fewer/thinner folds
(2022–23 is thin), so the feature search has less data — that is the price of a clean confirmation
year, and it should be stated, not hidden.

## What NOT to do

- **Do not run any feature experiment**, fit any feature model, or compute any result on the reserved
  2024–25 year.
- **Do not pull new data.**
- **Do not touch the 2025–26 sealed year** or restate any existing verdict.
- **Do not choose or lock any feature ordering** — E1 (upper-air) and the rest are planned separately;
  this session only reserves the year and guards the harness.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not commit.**
- **Do not exceed scope** — the reservation decision and the harness guard, nothing else.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the reservation decision as written, the harness change (with the exact guard), and the
   honest note on the reduced experiment data.
2. **DECISIONS:** the reservation decision appended (next sequential D-number, verified unique). This
   stays live — it binds every future feature experiment.
3. **Refresh STATUS.md** to record session 48 and that 2024–25 is now the reserved confirmation year,
   with the feature-experiment programme to run on the non-reserved years.
4. **Archive step (routine):** move any entry that became settled per the criterion (likely none).
   Check and state.
5. **Consistency check:** new DECISIONS number next-sequential and unique; the harness guard refuses
   reserved-year dates (verified by construction, no experiment run); **no 2024–25 result was
   computed**; `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only the expected files.
6. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the body,
   `--` not em-dashes, short body — then **stop and wait for the owner's review.**
