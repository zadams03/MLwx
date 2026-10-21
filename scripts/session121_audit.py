"""Session 121: the project health check, audit part 2 (the record).

Read-only (D114.4, D115.4). Standard library only. Offline. Each mode
prints a short summary and writes its full table to
data/processed/session121_audit/ (D93.12).

Modes (one per run):
  --citations  every Dnn/Fnn reference in the audited files must resolve to
               an entry in DECISIONS.md or DECISIONS-archive.md; a reference
               to a sub-item (D105.5, F163.10, D105.5(k)) must resolve to
               that item's label inside the entry. Writes citations.csv and
               citations_by_file.csv.
  --spec       SPEC 3.4's two markers (register S05): counts, the span's
               line range and SHA-256, and an independent parse of its two
               tables. Writes spec_span.txt.
  --archive    both DECISIONS files by script: opening lines once across
               both files, dated headings in order, numbers missing from
               the sequence, and the Live index against the entries present.
               Writes archive.txt.
  --paths      every file path named in RESULTS, ANALYSIS and the READMEs
               exists. Writes paths.csv.
  --sync       the eight Project-knowledge files of D115.5: bytes and
               SHA-256 at HEAD, and the commits after each listed date.
               Writes sync.csv.

A citation is D or F, digits, then optional .digits parts, then optional
(letter or number) parts, not inside a longer word or number. 'Table D1'
style labels (ANALYSIS.md's tables) are listed as excluded, not checked.
"""

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed" / "session121_audit"

AUDITED = [
    "SPEC.md", "STATUS.md", "DECISIONS.md", "RESULTS.md", "ANALYSIS.md",
    "README.md", "scripts/README.md", "data/README.md", "docs/README.md",
    "notes/README.md", "CLAUDE.md", "docs/PROJECT-INSTRUCTIONS.md",
]
CITE_RE = re.compile(
    r"(?<![A-Za-z0-9_])([DF])(\d+)((?:\.\d+)*)((?:\([a-z0-9]{1,4}\))*)(?![A-Za-z0-9_])")
# A table label, not a citation: 'Table D1', 'Tables E1 to E16, D1'.
TABLE_RE = re.compile(r"Tables?\s+(?:[A-Z]\d+(?:\s*(?:to|,|and)\s*)?)*$")
OPEN_RE = re.compile(r"^\*\*([DF]\d+)\. ")
DATED_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})")

# D115.5: the eight files Project knowledge holds, with their listed dates.
PK_FILES = [
    ("ANALYSIS.md", "ANALYSIS.md", "2026-10-21"),
    ("DECISIONS.md", "DECISIONS.md", "2026-10-21"),
    ("STATUS.md", "STATUS.md", "2026-10-21"),
    ("DECISIONS-archive.md", "DECISIONS-archive.md", "2026-10-18"),
    ("PROJECT-INSTRUCTIONS.md", "docs/PROJECT-INSTRUCTIONS.md", "2026-10-07"),
    ("SPEC.md", "SPEC.md", "2026-10-07"),
    ("CLAUDE.md", "CLAUDE.md", "2026-10-07"),
    ("RESULTS.md", "RESULTS.md", "2026-09-29"),
]

SPEC_START = "**3.4 The airport table.**"
SPEC_END = "Notes on the table:"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def entries(text, fname):
    """Each entry: number -> (file, first line, list of its lines).

    An entry starts at its first opening line ('**D12. ') and ends before
    the next '---' line or the next entry's opening line."""
    lines = text.split("\n")
    out, cur = {}, None
    for i, l in enumerate(lines):
        m = OPEN_RE.match(l)
        if m:
            cur = m.group(1)
            out.setdefault(cur, []).append((fname, i + 1, []))
        elif l == "---":
            cur = None
            continue
        if cur:
            out[cur][-1][2].append(l)
    return out


def all_entries():
    e = {}
    for fname in ("DECISIONS.md", "DECISIONS-archive.md"):
        for k, v in entries(read(ROOT / fname), fname).items():
            e.setdefault(k, []).extend(v)
    return e


