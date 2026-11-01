# Session 124: fix groups (7) the record text and (9) the data credits

Planning chat, 1 November 2026. One session (D117.2). Recommended model: Opus
(the terms reading needs judgment; the rest is careful text editing).

## Read first

- STATUS.md and SPEC section 2 (always).
- The live DECISIONS.md in full (this session records an entry).
- `docs/PROJECT-INSTRUCTIONS.md` in full (this session edits it).
- Only the parts each step edits: SPEC section 1 (l.29 to 60), section 6
  (l.725 to 800) and 9.6; RESULTS.md l.1 to 30 and section 7's roadmap
  bullet (about l.850 to 890); README.md section 9 (l.325 to 379); the
  first 14 lines of DECISIONS-archive.md.
- Register rows, by id, from `notes/session-121-register.csv` (SP04 to
  SP11, ST02, ST10, ST11, RE01 to RE05, RM05, CL03 to CL07, PI01 to PI12,
  PK09 to PK11, DE03) and `notes/session-120-register.csv` (S06). Read
  only those rows.
- Archived entries only if a step needs to check a citation (D82.2,
  D106.14, D107.2, D98.2, D70.6, D80.1), one entry at a time (CLAUDE.md).

## Limits

- No 2026-27 value is read or scored. No MLwx-live file, model, GRIB cache
  or frozen script is touched. Nothing under `src/`, `scripts/`, `tests/`
  or `data/` changes. No logged value changes, so D105.5(k) is not
  engaged.
- Network: read-only fetches of each data source's terms pages (Step 2)
  only. No `gh`, no push, no workflow.
- No em-dash in any new text (D76.6). Existing text keeps its em-dashes:
  where a step replaces part of a line that holds one, keep that part.
- SPEC 3.4's span (S05, D115.4) must stay byte-equal: SHA-256
  `a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`,
  2,050 bytes, found by its two markers. Its line numbers will move
  because section 1 grows; record the new ones.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md, SPEC.md, RESULTS.md,
CLAUDE.md, `docs/PROJECT-INSTRUCTIONS.md`, README.md (section 9 only),
`notes/session-124-output.txt`. This prompt file is already present,
untracked.

## Steps

### Step 0. Start checks

HEAD is bc70489 and the tree is clean apart from this file. Run
`.venv/bin/python -m unittest discover -s tests`: 195 OK. Record the byte
sizes of the eight record files (SPEC, STATUS, DECISIONS, the archive,
RESULTS, ANALYSIS, CLAUDE, `docs/PROJECT-INSTRUCTIONS.md`). Find SPEC
3.4's span by its two markers and check its SHA-256 and size as above.
Stop if any check fails.

### Step 1. Record D118

Append the block between the two marker lines below (the markers
themselves not included) to the end of DECISIONS.md, with `sed`, preceded
by the usual `---` separator as earlier entries are. Check it byte-equal
with `diff` and `cmp` against this file's block, and count em-dashes in
it (expect 0). Stop if either fails.

<!-- D118-start -->
## 2026-11-01: Session 124 decision: F166 accepted, the redeploy, rulings for fix groups 7 and 9, the scheduler closed, and the Project-knowledge sync (owner, planning chat)

**D118. Owner decisions, planning chat (after session 123's commit and the owner's redeploy): F166 accepted; the redeploy recorded; a planning-chat check of the runs since; the outside scheduler closed for v1; the rulings that fix groups (7) and (9) need (SP05, SP07, SP08, PI07 with PK10, DE03, S06); the Project-knowledge sync returned to the planning chat; session 124's scope; and Live index changes.** Written at the start of session 124, before any other edit. No 2026-27 value has been read or scored.

