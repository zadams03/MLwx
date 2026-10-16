# The stage C curve and its daily maximum: a descriptive analysis

Session 112, under DECISIONS D106 (finding F155), and session 114, under D107 and D108 (finding F157), which
added the comparisons with other forecasts and the official daily maximum and rewrote Part 1. Data: the 12 airports
of D103.4, spent years only (nothing valid on or after 2026-08-01). ECMWF IFS is pending (D108.2).

**Status (D106.2, D107, D108).** Descriptive only (SPEC 2.5, as F96). This changes no verdict, model, setting, rule, bar or
table, and nothing in D73, D77.6 or D105.5. It is not stage C's look: the look script's `--look` mode was not
run (D101.2); the claim airports' frozen models were refitted by the look's route only to regenerate
predictions already scored, and they reproduce F150 exactly. Nothing is selected or tuned on it. Ideas go
into Part 3 with their evidence; any change to the product is a later build choice judged by D89 on the
development airports. The owner chooses later which statistics to put first; Part 2 keeps every statistic
D106 planned, and any item picked or changed after the results were seen is labelled so.
The comparisons (session 114) are descriptive too (D107.2): they follow rules fixed before any competitor value was
scored (D107.9, D108), and scoring a competitor's test year here spends that year for that model at that airport
(D107.3, D108.5). Part 1's order was chosen by the owner after session 112's results were seen (D108.6), so it is
labelled so; model internals and drift by days since start are in Part 2 only.

**Where the files are.** Script: `scripts/session112_analysis.py`. Tables: `data/processed/session112_analysis/`
(SHA-256 of each in `analyse_meta.txt` and `contrib_meta.txt`). Figures: `figures/analysis/`. Regenerated
predictions, references and observations: `../MLwx-stagec/analysis112/` (outside the repo; SHA-256 in
`meta.txt` and `refs_meta.txt`). Full run log: `notes/session-112-output.txt`. Session 114: script
`scripts/session114_comparisons.py`; tables `data/processed/session114_comparisons/` (Part 1 and the Part 2 section
are rendered from them, `part1.md` and `part2_comparisons.md`); figures `figures/analysis/comparison_*.svg`; log
`notes/session-114-output.txt`. Competitor values: `data/processed/session113/` (F156).

**Words used here.** *Error* is observed minus forecast, in degrees C: a positive error means the forecast was
too low. *MAE* is the mean absolute error. *Skill* against a reference is 1 - MAE / MAE(reference): +20 % means
20 % smaller average error. *The curve* is the product (the baseline plus the drift correction b, SPEC 9.3).
*The baseline* is the curve without b. *Raw GFS* is GFS's 2 m temperature, adjusted for height (SPEC 5.2).
*Linear MOS* is a simple straight-line correction fitted on the same inputs and rows as the baseline. *Constant
bias* adds the average training error per cycle hour and lead. *Climatology* is the average observation at that
hour and time of year. *Persistence* repeats what was observed 24 hours (or a whole number of days) before.
*Lead* is hours after the run starts. A *[95 %]* range is a 95 % interval from a block bootstrap (7-day blocks,
F125.3's method, seed 112). *80 % of errors* means the 10th to 90th percentile. *Claim airports* (EDDM, KORD,
CYYZ, ZGSZ, ZUCK, NZWN) were never used for a build choice; *development airports* (marked dev) were, on these
same test years, so their figures flatter the method slightly (D106.3). *(sea)* marks the four airports with sea
in their grid box (D106.11). *AIFS* is ECMWF's machine-learning forecast model; *the NBM grid* is the National
Blend of Models' 2.5 km grid; *NBS* is the NBM's text forecast for a weather station; *MAV* is GFS's own
statistical station forecast (GFS MOS); *ECMWF IFS* is ECMWF's main physics model. *CLI* is the National Weather
Service's daily climate report, the official daily maximum at US airports. A *formal test* here is a
Diebold-Mariano test with the Benjamini-Hochberg false-discovery check at 0.05 across airports.

---

## Part 1. Field guide (order chosen by the owner after session 112's results were seen, D108.6, D106.2)

All figures are from spent test years (nothing valid on or after 2026-08-01). Claim airports come first; (dev)
marks the development airports, whose build choices used these years, so their figures flatter the method
slightly. Ranges run across the six claim airports unless named. Per-airport detail is in item 2's tables.

### 1. The short version

- **Hourly:** the curve's typical error (MAE) is 0.79 (NZWN) to 1.33 (EDDM) degrees C.
- **Daily maximum:** 0.74 (NZWN) to 1.25 (EDDM) degrees C, and it reads a little low (mean error +0.12 (CYYZ) to +0.25 (ZGSZ)).
- **Further ahead:** the hourly MAE grows by 16 % (EDDM) to 40 % (KORD) from leads 3-12 to leads 37-48.
- **Against raw GFS:** 11 % (KORD) to 32 % (NZWN) smaller hourly MAE, 6 % (KORD) to 56 % (NZWN) for the daily maximum.
- **Against other forecasts (formal tests, item 4):** hourly, against AIFS the curve is better at NZWN, worse
  at KORD and not separated at the other 4 claim airports; at the development airports better at
  EGLC, LFPG, KRNO and worse at KDSM, YSDU. It beats MAV at 3 of 4 and loses to NBS, the NBM
  station forecast, at 5 of 5. For the daily maximum it beats AIFS at 9 of
  12 (AIFS's maximum is the highest of four 6-hourly values; read at the same steps the curve's is
  worse at 6 of 12) and MAV at 4 of 4, and no test separates it from
  NBS at 5 of 5. ECMWF IFS is pending (D108.2).

### 2. How accurate it is x hours out

**Table 1a. Hourly MAE by lead band, degrees C (80 % of errors fall in the range shown, 10th to 90th
percentile; error = observed minus forecast).**

| airport | leads 3-12 | 13-24 | 25-36 | 37-48 |
|---|---|---|---|---|
| EDDM | 1.22 (-2.0 to +1.9) | 1.29 (-2.1 to +2.0) | 1.36 (-2.2 to +2.1) | 1.42 (-2.3 to +2.2) |
| KORD | 0.97 (-1.5 to +1.5) | 1.13 (-1.7 to +1.7) | 1.25 (-1.9 to +1.9) | 1.36 (-2.1 to +2.1) |
| CYYZ (sea) | 1.01 (-1.5 to +1.6) | 1.09 (-1.7 to +1.7) | 1.18 (-1.8 to +1.8) | 1.25 (-2.0 to +1.9) |
| ZGSZ (sea) | 0.79 (-1.3 to +1.2) | 0.87 (-1.4 to +1.3) | 0.94 (-1.5 to +1.5) | 0.99 (-1.6 to +1.5) |
| ZUCK | 0.99 (-1.5 to +1.5) | 1.05 (-1.6 to +1.6) | 1.11 (-1.7 to +1.7) | 1.18 (-1.8 to +1.8) |
| NZWN (sea) | 0.73 (-1.1 to +1.1) | 0.76 (-1.2 to +1.2) | 0.80 (-1.3 to +1.3) | 0.85 (-1.3 to +1.3) |
| EGLC (dev) | 0.73 (-1.2 to +1.1) | 0.81 (-1.3 to +1.3) | 0.87 (-1.4 to +1.4) | 0.92 (-1.5 to +1.4) |
| LFPG (dev) | 0.85 (-1.3 to +1.3) | 0.92 (-1.4 to +1.4) | 0.99 (-1.6 to +1.5) | 1.04 (-1.7 to +1.6) |
| KDSM (dev) | 1.11 (-1.8 to +1.7) | 1.23 (-2.0 to +1.8) | 1.37 (-2.2 to +2.1) | 1.46 (-2.3 to +2.2) |
| YSDU (dev) | 1.16 (-1.8 to +1.8) | 1.20 (-1.9 to +1.8) | 1.25 (-2.0 to +1.9) | 1.30 (-2.1 to +2.0) |
| KRNO (dev) | 1.12 (-1.8 to +1.7) | 1.17 (-1.9 to +1.8) | 1.24 (-2.0 to +1.9) | 1.29 (-2.0 to +2.0) |
| KSFO (dev) (sea) | 0.91 (-1.5 to +1.4) | 0.98 (-1.6 to +1.5) | 1.03 (-1.7 to +1.5) | 1.07 (-1.7 to +1.6) |

**Table 1b. Daily maximum MAE by the run's cycle hour, every cycle (80 % range; the lead at which the local day
starts).** The later the day starts after the run, the larger the error.

| airport | 00z run | 06z run | 12z run | 18z run |
|---|---|---|---|---|
| EDDM | 1.45 (-2.3 to +2.2), lead 22-23 | 1.37 (-2.2 to +2.1), lead 16-17 | 1.31 (-2.1 to +2.0), lead 10-11 | 1.25 (-2.1 to +1.8), lead 4-5 |
| KORD | 1.09 (-1.5 to +1.9), lead 5-6 | 1.30 (-1.9 to +2.2), lead 23-24 | 1.24 (-1.7 to +2.1), lead 17-18 | 1.16 (-1.5 to +2.0), lead 11-12 |
| CYYZ (sea) | 1.04 (-1.5 to +1.7), lead 4-5 | 1.21 (-1.8 to +1.9), lead 22-23 | 1.16 (-1.7 to +1.8), lead 16-17 | 1.11 (-1.5 to +1.8), lead 10-11 |
| ZGSZ (sea) | 0.99 (-1.4 to +1.8), lead 16 | 0.97 (-1.2 to +1.7), lead 10 | 0.91 (-1.2 to +1.7), lead 4 | 1.04 (-1.4 to +1.8), lead 22 |
| ZUCK | 1.25 (-1.9 to +2.1), lead 16 | 1.20 (-1.7 to +2.1), lead 10 | 1.17 (-1.6 to +2.0), lead 4 | 1.31 (-2.0 to +2.3), lead 22 |
| NZWN (sea) | 0.73 (-1.0 to +1.3), lead 11-12 | 0.74 (-1.0 to +1.3), lead 5-6 | 0.78 (-1.1 to +1.4), lead 23-24 | 0.78 (-1.0 to +1.5), lead 17-18 |
| EGLC (dev) | 0.97 (-1.5 to +1.5), lead 23-24 | 0.91 (-1.5 to +1.4), lead 17-18 | 0.88 (-1.3 to +1.4), lead 11-12 | 0.84 (-1.3 to +1.3), lead 5-6 |
| LFPG (dev) | 1.07 (-1.7 to +1.6), lead 22-23 | 1.08 (-1.8 to +1.6), lead 16-17 | 0.99 (-1.6 to +1.6), lead 10-11 | 0.96 (-1.5 to +1.5), lead 4-5 |
| KDSM (dev) | 1.22 (-2.0 to +1.9), lead 5-6 | 1.50 (-2.4 to +2.2), lead 23-24 | 1.41 (-2.4 to +2.1), lead 17-18 | 1.32 (-2.2 to +2.0), lead 11-12 |
| YSDU (dev) | 1.06 (-1.4 to +1.8), lead 13-14 | 1.03 (-1.4 to +1.8), lead 7-8 | 1.28 (-1.6 to +2.2), lead 25-26 | 1.12 (-1.5 to +1.8), lead 19-20 |
| KRNO (dev) | 0.95 (-1.3 to +1.6), lead 7-8 | 0.89 (-1.2 to +1.4), lead 25-26 | 1.01 (-1.3 to +1.7), lead 19-20 | 0.97 (-1.3 to +1.6), lead 13-14 |
| KSFO (dev) (sea) | 1.21 (-1.5 to +2.2), lead 7-8 | 1.35 (-1.7 to +2.5), lead 25-26 | 1.27 (-1.6 to +2.3), lead 19-20 | 1.24 (-1.6 to +2.3), lead 13-14 |

*Sources: `hourly_breakdowns.csv`, `hourly_ranges.csv`, `dailymax_every_cycle.csv`, `dailymax_ranges.csv`,
`dailymax_whole_day_leads.csv` (session 112); figures `hourly_ranges_fan.svg`, `dailymax_by_cycle_hour.svg`.*

### 3. The daily maximum

- **Accuracy.** On the day after the evening's run (D98.10) the MAE is 0.74 (NZWN) to 1.25 (EDDM) degrees C at the claim airports.
- **It reads low.** The mean error is +0.12 (CYYZ) to +0.25 (ZGSZ): the real maximum is on average a little warmer than shown. The
  curve's value at the observed peak hour is 0.81 (KORD) to 0.92 (ZGSZ) degrees C below the observed maximum; taking the curve's own
  highest hour wins back 0.63 (KORD) to 0.78 (EDDM). This fits a selection effect (the observed maximum is the highest of about 24
  noisy readings), but the split does not rule out some damping of the forecast peak (Table B4).
- **The hottest days.** On the observed hottest 10 % of days the curve reads low by +0.48 (ZUCK) to +0.98 (ZGSZ) degrees C (+1.97
  at KSFO (dev)); picked by the forecast instead, its mean error on the hot tail is at most +0.42 at the
  claim airports. Days picked by the observation always look like this, partly by selection (Table B3).
- **The official maximum.** At the four US airports the NWS climate report's maximum (CLI) is above our
  hourly-report maximum on average by: KORD +0.27; KDSM (dev) +0.30; KRNO (dev) +0.50; KSFO (dev) (sea) +0.48. Over the local standard time day it is KORD +0.29; KDSM +0.33; KRNO +0.50; KSFO +0.48, so the window
  explains little: the rest is a continuous reading against hourly ones. The two agree within 0.05 degrees C on
  30 % (KRNO) to 52 % (KORD) of days; 90 % of gaps are at most +0.56 (KDSM) to +1.11 (KRNO). Against CLI the curve's mean error is +0.28 (KDSM) to +0.70 (KSFO)
  (it is built to forecast the hourly maximum). Scores against CLI are in item 4.

### 4. How it compares

Each competitor is scored on its own paired rows or days (D108.4(a)), with the curve rescored on exactly the same
ones: a cell gives "competitor / curve" MAE in degrees C. * marks a formal test (Diebold-Mariano, Benjamini-Hochberg
at 0.05 across the airports) that rejects equal accuracy. The first three columns are on all scored rows or days
(F155). Linear MOS, a straight-line correction fitted on the same rows as the model, is the yardstick: the curve
beats it by +2.6 % (KORD) to +7.3 % (EDDM) hourly at the claim airports. AIFS covers 2025-02-25 on; NBM, NBS and MAV the full test years.

**Table 2a. Hourly.**

| airport | curve | raw GFS | linear MOS | AIFS | NBM grid | NBS | MAV | ECMWF IFS |
|---|---|---|---|---|---|---|---|---|
| EDDM | 1.33 | 1.79 | 1.43 | 1.21 / 1.28 | - | - | - | pending (D108.2) |
| KORD | 1.19 | 1.34 | 1.22 | 1.12 / 1.26 * | 1.05 / 1.16 * | 1.06 / 1.21 * | 1.36 / 1.21 * | pending (D108.2) |
| CYYZ (sea) | 1.14 | 1.47 | 1.20 | 1.17 / 1.18 | 1.05 / 1.12 * | 1.07 / 1.15 * | - | pending (D108.2) |
| ZGSZ (sea) | 0.90 | 1.16 | 0.94 | 0.96 / 0.89 | - | - | - | pending (D108.2) |
| ZUCK | 1.09 | 1.46 | 1.17 | 1.06 / 1.10 | - | - | - | pending (D108.2) |
| NZWN (sea) | 0.79 | 1.16 | 0.83 | 1.06 / 0.79 * | - | - | - | pending (D108.2) |
| EGLC (dev) | 0.84 | 1.04 | 0.85 | 1.13 / 0.87 * | - | - | - | pending (D108.2) |
| LFPG (dev) | 0.95 | 1.23 | 1.00 | 1.11 / 0.95 * | - | - | - | pending (D108.2) |
| KDSM (dev) | 1.30 | 1.88 | 1.43 | 1.08 / 1.35 * | 1.21 / 1.27 * | 1.16 / 1.32 * | 1.45 / 1.32 * | pending (D108.2) |
| YSDU (dev) | 1.23 | 1.52 | 1.32 | 1.12 / 1.19 * | - | - | - | pending (D108.2) |
| KRNO (dev) | 1.21 | 2.22 | 1.41 | 1.60 / 1.10 * | 1.44 / 1.19 * | 1.17 / 1.22 * | 1.16 / 1.23 * | pending (D108.2) |
| KSFO (dev) (sea) | 1.00 | 1.29 | 1.14 | 0.94 / 0.96 | 1.40 / 0.99 * | 0.92 / 1.01 * | 1.06 / 1.01 * | pending (D108.2) |

**Table 2b. Daily maximum** (D98.10's days; truth our hourly-report maximum; each competitor's own maximum: AIFS the
highest of its 6-hourly steps, NBM TMAX, NBS TXN, MAV X, windows as labelled in Part 2).

| airport | curve | raw GFS | linear MOS | AIFS | NBM grid | NBS | MAV | ECMWF IFS |
|---|---|---|---|---|---|---|---|---|
| EDDM | 1.25 | 1.79 | 1.37 | 1.21 / 1.12 | - | - | - | pending (D108.2) |
| KORD | 1.09 | 1.16 | 1.10 | 1.43 / 1.12 * | 1.14 / 1.09 | 1.12 / 1.09 | 1.47 / 1.09 * | pending (D108.2) |
| CYYZ (sea) | 1.04 | 1.34 | 1.13 | 1.39 / 1.08 * | 1.21 / 1.04 * | 1.16 / 1.04 | - | pending (D108.2) |
| ZGSZ (sea) | 0.91 | 1.52 | 1.07 | 1.23 / 0.92 * | - | - | - | pending (D108.2) |
| ZUCK | 1.17 | 1.37 | 1.30 | 1.32 / 1.20 | - | - | - | pending (D108.2) |
| NZWN (sea) | 0.74 | 1.70 | 0.83 | 1.80 / 0.72 * | - | - | - | pending (D108.2) |
| EGLC (dev) | 0.84 | 0.95 | 0.89 | 0.98 / 0.91 | - | - | - | pending (D108.2) |
| LFPG (dev) | 0.96 | 1.20 | 1.05 | 1.45 / 0.91 * | - | - | - | pending (D108.2) |
| KDSM (dev) | 1.22 | 1.73 | 1.46 | 1.43 / 1.24 * | 1.30 / 1.22 | 1.23 / 1.22 | 1.57 / 1.22 * | pending (D108.2) |
| YSDU (dev) | 1.03 | 1.09 | 1.11 | 1.48 / 0.97 * | - | - | - | pending (D108.2) |
| KRNO (dev) | 0.95 | 1.55 | 0.99 | 1.40 / 0.82 * | 0.93 / 0.95 | 0.97 / 0.95 | 1.12 / 0.95 * | pending (D108.2) |
| KSFO (dev) (sea) | 1.21 | 1.66 | 1.39 | 1.45 / 1.17 * | 1.87 / 1.21 * | 1.19 / 1.21 | 1.41 / 1.21 * | pending (D108.2) |

- **Formal tests, hourly:** the curve is better than AIFS at 4 of 12 airports
  (NZWN, EGLC, LFPG, KRNO) and worse at 3 (KORD, KDSM, YSDU); better than the NBM grid at 2
  (KRNO, KSFO) and worse at 3 (KORD, CYYZ, KDSM); worse than NBS at 5 of
  5; better than MAV at 3 (KORD, KDSM, KSFO) and worse at 1
  (KRNO).
- **Formal tests, daily maximum:** better than AIFS at 9 of 12, the NBM grid at
  2 of 5 (CYYZ, KSFO), NBS at 0 of 5, MAV at
  4 of 4; worse than no competitor at any airport.
- **Read with care.** AIFS's maximum comes from 6-hourly steps; sampled at the same steps the curve's maximum is
  -41 % (EDDM) to +46 % (NZWN) against AIFS at the claim airports (worse at 6 of 12). At the development
  airports both AIFS and the NBM grid are read at GFS's own position (D108.3), not the airport's; that position's
  distance from the airport (km, positions files): AIFS EGLC 4.3, LFPG 3.4, KDSM 1.8, YSDU 6.7, KRNO 6.0, KSFO 8.5; NBM grid KDSM 1.8, KRNO 6.0, KSFO 8.5. NBS, a station forecast, does not
  have that handicap. NBS's 01/07/13/19 UTC runs hold one
  hour more data than our cycle.

**Table 2c. The four US airports against the official maximum (CLI), daily maximum MAE, all test years.** Each
competitor on its own paired days; the curve's and raw GFS's on all D98.10 days with CLI.

| airport | curve | raw GFS | NBM TMAX | NBS TXN | MAV X |
|---|---|---|---|---|---|
| KORD | 1.15 | 1.22 | 1.10 | 1.08 | 1.40 |
| KDSM (dev) | 1.28 | 1.83 | 1.27 | 1.22 | 1.50 |
| KRNO (dev) | 1.13 | 1.95 | 1.10 | 0.83 | 0.95 |
| KSFO (dev) (sea) | 1.35 | 1.91 | 1.62 | 1.15 | 1.31 |