def sub_item(lines, label):
    """The lines of sub-item `label` (e.g. 'D105.5') inside an entry, or None.

    A label counts when it opens a list item or a bold span: '- **D105.5',
    '**D105.5' or '- D105.5'. A wrapped line that merely starts with the
    label's text is not enough."""
    pat = re.compile(r"^\s*(?:[-*]\s+\*\*|\*\*|[-*]\s+)\(?" + re.escape(label) + r"(?![\d])")
    bold = re.compile(r"\*\*" + re.escape(label) + r"(?![\d.])")
    start = None
    for i, l in enumerate(lines):
        if pat.match(l) or bold.search(l):
            start = i
            break
    if start is None:
        return None
    # The item runs to the next sibling or parent label.
    base = label.split(".")[0]
    nxt = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*)?" + re.escape(base) + r"\.\d")
    body = [lines[start]]
    for l in lines[start + 1:]:
        if nxt.match(l):
            break
        body.append(l)
    return body


def resolve(ent, num, dots, parens):
    """Return (status, where). status: resolved, unresolved-entry,
    unresolved-item, unresolved-letter, both-files."""
    if num not in ent:
        return "unresolved-entry", ""
    places = ent[num]
    files = {p[0] for p in places}
    where = "; ".join(f"{p[0]}:{p[1]}" for p in places)
    if len(files) > 1:
        return "both-files", where
    lines = [l for p in places for l in p[2]]
    if dots:
        label = num + dots
        body = sub_item(lines, label)
        if body is None:
            return "unresolved-item", where
        lines = body
    if parens:
        first = re.findall(r"\(([a-z0-9]{1,4})\)", parens)[0]
        text = "\n".join(lines)
        if not re.search(r"(?:^|[\s(*])\(" + re.escape(first) + r"\)", text, re.M):
            return "unresolved-letter", where
    return "resolved", where


def mode_citations():
    ent = all_entries()
    rows, per = [], {}
    for fname in AUDITED:
        path = ROOT / fname
        c = per.setdefault(fname, {"refs": 0, "resolved": 0, "unresolved": 0,
                                   "excluded": 0, "sub_refs": 0})
        for i, l in enumerate(read(path).split("\n")):
            for m in CITE_RE.finditer(l):
                num = m.group(1) + m.group(2)
                dots, parens = m.group(3), m.group(4)
                ref = m.group(0)
                if TABLE_RE.search(l[:m.start()]):
                    c["excluded"] += 1
                    rows.append([fname, i + 1, ref, "excluded: table label", ""])
                    continue
                c["refs"] += 1
                if dots or parens:
                    c["sub_refs"] += 1
                status, where = resolve(ent, num, dots, parens)
                c["resolved" if status == "resolved" else "unresolved"] += 1
                rows.append([fname, i + 1, ref, status, where])
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "citations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "line", "reference", "status", "entry_at"])
        w.writerows(rows)
    with open(OUT / "citations_by_file.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "references", "sub_item_references", "resolved",
                    "unresolved", "excluded_table_labels"])
        for fname, c in per.items():
            w.writerow([fname, c["refs"], c["sub_refs"], c["resolved"],
                        c["unresolved"], c["excluded"]])
    tot = {k: sum(c[k] for c in per.values()) for k in ("refs", "resolved", "unresolved", "excluded")}
    for fname, c in per.items():
        print(f"{fname}: refs {c['refs']} (sub-item {c['sub_refs']}), resolved "
              f"{c['resolved']}, unresolved {c['unresolved']}, excluded {c['excluded']}")
    print(f"TOTAL refs {tot['refs']}, resolved {tot['resolved']}, unresolved "
          f"{tot['unresolved']}, excluded {tot['excluded']}")
    kinds = {}
    for r in rows:
        if r[3] not in ("resolved",) and not r[3].startswith("excluded"):
            kinds[r[3]] = kinds.get(r[3], 0) + 1
    print("unresolved by kind:", kinds or "none")


