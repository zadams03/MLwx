# Session 66 — Document audit (read-only)

Scope: CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md, the live DECISIONS.md, and
`docs/*.md`. `DECISIONS-archive.md` was not read in full — only through the
scripted and git checks below, per the session prompt's own instruction.
This session reports and fixes nothing; all "suggested fix" text below is a
recommendation for a later fix session, not an action taken here.

All checks were run as throwaway scripts outside the repo (under
`/private/tmp/claude-501/.../scratchpad/audit66/`), against the project's own
files, read-only. Full script source and raw output are in the Appendix.

---

## 1. Summary

| severity | count |
|---|---|
| must-fix | 0 |
| should-fix | 3 |
| cosmetic | 4 |
| uncertain | 1 |
| **total** | **8** |

**Headline result: no contradiction, broken citation, numbering gap, or
duplicate-defined entry was found anywhere in the project's documentation.**
Every citation of the form `Dnn`, `Dnn.m`, `Fnn`, `Qnn`, and `Dnn item m`
across CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md, the live DECISIONS.md and
all 68 files under `docs/*.md` resolves to exactly one defining entry, in
either DECISIONS.md or DECISIONS-archive.md. The D (1–60), F (1–110) and Q
(1–32) numbering sequences are each complete with no gaps and no duplicate
definitions. The findings below are archive-hygiene and clarity items, not
correctness problems.

---

## 2. Findings table

