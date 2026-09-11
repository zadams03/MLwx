# Session 34a — DECISIONS.md archive manifest

**This file is a decision only. No canonical file was changed to produce it.**
`DECISIONS.md`, `DECISIONS-archive.md`, `SPEC.md`, `STATUS.md`, `RESULTS.md` and
`CLAUDE.md` are untouched. The mechanical move (cutting the MOVE line-ranges below out
of `DECISIONS.md` and appending them verbatim to `DECISIONS-archive.md`, with a
one-line pointer left behind — matching the format `DECISIONS.md` already uses at
lines 10 and 51 for the session-21 move) is session 34b's job, once this manifest is
approved.

Method: built from a `grep`-based header index (never a full read of `DECISIONS.md`),
plus bounded reads of `STATUS.md`, `RESULTS.md`, and the three live richer-features
entries (F85, F86, F87) in full, plus a handful of further bounded reads to resolve
specific citation questions those three entries raised.

---

## Task 1 — the entry index

**Header patterns confirmed by grep**, in this DECISIONS.md (post the session-21
archive move, which already removed D1–D12, F1–F4, F6 and F11 to
`DECISIONS-archive.md` — confirmed those numbers are genuinely absent from the live
file and present in the archive):

- Section headers: `^## <date> — <title>`
- Decision markers: `^\*\*D[0-9]+(\.[0-9]+)?\.` (plain `**D45.` style, and
  sub-numbered `**D21.1 —`, `**D31.1 —`, `**D35.1 —`, `**D39.1 —`, `**D44.1 —` style
  inside the four method-lock entries)
- Finding markers: `^\*\*F[0-9]+\.`

