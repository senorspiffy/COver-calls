#!/usr/bin/env python3
"""Check a work item's research files for count errors.

Usage: python3 scripts/check_handoff.py <work item ID>
       python3 scripts/check_handoff.py --all   (one line per item; A1's daily run)

Checks work/<ID>/03-handoff.md:
  - the fact-check table row count matches the Totals line;
  - VERIFIED as-is + fixed + removed adds up to the total;
  - a "## Self-check" section exists.
Prints the unique-URL count of work/<ID>/01-research.md (R1's sources count).
Exits 1 if any check fails. Items in LEGACY are reported LEGACY, not FAIL (item 028).
"""
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://[^\]\s)>`]+")
# Hand-offs written before the Totals line (019) and Self-check section (017) existed.
# Never add a new item here: a new hand-off must PASS.
LEGACY = {i: "written 2026-10-30, before the Totals/Self-check template (commit 77273f0)"
          for i in ("002", "003", "004", "005", "006", "007", "008")}

TOTALS_RE = re.compile(
    r"(\d+) rows checked.*?(\d+) VERIFIED as-is.*?(\d+) fixed.*?(\d+) removed",
    re.S,
)


def section(text, heading):
    """Return the text under a '## heading' up to the next '## ' heading."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def fact_rows(block):
    rows = [l for l in block.splitlines() if l.startswith("|")]
    # drop the header row and the |---| separator
    return [r for r in rows[2:] if not re.match(r"^\|\s*-", r)]


def unique_urls(text):
    return sorted({u.rstrip(".,;") for u in URL_RE.findall(text)})


def main(item):
    base = Path("work") / item
    problems = []
    if not base.is_dir():
        print(f"FAIL: no work item folder {base}")
        return 1

    research = base / "01-research.md"
    if research.exists():
        urls = unique_urls(research.read_text(encoding="utf-8"))
        print(f"sources count (unique URLs in 01-research.md): {len(urls)}")

    handoff = base / "03-handoff.md"
    if not handoff.exists():
        print(f"no {handoff}; nothing else to check")
        return 0
    text = handoff.read_text(encoding="utf-8")

    block = section(text, "Fact check")
    if block is None:
        problems.append("missing '## Fact check' section")
    else:
        rows = len(fact_rows(block))
        print(f"fact-check rows: {rows}")
        m = TOTALS_RE.search(block)
        if not m:
            problems.append("no Totals line ('<n> rows checked -> <n> VERIFIED as-is, <n> fixed, <n> removed')")
        else:
            total, ok, fixed, removed = map(int, m.groups())
            print(f"totals line: {total} rows -> {ok} as-is, {fixed} fixed, {removed} removed")
            if total != rows:
                problems.append(f"Totals say {total} rows, table has {rows}")
            if ok + fixed + removed != total:
                problems.append(f"{ok} + {fixed} + {removed} = {ok + fixed + removed}, not {total}")

    if section(text, "Self-check") is None:
        problems.append("missing '## Self-check' section")

    for p in problems:
        print(f"FAIL: {p}")
    print("PASS" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def check_all(work=Path("work")):
    """One line per work item: PASS, LEGACY, FAIL or 'no hand-off'. Exit 1 only on FAIL."""
    import contextlib
    import io
    failed = []
    for d in sorted(p for p in work.iterdir() if p.is_dir()):
        if not (d / "03-handoff.md").exists():
            print(f"{d.name}: no hand-off")
            continue
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(d.name)
        problems = [l[6:] for l in out.getvalue().splitlines() if l.startswith("FAIL: ")]
        if code == 0:
            print(f"{d.name}: PASS")
        elif d.name in LEGACY:
            print(f"{d.name}: LEGACY ({LEGACY[d.name]}; {len(problems)} known problem(s))")
        else:
            failed.append(d.name)
            print(f"{d.name}: FAIL: " + "; ".join(problems))
    print(f"FAIL on {', '.join(failed)}" if failed else "no new failures")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(check_all() if sys.argv[1] == "--all" else main(sys.argv[1]))
