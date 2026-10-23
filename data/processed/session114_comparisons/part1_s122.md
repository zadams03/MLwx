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
  station forecast, at 5 of 5. Against the NBM grid it is better at 2 of 5 hourly and worse at 3, and better at 2 of 5 for the daily maximum (item 4; F157.3, F157.4). For the daily maximum it beats AIFS at 9 of
  12 (AIFS's maximum is the highest of four 6-hourly values; read at the same steps the curve's is
  worse at 6 of 12) and MAV at 4 of 4, and no test separates it from
  NBS at 5 of 5. Against ECMWF IFS it is better at 12 of 12 hourly and at 12 of 12 for the daily maximum (IFS's maximum: the highest of its 3-hourly steps, D111.4).

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
| EDDM | 1.33 | 1.79 | 1.43 | 1.21 / 1.28 | - | - | - | 1.42 / 1.33 * |
| KORD | 1.19 | 1.34 | 1.22 | 1.12 / 1.26 * | 1.05 / 1.16 * | 1.06 / 1.21 * | 1.36 / 1.21 * | 1.39 / 1.18 * |
| CYYZ (sea) | 1.14 | 1.47 | 1.20 | 1.17 / 1.18 | 1.05 / 1.12 * | 1.07 / 1.15 * | - | 1.35 / 1.14 * |
| ZGSZ (sea) | 0.90 | 1.16 | 0.94 | 0.96 / 0.89 | - | - | - | 1.31 / 0.89 * |
| ZUCK | 1.09 | 1.46 | 1.17 | 1.06 / 1.10 | - | - | - | 1.32 / 1.10 * |
| NZWN (sea) | 0.79 | 1.16 | 0.83 | 1.06 / 0.79 * | - | - | - | 0.94 / 0.78 * |
| EGLC (dev) | 0.84 | 1.04 | 0.85 | 1.13 / 0.87 * | - | - | - | 1.17 / 0.83 * |
| LFPG (dev) | 0.95 | 1.23 | 1.00 | 1.11 / 0.95 * | - | - | - | 1.28 / 0.96 * |
| KDSM (dev) | 1.30 | 1.88 | 1.43 | 1.08 / 1.35 * | 1.21 / 1.27 * | 1.16 / 1.32 * | 1.45 / 1.32 * | 1.50 / 1.30 * |
| YSDU (dev) | 1.23 | 1.52 | 1.32 | 1.12 / 1.19 * | - | - | - | 1.34 / 1.24 * |
| KRNO (dev) | 1.21 | 2.22 | 1.41 | 1.60 / 1.10 * | 1.44 / 1.19 * | 1.17 / 1.22 * | 1.16 / 1.23 * | 2.20 / 1.21 * |
| KSFO (dev) (sea) | 1.00 | 1.29 | 1.14 | 0.94 / 0.96 | 1.40 / 0.99 * | 0.92 / 1.01 * | 1.06 / 1.01 * | 1.30 / 1.00 * |

**Table 2b. Daily maximum** (D98.10's days; truth our hourly-report maximum; each competitor's own maximum: AIFS the
highest of its 6-hourly steps, NBM TMAX, NBS TXN, MAV X, windows as labelled in Part 2).

| airport | curve | raw GFS | linear MOS | AIFS | NBM grid | NBS | MAV | ECMWF IFS |
|---|---|---|---|---|---|---|---|---|
| EDDM | 1.25 | 1.79 | 1.37 | 1.21 / 1.12 | - | - | - | 1.42 / 1.25 * |
| KORD | 1.09 | 1.16 | 1.10 | 1.43 / 1.12 * | 1.14 / 1.09 | 1.12 / 1.09 | 1.47 / 1.09 * | 1.38 / 1.09 * |
| CYYZ (sea) | 1.04 | 1.34 | 1.13 | 1.39 / 1.08 * | 1.21 / 1.04 * | 1.16 / 1.04 | - | 1.46 / 1.04 * |
| ZGSZ (sea) | 0.91 | 1.52 | 1.07 | 1.23 / 0.92 * | - | - | - | 1.65 / 0.91 * |
| ZUCK | 1.17 | 1.37 | 1.30 | 1.32 / 1.20 | - | - | - | 1.50 / 1.17 * |
| NZWN (sea) | 0.74 | 1.70 | 0.83 | 1.80 / 0.72 * | - | - | - | 1.48 / 0.74 * |
| EGLC (dev) | 0.84 | 0.95 | 0.89 | 0.98 / 0.91 | - | - | - | 1.04 / 0.84 * |
| LFPG (dev) | 0.96 | 1.20 | 1.05 | 1.45 / 0.91 * | - | - | - | 1.23 / 0.96 * |
| KDSM (dev) | 1.22 | 1.73 | 1.46 | 1.43 / 1.24 * | 1.30 / 1.22 | 1.23 / 1.22 | 1.57 / 1.22 * | 1.41 / 1.22 * |
| YSDU (dev) | 1.03 | 1.09 | 1.11 | 1.48 / 0.97 * | - | - | - | 1.61 / 1.03 * |
| KRNO (dev) | 0.95 | 1.55 | 0.99 | 1.40 / 0.82 * | 0.93 / 0.95 | 0.97 / 0.95 | 1.12 / 0.95 * | 2.44 / 0.95 * |
| KSFO (dev) (sea) | 1.21 | 1.66 | 1.39 | 1.45 / 1.17 * | 1.87 / 1.21 * | 1.19 / 1.21 | 1.41 / 1.21 * | 1.57 / 1.21 * |

- **Formal tests, hourly:** the curve is better than AIFS at 4 of 12 airports
  (NZWN, EGLC, LFPG, KRNO) and worse at 3 (KORD, KDSM, YSDU); better than the NBM grid at 2
  (KRNO, KSFO) and worse at 3 (KORD, CYYZ, KDSM); worse than NBS at 5 of
  5; better than MAV at 3 (KORD, KDSM, KSFO) and worse at 1
  (KRNO); better than ECMWF IFS at 12 of 12.
- **Formal tests, daily maximum:** better than AIFS at 9 of 12, the NBM grid at
  2 of 5 (CYYZ, KSFO), NBS at 0 of 5, MAV at
  4 of 4, ECMWF IFS (the highest of its 3-hourly steps, D111.4) at 12 of 12; worse than no competitor at any airport.
- **ECMWF IFS reads cold:** its hourly mean error is positive at 10 of 12 airports (F160.4), and the reading check found no fault, so the cold error is the model's own, not the reading's (F162.8).
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
  (Part 3). Figures: `comparison_hourly_mae_s122.svg`, `comparison_dailymax_mae_s122.svg`, `comparison_skill_s122.svg`,
  `comparison_lead_band_s122.svg`, `comparison_official_gap.svg`.