On the days where CLI and GHCN-Daily agree (D108.4(d)'s check), the order of the five is unchanged at 4
of 4 airports.

### 5. When to trust it less

- **Further ahead.** See item 2; the spread widens steadily with lead at every airport.
- **Season.** At EDDM the daily maximum's 5th percentile error is -4.9, -4.1, -1.6 degrees C in Sep-Nov, Dec-Feb and
  Mar-May (the shown maximum far too warm in autumn and winter). Hourly MAE in Mar-May against Sep-Nov: KORD
  1.45 against 0.89; CYYZ 1.36 against 0.91.
- **When the drift tracker is working hard.** In the top third of |b| the curve's MAE is higher than in the bottom
  third at 12 of 12 airports (by 0.01 (YSDU) to 0.22 (EDDM)). Large |b| may coincide with harder seasons or weather.
- **Cloud.** The MAE rises from the clearest to the cloudiest third of hours at KORD, CYYZ, ZGSZ, KDSM, YSDU, KRNO (by up to
  0.55 at KRNO); it falls at EDDM, ZUCK, NZWN, EGLC, LFPG, KSFO.
- **A maximum at the edge of the day.** On 7 % (ZGSZ) to 14 % (ZUCK) of days at the claim airports the observed maximum falls in
  the first or last local hour (a warm night or a front). Raw GFS puts it there on 19 % of days at ZUCK
  against 14 % observed, the case seen live in cycle 2026-10-13 06z (Part 2, D106.13).

### 6. What limits the accuracy

- **Rounded observations.** 8 of the 12 airports report whole degrees; against them even a perfect
  forecast would show an MAE of about 0.25 degrees C.
- **The curve is jagged.** Each lead has its own model, so it moves more from hour to hour than raw GFS
  (1.5 times (LFPG) to 3.3 times (ZGSZ) raw GFS's mean |second difference|).
- **Sea in the grid box.** At NZWN and ZGSZ raw GFS's daily maximum reads low by +1.64 and +1.24 degrees C; the curve
  fixes most of it.
- **What the comparisons add.** The NBM station forecast (NBS) has the smaller hourly error at 5 of
  the 5 airports it covers, so local station guidance holds information the curve does not use
  (Part 3). Figures: `comparison_hourly_mae.svg`, `comparison_dailymax_mae.svg`, `comparison_skill.svg`,
  `comparison_lead_band.svg`, `comparison_official_gap.svg`.

---

## Part 2. Appendix: every statistic D106 planned, in D106's order, then the comparisons (D107.9, D108)

Each item gives the file, a one-line note on how to read it, and the key numbers. Rows for development airports
carry the flag of D106.3 (marked dev): their build choices used these folds. Claim airports come first.
Intervals are 95 %, pooled over the test years (10,000 resamples for headline figures, 2,000 for breakdown
cells); the spread across test years is shown beside them (D106.11).

### D106.3 and D106.4: data and the forecasts compared

Regenerated predictions: 2,013,792 rows (1,206,438 scored at development airports, 804,426 at claim airports,
plus rows with complete features and no observation, predicted and never scored). They reproduce session 104's
and session 107's files exactly: Gate D, 9,936 of 9,936 cells and 6,570 of 6,570 days; Gate C, 11,100 of 11,100
score rows and 4,374 of 4,374 days. The references come from each fold's or look's own training rows; climatology,
constant bias and linear MOS have no missing value on any scored row; persistence is missing on 7 to 650 scored
rows per airport and period (the record's own gaps), which are counted and left out of its figures.

### D106.5: metrics

**Table A2. Hourly MAE of all seven forecasts and the curve's other metrics, pooled** (`hourly_headline.csv`,
`hourly_error_box.svg`, `hourly_abs_error_ecdf.svg`). Read: lower MAE is better; "share <= 1" is the share of
hours within 1 degree C.

| airport | curve | baseline | linear_mos | constant_bias | raw_gfs | climatology | persistence | curve mean error | curve RMSE | curve median abs | curve p90 abs | curve p95 abs | share <= 1 | share <= 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EDDM | 1.329 | 1.331 | 1.433 | 1.693 | 1.794 | 3.243 | 3.061 | +0.026 | 1.76 | 1.03 | 2.88 | 3.65 | 49 % | 78 % |
| KORD | 1.185 | 1.203 | 1.217 | 1.354 | 1.337 | 4.347 | 4.346 | -0.047 | 1.63 | 0.90 | 2.52 | 3.24 | 54 % | 83 % |
| CYYZ (sea) | 1.137 | 1.135 | 1.199 | 1.327 | 1.472 | 3.740 | 3.876 | -0.005 | 1.55 | 0.87 | 2.40 | 3.07 | 56 % | 85 % |
| ZGSZ (sea) | 0.900 | 0.911 | 0.944 | 1.079 | 1.159 | 1.922 | 1.800 | -0.003 | 1.22 | 0.67 | 1.98 | 2.54 | 66 % | 90 % |
| ZUCK | 1.089 | 1.093 | 1.171 | 1.433 | 1.461 | 2.822 | 2.481 | +0.007 | 1.48 | 0.83 | 2.32 | 2.96 | 58 % | 86 % |
| NZWN (sea) | 0.785 | 0.783 | 0.830 | 0.929 | 1.161 | 1.945 | 2.176 | +0.013 | 1.05 | 0.61 | 1.69 | 2.15 | 72 % | 94 % |
| EGLC (dev) | 0.839 | 0.838 | 0.847 | 0.972 | 1.042 | 2.553 | 2.327 | +0.001 | 1.11 | 0.66 | 1.77 | 2.23 | 68 % | 93 % |
| LFPG (dev) | 0.954 | 0.960 | 0.997 | 1.157 | 1.234 | 3.109 | 2.710 | -0.008 | 1.27 | 0.74 | 2.02 | 2.57 | 63 % | 90 % |
| KDSM (dev) | 1.300 | 1.323 | 1.426 | 1.746 | 1.879 | 4.439 | 4.294 | -0.023 | 1.76 | 1.00 | 2.74 | 3.51 | 50 % | 80 % |
| YSDU (dev) | 1.230 | 1.263 | 1.322 | 1.498 | 1.523 | 3.080 | 3.024 | -0.010 | 1.68 | 0.94 | 2.61 | 3.34 | 53 % | 82 % |
| KRNO (dev) | 1.208 | 1.228 | 1.412 | 1.859 | 2.219 | 3.387 | 2.985 | -0.011 | 1.67 | 0.89 | 2.63 | 3.43 | 55 % | 82 % |
| KSFO (dev) (sea) | 1.004 | 1.085 | 1.140 | 1.233 | 1.292 | 1.813 | 1.713 | -0.068 | 1.34 | 0.77 | 2.16 | 2.75 | 61 % | 88 % |

**Table A3. The curve's skill against each reference, hourly (percent [95 %])** (`hourly_curve_skill.csv`).
Read: positive means the curve's MAE is smaller.

| airport | raw GFS | persistence | climatology | constant bias | linear MOS | baseline |
|---|---|---|---|---|---|---|
| EDDM | +25.9 [+22.2, +29.4] | +56.6 [+53.4, +59.3] | +59.0 [+56.0, +61.7] | +21.5 [+18.0, +24.9] | +7.3 [+4.7, +9.7] | +0.2 [-1.3, +1.6] |
| KORD | +11.3 [+9.3, +13.3] | +72.7 [+70.9, +74.6] | +72.7 [+70.6, +74.9] | +12.4 [+10.2, +14.7] | +2.6 [+0.9, +4.4] | +1.5 [+0.2, +2.7] |
| CYYZ (sea) | +22.8 [+18.9, +26.2] | +70.7 [+68.9, +72.6] | +69.6 [+67.6, +71.6] | +14.3 [+11.9, +16.7] | +5.2 [+3.6, +6.8] | -0.2 [-1.0, +0.5] |
| ZGSZ (sea) | +22.4 [+19.3, +25.3] | +50.0 [+46.7, +53.3] | +53.2 [+49.0, +57.0] | +16.6 [+13.5, +19.6] | +4.7 [+2.7, +6.7] | +1.3 [+0.2, +2.4] |
| ZUCK | +25.5 [+21.4, +29.4] | +56.1 [+53.4, +58.9] | +61.4 [+58.0, +64.8] | +24.0 [+19.9, +27.8] | +7.0 [+4.2, +9.6] | +0.4 [-0.9, +1.6] |
| NZWN (sea) | +32.4 [+29.2, +35.2] | +63.9 [+62.1, +65.7] | +59.6 [+57.3, +61.8] | +15.5 [+12.7, +17.8] | +5.4 [+4.0, +6.7] | -0.3 [-0.7, +0.1] |
| EGLC (dev) | +19.6 [+17.3, +21.6] | +64.0 [+62.0, +65.8] | +67.2 [+64.8, +69.3] | +13.8 [+12.1, +15.3] | +1.0 [-0.1, +2.0] | -0.1 [-0.8, +0.5] |
| LFPG (dev) | +22.6 [+19.5, +25.5] | +64.8 [+62.9, +66.5] | +69.3 [+67.0, +71.3] | +17.5 [+15.1, +19.8] | +4.3 [+2.7, +5.8] | +0.5 [-0.3, +1.3] |
| KDSM (dev) | +30.8 [+27.3, +34.1] | +69.7 [+67.7, +71.7] | +70.7 [+68.6, +72.9] | +25.5 [+22.5, +28.5] | +8.9 [+6.6, +10.8] | +1.7 [+0.6, +2.8] |
| YSDU (dev) | +19.2 [+17.2, +21.2] | +59.3 [+57.4, +61.2] | +60.0 [+57.6, +62.5] | +17.9 [+16.1, +19.7] | +6.9 [+5.2, +8.7] | +2.6 [+1.6, +3.6] |
| KRNO (dev) | +45.6 [+42.5, +48.7] | +59.5 [+57.4, +61.7] | +64.3 [+62.0, +66.7] | +35.0 [+31.4, +38.8] | +14.4 [+11.8, +17.3] | +1.7 [+0.8, +2.5] |
| KSFO (dev) (sea) | +22.3 [+19.2, +25.3] | +41.4 [+37.5, +44.9] | +44.6 [+41.2, +47.9] | +18.6 [+15.0, +22.1] | +11.9 [+9.1, +14.6] | +7.5 [+4.9, +10.0] |

**Table A4. Per test year: the curve against raw GFS, hourly** (`hourly_headline.csv`). Read: this is the spread
across years that sits beside each pooled interval.

| airport | period | n | curve MAE [95 %] | raw GFS MAE | curve mean error | skill against raw GFS [95 %] |
|---|---|---|---|---|---|---|
| EDDM | A | 67160 | 1.3099 [1.229, 1.402] | 1.7425 | -0.016 [-0.132, +0.103] | +24.8 [+19.2, +30.2] |
| EDDM | B | 66968 | 1.3484 [1.278, 1.432] | 1.8461 | +0.068 [-0.070, +0.211] | +27.0 [+22.0, +31.2] |
| KORD | A | 67137 | 1.1495 [1.075, 1.233] | 1.3427 | -0.045 [-0.168, +0.079] | +14.4 [+11.3, +17.3] |
| KORD | B | 66749 | 1.2214 [1.141, 1.308] | 1.3307 | -0.049 [-0.193, +0.097] | +8.2 [+5.9, +10.6] |
| CYYZ (sea) | A | 67075 | 1.1549 [1.086, 1.230] | 1.4814 | -0.018 [-0.140, +0.108] | +22.0 [+17.2, +26.2] |
| CYYZ (sea) | B | 66968 | 1.1192 [1.044, 1.208] | 1.4627 | +0.008 [-0.116, +0.128] | +23.5 [+17.3, +28.9] |
| ZGSZ (sea) | A | 67160 | 0.9186 [0.870, 0.970] | 1.1722 | -0.002 [-0.105, +0.107] | +21.6 [+17.9, +25.8] |
| ZGSZ (sea) | B | 66968 | 0.8808 [0.827, 0.925] | 1.1452 | -0.004 [-0.105, +0.088] | +23.1 [+18.8, +27.8] |
| ZUCK | A | 67160 | 1.1301 [1.052, 1.217] | 1.4853 | +0.053 [-0.087, +0.197] | +23.9 [+18.2, +29.0] |
| ZUCK | B | 66976 | 1.0480 [0.987, 1.102] | 1.4369 | -0.039 [-0.156, +0.055] | +27.1 [+20.7, +32.5] |
| NZWN (sea) | A | 67153 | 0.7879 [0.753, 0.822] | 1.1537 | +0.001 [-0.060, +0.062] | +31.7 [+27.5, +35.9] |
| NZWN (sea) | B | 66952 | 0.7826 [0.744, 0.816] | 1.1678 | +0.024 [-0.052, +0.088] | +33.0 [+29.1, +37.2] |
| EGLC (dev) | 2023-24 | 67337 | 0.8028 [0.773, 0.835] | 1.0268 | +0.027 [-0.045, +0.094] | +21.8 [+17.5, +25.7] |
| EGLC (dev) | 2024-25 | 67128 | 0.8722 [0.828, 0.919] | 1.0595 | -0.003 [-0.083, +0.073] | +17.7 [+14.3, +21.1] |
| EGLC (dev) | 2025-26 | 66939 | 0.8410 [0.789, 0.893] | 1.0411 | -0.022 [-0.118, +0.072] | +19.2 [+15.7, +22.5] |
| LFPG (dev) | 2023-24 | 67267 | 0.9209 [0.868, 0.970] | 1.2197 | +0.051 [-0.037, +0.127] | +24.5 [+18.9, +29.3] |
| LFPG (dev) | 2024-25 | 67035 | 1.0167 [0.961, 1.077] | 1.2491 | -0.043 [-0.166, +0.073] | +18.6 [+13.8, +22.9] |
| LFPG (dev) | 2025-26 | 66730 | 0.9257 [0.885, 0.974] | 1.2319 | -0.031 [-0.129, +0.064] | +24.9 [+19.0, +29.7] |
| KDSM (dev) | 2023-24 | 67328 | 1.3266 [1.257, 1.381] | 2.0340 | +0.068 [-0.054, +0.238] | +34.8 [+28.1, +41.2] |
| KDSM (dev) | 2024-25 | 67153 | 1.2350 [1.179, 1.285] | 1.7774 | -0.073 [-0.216, +0.043] | +30.5 [+25.5, +35.0] |
| KDSM (dev) | 2025-26 | 66968 | 1.3384 [1.261, 1.435] | 1.8265 | -0.064 [-0.243, +0.113] | +26.7 [+20.7, +31.3] |
| YSDU (dev) | 2023-24 | 66806 | 1.2579 [1.211, 1.316] | 1.5344 | -0.037 [-0.154, +0.090] | +18.0 [+14.0, +21.7] |
| YSDU (dev) | 2024-25 | 66752 | 1.2376 [1.183, 1.302] | 1.5691 | -0.031 [-0.155, +0.098] | +21.1 [+17.7, +24.5] |
| YSDU (dev) | 2025-26 | 66323 | 1.1956 [1.140, 1.255] | 1.4638 | +0.038 [-0.067, +0.162] | +18.3 [+15.3, +21.0] |
| KRNO (dev) | 2023-24 | 67313 | 1.2397 [1.156, 1.339] | 2.0344 | +0.046 [-0.109, +0.186] | +39.1 [+34.7, +43.1] |
| KRNO (dev) | 2024-25 | 67137 | 1.2319 [1.126, 1.351] | 2.3459 | -0.023 [-0.195, +0.143] | +47.5 [+42.8, +52.2] |
| KRNO (dev) | 2025-26 | 66900 | 1.1518 [1.070, 1.258] | 2.2767 | -0.056 [-0.180, +0.078] | +49.4 [+43.3, +54.8] |
| KSFO (dev) (sea) | 2023-24 | 67323 | 0.9984 [0.939, 1.052] | 1.2896 | -0.086 [-0.215, +0.070] | +22.6 [+17.1, +28.2] |
| KSFO (dev) (sea) | 2024-25 | 67099 | 1.0250 [0.923, 1.119] | 1.2491 | -0.092 [-0.266, +0.106] | +17.9 [+13.8, +23.0] |
| KSFO (dev) (sea) | 2025-26 | 66900 | 0.9878 [0.916, 1.077] | 1.3382 | -0.026 [-0.188, +0.115] | +26.2 [+21.3, +30.7] |

**Table A5. Conditional bias** (`hourly_conditional_bias.csv`, `hourly_conditional_bias.svg`). Read: the slope
of observed on forecast (1 is ideal) and the mean error in the coldest and warmest tenth of forecasts (decile
edges from each training period's raw GFS). A slope above 1 means the forecast's range is too narrow.

| airport | raw GFS: slope, mean error in deciles 1 and 10 | linear MOS | curve |
|---|---|---|---|
| EDDM | 1.087; -0.61, +1.43 | 1.019; +0.19, +0.42 | 1.002; +0.05, +0.10 |
| KORD | 1.007; -0.15, -0.21 | 0.996; -0.13, -0.40 | 0.997; -0.04, -0.15 |
| CYYZ (sea) | 0.993; +1.07, +0.26 | 0.981; +0.69, -0.24 | 0.991; +0.29, -0.13 |
| ZGSZ (sea) | 1.100; -0.98, +0.65 | 0.983; +0.24, -0.04 | 0.989; +0.06, -0.14 |
| ZUCK | 1.081; -1.22, +0.54 | 1.010; +0.23, +0.57 | 0.988; +0.05, -0.31 |
| NZWN (sea) | 1.161; -0.09, +1.58 | 0.982; +0.10, -0.01 | 0.985; +0.16, -0.05 |
| EGLC (dev) | 0.964; +0.10, -0.59 | 1.002; -0.19, -0.16 | 0.993; +0.05, -0.12 |
| LFPG (dev) | 0.997; -0.19, -0.20 | 0.993; -0.15, -0.21 | 0.992; -0.06, -0.14 |
| KDSM (dev) | 1.019; -0.08, -0.83 | 0.993; +0.03, -0.78 | 0.990; +0.36, -0.23 |
| YSDU (dev) | 0.998; -1.23, -0.89 | 1.017; -0.27, +0.17 | 1.005; -0.01, -0.03 |
| KRNO (dev) | 1.067; -1.15, +0.47 | 1.009; -0.25, -0.10 | 1.002; -0.10, +0.02 |
| KSFO (dev) (sea) | 0.979; +0.03, -0.09 | 0.980; -0.02, -0.37 | 0.989; +0.22, -0.08 |

### D106.6: breakdowns

All in `hourly_breakdowns.csv` (every condition, bin and forecast, with n, MAE, mean error, both intervals and
the MAE in each test year). Figures: `hourly_mae_by_lead.svg`, `hourly_me_by_lead.svg`,
`hourly_mae_by_local_hour.svg`, `hourly_me_by_local_hour.svg`, `hourly_mae_by_month.svg`,
`hourly_me_by_month.svg`, `hourly_regimes.svg`.

**Table A6a. The curve's MAE by lead band [95 %] (raw GFS MAE in brackets).** Read: how fast the error grows.

| airport | 3-12 | 13-24 | 25-36 | 37-48 |
|---|---|---|---|---|
| EDDM | 1.22 [1.17, 1.28] (1.71) | 1.29 [1.23, 1.35] (1.76) | 1.36 [1.31, 1.43] (1.83) | 1.42 [1.36, 1.49] (1.86) |
| KORD | 0.97 [0.92, 1.01] (1.14) | 1.13 [1.07, 1.18] (1.28) | 1.25 [1.19, 1.32] (1.40) | 1.36 [1.28, 1.43] (1.49) |
| CYYZ (sea) | 1.01 [0.96, 1.05] (1.37) | 1.09 [1.04, 1.14] (1.44) | 1.18 [1.12, 1.24] (1.51) | 1.25 [1.19, 1.32] (1.56) |
| ZGSZ (sea) | 0.79 [0.76, 0.81] (1.03) | 0.87 [0.83, 0.90] (1.12) | 0.94 [0.90, 0.98] (1.20) | 0.99 [0.95, 1.04] (1.26) |
| ZUCK | 0.99 [0.95, 1.04] (1.35) | 1.05 [1.00, 1.10] (1.43) | 1.11 [1.06, 1.16] (1.49) | 1.18 [1.12, 1.24] (1.55) |
| NZWN (sea) | 0.73 [0.70, 0.75] (1.12) | 0.76 [0.73, 0.78] (1.15) | 0.80 [0.77, 0.83] (1.17) | 0.85 [0.82, 0.87] (1.19) |
| EGLC (dev) | 0.73 [0.71, 0.75] (0.92) | 0.81 [0.78, 0.84] (1.01) | 0.87 [0.85, 0.90] (1.08) | 0.92 [0.89, 0.96] (1.13) |
| LFPG (dev) | 0.85 [0.82, 0.88] (1.12) | 0.92 [0.89, 0.95] (1.20) | 0.99 [0.96, 1.03] (1.28) | 1.04 [1.01, 1.08] (1.32) |
| KDSM (dev) | 1.11 [1.08, 1.14] (1.69) | 1.23 [1.20, 1.27] (1.81) | 1.37 [1.32, 1.42] (1.95) | 1.46 [1.40, 1.52] (2.03) |
| YSDU (dev) | 1.16 [1.13, 1.19] (1.43) | 1.20 [1.16, 1.23] (1.49) | 1.25 [1.21, 1.29] (1.55) | 1.30 [1.27, 1.35] (1.60) |
| KRNO (dev) | 1.12 [1.06, 1.17] (2.16) | 1.17 [1.12, 1.23] (2.18) | 1.24 [1.18, 1.30] (2.24) | 1.29 [1.23, 1.36] (2.28) |
| KSFO (dev) (sea) | 0.91 [0.87, 0.95] (1.21) | 0.98 [0.93, 1.03] (1.28) | 1.03 [0.98, 1.09] (1.32) | 1.07 [1.02, 1.13] (1.35) |

**Table A6b. The curve's MAE by cycle hour and by season.** Read: the cycle hour barely matters for hourly
values; the season does at some airports.

| airport | 00z | 06z | 12z | 18z | Dec-Feb | Mar-May | Jun-Aug | Sep-Nov |
|---|---|---|---|---|---|---|---|---|
| EDDM | 1.33 | 1.33 | 1.31 | 1.35 | 1.39 | 1.28 | 1.18 | 1.47 |
| KORD | 1.18 | 1.20 | 1.19 | 1.17 | 1.22 | 1.45 | 1.18 | 0.89 |
| CYYZ (sea) | 1.14 | 1.14 | 1.14 | 1.13 | 1.22 | 1.36 | 1.05 | 0.91 |
| ZGSZ (sea) | 0.90 | 0.90 | 0.89 | 0.91 | 0.94 | 0.90 | 0.91 | 0.85 |
| ZUCK | 1.07 | 1.07 | 1.09 | 1.12 | 0.93 | 1.16 | 1.18 | 1.08 |
| NZWN (sea) | 0.78 | 0.79 | 0.78 | 0.79 | 0.79 | 0.82 | 0.82 | 0.70 |
| EGLC (dev) | 0.85 | 0.84 | 0.82 | 0.85 | 0.77 | 0.91 | 0.87 | 0.80 |
| LFPG (dev) | 0.97 | 0.96 | 0.93 | 0.96 | 0.94 | 0.94 | 1.01 | 0.92 |
| KDSM (dev) | 1.30 | 1.32 | 1.30 | 1.29 | 1.41 | 1.36 | 1.24 | 1.18 |
| YSDU (dev) | 1.23 | 1.23 | 1.22 | 1.24 | 1.26 | 1.16 | 1.22 | 1.29 |
| KRNO (dev) | 1.22 | 1.22 | 1.20 | 1.20 | 1.50 | 1.04 | 0.98 | 1.32 |
| KSFO (dev) (sea) | 1.01 | 1.02 | 1.00 | 0.99 | 1.04 | 0.86 | 1.04 | 1.07 |

**Table A7. Regimes: the curve's MAE in the low, mid and high third (raw GFS in brackets).** Read: higher in a
third means less trust in that regime. The last two columns (observed range and observed 24 h change) are only
known afterwards (secondary). Tercile edges come from each airport's training rows (per fold at development
airports), written to `bin_edges.csv` before any test error was computed; |b| (abs_b) and curve minus raw GFS
have no value on training rows, so their edges come from the test forecasts' own values, forecast side only
(a choice the plan left open, F155). Raw GFS's and the observed diurnal range need a whole local day inside the
cycle's leads 0 to 48, so about half of the rows have no value there and are left out of those two columns.

| airport | cloud_cover | wind_speed_10m | raw_range | raw_change24 | abs_b | curve_minus_raw | obs_range | obs_change24 |
|---|---|---|---|---|---|---|---|---|
| EDDM | 1.40/1.36/1.20 (2.09/1.70/1.49) | 1.47/1.34/1.14 (2.10/1.77/1.42) | 1.26/1.52/1.23 (1.48/1.87/2.09) | 1.41/1.40/1.36 (1.74/1.90/1.89) | 1.24/1.30/1.46 (1.71/1.78/1.89) | 1.64/1.19/1.15 (2.29/1.25/1.85) | 1.29/1.37/1.33 (1.47/1.62/2.19) | 1.42/1.30/1.28 (1.88/1.78/1.75) |
| KORD | 1.01/1.24/1.31 (1.24/1.38/1.40) | 1.14/1.15/1.26 (1.37/1.29/1.35) | 1.12/1.21/1.25 (1.22/1.36/1.44) | 1.38/1.17/1.34 (1.51/1.33/1.48) | 1.12/1.16/1.27 (1.30/1.30/1.40) | 1.09/1.14/1.33 (1.31/1.15/1.55) | 1.16/1.18/1.21 (1.22/1.35/1.42) | 1.34/1.02/1.21 (1.46/1.18/1.38) |
| CYYZ (sea) | 1.01/1.18/1.23 (1.44/1.51/1.47) | 1.14/1.14/1.14 (1.57/1.50/1.37) | 1.09/1.14/1.16 (1.28/1.44/1.66) | 1.22/1.12/1.29 (1.55/1.44/1.60) | 1.08/1.12/1.21 (1.44/1.45/1.52) | 1.03/1.08/1.30 (1.08/1.26/2.08) | 1.10/1.13/1.16 (1.28/1.42/1.60) | 1.18/1.02/1.21 (1.31/1.34/1.74) |
| ZGSZ (sea) | 0.77/0.91/1.03 (1.14/1.13/1.21) | 0.91/0.88/0.91 (1.17/1.12/1.19) | 0.93/0.79/0.97 (1.14/1.07/1.25) | 1.10/0.78/0.98 (1.34/1.09/1.24) | 0.86/0.89/0.95 (1.10/1.14/1.24) | 0.96/0.85/0.89 (1.18/0.95/1.35) | 0.91/0.86/0.94 (1.07/1.08/1.27) | 1.13/0.65/0.88 (1.22/0.95/1.24) |
| ZUCK | 1.13/1.16/1.00 (1.58/1.53/1.31) | 1.00/1.04/1.22 (1.41/1.45/1.52) | 0.90/1.20/1.16 (1.22/1.66/1.50) | 1.25/1.03/1.16 (1.50/1.45/1.62) | 1.01/1.04/1.22 (1.42/1.44/1.53) | 0.99/1.05/1.23 (1.66/1.09/1.64) | 0.85/1.18/1.15 (1.16/1.50/1.59) | 1.40/0.91/1.06 (1.62/1.37/1.45) |
| NZWN (sea) | 0.80/0.77/0.78 (1.27/1.11/1.09) | 1.00/0.77/0.63 (1.27/1.15/1.08) | 0.69/0.76/0.89 (0.97/1.15/1.33) | 0.89/0.78/0.79 (1.18/1.23/1.14) | 0.76/0.77/0.82 (1.16/1.15/1.17) | 0.90/0.68/0.77 (1.03/0.97/1.48) | 0.70/0.72/0.91 (0.88/1.11/1.40) | 0.90/0.74/0.75 (1.09/1.00/1.32) |
| EGLC (dev) | 0.86/0.86/0.80 (1.13/1.04/0.96) | 0.91/0.84/0.78 (1.13/1.05/0.96) | 0.77/0.83/0.93 (0.89/1.03/1.23) | 0.87/0.89/0.92 (1.12/1.07/1.12) | 0.80/0.83/0.88 (1.00/1.04/1.09) | 0.93/0.78/0.81 (1.06/0.85/1.22) | 0.81/0.79/0.89 (0.93/1.01/1.15) | 0.92/0.77/0.84 (1.04/0.96/1.10) |
| LFPG (dev) | 0.97/0.99/0.91 (1.36/1.26/1.10) | 1.03/0.96/0.87 (1.37/1.30/1.03) | 0.90/1.01/0.97 (1.02/1.29/1.48) | 0.99/1.02/1.03 (1.27/1.30/1.33) | 0.90/0.93/1.03 (1.19/1.22/1.29) | 1.02/0.89/0.96 (1.16/0.96/1.58) | 0.94/0.97/0.96 (1.05/1.23/1.41) | 1.06/0.88/0.94 (1.23/1.12/1.31) |
| KDSM (dev) | 1.18/1.36/1.36 (1.96/1.94/1.74) | 1.26/1.29/1.36 (1.97/1.92/1.74) | 1.33/1.32/1.30 (1.63/1.93/2.07) | 1.50/1.33/1.39 (2.05/2.01/1.90) | 1.24/1.27/1.38 (1.74/1.79/2.11) | 1.29/1.30/1.31 (1.64/1.41/2.58) | 1.36/1.29/1.24 (1.74/1.96/1.95) | 1.46/1.19/1.25 (1.80/1.90/1.94) |
| YSDU (dev) | 1.04/1.24/1.44 (1.40/1.51/1.68) | 1.32/1.22/1.15 (1.92/1.39/1.27) | 1.35/1.21/1.19 (1.54/1.53/1.52) | 1.37/1.19/1.26 (1.64/1.46/1.61) | 1.23/1.21/1.25 (1.53/1.50/1.54) | 1.32/1.18/1.19 (1.99/1.23/1.35) | 1.33/1.24/1.18 (1.42/1.46/1.60) | 1.50/1.07/1.16 (1.91/1.44/1.33) |
| KRNO (dev) | 0.92/1.21/1.47 (2.23/2.15/2.26) | 1.19/1.27/1.17 (2.74/2.02/1.84) | 1.50/1.14/0.88 (2.28/2.33/1.88) | 1.41/1.19/1.18 (2.00/2.40/2.37) | 1.17/1.19/1.26 (2.28/2.21/2.16) | 1.32/1.19/1.11 (3.35/1.30/2.01) | 1.55/1.11/0.94 (1.86/2.26/2.59) | 1.34/1.05/1.25 (2.16/2.42/2.05) |
| KSFO (dev) (sea) | 1.05/1.00/0.97 (1.48/1.24/1.17) | 0.98/1.01/1.03 (1.35/1.29/1.23) | 0.90/0.98/1.18 (1.14/1.29/1.50) | 1.03/0.97/1.15 (1.25/1.25/1.51) | 0.95/0.97/1.09 (1.26/1.24/1.38) | 1.12/0.94/0.95 (1.51/1.02/1.34) | 0.95/0.94/1.14 (1.16/1.17/1.57) | 1.05/0.87/1.08 (1.26/1.15/1.45) |

### D106.7: the daily maximum (the main section)

**(a) Scored days** (`dailymax_headline.csv`, `dailymax_curve_skill.csv`, `dailymax_error_box.svg`,
`dailymax_error_hist.svg`). D98.10's days, one cycle per day; they reproduce F147.6 and F150 exactly (729 of 729
days at each claim airport, 1,095 of 1,095 at each development airport).

**Table B1a. Daily maximum MAE of all seven forecasts and the curve's other metrics.**

| airport | curve | baseline | linear_mos | constant_bias | raw_gfs | climatology | persistence | curve mean error | curve RMSE | curve median abs | curve p90 abs | curve p95 abs | share <= 1 | share <= 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EDDM | 1.247 | 1.266 | 1.370 | 1.538 | 1.789 | 3.836 | 3.687 | +0.133 | 1.70 | 0.93 | 2.76 | 3.70 | 53 % | 81 % |
| KORD | 1.092 | 1.083 | 1.097 | 1.111 | 1.162 | 4.637 | 4.970 | +0.181 | 1.44 | 0.85 | 2.31 | 2.90 | 56 % | 86 % |
| CYYZ (sea) | 1.042 | 1.017 | 1.131 | 1.238 | 1.339 | 3.825 | 4.465 | +0.125 | 1.42 | 0.82 | 2.28 | 2.88 | 61 % | 87 % |
| ZGSZ (sea) | 0.913 | 0.930 | 1.066 | 1.139 | 1.521 | 2.119 | 2.173 | +0.245 | 1.17 | 0.73 | 1.93 | 2.26 | 62 % | 91 % |
| ZUCK | 1.172 | 1.192 | 1.298 | 1.364 | 1.371 | 3.639 | 3.462 | +0.164 | 1.54 | 0.91 | 2.50 | 3.17 | 54 % | 83 % |
| NZWN (sea) | 0.740 | 0.744 | 0.828 | 0.930 | 1.700 | 1.944 | 2.088 | +0.168 | 0.97 | 0.58 | 1.60 | 1.95 | 73 % | 95 % |
| EGLC (dev) | 0.841 | 0.848 | 0.889 | 0.949 | 0.946 | 2.903 | 2.655 | +0.048 | 1.12 | 0.66 | 1.72 | 2.25 | 66 % | 93 % |
| LFPG (dev) | 0.956 | 0.978 | 1.054 | 1.153 | 1.197 | 3.415 | 3.087 | +0.014 | 1.27 | 0.74 | 2.08 | 2.57 | 64 % | 89 % |
| KDSM (dev) | 1.224 | 1.254 | 1.456 | 1.697 | 1.730 | 4.866 | 5.025 | -0.031 | 1.62 | 0.94 | 2.59 | 3.19 | 53 % | 81 % |
| YSDU (dev) | 1.027 | 1.047 | 1.114 | 1.125 | 1.086 | 3.515 | 3.299 | +0.144 | 1.42 | 0.78 | 2.20 | 2.87 | 62 % | 87 % |
| KRNO (dev) | 0.948 | 0.949 | 0.990 | 1.108 | 1.551 | 4.003 | 3.693 | +0.156 | 1.30 | 0.71 | 2.07 | 2.72 | 65 % | 89 % |
| KSFO (dev) (sea) | 1.208 | 1.249 | 1.391 | 1.453 | 1.663 | 2.390 | 2.540 | +0.227 | 1.60 | 0.95 | 2.63 | 3.31 | 53 % | 82 % |

**Table B1b. The curve's skill against each reference, daily maximum (percent [95 %]).**

| airport | raw GFS | persistence | climatology | constant bias | linear MOS | baseline |
|---|---|---|---|---|---|---|
| EDDM | +30.3 [+24.6, +35.1] | +66.2 [+61.5, +69.8] | +67.5 [+62.7, +71.2] | +18.9 [+13.4, +23.4] | +8.9 [+5.3, +12.3] | +1.4 [-1.4, +4.1] |
| KORD | +6.0 [+1.1, +10.4] | +78.0 [+76.0, +79.9] | +76.4 [+74.3, +78.5] | +1.7 [-3.2, +5.9] | +0.4 [-3.5, +3.8] | -0.8 [-4.0, +2.1] |
| CYYZ (sea) | +22.2 [+16.1, +27.8] | +76.6 [+74.5, +78.9] | +72.8 [+70.3, +75.3] | +15.9 [+10.4, +21.0] | +7.9 [+3.2, +12.3] | -2.4 [-4.2, -0.5] |
| ZGSZ (sea) | +40.0 [+36.2, +43.7] | +58.0 [+53.9, +62.0] | +56.9 [+53.2, +60.5] | +19.8 [+16.1, +23.7] | +14.4 [+10.7, +18.2] | +1.9 [+0.1, +3.7] |
| ZUCK | +14.5 [+9.9, +18.9] | +66.1 [+63.8, +68.9] | +67.8 [+63.9, +71.4] | +14.0 [+9.3, +18.5] | +9.7 [+5.4, +14.1] | +1.7 [-0.3, +3.6] |
| NZWN (sea) | +56.5 [+53.1, +59.6] | +64.6 [+61.3, +67.6] | +61.9 [+59.0, +64.9] | +20.5 [+15.5, +25.4] | +10.7 [+6.4, +14.7] | +0.6 [-0.6, +1.8] |
| EGLC (dev) | +11.1 [+7.1, +14.5] | +68.3 [+65.7, +70.6] | +71.0 [+67.9, +73.6] | +11.4 [+7.1, +15.1] | +5.4 [+2.6, +7.8] | +0.8 [-1.1, +2.6] |
| LFPG (dev) | +20.1 [+16.1, +23.7] | +69.0 [+66.2, +71.3] | +72.0 [+68.9, +74.6] | +17.1 [+12.7, +21.0] | +9.3 [+6.0, +12.5] | +2.3 [-0.3, +4.8] |
| KDSM (dev) | +29.2 [+23.5, +34.5] | +75.6 [+73.4, +77.9] | +74.8 [+72.4, +77.3] | +27.9 [+22.2, +33.0] | +16.0 [+11.5, +19.9] | +2.4 [-0.0, +4.6] |
| YSDU (dev) | +5.5 [+0.3, +10.1] | +68.8 [+66.0, +71.2] | +70.8 [+67.4, +73.8] | +8.7 [+3.7, +13.3] | +7.8 [+4.1, +11.7] | +2.0 [-0.5, +4.3] |
| KRNO (dev) | +38.9 [+34.8, +42.8] | +74.3 [+72.0, +76.5] | +76.3 [+73.7, +78.8] | +14.4 [+10.3, +18.7] | +4.3 [+0.0, +8.7] | +0.1 [-2.7, +2.9] |
| KSFO (dev) (sea) | +27.4 [+23.5, +31.4] | +52.5 [+48.2, +56.6] | +49.5 [+45.2, +53.5] | +16.9 [+12.6, +21.1] | +13.2 [+9.5, +17.0] | +3.3 [-0.2, +6.8] |

**Table B1c. Per test year: the curve against raw GFS, daily maximum.**

| airport | period | n | curve MAE [95 %] | raw GFS MAE | curve mean error | skill against raw GFS [95 %] |
|---|---|---|---|---|---|---|
| EDDM | A | 365 | 1.2670 [1.079, 1.493] | 1.7879 | +0.032 [-0.282, +0.310] | +29.1 [+21.7, +35.7] |
| EDDM | B | 364 | 1.2277 [1.094, 1.399] | 1.7905 | +0.234 [+0.010, +0.457] | +31.4 [+22.8, +38.4] |
| KORD | A | 365 | 1.0657 [0.957, 1.188] | 1.1752 | +0.157 [-0.014, +0.344] | +9.3 [+2.6, +15.3] |
| KORD | B | 361 | 1.1186 [1.030, 1.221] | 1.1484 | +0.205 [+0.029, +0.389] | +2.6 [-5.0, +8.3] |
| CYYZ (sea) | A | 364 | 1.0581 [0.947, 1.185] | 1.3776 | +0.144 [-0.034, +0.315] | +23.2 [+14.9, +30.4] |
| CYYZ (sea) | B | 364 | 1.0251 [0.922, 1.144] | 1.3013 | +0.105 [-0.070, +0.266] | +21.2 [+12.0, +29.6] |
| ZGSZ (sea) | A | 365 | 0.9050 [0.825, 0.987] | 1.5162 | +0.220 [+0.082, +0.357] | +40.3 [+34.5, +45.8] |
| ZGSZ (sea) | B | 364 | 0.9207 [0.834, 0.995] | 1.5250 | +0.271 [+0.130, +0.409] | +39.6 [+34.9, +44.8] |
| ZUCK | A | 365 | 1.1950 [1.086, 1.324] | 1.4032 | +0.221 [+0.048, +0.410] | +14.8 [+8.6, +20.7] |
| ZUCK | B | 364 | 1.1493 [1.047, 1.243] | 1.3386 | +0.107 [-0.083, +0.260] | +14.1 [+6.5, +20.4] |
| NZWN (sea) | A | 365 | 0.7505 [0.682, 0.825] | 1.6959 | +0.131 [+0.013, +0.244] | +55.7 [+50.2, +60.7] |
| NZWN (sea) | B | 363 | 0.7292 [0.658, 0.797] | 1.7039 | +0.205 [+0.093, +0.308] | +57.2 [+53.6, +61.1] |
| EGLC (dev) | 2023-24 | 366 | 0.7867 [0.714, 0.863] | 0.8967 | +0.134 [+0.027, +0.229] | +12.3 [+5.2, +19.0] |
| EGLC (dev) | 2024-25 | 365 | 0.8729 [0.779, 0.970] | 0.9279 | +0.041 [-0.114, +0.197] | +5.9 [+0.5, +11.8] |
| EGLC (dev) | 2025-26 | 364 | 0.8636 [0.755, 0.981] | 1.0138 | -0.032 [-0.204, +0.138] | +14.8 [+7.3, +20.1] |
| LFPG (dev) | 2023-24 | 366 | 0.9170 [0.833, 1.008] | 1.1091 | +0.149 [-0.006, +0.287] | +17.3 [+10.2, +23.0] |
| LFPG (dev) | 2024-25 | 365 | 1.0649 [0.958, 1.193] | 1.2732 | -0.126 [-0.355, +0.077] | +16.4 [+9.2, +21.5] |
| LFPG (dev) | 2025-26 | 363 | 0.8854 [0.807, 0.973] | 1.2083 | +0.018 [-0.126, +0.164] | +26.7 [+19.4, +32.7] |
| KDSM (dev) | 2023-24 | 366 | 1.2007 [1.076, 1.288] | 2.0825 | +0.098 [-0.043, +0.308] | +42.3 [+33.4, +50.5] |
| KDSM (dev) | 2024-25 | 365 | 1.1638 [1.067, 1.257] | 1.5574 | -0.039 [-0.255, +0.153] | +25.3 [+16.7, +33.1] |
| KDSM (dev) | 2025-26 | 364 | 1.3079 [1.174, 1.465] | 1.5478 | -0.151 [-0.386, +0.099] | +15.5 [+7.2, +22.3] |
| YSDU (dev) | 2023-24 | 363 | 1.0082 [0.908, 1.126] | 1.0427 | +0.099 [-0.072, +0.277] | +3.3 [-4.4, +10.2] |
| YSDU (dev) | 2024-25 | 363 | 1.1230 [1.006, 1.270] | 1.1276 | +0.156 [-0.092, +0.417] | +0.4 [-10.5, +9.3] |
| YSDU (dev) | 2025-26 | 359 | 0.9484 [0.858, 1.052] | 1.0881 | +0.176 [+0.007, +0.324] | +12.8 [+4.8, +19.9] |
| KRNO (dev) | 2023-24 | 365 | 1.0130 [0.901, 1.147] | 1.7669 | +0.185 [+0.020, +0.338] | +42.7 [+35.7, +48.9] |
| KRNO (dev) | 2024-25 | 365 | 0.9792 [0.852, 1.124] | 1.5455 | +0.166 [-0.020, +0.341] | +36.6 [+29.7, +43.2] |
| KRNO (dev) | 2025-26 | 363 | 0.8503 [0.753, 0.968] | 1.3398 | +0.116 [-0.030, +0.264] | +36.5 [+29.3, +43.4] |
| KSFO (dev) (sea) | 2023-24 | 366 | 1.2018 [1.072, 1.339] | 1.8078 | +0.208 [-0.008, +0.459] | +33.5 [+26.6, +40.5] |
| KSFO (dev) (sea) | 2024-25 | 364 | 1.1741 [1.034, 1.318] | 1.6114 | +0.201 [-0.040, +0.467] | +27.1 [+20.9, +33.5] |
| KSFO (dev) (sea) | 2025-26 | 363 | 1.2470 [1.078, 1.432] | 1.5702 | +0.274 [-0.021, +0.546] | +20.6 [+13.7, +27.4] |

**(b) Every cycle** (`dailymax_every_cycle.csv`, `dailymax_whole_day_leads.csv`, `dailymax_by_cycle_hour.svg`).
*Changed after the first run, labelled (D106.2):* a run covers leads 3 to 48, 46 hours, and two whole local days
need at least 47, so no run holds a "day 2": every whole day is day 1 (day 2 counted: 0 at every airport). The
cycle hour fixes how far ahead that day lies (its first lead is shown in brackets), so it stands in for "day 1
or day 2" here and in (f) and (g). At YSDU, KRNO and KSFO one cycle hour has no whole day in standard time (its
first lead would be 25 or 26).