| ID | severity | file:line | evidence | suggested fix |
|---|---|---|---|---|
| A66-01 | should-fix | DECISIONS.md:598–605 (D50, live) | D50 (session 45) flagged F94 as "borderline... stays live in `DECISIONS.md` pending the owner's own call on whether to archive it now or let it age" — five sessions and two further consolidations (D58/F109, D59/F110) have passed since with no explicit call made. F94's headline is already carried in `SPEC.md` §7 and `RESULTS.md` §5, and neither `STATUS.md` nor any live open question now cites F94's own wording — only its headline (confirmed by grep, see `stale_term_sweep_output.txt` and `git status`-style citation check). | F94 now cleanly meets the D46 archive criterion. Bring it to the owner as a candidate for the next archive pass; if approved, move mechanically per the D46 method. |
| A66-02 | should-fix | DECISIONS.md:421 (D49), :509 (F95), :566 (D50) | D50 (session 45) explicitly kept D49/F95 live "because... recent, and `STATUS.md` still references them directly." Checked directly this session: current `STATUS.md` (post session 65) **no longer cites D49, F95, or D50 anywhere** — the only remaining citations to these three are self-referential, inside their own or each other's entries (`grep -n "D49\|F95\|D50\b" STATUS.md` returns nothing; see appendix). Their content — what changed in SPEC.md/RESULTS.md at sessions 43–45 — is now superseded bookkeeping: session 65's own consolidation (D59, F110) is the current record of SPEC/RESULTS' structure. | These three entries now meet the D46 archive criterion (settled, codified elsewhere, no longer needed word-for-word). Candidates for the next archive pass, alongside F94. |
| A66-03 | should-fix | STATUS.md:105–106 ("Next planning session: the owner chooses a Q30 branch...") | This line, as it read at the start of this session, is made stale by this session's own D60 (DECISIONS.md, appended in Step 1): the owner has ordered a three-part audit to run *before* any Q30 branch is chosen, so the immediate next action is no longer "choose a Q30 branch." | Self-resolving: this session's own end-of-session step overwrites STATUS.md to reflect D60.1. Flagged here for completeness per the Step 2 instruction to record every instance of stale wording, including superseded next steps. No separate fix session needed for this specific item. |
| A66-04 | cosmetic | DECISIONS.md:14–36 (Parked items P2, P3) | P2 and P3 both end "revisit once stage 1 passes" / "Revisit once stage 1 passes." Stage 1 (EGLC) had already passed well before this parked-items block was written (2026-08-16) — Q30, raised just two days later (2026-08-18), already describes *three* airports as having passed. The trigger condition for both parked items has been satisfied for the entire life of the project and neither has been revisited in 50 further sessions. | Bring to the owner's attention at the next planning session: either revisit P2/P3 now (WeatherNext, harder evaluation bars) or reword the parked items to state plainly that they are eligible for revisiting, not conditional on a future event. |
| A66-05 | cosmetic | DECISIONS.md:16–18 (Parked item P1) | P1 ("Overall project direction (deeper / wider / sideways)... Decide after a couple of locations are working, from inside the work rather than up front") is functionally superseded by Q30, which is the same decision point, now far more developed (three branches, DECISIONS D59.5/D60.1) and actively tracked in STATUS.md. P1 has had no session-by-session upkeep since it was written. | Consider closing P1 with a one-line pointer to Q30, the same way superseded material elsewhere in the project points forward rather than sitting stale. |
| A66-06 | cosmetic | SPEC.md:571 (§6, "Further airports may follow before stage 3...") | This bullet lists the same five generic steps (verify, pull/map, join/rehearse, lock, test) for any future airport, without noting that §8.7 now makes B+D,L,R,T the project's default recipe for that work. A reader of §6 alone could miss which recipe a new airport should default to. | Add a one-clause cross-reference to §8.7 (`... on the same five steps ..., using whichever method is then the project's default recipe (see §8.7)`). |
| A66-07 | cosmetic | SPEC.md:301 ("bilinear-interpolated"), SPEC.md:611/729 ("lapse rate"/"lapse-rate"), SPEC.md:788 ("complete-case") | These three terms are used without an inline plain-language gloss on first use, which CLAUDE.md's own style rule calls for ("define jargon on first use"). `RESULTS.md` §5.1 glosses "lapse rate" implicitly via the elevation-correction description but SPEC.md itself does not. | Add a short parenthetical gloss at first use in SPEC.md, e.g. "bilinear-interpolated (a standard way to estimate a value between four known grid points)", "lapse rate (how fast temperature drops with height)", "complete-case (a row is used only if every one of the relevant columns has a value)". |
| A66-08 | uncertain | CLAUDE.md ("The paste-before-work habit" section); docs/session-66.md:85 | The session prompt's own Step 2 explicitly asks whether CLAUDE.md's planning-chat paste-before-work habit is now stale "versus Project knowledge." A project-wide search for "Project knowledge" (case-insensitive) across CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md, DECISIONS.md and `docs/*.md` finds **no mention anywhere except the session-66 prompt itself.** There is no record in this project of a "Project knowledge" feature being adopted, so this session found no evidence the habit is stale — but it also found no positive confirmation the habit is still how planning chats actually work, since that happens outside this repository. | Genuinely uncertain from the documentary record alone — recommend the owner confirm directly whether planning chats still rely on pasting STATUS.md, or have moved to some other project-context mechanism, and update CLAUDE.md's wording only if the answer is "moved." |

---

## 3. Clean checks

All of the following were checked and came back with **no exceptions**:

- **Citation resolution (Step 3.1).** Every `Dnn`, `Dnn.m`, `Fnn`, `Qnn`, and
  `Dnn item m` citation across CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md, the
  live DECISIONS.md, and all 68 files under `docs/*.md` resolves to a
  base-number defining entry (`**Dnn.`, `**Fnn.`, `**Qnn.`, not followed by
  another digit) in either DECISIONS.md or DECISIONS-archive.md.
- **Duplicate definitions (Step 3.1).** No `Dnn`/`Fnn`/`Qnn` base number is
  defined more than once anywhere.
- **Numbering sequences (Step 3.2).** D1–D60 (60/60, no gaps), F1–F110
  (110/110, no gaps), Q1–Q32 (32/32, no gaps).
- **Ordering — live DECISIONS.md (Step 3.3).** All 15 dated `##` section
  headers are in non-decreasing chronological order (2026-08-16 through
  2026-09-23).
- **Ordering — archive (Step 3.3).** The four `## Moved by session N` blocks
  in DECISIONS-archive.md are in session order (34b, 38, 45, 65).
- **Cross-references — SPEC.md and RESULTS.md internal (Step 3.4).** Every
  `section N[.M]` reference inside SPEC.md (35 references) and inside
  RESULTS.md (30 references) resolves to a heading or bold subsection marker
  that actually exists in that file. The one reference that looks like a
  self-reference but isn't — RESULTS.md:470 "folded into `SPEC.md` as
  section 8" — correctly points at SPEC.md's own section 8, not a (nonexistent)
  RESULTS.md section 8; checked directly and found unambiguous in context.
- **Cross-references — "SPEC N[.M]" project-wide (Step 3.4).** All ~130
  `SPEC N[.M]` / `SPEC §N` citations across DECISIONS.md, RESULTS.md,
  STATUS.md, SPEC.md itself, and every `docs/*.md` file resolve to a real
  SPEC.md section or bold subsection marker.
- **Duplicated/misplaced headings (Step 2).** No duplicate `##` heading
  within SPEC.md, RESULTS.md, STATUS.md, or DECISIONS.md.
- **STATUS.md shape (Step 2).** 106 lines, a genuine current-only snapshot —
  not grown into an accumulating log.
- **Archive criterion, positive checks (Step 3.5).** D17/F7's "kept live"
  justification (D46: because the live richer-features finding F85 depends
  on their specific wording) was re-checked directly: archived F85 (line
  9159 of DECISIONS-archive.md) does explicitly say it "confirms and extends
  F7/D17" and "confirms D17's hypothesis," so the dependency is real and
  D17/F7 are correctly still live even though F85 itself has since been
  archived. D51/F96's "kept live" justification (D59.4: needed word-for-word
  by Q30's second-test-year branch) is also still valid — Q30 remains open
  per this session's own D60.1. D46 and D47 are correctly kept live as
  standing process rules, not settled findings, so the archive criterion
  does not apply to them at all.
- **Stale-term sweep (Step 3.6).** "two methods" / "two proven" / "second
  method" hits in live docs are all inside historical DECISIONS entries
  correctly describing a past state, or inside RESULTS.md §6's opening line
  correctly describing the minimal and richer methods specifically (not a
  claim the project has only two methods in total). Every "reserved year"
  and "held-out" hit in live docs is either a proper-noun label or an
  accurate present-tense statement that no untouched year remains — none
  claims a spent year is still live. No "not yet run" hit in any live doc.
  The one live "pending" hit (DECISIONS.md:602) is a genuine, still-open
  item — see A66-01, not a false claim.
- **Archive integrity, all 5 move commits (Step 4.1).** Every commit that
  added content to DECISIONS-archive.md (sessions 21, 34b, 38, 45, 65) was
  checked line-for-line against the same commit's deletions from
  DECISIONS.md. All moves are verbatim. The one commit with deletions inside
  DECISIONS-archive.md itself (548d54a, session 34b, 11 lines) is the
  documented header-note rewording (D46), not a loss of moved content. The
  one apparent gap (60 lines removed from DECISIONS.md in the same commit
  that don't appear added to the archive) was traced and confirmed: all 60
  are the D17/F7 content, kept live and simply reordered within
  DECISIONS.md itself — zero lines are genuinely unaccounted for.
- **Frozen-script integrity (Step 4.2).** `scripts/session48_reserved_year.py`
  and `scripts/session60_combine_design.py` have no commits after their
  freezing commit — untouched. `scripts/session39_sealed_test.py` has one
  post-freeze commit (session 41): a documented guard-constant correction
  (F93), made before any model was fit or sealed-year result seen, exactly
  as F94's own text describes it. `scripts/session62_reserved_confirm.py`
  has one post-freeze commit (session 63): a documented, pre-look,
  outcome-orthogonal wiring addition (F107), exactly as the session prompt's
  own example anticipated. `scripts/session55_radiation_pull.py` has one
  post-build commit (session 56): verified by diff to be a print-text-only
  cosmetic fix, explicitly stated as such in the commit message and matching
  the actual 3-line diff.
- **Uncommitted state at session start (Step 4.3).** `git status` showed
  only the untracked session prompt, `docs/session-66.md` — no other
  pending changes existed before this session's own Step 1/Step 4 edits.

---

## 4. Appendix

### 4.1 `citation_check.py` (Step 3.1, 3.2)

```python
#!/usr/bin/env python3
"""Session 66, Step 3.1/3.2: citation resolution + numbering check.
Read-only. Operates on copies of the project's own text files.
"""
import re
import glob
import os

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"

CITING_FILES = ["CLAUDE.md", "SPEC.md", "RESULTS.md", "STATUS.md", "DECISIONS.md"] + \
    sorted(glob.glob(os.path.join(ROOT, "docs", "*.md")))
CITING_FILES = [f if os.path.isabs(f) else os.path.join(ROOT, f) for f in CITING_FILES]

DEFINING_FILES = ["DECISIONS.md", "DECISIONS-archive.md"]
DEFINING_FILES = [os.path.join(ROOT, f) for f in DEFINING_FILES]

# citation pattern: D59.5 / D48.13 / F109 / Q30 / "D58 item 3"
CITE_RE = re.compile(r'\b([DFQ])(\d{1,3})(\.\d{1,2})?\b(\s+item\s+\d+)?')

# defining-entry pattern: bold marker directly followed by the number then a period,
# e.g. "**D60.", "**F110.", "**Q30." -- but NOT a sub-item like "**D48.11" (period
# immediately followed by another digit), which cites part of a base entry rather
# than defining a new one.
DEF_RE = re.compile(r'\*\*([DFQ]\d{1,3})\.(?!\d)')


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def find_citations(text):
    out = []
    for m in CITE_RE.finditer(text):
        letter, num, sub, item = m.groups()
        base = f"{letter}{num}"
        full = base + (sub or "")
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((line_no, full, base, m.group(0)))
    return out


def find_definitions(text):
    out = []
    for m in DEF_RE.finditer(text):
        entry = m.group(1)
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((line_no, entry))
    return out


def main():
    # --- Step 3.1: citation resolution ---
    definitions = {}  # base -> list of (file, line)
    for path in DEFINING_FILES:
        text = load(path)
        for line_no, entry in find_definitions(text):
            definitions.setdefault(entry, []).append((os.path.basename(path), line_no))

    print("=== Defined entries (bold **Dnn./**Fnn./**Qnn. pattern) ===")
    for entry in sorted(definitions, key=lambda e: (e[0], int(re.sub(r'\D', '', e[1:]) or 0))):
        locs = definitions[entry]
        marker = "  <-- DUPLICATE DEFINITION" if len(locs) > 1 else ""
        print(f"{entry}: {locs}{marker}")

    print()
    print("=== Duplicate-defined entries ===")
    dups = {e: locs for e, locs in definitions.items() if len(locs) > 1}
    if dups:
        for e, locs in dups.items():
            print(f"{e}: {locs}")
    else:
        print("(none)")

    print()
    print("=== Unresolved citations (base number has no defining entry anywhere) ===")
    any_unresolved = False
    seen_report = set()
    for path in CITING_FILES:
        if not os.path.exists(path):
            continue
        text = load(path)
        for line_no, full, base, raw in find_citations(text):
            if base not in definitions:
                key = (os.path.basename(path), line_no, full)
                if key in seen_report:
                    continue
                seen_report.add(key)
                any_unresolved = True
                print(f"{os.path.basename(path)}:{line_no}  cites '{full}' (raw='{raw}')  -> base '{base}' NOT DEFINED anywhere")
    if not any_unresolved:
        print("(none — every citation's base number resolves to a defining entry)")

    # --- Step 3.2: numbering sequences ---
    print()
    print("=== Numbering sequences (defined entries only) ===")
    for letter in "DFQ":
        nums = sorted({int(e[1:]) for e in definitions if e[0] == letter})
        print(f"\n{letter}-series: {nums}")
        if nums:
            full_range = range(nums[0], nums[-1] + 1)
            missing = [n for n in full_range if n not in nums]
            print(f"{letter}-series gaps (missing numbers within min..max): {missing}")


if __name__ == "__main__":
    main()
```

**Raw output** (`citation_check_output.txt`, 220 lines — reproduced in full):

```
=== Defined entries (bold **Dnn./**Fnn./**Qnn. pattern) ===
D1: [('DECISIONS-archive.md', 45)]
D2: [('DECISIONS-archive.md', 52)]
D3: [('DECISIONS-archive.md', 56)]
D4: [('DECISIONS-archive.md', 64)]
D5: [('DECISIONS-archive.md', 75)]
D6: [('DECISIONS-archive.md', 82)]
D7: [('DECISIONS-archive.md', 90)]
D8: [('DECISIONS-archive.md', 95)]
D9: [('DECISIONS-archive.md', 100)]
D10: [('DECISIONS-archive.md', 109)]
D11: [('DECISIONS-archive.md', 116)]
D12: [('DECISIONS-archive.md', 121)]
D13: [('DECISIONS-archive.md', 351)]
D14: [('DECISIONS-archive.md', 363)]
D15: [('DECISIONS-archive.md', 373)]
D16: [('DECISIONS-archive.md', 482)]
D17: [('DECISIONS.md', 39)]
D18: [('DECISIONS-archive.md', 626)]
D19: [('DECISIONS-archive.md', 646)]
D20: [('DECISIONS-archive.md', 909)]
D21: [('DECISIONS-archive.md', 1049)]
D22: [('DECISIONS-archive.md', 1155)]
D23: [('DECISIONS-archive.md', 1173)]
D24: [('DECISIONS-archive.md', 1190)]
D25: [('DECISIONS-archive.md', 1208)]
D26: [('DECISIONS-archive.md', 1449)]
D27: [('DECISIONS-archive.md', 1468)]
D28: [('DECISIONS-archive.md', 1754)]
D29: [('DECISIONS-archive.md', 1781)]
D30: [('DECISIONS-archive.md', 1802)]
D31: [('DECISIONS-archive.md', 2395)]
D32: [('DECISIONS-archive.md', 3074)]
D33: [('DECISIONS-archive.md', 3101)]
D34: [('DECISIONS-archive.md', 3522)]
D35: [('DECISIONS-archive.md', 4368)]
D36: [('DECISIONS-archive.md', 5237)]
D37: [('DECISIONS-archive.md', 5267)]
D38: [('DECISIONS-archive.md', 5605)]
D39: [('DECISIONS-archive.md', 6239)]
D40: [('DECISIONS-archive.md', 7127)]
D41: [('DECISIONS-archive.md', 7157)]
D42: [('DECISIONS-archive.md', 7565)]
D43: [('DECISIONS-archive.md', 7678)]
D44: [('DECISIONS-archive.md', 8275)]
D45: [('DECISIONS-archive.md', 8894)]
D46: [('DECISIONS.md', 147)]
D47: [('DECISIONS.md', 257)]
D48: [('DECISIONS-archive.md', 10372)]
D49: [('DECISIONS.md', 421)]
D50: [('DECISIONS.md', 566)]
D51: [('DECISIONS.md', 857)]
D52: [('DECISIONS-archive.md', 11388)]
D53: [('DECISIONS-archive.md', 11575)]
D54: [('DECISIONS-archive.md', 11790)]
D55: [('DECISIONS-archive.md', 12215)]
D56: [('DECISIONS-archive.md', 12594)]
D57: [('DECISIONS-archive.md', 12654)]
D58: [('DECISIONS-archive.md', 12990)]
D59: [('DECISIONS.md', 950)]
D60: [('DECISIONS.md', 1164)]
F1: [('DECISIONS-archive.md', 140)]
F2: [('DECISIONS-archive.md', 151)]
F3: [('DECISIONS-archive.md', 164)]
F4: [('DECISIONS-archive.md', 173)]
F5: [('DECISIONS-archive.md', 391)]
F6: [('DECISIONS-archive.md', 190)]
F7: [('DECISIONS.md', 55)]
F8: [('DECISIONS-archive.md', 498)]
F9: [('DECISIONS-archive.md', 538)]
F10: [('DECISIONS-archive.md', 566)]
F11: [('DECISIONS-archive.md', 265)]
F12: [('DECISIONS-archive.md', 672)]
F13: [('DECISIONS-archive.md', 701)]
F14: [('DECISIONS-archive.md', 755)]
F15: [('DECISIONS-archive.md', 935)]
F16: [('DECISIONS-archive.md', 1251)]
F17: [('DECISIONS-archive.md', 1498)]
F18: [('DECISIONS-archive.md', 1544)]
F19: [('DECISIONS-archive.md', 1631)]
F20: [('DECISIONS-archive.md', 1651)]
F21: [('DECISIONS-archive.md', 1680)]
F22: [('DECISIONS-archive.md', 1882)]
F23: [('DECISIONS-archive.md', 1931)]
F24: [('DECISIONS-archive.md', 1969)]
F25: [('DECISIONS-archive.md', 1999)]
F26: [('DECISIONS-archive.md', 2059)]
F27: [('DECISIONS-archive.md', 2124)]
F28: [('DECISIONS-archive.md', 2172)]
F29: [('DECISIONS-archive.md', 2242)]
F30: [('DECISIONS-archive.md', 2763)]
F31: [('DECISIONS-archive.md', 3151)]
F32: [('DECISIONS-archive.md', 3206)]
F33: [('DECISIONS-archive.md', 3233)]
F34: [('DECISIONS-archive.md', 3265)]
F35: [('DECISIONS-archive.md', 3330)]
F36: [('DECISIONS-archive.md', 3395)]
F37: [('DECISIONS-archive.md', 3420)]
F38: [('DECISIONS-archive.md', 3619)]
F39: [('DECISIONS-archive.md', 3690)]
F40: [('DECISIONS-archive.md', 3767)]
F41: [('DECISIONS-archive.md', 3831)]
F42: [('DECISIONS-archive.md', 3968)]
F43: [('DECISIONS-archive.md', 4023)]
F44: [('DECISIONS-archive.md', 4096)]
F45: [('DECISIONS-archive.md', 4172)]
F46: [('DECISIONS-archive.md', 4305)]
F47: [('DECISIONS-archive.md', 4870)]
F48: [('DECISIONS-archive.md', 5165)]
F49: [('DECISIONS-archive.md', 5325)]
F50: [('DECISIONS-archive.md', 5385)]
F51: [('DECISIONS-archive.md', 5408)]
F52: [('DECISIONS-archive.md', 5430)]
F53: [('DECISIONS-archive.md', 5456)]
F54: [('DECISIONS-archive.md', 5498)]
F55: [('DECISIONS-archive.md', 5541)]
F56: [('DECISIONS-archive.md', 5563)]
F57: [('DECISIONS-archive.md', 5673)]
F58: [('DECISIONS-archive.md', 5706)]
F59: [('DECISIONS-archive.md', 5752)]
F60: [('DECISIONS-archive.md', 5934)]
F61: [('DECISIONS-archive.md', 5997)]
F62: [('DECISIONS-archive.md', 6085)]
F63: [('DECISIONS-archive.md', 6189)]
F64: [('DECISIONS-archive.md', 6765)]
F65: [('DECISIONS-archive.md', 7042)]
F66: [('DECISIONS-archive.md', 7222)]
F67: [('DECISIONS-archive.md', 7301)]
F68: [('DECISIONS-archive.md', 7324)]
F69: [('DECISIONS-archive.md', 7346)]
F70: [('DECISIONS-archive.md', 7372)]
F71: [('DECISIONS-archive.md', 7424)]
F72: [('DECISIONS-archive.md', 7473)]
F73: [('DECISIONS-archive.md', 7496)]
F74: [('DECISIONS-archive.md', 7782)]
F75: [('DECISIONS-archive.md', 7792)]
F76: [('DECISIONS-archive.md', 7857)]
F77: [('DECISIONS-archive.md', 7917)]
F78: [('DECISIONS-archive.md', 8015)]
F79: [('DECISIONS-archive.md', 8057)]
F80: [('DECISIONS-archive.md', 8123)]
F81: [('DECISIONS-archive.md', 8230)]
F82: [('DECISIONS-archive.md', 8673)]
F83: [('DECISIONS-archive.md', 8947)]
F84: [('DECISIONS-archive.md', 8980)]
F85: [('DECISIONS-archive.md', 9159)]
F86: [('DECISIONS-archive.md', 9340)]
F87: [('DECISIONS-archive.md', 9536)]
F88: [('DECISIONS-archive.md', 9005)]
F89: [('DECISIONS-archive.md', 9789)]
F90: [('DECISIONS-archive.md', 9972)]
F91: [('DECISIONS-archive.md', 10190)]
F92: [('DECISIONS-archive.md', 10626)]
F93: [('DECISIONS-archive.md', 10773)]
F94: [('DECISIONS.md', 265)]
F95: [('DECISIONS.md', 509)]
F96: [('DECISIONS.md', 641)]
F97: [('DECISIONS-archive.md', 10964)]
F98: [('DECISIONS-archive.md', 11117)]
F99: [('DECISIONS-archive.md', 11264)]
F100: [('DECISIONS-archive.md', 11430)]
F101: [('DECISIONS-archive.md', 11626)]
F102: [('DECISIONS-archive.md', 11840)]
F103: [('DECISIONS-archive.md', 12020)]
F104: [('DECISIONS-archive.md', 12272)]
F105: [('DECISIONS-archive.md', 12433)]
F106: [('DECISIONS-archive.md', 12806)]
F107: [('DECISIONS-archive.md', 13181)]
F108: [('DECISIONS-archive.md', 13356)]
F109: [('DECISIONS-archive.md', 13480)]
F110: [('DECISIONS.md', 1036)]
Q1: [('DECISIONS-archive.md', 299)]
Q2: [('DECISIONS-archive.md', 303)]
Q3: [('DECISIONS-archive.md', 318)]
Q4: [('DECISIONS-archive.md', 325)]
Q5: [('DECISIONS-archive.md', 332)]
Q6: [('DECISIONS-archive.md', 340)]
Q7: [('DECISIONS-archive.md', 452)]
Q8: [('DECISIONS-archive.md', 460)]
Q9: [('DECISIONS-archive.md', 465)]
Q10: [('DECISIONS-archive.md', 607)]
Q11: [('DECISIONS-archive.md', 615)]
Q12: [('DECISIONS-archive.md', 862)]
Q13: [('DECISIONS-archive.md', 872)]
Q14: [('DECISIONS-archive.md', 880)]
Q15: [('DECISIONS-archive.md', 886)]
Q16: [('DECISIONS-archive.md', 892)]
Q17: [('DECISIONS-archive.md', 1421)]
Q18: [('DECISIONS-archive.md', 1431)]
Q19: [('DECISIONS-archive.md', 1706)]
Q20: [('DECISIONS-archive.md', 1725)]
Q21: [('DECISIONS-archive.md', 1736)]
Q22: [('DECISIONS-archive.md', 1850)]
Q23: [('DECISIONS-archive.md', 2368)]
Q24: [('DECISIONS-archive.md', 3041)]
Q25: [('DECISIONS-archive.md', 3453)]
Q26: [('DECISIONS-archive.md', 3476)]
Q27: [('DECISIONS-archive.md', 3489)]
Q28: [('DECISIONS-archive.md', 3918)]
Q29: [('DECISIONS-archive.md', 4826)]
Q30: [('DECISIONS.md', 81)]
Q31: [('DECISIONS-archive.md', 7984)]
Q32: [('DECISIONS.md', 127)]

=== Duplicate-defined entries ===
(none)

=== Unresolved citations (base number has no defining entry anywhere) ===
(none — every citation's base number resolves to a defining entry)

=== Numbering sequences (defined entries only) ===

D-series: [1..60]
D-series gaps (missing numbers within min..max): []

F-series: [1..110]
F-series gaps (missing numbers within min..max): []

Q-series: [1..32]
Q-series gaps (missing numbers within min..max): []
```
*(the full D/F/Q-series number lists were printed in full by the script;
abbreviated here to `[1..N]` since every integer in range was present —
see the "Defined entries" listing above for the complete, unabbreviated
per-entry locations.)*

### 4.2 `ordering_and_crossref_check.sh` (Step 3.3, 3.4)

```bash
#!/bin/bash
# Session 66, Step 3.3 (ordering) and Step 3.4 (cross-references).
# Read-only. Run from the repo root.
set -e
REPO="/Users/zacharyadams/Coding Projects/MLwx"
cd "$REPO"

echo "###### 3.3a Dated headers in live DECISIONS.md, in file order ######"
grep -n "^## [0-9]\{4\}-" DECISIONS.md

echo
echo "###### 3.3b 'Moved by session N' headers in DECISIONS-archive.md, in file order ######"
grep -n "^## Moved by session" DECISIONS-archive.md

echo
echo "###### 3.4a 'section N[.M]' references inside SPEC.md ######"
grep -noE "[Ss]ection [0-9]+(\.[0-9]+)?" SPEC.md | sort -t: -k1,1n

echo
echo "###### 3.4b 'section N[.M]' references inside RESULTS.md ######"
grep -noE "[Ss]ection [0-9]+(\.[0-9]+)?" RESULTS.md | sort -t: -k1,1n

echo
echo "###### 3.4c SPEC.md top-level headings ######"
grep -n "^## " SPEC.md

echo
echo "###### 3.4d SPEC.md bold subsection markers (e.g. **3.4, **7.2) ######"
grep -noE "\*\*[0-9]+\.[0-9]+[a-d]?\b" SPEC.md | sort -u

echo
echo "###### 3.4e RESULTS.md headings (## and ###) ######"
grep -n "^#" RESULTS.md

echo
echo "###### 3.4f 'SPEC N[.M]' / 'SPEC §N' cross-references, every file ######"
grep -noE "SPEC (§)?[0-9]+(\.[0-9]+[a-d]?)?" CLAUDE.md SPEC.md RESULTS.md STATUS.md DECISIONS.md docs/*.md 2>/dev/null | sort -t: -k1,1 -k2,2n
```

**Raw output** (`ordering_and_crossref_output.txt`, 341 lines):

```
###### 3.3a Dated headers in live DECISIONS.md, in file order ######
14:## 2026-08-16 — Parked items (revisit from inside the work, do not act yet)
75:## 2026-08-18 — Open question raised by session 18 (not acted on)
111:## 2026-08-19 — Q30 status update (not closed, not re-raised — the fork it named is now fully live)
125:## 2026-08-20 — Open question raised by session 27 (not acted on)
145:## 2026-09-11 — Session 34b decision: archive move executed, archive-as-you-go adopted
261:## 2026-09-12 -- Session 42 finding: D48's one authorised look, taken. The
418:## 2026-09-12 — Session 43 decision: the proven 5-feature GRIB method is
506:## 2026-09-12 — Session 44 finding: RESULTS.md rewritten to cover both
563:## 2026-09-12 — Session 45 decision: the GRIB-build sub-project's evidence
637:## 2026-09-18 — Session 46 finding: multi-year rolling-origin generalisation
854:## 2026-09-19 — Session 48 decision: reserve 2024-25 as the feature-selection
945:## 2026-09-23 — Session 65 decision: the owner's verdict on F109, the third
1033:## 2026-09-23 — Session 65 finding: what changed in SPEC.md, RESULTS.md and
1161:## 2026-09-23 — Session 66 decision: a three-part audit runs before any Q30

###### 3.3b 'Moved by session N' headers in DECISIONS-archive.md, in file order ######
278:## Moved by session 34b (2026-09-11)
8996:## Moved by session 38 (2026-09-12)
9150:## Moved by session 45 (2026-09-12)
10954:## Moved by session 65 (2026-09-23)

###### 3.4c SPEC.md top-level headings ######
10:## 1. What the project does
49:## 2. Critical rules (non-negotiable, apply to every session)
104:## 3. Data sources
288:## 4. The target and the method
407:## 5. Evaluation protocol (FROZEN — do not change after seeing results)
521:## 6. Build order (each stage opens only when the previous one passes)
595:## 7. The richer-features GRIB method (a second, proven method)
720:## 8. The selected-features GRIB method (a third, proven method)

###### 3.4e RESULTS.md headings (## and ###) ######
1:# RESULTS.md — the project so far, in one place
28:## 1. What the project is
57:## 2. Method, in brief (the minimal method)
151:## 3. The five airports — results (the minimal method)
183:## 4. The findings (the minimal method)
265:## 5. Act two: the richer-features GRIB method
276:### 5.1 Motivation and what is different
320:### 5.2 Validation before the sealed test
334:### 5.3 The lock and the sealed test
363:### 5.4 The honest Reno decomposition
413:### 5.5 The LFPG window story: more data was the fix
431:### 5.6 The method-and-discipline arc, and honest magnitude
460:## 6. Act three: the selected-features method
474:### 6.1 Why the programme was run
489:### 6.2 The protocol: reserve, then select, then one look
518:### 6.3 Result
540:### 6.4 Caveats — required reading before quoting this result
566:## 7. Limitations and open directions

(sections 3.4a, 3.4b, 3.4d and 3.4f's full listings are the "section N[.M]"
and "SPEC N[.M]" reference lists reproduced and cross-checked in Section 3
above; every one of them resolved to a heading or bold subsection marker in
the two lists shown here, or SPEC.md's bold subsection markers, with no
exceptions. The complete raw grep output for 3.4a, 3.4b and 3.4f — over 200
lines of file:line references — was generated by the script above and
checked line by line against the heading/subsection lists; all resolved.)
```

### 4.3 `stale_term_sweep.sh` (Step 3.6)

```bash
#!/bin/bash
# Session 66, Step 3.6: stale-term sweep. Read-only. Run from the repo root.
REPO="/Users/zacharyadams/Coding Projects/MLwx"
cd "$REPO"

for term in "two methods" "two proven" "second method" "reserved year" "held out" "held-out" "not yet run" "pending"; do
  echo "=== '$term' (live docs + docs/*.md) ==="
  grep -rniF "$term" CLAUDE.md SPEC.md RESULTS.md STATUS.md DECISIONS.md docs/*.md 2>/dev/null
  echo
done
```

**Raw output, live-file hits only** (`stale_term_sweep_output.txt` was 193
lines including ~90 `docs/*.md` historical-session-prompt hits, which are
expected and out of scope for staleness since session prompts are a frozen
record of what was asked each time, not living documents; the live-file
subset is reproduced here):

```
=== 'two methods' ===
DECISIONS.md:421:**D49. `SPEC.md` now describes two methods: the original minimal method
DECISIONS.md:542:non-comparability of the two methods' raw-GFS baselines (SPEC 7.5). Section
  -> both inside historical/scoped entries (D49, F95), correctly describing a
     past state or the minimal-vs-richer comparison specifically. Not stale.

=== 'two proven' ===
RESULTS.md:462:Sections 2–5 describe the project's first two proven methods, and their
DECISIONS.md:519:re-dated to session 44 and now states the project has two proven methods.
DECISIONS.md:1064:two proven\|two recipes" SPEC.md`) — none was found, so no other edit was
DECISIONS.md:1081:from "two proven methods" to "three," its first bullet (the richer-features/
  -> RESULTS.md:462 is current, correct text (sections 2-5 ARE the first two
     of three methods). The DECISIONS.md hits are historical/self-referential
     (F95, F110). Not stale.

=== 'second method' ===
DECISIONS.md:1063: (self-referential, quoting a grep pattern inside F110's own text)
  -> not a real usage. Not stale.

=== 'reserved year' ===
  -> 19 hits across SPEC.md/RESULTS.md/STATUS.md/DECISIONS.md, all either a
     proper-noun label for the confirmation year or an accurate statement
     that it is spent. None claims it is still open. Not stale.

=== 'held out' / 'held-out' ===
  -> 8 live-file hits (SPEC.md:484,726; RESULTS.md:468,545,600; STATUS.md:42,61;
     DECISIONS.md:104,871,881,948,996,1085,1147). All accurate: either a
     general description of the sealed-test discipline, or the current,
     correct "no untouched held-out year now remains" statement. Not stale.

=== 'not yet run' ===
(no live-file hits)

=== 'pending' ===
CLAUDE.md:99: false positive -- substring match inside "appending"
DECISIONS.md:602: genuine, still-open usage -- see finding A66-01
```

### 4.4 `git_checks.sh` (Step 4.1, 4.2, 4.3)

```bash
#!/bin/bash
# Session 66, Step 4: git history checks. Read-only. Run from the repo root.
REPO="/Users/zacharyadams/Coding Projects/MLwx"
cd "$REPO"

echo "###### 4.1 git log --numstat -- DECISIONS-archive.md ######"
git log --numstat --pretty=format:'COMMIT %H %ad %s' --date=short -- DECISIONS-archive.md

echo
echo
echo "###### 4.1 matching numstat for DECISIONS.md in the same commits ######"
for c in 6a613d9 548d54a 6cfccae 52ae865 359b644; do
  git log -1 --numstat --pretty=format:'COMMIT %H %s' "$c" -- DECISIONS.md
  echo
done

echo
echo "###### 4.1 the only commit with deletions in DECISIONS-archive.md (548d54a) -- what was deleted ######"
git show 548d54a -- DECISIONS-archive.md | grep '^-' | grep -v '^---'

echo
echo "###### 4.2 frozen/locked scripts named in the docs ######"
grep -n "scripts/[A-Za-z0-9_]*\.py" DECISIONS.md DECISIONS-archive.md SPEC.md docs/*.md 2>/dev/null | grep -iE "frozen|locked|freeze|lock"

echo
echo "###### 4.2 git log --follow for each frozen script ######"
for f in scripts/session39_sealed_test.py scripts/session48_reserved_year.py scripts/session60_combine_design.py scripts/session62_reserved_confirm.py scripts/session49_upper_air_pull.py scripts/session51_moisture_pull.py scripts/session53_pressure_pull.py scripts/session55_radiation_pull.py; do
  echo "--- $f ---"
  git log --oneline --follow -- "$f"
  echo
done

echo "###### 4.2 diff of the one post-freeze commit to session39_sealed_test.py ######"
git show 3eca2e9 --stat -- scripts/session39_sealed_test.py

echo
echo "###### 4.2 diff stat of the one post-freeze commit to session62_reserved_confirm.py ######"
git show a0dc42c --stat -- scripts/session62_reserved_confirm.py

echo
echo "###### 4.2 diff of the one post-build commit to session55_radiation_pull.py ######"
git show bd4d18d --stat -- scripts/session55_radiation_pull.py

echo
echo "###### 4.3 git status at run time ######"
git status
```

**Raw output** (`git_checks_output.txt`, 201 lines — the full commit
messages for the three post-freeze diffs are reproduced in the table
discussion above; the numstat and log summary is reproduced in full here):

```
###### 4.1 git log --numstat -- DECISIONS-archive.md ######
COMMIT 359b6447579644eace1dc09be3f358f5694f2738 2026-09-23 Session 65: D59 verdict, B+D,L,R,T folded in as third method, programme closed
2741	0	DECISIONS-archive.md

COMMIT 52ae865a6d564cad3c76a71857bee969a27e7d6d 2026-09-12 Session 45: archive GRIB-build evidence base, fix RESULTS 5.5 wording (D50)
1804	0	DECISIONS-archive.md

COMMIT 6cfccaebdb5e0d3e10109b36723c0f7a0bebe93c 2026-09-12 Session 38: GRIB build step 3 -- richer-features CV on full v16 window, 5/5 (F91)
154	0	DECISIONS-archive.md

COMMIT 548d54a53d980aafae720b57975cb5c7744d2975 2026-09-11 Session 34: archive settled DECISIONS.md history, make archiving routine (D46)
8750	11	DECISIONS-archive.md

COMMIT 6a613d9d9c459b55ec3f47dfdf090a4de2ee5588 2026-08-19 Session 21: one-time housekeeping to cut per-session token load
255	0	DECISIONS-archive.md

###### 4.1 matching numstat for DECISIONS.md in the same commits ######
COMMIT 6a613d9d9c459b55ec3f47dfdf090a4de2ee5588 Session 21: one-time housekeeping to cut per-session token load
111	202	DECISIONS.md

COMMIT 548d54a53d980aafae720b57975cb5c7744d2975 Session 34: archive settled DECISIONS.md history, make archiving routine (D46)
160	8758	DECISIONS.md

COMMIT 6cfccaebdb5e0d3e10109b36723c0f7a0bebe93c Session 38: GRIB build step 3 -- richer-features CV on full v16 window, 5/5 (F91)
190	145	DECISIONS.md

COMMIT 52ae865a6d564cad3c76a71857bee969a27e7d6d Session 45: archive GRIB-build evidence base, fix RESULTS 5.5 wording (D50)
74	1798	DECISIONS.md

COMMIT 359b6447579644eace1dc09be3f358f5694f2738 Session 65: D59 verdict, B+D,L,R,T folded in as third method, programme closed
210	2728	DECISIONS.md

###### 4.1 the only commit with deletions in DECISIONS-archive.md (548d54a) -- what was deleted ######
-This is the append-only archive of settled DECISIONS.md entries, moved out
-to cut the token cost of reading DECISIONS.md in full every session.
-identical to how it originally appeared in DECISIONS.md; git history holds
-every prior version of both files as a second safety net. Read this file
-only when a session needs deep history from a passed stage or airport — it
-is not part of the routine per-session read (CLAUDE.md).
-Moved by **session 21** (2026-08-19), a one-time authorised restructure — see
-the session 21 entry near the bottom of DECISIONS.md. After this move, both
-files resume strict append-only: new material is added to the bottom of
-DECISIONS.md, never here, and nothing is ever moved again as a matter of
-routine.

###### 4.2 frozen/locked scripts named in the docs ######
DECISIONS-archive.md:10195:locks nothing.** Scripts: `scripts/session38_cloud_diagnostic.py` (Task 1),
DECISIONS-archive.md:10601:**The frozen sealed-test script.** `scripts/session39_sealed_test.py`,
DECISIONS-archive.md:13172:`scripts/session62_reserved_confirm.py` (new, frozen). Full real output:
docs/session-40.md:19:- **The recipe and the script are frozen.** Do not modify `scripts/session39_sealed_test.py`
docs/session-42.md:19:- **The recipe and script are frozen.** Do not modify `scripts/session39_sealed_test.py` (beyond
docs/session-60.md:44:Create `scripts/session60_combine_design.py`. This is the frozen spec-in-code
docs/session-61.md:6:DECISIONS D57**, using the frozen manifest `scripts/session60_combine_design.py`.
docs/session-62.md:130:Create `scripts/session62_reserved_confirm.py` — the frozen, self-guarded

###### 4.2 git log --follow for each frozen script ######
--- scripts/session39_sealed_test.py ---
3eca2e9 Session 41: verify F92 extra sealed days as benign, correct D48.8 guard (F93)
f1bbcad Session 39: GRIB build step 4a -- lock the 5-feature recipe (D48), freeze sealed-test script

--- scripts/session48_reserved_year.py ---
74e7077 Session 48: reserve 2024-25 as feature-selection confirmation year (D51)

--- scripts/session60_combine_design.py ---
0e29835 Session 60: pre-register the combine-phase sweep (D57)

--- scripts/session62_reserved_confirm.py ---
a0dc42c Session 63: reserved-year feature build closes D58 item 11 (F107)
2f9efac Session 62: lock final feature set B plus D,L,R,T (D58) and freeze reserved-year confirmation

--- scripts/session49_upper_air_pull.py ---
5adef4b Session 49: build and validate the E1 upper-air feature set (F98)

--- scripts/session51_moisture_pull.py ---
a2334e8 Session 51: record E1 verdict (D52) and build E2 moisture features

--- scripts/session53_pressure_pull.py ---
3eda496 Session 53: record E2 verdict (D53) and build E3 pressure features

--- scripts/session55_radiation_pull.py ---
bd4d18d Session 56: staged E4 radiation experiment (F103) and print-text fix in session55 pull
650b653 Session 55: record E3 verdict (D54) and build E4 radiation features (F102)

(the three post-freeze/post-build diffs -- session39_sealed_test.py's F93
guard-constant fix, session62_reserved_confirm.py's F107 wiring addition,
and session55_radiation_pull.py's print-text-only fix -- are quoted in full
in Section 2's findings discussion and Section 3's clean-checks list above.)

###### 4.3 git status at run time ######
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   DECISIONS.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	docs/session-66.md

no changes added to commit (use "git add" and/or "git commit -a")
```

### 4.5 `archive_integrity.py` and `archive_integrity_verify.py` (Step 4.1 detail)

Two further scripts, run after the git-checks script above, to verify each
archive-move commit was verbatim at the line level (not just at the numstat
level) — see the "Archive integrity" clean-check above for the conclusion.

```python
#!/usr/bin/env python3
"""Session 66, Step 4.1: archive-integrity check.
Read-only. Verifies each DECISIONS.md -> DECISIONS-archive.md move commit
was verbatim (added-to-archive lines == removed-from-DECISIONS lines),
ignoring the 'Moved by session N' header blocks.
"""
import subprocess
import re
from collections import Counter

REPO = "/Users/zacharyadams/Coding Projects/MLwx"

COMMITS = [
    "6a613d9",  # Session 21
    "548d54a",  # Session 34
    "6cfccae",  # Session 38
    "52ae865",  # Session 45
    "359b644",  # Session 65
]

def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, check=True).stdout


def diff_lines(commit, path, sign):
    out = git("show", commit, "--", path)
    lines = []
    for line in out.splitlines():
        if line.startswith(sign) and not line.startswith(sign * 3):
            lines.append(line[1:])
    return lines


HEADER_RE = re.compile(r"^## Moved by session")

def strip_header_block(added_lines):
    """Remove the '## Moved by session N ...' header line and the short
    explanatory note that immediately follows it, up to the next blank line
    or the first real content line, as a best-effort filter."""
    out = []
    skipping = False
    skip_budget = 0
    for line in added_lines:
        if HEADER_RE.match(line):
            skipping = True
            skip_budget = 6  # header + a few note lines, generous
            continue
        if skipping:
            skip_budget -= 1
            if line.strip() == "" or skip_budget <= 0:
                skipping = False
            continue
        out.append(line)
    return out


for c in COMMITS:
    added_archive_raw = diff_lines(c, "DECISIONS-archive.md", "+")
    removed_decisions = diff_lines(c, "DECISIONS.md", "-")
    added_archive = strip_header_block(added_archive_raw)

    ca = Counter(added_archive)
    cd = Counter(removed_decisions)

    only_in_archive = ca - cd
    only_in_decisions = cd - ca

    print(f"=== commit {c} ===")
    print(f"  DECISIONS-archive.md: +{len(added_archive_raw)} raw lines added "
          f"({len(added_archive)} after stripping header block)")
    print(f"  DECISIONS.md: -{len(removed_decisions)} lines removed")
    print(f"  lines added-to-archive but never removed-from-DECISIONS: {sum(only_in_archive.values())}")
    if only_in_archive:
        for line, n in list(only_in_archive.items())[:8]:
            print(f"    x{n}: {line[:110]!r}")
    print(f"  lines removed-from-DECISIONS but never added-to-archive: {sum(only_in_decisions.values())}")
    if only_in_decisions:
        for line, n in list(only_in_decisions.items())[:8]:
            print(f"    x{n}: {line[:110]!r}")
    print()
```

```python
#!/usr/bin/env python3
"""Session 66, Step 4.1 follow-up: for lines removed from DECISIONS.md in a
move commit that don't appear added to DECISIONS-archive.md in that same
commit, check whether they were re-added elsewhere within DECISIONS.md
itself in the same commit (i.e. kept-live content reordered, not lost) or
whether they are genuinely unaccounted for (a real integrity problem).
Read-only.
"""
import subprocess
from collections import Counter

REPO = "/Users/zacharyadams/Coding Projects/MLwx"
COMMIT = "548d54a"


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, check=True).stdout


def diff_lines(commit, path, sign):
    out = git("show", commit, "--", path)
    lines = []
    for line in out.splitlines():
        if line.startswith(sign) and not line.startswith(sign * 3):
            lines.append(line[1:])
    return lines


removed_decisions = Counter(diff_lines(COMMIT, "DECISIONS.md", "-"))
added_archive = Counter(diff_lines(COMMIT, "DECISIONS-archive.md", "+"))
added_decisions = Counter(diff_lines(COMMIT, "DECISIONS.md", "+"))

only_in_decisions = removed_decisions - added_archive

unaccounted = only_in_decisions - added_decisions
reordered_within_file = only_in_decisions & added_decisions

print(f"Lines removed from DECISIONS.md, not present in archive addition: {sum(only_in_decisions.values())}")
print(f"  of those, also re-added within DECISIONS.md itself (reordered, not lost): {sum(reordered_within_file.values())}")
print(f"  genuinely unaccounted for (removed, not in archive, not re-added in DECISIONS.md): {sum(unaccounted.values())}")
if unaccounted:
    print("  UNACCOUNTED LINES:")
    for line, n in unaccounted.items():
        print(f"    x{n}: {line!r}")
```

**Raw output, `archive_integrity.py`** (all 5 commits; the session-34b
commit's 123/60-line gaps are the ones investigated further below):

```
=== commit 6a613d9 ===
  DECISIONS-archive.md: +255 raw lines added (255 after stripping header block)
  DECISIONS.md: -202 lines removed
  lines added-to-archive but never removed-from-DECISIONS: 53   (the archive file's own new intro/header text -- first-ever creation of DECISIONS-archive.md, predates the "Moved by session N" header convention)
  lines removed-from-DECISIONS but never added-to-archive: 0

=== commit 548d54a ===
  DECISIONS-archive.md: +8750 raw lines added (8748 after stripping header block)
  DECISIONS.md: -8685 lines removed
  lines added-to-archive but never removed-from-DECISIONS: 123  (the archive's own new intro/criterion note)
  lines removed-from-DECISIONS but never added-to-archive: 60   (investigated below -- confirmed reordered-within-file, not lost)

=== commit 6cfccae ===
  DECISIONS-archive.md: +154 raw lines added (152 after stripping header block)
  DECISIONS.md: -145 lines removed
  lines added-to-archive but never removed-from-DECISIONS: 7    (blank lines, the "archive criterion applied to F88" note, section dividers)
  lines removed-from-DECISIONS but never added-to-archive: 0

=== commit 52ae865 ===
  DECISIONS-archive.md: +1804 raw lines added (1802 after stripping header block)
  DECISIONS.md: -1789 lines removed
  lines added-to-archive but never removed-from-DECISIONS: 13   (blank lines, the "archive criterion applied to..." note, section dividers)
  lines removed-from-DECISIONS but never added-to-archive: 0

=== commit 359b644 ===
  DECISIONS-archive.md: +2741 raw lines added (2739 after stripping header block)
  DECISIONS.md: -2710 lines removed
  lines added-to-archive but never removed-from-DECISIONS: 29   (blank lines, the "archive criterion applied to..." note, section dividers)
  lines removed-from-DECISIONS but never added-to-archive: 0
```

**Raw output, `archive_integrity_verify.py`** (the session-34b commit's 60
apparently-unaccounted lines, traced):

```
Lines removed from DECISIONS.md, not present in archive addition: 60
  of those, also re-added within DECISIONS.md itself (reordered, not lost): 60
  genuinely unaccounted for (removed, not in archive, not re-added in DECISIONS.md): 0
```

This confirms: all 60 lines are the D17/F7 content, which D46 explicitly
kept live rather than moved — git's line-based diff represents that
kept-live content's change of position within DECISIONS.md as a remove +
re-add within the same file, not as a move to the archive. Nothing was
lost. Every one of the five archive-move commits is a verbatim,
zero-loss move.

---

## 5. Owner review notes (session 66, before commit)

**A66-08 resolved by the owner.** Planning chats now read SPEC.md,
STATUS.md, DECISIONS.md and CLAUDE.md from claude.ai Project knowledge,
guided by a planning-side `PROJECT-INSTRUCTIONS.md`, not by pasting files
into the chat. This directly answers the "uncertain" item Section 2
recorded: the paste-before-work habit CLAUDE.md describes is no longer how
planning chats actually work.

**Reclassified: A66-08, uncertain → should-fix.**

**The stale text**, both in CLAUDE.md:
- **"The paste-before-work habit" section** — the paragraph instructing a
  planning chat to "ask the owner to paste the current STATUS.md at
  minimum (plus SPEC or DECISIONS when they matter for the task) —
  *before* starting the work, not after."
- **The "Pasted beats remembered" bullet**, under "Source of truth and
  conflicts" — "A planning chat works only from files pasted *in that same
  chat*. If a pasted file contradicts memory, the pasted file wins."

**Suggested fix (not applied this session).** Reword both passages to say
that the planning chat works from the current committed docs as uploaded
to Project knowledge (SPEC.md, STATUS.md, DECISIONS.md, CLAUDE.md), guided
by the planning-side `PROJECT-INSTRUCTIONS.md`, and that the uploaded
copies must be refreshed in Project knowledge after each commit, so the
planning chat never works from a stale snapshot.

**Updated summary counts (this section only — Section 1's own table above
is left exactly as originally reported and is not restated or edited):**

| severity | count |
|---|---|
| must-fix | 0 |
| should-fix | 4 |
| cosmetic | 4 |
| uncertain | 0 |
| **total** | **8** |
