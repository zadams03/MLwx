# MLwx-live

A corrected temperature forecast, issued automatically for every new GFS run, with an
append-only record of what was issued.

**Version 1** (GFS only). For each GFS run (00, 06, 12 and 18 UTC) it issues, for 12 airports:

- a corrected 2 m air temperature for every whole hour from 3 to 48 hours ahead (the curve); and
- for each local calendar day that lies wholly inside those hours, the day's maximum, read off the
  curve.

The correction is a model fitted once on GFS version 16 data up to 31 July 2026 and then frozen (no
retraining), plus a running correction for drifting bias that uses only observations already in when
a run starts.

**No accuracy figure is computed or shown here.** Version 1 makes no claim. A test of the live
forecasts will be written down in advance before anything is scored.

## The prediction log

`log/YYYY/MM/gfs_YYYYMMDDHH.csv`: one file per GFS run, for all airports, written once.
**A file in `log/` is never edited.** A correction would be a new file. The git history is the proof:
every file is added in a commit made by the automated run, with the time it was issued in the file.

| column | meaning |
|---|---|
| `airport` | ICAO code |
| `cycle_utc` | start time of the GFS run |
| `lead` | hours ahead (3 to 48) |
| `valid_utc` | the hour being forecast (`cycle_utc` + `lead`) |
| `raw_gfs` | GFS's 2 m temperature at the airport, adjusted for the height difference between the model grid and the airport |
| `baseline` | the frozen model's forecast |
| `b` | the running bias correction at that moment (0 until errors arrive) |
| `corrected` | `baseline` + `b`: the forecast |
| `gfs_version` | GFS version of the run (v16 until the first v17 run is recorded) |
| `model_sha256` | SHA-256 of the manifest of the frozen models used |
| `code_commit` | the commit of the MLwx code that made the row |
| `issued_utc` | when the row was made |

If anything is wrong with a run's data, that run issues **nothing**: there is no file for it, and the
page says so. Nothing is ever filled in.

## The other folders

- `state/tracker_gfs.json`: where each bias tracker had got to (b, the last valid time applied, the
  count). A cache; the log is the record. Updated each run.
- `site/` is built by each run and published with GitHub Pages; it is not committed.
- `.github/workflows/live.yml`: the schedule (about 4 hours 10 minutes after each run starts), plus a
  manual trigger.
- `requirements.txt`: the exact Python packages.

## The code

The code is not in this repo. Each run checks out
[MLwx](https://github.com/zadams03/MLwx) (`src/mlwx/`) at one **pinned commit**, named in the workflow
and written in every log row. The reasons for every design choice are in that repo's `DECISIONS.md`
(entry D103) and `SPEC.md` (section 9).

## GFS version 17

When NOAA starts running GFS version 17, the code keeps going only if every GRIB message still has the
identity the code expects (a check on every message); otherwise that run issues nothing. Rows from
version 17 are marked on the page as not validated: the models were fitted on version 16 data.