**Table B2. Daily maximum MAE from every cycle: the curve [95 %] / raw GFS, by cycle hour.** Read: the earlier
the day starts after the run, the smaller the error.

| airport | 00z | 06z | 12z | 18z | all |
|---|---|---|---|---|---|
| EDDM | 1.45 [1.32, 1.60] / 1.96 (from lead 22) | 1.37 [1.24, 1.52] / 1.92 (from lead 16) | 1.31 [1.18, 1.45] / 1.90 (from lead 10) | 1.25 [1.13, 1.39] / 1.79 (from lead 4) | 1.34 [1.22, 1.49] / 1.89 |
| KORD | 1.09 [1.02, 1.17] / 1.16 (from lead 5) | 1.30 [1.21, 1.40] / 1.41 (from lead 23) | 1.24 [1.16, 1.33] / 1.33 (from lead 17) | 1.16 [1.08, 1.25] / 1.25 (from lead 11) | 1.20 [1.12, 1.28] / 1.29 |
| CYYZ (sea) | 1.04 [0.96, 1.12] / 1.34 (from lead 4) | 1.21 [1.11, 1.31] / 1.48 (from lead 22) | 1.16 [1.07, 1.26] / 1.46 (from lead 16) | 1.11 [1.02, 1.21] / 1.43 (from lead 10) | 1.13 [1.05, 1.22] / 1.43 |
| ZGSZ (sea) | 0.99 [0.92, 1.05] / 1.64 (from lead 16) | 0.97 [0.90, 1.04] / 1.57 (from lead 10) | 0.91 [0.85, 0.97] / 1.52 (from lead 4) | 1.04 [0.97, 1.12] / 1.71 (from lead 22) | 0.98 [0.91, 1.04] / 1.61 |
| ZUCK | 1.25 [1.17, 1.33] / 1.46 (from lead 16) | 1.20 [1.12, 1.28] / 1.43 (from lead 10) | 1.17 [1.09, 1.25] / 1.37 (from lead 4) | 1.31 [1.21, 1.41] / 1.54 (from lead 22) | 1.23 [1.16, 1.31] / 1.45 |
| NZWN (sea) | 0.73 [0.68, 0.78] / 1.72 (from lead 11) | 0.74 [0.69, 0.79] / 1.70 (from lead 5) | 0.78 [0.73, 0.83] / 1.70 (from lead 23) | 0.78 [0.73, 0.83] / 1.71 (from lead 17) | 0.76 [0.71, 0.81] / 1.71 |
| EGLC (dev) | 0.97 [0.91, 1.03] / 1.08 (from lead 23) | 0.91 [0.85, 0.98] / 1.04 (from lead 17) | 0.88 [0.82, 0.94] / 1.01 (from lead 11) | 0.84 [0.79, 0.90] / 0.95 (from lead 5) | 0.90 [0.84, 0.96] / 1.02 |
| LFPG (dev) | 1.07 [1.00, 1.13] / 1.32 (from lead 22) | 1.08 [1.01, 1.15] / 1.30 (from lead 16) | 0.99 [0.92, 1.05] / 1.26 (from lead 10) | 0.96 [0.90, 1.02] / 1.20 (from lead 4) | 1.02 [0.96, 1.09] / 1.27 |
| KDSM (dev) | 1.22 [1.15, 1.29] / 1.73 (from lead 5) | 1.50 [1.40, 1.58] / 2.04 (from lead 23) | 1.41 [1.32, 1.50] / 1.95 (from lead 17) | 1.32 [1.24, 1.41] / 1.87 (from lead 11) | 1.36 [1.28, 1.44] / 1.90 |
| YSDU (dev) | 1.06 [0.99, 1.13] / 1.13 (from lead 13) | 1.03 [0.97, 1.10] / 1.09 (from lead 7) | 1.28 [1.18, 1.40] / 1.35 (from lead 25) | 1.12 [1.04, 1.20] / 1.18 (from lead 19) | 1.10 [1.03, 1.17] / 1.16 |
| KRNO (dev) | 0.95 [0.88, 1.02] / 1.55 (from lead 7) | 0.89 [0.82, 0.96] / 1.42 (from lead 25) | 1.01 [0.95, 1.08] / 1.60 (from lead 19) | 0.97 [0.90, 1.04] / 1.57 (from lead 13) | 0.96 [0.90, 1.02] / 1.55 |
| KSFO (dev) (sea) | 1.21 [1.12, 1.30] / 1.66 (from lead 7) | 1.35 [1.23, 1.48] / 1.83 (from lead 25) | 1.27 [1.18, 1.37] / 1.74 (from lead 19) | 1.24 [1.15, 1.34] / 1.71 (from lead 13) | 1.26 [1.17, 1.36] / 1.72 |

