#!/usr/bin/env python3
"""Check that every work item's step files match its Scope (items 026, 029, 034; RI-007, RI-009).

Usage: python3 scripts/check_pipeline.py [--today YYYY-MM-DD]   (run from the repo root)

Required step files by `Scope:` in request.md (no Scope line = FULL):
  FULL           01 02 03 04 05 06 07
  RESEARCH ONLY  01 02 03 07
  FAST           01 03 05 06 07   (the person asked to go faster: R2 and I1 may be skipped,
                                    never R3's fact check or I3's verification)
A `Waived: <steps> (<who>, <date>: <why>)` line in request.md excuses those steps; it is
printed every run so it stays visible. 03 (fact check) and 06 (verification) can be waived
only by the person: <who> must be `person`, otherwise the item is SKIPPED (item 031).

Each item is one of:
  SKIPPED      a later required step exists while an earlier one is missing, or another
               file (a result for the person, e.g. screen-summary.md) exists before
               the fact check 03 (exit 1)
  STUCK        only request.md, and its Date is at least 1 day before --today
  not started  only request.md, opened today
  in progress  the required steps present so far have no gap
  awaiting A1  every required step is present, but 07-audit-task.md has no `A1 result:` line
               (every item except the closed PRE_A1_LINE list; items 033, 035). Listed, not an error.
  IN PR        stuck, not started or in progress here, but an unmerged remote branch has more of
               its step files (item 034). Listed, not an error: it waits for the person's merge.
  complete     every required step is present and A1 recorded its result
Items in LEGACY are older than this check and are reported as such.

When run inside a git repo, it also prints OPEN BRANCHES: every remote branch not merged into
HEAD, the work items it carries, whether it merges cleanly into HEAD (`git merge-tree`), and
whether it edits logs/recurring-issues.md, which only A1's daily commit on main should (036).
Outside a git repo (or without git) that part is skipped.
"""
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

STEPS = {"01": "01-research.md", "02": "02-improvements.md", "03": "03-handoff.md",
         "04": "04-build-plan.md", "05": "05-build-report.md", "06": "06-verification.md",
         "07": "07-audit-task.md"}
REQUIRED = {"FULL": ["01", "02", "03", "04", "05", "06", "07"],
            "RESEARCH ONLY": ["01", "02", "03", "07"],
            "FAST": ["01", "03", "05", "06", "07"]}
# Only the person may waive these (run-item.md: R3 and I3 are never skipped; item 031).
PERSON_ONLY = ("03", "06")
# Items whose audit was recorded only in a daily report, before 07 carried an
# `A1 result:` line (item 033). Every other item needs the line (item 035: a date cutoff let
# items opened early but built later through). Never add a new item here.
PRE_A1_LINE = {"002", "003", "017", "018", "019", "020", "021", "022"}
RECURRING = "logs/recurring-issues.md"
# Older than the Scope/07 rules. Never add a new item here.
LEGACY = {"001": "RESEARCH ONLY before 07-audit-task existed (item 021)",
          **{i: "07 is combined in work/003/07-audit-task.md" for i in ("004", "005", "006", "007", "008")}}