- **D118.1 F166 accepted,** with its readings (F166.8).
- **D118.2 The redeploy (D117.7; owner, by hand, 2026-10-27).** MLwx-live commit `628df88` copies the template of `bc70489` (session 123's commit). `MLWX_COMMIT` `d6ca3e4e9bd79d55ffbdfd1cc7a9a5d6e21747bb` and `MODELS_TAG` `gfs-models-49`, both unchanged. A manual check run at about 17:59Z was green: it issued 2026-10-27 12z (MLwx-live commit `d39e1fc`), its skip step printed "3 changed path(s): commit, push and publish", and it showed no Node.js 20 warning. D105.9 holds again: the template matches the deployed workflow apart from the two `SET-AT-DEPLOY` values. D112.8's rule on manual runs (none between :35 and :55 past the hour) stays as standing practice.
- **D118.3 Planning-chat check of the runs since (2026-11-01, a fresh clone of MLwx-live; no run log read, no error computed, D105.6).** 19 commits after `628df88`. Every cycle from 2026-10-27 12z to 2026-11-01 00z is logged, none missing. No commit after the redeploy changed only `state/`; before it, 14 of 41 did (F166.3). So the skip appears to work; no run log confirms it. The 2026-11-01 00z cycle was issued at 09:24Z, a lag of about 9.4 h, above F166.2's maximum of 9.20 h.
- **D118.4 The outside scheduler (D112.6(d), D117.4; owner): closed for v1.** None is built. Why: no cycle has come near the 24-hour loss limit (D112.4); late issues are counted by the live test, never excluded (D105.5(h)); and an outside trigger would need a token secret in MLwx-live. It is reopened, by a new entry, only if any cycle's issue lag exceeds 12 h.
- **D118.5 The end goal's wording (SP05, ST02, RM02; owner).** "Private" is dropped. The goal is a live tool for ten or more airports that corrects every GFS run into an hourly curve to 48 hours ahead, plus the daily maximum; version 1 is live and public (D103.9). D82.2's words stand as history. SPEC section 1 and STATUS change in session 124; README line 19 changes in the README update (group 6).
- **D118.6 Stage G in SPEC (SP07, with SP06 and SP11; owner).** No SPEC section for stage G. Section 6's closing note says its design stays in DECISIONS (D103, D105, D112.6, D117). Stage G's bullet gets status sentences, and stage B's names the live test (D105.5) beside D73.
- **D118.7 A pointer to ANALYSIS.md (SP08; owner).** One bullet in SPEC section 6, after stage A: descriptive analysis on spent data, never a source of rules or claims (D107.2).
- **D118.8 Project knowledge (PI07, PK10; owner; amends D115.2, restores D93.15(b) by a new route).** After the owner commits and pushes a reviewed session, the planning chat clones the public MLwx repo fresh from GitHub into its cloud workspace, checks that its HEAD is the pushed commit, and writes each changed file with project_write's `local_path`, so no content enters the chat (tested 2026-11-01: STATUS.md written this way, Project size unchanged). Every file sits at the root under its own name, the archive included (D115.3); ANALYSIS.md is on the list. If a write fails, the planning chat lists the files with their repo byte sizes and the owner uploads by hand (D115.2's route as the fallback). The size rule reads `knowledge_size` and `max_knowledge_size` from project_info, which share one unit that is not bytes (probably tokens, unconfirmed): on 2026-11-01, 668,149 of 2,000,000 for 1,929,457 repo bytes. Above 80 % of the maximum (1,600,000) is an ACTION NEEDED item. Repo byte totals are not used for the rule.
- **D118.9 The archive's order (DE03; owner).** DECISIONS-archive.md's header gets one line saying blocks are in the order they left the live file, not date order (D93.8). The header is not an entry.
- **D118.10 Session 86's gate (S06; owner): deferred.** Nothing is done now. If stage B needs `session86_forward_build.py --gate` before period A is scored, the session that prepares stage B's run builds a wrapper that swaps its DECISIONS lookup at run time for constants checked by a test, as D116.3 did; the frozen script is not edited.
- **D118.11 The planning chat's repo access (PI02).** The Filesystem extension no longer points at the repo. The planning chat asks for access to `~/Coding Projects/MLwx-all` through the linked computer, writes only into `docs/sessions/` and `docs/commits/`, and reads `notes/` only in a review, by the lines it needs.
- **D118.12 Data credits (RM05; group 9).** Session 124 reads each committed source's terms over the network, read-only, and credits each in README section 9 only. If any terms forbid redistributing the committed values in a public repo, the session stops before editing section 9; the owner rules. Any other condition (attribution, non-commercial use) is stated in the credit.
- **D118.13 Session 124's scope.** D118.5 to D118.9 and D118.11 to D118.12, and group (7)'s rows needing no ruling: SPEC SP04, SP06, SP10, SP11; RESULTS RE01, RE02, RE04, RE05; CLAUDE CL03, CL04, CL05 (D116.2's test command), CL07, and D116.10's rule; PROJECT-INSTRUCTIONS PI01, PI02, PI04 to PI08, PI12, PK09 to PK11; STATUS ST02, ST10, ST11 at its overwrite. Not in scope: groups (4) and (6) (the rest of README). No logged value, model, live file or frozen script changes, so D105.5(k) is not engaged.
- **D118.14 Live index.** Removed (archived): D112, D116, D117, F165 and F166, which are settled (D112.8's rule is carried by D118.2; D116.10's by CLAUDE.md and STATUS). Added: D118 and F167 (F167 when it is written). After session 124: D93, D103, D105, D114, D115, D118, F163, F164, F167.
<!-- D118-end -->

### Step 2. Data credits: the terms (D118.12; network)

(a) Inventory. List every committed file under `data/` whose values come
from ECMWF IFS or AIFS, the NBM grid, NBS, MAV, NWS CLI reports or
GHCN-Daily: `data/processed/session113/` (read its six `*_meta.txt`
files for each source's origin and fetch route) and any other committed
file the meta files or `git log` show is built from them (for example
session 117's IFS outputs, session 85's NBM and MAV). Record per source:
files, total bytes, how it was fetched (host or API), and for GHCN-Daily
and CLI which stations.

(b) Terms. For each source, fetch its own terms page read-only and record:
URL, date read, the licence or terms in at most two short quotes, whether
redistribution of derived values in a public repo is allowed, and the
credit wording asked for. Start from: ECMWF open data,
https://www.ecmwf.int/en/forecasts/datasets/open-data (follow its licence
link; also the AIFS dataset page
https://www.ecmwf.int/en/forecasts/datasets/aifs-machine-learning-data);
NBM, https://registry.opendata.aws/noaa-nbm; IEM,
https://mesonet.agron.iastate.edu/disclaimer.php (covers NBS, MAV and CLI
as fetched through IEM; also check the NWS's own page for its products,
https://www.weather.gov/disclaimer); GHCN-Daily, NCEI's metadata page
https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C00861/html
and the GHCN-Daily readme's use notes (including any note on data
exchanged under WMO Resolution 40, checked against the stations in (a)).
If a page cannot be fetched, record that; do not use a mirror.

Check: every source in (a) has a terms row. Stop (before Step 3) if any
terms forbid redistributing the committed values, and report.

### Step 3. README section 9 (RM05)

Edit section 9 only. (a) The opening sentence's dates: add that the terms
of the sources added here were read on the Step 2 date (D118.12). (b)
Extend the NBM bullet to name `data/processed/session113/`'s NBM grid
files. (c) Replace the MAV bullet's "Their own terms were not fetched"
with the terms read in Step 2, and name the session 113 MAV files. (d) Add
one bullet each, in the style of the existing ones (what it supplied,
where it is committed, the terms in plain words, the page URL, the credit
line asked for): ECMWF IFS and AIFS open data; NWS NBS through IEM; NWS
CLI reports through IEM; GHCN-Daily (NOAA NCEI). (e) In the "Probed only"
bullet, remove ECMWF IFS and AIFS; keep the rest. Nothing else in README
changes.

Check: `git diff --stat README.md` touches only lines inside section 9;
0 new em-dashes.

### Step 4. SPEC (SP04, SP05, SP06, SP07, SP08, SP10, SP11; D118.5 to D118.7)

Use this text, adjusted only to fit the line wrapping.

(a) SP04. After the KSFO bullet and before "**The list is open-ended",
add a paragraph: "Stage C's claim was run at six further airports: Munich
(EDDM), Chicago O'Hare (KORD), Toronto Pearson (CYYZ), Shenzhen (ZGSZ),
Chongqing (ZUCK) and Wellington (NZWN) (section 9.5; DECISIONS D100,
F150). The live product (stage G) runs at 49 airports (DECISIONS D103.4,
D105.2)." Check each airport name against SPEC 9.5 or DECISIONS before
writing; stop if any differs.

(b) SP05. Replace the paragraph from "The end goal is a private, live
tool" to "roadmap." with: "The end goal is a live tool for ten or more
airports that corrects every GFS run (four a day), as each run arrives,
into an hourly temperature curve out to 48 hours ahead, plus the daily
maximum. Then come a choice of which weather model is corrected, plus a
blend, and probabilistic ranges (DECISIONS D72.1, reworded by D82.2 and
D118.5). Version 1 is live and public (DECISIONS D103.9, D105.2). That is
the destination, not the starting point. See section 6 for the roadmap."

(c) SP08. After the stage A bullet, add: "- **Descriptive analysis on
spent data.** Comparisons with other forecasts, and a field guide to the
current models, on spent data only, are in `ANALYSIS.md` (DECISIONS D106
to D113). It is descriptive: never a source of rules or claims
(DECISIONS D107.2, D118.7)."

(d) SP11. At the end of the stage B bullet, add: "A second test on
2026-27 data, of stage G's live forecasts as issued, is pre-registered
separately in DECISIONS D105.5; neither test's result changes the
other."

(e) SP06. Keep the stage G bullet's heading "**Stage G — live product,
version 1.**" unchanged and replace its body with: "For every GFS cycle
(four a day), a corrected hourly curve at leads 3 to 48 and each local
day's maximum, a prediction log that is never edited, a simple page, and
one-script airport onboarding, on GFS only, with the weather model as a
setting; its design includes how it handles GFS v17 (DECISIONS D102.4,
D103). It is live at 49 airports, in the public repository
zadams03/MLwx-live (DECISIONS D103.9, D105.2). Its forecasts are under
the test of DECISIONS D105.5; no accuracy figure is computed or shown
before its look (DECISIONS D103.2, D105.6). Stages D, E, F and H follow
it, with their scope unchanged (DECISIONS D102.4)."

(f) SP07. In the closing note, replace "the others will not until the
owner opens them." with "stage G has none: its design stays in DECISIONS
(D103, D105, D112.6, D117; DECISIONS D118.6). The others will not have one
until the owner opens them." Fix the sentence break so it reads cleanly
(a full stop after "(DECISIONS D82.5, D100)").

(g) SP10. In 9.6, "GFS v17 is stage B's and stage F's question." becomes
"GFS v17 is stage B's and stage F's question, and stage G's (DECISIONS
D103.10)."