**(c) Extremes. Table B3. Mean error on the hottest and coldest 10 % of days** (`dailymax_extremes.csv`,
`dailymax_extremes.svg`). Each cell: the curve's mean error [95 %] / raw GFS's mean error (the curve's MAE), number
of days. Picked by the curve's forecast maximum (primary) and by the observed maximum (secondary).

| airport | hottest 10 % by forecast | coldest 10 % by forecast | hottest 10 % by observed | coldest 10 % by observed |
|---|---|---|---|---|
| EDDM | +0.42 [+0.17, +0.71] / +2.18 (0.85), 73 | +0.02 [-0.61, +0.60] / -0.88 (1.53), 73 | +0.59 [+0.35, +0.85] / +2.33 (0.93), 82 | -1.37 [-2.13, -0.62] / -2.38 (1.87), 73 |
| KORD | +0.20 [-0.28, +0.61] / -0.03 (1.18), 73 | +0.11 [-0.15, +0.40] / +0.26 (1.01), 73 | +0.77 [+0.45, +1.04] / +0.52 (1.09), 73 | -0.04 [-0.28, +0.18] / +0.16 (0.99), 78 |
| CYYZ (sea) | +0.05 [-0.27, +0.39] / +0.28 (1.02), 73 | -0.07 [-0.41, +0.27] / +0.77 (0.93), 73 | +0.60 [+0.30, +0.93] / +0.78 (1.14), 78 | -0.30 [-0.60, +0.02] / +0.58 (0.89), 79 |
| ZGSZ (sea) | +0.40 [+0.09, +0.71] / +1.47 (0.94), 73 | -0.00 [-0.42, +0.38] / +0.30 (1.20), 73 | +0.98 [+0.77, +1.19] / +1.94 (1.09), 96 | -0.65 [-0.97, -0.36] / -0.33 (1.16), 79 |
| ZUCK | -0.04 [-0.26, +0.18] / +0.72 (0.70), 73 | +0.19 [-0.15, +0.51] / -0.70 (1.03), 73 | +0.48 [+0.15, +0.75] / +1.20 (0.86), 93 | -0.45 [-0.72, -0.20] / -1.21 (1.02), 98 |
| NZWN (sea) | +0.13 [-0.16, +0.42] / +2.73 (0.90), 73 | +0.15 [-0.03, +0.32] / +0.83 (0.55), 73 | +0.96 [+0.76, +1.20] / +3.30 (1.11), 75 | -0.16 [-0.31, -0.00] / +0.56 (0.53), 74 |
| EGLC (dev) | +0.06 [-0.24, +0.37] / -0.65 (0.96), 110 | +0.06 [-0.12, +0.25] / +0.13 (0.62), 110 | +0.34 [+0.06, +0.64] / -0.33 (1.00), 115 | -0.23 [-0.42, -0.03] / -0.08 (0.68), 126 |
| LFPG (dev) | -0.17 [-0.47, +0.10] / -0.57 (1.02), 110 | -0.11 [-0.45, +0.23] / -0.55 (1.13), 110 | +0.22 [-0.06, +0.49] / -0.17 (0.88), 118 | -0.32 [-0.60, -0.02] / -0.64 (1.07), 137 |
| KDSM (dev) | -0.25 [-0.52, +0.17] / -0.76 (1.32), 110 | +0.15 [-0.18, +0.51] / -0.21 (1.16), 110 | +0.57 [+0.24, +0.92] / +0.07 (1.32), 125 | -0.15 [-0.43, +0.13] / -0.47 (1.03), 124 |
| YSDU (dev) | +0.23 [-0.05, +0.50] / -0.34 (0.92), 109 | +0.13 [-0.14, +0.41] / +0.54 (0.97), 109 | +0.82 [+0.60, +1.07] / +0.14 (1.08), 133 | -0.55 [-0.80, -0.35] / -0.05 (1.03), 157 |
| KRNO (dev) | +0.22 [+0.05, +0.38] / +0.94 (0.60), 110 | +0.15 [-0.23, +0.49] / +1.24 (1.24), 110 | +0.39 [+0.23, +0.55] / +1.11 (0.64), 121 | -0.77 [-1.17, -0.39] / +0.36 (1.35), 110 |
| KSFO (dev) (sea) | +0.68 [+0.08, +1.25] / +2.09 (1.97), 110 | +0.04 [-0.26, +0.29] / +0.33 (0.94), 110 | +1.97 [+1.69, +2.27] / +3.15 (2.07), 127 | -0.95 [-1.41, -0.52] / -0.58 (1.17), 113 |

**(d) Why it reads low. Table B4. Mean e_max = mean peak-level term - mean timing term** (`dailymax_decomposition.csv`,
`dailymax_decomposition.svg`). Read: the level term is how far the forecast at the observed peak hour falls below
the observed maximum; the timing term (never negative) is how much higher the forecast's own peak is than its value
at the observed peak hour. The sum check holds within 9e-16 everywhere. The low reading is consistent with a selection effect (the observed maximum is the highest of about 24 noisy readings, which a forecast of each hour cannot know), but the decomposition does not separate that from any damping of the forecast peak; raw GFS's larger low reading at some airports is a real bias.

| airport | raw GFS: e_max = level - timing | linear MOS | baseline | curve | curve: share of days with timing above 0 |
|---|---|---|---|---|---|
| EDDM | +0.66 = +1.27 - 0.60 | +0.16 = +0.87 - 0.72 | +0.03 = +0.81 - 0.79 | +0.13 = +0.91 - 0.78 | 78 % |
| KORD | +0.38 = +0.90 - 0.52 | +0.17 = +0.65 - 0.48 | -0.07 = +0.56 - 0.63 | +0.18 = +0.81 - 0.63 | 73 % |
| CYYZ (sea) | +0.77 = +1.44 - 0.67 | +0.39 = +0.98 - 0.59 | +0.12 = +0.89 - 0.77 | +0.12 = +0.87 - 0.75 | 79 % |
| ZGSZ (sea) | +1.24 = +1.78 - 0.54 | +0.61 = +1.12 - 0.51 | +0.34 = +1.00 - 0.65 | +0.25 = +0.92 - 0.67 | 84 % |
| ZUCK | +0.23 = +0.81 - 0.58 | +0.47 = +1.03 - 0.56 | +0.20 = +0.96 - 0.76 | +0.16 = +0.89 - 0.73 | 79 % |
| NZWN (sea) | +1.64 = +2.04 - 0.40 | +0.39 = +0.89 - 0.50 | +0.21 = +0.89 - 0.67 | +0.17 = +0.82 - 0.66 | 80 % |
| EGLC (dev) | +0.07 = +0.65 - 0.59 | +0.15 = +0.73 - 0.59 | -0.05 = +0.63 - 0.67 | +0.05 = +0.71 - 0.66 | 79 % |
| LFPG (dev) | +0.14 = +0.73 - 0.60 | +0.09 = +0.66 - 0.57 | -0.12 = +0.58 - 0.69 | +0.01 = +0.72 - 0.71 | 77 % |
| KDSM (dev) | +0.37 = +0.87 - 0.50 | +0.23 = +0.81 - 0.57 | -0.22 = +0.45 - 0.67 | -0.03 = +0.64 - 0.67 | 70 % |
| YSDU (dev) | +0.07 = +0.57 - 0.50 | +0.37 = +0.88 - 0.51 | +0.13 = +0.80 - 0.67 | +0.14 = +0.79 - 0.64 | 76 % |
| KRNO (dev) | +1.23 = +1.62 - 0.39 | -0.03 = +0.50 - 0.53 | -0.11 = +0.42 - 0.53 | +0.16 = +0.69 - 0.54 | 67 % |
| KSFO (dev) (sea) | +0.87 = +1.24 - 0.37 | +0.12 = +0.62 - 0.50 | -0.02 = +0.58 - 0.60 | +0.23 = +0.83 - 0.60 | 76 % |

**(e) Peak hour. Table B5. Forecast peak hour minus observed peak hour** (`dailymax_peak_hour.csv`,
`dailymax_peak_hour_hist.csv`, `dailymax_peak_hour.svg`). Ties go to the first hour. Read: positive means the
forecast peaks later; the curve's peak is later than raw GFS's at most airports.

| airport | raw GFS: mean (forecast - observed) h, mean abs h, within 1 h | curve |
|---|---|---|
| EDDM | +0.57, 2.01, 66 % | +1.49, 2.44, 53 % |
| KORD | +0.37, 1.85, 66 % | +0.76, 2.02, 60 % |
| CYYZ (sea) | +1.38, 2.42, 54 % | +1.58, 2.58, 49 % |
| ZGSZ (sea) | +1.95, 2.80, 37 % | +1.75, 2.52, 43 % |
| ZUCK | +0.31, 2.93, 53 % | +1.76, 2.88, 53 % |
| NZWN (sea) | +1.73, 2.91, 45 % | +1.81, 2.76, 47 % |
| EGLC (dev) | +1.19, 2.45, 59 % | +1.79, 2.66, 51 % |
| LFPG (dev) | +1.02, 2.26, 64 % | +1.52, 2.47, 53 % |
| KDSM (dev) | +0.48, 1.76, 72 % | +0.81, 1.90, 65 % |
| YSDU (dev) | +0.45, 1.26, 74 % | +0.76, 1.37, 66 % |
| KRNO (dev) | -0.03, 1.10, 82 % | +0.53, 1.18, 78 % |
| KSFO (dev) (sea) | -0.12, 1.43, 67 % | +0.67, 1.47, 66 % |

**(f) Edge-of-day days. Table B6. Scored days whose maximum falls in the first or last local hour**
(`dailymax_edge.csv`, `dailymax_edge_of_day.svg`; the same counts for every cycle and per cycle hour are in the
file). The two-by-two table for the curve is given as: both at an edge / curve only / observed only (the rest
neither; the raw GFS table is in the file). Errors are on days where any of the three is at an edge, against the
other days. This is D105.5(i)'s quantity on spent data.

| airport | days | observed max at an edge hour | curve | raw GFS | any of the three | curve edge and observed edge / curve only / observed only | curve MAE: edge days, other days | raw GFS MAE: edge days, other days | curve mean error on edge days |
|---|---|---|---|---|---|---|---|---|---|
| EDDM | 729 | 57 (8 %) | 25 (3 %) | 38 (5 %) | 81 (11 %) | 16 / 9 / 41 | 1.52, 1.21 | 2.14, 1.75 | -0.38 |
| KORD | 726 | 78 (11 %) | 58 (8 %) | 74 (10 %) | 103 (14 %) | 43 / 15 / 35 | 0.92, 1.12 | 1.04, 1.18 | +0.10 |
| CYYZ (sea) | 728 | 92 (13 %) | 77 (11 %) | 85 (12 %) | 138 (19 %) | 44 / 33 / 48 | 1.13, 1.02 | 1.25, 1.36 | -0.13 |
| ZGSZ (sea) | 729 | 50 (7 %) | 14 (2 %) | 40 (5 %) | 65 (9 %) | 12 / 2 / 38 | 1.18, 0.89 | 1.23, 1.55 | -0.45 |
| ZUCK | 729 | 102 (14 %) | 54 (7 %) | 136 (19 %) | 170 (23 %) | 34 / 20 / 68 | 1.23, 1.16 | 1.48, 1.34 | -0.15 |
| NZWN (sea) | 728 | 72 (10 %) | 36 (5 %) | 70 (10 %) | 108 (15 %) | 23 / 13 / 49 | 0.66, 0.75 | 0.99, 1.82 | -0.08 |
| EGLC (dev) | 1095 | 102 (9 %) | 51 (5 %) | 61 (6 %) | 142 (13 %) | 24 / 27 / 78 | 0.73, 0.86 | 0.77, 0.97 | -0.37 |
| LFPG (dev) | 1094 | 95 (9 %) | 65 (6 %) | 48 (4 %) | 137 (13 %) | 34 / 31 / 61 | 0.96, 0.96 | 1.24, 1.19 | -0.28 |
| KDSM (dev) | 1095 | 94 (9 %) | 78 (7 %) | 69 (6 %) | 129 (12 %) | 47 / 31 / 47 | 1.26, 1.22 | 1.44, 1.77 | -0.38 |
| YSDU (dev) | 1085 | 12 (1 %) | 5 (0 %) | 12 (1 %) | 21 (2 %) | 3 / 2 / 9 | 2.27, 1.00 | 2.17, 1.06 | -0.15 |
| KRNO (dev) | 1093 | 19 (2 %) | 12 (1 %) | 22 (2 %) | 33 (3 %) | 5 / 7 / 14 | 1.53, 0.93 | 1.48, 1.55 | -0.61 |
| KSFO (dev) (sea) | 1093 | 21 (2 %) | 11 (1 %) | 13 (1 %) | 34 (3 %) | 3 / 8 / 18 | 1.04, 1.21 | 1.41, 1.67 | +0.19 |

**(g) Ranges. Table B9. The curve's daily maximum error percentiles (5, 10, 25, median, 75, 90, 95), every
cycle, by season** (`dailymax_ranges.csv`, which also has raw GFS and each cycle hour; `dailymax_ranges_fan.svg`).

| airport | all seasons | Dec-Feb | Mar-May | Jun-Aug | Sep-Nov |
|---|---|---|---|---|---|
| EDDM | -3.4, -2.2, -0.7, **+0.3**, +1.2, +2.1, +2.7 | -4.1, -3.2, -1.4, **+0.1**, +1.1, +2.7, +3.4 | -1.6, -1.0, -0.2, **+0.5**, +1.3, +2.0, +2.4 | -1.9, -1.4, -0.6, **+0.2**, +1.0, +1.7, +2.0 | -4.9, -3.3, -1.0, **+0.3**, +1.3, +2.3, +2.9 |
| KORD | -2.4, -1.7, -0.7, **+0.2**, +1.1, +2.1, +2.7 | -2.0, -1.4, -0.5, **+0.5**, +1.5, +2.5, +3.2 | -3.0, -2.4, -0.8, **+0.3**, +1.4, +2.3, +2.9 | -2.2, -1.4, -0.7, **+0.2**, +1.0, +1.9, +2.5 | -2.1, -1.6, -0.9, **-0.1**, +0.6, +1.3, +1.6 |
| CYYZ (sea) | -2.4, -1.6, -0.7, **+0.1**, +1.0, +1.8, +2.5 | -2.0, -1.6, -0.8, **-0.0**, +0.9, +1.7, +2.2 | -3.2, -2.5, -1.0, **+0.1**, +1.2, +2.5, +3.1 | -2.4, -1.5, -0.6, **+0.3**, +1.0, +1.9, +2.4 | -1.5, -1.1, -0.5, **+0.2**, +1.0, +1.5, +2.0 |
| ZGSZ (sea) | -1.9, -1.3, -0.5, **+0.3**, +1.0, +1.7, +2.2 | -1.9, -1.3, -0.6, **+0.4**, +1.2, +1.9, +2.3 | -2.1, -1.3, -0.4, **+0.3**, +1.0, +1.6, +2.0 | -1.7, -1.2, -0.3, **+0.4**, +1.1, +1.8, +2.3 | -2.1, -1.5, -0.5, **+0.1**, +0.8, +1.5, +1.9 |
| ZUCK | -2.6, -1.8, -0.7, **+0.2**, +1.1, +2.1, +2.8 | -2.2, -1.7, -0.9, **+0.1**, +1.1, +2.3, +2.7 | -2.8, -1.9, -0.7, **+0.3**, +1.3, +2.4, +3.0 | -2.5, -1.6, -0.6, **+0.3**, +1.2, +2.1, +2.9 | -3.0, -1.8, -0.8, **+0.1**, +0.9, +1.6, +2.2 |
| NZWN (sea) | -1.4, -1.0, -0.4, **+0.2**, +0.8, +1.4, +1.8 | -1.7, -1.3, -0.6, **+0.1**, +0.9, +1.6, +2.1 | -1.5, -1.0, -0.3, **+0.2**, +0.7, +1.3, +1.6 | -1.1, -0.7, -0.2, **+0.2**, +0.7, +1.2, +1.6 | -1.3, -1.0, -0.4, **+0.2**, +0.8, +1.4, +1.7 |
| EGLC (dev) | -2.0, -1.4, -0.6, **+0.1**, +0.8, +1.4, +1.8 | -1.6, -1.2, -0.6, **-0.0**, +0.5, +1.1, +1.4 | -2.3, -1.5, -0.5, **+0.3**, +1.1, +1.7, +2.2 | -2.2, -1.5, -0.6, **+0.2**, +0.9, +1.5, +1.9 | -2.1, -1.5, -0.6, **+0.1**, +0.7, +1.2, +1.5 |
| LFPG (dev) | -2.3, -1.6, -0.7, **+0.1**, +0.9, +1.6, +2.0 | -2.4, -1.7, -0.8, **+0.0**, +0.7, +1.5, +1.9 | -2.0, -1.5, -0.6, **+0.3**, +1.0, +1.7, +2.1 | -2.4, -1.6, -0.7, **+0.1**, +0.8, +1.6, +1.9 | -2.6, -1.8, -0.6, **+0.2**, +0.9, +1.5, +2.0 |
| KDSM (dev) | -3.1, -2.3, -1.0, **+0.0**, +1.0, +2.0, +2.7 | -3.4, -2.5, -1.1, **+0.1**, +1.1, +2.3, +3.1 | -3.4, -2.4, -1.0, **+0.1**, +1.1, +2.3, +3.1 | -2.8, -2.2, -1.1, **-0.1**, +0.9, +1.7, +2.2 | -2.8, -2.0, -0.9, **-0.0**, +1.0, +1.9, +2.4 |
| YSDU (dev) | -2.2, -1.5, -0.6, **+0.2**, +1.0, +1.9, +2.4 | -1.7, -1.2, -0.3, **+0.6**, +1.5, +2.2, +2.9 | -2.6, -1.7, -0.8, **+0.0**, +0.7, +1.7, +2.4 | -2.4, -1.6, -0.9, **-0.1**, +0.6, +1.2, +1.5 | -2.2, -1.3, -0.5, **+0.3**, +1.1, +1.8, +2.3 |
| KRNO (dev) | -2.0, -1.3, -0.5, **+0.2**, +0.9, +1.6, +2.1 | -2.6, -1.7, -0.6, **+0.4**, +1.4, +2.3, +3.0 | -1.6, -1.1, -0.5, **+0.2**, +0.9, +1.4, +1.7 | -1.5, -1.0, -0.4, **+0.2**, +0.8, +1.3, +1.7 | -2.7, -1.5, -0.6, **+0.2**, +0.8, +1.5, +1.9 |
| KSFO (dev) (sea) | -2.4, -1.6, -0.8, **+0.2**, +1.2, +2.3, +3.0 | -2.4, -1.6, -0.8, **+0.1**, +1.1, +2.1, +2.6 | -1.7, -1.3, -0.6, **+0.2**, +1.2, +2.4, +3.2 | -3.1, -2.2, -1.1, **-0.1**, +1.0, +2.3, +3.2 | -2.3, -1.3, -0.5, **+0.4**, +1.3, +2.3, +3.0 |

**Table B10. The curve's hourly error percentiles by lead band** (`hourly_ranges.csv` has every single lead 3 to
48, all seasons and per season, for the curve and raw GFS, each with its n; `hourly_ranges_fan.svg`).

| airport | 3-12 | 13-24 | 25-36 | 37-48 |
|---|---|---|---|---|
| EDDM | -2.8, -2.0, -0.9, **+0.1**, +1.0, +1.9, +2.6 | -2.9, -2.1, -0.9, **+0.1**, +1.1, +2.0, +2.7 | -3.1, -2.2, -1.0, **+0.1**, +1.1, +2.1, +2.8 | -3.2, -2.3, -1.0, **+0.1**, +1.2, +2.2, +2.9 |
| KORD | -2.1, -1.5, -0.7, **-0.0**, +0.7, +1.5, +2.0 | -2.4, -1.7, -0.9, **-0.0**, +0.9, +1.7, +2.3 | -2.7, -1.9, -1.0, **-0.0**, +1.0, +1.9, +2.6 | -3.0, -2.1, -1.1, **+0.0**, +1.0, +2.1, +2.8 |
| CYYZ (sea) | -2.1, -1.5, -0.8, **+0.0**, +0.8, +1.6, +2.1 | -2.3, -1.7, -0.8, **+0.0**, +0.9, +1.7, +2.3 | -2.5, -1.8, -0.9, **+0.0**, +0.9, +1.8, +2.5 | -2.7, -2.0, -0.9, **+0.0**, +1.0, +1.9, +2.6 |
| ZGSZ (sea) | -1.8, -1.3, -0.5, **+0.1**, +0.6, +1.2, +1.6 | -2.0, -1.4, -0.6, **+0.1**, +0.7, +1.3, +1.8 | -2.2, -1.5, -0.6, **+0.1**, +0.7, +1.5, +1.9 | -2.3, -1.6, -0.7, **+0.1**, +0.8, +1.5, +2.1 |
| ZUCK | -2.1, -1.5, -0.7, **+0.0**, +0.8, +1.5, +2.1 | -2.3, -1.6, -0.8, **+0.0**, +0.8, +1.6, +2.2 | -2.4, -1.7, -0.8, **+0.1**, +0.9, +1.7, +2.3 | -2.5, -1.8, -0.8, **+0.1**, +0.9, +1.8, +2.5 |
| NZWN (sea) | -1.5, -1.1, -0.5, **+0.0**, +0.6, +1.1, +1.6 | -1.6, -1.2, -0.6, **+0.0**, +0.6, +1.2, +1.7 | -1.7, -1.3, -0.6, **+0.0**, +0.6, +1.3, +1.7 | -1.8, -1.3, -0.7, **+0.0**, +0.7, +1.3, +1.8 |
| EGLC (dev) | -1.6, -1.2, -0.6, **+0.0**, +0.6, +1.1, +1.5 | -1.8, -1.3, -0.6, **+0.0**, +0.7, +1.3, +1.6 | -1.9, -1.4, -0.7, **+0.1**, +0.7, +1.4, +1.8 | -2.0, -1.5, -0.7, **+0.1**, +0.8, +1.4, +1.9 |
| LFPG (dev) | -1.9, -1.3, -0.6, **+0.0**, +0.7, +1.3, +1.7 | -2.0, -1.4, -0.7, **+0.0**, +0.7, +1.4, +1.9 | -2.2, -1.6, -0.7, **+0.0**, +0.8, +1.5, +2.0 | -2.4, -1.7, -0.8, **+0.0**, +0.8, +1.6, +2.1 |
| KDSM (dev) | -2.5, -1.8, -0.8, **+0.0**, +0.9, +1.7, +2.2 | -2.8, -2.0, -0.9, **+0.1**, +1.0, +1.8, +2.4 | -3.0, -2.2, -1.0, **+0.0**, +1.1, +2.1, +2.7 | -3.2, -2.3, -1.1, **+0.1**, +1.2, +2.2, +2.9 |
| YSDU (dev) | -2.5, -1.8, -0.9, **+0.0**, +0.9, +1.8, +2.4 | -2.6, -1.9, -0.9, **+0.0**, +0.9, +1.8, +2.5 | -2.7, -2.0, -0.9, **+0.0**, +1.0, +1.9, +2.6 | -2.8, -2.1, -1.0, **+0.0**, +1.0, +2.0, +2.7 |
| KRNO (dev) | -2.5, -1.8, -0.8, **-0.0**, +0.8, +1.7, +2.4 | -2.6, -1.9, -0.9, **-0.0**, +0.8, +1.8, +2.5 | -2.7, -2.0, -0.9, **-0.0**, +0.9, +1.9, +2.7 | -2.9, -2.0, -1.0, **-0.0**, +0.9, +2.0, +2.8 |
| KSFO (dev) (sea) | -2.0, -1.5, -0.8, **-0.1**, +0.6, +1.4, +1.9 | -2.2, -1.6, -0.8, **-0.1**, +0.7, +1.5, +2.0 | -2.3, -1.7, -0.9, **-0.1**, +0.7, +1.5, +2.2 | -2.3, -1.7, -0.9, **-0.1**, +0.7, +1.6, +2.3 |

### D106.8: curve shape and consistency

**Table C1** (`shape_diurnal_range.csv`, `smoothness.csv`, `run_to_run_hourly.csv`, `run_to_run_dailymax.csv`,
`shape_range_smoothness.svg`, `run_to_run_hourly.svg`). Diurnal range on scored days (correlation with the
observed range in brackets); smoothness as the mean |second difference| over consecutive leads within a cycle on
hours where raw GFS, the curve and the observation all exist; run-to-run as the mean |change| between a cycle and
the one 6 hours earlier for the same valid time (lead 24 shown; every lead in the file) and for the same day's
maximum (all cycle hours pooled). Peak hour is in Table B5.

| airport | observed mean diurnal range | raw GFS range (corr.) | curve range (corr.) | smoothness raw / curve / observed | run-to-run, lead 24: raw / curve | daily max run-to-run: raw / curve |
|---|---|---|---|---|---|---|
| EDDM | 10.1 | 8.0 (0.84) | 9.8 (0.87) | 0.42 / 0.85 / 0.99 | 0.34 / 0.54 | 0.34 / 0.43 |
| KORD | 9.0 | 8.1 (0.83) | 8.6 (0.87) | 0.37 / 0.68 / 0.69 | 0.42 / 0.52 | 0.47 / 0.54 |
| CYYZ (sea) | 8.3 | 7.9 (0.77) | 8.0 (0.83) | 0.40 / 0.68 / 0.87 | 0.36 / 0.46 | 0.41 / 0.46 |
| ZGSZ (sea) | 5.2 | 3.3 (0.60) | 4.7 (0.69) | 0.15 / 0.50 / 0.76 | 0.27 / 0.38 | 0.33 / 0.43 |
| ZUCK | 6.7 | 5.8 (0.85) | 6.5 (0.87) | 0.25 / 0.64 / 0.78 | 0.40 / 0.48 | 0.52 / 0.56 |
| NZWN (sea) | 5.1 | 3.3 (0.74) | 4.9 (0.81) | 0.22 / 0.54 / 0.74 | 0.18 / 0.32 | 0.16 / 0.28 |
| EGLC (dev) | 6.4 | 6.5 (0.85) | 6.3 (0.88) | 0.37 / 0.58 / 0.70 | 0.34 / 0.39 | 0.37 / 0.38 |
| LFPG (dev) | 7.7 | 7.9 (0.88) | 7.6 (0.91) | 0.42 / 0.62 / 0.75 | 0.37 / 0.44 | 0.39 / 0.43 |
| KDSM (dev) | 10.4 | 10.5 (0.73) | 10.2 (0.86) | 0.52 / 0.80 / 0.78 | 0.50 / 0.60 | 0.51 / 0.59 |
| YSDU (dev) | 14.3 | 12.9 (0.83) | 13.9 (0.89) | 0.66 / 0.99 / 1.27 | 0.46 / 0.55 | 0.46 / 0.48 |
| KRNO (dev) | 14.2 | 10.5 (0.76) | 14.0 (0.89) | 0.46 / 0.97 / 0.98 | 0.29 / 0.54 | 0.27 / 0.36 |
| KSFO (dev) (sea) | 7.4 | 6.1 (0.67) | 7.0 (0.81) | 0.31 / 0.64 / 0.78 | 0.20 / 0.35 | 0.21 / 0.37 |

### D106.9: drift

**Table C2. The curve's MAE / the baseline's MAE by days since the tracker started** (`hourly_breakdowns.csv`,
condition days_since_start; `drift_by_days_since_start.svg`; b over time in `b_over_time.svg` and
`b_summary.csv`). Read with care: each band is also a season (0 to 30 days is always August), so the bands mix
drift with season. Development trackers restart each 1 August (D97.7), so they have no "over 365" band.

| airport | 0-30 | 31-90 | 91-180 | 181-365 | over 365 |
|---|---|---|---|---|---|
| EDDM | 1.16 / 1.16 | 1.37 / 1.41 | 1.53 / 1.50 | 1.21 / 1.21 | 1.35 / 1.35 |
| KORD | 1.08 / 1.08 | 0.80 / 0.81 | 1.15 / 1.15 | 1.27 / 1.27 | 1.22 / 1.26 |
| CYYZ (sea) | 1.03 / 1.02 | 0.95 / 0.97 | 1.04 / 1.04 | 1.29 / 1.29 | 1.12 / 1.12 |
| ZGSZ (sea) | 0.88 / 0.88 | 0.85 / 0.84 | 0.92 / 0.95 | 0.95 / 0.97 | 0.88 / 0.89 |
| ZUCK | 1.14 / 1.15 | 1.30 / 1.32 | 0.89 / 0.87 | 1.19 / 1.22 | 1.05 / 1.04 |
| NZWN (sea) | 0.74 / 0.74 | 0.72 / 0.72 | 0.75 / 0.75 | 0.84 / 0.83 | 0.78 / 0.78 |
| EGLC (dev) | 0.79 / 0.80 | 0.81 / 0.81 | 0.80 / 0.79 | 0.88 / 0.88 | - / - |
| LFPG (dev) | 0.99 / 1.01 | 0.89 / 0.90 | 0.96 / 0.95 | 0.97 / 0.98 | - / - |
| KDSM (dev) | 1.13 / 1.15 | 1.17 / 1.17 | 1.33 / 1.34 | 1.36 / 1.40 | - / - |
| YSDU (dev) | 1.20 / 1.22 | 1.24 / 1.29 | 1.30 / 1.31 | 1.20 / 1.24 | - / - |
| KRNO (dev) | 1.14 / 1.16 | 1.19 / 1.21 | 1.55 / 1.55 | 1.06 / 1.09 | - / - |
| KSFO (dev) (sea) | 1.18 / 1.28 | 1.10 / 1.26 | 1.08 / 1.14 | 0.91 / 0.97 | - / - |

**Table C3. b per airport and test year.**

