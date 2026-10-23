# Superseded files in this folder (DECISIONS D116.6)

| superseded (kept unchanged) | replaced by |
|---|---|
| `part1.md` | `part1_s122.md` |
| `part2_comparisons.md` | `part2_comparisons_s122.md` |

**Why.** Session 114 wrote `part1.md` and `part2_comparisons.md` once, as the
text of ANALYSIS.md's Part 1 and of its Part 2 comparisons section, before
ECMWF IFS was pulled. Session 117 then added IFS to ANALYSIS.md (D111,
F160), so these two files no longer match it (F163 rows A01 and C08), and
session 114's `--verify` fails on Part 1.

**What replaces them.** `scripts/session122_analysis.py` renders the two
parts from session 114's code and tables, session 117's IFS tables and text,
and session 122's text and figure names (D116.7, D116.8). Its `--render`
wrote the two `_s122.md` files, write-once; its `--verify` checks
ANALYSIS.md against that render and supersedes session 114's `--verify`.

**What is kept.** The old two files are write-once and stay as written, so
they still show what session 114 rendered. `scripts/session114_comparisons.py`
is not edited, because session 117 records its SHA-256 (D116.10).