Check: SPEC 3.4's span by its markers: SHA-256 and 2,050 bytes unchanged;
record its new first and last line. Stage B's three `--guard-check` modes
pass (as F164.4). 0 new em-dashes. Stop if any fails.

### Step 5. RESULTS (RE01, RE02, RE04, RE05)

(a) RE04. The header's revision sentence becomes "Written after session
30, revised after sessions 44, 65, 79, 80, 84, 101, 104, 106, 108 and
124." The footer adds "after session 84" in its place in the list (cite
an entry only if session 84's commit message names one) and ends the list
with "and after session 124 (DECISIONS D118)".

(b) RE05. In the opening, after the KSFO sentences ("...see section
6.5."), add: "Stage C's hourly curve and daily maximum, from every GFS
run, have since passed their pre-registered claim at six new airports in
both held-out years (DECISIONS F150; section 7)."

(c) RE02. In section 7's roadmap bullet, replace "plus the daily maximum,
at 51 airports. Its GFS archive pull to 24 hours ahead is complete," with
"plus the daily maximum. Its GFS archive pull covers 51 airports
(DECISIONS D83.2) and is complete to 24 hours ahead,". Check D83.2 says
51 before writing.

(d) RE01. Replace "Stage G, the live tool on GFS, comes next; stages D,
E, F and H (other weather models, blending, upgrade policy and
probabilistic ranges) follow it (DECISIONS D102.4); pooling is
conditional." with "Stage G, the live tool on GFS, is live: version 1 has
corrected every GFS run since 2026-10-12, at 49 airports since
2026-10-13, with a public log and page (DECISIONS D103, D105.2). A test
of its forecasts as issued is pre-registered (DECISIONS D105.5); no
accuracy figure is computed or shown before its look (DECISIONS D103.2,
D105.6). Stages D, E, F and H (other weather models, blending, upgrade
policy and probabilistic ranges) follow it (DECISIONS D102.4); pooling is
conditional." Check both dates against D103 and D105.2/D105.3 first.

Check: 0 new em-dashes; no number elsewhere in RESULTS changed.

### Step 6. CLAUDE.md (CL03, CL04, CL05, CL07; D116.10)

(a) CL07. Under "Read on demand only", after the RESULTS.md bullet, add:
"- **ANALYSIS.md**: the descriptive analysis on spent data (D106.14). Never
a source of truth or of rules."

(b) CL03. "Frozen scripts are never edited (D62.3(a), restated in D93.8)."
becomes "Frozen scripts are never edited (D62.3(a), restated in D93.8;
also D70.6 and D80.1). `tests/test_frozen_scripts.py` checks their SHA-256
(D116.4)."