| airport | period | mean b | mean abs b | 95th pct abs b |
|---|---|---|---|---|
| EDDM | A | +0.04 | 0.24 | 0.73 |
| EDDM | B | -0.03 | 0.24 | 0.60 |
| KORD | A | -0.10 | 0.18 | 0.43 |
| KORD | B | -0.36 | 0.38 | 0.81 |
| CYYZ (sea) | A | -0.00 | 0.17 | 0.43 |
| CYYZ (sea) | B | +0.05 | 0.20 | 0.51 |
| ZGSZ (sea) | A | +0.16 | 0.19 | 0.52 |
| ZGSZ (sea) | B | +0.11 | 0.15 | 0.35 |
| ZUCK | A | +0.03 | 0.21 | 0.66 |
| ZUCK | B | +0.08 | 0.17 | 0.41 |
| NZWN (sea) | A | +0.04 | 0.10 | 0.24 |
| NZWN (sea) | B | +0.06 | 0.10 | 0.27 |
| EGLC (dev) | 2023-24 | +0.00 | 0.12 | 0.32 |
| EGLC (dev) | 2024-25 | -0.10 | 0.15 | 0.38 |
| EGLC (dev) | 2025-26 | -0.11 | 0.14 | 0.37 |
| LFPG (dev) | 2023-24 | +0.04 | 0.12 | 0.30 |
| LFPG (dev) | 2024-25 | -0.14 | 0.21 | 0.61 |
| LFPG (dev) | 2025-26 | -0.14 | 0.18 | 0.49 |
| KDSM (dev) | 2023-24 | +0.16 | 0.30 | 0.71 |
| KDSM (dev) | 2024-25 | -0.11 | 0.27 | 0.61 |
| KDSM (dev) | 2025-26 | -0.16 | 0.35 | 1.00 |
| YSDU (dev) | 2023-24 | +0.19 | 0.36 | 0.92 |
| YSDU (dev) | 2024-25 | -0.04 | 0.29 | 0.72 |
| YSDU (dev) | 2025-26 | +0.20 | 0.32 | 0.78 |
| KRNO (dev) | 2023-24 | +0.16 | 0.28 | 0.72 |
| KRNO (dev) | 2024-25 | -0.09 | 0.28 | 0.69 |
| KRNO (dev) | 2025-26 | -0.28 | 0.30 | 0.68 |
| KSFO (dev) (sea) | 2023-24 | +0.19 | 0.34 | 0.94 |
| KSFO (dev) (sea) | 2024-25 | -0.45 | 0.49 | 1.21 |
| KSFO (dev) (sea) | 2025-26 | -0.38 | 0.39 | 1.06 |

### D106.10: model internals

**Table C4. Share of mean |contribution| per feature, percent, averaged over leads 6, 12, 18, 24, 36 and 48 (all cycle hours and test years)** (`contrib_shares.csv` has each lead; `contrib_shares.svg`, `contrib_vs_temperature.svg`, `contrib_vs_cloud.svg`). LightGBM's own feature contributions (`pred_contrib=True`) on the scored test rows of 576 refits, each of which reproduces the stored baseline exactly (0 differences); contributions sum to the prediction within 2.5e-14. Read for physical sense only.

| airport | temperature | season (sin) | season (cos) | cloud cover | 10 m wind | dewpoint depression | lapse rate | radiation | pressure tendency |
|---|---|---|---|---|---|---|---|---|---|
| EDDM | 9 | 5 | 16 | 5 | 15 | 14 | 16 | 15 | 5 |
| KORD | 17 | 12 | 13 | 6 | 16 | 17 | 6 | 7 | 5 |
| CYYZ (sea) | 11 | 15 | 19 | 5 | 8 | 13 | 10 | 10 | 8 |
| ZGSZ (sea) | 33 | 8 | 8 | 6 | 9 | 17 | 7 | 6 | 6 |
| ZUCK | 10 | 7 | 36 | 6 | 6 | 12 | 15 | 4 | 5 |
| NZWN (sea) | 16 | 7 | 17 | 7 | 17 | 9 | 8 | 10 | 9 |
| EGLC (dev) | 8 | 13 | 15 | 6 | 12 | 18 | 6 | 13 | 9 |
| LFPG (dev) | 6 | 19 | 19 | 5 | 9 | 11 | 10 | 15 | 5 |
| KDSM (dev) | 16 | 15 | 25 | 5 | 7 | 13 | 8 | 7 | 4 |
| YSDU (dev) | 8 | 12 | 7 | 7 | 21 | 24 | 11 | 4 | 6 |
| KRNO (dev) | 6 | 7 | 28 | 5 | 19 | 16 | 7 | 5 | 6 |
| KSFO (dev) (sea) | 10 | 8 | 30 | 5 | 11 | 13 | 16 | 3 | 5 |

Read: the seasonal terms carry the most at most airports (a bias that changes through the year); dewpoint depression (how dry the air is) and wind come next; cloud cover is 5 to 7 % everywhere and moves the correction by at most about 0.3 degrees C either way (`contrib_vs_cloud.svg`). The temperature term is largest at ZGSZ (33 %), where it pulls cold forecasts colder and warm ones warmer: raw GFS's range there is too narrow (slope 1.10, Table A5), and the model widens it (`contrib_vs_temperature.svg`).

### D106.11: limits

**Table C5** (`limits.csv`). Against whole-degree reports, even a perfect forecast of the true temperature would show an MAE of about 0.25 degrees C. That is a floor. Rounding adds much less than 0.25 to a forecast whose other errors are larger, so it is not a share of the MAE. The sea-grid
airports are marked (sea) in every table; as a group (CYYZ, ZGSZ, NZWN, KSFO) their mean hourly curve MAE is
0.96 against 1.14 for the other eight, and their mean hourly skill against raw GFS +24.9 %
against +25.1 %.

| airport | sea in grid box | share of whole-degree observations | curve MAE | raw GFS MAE |
|---|---|---|---|---|
| EDDM | no | 100 % | 1.329 | 1.794 |
| KORD | no | 12 % | 1.185 | 1.337 |
| CYYZ (sea) | yes | 100 % | 1.137 | 1.472 |
| ZGSZ (sea) | yes | 100 % | 0.900 | 1.159 |
| ZUCK | no | 100 % | 1.089 | 1.461 |
| NZWN (sea) | yes | 100 % | 0.785 | 1.161 |
| EGLC (dev) | no | 100 % | 0.839 | 1.042 |
| LFPG (dev) | no | 100 % | 0.954 | 1.234 |
| KDSM (dev) | no | 11 % | 1.300 | 1.879 |
| YSDU (dev) | no | 100 % | 1.230 | 1.523 |
| KRNO (dev) | no | 11 % | 1.208 | 2.219 |
| KSFO (dev) (sea) | yes | 11 % | 1.004 | 1.292 |

### D106.12: formal tests