def read_request(path):
    text = path.read_text(encoding="utf-8")
    scope = re.search(r"^Scope:\s*(FULL|RESEARCH ONLY|FAST)\b", text, re.M)
    date = re.search(r"^Date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    waived = re.search(r"^Waived:\s*([0-9 ,]+)(.*)$", text, re.M)
    who = re.match(r"\s*\(\s*([^,:)]+)", waived.group(2)) if waived else None
    return (scope.group(1) if scope else "FULL",
            dt.date.fromisoformat(date.group(1)) if date else None,
            (re.findall(r"\d\d", waived.group(1)), waived.group(0).strip(),
             who.group(1).strip().lower() if who else "") if waived else ([], "", ""))


def classify(item_dir, today):
    """(status, detail) for one work item folder."""
    scope, opened, (waived, waived_line, who) = read_request(item_dir / "request.md")
    extra = f"; {waived_line}" if waived_line else ""
    blocked = [s for s in waived if s in PERSON_ONLY and who != "person"]
    if blocked:
        return "SKIPPED", f"{scope}: {' '.join(blocked)} can be waived only by the person{extra}"
    need = [s for s in REQUIRED[scope] if s not in waived]
    have = [s for s in need if (item_dir / STEPS[s]).exists()]
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
        audit = item_dir / STEPS["07"]
        if (item_dir.name not in PRE_A1_LINE and audit.exists()
                and not re.search(r"^A1 result:", audit.read_text(encoding="utf-8"), re.M)):
            return "awaiting A1", f"{scope}{extra}"
        return "complete", f"{scope}{extra}"
    return "in progress", f"{scope}: next {need[len(have)]}{extra}"


def _git(*args):
    """stdout and exit code of a git command in the current directory, or None if git is
    missing or this directory is not the top of a git work tree."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, encoding="utf-8")
        if top.returncode != 0 or Path(top.stdout.strip()).resolve() != Path.cwd().resolve():
            return None
        r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return None
    return r.stdout, r.returncode


def open_branches():
    """[(branch, {item: set of step codes}, conflicts, edits_recurring)] for every remote
    branch not merged into HEAD (item 034)."""
    out = _git("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")
    if out is None or out[1] != 0:
        return []
    found = []
    for ref in out[0].split():
        if ref.endswith("/HEAD") or "/" not in ref:
            continue
        # items the branch changes (since it left HEAD), with every step file it has for them
        changed = _git("diff", "--name-only", f"HEAD...{ref}", "--", "work/")
        touched = {n.split("/")[1] for n in (changed[0].splitlines() if changed else []) if n.count("/") == 2}
        items = {i: set() for i in touched}
        listing = _git("ls-tree", "-r", "--name-only", ref, "--", "work/")
        for name in (listing[0].splitlines() if listing and listing[1] == 0 else []):
            parts = name.split("/")
            if len(parts) == 3 and parts[1] in items and parts[2] in STEPS.values():
                items[parts[1]].add(parts[2][:2])
        merge = _git("merge-tree", "--write-tree", "--name-only", "--no-messages", "HEAD", ref)
        conflicts = None
        if merge is not None and merge[1] in (0, 1):
            conflicts = merge[0].splitlines()[1:] if merge[1] == 1 else []
        diff = _git("diff", "--name-only", f"HEAD...{ref}", "--", RECURRING)
        found.append((ref, items, conflicts, bool(diff and diff[0].strip())))
    return found


def main(argv):
    today = dt.datetime.now(dt.timezone.utc).date()
    if argv[:1] == ["--today"]:
        today = dt.date.fromisoformat(argv[1])
    elif argv:
        sys.exit(__doc__)
    work = Path("work")
    skipped, stuck, awaiting, in_pr = [], [], [], []
    branches = open_branches()
    for d in sorted(p for p in work.iterdir() if (p / "request.md").exists()):
        status, detail = classify(d, today)
        if d.name in LEGACY and status in ("SKIPPED", "in progress"):
            status, detail = "LEGACY", LEGACY[d.name]
        if status in ("STUCK", "not started", "in progress"):
            here = {s for s, f in STEPS.items() if (d / f).exists()}
            best = max(((len(items.get(d.name, set()) - here), ref, items.get(d.name, set()))
                        for ref, items, _, _ in branches), default=(0, "", set()))
            if best[0] > 0:
                status, detail = "IN PR", f"{best[1]} has {' '.join(sorted(best[2]))}; was {status} here"
                in_pr.append(d.name)
        print(f"{d.name}: {status} ({detail})")
        if status == "SKIPPED":
            skipped.append(d.name)
        if status == "STUCK":
            stuck.append(d.name)
        if status == "awaiting A1":
            awaiting.append(d.name)
    print(f"STUCK: {', '.join(stuck) or 'none'}")
    print(f"AWAITING A1: {', '.join(awaiting) or 'none'}")
    print(f"IN PR: {', '.join(in_pr) or 'none'}")
    if branches:
        print("OPEN BRANCHES (not merged into HEAD):")
        for ref, items, conflicts, recurring in branches:
            merge = ("merge not checked" if conflicts is None else
                     f"CONFLICTS: {', '.join(conflicts)}" if conflicts else "merges cleanly")
            note = f"; edits {RECURRING} (item 036)" if recurring else ""
            print(f"  {ref}: items {', '.join(sorted(items)) or 'none'}; {merge}{note}")
    print(f"SKIPPED: {', '.join(skipped) or 'none'}")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