(c) D116.10 and CL04. Add two bullets after it: "- A script whose SHA-256
is recorded by another script, a test or a data file's meta file is not
edited; a fix goes in a new script that imports it (D116.10)." and "- A
script never finds a recorded value by searching DECISIONS text; it holds
it as a constant checked by a test (D98.2)."

(d) CL05. In "End of every session", step 1, add: "Run the tests with
`.venv/bin/python -m unittest discover -s tests` (D116.2) and give the
count."

Check: each cited entry exists; 0 new em-dashes.

### Step 7. PROJECT-INSTRUCTIONS (PI01, PI02, PI04 to PI08, PI12, PK09 to PK11; D118.8, D118.11)

(a) PI01. Section 2's table: add after the RESULTS row: "| `ANALYSIS.md` |
Descriptive analysis on spent data: field guide, comparisons, candidates
| Read only when needed. Never a source of rules (D107.2). |"

(b) PI02. Section 4 step 1: replace the sentences from "**Deliver it
straight into the repo:**" to "fall back to a downloadable file." with:
"**Deliver it straight into the repo:** the planning chat asks for access
to `~/Coding Projects/MLwx-all` through the linked computer and writes
with its shell (D118.11). It writes only into docs/sessions/ and
docs/commits/ (section 1), after checking that no file of that name
exists. Reading a file this way puts its contents into the chat, so it
reads only the lines it needs. If the computer is not linked, fall back to
a downloadable file."

