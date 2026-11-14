# MLwx-mosmix

A small saver for DWD's MOSMIX_L station forecasts. It is a template: this folder
lives in the MLwx project, and the owner copies it into a new **private** repository,
`zadams03/MLwx-mosmix`. Nothing here runs until that is done.

## What it saves, and why

MOSMIX is the German weather service's (DWD's) statistical forecast for single weather
stations. DWD's open data server keeps only about the last two days of it (eight issues
of MOSMIX_L), and keeps no archive. So a comparison with MOSMIX later, for airports
outside the United States, is only possible if somebody has kept the files. This saver
keeps them.

- **Which files:** the MOSMIX_L single-station files (`.kmz`) for the stations in
  `stations.csv`, every issue (about four a day, at 03, 09, 15 and 21 UTC), unchanged as
  downloaded. The rolling `LATEST` file is never saved (it is a copy of the newest issue).
- **Each file is checked before it is kept:** it must be a valid zip holding one KML file
  whose issue time and station id equal the ones in the file's name. A file that fails is
  not kept, and the run reports it and fails.
- **Where they go:** each run puts the files of one issue into one uncompressed tar and
  uploads it as an asset of that month's Release (`mosmix-YYYY-MM`), so the git history
  stays small. The list of what was saved, `manifest/YYYY-MM.csv`, is committed.
  Nothing is ever overwritten or deleted, and a station and issue already in the manifest
  is never downloaded again.
- **No test is planned on these files.** No saved value is compared with an observation or
  another forecast until the project's record sets the rules for that comparison.

**How much:** each file is about 9 to 20 KB. The newest issue for all 38 stations, from the
sizes in DWD's listing on 2026-11-14, was 536,581 bytes. At four issues a day that is about
2.1 MB a day and about 0.8 GB a year, a little more in the tars (each tar adds headers and
padding). Each Release asset is far below GitHub's limit for one asset (2 GB).

## The stations

`stations.csv` has 38 rows: `icao`, `station_id`, `distance_km` and `note`. They are every
airport in the live tool's list (`src/mlwx/data/gfs_airports.csv` in the MLwx repository)
that has a MOSMIX station within 10 km. 35 come from the project's 47-airport check
(`data/processed/session90_airports.csv`, the rows with `mosmix_within_10km` = yes whose airport
is in the live list), and three (LFPG 07157, KDSM 72546 and KRNO 72488) from the project's
first station check. YSDU has no station within 10 km, so it is not here. For EGLC, DWD
places the station about 7.7 km away, but its longitude may have the wrong sign, in which case it
is about 2.5 km away; the note says so. A test in the MLwx repository checks the list against
both sources.

## The files

- `saver.py`: the saver, Python standard library only. It prints only names, sizes, SHA-256
  checksums, issue times and station ids, never a forecast value.
  - `python saver.py --list` prints, for each station, the issues on the server, newest first.
  - `python saver.py --save out --manifest-dir manifest` saves what the manifest does not hold.
  - `python saver.py --check-fresh --manifest-dir manifest` fails if the newest issue held is
    more than 12 hours older than the newest issue on the server. It also fails if any one
    station's newest issue held is more than 12 hours older than that, so a station that stops
    getting new files is noticed even while the others keep coming.
  - `--only EGLC,LFPG` limits any mode to some airports; `--newest 2` limits `--save` to each
    station's newest two issues (both are for trials).
  - A request that fails is tried three times, with a longer wait each time. Any failure makes
    the exit code non-zero.
- `stations.csv`: the list above.
- `.github/workflows/save.yml`: runs the saver every three hours at 50 minutes past (UTC) and by
  hand. It saves, uploads each new tar to the month's Release (an upload never replaces an
  asset), and only then commits the manifest, so a manifest row never points to an asset that
  is not there. If a push is rejected it rebases once and tries again. It then runs the
  freshness check. **The run fails, and GitHub tells you,** if a download, a check, an
  upload or a push fails, or if the freshness rule fails. A run can be missed for about 40
  hours before anything is lost, because DWD holds about eight issues.
- `.gitignore`: keeps the tars and the download folder out of the history.

## Setting it up

1. Create a private repository `zadams03/MLwx-mosmix` (empty, branch `main`).
2. Copy this folder's files into it: `saver.py`, `stations.csv`, `README.md`, `.gitignore` and
   `.github/workflows/save.yml`. Commit and push to `main`.
3. In the repository's Settings, Actions, General, Workflow permissions: choose **Read and
   write permissions**. (The workflow also asks for `contents: write` itself.)
4. In the Actions tab, run **save** once by hand ("Run workflow"). Check that it is green, that
   a Release `mosmix-YYYY-MM` appeared with tar assets, and that `manifest/` was committed.
5. Leave it running. If GitHub emails you a failed run, look at the run's log: it names the
   station and issue that failed and why.
6. After about a week, open the Actions tab and read the list of runs. GitHub does not always
   start scheduled runs on time, and it sends no message when it starts none at all. If the gaps
   between runs come near 24 hours, look again: DWD keeps about 40 hours of issues, so a longer
   gap loses files.

## Getting files back

Each tar holds one issue's files, named as DWD names them. To fetch one:

```
gh release download mosmix-2026-11 --repo zadams03/MLwx-mosmix --pattern 'MOSMIX_L_2026111409_*.tar'
tar -xf MOSMIX_L_2026111409_run*.tar
```

`manifest/YYYY-MM.csv` has one row per saved file: `station`, `icao`, `issue`, `url`, `bytes`,
`sha256`, `saved_utc`, `asset` (the tar's name) and `run_id`. The `sha256` is of the `.kmz` file
exactly as it was downloaded.

A tar in a Release with no row in the manifest is a leftover of a run that failed part-way: its
upload worked, but the run stopped before the manifest was committed. Nothing is lost or
overwritten. The next run downloads those issues again (if DWD still has them), uploads them in
a tar named with its own run id, and records that tar. Use the tars the manifest names.

## DWD's terms and credit

Read on 2026-11-14, on DWD's English "Legal notice" page
(`https://www.dwd.de/EN/service/legal_notice/legal_notice_node.html`). In plain words:
DWD's open spatial data, meaning any location-related weather and climate information it
offers for access, may be re-used under the Creative Commons licence **CC BY 4.0**, as long
as DWD is acknowledged as the source. Nothing on the page forbids keeping copies. The page
does not name MOSMIX; I take MOSMIX to be covered as location-related weather information
on DWD's open data server, and that reading has not been confirmed with DWD. Rules for the
form of the credit are on a DWD page the Legal notice links to, which was not read. So: any
published use of these files or of values from them should say that the source is Deutscher
Wetterdienst (DWD), MOSMIX, and that it is licensed CC BY 4.0, and should say what was
changed. The repository is private, so nothing is redistributed by keeping the files.