**Contiguity check (Task 1's required check):**
- Main D-numbers present in the live file: **D13 through D45, no gaps, no
  duplicates.** D1–D12 are the ones already archived (confirmed absent here, present
  in `DECISIONS-archive.md`).
- Main F-numbers present in the live file: **F5, F7 through F87, no gaps, no
  duplicates**, except F6 and F11, which are the two already archived (confirmed
  absent here, present in `DECISIONS-archive.md`). F1–F4 are the other archived four.
- The sub-numbered decisions (D21.1–D21.11, D31.1–D31.11, D35.1–D35.13, D39.1–D39.13,
  D44.1–D44.12) are internal parts of one parent method-lock entry each, not separate
  top-level numbers, and don't affect the main-sequence contiguity check above.
- A handful of bolded lead-sentences inside later findings (e.g. `**D35.8 named the
  deciding half of the bar in advance and it was right.**` inside F47, or `**D44.12's
  near-constant-bias / overfit watch-item, read exactly as it was...**` inside F82)
  matched the D-marker regex too, because they *start* a bold sentence with a D-number.
  These are not new entries — they're follow-up commentary paragraphs inside the
  finding that precedes them, referencing an earlier lock decision by number. They are
  listed in the index below (so their line ranges are accounted for) but are not part
  of the D13–D45 contiguous count.

**Full entry count:** 250 header-matched spans (sections + D-entries + F-entries +
the follow-up-commentary spans noted above), covering lines 14–9471 (lines 1–13 are
the file's own title/intro and the existing D1–D12 pointer, untouched either way).

**Full index (number/title/line range/classification):**

| lines | class | title (as it appears at that line) | why (if not obvious) |
|---|---|---|---|
| 14-38 | KEEP-LIVE | Parked items (P1–P3) | not settled — P2 feeds stage 4, P3 feeds SPEC 5.4 |
| 39-54 | MOVE | Open questions (verify on contact) — Q1, Q2 | closed (answered by archived F1/F2) |
| 55-90 | MOVE | Open questions raised by session 01 — Q3–Q6 | closed (D14/F5/SPEC/D15 answer them) |
| 91-92 | MOVE | Session 02 decisions header | — |
| 93-104 | MOVE | D13 — fixed train/test split dates | codified in SPEC 4.3 |
| 105-114 | MOVE | D14 — pairing rule | codified in SPEC 4.5 |
| 115-125 | MOVE | D15 — raw data in version control | codified in SPEC 2.3 |
| 126-132 | MOVE | Session 02 findings header | — |
| 133-191 | MOVE | F5 — previous_day1 is a nominal 24h lead | codified in SPEC 3.2 |
| 192-217 | MOVE | Open questions raised by session 02 | closed |
| 218-223 | MOVE | Session 03b decisions header | — |
| 224-233 | MOVE | D16 — pin `gfs_global` | codified in SPEC 3.2 |
| **234-249** | **KEEP-LIVE** | **D17 — stage 1 temperature-only, extras dropped** | **see "Reno / live-phase citations" below — F85 relies on its exact wording** |
| 250-255 | MOVE | Session 03b findings header | — |
| **256-275** | **KEEP-LIVE** | **F7 — extra forecast variables exist only for recent data** | **same as D17, its paired finding** |
| 276-315 | MOVE | F8 — the 492-hour gap, EGLC | headline in SPEC 3.2 |
| 316-343 | MOVE | F9 — EGLC observation record is good | settled, EGLC-only |
| 344-382 | MOVE | F10 — value-range sanity check | settled |
| 383-401 | MOVE | Open questions raised by session 03b | closed |
| 402-403 | MOVE | Session 04 decisions header | — |
| 404-423 | MOVE | D18 — rehearsal/validation-year split | codified in SPEC 4.3 |
| 424-439 | MOVE | D19 — minimal 3-feature set | codified in RESULTS §2 verbatim |
| 440-449 | MOVE | Session 04 findings header | — |
| 450-478 | MOVE | F12 — EGLC join, rows kept/dropped | superseded precedent (F16 is the record) |
| 479-532 | MOVE | F13 — EGLC bias shape | headline in RESULTS §4 finding 2 |
| 533-637 | MOVE | F14 — EGLC validation rehearsal | superseded by F16 (sealed test) |
| 638-684 | MOVE | Open questions raised by session 04 | closed |
| 685-686 | MOVE | Session 05 decision header | — |
| 687-710 | MOVE | D20 — absolute-error objective | codified in RESULTS §2 (`objective=regression_l1`) |
| 711-712 | MOVE | Session 05 finding header | — |
| 713-820 | MOVE | F15 — objective-fix measured | superseded by F16 |
| 821-826 | MOVE | Session 06: THE METHOD LOCK header | — |
| 827-932 | MOVE | D21 + D21.1–D21.11 — EGLC method lock | fully superseded by F16's pass; settings codified in RESULTS §2 |
| 933-950 | MOVE | D22 — qualitative bar, no numeric margin | codified in SPEC 5.3 |
| 951-967 | MOVE | D23 — mean-bias reference listed | codified in SPEC 5.2 |
| 968-985 | MOVE | D24 — environment pinned | settled housekeeping |
| 986-995 | MOVE | D25 — SPEC 3.2 records the gap | codified in SPEC 3.2 |
| 996-1021 | MOVE | Session 06 note | — |
| 1022-1028 | MOVE | Session 07: SEALED-TEST RESULT header | — |
| 1029-1193 | MOVE | **F16 — STAGE 1 PASSES** | headline fully in SPEC 5.0 / RESULTS throughout |
| 1194-1221 | MOVE | Open questions raised by session 07 | closed |
| 1222-1226 | MOVE | Session 08 decisions header | — |
| 1227-1245 | MOVE | D26 — stage 2 opens at CDG | codified in SPEC 6 |
| 1246-1266 | MOVE | D27 — stage 3 target-hour convention, noted | codified in SPEC 4.1 |
| 1267-1275 | MOVE | Session 08 findings header | — |
| 1276-1481 | MOVE | F17–F21 — CDG verify-on-contact | superseded by F30 (CDG passed); grid point also in SPEC 3.4 |
| 1482-1524 | MOVE | Open questions raised by session 08 | closed |
| 1525-1531 | MOVE | Session 09 decisions header | — |
| 1532-1604 | MOVE | D28, D29 — SPEC generalised; deeper eval optional | codified in SPEC §6/5.4 |
| 1580-1604 | MOVE | D30 — off-hour days dropped and taken | codified in SPEC 4.5 |
| 1605-1649 | MOVE | Session 09 note + open question | closed |
| 1650-1890 | MOVE | F22–F26 — CDG full pull and gap map | superseded by F30 |
| 1891-2165 | MOVE | F27–F29 — CDG join, bias, rehearsal | superseded by F30 |
| 2166-2532 | MOVE | Session 12: CDG METHOD LOCK (D31 + D31.1–D31.11) | superseded by F30's pass |
| 2533-2846 | MOVE | Session 13: **F30 — STAGE 2 PASSES (CDG)** | headline fully in SPEC 5.0 / RESULTS |
| 2847-2917 | MOVE | Session 14 decisions — D32 (DSM opens), D33 (target hour) | codified in SPEC 3.4/4.1 |
| 2918-3293 | MOVE | F31–F37 — DSM verify-on-contact | superseded by F47 |
| 3294-3382 | MOVE | D34 — SPEC generalised for per-airport hours | codified in SPEC 3.4/4.1 |
| 3383-3734 | MOVE | F38–F41 — DSM full pull and gap map | superseded by F47 |
| 3735-4137 | MOVE | F42–F46 — DSM join, bias, rehearsal | superseded by F47 |
| 4138-4639 | MOVE | Session 17: DSM METHOD LOCK (D35 + D35.1–D35.13) | superseded by F47's pass |
| 4640-5009 | MOVE | Session 18: **F47 — DSM PASSES**, F48 (3-pass synthesis) | headline fully in SPEC 5.0 / RESULTS |
| **5010-5045** | **KEEP-LIVE** | **Open question raised by session 18 — Q30 is raised here** | **Q30 is still open (STATUS)** |
| 5046-5117 | MOVE | Session 19 decisions — D36 (Dubbo opens), D37 (target hour) | codified in SPEC 3.4/4.1 |
| 5118-5415 | MOVE | F49–F56 — Dubbo verify-on-contact | superseded by F64 |
| 5416-5473 | MOVE | D38 — SPEC housekeeping | codified in SPEC |
| 5474-5623 | MOVE | F57–F59 — Dubbo full pull and gap map | superseded by F64 |
| **5624-5730** | **BORDERLINE** | **Session 21: ONE-TIME HOUSEKEEPING RESTRUCTURE record** | **flagged below — recommend MOVE, owner should confirm** |
| 5731-6034 | MOVE | F60–F63 — Dubbo join, bias, rehearsal | superseded by F64 |
| 6035-6565 | MOVE | Session 23: DUBBO METHOD LOCK (D39 + D39.1–D39.13) | superseded by F64's pass |
| 6566-6934 | MOVE | Session 24: **F64 — DUBBO PASSES**, F65 (4-pass synthesis) | headline fully in SPEC 5.0 / RESULTS |
| **6935-6948** | **KEEP-LIVE** | **Q30 status update** | **Q30 is still open (STATUS)** |
| 6949-7384 | MOVE | Session 25 decisions (D40, D41) + F66–F73 — Bozeman/Reno candidate compare, Bozeman initially chosen | superseded by D42 (switched to Reno); grid coordinates also in SPEC 3.4 |
| 7385-7502 | MOVE | D42 — fifth airport switched to Reno | codified in SPEC 3.4, superseding D40 |
| 7503-7809 | MOVE | D43 (SPEC housekeeping) + F74–F77 — Reno verified, full pull, gap map | superseded by F82; grid point also in SPEC 3.4 |
| 7810-7826 | MOVE | Open question raised by session 26 | closed (not Q30/Q32) |
| 7827-8100 | MOVE | F78–F81 — Reno join, bias, rehearsal (first negative rehearsal) | superseded by F82; F81's hypothesis headline is in RESULTS §5 |
| **8101-8120** | **KEEP-LIVE** | **Open question raised by session 27 — Q32 is raised here** | **Q32 is still open (STATUS)** |
| 8121-8518 | MOVE | Session 28: RENO METHOD LOCK (D44 + D44.1–D44.12) | superseded by F82's result; D44.12's headline prediction is in RESULTS §4 finding 4 |
| 8519-8738 | MOVE | Session 29: **F82 — RENO DOES NOT PASS** | headline fully in SPEC 5.0 / RESULTS |
| 8739-8842 | MOVE | Session 30 — D45 (SPEC housekeeping), F83 (Q31 closed), F84 (RESULTS.md written) | headline fully in STATUS "Done" |
| **8843-9471** | **KEEP-LIVE** | **Sessions 31–33 — F85, F86, F87 (richer-features live phase)** | **explicitly named live by the session prompt** |

---

## Task 2 — classification against the archive criterion

**Expected-MOVE airports (EGLC/LFPG/DSM/YSDU), checked and confirmed archivable.**
Every verify-on-contact / pull-and-map / join-and-rehearse / lock / test entry for
these four airports is settled (each airport passed, its cycle is closed) and its
result is fully carried forward as a headline in `SPEC.md` §5.0/3.4 and `RESULTS.md`
— nothing in the live richer-features phase (F85–F87) cites any of these entries
beyond a number-and-headline already stated in `RESULTS.md`/`STATUS.md`/`SPEC.md`.
**All MOVE**, per the session prompt's own "expected" list.

**Closed questions.** Every `## Open question(s) raised by session N` block, and the
original `## Open questions (verify on contact)` block, is closed **except** the two
that raise Q30 (session 18's block, and the later "Q30 status update") and the one
that raises Q32 (session 27's block) — `STATUS.md`'s own "Open questions (live)"
section confirms Q30 and Q32 are the *only* two still open, and Q31 is confirmed
closed (F83). **MOVE for all closed-question blocks; KEEP-LIVE for the three
Q30/Q32-bearing blocks.**

**"Parked items" (P1–P3), lines 14–38 — reclassified from the session prompt's
"expected" list.** These are not questions and were never closed — they are
explicitly still-parked considerations. P2 (the WeatherNext / stage-4 angle) and P3
(harder evaluation bars) are still live per `SPEC.md` (stage 4's WeatherNext note, and
SPEC 5.4's "deeper evaluation... optional, now available" wording tracing to D29,
which itself answers part of P3). Neither is "settled" in the sense the criterion
requires (a settled entry's conclusion won't change — these are explicitly open for
future action). **KEEP-LIVE**, not MOVE.

**Reno — judged individually, per entry, as instructed.** Reno's full cycle (D40–D44,
F66–F82, sessions 25–29) is settled — Reno's result stands, and no further Reno work
is contemplated by any live open question. The two places the live phase (F85, F86)
mentions a Reno-specific finding by number:
- **F66** (Reno's grid point/coordinates) — cited by F85 only to confirm a repeat pull
  landed on the same grid point. The coordinates themselves are permanently on record
  in `SPEC.md` §3.4's airport table, so archiving F66 loses nothing F85 or a future
  session would need to re-derive.
- **F81** (the "richer features might help Reno" hypothesis: cloud cover, wind,
  terrain descriptor) — cited by F86 by name, but its exact content is already quoted
  verbatim in `RESULTS.md` §5 ("richer features at Reno specifically, as the
  diagnostic case (cloud cover, wind, a genuine terrain descriptor)"). Nothing in F86
  needs anything from F81 beyond that already-published phrase.

Both check out as headline-only citations. **Conclusion: all of Reno's cycle is
archivable, same as the four passed airports — MOVE**, with F66 and F81 specifically
checked (not just assumed) rather than swept in by pattern-matching alone.

**One exception found that the session prompt's "expected" list did not anticipate:
D17 and F7.** These are not Reno-specific — they're EGLC-only, session-02/03b
entries about why the extra forecast variables (cloud cover, wind, dew point, surface
pressure) were dropped from stage 1. On a bounded read of F85 in full, its central
finding — that these variables become available project-wide starting exactly
2024-01-19 12:00 UTC, "exactly the shape D17 already anticipated for stage 1's
rejected extra variables" — directly quotes D17's own reasoning ("Kept as a possible
later enhancement, recent period only... a different, shorter dataset") as the design
precedent for the live two-tier richer-features training window, and restates F7's
specific date-bracketing claim ("absent 2023-07-01, present 2024-07-01") to show F85
sharpened it "down to the hour." `STATUS.md` only ever mentions these two in passing
("confirms and extends F7/D17") — it does not restate either entry's actual content.
Since the still-open richer-features question (go/no-go on a full lock-and-test
cycle, `STATUS.md` "Next" item 2) traces its two-tier-window design directly back to
D17's own wording, a future richer-features session is more likely than not to want
D17/F7 at hand rather than re-deriving the same reasoning from `RESULTS.md`'s much
shorter mention. **KEEP-LIVE for D17 and F7**, overriding the initial pattern-based
MOVE call.

---

## Consolidated lists

### MOVE — line ranges for 34b's script (contiguous blocks; 7 cuts, 8,591 lines total)

```
39-233
250-255
276-5009
5046-5623
5731-6934
6949-8100
8121-8842
```

Each cut spans complete entries only (verified against the entry index above — no
cut starts or ends mid-entry). Line 5624-5730 (the session-21 restructure record) and
lines 234-249 / 256-275 (D17, F7) are deliberately excluded from the surrounding cuts
— see BORDERLINE and the D17/F7 exception above.

### KEEP-LIVE — line ranges (nothing moves; listed for the audit trail)

```
14-38      Parked items P1-P3
234-249    D17
256-275    F7
5010-5045  Open question raised by session 18 (Q30 origin)
6935-6948  Q30 status update
8101-8120  Open question raised by session 27 (Q32 origin)
8843-9471  Sessions 31-33: F85, F86, F87 (the live richer-features phase)
```

### BORDERLINE — flagged for the owner to confirm before 34b runs

```
5624-5730  Session 21: ONE-TIME HOUSEKEEPING RESTRUCTURE record
```

This entry is the meta-record of the *first* archive move (what moved to
`DECISIONS-archive.md` in session 21, and why). It meets the archive criterion on a
literal reading — settled, not cited by any live open question or by F85–F87 — and
the facts it documents (which blocks moved, why, and the byte-for-byte verification)
are preserved regardless of archive/live status, since `DECISIONS-archive.md` itself
and git history both hold the same information independently. Recommendation:
**MOVE**, alongside the first restructure record it describes, for symmetry with the
"nothing here is deleted or altered" framing `DECISIONS-archive.md` already uses.

But there's a real argument to **KEEP-LIVE** instead: it is the only place in either
live file that explains *why* `DECISIONS-archive.md` exists at all and how pointers
work, which a reader of a bare `[D1–D12 ... archived]`-style pointer line (as seen at
`DECISIONS.md` lines 10 and 51) might want without having to open the archive file
first. Since session 34b will add a second, near-identical restructure-record entry
for *this* move, keeping the first one live costs little and gives a reader two
worked examples instead of one.

**Recommend the owner pick one before 34b runs; both are defensible.**

---

## What this session did not do

No entry was moved, edited, deleted, or reworded. No canonical file
(`DECISIONS.md`, `DECISIONS-archive.md`, `SPEC.md`, `STATUS.md`, `RESULTS.md`,
`CLAUDE.md`) was touched. No code, script, model, data file, or figure was touched.
No entry number was renumbered or proposed for renumbering.

**One thing noticed outside this session's scope, logged rather than acted on:** the
mid-entry "false positive" header matches described in Task 1 (bolded lead sentences
inside a later finding that happen to start with an earlier D-number, e.g. inside
F47, F64, F82) are harmless for this manifest's purposes, but if a future session ever
wants to grep DECISIONS.md for "all entries," the same regex will over-match the same
way. Not worth fixing now — noted for whoever next builds tooling against this file.

---

## End-of-session steps

**1. Report (entry index + manifest summary).**
- Total header-matched spans indexed: **250**, covering `DECISIONS.md` lines 14–9471.
- Main D-number sequence: **D13–D45, contiguous, no gaps, no duplicates** (D1–D12
  already archived).
- Main F-number sequence: **F5, F7–F87, contiguous, no gaps, no duplicates** except
  F6 and F11, already archived (F1–F4 also already archived).
- Manifest summary: **237 spans MOVE, 12 spans KEEP-LIVE, 1 span BORDERLINE.**
  MOVE totals 8,591 of the file's 9,471 lines, in 7 contiguous cuts. KEEP-LIVE is the
  file's front matter/parked items, D17/F7, the three Q30/Q32-bearing blocks, and the
  whole sessions 31–33 richer-features phase. The one BORDERLINE call (the session-21
  restructure record, 107 lines) is flagged above for the owner's pick.
- Reno calls: **all of Reno's cycle (D40–D44, F66–F82) classified MOVE**, after
  individually checking the two places the live phase cites a Reno-specific entry by
  number (F66, F81) and confirming both citations are headline-only, already
  reproduced elsewhere.
- One correction to the session prompt's own "expected MOVE" framing found and
  applied: **D17 and F7 (EGLC-only, sessions 02/03b) reclassified KEEP-LIVE**, because
  F85 relies on their specific wording, not just their headline.

**2. Saved.** `notes/session-34-archive-manifest.md` (this file).

**3. Consistency check.**
- Every one of the 250 indexed spans is classified exactly once (237 + 12 + 1 = 250).
- Every MOVE span has an exact line range; the seven consolidated cut ranges above
  cover all 237 MOVE spans with no gaps between adjacent MOVE spans and no overlap
  with any KEEP-LIVE/BORDERLINE span.
- The KEEP-LIVE set includes F85, F86, F87 in full, and both blocks carrying the two
  live open questions (Q30, Q32).
- `git status` at the end of this session shows only two untracked files:
  `notes/session-34-archive-manifest.md` (new, this file) and
  `docs/session-34a.md` (the session prompt, already untracked at session start,
  unrelated to this session's work). No canonical file shows as modified.
- No duplicated heading and no out-of-order log entry was noticed in the portions of
  `DECISIONS.md` read this session (the header index itself, plus the bounded reads
  of F85/F86/F87, D17, and F7) — this is not a claim about portions not read.

**4. Stopping here per the session prompt.** No commit. No `DECISIONS.md` or
`STATUS.md` edit this session. Waiting for the owner's review of this manifest —
including a decision on the one BORDERLINE call — before 34b executes the move.