def mode_spec():
    text = read(ROOT / "SPEC.md")
    lines = text.split("\n")
    s = [i + 1 for i, l in enumerate(lines) if l.startswith(SPEC_START)]
    e = [i + 1 for i, l in enumerate(lines) if l.startswith(SPEC_END)]
    s_any = text.count(SPEC_START)
    e_any = text.count(SPEC_END)
    out = [f"start marker {SPEC_START!r}: {s_any} occurrence(s), at line start {s}",
           f"end marker {SPEC_END!r}: {e_any} occurrence(s), at line start {e}"]
    ok = s_any == 1 and e_any == 1 and len(s) == 1 and len(e) == 1 and s[0] < e[0]
    if ok:
        span = "\n".join(lines[s[0] - 1:e[0]]) + "\n"
        digest = hashlib.sha256(span.encode("utf-8")).hexdigest()
        out.append(f"span: lines {s[0]} to {e[0]} inclusive ({e[0] - s[0] + 1} lines), "
                   f"{len(span.encode('utf-8'))} bytes, each line followed by a newline")
        out.append(f"span SHA-256: {digest}")
        # Independent parse: each markdown table in the span.
        tables, cur = [], None
        for l in lines[s[0] - 1:e[0]]:
            if l.startswith("|"):
                cells = [c.strip() for c in l.strip().strip("|").split("|")]
                if cur is None:
                    cur = {"header": cells, "rows": []}
                    tables.append(cur)
                elif set("".join(cells)) <= set("-: "):
                    continue
                else:
                    cur["rows"].append(cells)
            else:
                cur = None
        for n, t in enumerate(tables, 1):
            widths = {len(r) for r in t["rows"]}
            codes = [r[0] for r in t["rows"]]
            out.append(f"table {n}: {len(t['rows'])} rows, {len(t['header'])} columns "
                       f"(row widths {sorted(widths)}), codes {codes}")
            out.append(f"  header: {t['header']}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "spec_span.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(l for l in out if not l.startswith("  header")))
    print("PASS" if ok else "FAIL: marker missing, doubled or out of order")
    return 0 if ok else 1