**Table D1. Diebold-Mariano tests** (`dm_tests.csv`, `dm_tests.svg`). Per airport, test years pooled, on the
daily mean of |e_curve| - |e_other| (negative: the curve's errors are smaller), Newey-West variance at 7 lags,
two-sided normal p-value; Benjamini-Hochberg at 0.05 across the 12 airports within each family. Outcome: family
1 (against raw GFS, hourly) 12 of 12 rejected; family 2 (against raw GFS, daily maximum) 12 of 12; family 3
(against linear MOS, hourly) 11 of 12 (not EGLC); family 4 (against the baseline, hourly) 4 of 12 (KDSM, YSDU,
KRNO, KSFO, all development airports). Everything else in this file is descriptive.

| family | airport | days | mean daily difference [95 %] | DM statistic | p-value | BH at 0.05 |
|---|---|---|---|---|---|---|
| 1: curve against raw GFS, hourly | EDDM | 730 | -0.466 [-0.550, -0.384] | -10.68 | 1.3e-26 | rejected |
| 1: curve against raw GFS, hourly | KORD | 730 | -0.152 [-0.179, -0.123] | -10.54 | 5.7e-26 | rejected |
| 1: curve against raw GFS, hourly | CYYZ (sea) | 730 | -0.335 [-0.402, -0.264] | -9.08 | 1.1e-19 | rejected |
| 1: curve against raw GFS, hourly | ZGSZ (sea) | 730 | -0.259 [-0.301, -0.219] | -12.16 | 5.0e-34 | rejected |
| 1: curve against raw GFS, hourly | ZUCK | 730 | -0.373 [-0.445, -0.301] | -9.91 | 3.6e-23 | rejected |
| 1: curve against raw GFS, hourly | NZWN (sea) | 730 | -0.376 [-0.420, -0.329] | -16.06 | 5.0e-58 | rejected |
| 1: curve against raw GFS, hourly | EGLC (dev) | 1096 | -0.204 [-0.231, -0.176] | -13.62 | 3.0e-42 | rejected |
| 1: curve against raw GFS, hourly | LFPG (dev) | 1096 | -0.280 [-0.326, -0.232] | -11.16 | 6.3e-29 | rejected |
| 1: curve against raw GFS, hourly | KDSM (dev) | 1096 | -0.579 [-0.666, -0.493] | -12.41 | 2.3e-35 | rejected |
| 1: curve against raw GFS, hourly | YSDU (dev) | 1096 | -0.292 [-0.328, -0.258] | -16.11 | 2.1e-58 | rejected |
| 1: curve against raw GFS, hourly | KRNO (dev) | 1096 | -1.011 [-1.129, -0.905] | -17.22 | 1.7e-66 | rejected |
| 1: curve against raw GFS, hourly | KSFO (dev) (sea) | 1096 | -0.288 [-0.339, -0.240] | -11.07 | 1.8e-28 | rejected |
| 2: curve against raw GFS, daily maximum | EDDM | 729 | -0.542 [-0.645, -0.427] | -9.32 | 1.1e-20 | rejected |
| 2: curve against raw GFS, daily maximum | KORD | 726 | -0.070 [-0.126, -0.013] | -2.35 | 1.9e-02 | rejected |
| 2: curve against raw GFS, daily maximum | CYYZ (sea) | 728 | -0.298 [-0.395, -0.204] | -5.94 | 2.8e-09 | rejected |
| 2: curve against raw GFS, daily maximum | ZGSZ (sea) | 729 | -0.608 [-0.686, -0.532] | -15.38 | 2.1e-53 | rejected |
| 2: curve against raw GFS, daily maximum | ZUCK | 729 | -0.199 [-0.269, -0.129] | -5.46 | 4.7e-08 | rejected |
| 2: curve against raw GFS, daily maximum | NZWN (sea) | 728 | -0.960 [-1.065, -0.863] | -18.41 | 1.2e-75 | rejected |
| 2: curve against raw GFS, daily maximum | EGLC (dev) | 1095 | -0.105 [-0.141, -0.065] | -5.22 | 1.8e-07 | rejected |
| 2: curve against raw GFS, daily maximum | LFPG (dev) | 1094 | -0.241 [-0.293, -0.186] | -8.61 | 7.3e-18 | rejected |
| 2: curve against raw GFS, daily maximum | KDSM (dev) | 1095 | -0.506 [-0.630, -0.382] | -7.76 | 8.7e-15 | rejected |
| 2: curve against raw GFS, daily maximum | YSDU (dev) | 1085 | -0.059 [-0.114, -0.003] | -2.06 | 3.9e-02 | rejected |
| 2: curve against raw GFS, daily maximum | KRNO (dev) | 1093 | -0.603 [-0.691, -0.521] | -13.52 | 1.2e-41 | rejected |
| 2: curve against raw GFS, daily maximum | KSFO (dev) (sea) | 1093 | -0.456 [-0.541, -0.378] | -10.51 | 7.9e-26 | rejected |
| 3: curve against linear MOS, hourly | EDDM | 730 | -0.104 [-0.144, -0.066] | -5.14 | 2.8e-07 | rejected |
| 3: curve against linear MOS, hourly | KORD | 730 | -0.032 [-0.055, -0.010] | -2.80 | 5.1e-03 | rejected |
| 3: curve against linear MOS, hourly | CYYZ (sea) | 730 | -0.062 [-0.084, -0.042] | -5.59 | 2.2e-08 | rejected |
| 3: curve against linear MOS, hourly | ZGSZ (sea) | 730 | -0.044 [-0.064, -0.025] | -4.38 | 1.2e-05 | rejected |
| 3: curve against linear MOS, hourly | ZUCK | 730 | -0.082 [-0.115, -0.048] | -4.73 | 2.3e-06 | rejected |
| 3: curve against linear MOS, hourly | NZWN (sea) | 730 | -0.046 [-0.056, -0.033] | -7.37 | 1.7e-13 | rejected |
| 3: curve against linear MOS, hourly | EGLC (dev) | 1096 | -0.008 [-0.018, +0.001] | -1.74 | 8.2e-02 | not rejected |
| 3: curve against linear MOS, hourly | LFPG (dev) | 1096 | -0.043 [-0.058, -0.026] | -4.99 | 6.1e-07 | rejected |
| 3: curve against linear MOS, hourly | KDSM (dev) | 1096 | -0.127 [-0.156, -0.093] | -7.85 | 4.3e-15 | rejected |
| 3: curve against linear MOS, hourly | YSDU (dev) | 1096 | -0.091 [-0.116, -0.068] | -7.24 | 4.4e-13 | rejected |
| 3: curve against linear MOS, hourly | KRNO (dev) | 1096 | -0.204 [-0.252, -0.162] | -8.47 | 2.4e-17 | rejected |
| 3: curve against linear MOS, hourly | KSFO (dev) (sea) | 1096 | -0.136 [-0.173, -0.101] | -7.03 | 2.0e-12 | rejected |
| 4: curve against baseline, hourly | EDDM | 730 | -0.002 [-0.022, +0.017] | -0.21 | 8.3e-01 | not rejected |
| 4: curve against baseline, hourly | KORD | 730 | -0.018 [-0.033, -0.003] | -2.30 | 2.1e-02 | not rejected |
| 4: curve against baseline, hourly | CYYZ (sea) | 730 | +0.003 [-0.006, +0.011] | +0.57 | 5.7e-01 | not rejected |
| 4: curve against baseline, hourly | ZGSZ (sea) | 730 | -0.012 [-0.022, -0.002] | -2.18 | 2.9e-02 | not rejected |
| 4: curve against baseline, hourly | ZUCK | 730 | -0.004 [-0.017, +0.009] | -0.57 | 5.7e-01 | not rejected |
| 4: curve against baseline, hourly | NZWN (sea) | 730 | +0.002 [-0.001, +0.006] | +1.24 | 2.2e-01 | not rejected |
| 4: curve against baseline, hourly | EGLC (dev) | 1096 | +0.001 [-0.004, +0.007] | +0.37 | 7.1e-01 | not rejected |
| 4: curve against baseline, hourly | LFPG (dev) | 1096 | -0.005 [-0.013, +0.002] | -1.36 | 1.8e-01 | not rejected |
| 4: curve against baseline, hourly | KDSM (dev) | 1096 | -0.023 [-0.037, -0.008] | -2.99 | 2.8e-03 | rejected |
| 4: curve against baseline, hourly | YSDU (dev) | 1096 | -0.033 [-0.046, -0.020] | -4.78 | 1.7e-06 | rejected |
| 4: curve against baseline, hourly | KRNO (dev) | 1096 | -0.021 [-0.031, -0.010] | -3.71 | 2.1e-04 | rejected |
| 4: curve against baseline, hourly | KSFO (dev) (sea) | 1096 | -0.081 [-0.112, -0.052] | -4.95 | 7.3e-07 | rejected |

BH column corrected at session 114's review; session 112 had printed 'not rejected' on every row.

### D106.13: the ZUCK case

`figures/analysis/zuck_case_2026101306.svg`. MLwx-live's logged cycle 2026-10-13 06z at ZUCK, forecast columns
only (file SHA-256 `348feb226d8da93f048a32fad6f140a12fa26881a82a1b7668579bf5017fddeb`, 121,529 bytes). No
observation, error or `obs/` file valid on or after 2026-08-01 was read (D105.6). The run holds one whole local day
(2026-10-14, Asia/Chongqing, leads 10 to 33). Raw GFS's maximum, 22.9 degrees C, is at 00:00 local, the first hour:
it is the warmth left over from the previous afternoon, not that day's peak. The curve's maximum, 22.3, is at
14:00. Beside it: ZUCK's spent-data figures from (f): the observed maximum is at an edge hour on 14 % of scored days
(102 of 729), raw GFS's on 19 % (136), the curve's on 7 % (54). On ZUCK's edge days the curve's MAE was 1.23 against
1.16 on other days; raw GFS's 1.48 against 1.34. The whole-airport view is `dailymax_edge_of_day.svg`.

### D107.9 and D108: comparisons (session 114)

Descriptive only (D107.2). Rules fixed before any score in D107.9 and D108. Positions: raw GFS's own (the positions file's `gfs` set at the development airports, IEM's at the claim airports). AIFS adjusted for height as GFS is (7.429 degrees C per km, its own terrain with the same four weights); the NBM grid has no terrain field (no elevation treatment); NBS and MAV as issued. Pairs by valid time; NBS 01/07/13/19 UTC runs pair with the cycle one hour earlier (one hour more data), and where both run sets exist the same cycle's run is used. Truth: our hourly-report maximum (D82.8). Intervals: 7-day block bootstrap, seed 114 (10,000 resamples headline, 2,000 cells). Formal tests: Diebold-Mariano, one family per competitor and output, Benjamini-Hochberg at 0.05 across its airports. ECMWF IFS: pending (D108.2), not pulled yet. Script `scripts/session114_comparisons.py`; tables `data/processed/session114_comparisons/`; full log `notes/session-114-output.txt`. Latency (not adjusted for, D108.4(f)): AIFS: archive write time minus cycle, median 5.14 to 5.27 h over the cycle hours (range 5.07 to 30.93); may be later than public release. GFS: archive write time minus cycle, median 3.74 to 3.81 h over the cycle hours (range 3.67 to 7.46); may be later than public release. Not adjusted for (D108.4(f)); NBM grid archive write time minus cycle, median 0.81 to 1.07 h over the cycle hours (range 0.62 to 44.77); may be later than public release; NBS and MAV: documented time only.

**Table E1. Paired rows and days per source, airport and test year** (`match_counts.csv`, which also has every unpaired row and day by reason, cycle hour, version and run set).

| source | airport | test year | paired hourly rows | paired D98.10 days | paired every-cycle days |
|---|---|---|---|---|---|
| AIFS | EDDM | 2024-25 | 5,016 | 157 | 627 |
| AIFS | EDDM | 2025-26 | 11,644 | 364 | 1,456 |
| AIFS | KORD | 2024-25 | 5,016 | 156 | 627 |
| AIFS | KORD | 2025-26 | 11,604 | 361 | 1,441 |
| AIFS | CYYZ (sea) | 2024-25 | 5,016 | 156 | 627 |
| AIFS | CYYZ (sea) | 2025-26 | 11,644 | 364 | 1,453 |
| AIFS | ZGSZ (sea) | 2024-25 | 5,016 | 157 | 627 |
| AIFS | ZGSZ (sea) | 2025-26 | 11,644 | 364 | 1,455 |
| AIFS | ZUCK | 2024-25 | 5,016 | 157 | 627 |
| AIFS | ZUCK | 2025-26 | 11,644 | 364 | 1,455 |
| AIFS | NZWN (sea) | 2024-25 | 5,016 | 157 | 627 |
| AIFS | NZWN (sea) | 2025-26 | 11,628 | 363 | 1,450 |
| AIFS | EGLC (dev) | 2024-25 | 5,016 | 157 | 627 |
| AIFS | EGLC (dev) | 2025-26 | 11,628 | 364 | 1,456 |
| AIFS | LFPG (dev) | 2024-25 | 5,000 | 157 | 627 |
| AIFS | LFPG (dev) | 2025-26 | 11,572 | 363 | 1,452 |
| AIFS | KDSM (dev) | 2024-25 | 5,016 | 156 | 627 |
| AIFS | KDSM (dev) | 2025-26 | 11,644 | 364 | 1,453 |
| AIFS | YSDU (dev) | 2024-25 | 5,000 | 156 | 504 |
| AIFS | YSDU (dev) | 2025-26 | 11,492 | 359 | 1,255 |
| AIFS | KRNO (dev) | 2024-25 | 5,016 | 156 | 616 |
| AIFS | KRNO (dev) | 2025-26 | 11,636 | 363 | 1,323 |
| AIFS | KSFO (dev) (sea) | 2024-25 | 5,016 | 155 | 612 |
| AIFS | KSFO (dev) (sea) | 2025-26 | 11,636 | 363 | 1,323 |
| NBM grid | KORD | 2024-25 | 55,463 | 365 | 1,460 |
| NBM grid | KORD | 2025-26 | 57,919 | 361 | 1,441 |
| NBM grid | CYYZ (sea) | 2024-25 | 55,409 | 364 | 1,456 |
| NBM grid | CYYZ (sea) | 2025-26 | 58,104 | 364 | 1,453 |
| NBM grid | KDSM (dev) | 2023-24 | 55,615 | 366 | 1,464 |
| NBM grid | KDSM (dev) | 2024-25 | 55,475 | 365 | 1,460 |
| NBM grid | KDSM (dev) | 2025-26 | 58,104 | 364 | 1,453 |
| NBM grid | KRNO (dev) | 2023-24 | 55,602 | 365 | 1,334 |
| NBM grid | KRNO (dev) | 2024-25 | 55,461 | 365 | 1,334 |
| NBM grid | KRNO (dev) | 2025-26 | 58,044 | 363 | 1,323 |
| NBM grid | KSFO (dev) (sea) | 2023-24 | 55,614 | 366 | 1,338 |
| NBM grid | KSFO (dev) (sea) | 2024-25 | 55,433 | 364 | 1,330 |
| NBM grid | KSFO (dev) (sea) | 2025-26 | 58,048 | 363 | 1,323 |
| NBS | KORD | 2024-25 | 21,870 | 365 | 1,458 |
| NBS | KORD | 2025-26 | 21,739 | 361 | 1,440 |
| NBS | CYYZ (sea) | 2024-25 | 21,840 | 364 | 1,454 |
| NBS | CYYZ (sea) | 2025-26 | 21,784 | 364 | 1,450 |
| NBS | KDSM (dev) | 2023-24 | 21,937 | 366 | 1,463 |
| NBS | KDSM (dev) | 2024-25 | 21,870 | 365 | 1,458 |
| NBS | KDSM (dev) | 2025-26 | 21,784 | 364 | 1,450 |
| NBS | KRNO (dev) | 2023-24 | 21,915 | 365 | 1,332 |
| NBS | KRNO (dev) | 2024-25 | 21,863 | 365 | 1,332 |
| NBS | KRNO (dev) | 2025-26 | 21,799 | 363 | 1,323 |
| NBS | KSFO (dev) (sea) | 2023-24 | 21,930 | 366 | 1,336 |
| NBS | KSFO (dev) (sea) | 2024-25 | 21,863 | 364 | 1,328 |
| NBS | KSFO (dev) (sea) | 2025-26 | 21,791 | 363 | 1,322 |
| MAV | KORD | 2024-25 | 21,855 | 364 | 1,457 |
| MAV | KORD | 2025-26 | 21,739 | 360 | 1,440 |
| MAV | KDSM (dev) | 2023-24 | 21,952 | 366 | 1,464 |
| MAV | KDSM (dev) | 2024-25 | 21,855 | 364 | 1,457 |
| MAV | KDSM (dev) | 2025-26 | 21,814 | 363 | 1,452 |
| MAV | KRNO (dev) | 2023-24 | 21,945 | 365 | 1,334 |
| MAV | KRNO (dev) | 2024-25 | 21,848 | 364 | 1,331 |
| MAV | KRNO (dev) | 2025-26 | 21,799 | 362 | 1,322 |
| MAV | KSFO (dev) (sea) | 2023-24 | 21,960 | 366 | 1,338 |
| MAV | KSFO (dev) (sea) | 2024-25 | 21,848 | 363 | 1,327 |
| MAV | KSFO (dev) (sea) | 2025-26 | 21,806 | 362 | 1,322 |

Unpaired, all airports together: AIFS daily max, D98.10 days, cycle before the source's first run: 4,697; AIFS daily max, D98.10 days, observed maximum not usable (D82.8): 14; AIFS daily max, every cycle, cycle before the source's first run: 18,057; AIFS daily max, every cycle, day ends after 2026-07-31T23:00 UTC (nothing after it is read): 67; AIFS daily max, every cycle, observed maximum not usable (D82.8): 54; AIFS hourly, competitor value our row not scored (no observation or incomplete features): 344; AIFS hourly, cycle before the source's first run: 862,657; AIFS hourly, no run at this cycle: 36; AIFS hourly, valid time not one of the source's steps: 948,595; NBM grid daily max, D98.10 days, observed maximum not usable (D82.8): 8; NBM grid daily max, every cycle, day ends after 2026-07-31T23:00 UTC (nothing after it is read): 35; NBM grid daily max, every cycle, observed maximum not usable (D82.8): 32; NBM grid hourly, competitor value our row not scored (no observation or incomplete features): 586; NBM grid hourly, step missing from the run: 19; NBM grid hourly, valid time not one of the source's steps: 137,740; NBS daily max, D98.10 days, observed maximum not usable (D82.8): 8; NBS daily max, every cycle, day ends after 2026-07-31T23:00 UTC (nothing after it is read): 35; NBS daily max, every cycle, no run at this cycle: 23; NBS daily max, every cycle, observed maximum not usable (D82.8): 32; NBS hourly, competitor value our row not scored (no observation or incomplete features): 200; NBS hourly, no run at this cycle: 1,165; NBS hourly, valid time not one of the source's steps: 586,900; MAV daily max, D98.10 days, no run at this cycle: 8; MAV daily max, D98.10 days, observed maximum not usable (D82.8): 7; MAV daily max, every cycle, day ends after 2026-07-31T23:00 UTC (nothing after it is read): 28; MAV daily max, every cycle, no run at this cycle: 16; MAV daily max, every cycle, observed maximum not usable (D82.8): 28; MAV hourly, competitor value our row not scored (no observation or incomplete features): 163; MAV hourly, no run at this cycle: 741; MAV hourly, valid time not one of the source's steps: 496,845.

**Table E2. Hourly: MAE [95 %] on each source's paired rows, per test year and pooled** (`hourly_<source>.csv`, `hourly_<source>_skill.csv`; breakdowns by lead band, cycle hour, season, version and NBS run set in `hourly_<source>_breakdown.csv`). Skill = 1 - MAE(a) / MAE(b), percent.

| source | airport | test year | n | competitor | curve | raw GFS | linear MOS | skill curve vs it [95 %] | skill raw GFS vs it |
|---|---|---|---|---|---|---|---|---|---|
| AIFS | EDDM | 2024-25 | 5,016 | 1.27 [1.14, 1.42] | 1.12 [1.03, 1.20] | 1.85 | 1.26 | +12.0 [+1.4, +22.5] | -44.9 |
| AIFS | EDDM | 2025-26 | 11,644 | 1.19 [1.11, 1.27] | 1.35 [1.28, 1.44] | 1.92 | 1.48 | -13.7 [-22.5, -6.6] | -61.3 |
| AIFS | EDDM | all | 16,660 | 1.21 [1.14, 1.28] | 1.28 [1.22, 1.35] | 1.90 | 1.42 | -5.5 [-13.2, +1.0] | -56.1 |
| AIFS | KORD | 2024-25 | 5,016 | 1.20 [1.10, 1.32] | 1.33 [1.22, 1.48] | 1.58 | 1.39 | -11.3 [-18.2, -4.1] | -32.3 |
| AIFS | KORD | 2025-26 | 11,604 | 1.08 [1.02, 1.16] | 1.23 [1.15, 1.32] | 1.35 | 1.27 | -13.6 [-22.7, -4.6] | -24.3 |
| AIFS | KORD | all | 16,620 | 1.12 [1.06, 1.18] | 1.26 [1.19, 1.33] | 1.42 | 1.31 | -12.8 [-19.1, -6.3] | -26.9 |
| AIFS | CYYZ (sea) | 2024-25 | 5,016 | 1.19 [1.08, 1.31] | 1.29 [1.17, 1.40] | 1.78 | 1.35 | -7.8 [-17.5, +1.1] | -49.1 |
| AIFS | CYYZ (sea) | 2025-26 | 11,644 | 1.17 [1.09, 1.25] | 1.14 [1.06, 1.23] | 1.51 | 1.20 | +2.4 [-5.5, +9.9] | -29.2 |
| AIFS | CYYZ (sea) | all | 16,660 | 1.17 [1.11, 1.24] | 1.18 [1.11, 1.25] | 1.59 | 1.25 | -0.7 [-6.5, +5.5] | -35.3 |
| AIFS | ZGSZ (sea) | 2024-25 | 5,016 | 1.03 [0.97, 1.11] | 0.96 [0.86, 1.05] | 1.28 | 1.05 | +7.2 [-3.4, +18.4] | -24.0 |
| AIFS | ZGSZ (sea) | 2025-26 | 11,644 | 0.93 [0.87, 0.99] | 0.86 [0.81, 0.91] | 1.17 | 0.91 | +6.8 [-0.8, +14.4] | -25.9 |
| AIFS | ZGSZ (sea) | all | 16,660 | 0.96 [0.92, 1.01] | 0.89 [0.84, 0.94] | 1.20 | 0.95 | +6.9 [+0.9, +13.3] | -25.3 |
| AIFS | ZUCK | 2024-25 | 5,016 | 1.16 [1.06, 1.26] | 1.24 [1.15, 1.36] | 1.59 | 1.34 | -7.2 [-20.6, +2.7] | -37.3 |
| AIFS | ZUCK | 2025-26 | 11,644 | 1.02 [0.98, 1.06] | 1.04 [0.97, 1.09] | 1.47 | 1.15 | -1.7 [-6.8, +4.0] | -43.8 |
| AIFS | ZUCK | all | 16,660 | 1.06 [1.02, 1.11] | 1.10 [1.04, 1.15] | 1.50 | 1.21 | -3.5 [-8.5, +2.1] | -41.6 |
| AIFS | NZWN (sea) | 2024-25 | 5,016 | 1.02 [0.94, 1.10] | 0.84 [0.78, 0.89] | 1.09 | 0.88 | +17.9 [+10.6, +24.5] | -6.5 |
| AIFS | NZWN (sea) | 2025-26 | 11,628 | 1.07 [1.02, 1.14] | 0.77 [0.73, 0.81] | 1.16 | 0.81 | +28.1 [+23.1, +33.7] | -8.2 |
| AIFS | NZWN (sea) | all | 16,644 | 1.06 [1.01, 1.10] | 0.79 [0.76, 0.83] | 1.14 | 0.83 | +25.1 [+20.4, +29.4] | -7.7 |
| AIFS | EGLC (dev) | 2024-25 | 5,016 | 1.19 [1.09, 1.29] | 0.95 [0.89, 1.02] | 1.21 | 0.95 | +20.3 [+12.2, +26.6] | -1.8 |
| AIFS | EGLC (dev) | 2025-26 | 11,628 | 1.10 [1.02, 1.18] | 0.84 [0.79, 0.90] | 1.03 | 0.85 | +23.6 [+17.4, +28.7] | +6.5 |
| AIFS | EGLC (dev) | all | 16,644 | 1.13 [1.06, 1.19] | 0.87 [0.84, 0.92] | 1.09 | 0.88 | +22.5 [+17.5, +26.5] | +3.8 |
| AIFS | LFPG (dev) | 2024-25 | 5,000 | 1.15 [1.05, 1.27] | 1.00 [0.94, 1.06] | 1.42 | 1.04 | +13.2 [+4.4, +21.1] | -23.4 |
| AIFS | LFPG (dev) | 2025-26 | 11,572 | 1.09 [1.01, 1.16] | 0.93 [0.89, 0.99] | 1.23 | 1.00 | +14.1 [+6.3, +20.5] | -13.5 |
| AIFS | LFPG (dev) | all | 16,572 | 1.11 [1.05, 1.17] | 0.95 [0.92, 1.00] | 1.29 | 1.01 | +13.8 [+8.0, +19.0] | -16.6 |
| AIFS | KDSM (dev) | 2024-25 | 5,016 | 1.07 [1.01, 1.14] | 1.32 [1.25, 1.40] | 1.91 | 1.41 | -22.8 [-31.3, -15.8] | -78.2 |
| AIFS | KDSM (dev) | 2025-26 | 11,644 | 1.09 [1.03, 1.15] | 1.36 [1.28, 1.46] | 1.84 | 1.43 | -24.9 [-35.5, -16.1] | -69.5 |
| AIFS | KDSM (dev) | all | 16,660 | 1.08 [1.04, 1.14] | 1.35 [1.28, 1.42] | 1.86 | 1.43 | -24.3 [-31.7, -17.6] | -72.1 |
| AIFS | YSDU (dev) | 2024-25 | 5,000 | 1.04 [0.96, 1.12] | 1.18 [1.11, 1.28] | 1.58 | 1.34 | -13.9 [-23.6, -6.8] | -52.3 |
| AIFS | YSDU (dev) | 2025-26 | 11,492 | 1.16 [1.09, 1.22] | 1.19 [1.12, 1.26] | 1.45 | 1.29 | -3.1 [-7.8, +1.3] | -25.5 |
| AIFS | YSDU (dev) | all | 16,492 | 1.12 [1.07, 1.17] | 1.19 [1.14, 1.25] | 1.49 | 1.31 | -6.1 [-10.6, -2.3] | -33.0 |
| AIFS | KRNO (dev) | 2024-25 | 5,016 | 1.31 [1.23, 1.36] | 0.97 [0.88, 1.06] | 1.68 | 1.12 | +26.1 [+17.3, +32.7] | -27.7 |
| AIFS | KRNO (dev) | 2025-26 | 11,636 | 1.73 [1.57, 1.91] | 1.15 [1.07, 1.27] | 2.27 | 1.40 | +33.1 [+25.2, +39.9] | -31.6 |
| AIFS | KRNO (dev) | all | 16,652 | 1.60 [1.48, 1.73] | 1.10 [1.03, 1.18] | 2.09 | 1.32 | +31.4 [+25.0, +37.0] | -30.7 |
| AIFS | KSFO (dev) (sea) | 2024-25 | 5,016 | 0.89 [0.78, 0.98] | 0.86 [0.79, 0.93] | 1.08 | 1.06 | +3.4 [-11.6, +14.3] | -21.0 |
| AIFS | KSFO (dev) (sea) | 2025-26 | 11,636 | 0.97 [0.90, 1.04] | 1.01 [0.93, 1.10] | 1.39 | 1.12 | -4.2 [-10.8, +1.8] | -44.4 |
| AIFS | KSFO (dev) (sea) | all | 16,652 | 0.94 [0.88, 1.01] | 0.96 [0.90, 1.03] | 1.30 | 1.10 | -2.0 [-8.1, +3.8] | -37.7 |
| NBM grid | KORD | 2024-25 | 55,463 | 1.00 [0.92, 1.08] | 1.11 [1.04, 1.19] | 1.31 | 1.15 | -11.7 [-15.7, -8.2] | -31.4 |
| NBM grid | KORD | 2025-26 | 57,919 | 1.09 [1.01, 1.19] | 1.20 [1.12, 1.28] | 1.31 | 1.24 | -9.7 [-14.2, -5.0] | -20.1 |
| NBM grid | KORD | all | 113,382 | 1.05 [0.98, 1.11] | 1.16 [1.10, 1.21] | 1.31 | 1.19 | -10.6 [-13.6, -7.6] | -25.4 |
| NBM grid | CYYZ (sea) | 2024-25 | 55,409 | 1.03 [0.96, 1.10] | 1.13 [1.07, 1.21] | 1.46 | 1.19 | -10.4 [-13.7, -7.0] | -42.4 |
| NBM grid | CYYZ (sea) | 2025-26 | 58,104 | 1.06 [0.98, 1.16] | 1.10 [1.03, 1.19] | 1.47 | 1.17 | -3.5 [-8.7, +1.4] | -38.3 |
| NBM grid | CYYZ (sea) | all | 113,513 | 1.05 [0.99, 1.10] | 1.12 [1.07, 1.17] | 1.47 | 1.18 | -6.8 [-9.9, -3.5] | -40.3 |
| NBM grid | KDSM (dev) | 2023-24 | 55,615 | 1.22 [1.15, 1.28] | 1.30 [1.23, 1.35] | 2.01 | 1.48 | -6.3 [-11.8, -0.6] | -64.3 |
| NBM grid | KDSM (dev) | 2024-25 | 55,475 | 1.15 [1.10, 1.20] | 1.20 [1.15, 1.25] | 1.75 | 1.33 | -4.4 [-8.6, +0.0] | -51.5 |
| NBM grid | KDSM (dev) | 2025-26 | 58,104 | 1.25 [1.17, 1.32] | 1.31 [1.24, 1.40] | 1.82 | 1.39 | -4.7 [-10.6, -0.3] | -45.7 |
| NBM grid | KDSM (dev) | all | 169,194 | 1.21 [1.17, 1.25] | 1.27 [1.23, 1.31] | 1.86 | 1.40 | -5.1 [-8.1, -2.2] | -53.7 |
| NBM grid | KRNO (dev) | 2023-24 | 55,602 | 1.51 [1.44, 1.59] | 1.23 [1.14, 1.32] | 2.03 | 1.36 | +18.7 [+13.7, +23.0] | -34.5 |
| NBM grid | KRNO (dev) | 2024-25 | 55,461 | 1.44 [1.36, 1.52] | 1.21 [1.11, 1.33] | 2.33 | 1.44 | +15.5 [+10.3, +20.6] | -62.3 |
| NBM grid | KRNO (dev) | 2025-26 | 58,044 | 1.39 [1.31, 1.48] | 1.13 [1.05, 1.23] | 2.23 | 1.38 | +18.9 [+14.5, +22.6] | -60.7 |
| NBM grid | KRNO (dev) | all | 169,107 | 1.44 [1.40, 1.49] | 1.19 [1.13, 1.25] | 2.20 | 1.39 | +17.7 [+15.0, +20.3] | -52.2 |
| NBM grid | KSFO (dev) (sea) | 2023-24 | 55,614 | 1.47 [1.38, 1.57] | 0.99 [0.93, 1.04] | 1.28 | 1.12 | +33.0 [+28.6, +37.3] | +13.1 |
| NBM grid | KSFO (dev) (sea) | 2024-25 | 55,433 | 1.43 [1.27, 1.60] | 1.02 [0.92, 1.11] | 1.24 | 1.18 | +29.0 [+24.6, +33.1] | +13.4 |
| NBM grid | KSFO (dev) (sea) | 2025-26 | 58,048 | 1.31 [1.24, 1.39] | 0.97 [0.90, 1.05] | 1.31 | 1.09 | +26.2 [+21.5, +30.3] | -0.0 |
| NBM grid | KSFO (dev) (sea) | all | 169,095 | 1.40 [1.34, 1.48] | 0.99 [0.95, 1.04] | 1.28 | 1.13 | +29.5 [+26.8, +32.0] | +9.0 |
| NBS | KORD | 2024-25 | 21,870 | 1.02 [0.94, 1.12] | 1.17 [1.10, 1.26] | 1.37 | 1.19 | -14.9 [-19.2, -11.1] | -34.2 |
| NBS | KORD | 2025-26 | 21,739 | 1.10 [1.01, 1.20] | 1.24 [1.16, 1.33] | 1.34 | 1.27 | -12.8 [-17.6, -7.9] | -22.3 |
| NBS | KORD | all | 43,609 | 1.06 [1.00, 1.13] | 1.21 [1.15, 1.27] | 1.36 | 1.23 | -13.8 [-17.0, -10.6] | -28.0 |
| NBS | CYYZ (sea) | 2024-25 | 21,840 | 1.07 [1.00, 1.14] | 1.18 [1.10, 1.25] | 1.50 | 1.23 | -10.5 [-13.8, -6.8] | -40.8 |
| NBS | CYYZ (sea) | 2025-26 | 21,784 | 1.08 [1.00, 1.17] | 1.13 [1.06, 1.22] | 1.48 | 1.20 | -5.0 [-10.3, +0.0] | -37.0 |
| NBS | CYYZ (sea) | all | 43,624 | 1.07 [1.02, 1.13] | 1.15 [1.10, 1.21] | 1.49 | 1.21 | -7.7 [-10.8, -4.5] | -38.9 |
| NBS | KDSM (dev) | 2023-24 | 21,937 | 1.17 [1.09, 1.23] | 1.36 [1.28, 1.42] | 2.06 | 1.54 | -16.3 [-22.5, -10.8] | -77.0 |
| NBS | KDSM (dev) | 2024-25 | 21,870 | 1.12 [1.06, 1.19] | 1.25 [1.19, 1.30] | 1.80 | 1.38 | -11.8 [-16.2, -6.9] | -60.6 |
| NBS | KDSM (dev) | 2025-26 | 21,784 | 1.21 [1.13, 1.29] | 1.36 [1.28, 1.46] | 1.84 | 1.44 | -12.6 [-19.2, -7.2] | -52.7 |
| NBS | KDSM (dev) | all | 65,591 | 1.16 [1.12, 1.21] | 1.32 [1.28, 1.37] | 1.90 | 1.45 | -13.6 [-16.9, -10.4] | -63.4 |
| NBS | KRNO (dev) | 2023-24 | 21,915 | 1.13 [1.05, 1.23] | 1.26 [1.18, 1.36] | 2.05 | 1.39 | -11.8 [-17.1, -6.3] | -81.0 |
| NBS | KRNO (dev) | 2024-25 | 21,863 | 1.17 [1.07, 1.27] | 1.25 [1.14, 1.36] | 2.36 | 1.47 | -6.4 [-11.6, -1.0] | -102.1 |
| NBS | KRNO (dev) | 2025-26 | 21,799 | 1.20 [1.12, 1.29] | 1.16 [1.08, 1.27] | 2.29 | 1.41 | +2.9 [-2.9, +8.0] | -90.8 |
| NBS | KRNO (dev) | all | 65,577 | 1.17 [1.11, 1.22] | 1.22 [1.17, 1.28] | 2.23 | 1.42 | -5.0 [-8.1, -1.8] | -91.4 |
| NBS | KSFO (dev) (sea) | 2023-24 | 21,930 | 0.88 [0.82, 0.94] | 1.00 [0.94, 1.06] | 1.29 | 1.13 | -13.7 [-18.2, -8.3] | -47.7 |
| NBS | KSFO (dev) (sea) | 2024-25 | 21,863 | 0.91 [0.83, 1.00] | 1.04 [0.94, 1.14] | 1.26 | 1.19 | -14.3 [-20.0, -8.4] | -37.6 |
| NBS | KSFO (dev) (sea) | 2025-26 | 21,791 | 0.97 [0.89, 1.05] | 1.00 [0.92, 1.09] | 1.35 | 1.12 | -3.3 [-8.2, +1.6] | -40.0 |
| NBS | KSFO (dev) (sea) | all | 65,584 | 0.92 [0.88, 0.96] | 1.01 [0.97, 1.06] | 1.30 | 1.15 | -10.3 [-13.7, -7.2] | -41.7 |
| MAV | KORD | 2024-25 | 21,855 | 1.32 [1.25, 1.41] | 1.17 [1.10, 1.26] | 1.37 | 1.19 | +11.4 [+7.4, +15.6] | -3.6 |
| MAV | KORD | 2025-26 | 21,739 | 1.40 [1.31, 1.49] | 1.24 [1.16, 1.33] | 1.34 | 1.27 | +11.3 [+7.8, +14.8] | +3.8 |
| MAV | KORD | all | 43,594 | 1.36 [1.30, 1.42] | 1.21 [1.15, 1.27] | 1.36 | 1.23 | +11.4 [+8.7, +14.0] | +0.2 |
| MAV | KDSM (dev) | 2023-24 | 21,952 | 1.53 [1.43, 1.61] | 1.36 [1.28, 1.42] | 2.07 | 1.54 | +11.3 [+5.6, +16.5] | -35.0 |
| MAV | KDSM (dev) | 2024-25 | 21,855 | 1.39 [1.31, 1.47] | 1.25 [1.19, 1.30] | 1.80 | 1.38 | +9.5 [+5.8, +14.1] | -30.0 |
| MAV | KDSM (dev) | 2025-26 | 21,814 | 1.43 [1.34, 1.53] | 1.36 [1.28, 1.46] | 1.84 | 1.44 | +4.7 [+0.3, +8.4] | -29.2 |
| MAV | KDSM (dev) | all | 65,621 | 1.45 [1.39, 1.50] | 1.32 [1.28, 1.37] | 1.90 | 1.45 | +8.6 [+5.7, +11.2] | -31.5 |
| MAV | KRNO (dev) | 2023-24 | 21,945 | 1.16 [1.09, 1.24] | 1.26 [1.18, 1.36] | 2.05 | 1.39 | -8.9 [-14.1, -4.0] | -76.3 |
| MAV | KRNO (dev) | 2024-25 | 21,848 | 1.19 [1.09, 1.29] | 1.25 [1.14, 1.36] | 2.36 | 1.47 | -4.9 [-10.7, -0.0] | -98.8 |
| MAV | KRNO (dev) | 2025-26 | 21,799 | 1.12 [1.05, 1.22] | 1.17 [1.08, 1.27] | 2.29 | 1.41 | -3.8 [-9.0, +1.4] | -103.9 |
| MAV | KRNO (dev) | all | 65,592 | 1.16 [1.11, 1.21] | 1.23 [1.17, 1.29] | 2.23 | 1.42 | -5.9 [-9.0, -2.9] | -92.9 |
| MAV | KSFO (dev) (sea) | 2023-24 | 21,960 | 1.09 [1.02, 1.17] | 1.00 [0.94, 1.06] | 1.29 | 1.13 | +8.7 [+3.6, +13.9] | -18.6 |
| MAV | KSFO (dev) (sea) | 2024-25 | 21,848 | 1.04 [0.98, 1.11] | 1.04 [0.94, 1.14] | 1.25 | 1.19 | +0.2 [-6.0, +7.0] | -20.1 |
| MAV | KSFO (dev) (sea) | 2025-26 | 21,806 | 1.06 [0.98, 1.16] | 1.00 [0.92, 1.09] | 1.35 | 1.12 | +5.8 [+1.6, +9.9] | -27.7 |
| MAV | KSFO (dev) (sea) | all | 65,614 | 1.06 [1.02, 1.11] | 1.01 [0.97, 1.06] | 1.30 | 1.15 | +5.0 [+1.6, +8.1] | -22.1 |

**Table E2b. Hourly skill of the curve against the competitor by lead band, percent [95 %]** (`hourly_<source>_breakdown.csv`; `comparison_lead_band.svg`).

| source | airport | 3-12 | 13-24 | 25-36 | 37-48 |
|---|---|---|---|---|---|
| AIFS | EDDM | -4.8 [-12.3, +1.5] | -4.4 [-11.8, +2.0] | -7.0 [-15.5, +0.0] | -5.9 [-14.1, +1.0] |
| AIFS | KORD | -2.9 [-9.8, +3.7] | -9.7 [-16.6, -2.5] | -17.2 [-23.8, -9.6] | -19.9 [-27.1, -13.2] |
| AIFS | CYYZ (sea) | +9.3 [+2.8, +15.6] | +0.9 [-5.3, +7.4] | -4.8 [-11.4, +1.7] | -7.7 [-14.5, -1.1] |
| AIFS | ZGSZ (sea) | +14.5 [+9.1, +20.3] | +8.7 [+2.5, +14.9] | +4.4 [-2.7, +11.1] | +0.7 [-6.8, +8.1] |
| AIFS | ZUCK | -1.7 [-7.1, +4.1] | -1.8 [-7.4, +3.9] | -3.6 [-8.6, +2.0] | -6.5 [-12.6, -0.2] |
| AIFS | NZWN (sea) | +30.5 [+25.6, +34.9] | +26.5 [+21.7, +30.9] | +23.9 [+18.7, +28.4] | +19.7 [+14.4, +24.1] |
| AIFS | EGLC (dev) | +28.3 [+23.7, +32.2] | +24.4 [+18.9, +28.5] | +19.7 [+13.9, +24.3] | +18.3 [+12.6, +23.0] |
| AIFS | LFPG (dev) | +19.6 [+13.6, +25.2] | +15.2 [+8.8, +21.1] | +11.6 [+5.4, +17.3] | +9.4 [+3.3, +15.1] |
| AIFS | KDSM (dev) | -18.0 [-24.6, -11.5] | -22.5 [-29.9, -15.0] | -26.7 [-35.7, -18.5] | -28.8 [-37.0, -21.4] |
| AIFS | YSDU (dev) | -2.3 [-8.1, +2.3] | -6.1 [-11.3, -1.5] | -6.6 [-11.5, -1.8] | -9.4 [-14.3, -4.8] |
| AIFS | KRNO (dev) | +34.0 [+27.9, +39.4] | +32.1 [+25.8, +37.6] | +31.0 [+24.6, +36.5] | +28.7 [+21.8, +34.6] |
| AIFS | KSFO (dev) (sea) | +3.9 [-1.3, +9.0] | -0.1 [-6.6, +5.9] | -3.9 [-10.7, +2.6] | -7.6 [-14.7, -0.9] |
| NBM grid | KORD | -7.8 [-11.1, -4.4] | -12.2 [-15.4, -9.0] | -11.1 [-14.6, -7.5] | -10.7 [-15.0, -6.5] |
| NBM grid | CYYZ (sea) | -6.3 [-9.4, -3.0] | -6.4 [-9.6, -2.9] | -8.2 [-11.5, -4.7] | -5.4 [-9.9, -1.5] |
| NBM grid | KDSM (dev) | -5.5 [-8.7, -2.6] | -5.3 [-8.3, -2.2] | -5.0 [-8.3, -1.5] | -4.6 [-8.5, -1.0] |
| NBM grid | KRNO (dev) | +19.3 [+16.4, +22.1] | +18.7 [+15.9, +21.5] | +16.7 [+13.7, +19.7] | +14.4 [+11.2, +17.4] |
| NBM grid | KSFO (dev) (sea) | +33.9 [+31.4, +36.3] | +29.8 [+27.0, +32.4] | +27.1 [+24.0, +29.8] | +25.6 [+22.3, +28.6] |
| NBS | KORD | -13.7 [-17.7, -9.9] | -14.8 [-18.4, -11.5] | -13.9 [-17.7, -9.9] | -12.8 [-16.8, -9.2] |
| NBS | CYYZ (sea) | -7.6 [-11.0, -4.1] | -6.8 [-10.2, -3.1] | -8.4 [-11.9, -4.7] | -8.0 [-11.1, -4.7] |
| NBS | KDSM (dev) | -17.0 [-20.9, -13.5] | -13.6 [-17.1, -10.3] | -13.1 [-16.8, -9.6] | -12.1 [-15.5, -8.6] |
| NBS | KRNO (dev) | -5.9 [-9.2, -2.3] | -4.3 [-7.6, -0.8] | -4.2 [-7.5, -0.7] | -5.7 [-9.2, -1.9] |
| NBS | KSFO (dev) (sea) | -8.8 [-12.7, -5.2] | -10.4 [-14.4, -7.1] | -10.7 [-14.3, -7.5] | -10.6 [-14.1, -7.5] |
| MAV | KORD | +15.5 [+12.6, +18.7] | +13.9 [+10.8, +17.1] | +10.5 [+7.5, +13.6] | +7.4 [+4.5, +10.3] |
| MAV | KDSM (dev) | +12.5 [+8.9, +15.6] | +9.0 [+5.9, +11.6] | +7.9 [+4.7, +10.7] | +6.5 [+3.6, +9.0] |
| MAV | KRNO (dev) | -10.6 [-14.0, -7.4] | -4.1 [-7.9, -0.9] | -5.0 [-8.7, -1.8] | -5.4 [-8.8, -2.1] |
| MAV | KSFO (dev) (sea) | -5.0 [-9.4, -1.1] | +5.8 [+2.1, +9.2] | +5.1 [+1.3, +8.5] | +9.6 [+6.0, +13.1] |

**Table E3. Formal tests, hourly** (`hourly_<source>_dm.csv`). Daily mean of |e_curve| - |e_competitor| (negative: the curve's errors are smaller), Newey-West at 7 lags.

| family | airport | days | mean daily difference [95 %] | DM statistic | p-value | BH at 0.05 |
|---|---|---|---|---|---|---|
| aifs hourly | EDDM | 522 | +0.066 [-0.013, +0.154] | +1.52 | 1.3e-01 | not rejected |
| aifs hourly | KORD | 522 | +0.144 [+0.072, +0.211] | +3.98 | 6.9e-05 | rejected |
| aifs hourly | CYYZ (sea) | 522 | +0.007 [-0.066, +0.075] | +0.19 | 8.5e-01 | not rejected |
| aifs hourly | ZGSZ (sea) | 522 | -0.066 [-0.132, -0.008] | -2.06 | 4.0e-02 | not rejected |
| aifs hourly | ZUCK | 522 | +0.039 [-0.022, +0.090] | +1.36 | 1.7e-01 | not rejected |
| aifs hourly | NZWN (sea) | 522 | -0.265 [-0.320, -0.207] | -9.00 | 2.3e-19 | rejected |
| aifs hourly | EGLC (dev) | 522 | -0.255 [-0.311, -0.189] | -8.02 | 1.0e-15 | rejected |
| aifs hourly | LFPG (dev) | 522 | -0.153 [-0.222, -0.086] | -4.44 | 9.2e-06 | rejected |
| aifs hourly | KDSM (dev) | 522 | +0.262 [+0.195, +0.337] | +7.01 | 2.4e-12 | rejected |
| aifs hourly | YSDU (dev) | 522 | +0.069 [+0.028, +0.117] | +2.98 | 2.8e-03 | rejected |
| aifs hourly | KRNO (dev) | 522 | -0.505 [-0.629, -0.378] | -7.68 | 1.6e-14 | rejected |
| aifs hourly | KSFO (dev) (sea) | 522 | +0.020 [-0.037, +0.075] | +0.68 | 5.0e-01 | not rejected |
| nbm hourly | KORD | 730 | +0.112 [+0.084, +0.139] | +7.92 | 2.3e-15 | rejected |
| nbm hourly | CYYZ (sea) | 730 | +0.075 [+0.043, +0.104] | +4.68 | 2.8e-06 | rejected |
| nbm hourly | KDSM (dev) | 1,096 | +0.064 [+0.029, +0.098] | +3.49 | 4.9e-04 | rejected |
| nbm hourly | KRNO (dev) | 1,096 | -0.255 [-0.294, -0.215] | -12.39 | 2.8e-35 | rejected |
| nbm hourly | KSFO (dev) (sea) | 1,096 | -0.414 [-0.463, -0.365] | -15.77 | 5.1e-56 | rejected |
| nbs hourly | KORD | 730 | +0.145 [+0.116, +0.174] | +9.74 | 2.0e-22 | rejected |
| nbs hourly | CYYZ (sea) | 730 | +0.083 [+0.049, +0.114] | +4.82 | 1.4e-06 | rejected |
| nbs hourly | KDSM (dev) | 1,096 | +0.158 [+0.124, +0.193] | +8.57 | 1.1e-17 | rejected |
| nbs hourly | KRNO (dev) | 1,096 | +0.057 [+0.021, +0.094] | +2.95 | 3.1e-03 | rejected |
| nbs hourly | KSFO (dev) (sea) | 1,096 | +0.094 [+0.067, +0.124] | +6.17 | 7.0e-10 | rejected |
| mav hourly | KORD | 730 | -0.155 [-0.193, -0.117] | -7.87 | 3.6e-15 | rejected |
| mav hourly | KDSM (dev) | 1,096 | -0.124 [-0.164, -0.080] | -5.60 | 2.1e-08 | rejected |
| mav hourly | KRNO (dev) | 1,096 | +0.068 [+0.034, +0.102] | +3.84 | 1.2e-04 | rejected |
| mav hourly | KSFO (dev) (sea) | 1,096 | -0.053 [-0.088, -0.017] | -2.86 | 4.3e-03 | rejected |

**Table E4. Daily maximum (D98.10's days): MAE [95 %] on each source's paired days, per test year and pooled** (`dailymax_<source>.csv`, `dailymax_<source>_skill.csv`; breakdowns by cycle hour, season, version and NBS run set in `dailymax_<source>_breakdown.csv`). Skill = 1 - MAE(a) / MAE(b), percent.

| source | airport | test year | days | competitor's maximum | curve (D98.10) | curve at its steps | raw GFS | skill curve vs it [95 %] | skill curve at its steps vs it |
|---|---|---|---|---|---|---|---|---|---|
| AIFS | EDDM | 2024-25 | 157 | 1.24 [1.07, 1.42] | 0.88 [0.80, 1.00] | 1.57 | 1.50 | +28.5 [+17.1, +37.6] | -27.2 |
| AIFS | EDDM | 2025-26 | 364 | 1.19 [1.07, 1.32] | 1.23 [1.09, 1.40] | 1.76 | 1.79 | -2.8 [-18.0, +8.1] | -47.4 |
| AIFS | EDDM | all | 521 | 1.21 [1.10, 1.31] | 1.12 [1.02, 1.26] | 1.70 | 1.70 | +6.9 [-4.3, +15.9] | -41.2 |
| AIFS | KORD | 2024-25 | 156 | 1.80 [1.56, 2.08] | 1.11 [0.95, 1.29] | 1.59 | 1.32 | +38.1 [+28.7, +47.3] | +11.7 |
| AIFS | KORD | 2025-26 | 361 | 1.27 [1.14, 1.43] | 1.12 [1.03, 1.22] | 1.51 | 1.15 | +11.6 [+1.5, +20.9] | -19.2 |
| AIFS | KORD | all | 517 | 1.43 [1.29, 1.57] | 1.12 [1.03, 1.20] | 1.53 | 1.20 | +21.7 [+13.9, +29.0] | -7.5 |
| AIFS | CYYZ (sea) | 2024-25 | 156 | 1.71 [1.44, 2.02] | 1.22 [1.03, 1.45] | 1.58 | 1.83 | +28.6 [+17.7, +38.0] | +7.6 |
| AIFS | CYYZ (sea) | 2025-26 | 364 | 1.25 [1.13, 1.38] | 1.03 [0.92, 1.15] | 1.28 | 1.30 | +17.8 [+9.7, +25.4] | -2.5 |
| AIFS | CYYZ (sea) | all | 520 | 1.39 [1.26, 1.53] | 1.08 [0.98, 1.19] | 1.37 | 1.46 | +21.8 [+15.3, +28.1] | +1.2 |
| AIFS | ZGSZ (sea) | 2024-25 | 157 | 1.35 [1.18, 1.55] | 0.93 [0.79, 1.05] | 0.98 | 1.68 | +31.4 [+17.4, +45.0] | +27.5 |
| AIFS | ZGSZ (sea) | 2025-26 | 364 | 1.17 [1.05, 1.28] | 0.92 [0.83, 0.99] | 1.08 | 1.52 | +21.4 [+13.9, +28.7] | +7.5 |
| AIFS | ZGSZ (sea) | all | 521 | 1.23 [1.13, 1.33] | 0.92 [0.85, 0.98] | 1.05 | 1.57 | +24.8 [+18.1, +31.7] | +14.2 |
| AIFS | ZUCK | 2024-25 | 157 | 1.58 [1.40, 1.76] | 1.32 [1.14, 1.56] | 1.88 | 1.69 | +16.6 [-2.2, +29.2] | -19.1 |
| AIFS | ZUCK | 2025-26 | 364 | 1.20 [1.10, 1.33] | 1.15 [1.05, 1.24] | 1.40 | 1.34 | +4.3 [-4.7, +14.9] | -16.4 |
| AIFS | ZUCK | all | 521 | 1.32 [1.21, 1.42] | 1.20 [1.10, 1.29] | 1.54 | 1.44 | +8.8 [+0.0, +17.2] | -17.4 |
| AIFS | NZWN (sea) | 2024-25 | 157 | 1.52 [1.29, 1.79] | 0.71 [0.62, 0.81] | 0.95 | 1.45 | +53.1 [+43.5, +60.4] | +37.5 |
| AIFS | NZWN (sea) | 2025-26 | 363 | 1.92 [1.73, 2.14] | 0.73 [0.66, 0.80] | 0.98 | 1.70 | +62.0 [+58.6, +65.7] | +49.1 |
| AIFS | NZWN (sea) | all | 520 | 1.80 [1.64, 1.97] | 0.72 [0.67, 0.78] | 0.97 | 1.63 | +59.8 [+56.0, +63.1] | +46.1 |
| AIFS | EGLC (dev) | 2024-25 | 157 | 1.04 [0.88, 1.19] | 1.01 [0.88, 1.16] | 1.44 | 1.07 | +2.9 [-18.1, +17.9] | -39.1 |
| AIFS | EGLC (dev) | 2025-26 | 364 | 0.96 [0.88, 1.04] | 0.86 [0.76, 0.98] | 1.14 | 1.01 | +9.7 [-3.3, +21.5] | -19.4 |
| AIFS | EGLC (dev) | all | 521 | 0.98 [0.91, 1.05] | 0.91 [0.82, 1.01] | 1.23 | 1.03 | +7.6 [-3.8, +16.5] | -25.7 |
| AIFS | LFPG (dev) | 2024-25 | 157 | 1.32 [1.10, 1.57] | 0.96 [0.88, 1.08] | 1.48 | 1.23 | +27.4 [+12.4, +36.6] | -11.8 |
| AIFS | LFPG (dev) | 2025-26 | 363 | 1.50 [1.39, 1.60] | 0.89 [0.80, 0.97] | 1.41 | 1.21 | +41.1 [+33.3, +47.0] | +6.3 |
| AIFS | LFPG (dev) | all | 520 | 1.45 [1.34, 1.55] | 0.91 [0.85, 0.98] | 1.43 | 1.21 | +37.3 [+30.8, +42.7] | +1.3 |
| AIFS | KDSM (dev) | 2024-25 | 156 | 1.39 [1.19, 1.64] | 1.07 [0.96, 1.21] | 1.42 | 1.72 | +22.8 [+3.7, +37.7] | -2.4 |
| AIFS | KDSM (dev) | 2025-26 | 364 | 1.45 [1.28, 1.66] | 1.31 [1.17, 1.46] | 1.78 | 1.55 | +9.7 [-3.9, +22.6] | -22.8 |
| AIFS | KDSM (dev) | all | 520 | 1.43 [1.29, 1.59] | 1.24 [1.13, 1.36] | 1.67 | 1.60 | +13.5 [+2.0, +23.4] | -16.9 |
| AIFS | YSDU (dev) | 2024-25 | 156 | 1.31 [1.11, 1.51] | 1.01 [0.85, 1.24] | 1.25 | 1.05 | +22.6 [+5.1, +35.0] | +4.2 |
| AIFS | YSDU (dev) | 2025-26 | 359 | 1.55 [1.39, 1.74] | 0.95 [0.86, 1.05] | 1.33 | 1.09 | +38.9 [+31.5, +45.7] | +14.5 |
| AIFS | YSDU (dev) | all | 515 | 1.48 [1.34, 1.62] | 0.97 [0.89, 1.06] | 1.31 | 1.08 | +34.5 [+27.3, +41.1] | +11.7 |
| AIFS | KRNO (dev) | 2024-25 | 156 | 1.22 [0.98, 1.43] | 0.74 [0.65, 0.85] | 1.09 | 1.43 | +38.9 [+24.4, +48.1] | +10.1 |
| AIFS | KRNO (dev) | 2025-26 | 363 | 1.48 [1.31, 1.69] | 0.85 [0.76, 0.97] | 1.19 | 1.34 | +42.4 [+34.3, +49.8] | +19.2 |
| AIFS | KRNO (dev) | all | 519 | 1.40 [1.26, 1.57] | 0.82 [0.74, 0.91] | 1.16 | 1.37 | +41.5 [+34.6, +47.6] | +16.8 |
| AIFS | KSFO (dev) (sea) | 2024-25 | 155 | 1.50 [1.24, 1.78] | 0.98 [0.84, 1.14] | 1.42 | 1.40 | +34.6 [+18.0, +47.4] | +5.1 |
| AIFS | KSFO (dev) (sea) | 2025-26 | 363 | 1.43 [1.29, 1.58] | 1.25 [1.08, 1.44] | 1.72 | 1.57 | +12.9 [-0.5, +25.1] | -19.9 |
| AIFS | KSFO (dev) (sea) | all | 518 | 1.45 [1.33, 1.59] | 1.17 [1.04, 1.31] | 1.63 | 1.52 | +19.6 [+9.1, +29.6] | -12.1 |
| NBM grid | KORD | 2024-25 | 365 | 1.09 [0.96, 1.24] | 1.07 [0.96, 1.19] | 1.07 | 1.18 | +2.3 [-8.0, +11.6] | +2.3 |
| NBM grid | KORD | 2025-26 | 361 | 1.20 [1.04, 1.38] | 1.12 [1.03, 1.22] | 1.11 | 1.15 | +6.4 [-6.3, +17.5] | +6.7 |
| NBM grid | KORD | all | 726 | 1.14 [1.04, 1.26] | 1.09 [1.02, 1.17] | 1.09 | 1.16 | +4.4 [-3.6, +12.2] | +4.6 |
| NBM grid | CYYZ (sea) | 2024-25 | 364 | 1.23 [1.09, 1.39] | 1.06 [0.95, 1.18] | 1.06 | 1.38 | +14.1 [+4.3, +22.9] | +14.1 |
| NBM grid | CYYZ (sea) | 2025-26 | 364 | 1.19 [1.04, 1.36] | 1.03 [0.92, 1.15] | 1.02 | 1.30 | +14.0 [+2.9, +23.6] | +14.3 |
| NBM grid | CYYZ (sea) | all | 728 | 1.21 [1.10, 1.33] | 1.04 [0.96, 1.13] | 1.04 | 1.34 | +14.0 [+6.7, +20.9] | +14.2 |
| NBM grid | KDSM (dev) | 2023-24 | 366 | 1.26 [1.12, 1.37] | 1.20 [1.08, 1.29] | 1.20 | 2.08 | +4.5 [-5.8, +14.3] | +4.5 |
| NBM grid | KDSM (dev) | 2024-25 | 365 | 1.17 [1.05, 1.30] | 1.16 [1.07, 1.26] | 1.16 | 1.56 | +0.2 [-9.4, +10.4] | +0.2 |
| NBM grid | KDSM (dev) | 2025-26 | 364 | 1.46 [1.30, 1.64] | 1.31 [1.17, 1.46] | 1.31 | 1.55 | +10.5 [+0.5, +19.2] | +10.7 |
| NBM grid | KDSM (dev) | all | 1,095 | 1.30 [1.21, 1.38] | 1.22 [1.15, 1.29] | 1.23 | 1.73 | +5.5 [-0.5, +11.1] | +5.5 |
| NBM grid | KRNO (dev) | 2023-24 | 365 | 1.04 [0.94, 1.16] | 1.01 [0.90, 1.14] | 1.01 | 1.77 | +2.8 [-6.9, +11.1] | +3.0 |
| NBM grid | KRNO (dev) | 2024-25 | 365 | 0.89 [0.79, 1.01] | 0.98 [0.85, 1.13] | 0.98 | 1.55 | -10.0 [-18.8, -1.2] | -10.0 |
| NBM grid | KRNO (dev) | 2025-26 | 363 | 0.87 [0.77, 0.99] | 0.85 [0.75, 0.97] | 0.85 | 1.34 | +2.1 [-8.4, +12.4] | +2.1 |
| NBM grid | KRNO (dev) | all | 1,093 | 0.93 [0.87, 1.00] | 0.95 [0.88, 1.02] | 0.95 | 1.55 | -1.5 [-7.1, +4.0] | -1.4 |
| NBM grid | KSFO (dev) (sea) | 2023-24 | 366 | 1.52 [1.21, 1.82] | 1.20 [1.07, 1.34] | 1.20 | 1.81 | +21.0 [+1.9, +33.8] | +20.9 |
| NBM grid | KSFO (dev) (sea) | 2024-25 | 364 | 2.06 [1.69, 2.41] | 1.17 [1.03, 1.31] | 1.17 | 1.61 | +43.1 [+32.2, +50.6] | +43.1 |
| NBM grid | KSFO (dev) (sea) | 2025-26 | 363 | 2.02 [1.75, 2.31] | 1.25 [1.08, 1.43] | 1.25 | 1.57 | +38.2 [+28.1, +46.3] | +38.2 |
| NBM grid | KSFO (dev) (sea) | all | 1,093 | 1.87 [1.68, 2.07] | 1.21 [1.13, 1.30] | 1.21 | 1.66 | +35.3 [+28.4, +41.1] | +35.3 |
| NBS | KORD | 2024-25 | 365 | 1.07 [0.94, 1.22] | 1.07 [0.96, 1.19] | 1.16 | 1.18 | +0.3 [-10.4, +10.0] | -8.8 |
| NBS | KORD | 2025-26 | 359 | 1.17 [1.01, 1.35] | 1.12 [1.03, 1.22] | 1.20 | 1.15 | +4.4 [-10.0, +15.9] | -1.8 |
| NBS | KORD | all | 724 | 1.12 [1.01, 1.23] | 1.09 [1.02, 1.17] | 1.18 | 1.16 | +2.5 [-6.2, +10.6] | -5.2 |
| NBS | CYYZ (sea) | 2024-25 | 364 | 1.17 [1.02, 1.35] | 1.06 [0.95, 1.18] | 1.12 | 1.38 | +9.6 [-0.6, +19.4] | +4.3 |
| NBS | CYYZ (sea) | 2025-26 | 362 | 1.14 [1.00, 1.32] | 1.02 [0.92, 1.15] | 1.11 | 1.30 | +10.3 [-0.7, +20.0] | +2.5 |
| NBS | CYYZ (sea) | all | 726 | 1.16 [1.05, 1.28] | 1.04 [0.96, 1.13] | 1.12 | 1.34 | +9.9 [+2.3, +16.9] | +3.4 |
| NBS | KDSM (dev) | 2023-24 | 366 | 1.18 [1.05, 1.29] | 1.20 [1.08, 1.29] | 1.30 | 2.08 | -1.6 [-13.0, +9.0] | -10.3 |
| NBS | KDSM (dev) | 2024-25 | 365 | 1.13 [1.01, 1.28] | 1.16 [1.07, 1.26] | 1.22 | 1.56 | -2.6 [-14.3, +9.2] | -7.8 |
| NBS | KDSM (dev) | 2025-26 | 362 | 1.37 [1.21, 1.55] | 1.31 [1.17, 1.46] | 1.35 | 1.54 | +4.6 [-6.1, +14.2] | +1.5 |
| NBS | KDSM (dev) | all | 1,093 | 1.23 [1.14, 1.32] | 1.22 [1.15, 1.29] | 1.29 | 1.73 | +0.4 [-6.1, +6.7] | -5.2 |
| NBS | KRNO (dev) | 2023-24 | 365 | 1.03 [0.91, 1.15] | 1.01 [0.90, 1.14] | 1.19 | 1.77 | +1.4 [-9.9, +10.7] | -16.1 |
| NBS | KRNO (dev) | 2024-25 | 365 | 0.95 [0.86, 1.06] | 0.98 [0.85, 1.13] | 1.10 | 1.55 | -2.6 [-14.7, +8.1] | -14.7 |
| NBS | KRNO (dev) | 2025-26 | 361 | 0.92 [0.82, 1.02] | 0.85 [0.76, 0.97] | 1.01 | 1.34 | +7.3 [-4.7, +17.5] | -10.2 |
| NBS | KRNO (dev) | all | 1,091 | 0.97 [0.91, 1.03] | 0.95 [0.88, 1.02] | 1.10 | 1.55 | +2.0 [-4.6, +8.0] | -13.8 |
| NBS | KSFO (dev) (sea) | 2023-24 | 366 | 1.15 [1.03, 1.28] | 1.20 [1.07, 1.34] | 1.30 | 1.81 | -4.1 [-16.5, +6.9] | -12.6 |
| NBS | KSFO (dev) (sea) | 2024-25 | 364 | 1.13 [0.98, 1.28] | 1.17 [1.03, 1.32] | 1.31 | 1.61 | -4.3 [-16.7, +7.1] | -16.3 |
| NBS | KSFO (dev) (sea) | 2025-26 | 361 | 1.30 [1.12, 1.52] | 1.25 [1.09, 1.44] | 1.39 | 1.57 | +4.3 [-7.7, +13.9] | -6.3 |
| NBS | KSFO (dev) (sea) | all | 1,091 | 1.19 [1.10, 1.29] | 1.21 [1.12, 1.30] | 1.33 | 1.67 | -1.1 [-8.1, +5.1] | -11.5 |
| MAV | KORD | 2024-25 | 364 | 1.38 [1.25, 1.53] | 1.07 [0.96, 1.19] | 1.17 | 1.17 | +23.0 [+13.6, +30.8] | +15.8 |
| MAV | KORD | 2025-26 | 360 | 1.56 [1.40, 1.72] | 1.12 [1.03, 1.22] | 1.19 | 1.15 | +28.2 [+18.5, +35.5] | +23.5 |
| MAV | KORD | all | 724 | 1.47 [1.36, 1.58] | 1.09 [1.02, 1.17] | 1.18 | 1.16 | +25.8 [+19.3, +31.4] | +19.9 |
| MAV | KDSM (dev) | 2023-24 | 366 | 1.52 [1.33, 1.65] | 1.20 [1.08, 1.29] | 1.30 | 2.08 | +20.8 [+9.7, +29.8] | +14.0 |
| MAV | KDSM (dev) | 2024-25 | 364 | 1.62 [1.46, 1.79] | 1.17 [1.07, 1.26] | 1.23 | 1.56 | +27.8 [+20.2, +35.2] | +24.1 |
| MAV | KDSM (dev) | 2025-26 | 363 | 1.58 [1.40, 1.74] | 1.30 [1.17, 1.46] | 1.34 | 1.55 | +17.2 [+7.9, +23.8] | +15.1 |
| MAV | KDSM (dev) | all | 1,093 | 1.57 [1.46, 1.66] | 1.22 [1.15, 1.29] | 1.29 | 1.73 | +22.0 [+16.4, +26.6] | +17.8 |
| MAV | KRNO (dev) | 2023-24 | 365 | 0.97 [0.85, 1.11] | 1.01 [0.90, 1.15] | 1.19 | 1.77 | -4.8 [-15.4, +4.1] | -23.4 |
| MAV | KRNO (dev) | 2024-25 | 364 | 1.15 [1.04, 1.28] | 0.98 [0.86, 1.13] | 1.10 | 1.55 | +15.0 [+3.7, +25.1] | +5.0 |
| MAV | KRNO (dev) | 2025-26 | 362 | 1.25 [1.15, 1.38] | 0.85 [0.75, 0.96] | 1.01 | 1.34 | +32.2 [+22.3, +41.1] | +19.4 |
| MAV | KRNO (dev) | all | 1,091 | 1.12 [1.05, 1.20] | 0.95 [0.88, 1.02] | 1.10 | 1.55 | +15.7 [+9.3, +21.8] | +2.2 |
| MAV | KSFO (dev) (sea) | 2023-24 | 366 | 1.24 [1.09, 1.37] | 1.20 [1.07, 1.34] | 1.30 | 1.81 | +3.4 [-8.7, +11.7] | -4.5 |
| MAV | KSFO (dev) (sea) | 2024-25 | 363 | 1.39 [1.21, 1.53] | 1.17 [1.03, 1.32] | 1.31 | 1.61 | +15.3 [+1.9, +25.5] | +5.5 |
| MAV | KSFO (dev) (sea) | 2025-26 | 362 | 1.59 [1.38, 1.84] | 1.24 [1.08, 1.44] | 1.38 | 1.56 | +21.9 [+11.1, +30.4] | +13.2 |
| MAV | KSFO (dev) (sea) | all | 1,091 | 1.41 [1.30, 1.51] | 1.21 [1.12, 1.30] | 1.33 | 1.66 | +14.2 [+7.7, +19.9] | +5.4 |

NBM's maximum from its own steps (descriptive, beside TMAX), MAE pooled: KORD 1.03; CYYZ 1.05; KDSM 1.19; KRNO 1.26; KSFO 1.51. NBS days of versions whose TXN definition was not found (v5.0.14), reported separately (`dailymax_nbs_txn_not_found.csv`): KORD 2 days, NBS 0.28; CYYZ 2 days, NBS 0.83; KDSM 2 days, NBS 2.50; KRNO 2 days, NBS 0.28; KSFO 2 days, NBS 1.11.

**Table E5. Formal tests, daily maximum** (`dailymax_<source>_dm.csv`). Daily mean of |e_curve| - |e_competitor| (negative: the curve's errors are smaller), Newey-West at 7 lags.

| family | airport | days | mean daily difference [95 %] | DM statistic | p-value | BH at 0.05 |
|---|---|---|---|---|---|---|
| aifs daily maximum | EDDM | 521 | -0.083 [-0.200, +0.049] | -1.29 | 2.0e-01 | not rejected |
| aifs daily maximum | KORD | 517 | -0.309 [-0.445, -0.184] | -4.59 | 4.4e-06 | rejected |
| aifs daily maximum | CYYZ (sea) | 520 | -0.302 [-0.410, -0.201] | -5.71 | 1.1e-08 | rejected |
| aifs daily maximum | ZGSZ (sea) | 521 | -0.303 [-0.412, -0.209] | -5.78 | 7.3e-09 | rejected |
| aifs daily maximum | ZUCK | 521 | -0.115 [-0.236, -0.000] | -1.91 | 5.6e-02 | not rejected |
| aifs daily maximum | NZWN (sea) | 520 | -1.075 [-1.229, -0.930] | -13.75 | 5.3e-43 | rejected |
| aifs daily maximum | EGLC (dev) | 521 | -0.074 [-0.168, +0.036] | -1.42 | 1.6e-01 | not rejected |
| aifs daily maximum | LFPG (dev) | 520 | -0.540 [-0.652, -0.422] | -8.91 | 5.3e-19 | rejected |
| aifs daily maximum | KDSM (dev) | 520 | -0.193 [-0.362, -0.027] | -2.22 | 2.7e-02 | rejected |
| aifs daily maximum | YSDU (dev) | 515 | -0.510 [-0.648, -0.377] | -7.45 | 9.0e-14 | rejected |
| aifs daily maximum | KRNO (dev) | 519 | -0.579 [-0.726, -0.448] | -7.95 | 1.9e-15 | rejected |
| aifs daily maximum | KSFO (dev) (sea) | 518 | -0.285 [-0.457, -0.127] | -3.30 | 9.7e-04 | rejected |
| nbm daily maximum | KORD | 726 | -0.051 [-0.149, +0.038] | -1.05 | 2.9e-01 | not rejected |
| nbm daily maximum | CYYZ (sea) | 728 | -0.170 [-0.266, -0.077] | -3.53 | 4.2e-04 | rejected |
| nbm daily maximum | KDSM (dev) | 1,095 | -0.071 [-0.148, +0.006] | -1.81 | 7.1e-02 | not rejected |
| nbm daily maximum | KRNO (dev) | 1,093 | +0.014 [-0.038, +0.065] | +0.52 | 6.0e-01 | not rejected |
| nbm daily maximum | KSFO (dev) (sea) | 1,093 | -0.660 [-0.836, -0.488] | -7.16 | 8.1e-13 | rejected |
| nbs daily maximum | KORD | 724 | -0.027 [-0.128, +0.065] | -0.55 | 5.8e-01 | not rejected |
| nbs daily maximum | CYYZ (sea) | 726 | -0.115 [-0.209, -0.025] | -2.42 | 1.6e-02 | not rejected |
| nbs daily maximum | KDSM (dev) | 1,093 | -0.004 [-0.085, +0.071] | -0.11 | 9.1e-01 | not rejected |
| nbs daily maximum | KRNO (dev) | 1,091 | -0.019 [-0.079, +0.043] | -0.60 | 5.5e-01 | not rejected |
| nbs daily maximum | KSFO (dev) (sea) | 1,091 | +0.014 [-0.063, +0.094] | +0.34 | 7.4e-01 | not rejected |
| mav daily maximum | KORD | 724 | -0.379 [-0.485, -0.270] | -6.81 | 9.7e-12 | rejected |
| mav daily maximum | KDSM (dev) | 1,093 | -0.345 [-0.431, -0.245] | -7.16 | 8.2e-13 | rejected |
| mav daily maximum | KRNO (dev) | 1,091 | -0.176 [-0.253, -0.102] | -4.52 | 6.0e-06 | rejected |
| mav daily maximum | KSFO (dev) (sea) | 1,091 | -0.200 [-0.291, -0.103] | -4.04 | 5.3e-05 | rejected |

**Table E6. Daily maximum from every cycle, by cycle hour: competitor / curve MAE (first lead of the local day)** (`dailymax_<source>_every_cycle.csv`, with intervals and the curve sampled at the competitor's steps).

| source | airport | 00z | 06z | 12z | 18z |
|---|---|---|---|---|---|
| AIFS | EDDM | 1.26 / 1.31 (lead 22-23) | 1.26 / 1.24 (lead 16-17) | 1.22 / 1.16 (lead 10-11) | 1.21 / 1.12 (lead 4-5) |
| AIFS | KORD | 1.43 / 1.12 (lead 5-6) | 1.56 / 1.37 (lead 23-24) | 1.51 / 1.29 (lead 17-18) | 1.53 / 1.21 (lead 11-12) |
| AIFS | CYYZ (sea) | 1.39 / 1.08 (lead 4-5) | 1.38 / 1.29 (lead 22-23) | 1.33 / 1.23 (lead 16-17) | 1.42 / 1.18 (lead 10-11) |
| AIFS | ZGSZ (sea) | 1.25 / 0.98 (lead 16) | 1.19 / 0.99 (lead 10) | 1.23 / 0.92 (lead 4) | 1.29 / 1.04 (lead 22) |
| AIFS | ZUCK | 1.40 / 1.29 (lead 16) | 1.34 / 1.24 (lead 10) | 1.32 / 1.20 (lead 4) | 1.43 / 1.36 (lead 22) |
| AIFS | NZWN (sea) | 1.82 / 0.71 (lead 11-12) | 1.80 / 0.72 (lead 5-6) | 1.82 / 0.74 (lead 23-24) | 1.83 / 0.74 (lead 17-18) |
| AIFS | EGLC (dev) | 1.07 / 1.05 (lead 23-24) | 1.06 / 0.98 (lead 17-18) | 1.00 / 0.95 (lead 11-12) | 0.98 / 0.91 (lead 5-6) |
| AIFS | LFPG (dev) | 1.53 / 1.01 (lead 22-23) | 1.53 / 1.03 (lead 16-17) | 1.47 / 0.95 (lead 10-11) | 1.45 / 0.91 (lead 4-5) |
| AIFS | KDSM (dev) | 1.43 / 1.24 (lead 5-6) | 1.60 / 1.52 (lead 23-24) | 1.53 / 1.43 (lead 17-18) | 1.57 / 1.35 (lead 11-12) |
| AIFS | YSDU (dev) | 1.52 / 0.99 (lead 13-14) | 1.48 / 0.97 (lead 7-8) | 2.06 / 1.28 (lead 25-26) | 1.58 / 1.03 (lead 19-20) |
| AIFS | KRNO (dev) | 1.40 / 0.82 (lead 7-8) | 1.30 / 0.87 (lead 25-26) | 1.39 / 0.91 (lead 19-20) | 1.42 / 0.85 (lead 13-14) |
| AIFS | KSFO (dev) (sea) | 1.45 / 1.17 (lead 7-8) | 1.59 / 1.26 (lead 25-26) | 1.51 / 1.26 (lead 19-20) | 1.49 / 1.23 (lead 13-14) |
| NBM grid | KORD | 1.14 / 1.09 (lead 5-6) | 1.31 / 1.30 (lead 23-24) | 1.24 / 1.24 (lead 17-18) | 1.19 / 1.16 (lead 11-12) |
| NBM grid | CYYZ (sea) | 1.21 / 1.04 (lead 4-5) | 1.30 / 1.21 (lead 22-23) | 1.26 / 1.16 (lead 16-17) | 1.22 / 1.11 (lead 10-11) |
| NBM grid | KDSM (dev) | 1.30 / 1.22 (lead 5-6) | 1.41 / 1.50 (lead 23-24) | 1.38 / 1.41 (lead 17-18) | 1.34 / 1.32 (lead 11-12) |
| NBM grid | KRNO (dev) | 0.93 / 0.95 (lead 7-8) | 0.85 / 0.89 (lead 25-26) | 0.98 / 1.01 (lead 19-20) | 0.95 / 0.97 (lead 13-14) |
| NBM grid | KSFO (dev) (sea) | 1.87 / 1.21 (lead 7-8) | 2.20 / 1.35 (lead 25-26) | 1.91 / 1.27 (lead 19-20) | 1.88 / 1.24 (lead 13-14) |
| NBS | KORD | 1.12 / 1.09 (lead 5-6) | 1.33 / 1.30 (lead 23-24) | 1.23 / 1.24 (lead 17-18) | 1.17 / 1.16 (lead 11-12) |
| NBS | CYYZ (sea) | 1.16 / 1.04 (lead 4-5) | 1.28 / 1.21 (lead 22-23) | 1.26 / 1.16 (lead 16-17) | 1.18 / 1.11 (lead 10-11) |
| NBS | KDSM (dev) | 1.23 / 1.22 (lead 5-6) | 1.38 / 1.50 (lead 23-24) | 1.37 / 1.41 (lead 17-18) | 1.29 / 1.32 (lead 11-12) |
| NBS | KRNO (dev) | 0.97 / 0.95 (lead 7-8) | 0.95 / 0.88 (lead 25-26) | 1.04 / 1.01 (lead 19-20) | 0.99 / 0.97 (lead 13-14) |
| NBS | KSFO (dev) (sea) | 1.19 / 1.21 (lead 7-8) | 1.30 / 1.35 (lead 25-26) | 1.27 / 1.27 (lead 19-20) | 1.24 / 1.24 (lead 13-14) |
| MAV | KORD | 1.47 / 1.09 (lead 5-6) | 1.75 / 1.30 (lead 23-24) | 1.70 / 1.24 (lead 17-18) | 1.64 / 1.16 (lead 11-12) |
| MAV | KDSM (dev) | 1.57 / 1.22 (lead 5-6) | 1.82 / 1.50 (lead 23-24) | 1.81 / 1.41 (lead 17-18) | 1.70 / 1.32 (lead 11-12) |
| MAV | KRNO (dev) | 1.12 / 0.95 (lead 7-8) | 1.11 / 0.88 (lead 25-26) | 1.19 / 1.01 (lead 19-20) | 1.19 / 0.97 (lead 13-14) |
| MAV | KSFO (dev) (sea) | 1.41 / 1.21 (lead 7-8) | 1.58 / 1.35 (lead 25-26) | 1.47 / 1.27 (lead 19-20) | 1.37 / 1.24 (lead 13-14) |

**Table E7. NBS TXN window per NBM version (D108.4(c))** (`txn_windows.csv`, with the text and every URL tried).

| version | first run | status | maximum window (UTC) | page |
|---|---|---|---|---|
| v4.1 | before the window | definition found | 12Z (current day) to 06Z (next day) | https://vlab.noaa.gov/web/mdl/nbm-textcard-v4.1 |
| v4.2 | 2024-05-15T00:00Z | definition found | 12Z (current day) to 06Z (next day) | https://vlab.noaa.gov/web/mdl/nbm-textcard-v4.2 |
| v4.3 | 2025-05-27T12:00Z | definition found | 12Z (current day) to 06Z (next day) | https://vlab.noaa.gov/web/mdl/nbm-textcard-v4.3 |
| v5.0 | 2026-04-30T13:00Z | definition found | 12Z (current day) to 06Z (next day) | https://vlab.noaa.gov/web/mdl/nbm-textcard-v5.0 |
| v5.0.14 | 2026-07-28T12:00Z | definition not found | - | - |

Maximum fields and their windows: AIFS none (highest of its 6-hourly steps, labelled "6-hourly steps"); NBM TMAX 12z to 00z UTC from the same run; NBS TXN as above, reported at 00Z; MAV X daytime 7 a.m. to 7 p.m. local standard time. Each is taken from the same run, the window starting on the local date inside leads 3 to 48.

**Table E8. The official maximum's gap: CLI minus our hourly-report maximum, degrees C** (`official_gap.csv`, with every percentile).

| airport | test year | days (civil / agree) | civil day: mean, MAE | 10th to 90th pct | share equal (< 0.05) | standard time day: mean, MAE | on agreement days: mean, MAE |
|---|---|---|---|---|---|---|---|
| KORD | 2024-25 | 365 / 327 | +0.26, 0.34 | -0.00 to +0.56 | 52 % | +0.30, 0.31 | +0.27, 0.36 |
| KORD | 2025-26 | 361 / 361 | +0.27, 0.32 | -0.00 to +0.56 | 52 % | +0.29, 0.31 | +0.27, 0.32 |
| KORD | all | 726 / 688 | +0.27, 0.33 | -0.00 to +0.56 | 52 % | +0.29, 0.31 | +0.27, 0.34 |
| KDSM (dev) | 2023-24 | 366 / 349 | +0.34, 0.39 | -0.00 to +0.56 | 42 % | +0.37, 0.38 | +0.35, 0.40 |
| KDSM (dev) | 2024-25 | 363 / 321 | +0.29, 0.36 | -0.00 to +0.56 | 46 % | +0.33, 0.34 | +0.30, 0.36 |
| KDSM (dev) | 2025-26 | 364 / 364 | +0.28, 0.33 | -0.00 to +0.56 | 48 % | +0.30, 0.31 | +0.28, 0.33 |
| KDSM (dev) | all | 1093 / 1034 | +0.30, 0.36 | -0.00 to +0.56 | 45 % | +0.33, 0.34 | +0.31, 0.37 |
| KRNO (dev) | 2023-24 | 365 / 363 | +0.52, 0.53 | -0.00 to +1.11 | 27 % | +0.52, 0.53 | +0.52, 0.52 |
| KRNO (dev) | 2024-25 | 362 / 362 | +0.50, 0.51 | -0.00 to +1.11 | 30 % | +0.50, 0.51 | +0.50, 0.51 |
| KRNO (dev) | 2025-26 | 363 / 363 | +0.46, 0.46 | -0.00 to +1.11 | 33 % | +0.47, 0.47 | +0.46, 0.46 |
| KRNO (dev) | all | 1090 / 1088 | +0.50, 0.50 | -0.00 to +1.11 | 30 % | +0.50, 0.50 | +0.49, 0.50 |
| KSFO (dev) (sea) | 2023-24 | 365 / 365 | +0.47, 0.47 | -0.00 to +1.11 | 37 % | +0.47, 0.47 | +0.47, 0.47 |
| KSFO (dev) (sea) | 2024-25 | 361 / 361 | +0.47, 0.47 | -0.00 to +1.11 | 32 % | +0.47, 0.47 | +0.47, 0.47 |
| KSFO (dev) (sea) | 2025-26 | 361 / 361 | +0.49, 0.50 | -0.00 to +1.11 | 32 % | +0.49, 0.50 | +0.49, 0.50 |
| KSFO (dev) (sea) | all | 1087 / 1087 | +0.48, 0.48 | -0.00 to +1.11 | 33 % | +0.48, 0.48 | +0.48, 0.48 |

**Table E9. Daily maximum scored against CLI: MAE and mean error, all test years** (`official_scores.csv`, which has each test year and NBS by version). Each pair set on its own days.

| airport | pair set | forecast | all days: n, MAE, mean error | CLI and GHCN agree: n, MAE |
|---|---|---|---|---|
| KORD | curve and raw GFS (D98.10 days with CLI) | curve | 729, 1.15, +0.45 | 691, 1.16 |
| KORD | curve and raw GFS (D98.10 days with CLI) | raw_gfs | 729, 1.22, +0.64 | 691, 1.23 |
| KORD | curve and raw GFS (D98.10 days with CLI) | our hourly-report maximum | 726, 0.33, +0.27 | 688, 0.34 |
| KORD | NBM grid pairs | nbm (TMAX) | 729, 1.10, +0.21 | 691, 1.11 |
| KORD | NBM grid pairs | nbm (its own steps) | 728, 1.16, +0.74 | 690, 1.18 |
| KORD | NBM grid pairs | curve | 729, 1.15, +0.45 | 691, 1.16 |
| KORD | NBM grid pairs | raw_gfs | 729, 1.22, +0.64 | 691, 1.23 |
| KORD | NBS pairs | nbs (TXN) | 727, 1.08, +0.23 | 689, 1.09 |
| KORD | NBS pairs | curve | 727, 1.15, +0.44 | 689, 1.16 |
| KORD | NBS pairs | raw_gfs | 727, 1.22, +0.65 | 689, 1.23 |
| KORD | MAV pairs | mav (X) | 727, 1.40, -0.04 | 689, 1.40 |
| KORD | MAV pairs | curve | 727, 1.15, +0.44 | 689, 1.16 |
| KORD | MAV pairs | raw_gfs | 727, 1.22, +0.64 | 689, 1.23 |
| KDSM (dev) | curve and raw GFS (D98.10 days with CLI) | curve | 1093, 1.28, +0.28 | 1034, 1.29 |
| KDSM (dev) | curve and raw GFS (D98.10 days with CLI) | raw_gfs | 1093, 1.83, +0.67 | 1034, 1.87 |
| KDSM (dev) | curve and raw GFS (D98.10 days with CLI) | our hourly-report maximum | 1093, 0.36, +0.30 | 1034, 0.37 |
| KDSM (dev) | NBM grid pairs | nbm (TMAX) | 1093, 1.27, +0.18 | 1034, 1.26 |
| KDSM (dev) | NBM grid pairs | nbm (its own steps) | 1091, 1.27, +0.55 | 1032, 1.28 |
| KDSM (dev) | NBM grid pairs | curve | 1093, 1.28, +0.28 | 1034, 1.29 |
| KDSM (dev) | NBM grid pairs | raw_gfs | 1093, 1.83, +0.67 | 1034, 1.87 |
| KDSM (dev) | NBS pairs | nbs (TXN) | 1091, 1.22, +0.23 | 1032, 1.21 |
| KDSM (dev) | NBS pairs | curve | 1091, 1.28, +0.28 | 1032, 1.29 |
| KDSM (dev) | NBS pairs | raw_gfs | 1091, 1.83, +0.68 | 1032, 1.87 |
| KDSM (dev) | MAV pairs | mav (X) | 1091, 1.50, -0.04 | 1032, 1.49 |
| KDSM (dev) | MAV pairs | curve | 1091, 1.28, +0.27 | 1032, 1.29 |
| KDSM (dev) | MAV pairs | raw_gfs | 1091, 1.83, +0.67 | 1032, 1.87 |
| KRNO (dev) | curve and raw GFS (D98.10 days with CLI) | curve | 1092, 1.13, +0.65 | 1090, 1.13 |
| KRNO (dev) | curve and raw GFS (D98.10 days with CLI) | raw_gfs | 1092, 1.95, +1.73 | 1090, 1.95 |
| KRNO (dev) | curve and raw GFS (D98.10 days with CLI) | our hourly-report maximum | 1090, 0.50, +0.50 | 1088, 0.50 |
| KRNO (dev) | NBM grid pairs | nbm (TMAX) | 1092, 1.10, +0.62 | 1090, 1.10 |
| KRNO (dev) | NBM grid pairs | nbm (its own steps) | 1091, 1.63, +1.44 | 1089, 1.63 |
| KRNO (dev) | NBM grid pairs | curve | 1092, 1.13, +0.65 | 1090, 1.13 |
| KRNO (dev) | NBM grid pairs | raw_gfs | 1092, 1.95, +1.73 | 1090, 1.95 |
| KRNO (dev) | NBS pairs | nbs (TXN) | 1090, 0.83, -0.02 | 1088, 0.83 |
| KRNO (dev) | NBS pairs | curve | 1090, 1.13, +0.65 | 1088, 1.13 |
| KRNO (dev) | NBS pairs | raw_gfs | 1090, 1.95, +1.73 | 1088, 1.95 |
| KRNO (dev) | MAV pairs | mav (X) | 1090, 0.95, -0.27 | 1088, 0.95 |
| KRNO (dev) | MAV pairs | curve | 1090, 1.13, +0.65 | 1088, 1.13 |
| KRNO (dev) | MAV pairs | raw_gfs | 1090, 1.95, +1.73 | 1088, 1.95 |
| KSFO (dev) (sea) | curve and raw GFS (D98.10 days with CLI) | curve | 1089, 1.35, +0.70 | 1089, 1.35 |
| KSFO (dev) (sea) | curve and raw GFS (D98.10 days with CLI) | raw_gfs | 1089, 1.91, +1.35 | 1089, 1.91 |
| KSFO (dev) (sea) | curve and raw GFS (D98.10 days with CLI) | our hourly-report maximum | 1087, 0.48, +0.48 | 1087, 0.48 |
| KSFO (dev) (sea) | NBM grid pairs | nbm (TMAX) | 1089, 1.62, -1.06 | 1089, 1.62 |
| KSFO (dev) (sea) | NBM grid pairs | nbm (its own steps) | 1088, 1.46, -0.15 | 1088, 1.46 |
| KSFO (dev) (sea) | NBM grid pairs | curve | 1089, 1.35, +0.70 | 1089, 1.35 |
| KSFO (dev) (sea) | NBM grid pairs | raw_gfs | 1089, 1.91, +1.35 | 1089, 1.91 |
| KSFO (dev) (sea) | NBS pairs | nbs (TXN) | 1087, 1.15, -0.02 | 1087, 1.15 |
| KSFO (dev) (sea) | NBS pairs | curve | 1087, 1.35, +0.69 | 1087, 1.35 |
| KSFO (dev) (sea) | NBS pairs | raw_gfs | 1087, 1.91, +1.35 | 1087, 1.91 |
| KSFO (dev) (sea) | MAV pairs | mav (X) | 1088, 1.31, -0.28 | 1088, 1.31 |
| KSFO (dev) (sea) | MAV pairs | curve | 1088, 1.35, +0.70 | 1088, 1.35 |
| KSFO (dev) (sea) | MAV pairs | raw_gfs | 1088, 1.91, +1.35 | 1088, 1.91 |

Truth windows: CLI is midnight to midnight local standard time from continuous readings; the forecasts are for the civil local day. Every score against CLI is descriptive.

---

## Part 3. Candidates for later

None of these is done or changed here. Each would be a build choice, fixed in its own entry and judged by D89 on
the six development airports (more than 1 % lower average MAE, lower at 4 of 6 airports and in 2 of 3 years)
before it could touch the product.

1. **Smooth the curve across leads.** Evidence: the curve's hour-to-hour jaggedness is 1.5 to 3.3 times raw
   GFS's and its run-to-run change is larger than raw GFS's at every airport (Table C1); the ZUCK case shows the
   steps. A light smoother over neighbouring leads (or a model shared by neighbouring leads; D94's pooled
   structures were tested for accuracy, not smoothness, F143) might cut noise at no cost. Test: D89 on the hourly
   MAE and the daily maximum's MAE, with smoothness and run-to-run change reported beside it.
2. **A small upward offset for the daily maximum.** Evidence: the maximum reads low by +0.12 to +0.25 degrees C at
   every claim airport and at five of six development airports (Table B1a); Table B4 splits it into a
   peak-level and a timing term. It is consistent with a selection effect (the observed maximum is the highest of about 24 noisy readings, which a forecast of each hour cannot know), but the decomposition does not separate that from any damping of the forecast peak; raw GFS's larger low reading at some airports is a real bias. D99's
   own daily-maximum model and its daily drift correction were not adopted (F148); a fixed offset per airport and
   cycle hour, fitted on training rows only, is simpler and was not tried. Test: D89 on D98.10's metric.
3. **Show a range on the page.** Evidence: Tables B9 and B10 give stable empirical ranges per airport, lead band
   and season, and the spread across test years is small (Tables A4, B1c). Test: not D89 (no MAE change); a
   calibration check that the shown 80 % range holds about 80 % of later errors at the development airports, fold
   by fold.
4. **Flag edge-of-day maxima on the page.** Evidence: raw GFS puts the maximum in the first or last local hour on
   19 % of days at ZUCK (Table B6), and the observed maximum is there on 7 to 14 % of days at the
   claim airports. A display note ("this day's highest value is at midnight") changes no number. Test: none
   needed for a display note; D105.5(i) already counts these days in the live test.
5. **Watch the regimes where b is large.** Evidence: the top |b| third has the highest curve MAE at every airport
   (Table A7), though large |b| may coincide with harder seasons or weather, which this breakdown does not
   separate. A drift weight that adapts to the size of recent errors is a possible later build choice; D97's
   weight (0.02) was fixed in advance and must not be tuned on these results. Test: D89 with the weight rule fixed
   first.
6. **Use station guidance where it exists.** Evidence: NBS (the NBM station text forecast) has the smaller hourly
   MAE than the curve at all 5 airports it covers (the curve's MAE is 5.0 % (KRNO) to 13.8 % (KORD) larger), every
   formal test rejecting (Tables 2a, E2, E3); for the daily maximum no test separates them (Table E5). A blend of the curve with
   NBS, or NBS as an input, would apply only where NBS exists, which D89's identical-at-every-airport rule (SPEC 2.5)
   would have to allow first. Seen after the comparisons; any test is a D89 build choice.
7. **A maximum aimed at the official figure at US airports.** Evidence: the official (CLI) maximum is above our
   hourly-report maximum by +0.27 (KORD) to +0.50 (KRNO) degrees C on average, nearly the same over the local
   standard time day (Table E8), and the curve's mean error against CLI is +0.28 (KDSM) to +0.70 (KSFO) (Part 1
   item 3, Table E9). An offset learned on training days against CLI would change the target D82.8 fixed, so it
   needs an owner's decision before any build choice. Seen after the comparisons; any test is a D89 build choice.
