#!/usr/bin/env python3
"""Check that every work item's step files match its Scope (items 026 and 029, RI-007).

Usage: python3 scripts/check_pipeline.py [--today YYYY-MM-DD]   (run from the repo root)

Required step files by `Scope:` in request.md (no Scope line = FULL):
  FULL           01 02 03 04 05 06 07
  RESEARCH ONLY  01 02 03 07
  FAST           01 03 05 06 07   (the person asked to go faster: R2 and I1 may be skipped,
                                    never R3's fact check or I3's verification)
A `Waived: <steps> (<who>, <date>: <why>)` line in request.md excuses those steps; it is
printed every run so it stays visible.

Each item is one of:
  SKIPPED      a later required step exists while an earlier one is missing, or another
               file (a result for the person, e.g. screen-summary.md) exists before
               the fact check 03 (exit 1)
  STUCK        only request.md, and its Date is at least 1 day before --today
  not started  only request.md, opened today
  in progress  the required steps present so far have no gap
  complete     every required step is present
Items in LEGACY are older than this check and are reported as such.
"""
import datetime as dt
import re
import sys
from pathlib import Path

STEPS = {"01": "01-research.md", "02": "02-improvements.md", "03": "03-handoff.md",
         "04": "04-build-plan.md", "05": "05-build-report.md", "06": "06-verification.md",
         "07": "07-audit-task.md"}
REQUIRED = {"FULL": ["01", "02", "03", "04", "05", "06", "07"],
            "RESEARCH ONLY": ["01", "02", "03", "07"],
            "FAST": ["01", "03", "05", "06", "07"]}
# Older than the Scope/07 rules. Never add a new item here.
LEGACY = {"001": "RESEARCH ONLY before 07-audit-task existed (item 021)",
          **{i: "07 is combined in work/003/07-audit-task.md" for i in ("004", "005", "006", "007", "008")}}


def read_request(path):
    text = path.read_text(encoding="utf-8")
    scope = re.search(r"^Scope:\s*(FULL|RESEARCH ONLY|FAST)\b", text, re.M)
    date = re.search(r"^Date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    waived = re.search(r"^Waived:\s*([0-9 ,]+)(.*)$", text, re.M)
    return (scope.group(1) if scope else "FULL",
            dt.date.fromisoformat(date.group(1)) if date else None,
            (re.findall(r"\d\d", waived.group(1)), waived.group(0).strip()) if waived else ([], ""))


def classify(item_dir, today):
    """(status, detail) for one work item folder."""
    scope, opened, (waived, waived_line) = read_request(item_dir / "request.md")
    need = [s for s in REQUIRED[scope] if s not in waived]
    have = [s for s in need if (item_dir / STEPS[s]).exists()]
    extra = f"; {waived_line}" if waived_line else ""
    if not have and not any(f.name != "request.md" for f in item_dir.iterdir()):
        if opened is not None and (today - opened).days >= 1:
            return "STUCK", f"{scope}, opened {opened}, {(today - opened).days} day(s) with request.md only{extra}"
        return "not started", f"{scope}{extra}"
    last = max((need.index(s) for s in have), default=-1)
    gaps = [s for s in need[:last] if s not in have]
    if gaps:
        return "SKIPPED", f"{scope}: missing {' '.join(gaps)} before {need[last]}{extra}"
    results = sorted(f.name for f in item_dir.iterdir() if f.name != "request.md" and f.name not in STEPS.values())
    unchecked = [s for s in need[:need.index("03") + 1] if s not in have] if "03" in need else []
    if results and unchecked:
        return "SKIPPED", f"{scope}: {', '.join(results)} written before {' '.join(unchecked)}{extra}"
    if len(have) == len(need):
        return "complete", f"{scope}{extra}"
    return "in progress", f"{scope}: next {need[len(have)]}{extra}"


def main(argv):
    today = dt.datetime.now(dt.timezone.utc).date()
    if argv[:1] == ["--today"]:
        today = dt.date.fromisoformat(argv[1])
    elif argv:
        sys.exit(__doc__)
    work = Path("work")
    skipped, stuck = [], []
    for d in sorted(p for p in work.iterdir() if (p / "request.md").exists()):
        status, detail = classify(d, today)
        if d.name in LEGACY and status in ("SKIPPED", "in progress"):
            status, detail = "LEGACY", LEGACY[d.name]
        print(f"{d.name}: {status} ({detail})")
        if status == "SKIPPED":
            skipped.append(d.name)
        if status == "STUCK":
            stuck.append(d.name)
    print(f"STUCK: {', '.join(stuck) or 'none'}")
    print(f"SKIPPED: {', '.join(skipped) or 'none'}")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
