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

Item 092 (RI-014): 01 and 03 are read by scripts/check_pipeline.py's one reader, _read, so this script
depends on check_pipeline.py importing cleanly. An 01 that exists but can't be read prints
`sources count (unique URLs in 01-research.md): not computed (<path> unreadable (<detail>))`, never a
number; an unreadable 01 or 03 prints `FAIL: <path> unreadable (<detail>)` and exits 1 (detail
`not UTF-8 at byte <n>` or the exception class name). No traceback on an unreadable 01 or 03; work/
listing errors under --all may still raise. An unreadable file is never LEGACY: under --all it is FAIL,
even for a LEGACY ID.
"""
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://[^\]\s)>`]+")
# Hand-offs written before the Totals line (019) and Self-check section (017) existed.
# Never add a new item here: a new hand-off must PASS.
LEGACY = {i: "written 2026-10-30, before the Totals/Self-check template (commit 77273f0)"
          for i in ("002", "003", "004", "005", "006", "007", "008")}

# Item 092: a FAIL line that names an unreadable file (never LEGACY). fullmatch only, never a substring (RI-012).
UNREADABLE_PROBLEM = re.compile(r"\S+ unreadable \((?:not UTF-8 at byte \d+|[A-Z]\w*Error)\)")

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


def _pipeline():
    """Item 092: scripts/check_pipeline.py as a module object (its _read, _UNREAD, _shown and
    open_branches are looked up on it at call time). The scripts dir is put on sys.path once."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import check_pipeline
    return check_pipeline


def _report(problems):
    """Print each problem as a `FAIL: ` line, then PASS or `<n> problem(s)`; 1 if any, else 0."""
    for p in problems:
        print(f"FAIL: {p}")
    print("PASS" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def main(item):
    base = Path("work") / item
    problems = []
    if not base.is_dir():
        print(f"FAIL: no work item folder {base}")
        return 1
    cp = _pipeline()

    research = base / "01-research.md"
    text01, why01 = cp._read(research, missing_ok=True)
    if why01:
        p = f"{why01} ({cp._UNREAD[cp._shown(research)]})"
        print(f"sources count (unique URLs in 01-research.md): not computed ({p})")
        problems.append(p)
    elif text01 is not None:
        urls = unique_urls(text01)
        print(f"sources count (unique URLs in 01-research.md): {len(urls)}")

    handoff = base / "03-handoff.md"
    text, why03 = cp._read(handoff, missing_ok=True)
    if why03:
        problems.append(f"{why03} ({cp._UNREAD[cp._shown(handoff)]})")
        return _report(problems)
    if text is None:
        print(f"no {handoff}; nothing else to check")
        if problems:
            return _report(problems)
        return 0

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

    return _report(problems)


def _branch_with_handoff(item):
    """(ref, None) for the first open branch (scripts/check_pipeline.py OPEN BRANCHES) that has
    this item's 03-handoff.md, else (None, None) (item 044); without git (None, None). Item 081:
    (None, why) when the branch list itself failed, so "no hand-off" is never claimed unread."""
    cp = _pipeline()
    found = cp.open_branches()
    if found is None:
        return None, None
    if isinstance(found, str):
        return None, found
    for b in found:
        if "03" in b["items"].get(item, set()):
            return b["ref"], None
    return None, None


def check_all(work=Path("work")):
    """One line per work item: PASS, LEGACY, FAIL, 'IN PR (<branch>)' (the hand-off is only on an
    open branch, item 044), 'no hand-off', or 'not checked (open branches: <why>)' when git cannot list
    the branches (item 081). Exit 1 on FAIL or not checked. Item 094: in a single-branch clone the line is
    `not checked (open branches: <SINGLE_TEXT>)`, exit 1 (open_branches returns SINGLE_TEXT as its reason)."""
    import contextlib
    import io
    failed = []
    for d in sorted(p for p in work.iterdir() if p.is_dir()):
        if not (d / "03-handoff.md").exists():
            ref, why = _branch_with_handoff(d.name)
            if why:                                         # item 081: counted as a failure
                print(f"{d.name}: not checked (open branches: {why})")
                failed.append(d.name)
                continue
            print(f"{d.name}: IN PR ({ref})" if ref else f"{d.name}: no hand-off")
            continue
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(d.name)
        problems = [l[6:] for l in out.getvalue().splitlines() if l.startswith("FAIL: ")]
        if code == 0:
            print(f"{d.name}: PASS")
        elif d.name in LEGACY and not any(UNREADABLE_PROBLEM.fullmatch(p) for p in problems):
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
