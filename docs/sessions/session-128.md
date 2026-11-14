# Session 128: the MOSMIX saver

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
This session builds a small, self-contained saver for DWD's MOSMIX_L
station forecasts (D81), as a template for a new private repository,
with offline tests and one real dry run. It deploys nothing: the owner
creates the repository and copies the template after review. No model,
data file, logged value or live file changes. No 2026-27 value is read
or scored, and no MOSMIX value is compared with anything.

## Read first

- STATUS.md in full; SPEC section 2; the live DECISIONS.md in full.
- Archived, one entry at a time by line range: D80.5, D81 (all), F130.2
  to F130.4, F132.5.
- `deploy/mlwx-live/.github/workflows/live.yml`, `deploy/mlwx-live/README.md`
  and `tests/test_live_template.py`: the pattern to follow for a template
  and its tests. Read only.
- `data/processed/session90_airports.csv` (columns `icao`,
  `mosmix_station_id`, `mosmix_distance_km`, `mosmix_within_10km`,
  `mosmix_lon_sign_flag` only) and `src/mlwx/data/gfs_airports.csv`
  (column `icao` only).

## Rules for this session

- Network: only `https://opendata.dwd.de/weather/local_forecasts/mos/MOSMIX_L/`,
  for listings and the files of Step 4's dry run. Nothing else.
- Downloaded files go only into a `mktemp -d` folder outside the repo and
  are deleted at the end of Step 4. No MOSMIX file is committed to this
  repository. No forecast value is printed, written to a file or compared
  with an observation or another forecast; only metadata (names, sizes,
  SHA-256, issue times, station ids) is reported.
- The saver uses the Python standard library only.
- No existing script, test, data file, figure, model, `src/` or
  `deploy/mlwx-live/` file is edited.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md, README.md (one row in the
repository map only), deploy/mlwx-mosmix/ (new folder: `saver.py`,
`stations.csv`, `README.md`, `.gitignore`, `.github/workflows/save.yml`),
tests/test_mosmix_saver.py (new), notes/session-128-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `9141ec3`; the tree is clean apart from
this prompt. Tests (`.venv/bin/python -m unittest discover -s tests`):
206 OK. SPEC 3.4's span has SHA-256
`a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
`deploy/mlwx-mosmix/` does not exist. Stop if any check fails.

**Step 2. Record D122.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-14: Session 128 decision: F170 accepted, the session order for the next days, and the MOSMIX saver's design (owner, planning chat)

**D122. Owner decisions, planning chat (after session 127's commit): F170 accepted; the order of the next sessions (amends D121.2's numbering only); and the MOSMIX saver's design (D81.4, D81.5), fixed before it is built; and Live index changes.** Written at the start of session 128, before any other edit or network call. No 2026-27 value has been read or scored.

- **D122.1 F170 accepted,** with its readings. The tests README's missing line for the new test file is fixed in a later session.
- **D122.2 Session order (D121.2's content unchanged).** 128: the MOSMIX saver. 129: the live test's scoring script (D105.5(l)), written and gated on spent data and synthetic logs and committed before any observation valid on or after 2026-10-12 is read, together with session 86's gate wrapper (D118.10). 130: an independent, read-only code review of the live tool (`src/mlwx/`, the workflow template), stage B's scoring path and session 129's script, as a findings register. 131: fixes from that register, Gates C and D (F154.9(4)), the iem-position rows for AIFS and the NBM grid at the development airports, and D115.6's question, each with its rules fixed in that session's entry first. 132: stage H's design and build choices. A GFS v17 Service Change Notice goes ahead of any of these.
- **D122.3 Stations (widens D81.2).** Every live airport (`src/mlwx/data/gfs_airports.csv`) with a MOSMIX station within 10 km: the 35 in `data/processed/session90_airports.csv` (`mosmix_within_10km` = yes; MMMX and VILK are not live) and LFPG 07157, KDSM 72546 and KRNO 72488 (F130.4); 38 stations. YSDU has none (D81.3). EGLC's station keeps D81.6's position note. The list is held in the template's `stations.csv` and checked by a test against those two sources.
- **D122.4 What is saved.** MOSMIX_L single-station files (`.kmz`), every issue, unchanged as downloaded (D81.2). The rolling `LATEST` file is never saved. Each file is checked before it is kept: a valid zip holding one KML whose issue time and station id equal the file name's; a file that fails is not kept, and is reported.
- **D122.5 Where and how (D81.4).** A private repository, `zadams03/MLwx-mosmix`, run by GitHub Actions. Each run lists each station's directory and downloads every issue the manifest does not yet hold. The files saved by one run for one issue go into one uncompressed tar, uploaded as an asset to that month's Release (`mosmix-YYYY-MM`), so the git history stays small; the manifest (`manifest/YYYY-MM.csv`: station, icao, issue, url, bytes, sha256, saved_utc, asset, run_id) is committed. Nothing is ever overwritten or deleted. A station and issue already in the manifest is never downloaded again.
- **D122.6 Schedule and failure.** Every three hours at 50 minutes past (UTC), and by hand. With about eight issues on DWD's server (F130.2), a run can be missed for about 40 hours before anything is lost. A run fails (so the owner is told by GitHub) if a download, check, upload or push fails, or if the newest issue held is more than 12 hours older than the newest issue listed.
- **D122.7 Use.** No MOSMIX test is pre-registered (D81.5). No saved value is compared with an observation or a forecast until an entry sets the rules for that comparison.
- **D122.8 Live index.** Removed (archived): D121 and F170, which are settled (D121.2 to D121.6 are carried by D122.2, STATUS and the documents). Added: D122 and F171 (F171 when it is written). After session 128: D93, D103, D105, D118, D122, F171.
```