(c) PI04 to PI07, PK09 to PK11. Replace section 5's body (from "After
Zac has committed" to the end of its "Size" bullet) with:

"After Zac has committed and pushed a reviewed session, **the planning
chat copies every changed file into Project knowledge itself** (D93.15(b),
D118.8). Never sync before the push: Project knowledge must match the
committed repo.

- **Which files:** `STATUS.md` every session; `DECISIONS.md` and
  `DECISIONS-archive.md` whenever they changed (almost every session);
  `SPEC.md`, `RESULTS.md`, `ANALYSIS.md`, `CLAUDE.md` and
  `docs/PROJECT-INSTRUCTIONS.md` (kept as `PROJECT-INSTRUCTIONS.md`) only
  when the session changed them. Every file sits at Project knowledge's
  root under its own name, the archive included (D115.3).
- **How:** clone the public MLwx repo fresh from GitHub into the chat's
  cloud workspace, check that its HEAD is the pushed commit, copy each
  file into the working directory, and write it with project_write's
  `local_path` to the same path, so its contents never enter the chat.
- **If it fails** (no network, or a write refused): say so plainly and
  give Zac the files to upload by hand, each with its byte size in the
  repo, for example *\"Upload to Project knowledge: STATUS.md (7,683
  bytes).\"* Zac checks each size after uploading (D115.2).
