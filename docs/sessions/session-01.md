# Session 01 — first data pull and verify-on-contact checks

## Scope of this session

This session is about **getting a small sample of the two data sources and
checking they are usable**. Do **not** build any model. Do **not** start any
later stage. Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. The
critical rules in SPEC section 2 apply throughout — especially the
missing-data rule (2.2) and the raw-data rule (2.3).

## What to do

**1. Set up the folders.**
- Create `data/raw/` for untouched raw pulls.
- Anything you generate that is not raw (notes, small summaries) goes
  somewhere separate, not in `data/raw/`.

**2. Pull a small sample of forecast data.**
- Source: Open-Meteo **Previous Runs API** (NOT the Historical Forecast API —
  see SPEC 2.1b and DECISIONS D4).
- Model: GFS. Variable: 2-metre temperature. Lead-time offset: 1 day (24h).
- Location: EGLC, latitude 51.505, longitude 0.055.
- Pull a **small sample only** — for example a few weeks in a recent month.
  This is just to confirm the API works and see the shape of the data.
- Save the raw response untouched in `data/raw/`. Record the pull date and
  the exact request URL/parameters alongside it (SPEC 2.3).

**3. Check-on-contact Q1: how far back does the forecast archive go?**
- Make a **separate** small request for an early date — around
  **March 2021** — for the same location and variable.
- Report plainly: did data come back for that early date, yes or no? This
  answers open question Q1 in DECISIONS.

**4. Pull a small sample of truth data.**
- Source: IEM ASOS/METAR download service.
- Station: EGLC. Pull the **same recent sample period** as step 2 (so the two
  can later be lined up), plus enough to see the record clearly.
- Save the raw response untouched in `data/raw/`, with pull date and exact
  query recorded.

**5. Check-on-contact Q2: how complete is EGLC's observation record?**
- For the sample pulled, count how many hourly observations are present versus
  how many would be expected if every hour were reported.
- Report the gap count and roughly where gaps fall. Do **not** fill any gaps
  (SPEC 2.2). This answers open question Q2 in DECISIONS.

## What to report at the end of the session

Paste **real output**, not descriptions:
- confirmation the folders were created;
- the shape of each sample (how many rows, what columns, the date range);
- the plain yes/no for Q1 (does 2021 data come back);
- the gap count for Q2, with a sentence on where gaps fall.

## What NOT to do

- Do not build, train, or evaluate any model.
- Do not join the two datasets yet.
- Do not fill, interpolate, or clean away any missing data.
- Do not commit anything to version control.
- If anything outside this scope looks worth doing, log it in DECISIONS.md as
  an open question — do not act on it.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md to reflect what this session actually did.
2. Add any findings (including the Q1 and Q2 answers) to DECISIONS.md.
3. Run the three-file consistency check and report anything that disagrees —
   report only, do not fix silently.
4. Write out a suggested commit message, then stop. The owner reviews and
   commits by hand.
