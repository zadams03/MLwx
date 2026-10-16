# Session 113: D107 (F155 accepted with two rulings, and the comparison sources, their pull and the comparison rules fixed before any score), and the probe and pull

Recommended model: Opus.

## Read first

- STATUS.md and SPEC section 2 (always). SPEC sections 3.4 and 5.2.
- DECISIONS.md, the live file, in full (this session records a decision).
- Archived entries, one at a time by line range, only when a step needs them: D47, D72.4, D72.6, D72.8, D76.2, D77.2, D77.7, F123 (all of it), F127.3, F127.7, F131.7, F132.5, D82.8, D83.3, F133.3, D86.5, D89.3, D98.10(a), D100.4, F117.3.
- Files, when the step that uses them starts, docstrings and the functions used only: `scripts/session76_grib_pull.py` (`bilinear_from_gid`), `scripts/session82_source_probe.py` (listing and decoding helpers), `scripts/session85_nbm_mos_comparison.py` and `scripts/session87_forward_competitors.py` (the NBM byte-range and MAV fetch code; read only, and session 87's script is never run: it is for 2026-27), `scripts/session90_airport_check.py` (positions).

## What this session is

D107 is recorded first. It accepts F155 with two rulings, fixes the sources, windows and pull rules for comparison forecasts and the official daily maximum on spent years, and fixes session 114's comparison rules before any competitor value is scored. Then the session probes each source, applies a cost gate, and pulls point values on each airport's own test periods.

It scores nothing (D107.2). It computes no error, and opens no observation file, stage C table or prediction file. No value valid after 2026-07-31T23:00 UTC is requested, kept or used. Nothing from the 37 airports of F153.6 is read.

Network: the archives named in D107.4 and D107.8 and their documentation pages only. Nothing is installed; if a needed package is missing, stop. At most 8 requests at once (D107.7). For long runs follow D86.5. Pulls run in monthly chunks with a done-marker per chunk, so a rerun skips finished chunks; a chunk that fails 3 times is recorded and the pull goes on.

Write a checkpoint line to `notes/session-113-output.txt` after each step (D93.11). Stop rather than work around a failed check. Scripts print short summaries; full tables go to files (D93.12). No forecast or observed value is printed.

## Scope: the only files this session may create or edit

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`
- `scripts/session113_comparison_pull.py` (new)
- `data/processed/session113/` (new folder and files)
- `notes/session-113-output.txt` (new)
- Outside the repo: one temporary folder for downloads in flight, deleted at the end.

Everything else is out of scope, including SPEC.md, RESULTS.md, README.md, CLAUDE.md, `ANALYSIS.md`, `docs/PROJECT-INSTRUCTIONS.md`, every existing script (frozen or not), every existing table and data file, every model folder, `src/mlwx/`, `tests/` and `requirements.txt`. Anything worth changing there is reported as an open item.

## Steps

### Step 0: Preflight

- `git status` is clean apart from this session file. HEAD is session 112's commit (its title is the first line of `docs/commits/commit-112.txt`).
- The Live index lists D93, D103, D105, D106 and F155. No D107 or F156 exists in either DECISIONS file. None of this session's new paths exists.
- `eccodes`, `numpy` and `requests` import; record their versions. Stop if any is missing.
- Record DECISIONS.md's byte size.

Stop if any check fails.

### Step 1: Record D107

Append the block below to DECISIONS.md, byte-equal (copy it with `sed` from this file, then check with `diff` and `cmp`), and add D107 to the Live index. Count em-dashes in the block: must be 0.

~~~markdown
---

## 2026-10-15: Session 113 decision: F155 accepted, the comparison sources and their pull on spent years, and session 114's comparison rules fixed before any score (owner, planning chat)

**D107. Owner decisions, planning chat (after session 112's commit): F155 accepted with two rulings; the sources, windows and pull rules for the probe and pull of comparison forecasts and the official daily maximum on spent years (D106.15); and the rules for session 114's comparisons, fixed before any competitor value is scored.** Written at the start of session 113, before any other edit or network call. No competitor value has been read, and no value on or after 2026-08-01 has been scored.

- **D107.1 F155 accepted,** with its F155.7 readings. Two are owner rulings. (a) A run (leads 3 to 48) never holds a whole second local day, so D106.7's "day 1 or day 2" is replaced by the cycle hour, which fixes how far ahead a local day lies. D106.15's plan for session 114 is read the same way, and no later entry uses "day 2" for a run of leads 3 to 48. (b) The tercile edges for |b| and for the curve minus raw GFS come from the test period's forecast values (forecast side only), because neither quantity has a training value.
- **D107.2 Status.** Session 113 probes and pulls; it scores nothing. It computes no error, and compares no competitor value, official maximum or forecast with an observation, with our forecasts or with another source, except D107.8's agreement count between the two official sources. Session 114's comparisons are descriptive (D106.2): no verdict, model, setting, rule, bar or table changes, and nothing is selected or tuned on them. Ideas go to `ANALYSIS.md`'s candidates for later.
- **D107.3 What seeing these years costs (D72.6).** Once session 114 scores a competitor at an airport and test year, that year counts as used for that model at that airport, and a later stage D spent-year test of that model there may not use it. Every test year is pulled, so no spent-year test of ECMWF IFS or AIFS remains at these 12 airports; claims for those models come from new airports or forward years (D72.4). The 37 airports of F153.6 are not touched. D107.9's rules are fixed here, before any score, and are not changed after one.
- **D107.4 Sources, in this order.** ECMWF IFS open data (AWS `ecmwf-forecasts`); ECMWF AIFS Single (same bucket); NBM CONUS (the `core` grid on AWS, and the NBS station text from IEM's MOS archive); GFS MOS (MAV, IEM's MOS archive); the official daily maximum (D107.8). WeatherNext is deferred: the owner has no access yet; once access is granted it gets its own probe and pull under D107.5 to D107.10, and D107.3 applies to it in the same way. ICON is dropped: the official archive keeps 24 hours (F123.3); the third-party copy needs an account and accepted conditions, and its completeness is unknown; and its icosahedral grid cannot take D106.15's four-point interpolation. D76.2 stands.
- **D107.5 Airports and windows.** ECMWF at the 12 airports of D103.4. NBM and MAV at DSM, RNO, KSFO and KORD; NBM also at CYYZ if the probe finds it inside the CONUS grid (grid) or listed as an NBS station (text). Each airport's own test periods: development airports, cycles 2023-08-01T00 to 2026-07-31T18 (D89.3's test years); claim airports, cycles 2024-08-01T00 to 2026-07-31T18 (D100.4). All four cycles (00, 06, 12, 18 UTC) where a source has them; a cycle a source lacks is counted, never filled. Leads 3 to 48 at each source's own steps. Nothing valid after 2026-07-31T23:00 UTC, and no maximum whose window ends after it. IFS's 0.4 degree months (to 2024-01-31) are kept and labelled, as are IFS's cycle changes (48r1, 49r1, 50r1), AIFS's versions and NBM's (v4.2, v4.3, v5.0, v5.0.14; D77.7 with F127.7's corrections).
- **D107.6 What is kept per value.** Gridded sources: 2 m temperature at the four grid points around IEM's airport position (D83.3), with bilinear weights computed as session 76's `bilinear_from_gid` (the GFS route), the nearest point marked, and each point's model terrain height where the source carries an orography field (recorded as absent otherwise). Text sources (MAV, NBS): values as issued in whole degrees F, also converted to degrees C exactly. Each source's own maximum field where it exists (ECMWF's maximum 2 m temperature parameter, NBM's TMAX grid, NBS's TXN, MAV's X), with its window in UTC and its stated definition. Point values only, as gzipped CSVs under `data/processed/session113/`, each under 50 MB, with a manifest of every URL, byte range and index line; no GRIB file is kept (D47).
- **D107.7 Cost gate.** Before each gridded pull, the probe measures the bytes and time per message on spent dates and estimates the source's total. A source whose estimate exceeds 250 GB of downloads or 24 hours of wall time is not pulled; its estimate is reported and the owner decides. NBS is pulled whatever the NBM grid estimate is. At most 8 requests run at once.
- **D107.8 The official daily maximum.** At DSM, RNO, KSFO and KORD: the NWS daily climate report (CLI) maximum from IEM's archive (primary) and GHCN-Daily TMAX from NCEI (cross-check), each station's identity checked by its metadata. The climate days of each airport's test periods whose window ends on or before 2026-07-31T23:00 UTC. The climate day runs midnight to midnight local standard time; this is recorded, not adjusted. Session 113 reports how many days the two sources agree on after exact conversion, and nothing else about their values.
- **D107.9 Session 114's comparison rules.** (a) Primary: same cycle. Each competitor's run at the same nominal cycle as our GFS cycle. Each source's arrival latency (D107.10) is reported beside it and not adjusted for. (b) Hourly: common valid times at the competitor's own steps and a common window (the leads where both have values); raw GFS beside each raw competitor; gridded values with the same four-point interpolation and elevation treatment as GFS (D106.15) where the source's terrain heights exist, otherwise labelled; MAV and NBS as issued. (c) The daily maximum: ours read off the curve (D98.10) and also sampled at each competitor's time step (D106.15); each competitor's own maximum field where it exists, labelled with its definition (its window and UTC span); otherwise read off its own steps. Days are grouped by cycle hour (D107.1(a)). (d) Truth: our hourly-report maximum (D82.8) for every comparison. At the four US airports, the official maximum as a second truth: to measure its gap from our hourly-report maximum on the same days, and to score NBM's and MAV's maxima, and ours, against the truth NBM and MAV forecast. Each window difference (civil local day, local standard time day, daytime windows) is labelled. (e) Metrics and uncertainty as D106.5 and D106.12: 7-day moving-block bootstrap, seed 114, 10,000 resamples for headline figures and 2,000 for breakdown cells; Diebold-Mariano on the daily mean of |e_A| - |e_B| with a Newey-West variance at 7 lags, the curve against each competitor, one family per competitor and output (hourly, daily maximum), Benjamini-Hochberg at 0.05 across the airports in each family. Everything else is descriptive. (f) Claim airports lead; development airports carry D106.3's flag. Version segments are labelled and descriptive only.
- **D107.10 Latency.** For GFS (`noaa-gfs-bdp-pds`), ECMWF and the NBM grid: the time each cycle's 48 h file was written to the archive, from listing timestamps on spent dates, minus the cycle time, per cycle hour (median and range), labelled "archive write time" (it may be later than public release). For MAV and NBS: the issuance time in the product header where IEM keeps it, otherwise the documented time, labelled as such.
- **D107.11 Live index.** Removed (archived): F155, which is settled. Added: D107 and F156. After session 113: D93, D103, D105, D106, D107, F156.
~~~

Stop if the block is not byte-equal.

### Step 2: Positions, guards and self-checks

Write `scripts/session113_comparison_pull.py` with modes `--check`, `--probe`, `--cost`, `--pull <source>` and `--latency`. Import, read only, from the scripts in Read first; write new code only where no function exists, and say which in the checkpoint.

- Build the airport table from `data/processed/session90_airports.csv` and the pull's positions file (D83.3, F133.3): the 12 airports, IEM position, time zone, `height_diff_m`, and each airport's window (D107.5). Read nothing else from `data/`.
- `--check` (no network): (1) the weights function, applied to the GFS 0.25 degree grid, reproduces every airport's recorded four GFS points and weights exactly (12 of 12); (2) the same function on a made-up regular grid and on a made-up Lambert grid gives weights that sum to 1 and the right corner points; (3) the guards refuse a valid time of 2026-08-01T00:00, a maximum window ending 2026-08-01T00:00 and a climate day ending after 2026-07-31T23:00 UTC, and allow 2026-07-31T23:00 (4 of 4 cases at least); (4) degrees F to C is exact on a few whole values; (5) the cycle lists per airport have the expected counts.

Stop if any check fails.

### Step 3: The probe (`--probe`, D107.4 to D107.6, D107.8)

Read only and small; metadata and counts only. Per source, on spent dates:

- Coverage: present and missing cycles per cycle hour and test year, over each airport's window.
- Steps available within leads 3 to 48; whether all four cycles exist through the window.
- Grid metadata; the 2 m temperature message's size; index-file availability.
- Each maximum field: present or not, its parameter name, step ranges and window (decode a few messages' metadata).
- Any orography or terrain-height field (or a static file the archive documents).
- NBM: whether CYYZ lies inside the CONUS grid; whether the five airports are NBS stations; NBS's projections and TXN windows.
- MAV: cycles, projections and the X element's window.
- Official maximum: each station's IEM CLI identity and GHCN-Daily station id, checked by name and position; days present per test year.
- Version and cycle-change dates inside the windows (archive and documentation, each labelled).

Write `data/processed/session113/probe.csv`. Stop if the IFS or official-maximum probe cannot run at all; for other sources, record the failure and go on.

### Step 4: The cost gate (`--cost`, D107.7)

Measure throughput on at least 50 spent-date messages per gridded source (ECMWF IFS, AIFS, NBM grid), at up to 8 at once. Estimate each source's total requests, bytes and hours for its full window (2 m temperature plus its maximum field and any orography). Print one table. Apply D107.7 mechanically: a source over 250 GB or 24 hours is not pulled and goes to F156 for the owner. Write `data/processed/session113/cost.csv`.

### Step 5: Pull ECMWF IFS (`--pull ifs`)

Only if Step 4 passed it. Per airport and cycle: 2 m temperature at the four points at each step 3 to 48, the maximum field at each step it exists, and terrain heights once per grid (0.4 and 0.25 degrees separately). Checks: rows per airport and cycle hour equal the probe's expected counts minus counted gaps; the latest valid time and the latest maximum window end are on or before 2026-07-31T23:00; 20 random messages re-fetched and re-decoded give identical values; values outside -70 to 60 degrees C counted (stop if more than 0.1 %). Write per-airport gzipped files and a meta file (counts, columns, SHA-256 per file, pull dates, versions).

### Step 6: Pull ECMWF AIFS (`--pull aifs`)

As Step 5, at AIFS's own steps and from its first operational run inside each window.

### Step 7: Pull NBM (`--pull nbs`, then `--pull nbm` if Step 4 passed it)

NBS first: TMP and TXN for each cycle 00, 06, 12, 18 UTC, as issued, at the airports the probe found. Then the grid, if passed: as Step 5 at NBM's steps, with TMAX. Same checks.

### Step 8: Pull MAV (`--pull mav`)

TMP and X for each cycle at DSM, RNO, KSFO and KORD, as issued, with the run and issuance times where IEM gives them. Same checks.

### Step 9: The official maximum (`--pull official`, D107.8)

CLI (IEM) and GHCN-Daily TMAX for the four airports' climate days. Keep both as issued and in degrees C. Report only: days present per source and test year, days with both, and how many of those agree after exact conversion. No comparison with any observation or forecast.

### Step 10: Latency (`--latency`, D107.10)

From listing timestamps (GFS, ECMWF IFS and AIFS, NBM grid) for every cycle in the windows where the listing gives them, and product headers or documentation (MAV, NBS). Write `data/processed/session113/latency.csv`; print medians and ranges per source and cycle hour.

### Step 11: F156

Record F156 (at most about 40 lines, D93.10): D107 recorded; the self-checks; per source the coverage by airport and test year (claim airports first), the cost gate's outcome, the maximum fields found and their windows, and whether terrain heights exist; the official sources' agreement count; the latency table in one line per source; readings for the owner (anything the plan left open that the session had to decide, anything that blocks D107.9 in session 114, such as a missing orography field or a source not pulled); what was not done; pointers to the output file and `data/processed/session113/`.

## End of session

As CLAUDE.md, with:

- STATUS.md overwritten as a current-only snapshot. Its last line: "**Next planning session:** Review session 113 and commit; then plan session 114 (D107.9): the comparisons against ECMWF, NBM and MAV, the official-maximum gap, and the field guide finished. WeatherNext is deferred until the owner's access is granted (D107.4)."
- The archive step with D107.11's Live index, `--citations`, DECISIONS.md's byte size, and the scope-list check against this file's scope.
- The temporary download folder deleted, and that recorded.
- `notes/session-113-output.txt` begins with the summary of at most 30 lines, then the checkpoints and full detail.

Do not commit anything. Stop and wait for review.
