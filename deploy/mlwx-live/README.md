# MLwx-live

A corrected temperature forecast, issued automatically for every new GFS run, with an
append-only record of what was issued.

**Version 1** (GFS only). For each GFS run (00, 06, 12 and 18 UTC) it issues, for 49 airports:

- a corrected 2 m air temperature for every whole hour from 3 to 48 hours ahead (the curve); and
- for each local calendar day that lies wholly inside those hours, the day's maximum, read off the
  curve.

The correction is a model fitted once on GFS version 16 data up to 31 July 2026 and then frozen (no
retraining), plus a running correction for drifting bias that uses only observations already in when
a run starts.

**No accuracy figure is computed or shown here.** Version 1 makes no claim. The test of the live
forecasts is pre-registered in DECISIONS D105.5 in the MLwx repo.

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

If the data cannot be fetched yet (a GFS file not there yet, a network error, or an observation reply
from IEM that is empty or is not the expected table), the GFS run waits. Every later scheduled run
tries it again, and later GFS runs wait behind it so that runs are always issued in time order. Once
a GFS run is 20 hours old, a fetch problem is final: that run issues nothing and later runs go on. A
problem with the data itself (a GRIB message that is not what the code expects) is final at once.

## The observation snapshot

`obs/YYYY/MM/gfs_YYYYMMDDHH.csv`: for each issued run, named like its log file, the observations the
bias trackers looked up for that run. One row per airport and valid time, sorted by airport and valid
time. Written once, after the log file, and never edited. A run with nothing to look up gets a file
with only the header. A problem writing it never blocks or changes the log file; it is shown in the
run's output.

| column | meaning |
|---|---|
| `airport` | ICAO code |
| `valid_utc` | the hour looked up |
| `obs_c` | the observed temperature (deg C) of the routine report nearest that hour within 15 minutes; empty if none |
| `report_utc` | the time of that report; empty if none |

It holds no forecast and no error.

## The page

For each airport the page shows the latest run's raw GFS and corrected curves and the daily maxima.
At 12 airports it also shows a shaded band around the corrected curve, and a range beside each
daily maximum: where the temperature is expected to fall about 8 times in 10, built from the
method's past errors up to 31 July 2026 and then frozen. The ranges are **not yet verified**: they
are being tested on this season's forecasts, by a test written down before any of them was scored.
They are worked out when the page is built and are not in the log, so no logged value changes. If
the ranges file is missing or is not the frozen one, the page shows no range and says so.

## The other folders

- `state/tracker_gfs.json`: where each bias tracker had got to (b, the last valid time applied, the
  count), the runs that issued nothing and why, and the last run's time and status. A cache; the log
  is the record. Committed when anything in it changes besides the last run's time.
- `.gitignore`: files that are never committed, including the temporary files a log or snapshot
  file is first written as (`*.partial`, `*.tmp`).
- `site/` is built by each run and published with GitHub Pages; it is not committed.
- `.github/workflows/live.yml`: the schedule (every hour at 15 and 40 minutes past, UTC; GitHub
  starts scheduled runs late or skips some; a GFS run is used from about 4 hours 10 minutes after it
  starts), plus a manual trigger. Each run checks out the latest `main`. If anything changed besides
  the last run's time in `state/`, the run commits `log/`, `obs/` and `state/`, pushes, and publishes
  the page; otherwise it commits nothing and leaves the page as it was, so the page's build time
  shows the last run that changed something. The job fails if the push did not land on `main` (the
  page is then not published), or if the runner's exit code is anything other than 0 or 2: code 3
  when a GFS run should have issued and did not, and code 1 or any other when the runner itself
  failed. Code 0 means a run was issued or nothing was due; code 2 means a GFS run is still waiting
  for its data and is tried again at the next run. Each run's output also says how many observation
  lookups found no report. The Python packages are cached between runs; the versions are the same.
- `requirements.txt`: the exact Python packages.

## The code

The code is not in this repo. Each run checks out
[MLwx](https://github.com/zadams03/MLwx) (`src/mlwx/`) at one **pinned commit**, named in the workflow
and written in every log row. The reasons for every design choice are in that repo's `DECISIONS.md`
(entry D103) and `SPEC.md` (section 9).

## The models

The frozen models are one file, `gfs-models.tar`, kept as a Release in a **private** repository,
`zadams03/MLwx-models`. The models are the working product, so they are not public; the code, the
record of every decision, the prediction log and the page all stay public. The file is the same one
this repository once held as a public Release: same tag (`gfs-models-49`), same bytes, same SHA-256.

Each run downloads the file with a token kept in this repository's secret `MODELS_TOKEN`. The token
can only read that one private repository's contents and nothing else. If the secret is missing, the
run stops at once with a message saying so. The download is cached between runs, so it happens only
when the cache is empty. After the download the code checks the models against the fingerprint
(SHA-256) of their manifest held in the code; if they do not match, the run fails and issues nothing.
Every log row names that fingerprint in `model_sha256`.

Runs started by a pull request from someone outside need the owner's approval, so no outside
workflow can read the cache.

## GFS version 17

When NOAA starts running GFS version 17, the code keeps going only if every GRIB message still has the
identity the code expects (a check on every message); otherwise that run issues nothing. Rows from
version 17 are marked on the page as not validated: the models were fitted on version 16 data.