- **Size:** after the sync, read `knowledge_size` and
  `max_knowledge_size` from project_info and report both. They share the
  Project's own unit, which is not bytes (probably tokens, unconfirmed;
  D115.5, D118.8). Above 80 % of the maximum (1,600,000 of 2,000,000) is
  an ACTION NEEDED item. Repo byte totals are not used for this rule."

(The backslashes above mark quotes inside this prompt's quote; write
plain quote marks.)

(d) PI08. With (c), section 3 step 2, section 4 step 5 and the closing
line already match D118.8 (the planning chat syncs, with a hand upload as
fallback). Check each and change nothing unless one still names the
staging tool or `claude/`; report what was checked.

(e) PI12. Section 9: add after the "Forward years" bullet: "- **The live
test (D105.5) is locked.** No accuracy figure for the live forecasts is
computed or shown until its look (D103.2). Neither the planning chat nor
Zac computes an error from MLwx-live's log, observation snapshots or page
before a look (D105.6)."

Check: the invocation in section 4 is unchanged and equals D93.16's; 0
new em-dashes.

### Step 8. Archive header (DE03, D118.9)

Check first that nothing reads or hashes the archive's header lines:
`scripts/archive_decisions.py` (its header handling is for DECISIONS.md)
and `tests/test_record.py`. Then add, after the header's first paragraph
(ending "...served by the headline already carried forward into
`SPEC.md` or `RESULTS.md`)."), one paragraph: "**Order.** Blocks are in
the order they left the live file, not in date order (D93.8): an entry
that stayed live a long time sits after later ones (D118.9)." Check:
`python3 scripts/archive_decisions.py --citations` passes, and the diff
of the archive touches only those lines. Stop if the script or a test
depends on the header.

### Step 9. Tests and F167

Run the suite: 195 OK expected (no test changes). Write F167 (at most
about 40 lines, D93.10): Step 2's terms table in short (one line per
source: terms, redistribution, credit), what changed in each file by
register id, the SPEC 3.4 span's new lines and unchanged hash, the
record files' new byte sizes, readings for the owner, and what was not
done (groups 4 and 6; README beyond section 9).

## End-of-session steps (CLAUDE.md)

1. Real output: paste the checks' real numbers.
2. Overwrite STATUS.md as a current-only snapshot, with: the goal
   without "private" (D118.5, ST02); the redeploy recorded (D118.2) and
   the scheduler closed (D118.4); group (3) live, groups (7) and (9)
   done; SPEC 3.4's new line numbers and unchanged hash; the sync and
   size rule as D118.8; S06 deferred (D118.10); drop "(of about 49,000)"
   from MMMX coverage (ST10); cite D112.2 item 5 for the longer-term
   items (ST11); tests 195. End with: "**Next planning session:** Review
   session 124 and commit; the planning chat syncs Project knowledge
   (D118.8); then fix group (4) when the drive is attached, or group (6),
   the README update, last."
3. Archive step: make D118.14's index changes, add F167, then
   `python3 scripts/archive_decisions.py --apply --session 124`.
4. Checks: `--citations`; re-read only what changed; DECISIONS.md byte
   size (above 80,000 is a finding); the scope-list check with
   `git status --porcelain`.
5. Output file `notes/session-124-output.txt`, summary first (at most 30
   lines), then checkpoints and detail. Report the summary in chat. Then
   stop and wait for review. Do not commit.