**Step 3. The template.** Write `deploy/mlwx-mosmix/`:
- `stations.csv`: `icao,station_id,distance_km,note`, 38 rows sorted by
  ICAO, built from the two sources of D122.3 (note EGLC's
  `mosmix_lon_sign_flag`). Check: 38 rows, 38 distinct station ids.
- `saver.py`, standard library only, modes:
  `--list` (print, per station, the issues on the server, newest first),
  `--save OUTDIR --manifest-dir DIR` (download every issue not in the
  manifest into OUTDIR, check each file by D122.4, tar per issue, write
  new manifest rows with `asset` set to the tar's name), and
  `--check-fresh` (D122.6's 12-hour rule). It parses DWD's directory
  listing for names of the form `MOSMIX_L_YYYYMMDDHH_<station>.kmz`
  (confirm the exact form in Step 4 and match it), retries a failed
  request three times with a back-off, never overwrites a file and
  exits non-zero on any failure. It prints only metadata.
- `.github/workflows/save.yml`: D122.6's schedule plus
  `workflow_dispatch`; `permissions: contents: write`; current major
  versions of the actions, Python 3.12 (as the live template); steps:
  check out, run `--save`, create the month's Release if missing and
  upload each new tar with `gh release upload` (never `--clobber`),
  then commit and push the manifest only if it changed (rebase once on
  a rejected push; fail if it still does not land), then
  `--check-fresh`. Upload before commit, so a manifest row never points
  to an asset that is not there.
- `README.md`: plain words: what is saved and why (a future comparison
  outside the US; DWD keeps about two days), the station list's source,
  how to set up the repository (create it private, copy these files,
  allow Actions to write, run once by hand), how to get files back
  (`gh release download`), DWD's terms and credit (read the terms page
  once, network allowed for that one page; quote the conditions in
  plain words with the date read; if they forbid keeping copies, stop
  and report before Step 4).
- `.gitignore`: the tar and download folders.

**Step 4. One real dry run.** Into a `mktemp -d` folder, with an empty
manifest folder: `--list` for all 38 stations (report the issue count
per station and any station with no directory or no issues); then
`--save` for three stations only (LFPG, EDDM, KORD) and the newest two
issues. Report each file's name, bytes and SHA-256, the checks of D122.4
for each, the tars' names and sizes, and the manifest rows. Then run
`--save` again: it downloads nothing. Then `--check-fresh` on that
manifest. Report the measured bytes per file and an estimate of bytes
per day and per year for 38 stations and four issues a day. Delete the
folder. Stop if any station's directory is missing; report it and do not
change the list.

**Step 5. Tests.** `tests/test_mosmix_saver.py`, offline only, with small
synthetic `.kmz` files built in a temporary folder and a fake listing:
the listing parser (real-form names, `LATEST` ignored, other names
ignored); each D122.4 check rejects a bad zip, a missing KML, a
mismatched issue time and a mismatched station id; nothing in the
manifest is downloaded again; no file is overwritten; the 12-hour rule;
`stations.csv` equals D122.3's two sources exactly; the workflow parses
as YAML (if a parser is already installed; otherwise check by text),
has the cron `50 */3 * * *`, `workflow_dispatch`, `contents: write`, no
`--clobber`, and the upload step before the commit step. All tests pass.

**Step 6. README.md.** One row in the repository map for
`deploy/mlwx-mosmix/`, in plain words, no D or F number in the row.

**Step 7. Final checks.** Tests: 206 plus the new ones, all OK. SPEC.md
unchanged; 3.4's span hash unchanged. No file outside the scope list
changed (`git status --porcelain`). 0 em-dashes in added lines and new
files. No `.kmz` or `.tar` file anywhere in the repository.

## End of session (CLAUDE.md)

1. **F171**, at most about 40 lines: the template's files and SHA-256,
   the station list, the dry run's results and size estimate, DWD's terms
   as read, the tests, every check with PASS or FAIL, readings for the
   owner, what was not done, pointer to `notes/session-128-output.txt`.
2. **Overwrite STATUS.md** as a current snapshot: the saver is built and
   waits for the owner to create `zadams03/MLwx-mosmix` and copy the
   template (D122.5); the order of D122.2. End with: `**Next planning
   session:** Review session 128 and commit; the owner deploys the
   MOSMIX saver; the planning chat syncs Project knowledge (D118.8);
   then session 129 (D122.2).`
3. **Archive step:** make D122.8's index changes, add F171, then
   `python3 scripts/archive_decisions.py --apply --session 128`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a summary of at most 30 lines; report the
   same summary in chat. Then stop and wait for review. Do not commit.
