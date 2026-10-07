# Session 84: GitHub readiness

The repo is now pushed to a private GitHub repository. Before the owner
makes it public, this session gets it ready. It:

1. records **D76** (the owner's decisions from the session 83 review and
   this session's plan), before any other edit or network call;
2. runs a **read-only audit** of the working tree and the full git
   history (secrets, personal paths, large files, what data is
   committed);
3. runs a **read-only terms check** of each data source whose data is
   committed or used;
4. records steps 2 and 3 as **F126**;
5. makes the **edits**: a README rewrite, a new RESULTS.md subsection
   with F125's intervals and caveats, an MIT LICENSE file, four
   `.gitignore` lines, and one rule added to CLAUDE.md;
6. does the end-of-session steps.

It **scores nothing, fits nothing and changes no verdict**. The owner
makes the repo public by hand, after review.

---

## Writing rule for this session (new, D76.6)

**No em-dashes (the long dash, U+2014) in any new text this session
writes:** README.md, the RESULTS.md subsection, LICENSE, D76, F126,
STATUS.md, `.gitignore` comments, the CLAUDE.md addition and the output
file's prose. Do not use the en-dash (U+2013) as a substitute either. Use
a colon, a comma, brackets or a new sentence instead. Write numeric
ranges with "to" (for example "12 to 21%"). New DECISIONS headings use a
colon where older headings used the long dash, for example
`## 2026-09-29: Session 84 decision: ...`. **Existing text is not
edited to remove them.**

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No data work.** Read no forecast or observation values, score
  nothing, fit nothing. Write nothing under `data/`.
- **Do not edit any script** under `scripts/` and write no new script.
  Use shell commands (`git`, `grep`, `find`, `du`, `curl`) for the audit
  and the terms check. You may write throwaway commands in the shell,
  not files in the repo.
- **Network: Step 3 only,** and only plain GET requests for public
  terms, licence or attribution pages. No data API requests. No
  accounts, no installs.
- **Never print a secret's value.** If a secret pattern matches, print
  only the file path, the line number (or commit hash for history hits)
  and the pattern's name. Never write a matched value into any file,
  including `notes/session-84-output.txt`, which will be committed.
- **Git is read-only.** No history rewrite, no `git rm`, no `git mv`, no
  push, no remote or GitHub settings, no staging, no commit.
- **Edit only these files:** README.md (full rewrite), RESULTS.md (the
  new subsection and its header line only), LICENSE (new), `.gitignore`
  (append only), CLAUDE.md (the one addition in Step 5.5), DECISIONS.md
  (append D76 and F126; archive step), DECISIONS-archive.md (archive
  step only), STATUS.md (overwrite), `notes/session-84-output.txt` (new).
- **Do not edit** SPEC.md, PROJECT-INSTRUCTIONS.md, any existing entry
  in either DECISIONS file, anything in `docs/`, or any existing file in
  `notes/`. **Personal paths found by the audit are reported, never
  edited (D76.5).**
- Every number in README.md and the RESULTS.md subsection must come
  from SPEC.md, DECISIONS.md or RESULTS.md, cited to its entry. Compute
  nothing new.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-84.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D75, F124 and F125, and
   that no D76 or F126 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that `README.md` exists and that `LICENSE`
   (any extension) and `notes/session-84-output.txt` do not. Otherwise
   stop and report.
4. Read D72 (in particular D72.7 and D72.8), D73.8, D75, F123, F124 and
   F125 in full. Read RESULTS.md in full, the current README.md in full,
   and SPEC section 3 (data sources).
5. Run `git log --format='%an' | sort -u`. Report the distinct author
   names. If there is more than one, stop and report (Step 5.3 needs a
   single copyright holder).

---

## Step 1: record D76 (before any other edit or network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under the heading
`## 2026-09-29: Session 84 decision: GitHub readiness (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D76. Owner decisions, planning chat (after session 83): the session 83
review and session 84's plan.** Written at the start of session 84,
before any other edit or network call.

- **D76.1 F125.1 accepted.** The refits' read-only use of committed raw
  files (the Open-Meteo JSON chunks and the IEM observation chunks), as
  the record code does and as F122.3 did, is accepted. It is within
  "committed files" for session 83's purpose.
- **D76.2 ICON: the project does not save ICON.** F124.2(b) found 850
  hPa temperature present in Open-Meteo's Single Runs `icon_global` from
  2026-04-02. D75.1's rule, stated in advance, therefore applies: the
  project does not save ICON itself. This closes D72.8 for ICON. The
  completeness of the Single Runs archive (one missing 18z run found,
  not scanned) and the timing at hours 18 to 23 (F124.2) stay open, for
  stage D.
- **D76.3 Session order.** Session 84 is a GitHub-readiness session
  before the repo goes public: a README rewrite, F125's intervals and
  caveats in RESULTS.md, data credits and terms, a secrets and
  personal-path check, and a licence file. The NBM/MOS comparison and
  its outcome rule (D72.7), the carried F123.9 decision (D75.3) and
  whether 2026-27 gets a pre-registered NBM/MOS test (D73.8) move to
  session 85. The hold rule (D73.8) is unchanged.
- **D76.4 Licence.** The code is released under the MIT licence. Data
  committed in the repo stays under its sources' terms, which the MIT
  licence cannot change; the README says so.
- **D76.5 Public contents.** `docs/`, `notes/` and the planning files
  stay in the public repo as the working record. The README tells
  readers which files to read and which to skip. Personal paths found by
  the audit are reported, not edited: editing old notes would alter the
  record, and the git history keeps them anyway.
- **D76.6 No em-dashes (standing rule).** No new text from session 84
  on uses the em-dash (U+2014). Existing text is not edited to remove
  it. The rule is added to CLAUDE.md's plain-writing rule.
- **D76.7 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice. NOAA's April 2026
  proposal says one will be issued 30 days before go-live, so the
  earliest go-live is about late October 2026.
```

---

## Step 2: read-only audit

Run everything below read-only. Put the full real output in
`notes/session-84-output.txt`, observing the "never print a secret's
value" rule.

**2.1 Tracked-file overview.** Number of tracked files (`git ls-files`),
and the tracked size per top-level folder. Under `data/`, give file
counts and sizes per subfolder, down to two levels.

**2.2 Secret files by name.** List tracked files, and files that ever
existed in history (`git log --all --name-only --format=`), whose names
match any of: `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`,
`id_rsa*`, `id_ed25519*`, `.netrc`, `credentials*`, `secrets*`,
`*.token`. Also report whether any `.DS_Store` file is tracked or ever
was.

**2.3 Secret patterns in the working tree.** Over tracked text files,
search (case-insensitive where sensible) for:
- AWS key ids: `AKIA[0-9A-Z]{16}`
- private keys: `-----BEGIN [A-Z ]*PRIVATE KEY-----`
- GitHub tokens: `ghp_`, `gho_`, `github_pat_`
- Anthropic and OpenAI-style keys: `sk-ant-`, `sk-[A-Za-z0-9]{20,}`
- Slack tokens: `xox[abprs]-`
- Google API keys: `AIza[0-9A-Za-z_-]{35}`
- assignments: `(api[_-]?key|apikey|secret|token|passwd|password)\s*[:=]`
- URL parameters: `(apikey|api_key|token|key)=`

For each hit print only the path, line number and pattern name. Then
classify each hit as one of: a real credential; a placeholder or
example; code that reads a variable or names a parameter without a
value. Give the reason in a few words.

**2.4 The same patterns in the full history.** Run the 2.3 patterns over
`git log --all -p`. For each hit print only the commit hash (short),
the path and the pattern name, and classify it as in 2.3.

**2.5 Personal details.**
- `/Users/` paths: count per tracked file, and list the files. Do not
  print the lines.
- Email addresses in tracked files: count per file, and list the files.
  Do not print the addresses.
- Commit metadata: the number of distinct author and committer email
  addresses in the history, and for each, only whether it is a GitHub
  `noreply` address or not. Do not print the addresses.

**2.6 Large files.**
- Tracked files over 10 MB, with sizes.
- Blobs over 10 MB anywhere in history (`git rev-list --objects --all`
  with `git cat-file --batch-check`), with sizes and paths.
- `git count-objects -vH`.
- Say whether any file or blob exceeds GitHub's 50 MB warning or 100 MB
  limit.

**2.7 `.gitignore` coverage.** Confirm that `data/raw/grib` is not
tracked. Check whether any tracked file matches the four lines Step 5.4
adds (`.env`, `.env.*`, `*.pem`, `*.key`) and report it: adding them
does not untrack such a file.

**2.8 Stop rule.** If 2.2, 2.3 or 2.4 finds anything classed as a real
credential, **stop here.** Report it in chat and in the output file
(path, line or commit, pattern name only). Do not do Steps 3 to 5. Do
not record F126. The owner decides.

---

## Step 3: read-only terms check

1. From SPEC section 3 and the pull scripts (read only), list every
   source whose data is committed in the repo or was used to build a
   committed file. At least: Open-Meteo (the Previous Runs API),
   the Iowa Environmental Mesonet (IEM) ASOS observations, and the NOAA
   GFS GRIB files (name the exact host the pull scripts use).
2. For each, fetch the source's own current terms, licence or
   attribution page with a plain GET. Record: the URL, the fetch date,
   the licence or terms name, what attribution it asks for (in a short
   paraphrase; a quote only if under 15 words), and any use limit that
   matters for a public repo (for example non-commercial API use). Keep
   anything the page says about redistributing the data.
3. If a page cannot be found or fetched, record "not found" or the
   error, and **do not guess its terms.**
4. Sources probed read-only in F123 and F124 (ECMWF IFS and AIFS, DWD
   ICON, GEFS, WeatherNext, NBM, NWS MOS, Open-Meteo Single Runs):
   confirm that no data from them is committed (F123, F124.4). Do not
   fetch their terms. They get one line each in the README.

---

## Step 4: record F126

Append **F126** after D76, under the heading
`## <run date>: Session 84 finding: the GitHub-readiness audit and terms check`
(the run date as YYYY-MM-DD). Compact; the output file holds the
detail. It gives:
- **F126.1** Step 0 and Step 1 results.
- **F126.2** The audit: tracked-file count and `data/` sizes in brief;
  secret files by name (tree and history); secret-pattern hits, each
  with its classification (tree and history); personal paths and email
  addresses (counts and files only); commit-metadata email count and
  noreply status; large files and blobs; `.gitignore` coverage.
- **F126.3** The terms table: source, URL, fetch date, licence or terms,
  attribution asked for, redistribution and use limits.
- **F126.4** The edits made in Step 5, one line each.
- **F126.5** What this did not do: no data read, scored or fitted; no
  script edited; no personal path edited; no git write; no verdict
  changed.

---

## Step 5: the edits

**5.1 README.md: full rewrite.** Written for two kinds of reader: quant
and finance, and atmospheric science. Plain language, jargon defined on
first use, no em-dashes. Aim for about 150 to 250 lines. Every number is
cited to its DECISIONS entry (for example "(F109)"). Sections, in this
order:

1. **What this is.** One short paragraph: per-airport LightGBM models
   that correct the local bias in GFS 2 m temperature forecasts (a form
   of Model Output Statistics, MOS), judged against raw GFS and
   persistence on held-out years. It is a research project and a
   private tool, not an operational forecast.
2. **Headline result.** Lead with the selected-features method
   (`B+D,L,R,T`, SPEC 8) on the reserved year 2024-25 (F109): a table of
   the five airports with MAE skill over raw GFS and its 95% interval
   (F125.6), stating that every interval lies above zero, against both
   references. Then, in plain sentences, keep these visible:
   - the minimal method fails at Reno (F82), and its margins over raw
     GFS at DSM, YSDU and RNO have intervals that include zero (F125.4);
   - KSFO passes both pre-registered looks (F119, D71) but is not
     directly comparable with the five earlier airports (D69; RESULTS
     6.5);
   - the intervals describe one test year only, and the airports share
     each year's weather, so they are not independent (F125.9);
   - both held-out years are now spent (D59, D71.1); the 2026-27 forward
     test is pre-registered and frozen (D73, F122) and not yet scored.
3. **How it works.** The three methods in a few sentences each, and the
   evaluation discipline: time-ordered splits, pre-registered bars,
   one look per held-out year, same features at every airport.
4. **How this was built.** Two or three sentences: the owner planned
   the work, made every decision and reviewed every change; the code was
   written by Claude Code (Anthropic's AI coding tool) under the rules
   in CLAUDE.md; every change was reviewed and committed by hand.
5. **Repository layout.** What to read: README.md, RESULTS.md, SPEC.md,
   DECISIONS.md, `scripts/`, `data/`. What readers can skip: `docs/`
   (session prompts and commit messages), `notes/` (raw session
   outputs), PROJECT-INSTRUCTIONS.md, CLAUDE.md and
   DECISIONS-archive.md, as the working record of the planning and
   execution loop, kept for audit.
6. **Reproducing.** Only what you can verify by reading the scripts,
   SPEC and `requirements.txt`: the Python setup, that raw pulls are
   committed except the GRIB cache (D47), and how the GRIB cache is
   fetched again. Do not run anything. If a step cannot be verified
   from the repo, say so in one line rather than guess, and report it.
7. **Status and roadmap.** Stages A to H in one line each (SPEC 6).
8. **Data credits and terms.** From F126.3: each source, what it
   supplied, its licence or terms, and the attribution it asks for. One
   line for the probed-only sources. State that the data stays under
   its sources' terms and is not covered by the code licence.
9. **Licence.** MIT for the code; see LICENSE. No warranty; not for
   operational or safety-critical use.

**5.2 RESULTS.md: new subsection 6.6.** Add
`### 6.6 Confidence intervals for every result on record (F125)` after
6.5 and before section 7, so no section is renumbered. Copy F125's four
tables (F125.4 to F125.7) with their numbers unchanged, their raw-GFS
source notes, F125.8's note in one or two sentences, all three
statements of F125.9, and D71.5's framing for KSFO. Add a short plain
reading: which intervals over raw GFS include zero (minimal method: DSM,
YSDU, RNO; F94: DSM, RNO), and that the selected method's are all above
zero. State that the intervals are descriptive, reuse the spent years
and change no verdict (D75.2). Also add "revised after session 84" to
the header's revision sentence. Change nothing else in RESULTS.md.

**5.3 LICENSE (new).** The standard MIT licence text, unchanged, with
the line `Copyright (c) 2026 <name>`, where `<name>` is the single
author name from Step 0.5.

**5.4 `.gitignore`: append only.** At the end:

```
# --- local secrets: never commit (D76) ---
.env
.env.*
*.pem
*.key
```

**5.5 CLAUDE.md: one addition.** Directly after the paragraph that ends
"This applies to code comments, the spec files, and chat replies.", add
this paragraph, copied exactly:

```
Do not use the em-dash (the long dash) in any new text: use a colon, a
comma, brackets or a new sentence instead. Existing text is not edited
to remove it (DECISIONS D76.6).
```

**5.6 Checks.** Print the result of each:
- counts of U+2014 and U+2013 (count them with Python, not shell
  escapes) in README.md, LICENSE and `notes/session-84-output.txt`:
  expected 0;
- the same two counts for D76, F126, the RESULTS.md subsection 6.6, the
  CLAUDE.md addition and STATUS.md, each checked on its own line range:
  expected 0;
- `git diff --stat`: only the files the scope guard allows;
- for RESULTS.md, `git diff` shows only the new 6.6 and the header line;
- every number in README.md and 6.6 found in its cited entry (list
  each number and its source).

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot, with no em-dashes.
   Include: the forward test's state (D73, F122) and the hold rule
   (D73.8), unchanged; F123's source table in brief; the ICON decision
   (D76.2) in one line; F125 in brief (one line per method); session
   84's outcome in brief (F126). Remove the F125.1 open question (closed
   by D76.1). Carried items:
   - **GFS v17 (D76.7).** Still no Service Change Notice as of
     2026-09-29. Re-check at each planning session. The go-live date
     sets period A's length. PNS 26-30's statement that the 0.25 degree
     GRIB2 files remain is to be confirmed against the SCN (D73.4).
   - **Session 82's MOS near-miss (F123.9).** The owner's decision is
     deferred to the NBM/MOS outcome rule (D72.7, D73.8), now session
     85 (D76.3).
   - The remaining stage A/B uncertainties from the session 83 STATUS,
     less the ICON saving decision (closed by D76.2).

   It must end with: "**Next planning session:** Review session 84. If
   the review is clean, the owner makes the repo public. Then design
   session 85: the NBM/MOS comparison and its outcome rule (D72.7),
   including the carried F123.9 decision and whether 2026-27 gets a
   pre-registered NBM/MOS test (D73.8)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Also
   check that README.md and RESULTS.md 6.6 agree with DECISIONS. Report
   only. **Write the findings into `notes/session-84-output.txt`** as
   well as reporting them in chat (D74.2).
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, F123,
   F124, F125, D76 and F126 stay live. D75 may move if it meets the
   criterion (D75.1 is decided by D76.2, D75.2 is done, D75.3 is carried
   by D76.3). Report what moved and why.
5. Stop and wait for review. Do not commit. Do not write a commit
   message.