def mode_archive():
    live = read(ROOT / "DECISIONS.md")
    arch = read(ROOT / "DECISIONS-archive.md")
    out, counts = [], {}
    for fname, text in (("DECISIONS.md", live), ("DECISIONS-archive.md", arch)):
        for i, l in enumerate(text.split("\n")):
            m = OPEN_RE.match(l)
            if m:
                counts.setdefault(m.group(1), []).append(f"{fname}:{i + 1}")
    doubled = {k: v for k, v in counts.items() if len(v) > 1}
    for kind in "DF":
        nums = sorted(int(k[1:]) for k in counts if k[0] == kind)
        missing = sorted(set(range(1, nums[-1] + 1)) - set(nums))
        out.append(f"{kind}: {len(nums)} entries, highest {kind}{nums[-1]}, "
                   f"missing from 1..{nums[-1]}: {len(missing)} {missing}")
    for fname, text in (("DECISIONS.md", live), ("DECISIONS-archive.md", arch)):
        prev, bad, n = None, [], 0
        for i, l in enumerate(text.split("\n")):
            m = DATED_RE.match(l)
            if m:
                n += 1
                if prev and m.group(1) < prev[0]:
                    bad.append(f"line {i + 1}: {m.group(1)} after {prev[0]}")
                prev = (m.group(1), i + 1)
        out.append(f"{fname}: {n} dated headings, out of order {len(bad)}")
        out.extend(f"  {b}" for b in bad)
        # Entry numbers in file order: each kind should rise.
        seq = [int(m.group(1)[1:]) if m else None for m in
               (OPEN_RE.match(l) for l in text.split("\n"))]
        for kind in "DF":
            order = [int(l[3:].split(".")[0]) for l in text.split("\n")
                     if OPEN_RE.match(l) and l[2] == kind]
            falls = [(a, b) for a, b in zip(order, order[1:]) if b < a]
            out.append(f"  {kind} numbers in file order: {len(order)}, falls {len(falls)} {falls[:10]}")
    out.append(f"opening lines doubled across both files: {len(doubled)}")
    out.extend(f"  {k}: {v}" for k, v in sorted(doubled.items()))
    # The Live index against the entries present.
    idx = re.search(r"<!-- live-index-start -->\n(.*?)<!-- live-index-end -->", live, re.S)
    listed = re.findall(r"^- ([DF]\d+):", idx.group(1), re.M) if idx else []
    present = [m.group(1) for m in (OPEN_RE.match(l) for l in live.split("\n")) if m]
    out.append(f"Live index: {len(listed)} listed {listed}")
    out.append(f"entries present in DECISIONS.md: {len(present)} {present}")
    out.append(f"listed but not present: {sorted(set(listed) - set(present))}; "
               f"present but not listed: {sorted(set(present) - set(listed))}")
    out.append(f"DECISIONS.md bytes: {len(live.encode('utf-8'))}; "
               f"DECISIONS-archive.md bytes: {len(arch.encode('utf-8'))}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "archive.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


PATH_RE = re.compile(r"`([^`\s]+)`")
EXT_RE = re.compile(r"\.(py|md|csv|txt|svg|png|json|yml|yaml|tar|gz|parquet|cfg|toml|ini)$")
PATH_FILES = ["RESULTS.md", "ANALYSIS.md", "README.md", "scripts/README.md",
              "data/README.md", "docs/README.md", "notes/README.md"]


def mode_paths():
    tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout.split("\n"))
    rows, per = [], {}
    for fname in PATH_FILES:
        here = (ROOT / fname).parent
        c = per.setdefault(fname, [0, 0, 0, 0])
        for i, l in enumerate(read(ROOT / fname).split("\n")):
            # Backticked tokens, and markdown link targets.
            toks = PATH_RE.findall(l) + re.findall(r"\]\(([^)\s#]+)\)", l)
            for t in toks:
                t = t.rstrip(".,;:")
                if t.startswith(("http://", "https://", "--", "-")):
                    continue
                if not ("/" in t or EXT_RE.search(t)):
                    continue
                if any(x in t for x in ("NN", "<", "YYYY", "{", "$")):
                    c[3] += 1
                    rows.append([fname, i + 1, t, "pattern", ""])
                    continue
                c[0] += 1
                found = ""
                for base, name in ((ROOT, "root"), (here, "folder")):
                    p = (base / t).resolve()
                    if "*" in t:
                        if list(base.glob(t)):
                            found = f"{name} (glob)"
                            break
                    elif p.exists():
                        if not str(p).startswith(str(ROOT) + "/"):
                            found = name + ", outside the repo"
                            break
                        rel = str(p.relative_to(ROOT))
                        found = name + ("" if rel in tracked or p.is_dir() else ", untracked")
                        break
                if not found and "/" not in t:
                    # A bare file name: look for it by name among tracked files.
                    hits = [x for x in tracked if x.endswith("/" + t) or x == t]
                    if hits:
                        found = "by name: " + "; ".join(sorted(hits)[:3])
                if found:
                    c[1] += 1
                else:
                    c[2] += 1
                rows.append([fname, i + 1, t, "exists" if found else "MISSING", found])
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "paths.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "line", "path", "result", "resolved_from"])
        w.writerows(rows)
    for fname, c in per.items():
        print(f"{fname}: paths {c[0]}, exist {c[1]}, missing {c[2]}, patterns {c[3]}")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def mode_sync():
    rows, total = [], 0
    for pk, repo, listed in PK_FILES:
        blob = subprocess.run(["git", "show", f"HEAD:{repo}"], cwd=ROOT,
                              capture_output=True, check=True).stdout
        total += len(blob)
        log = git("log", "--format=%h %cI %s", "--", repo).strip().split("\n")
        after = [x for x in log if x and x.split()[1][:10] > listed]
        same = [x for x in log if x and x.split()[1][:10] == listed]
        last = log[0] if log and log[0] else ""
        state = "current" if not after else "check: compare byte sizes"
        rows.append([pk, repo, listed, len(blob), hashlib.sha256(blob).hexdigest(),
                     last.split()[0] if last else "", last.split()[1][:10] if last else "",
                     len(after), " | ".join(a[:60] for a in after),
                     len(same), " | ".join(s[:60] for s in same), state])
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "sync.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pk_name", "repo_path", "listed_date", "bytes_at_head", "sha256_at_head",
                    "last_commit", "last_commit_date", "commits_after_listed_date",
                    "those_commits", "commits_on_listed_date", "same_day_commits", "state"])
        w.writerows(rows)
    for r in rows:
        print(f"{r[0]}: {r[3]} bytes, last {r[5]} {r[6]}, after {r[2]}: {r[7]}, "
              f"same day: {r[9]} -> {r[11]}")
    print(f"total bytes of the eight at HEAD: {total}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("citations", "spec", "archive", "paths", "sync"):
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    if a.citations:
        mode_citations()
    elif a.spec:
        sys.exit(mode_spec())
    elif a.archive:
        mode_archive()
    elif a.paths:
        mode_paths()
    elif a.sync:
        mode_sync()


if __name__ == "__main__":
    main()
