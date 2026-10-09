"""Standing tool (D93.8): keep DECISIONS.md to its Live index, and check that
every citation still resolves. Run at the end of every session. Standard
library only. Offline.

Modes (one per run):
  --plan                 split DECISIONS.md into its header and spans, read
                         the Live index, and mark each span KEEP or MOVE. No
                         file is written except the --out table.
  --apply --session NN   do the plan, then move every span outside the Live
                         index, verbatim and in order, to the end of
                         DECISIONS-archive.md. Writes only if all four checks
                         pass (see apply()).
  --citations            check that every Dnn/Fnn cited in SPEC.md, STATUS.md,
                         CLAUDE.md, DECISIONS.md and RESULTS.md has its
                         opening line in exactly one of the two DECISIONS
                         files; also report doubled entries and dated
                         headings out of order. Report only.

Terms:
  header  every line of DECISIONS.md before the first line that is exactly
          '---'. The Live index sits at its end, between the markers
          '<!-- live-index-start -->' and '<!-- live-index-end -->'.
  span    the lines between two '---' lines (or after the last one). The
          '---' lines are separators and belong to no span.
  ID      the entry number of the first line in a span that matches
          ^\\*\\*([DF]\\d+)\\. ; a span with no such line is a 'pointer'.

Options:
  --out PATH   append the full table (plan) or the unresolved list
               (citations) to PATH. The terminal gets a short summary only.
  --root DIR   the repo folder (default: this script's parent folder). Used
               to test the script on a temporary copy.

A "line" below is one element of the text split on '\\n', so a file that ends
with a newline has an empty last element. Joining the elements with '\\n'
gives the file back byte for byte.
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

SEP = "---"
INDEX_START = "<!-- live-index-start -->"
INDEX_END = "<!-- live-index-end -->"
ID_RE = re.compile(r"^\*\*([DF]\d+)\.")
INDEX_RE = re.compile(r"^- ([DF]\d+):")
# A citation: D or F, then digits, then an optional .digits part. Not part of
# a longer word or number (so 'FY27' and hex strings do not match).
CITE_RE = re.compile(r"(?<![A-Za-z0-9_])([DF])(\d+)(?:\.\d+)?(?![A-Za-z0-9_])")
DATED_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})")
CITING_FILES = ["SPEC.md", "STATUS.md", "CLAUDE.md", "DECISIONS.md", "RESULTS.md"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return path.read_bytes().decode("utf-8")


def plan(text):
    """Split DECISIONS.md text into header and spans, and mark KEEP or MOVE.

    Returns (header, spans, keep_ids, problems). Each span is a dict with its
    lines, its first line number (1-based) in the file, its ID and its action.
    Stops (SystemExit) on any problem D93.8's script must stop on.
    """
    lines = text.split("\n")
    seps = [i for i, l in enumerate(lines) if l == SEP]
    if not seps:
        sys.exit("STOP: DECISIONS.md has no '---' line")
    header = lines[:seps[0]]

    # The Live index, read from the header only.
    starts = [i for i, l in enumerate(header) if l.strip() == INDEX_START]
    ends = [i for i, l in enumerate(header) if l.strip() == INDEX_END]
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        sys.exit("STOP: the Live index markers are missing or doubled in the header")
    keep_ids = []
    for l in header[starts[0] + 1:ends[0]]:
        m = INDEX_RE.match(l)
        if m:
            keep_ids.append(m.group(1))
    if not keep_ids:
        sys.exit("STOP: the Live index is empty")
    if len(set(keep_ids)) != len(keep_ids):
        sys.exit("STOP: the Live index lists an ID twice")

    spans = []
    bounds = seps + [len(lines)]
    for k in range(len(seps)):
        first, stop = bounds[k] + 1, bounds[k + 1]
        span_lines = lines[first:stop]
        ids = []
        for l in span_lines:
            m = ID_RE.match(l)
            if m and m.group(1) not in ids:
                ids.append(m.group(1))
        if len(ids) > 1:
            sys.exit(f"STOP: span {k + 1} (line {first + 1}) gives more than one ID: {ids}")
        span_id = ids[0] if ids else "pointer"
        spans.append({
            "n": k + 1,
            "line": first + 1,
            "lines": span_lines,
            "id": span_id,
            "action": "KEEP" if span_id in keep_ids else "MOVE",
        })

    problems = []
    for kid in keep_ids:
        found = [s for s in spans if s["id"] == kid]
        if len(found) != 1:
            sys.exit(f"STOP: Live index ID {kid} is in {len(found)} spans (must be 1)")
    seen = {}
    for s in spans:
        if s["id"] != "pointer":
            seen.setdefault(s["id"], []).append(s["n"])
    for sid, ns in seen.items():
        if len(ns) > 1:
            problems.append(f"ID {sid} is in more than one span: {ns}")
    return header, spans, keep_ids, problems


def span_bytes(span):
    # The span's lines plus the newline that ends each of them.
    return len(("\n".join(span["lines"]) + "\n").encode("utf-8"))


def write_table(out, title, header, spans, problems):
    with open(out, "a", encoding="utf-8") as f:
        f.write(f"\n{title}\n\n")
        f.write(f"Header: lines 1 to {len(header)}.\n\n")
        f.write("index | first line | lines | bytes | ID | first line of span (80 chars) | action\n")
        for s in spans:
            first_text = next((l for l in s["lines"] if l.strip()), "")[:80]
            f.write(f"{s['n']} | {s['line']} | {len(s['lines'])} | {span_bytes(s)} | "
                    f"{s['id']} | {first_text} | {s['action']}\n")
        f.write(f"\nIDs in more than one span: {problems if problems else 'none'}\n")


def summary(text, spans, keep_ids):
    keep = sum(1 for s in spans if s["action"] == "KEEP")
    move = len(spans) - keep
    move_b = sum(span_bytes(s) for s in spans if s["action"] == "MOVE")
    print(f"plan: spans {len(spans)}, keep {keep} (index IDs {len(keep_ids)}), "
          f"move {move} ({move_b} bytes), DECISIONS.md {len(text.encode('utf-8'))} bytes")


def apply(root, session, out):
    live_path = root / "DECISIONS.md"
    arch_path = root / "DECISIONS-archive.md"
    live_b, arch_b = live_path.read_bytes(), arch_path.read_bytes()
    live, arch = live_b.decode("utf-8"), arch_b.decode("utf-8")
    header, spans, keep_ids, problems = plan(live)
    summary(live, spans, keep_ids)
    if out:
        write_table(out, f"archive_decisions.py --apply --session {session}: span table",
                    header, spans, problems)
    moved = [s for s in spans if s["action"] == "MOVE"]
    kept = [s for s in spans if s["action"] == "KEEP"]
    if not moved:
        print("apply: nothing to move; no file written")
        return

    # The new live file: header, then each kept span after its separator.
    new_live_lines = list(header)
    for s in kept:
        new_live_lines += [SEP] + s["lines"]
    new_live = "\n".join(new_live_lines)

    # The archive addition: a blank line, '---', a blank line, the heading,
    # then each moved span after its separator.
    added_lines = ["", SEP, "", f"## Moved by session {session} (D93.8)"]
    moved_lines = []
    for s in moved:
        moved_lines += [SEP] + s["lines"]
    added = "\n".join(added_lines + moved_lines)
    new_arch = arch + added

    # (1) The new archive starts with the old archive, byte for byte.
    c1 = new_arch.encode("utf-8")[:len(arch_b)] == arch_b
    # (2) Line counts. New live plus the moved spans and their separators
    # equals the original; the new archive equals the old archive's lines
    # plus the four added heading lines plus the moved spans and separators.
    n = lambda t: len(t.split("\n"))
    old_arch_lines = n(arch) - 1 if arch.endswith("\n") else n(arch)
    c2a = n(new_live) + len(moved_lines) == n(live)
    c2b = n(new_arch) == old_arch_lines + len(added_lines) + len(moved_lines)
    c2 = c2a and c2b
    # (3) Rebuild the original from the two new texts alone. Re-split the
    # new live file and the added archive section, then put the spans back
    # at their recorded positions (the plan's KEEP/MOVE order).
    nl = new_live.split("\n")
    nl_seps = [i for i, l in enumerate(nl) if l == SEP]
    re_header = nl[:nl_seps[0]]
    nb = nl_seps + [len(nl)]
    re_kept = [nl[nb[k] + 1:nb[k + 1]] for k in range(len(nl_seps))]
    al = new_arch[len(arch):].split("\n")
    al_seps = [i for i, l in enumerate(al) if l == SEP]
    # The first '---' belongs to the added heading lines; spans follow the rest.
    ab = al_seps[1:] + [len(al)]
    re_moved = [al[ab[k] + 1:ab[k + 1]] for k in range(len(al_seps) - 1)]
    rebuilt_lines = list(re_header)
    ki = mi = 0
    for s in spans:
        if s["action"] == "KEEP":
            rebuilt_lines += [SEP] + re_kept[ki]
            ki += 1
        else:
            rebuilt_lines += [SEP] + re_moved[mi]
            mi += 1
    c3 = (ki == len(re_kept) and mi == len(re_moved)
          and "\n".join(rebuilt_lines).encode("utf-8") == live_b)
    # (4) Every moved span appears verbatim, in order, in the added section.
    section = new_arch[len(arch):]
    pos, c4 = 0, True
    for s in moved:
        piece = SEP + "\n" + "\n".join(s["lines"])
        at = section.find(piece, pos)
        if at < 0:
            c4 = False
            break
        pos = at + len(piece)

    print(f"check 1 (archive starts with old archive): {'PASS' if c1 else 'FAIL'}")
    print(f"check 2 (line counts: live {n(new_live)} + moved {len(moved_lines)} = "
          f"original {n(live)}; archive {n(new_arch)} = {old_arch_lines} + "
          f"{len(added_lines)} + {len(moved_lines)}): {'PASS' if c2 else 'FAIL'}")
    print(f"check 3 (rebuild original byte for byte): {'PASS' if c3 else 'FAIL'}")
    print(f"check 4 (every moved span verbatim in archive): {'PASS' if c4 else 'FAIL'}")
    if not (c1 and c2 and c3 and c4):
        sys.exit("STOP: a check failed; nothing written")

    new_live_b, new_arch_b = new_live.encode("utf-8"), new_arch.encode("utf-8")
    live_path.write_bytes(new_live_b)
    arch_path.write_bytes(new_arch_b)
    print(f"moved {len(moved)} spans, kept {len(kept)}")
    print(f"DECISIONS.md         before {len(live_b)} bytes {sha(live_b)}")
    print(f"DECISIONS.md         after  {len(new_live_b)} bytes {sha(new_live_b)}")
    print(f"DECISIONS-archive.md before {len(arch_b)} bytes {sha(arch_b)}")
    print(f"DECISIONS-archive.md after  {len(new_arch_b)} bytes {sha(new_arch_b)}")


def opening_lines(text, pattern):
    return [i + 1 for i, l in enumerate(text.split("\n")) if pattern.match(l)]


def citations(root, out):
    live = read(root / "DECISIONS.md")
    arch = read(root / "DECISIONS-archive.md")

    # Every citation, with the file and line citing it.
    cited = {}
    for name in CITING_FILES:
        path = root / name
        if not path.exists():
            print(f"note: {name} not found; skipped")
            continue
        for i, l in enumerate(read(path).split("\n")):
            for m in CITE_RE.finditer(l):
                cited.setdefault(m.group(1) + m.group(2), []).append(f"{name}:{i + 1}")

    # Opening lines in each DECISIONS file: '**D12.' at the start of a line.
    open_re = re.compile(r"^\*\*([DF]\d+)\.")
    in_live, in_arch = set(), set()
    for text, bucket in ((live, in_live), (arch, in_arch)):
        for l in text.split("\n"):
            m = open_re.match(l)
            if m:
                bucket.add(m.group(1))

    resolved, unresolved, both = [], [], []
    for num in sorted(cited, key=lambda x: (x[0], int(x[1:]))):
        a, b = num in in_live, num in in_arch
        if a and b:
            both.append(num)
        elif a or b:
            resolved.append(num)
        else:
            unresolved.append(num)

    # First opening lines ('**D12. ', with a space) found more than once.
    first_re = re.compile(r"^\*\*([DF]\d+)\. ")
    counts = {}
    for fname, text in (("DECISIONS.md", live), ("DECISIONS-archive.md", arch)):
        for i, l in enumerate(text.split("\n")):
            m = first_re.match(l)
            if m:
                counts.setdefault(m.group(1), []).append(f"{fname}:{i + 1}")
    doubled = {k: v for k, v in counts.items() if len(v) > 1}

    # Dated headings in DECISIONS.md earlier than the one before them.
    out_of_order, prev = [], None
    for i, l in enumerate(live.split("\n")):
        m = DATED_RE.match(l)
        if m:
            if prev and m.group(1) < prev[0]:
                out_of_order.append(f"line {i + 1}: {m.group(1)} after {prev[0]} (line {prev[1]})")
            prev = (m.group(1), i + 1)

    print(f"citations: {len(cited)} distinct entry numbers cited; resolved {len(resolved)}, "
          f"unresolved {len(unresolved)}, found in both files {len(both)}")
    print(f"entries whose first opening line appears more than once: {len(doubled)}")
    print(f"dated headings out of order in DECISIONS.md: {len(out_of_order)}")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write("\narchive_decisions.py --citations\n\n")
            f.write(f"Distinct entry numbers cited: {len(cited)}. Resolved {len(resolved)}, "
                    f"unresolved {len(unresolved)}, in both files {len(both)}.\n\n")
            f.write("Unresolved (number: where cited):\n")
            for num in unresolved:
                f.write(f"  {num}: {', '.join(cited[num])}\n")
            f.write("Found in both files (number: where cited):\n")
            for num in both:
                f.write(f"  {num}: {', '.join(cited[num])}\n")
            f.write("First opening line appearing more than once:\n")
            for k in sorted(doubled, key=lambda x: (x[0], int(x[1:]))):
                f.write(f"  {k}: {', '.join(doubled[k])}\n")
            f.write("Dated headings out of order in DECISIONS.md:\n")
            for x in out_of_order:
                f.write(f"  {x}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--citations", action="store_true")
    ap.add_argument("--session", help="session number, for --apply's heading")
    ap.add_argument("--out", help="append the full table or list to this file")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    root = Path(args.root)

    if args.plan:
        text = read(root / "DECISIONS.md")
        header, spans, keep_ids, problems = plan(text)
        summary(text, spans, keep_ids)
        if problems:
            print(f"note: {len(problems)} non-index IDs are in more than one span (see table)")
        if args.out:
            write_table(args.out, "archive_decisions.py --plan: span table",
                        header, spans, problems)
    elif args.apply:
        if not args.session:
            sys.exit("STOP: --apply needs --session NN")
        apply(root, args.session, args.out)
    else:
        citations(root, args.out)


if __name__ == "__main__":
    main()
