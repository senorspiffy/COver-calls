#!/usr/bin/env python3
"""Check that every work item's step files match its Scope (items 026, 029, 034; RI-007, RI-009).

Usage: python3 scripts/check_pipeline.py [--today YYYY-MM-DD] [--untracked-from SHA]   (run from the repo root;
       --untracked-from is for tests only; the daily run uses the item-053 constant UNTRACKED_FROM)
       python3 scripts/check_pipeline.py --log <agent> <ID> "<fields>"   (item 045)
       python3 scripts/check_pipeline.py --next-id   (the ID to give a new work item, item 037)

Required step files by `Scope:` in request.md (no Scope line = FULL):
  FULL           01 02 03 04 05 06 07
  RESEARCH ONLY  01 02 03 07
  FAST           01 03 05 06 07   (the person asked to go faster: R2 and I1 may be skipped,
                                    never R3's fact check or I3's verification)
FAST counts only as `Scope: FAST (person, YYYY-MM-DD)`: the person asked for it. Any other
FAST line (no who, or another who) makes the item SKIPPED (item 042).
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
  A1 FAIL      every required step is present and the last `A1 result:` line is FAIL (item 042):
               the item went back to the team and is not complete until a later PASS line (exit 1)
  complete     every required step is present and A1's last result is PASS
Items in LEGACY are older than this check and are reported as such.
INCOMPLETE (item 043, exit 1): for items from CHECKLIST_FROM on, a 06 with no
`Recurring issues checked:` line naming an RI-, or a step file whose agent wrote no
`| <agent> | <ID> |` line in logs/research or logs/implementation.

When run inside a git repo, it also prints OPEN BRANCHES: every remote branch not merged into
HEAD, the work items it carries (what merging it into HEAD would change, from the
`git merge-tree` result, so a branch with two merge bases is not credited with work already in
HEAD; item 052), whether it merges cleanly into HEAD (`git merge-tree`), and
whether it edits logs/recurring-issues.md, which only A1's daily commit on main should (036),
and its last commit date and age (039). Two more lines come from the branches:
  ID CLASH        HEAD and an open branch each added work/<ID>/request.md since their merge
                  base, with different text: two items share one ID (item 037). Rename one.
  BRANCH SKIPPED  an item the open branch changes skips a step by the rules above, using the
                  branch's own files (item 038). An error for A1 (RI-007); exit code unchanged,
                  since the branch is not part of HEAD.
--log <agent> <ID> "<fields>" (item 045) appends `HH:MM | <agent> | <ID> | <fields>` with the
current UTC time to logs/research or logs/implementation/<UTC date>.md, and refuses (exit 2)
fields that don't match the agent's format (LOG_FORMAT). Every step logs this way, right after
writing its file. From LOG_CHECK_FROM on, a log line not in its format is INCOMPLETE, and
  LOG TIME        a committed log line timed after the commit that added it (git blame): it was
                  not written when its step ran (exit 1; RI-010).
                  Items in LOG_TIME_EXCEPT are not checked and are named with their reason
                  (item 049). Known gap: blame gives a line's latest commit, so a line edited
                  in a later commit is checked against that later commit.
  RULES BRANCH    an open branch that changes the rules (.claude/, templates/,
                  scripts/check_pipeline.py, scripts/check_handoff.py): build new items on top
                  of it, so its rules apply to them (item 049, RI-010). Listed, not an error.
  ORPHAN LOG      a log line whose item has no work/<ID>/ folder (exit 1; item 047). --log
                  refuses an ID without work/<ID>/request.md (exit 2), so a typo'd ID is caught
                  when it is written.
  MAIN AHEAD      HEAD is behind origin/main: merge main first. origin/main and branches whose
                  tip is already in it are then left out of OPEN BRANCHES (item 051); --next-id
                  still counts them.
  UNTRACKED CHANGE  (item 053, exit 1; RI-007) a commit on HEAD's first-parent chain after the
                  cutoff UNTRACKED_FROM that changes CODE_PATHS (ccbot/, config/, scripts/, tests/,
                  .claude/, templates/) and changes no step file 01-06 of a work item that is open at
                  the commit's first parent (07 absent, no `A1 result:` line, or last line FAIL;
                  PRE_A1_LINE and LEGACY items are closed). Each commit is judged against its first
                  parent (`git diff-tree --no-renames`), so a merge is one unit. 07 never covers code.
                  A follow-up to a completed item is a new item. "not checked (no git)" without git;
                  "not checked (... shallow clone ...)" when the cutoff is missing from a shallow
                  clone (exit unchanged); a cutoff missing from a full clone is an error (exit 1).
                  Known gaps: (a) one open item's 01-06 file covers unrelated code in the same unit;
                  (b) on a branch each direct commit is its own unit, so commit code together with
                  your 05; (c) PRs must land as merge commits (squash or rebase drops the cutoff ->
                  exit 1); (d) a merge's conflict edits are judged together with the whole merge
                  against its first parent; (e) paths outside CODE_PATHS (pyproject.toml, README.md,
                  data/) are not checked; (f) non-ASCII paths are quoted (no -z).
  RESEARCH CODE   (item 062, RI-007) a RESEARCH ONLY item whose unit changes RESEARCH_CODE_PATHS
                  (ccbot/, config/, scripts/, tests/) with no I1-I3. A unit is one HEAD commit after
                  the cutoff (as 053, against its first parent) or one open branch as a whole. On
                  HEAD the item's line becomes `<ID>: SKIPPED (<sha7> RESEARCH ONLY: changes <files>
                  ...)` (exit 1) and the line lists the IDs, or none, "not checked (no git)", or
                  "not checked (see UNTRACKED CHANGE)" when the cutoff can't be used. On a branch it
                  is `BRANCH SKIPPED: <ID> (<ref>: RESEARCH ONLY: changes <files> ...)`, joined to the
                  item's classify detail when that is SKIPPED too (exit unchanged). Scope and waiver
                  are read from request.md at the tip; a missing request.md is flagged, never passed.
                  Only `Waived: 04 05 06 (person, YYYY-MM-DD: <why>)` excuses it. Known gaps:
                  (g) a FULL/FAST item's 04 or 05 in the same unit covers the research item's code;
                  (h) .claude/ and templates/ edits are 053's only; (i) on a branch, code committed
                  without the research item's step file is caught by 053 on HEAD, not by 062;
                  (j) only the first `Waived:` line is read, so 04 05 06 go on the item's single
                  Waived line.
--next-id prints the next free ID over HEAD and every unmerged remote branch, so two threads
never pick the same number. Outside a git repo (or without git) the branch part is skipped.
"""
import datetime as dt
import re
import subprocess
import sys
import tempfile
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
# Item 043: the step-0 line in 06 and a log line per step are checked from this ID on.
# Earlier items are not re-checked (013-016 and 040 were found by A1 on 2026-11-04).
CHECKLIST_FROM = 41
AGENT = {"01": "R1", "02": "R2", "03": "R3", "04": "I1", "05": "I2", "06": "I3"}
# Item 045: from this ID on, each log line must match its agent's format, and a committed line
# may not be timed after the commit that added it. Lines are written with --log, never by hand.
LOG_CHECK_FROM = 45
# Item 049: items whose log times can't be checked, with why. 048 was built on a branch cut
# before 045 merged; its six lines were typed by hand with a time after their commit, and the
# real times are lost. Never add a new item here.
LOG_TIME_EXCEPT = {"048": "built before 045's --log rule reached main; times typed by hand, not recoverable (item 049)"}
# Item 049: an open branch changing any of these changes the rules new items are built under.
RULE_PATHS = (".claude/", "templates/", "scripts/check_pipeline.py", "scripts/check_handoff.py")
# Item 053: a commit changing any of these must change a step file 01-06 of an open work item.
CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/", ".claude/", "templates/")
# item 053: HEAD of daily-fixes/2026-11-11 just before I2's first code commit; never move it forward
UNTRACKED_FROM = "694bf4d0038e25bb82bd111018fbd67a94bbc74d"
# Item 062: a RESEARCH ONLY item may not change these unless I1-I3 ran or the person waived them.
# .claude/ and templates/ are left to 053 (gap h).
RESEARCH_CODE_PATHS = ("ccbot/", "config/", "scripts/", "tests/")
WAIVE_BUILD = {"04", "05", "06"}
WAIVE_BUILD_BY_PERSON = re.compile(r"\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:")
STEP_FILE = re.compile(r"^work/(\d{3})/(01-research|02-improvements|03-handoff|04-build-plan|"
                       r"05-build-report|06-verification)\.md$")
LOG_FORMAT = {  # the fields after `HH:MM | <agent> | <ID> | ` (.claude/agents/*.md)
    "R1": r"brief written \| \d+",
    "R2": r"3 for / 3 against \| languages: \S.*",
    "R3": r"\d+ (verified|as-is), \d+ fixed, \d+ removed \| (READY|BLOCKED)\b.*",
    "I1": r"(FIT|FIT WITH CHANGES|NOT A FIT) \| \d+ files planned\b.*",
    "I2": r"\d+ files? changed \| tests \d+/\d+\b.*",
    "I3": r"(PASS|FAIL) \| sent to audit: (yes|no)\b.*",
}
# Item 050: the same formats in plain words (as the agent files write them), with an example
# that fits each regex (tests check both), for INCOMPLETE and --log refusals.
LOG_HINT = {
    "R1": ("brief written | <sources count>", "brief written | 3"),
    "R2": ("3 for / 3 against | languages: <list or N/A>", "3 for / 3 against | languages: N/A"),
    "R3": ("<n> verified, <n> fixed, <n> removed | READY or BLOCKED", "5 verified, 1 fixed, 0 removed | READY"),
    "I1": ("FIT or FIT WITH CHANGES or NOT A FIT | <n> files planned", "FIT | 2 files planned"),
    "I2": ("<n> files changed | tests <pass>/<total>", "2 files changed | tests 9/9"),
    "I3": ("PASS or FAIL | sent to audit: yes or no", "PASS | sent to audit: yes"),
}
LOG_LINE = re.compile(r"^(\d{2}):(\d{2}) \| (R1|R2|R3|I1|I2|I3) \| (\d{3}) \| (.*)$")
FAST_BY_PERSON = re.compile(r"^Scope:\s*FAST\s*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*\)", re.M)
# Older than the Scope/07 rules. Never add a new item here.
LEGACY = {"001": "RESEARCH ONLY before 07-audit-task existed (item 021)",
          **{i: "07 is combined in work/003/07-audit-task.md" for i in ("004", "005", "006", "007", "008")}}


def read_request(path):
    return parse_request(path.read_text(encoding="utf-8"))


def parse_request(text):
    """(scope, date, (waived steps, first Waived: line, who)) from request.md text."""
    scope = re.search(r"^Scope:\s*(FULL|RESEARCH ONLY|FAST)\b", text, re.M)
    date = re.search(r"^Date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    waived = re.search(r"^Waived:\s*([0-9 ,]+)(.*)$", text, re.M)
    who = re.match(r"\s*\(\s*([^,:)]+)", waived.group(2)) if waived else None
    return (scope.group(1) if scope else "FULL",
            dt.date.fromisoformat(date.group(1)) if date else None,
            (re.findall(r"\d\d", waived.group(1)), waived.group(0).strip(),
             who.group(1).strip().lower() if who else "") if waived else ([], "", ""))


def _build_waived(text):
    """Item 062: the item's first `Waived:` line excuses 04 05 06 and was written by the person
    with a date: `Waived: 04 05 06 (person, YYYY-MM-DD: <why>)`."""
    _, _, (steps, waived_line, who) = parse_request(text)
    return WAIVE_BUILD <= set(steps) and who == "person" and bool(WAIVE_BUILD_BY_PERSON.search(waived_line))


def _research_code(files, request_text_of):
    """Item 062 (RI-007): [(ID, detail)] for the RESEARCH ONLY items in one unit (a HEAD commit
    or an open branch) whose `files` change RESEARCH_CODE_PATHS with no I1-I3 and no person's
    waiver. `request_text_of(ID)` is the item's request.md text at the tip, or None. Items come
    from the paths only, never from commit messages (RI-012)."""
    code = [f for f in files if f.startswith(RESEARCH_CODE_PATHS)]
    if not code:
        return []
    items = sorted({m[1] for m in map(STEP_FILE.match, files) if m})
    texts = {i: request_text_of(i) for i in items}
    built = {i for i in items for s in ("04", "05") if f"work/{i}/{STEPS[s]}" in files}
    if any(texts[i] is not None and parse_request(texts[i])[0] in ("FULL", "FAST") for i in built):
        return []                                           # gap (g): a built item covers the unit
    flags = []
    for i in items:
        if i in LEGACY:
            continue
        if texts[i] is None:
            flags.append((i, "RESEARCH ONLY check: no request.md at the tip, item 062"))
        elif parse_request(texts[i])[0] == "RESEARCH ONLY" and not _build_waived(texts[i]):
            flags.append((i, f"RESEARCH ONLY: changes {' '.join(code)} with no 04-06; needs Scope FULL or "
                             '"Waived: 04 05 06 (person, <date>: <why>)" on the item\'s single Waived: line '
                             "(item 062)"))
    return flags


def classify(item_dir, today):
    """(status, detail) for one work item folder."""
    scope, opened, (waived, waived_line, who) = read_request(item_dir / "request.md")
    extra = f"; {waived_line}" if waived_line else ""
    if scope == "FAST" and not FAST_BY_PERSON.search((item_dir / "request.md").read_text(encoding="utf-8")):
        return "SKIPPED", f"FAST needs (person, <date>): only the person may shorten the pipeline (item 042){extra}"
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
        verdicts = re.findall(r"^A1 result:\s*(\w+)", audit.read_text(encoding="utf-8"), re.M) \
            if audit.exists() else []
        if item_dir.name not in PRE_A1_LINE and not verdicts:
            return "awaiting A1", f"{scope}{extra}"
        if verdicts and verdicts[-1].upper() == "FAIL":
            return "A1 FAIL", f"{scope}; sent back, needs a later A1 PASS line (item 042){extra}"
        return "complete", f"{scope}{extra}"
    return "in progress", f"{scope}: next {need[len(have)]}{extra}"


def incomplete(item_dir, logs=Path("logs")):
    """Item 043: what is missing from a step's own checklist ([] = nothing)."""
    if not item_dir.name.isdigit() or int(item_dir.name) < CHECKLIST_FROM:
        return []
    missing = []
    ver = item_dir / STEPS["06"]
    if ver.exists() and not re.search(r"^.*Recurring issues checked:.*RI-\d", ver.read_text(encoding="utf-8"), re.M):
        missing.append("06 has no 'Recurring issues checked: RI-...' line")
    text = "".join(f.read_text(encoding="utf-8") for sub in ("research", "implementation")
                   for f in sorted((logs / sub).glob("*.md")) if (logs / sub).is_dir())
    unlogged = [AGENT[s] for s in sorted(AGENT) if (item_dir / STEPS[s]).exists()
                and not re.search(rf"\|\s*{AGENT[s]}\s*\|\s*{item_dir.name}\s*\|", text)]
    if unlogged:
        missing.append(f"no log line for {' '.join(unlogged)}")
    if int(item_dir.name) >= LOG_CHECK_FROM:
        bad = sorted({m[3] for m in (LOG_LINE.match(l) for l in text.splitlines())
                      if m and m[4] == item_dir.name and not re.fullmatch(LOG_FORMAT[m[3]], m[5].strip())})
        if bad:
            wants = "; ".join(f'{a} wants "{LOG_HINT[a][0]}"' for a in bad)
            missing.append(f"log line for {' '.join(bad)} does not match its format (item 045): {wants}")
    return missing


def write_log(agent, item, fields, now=None):
    """Item 045: append `HH:MM | agent | ID | fields` (UTC) to today's research or implementation
    log. Exit code 2 and nothing written when the agent, ID or fields are not in the format."""
    if agent not in LOG_FORMAT or not re.fullmatch(r"\d{3}", item) \
            or not re.fullmatch(LOG_FORMAT[agent], fields.strip()):
        print(f"--log refused: {agent} | {item} | {fields} does not match "
              f"{chr(34) + LOG_HINT[agent][0] + chr(34) if agent in LOG_HINT else 'an agent R1 R2 R3 I1 I2 I3'}",
              file=sys.stderr)
        return 2
    if not (Path("work") / item / "request.md").exists():
        print(f"--log refused: no work/{item}/request.md (item 047)", file=sys.stderr)
        return 2
    now = now or dt.datetime.now(dt.timezone.utc)
    team = "research" if agent[0] == "R" else "implementation"
    log = Path("logs") / team / f"{now:%Y-%m-%d}.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    head = "" if log.exists() else f"# {team.capitalize()} log - {now:%Y-%m-%d}\n\n"
    line = f"{now:%H:%M} | {agent} | {item} | {fields.strip()}"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"{head}{line}\n")
    print(line)
    return 0


def orphan_log_lines():
    """Item 047: `<ID> (<log file>)` for every agent log line whose work/<ID>/ folder is missing."""
    orphans = []
    for team in ("research", "implementation"):
        for f in sorted((Path("logs") / team).glob("????-??-??.md")):
            ids = {m[4] for m in map(LOG_LINE.match, f.read_text(encoding="utf-8").splitlines()) if m}
            orphans += [f"{i} ({f.as_posix()})" for i in sorted(ids) if not (Path("work") / i).is_dir()]
    return orphans


def late_log_lines():
    """Item 045: committed log lines (items from LOG_CHECK_FROM on) timed after the commit that
    added them, by `git blame`. None when git is not available here."""
    if _git("rev-parse", "HEAD") is None:
        return None
    late = []
    for team in ("research", "implementation"):
        for f in sorted((Path("logs") / team).glob("????-??-??.md")):
            out = _git("blame", "--line-porcelain", "--", str(f))
            if out is None or out[1] != 0:
                continue
            ctime = None
            for row in out[0].splitlines():
                if row.startswith("committer-time "):
                    ctime = int(row.split()[1])
                elif row.startswith("\t"):
                    m = LOG_LINE.match(row[1:])
                    if m and ctime and int(m[4]) >= LOG_CHECK_FROM and m[4] not in LOG_TIME_EXCEPT:
                        stated = dt.datetime.fromisoformat(f"{f.stem}T{m[1]}:{m[2]}+00:00")
                        commit = dt.datetime.fromtimestamp(ctime, dt.timezone.utc).replace(second=0)
                        if stated > commit:
                            late.append(f"{m[4]} {m[3]} ({f.stem} {m[1]}:{m[2]} after commit "
                                        f"{commit:%Y-%m-%d %H:%M} UTC)")
                    ctime = None
    return late


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


def open_branches(today=None):
    """One dict per remote branch not merged into HEAD (items 034, 037, 038, 039): ref, items
    {item: set of step codes}, conflicts, recurring, clashes, skipped [(item, detail)], last."""
    out = _git("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")
    if out is None or out[1] != 0:
        return []
    today = today or dt.datetime.now(dt.timezone.utc).date()
    behind = main_ahead() > 0
    found = []
    for ref in out[0].split():
        if ref.endswith("/HEAD") or "/" not in ref:
            continue
        # HEAD is behind main: main and refs already in main are not open work (item 051)
        if behind and (ref == MAIN or _git("merge-base", "--is-ancestor", ref, MAIN)[1] == 0):
            continue
        merge = _git("merge-tree", "--write-tree", "--name-only", "--no-messages", "HEAD", ref)
        conflicts = None
        if merge is not None and merge[1] in (0, 1):
            conflicts = merge[0].splitlines()[1:] if merge[1] == 1 else []
        # what merging the branch would change: HEAD vs the merge result. `HEAD...ref` uses one
        # merge base, so with two (criss-cross) a PR already merged looks like this branch's (052)
        tree = merge[0].split()[0] if conflicts is not None and merge[0].strip() else None

        def changed(*paths):
            out = _git("diff", "--name-only", "HEAD", tree, "--", *paths) if tree else None
            if out is None or out[1] != 0:
                out = _git("diff", "--name-only", f"HEAD...{ref}", "--", *paths)
            return out[0].split() if out and out[1] == 0 else []

        # items the branch changes, with every step file it has for them
        touched = {n.split("/")[1] for n in changed("work/") if n.count("/") == 2}
        items = {i: set() for i in touched}
        files = {i: [] for i in touched}
        listing = _git("ls-tree", "-r", "--name-only", ref, "--", "work/")
        for name in (listing[0].splitlines() if listing and listing[1] == 0 else []):
            parts = name.split("/")
            if len(parts) == 3 and parts[1] in items:
                files[parts[1]].append(parts[2])
                if parts[2] in STEPS.values():
                    items[parts[1]].add(parts[2][:2])
        recurring = bool(changed(RECURRING))
        rules = changed(*RULE_PATHS)
        bases = _git("merge-base", "--all", "HEAD", ref)
        bases = bases[0].split() if bases and bases[1] == 0 else []
        clashes, skipped, requests = [], [], {}
        for item in sorted(touched):
            req = f"work/{item}/request.md"
            theirs = _git("show", f"{ref}:{req}")
            requests[item] = theirs[0] if theirs and theirs[1] == 0 else None
            mine = Path(req)
            if (bases and theirs and theirs[1] == 0 and mine.exists()
                    and all(_git("cat-file", "-e", f"{b}:{req}")[1] != 0 for b in bases)
                    and theirs[0] != mine.read_text(encoding="utf-8")):
                clashes.append(item)
            if theirs and theirs[1] == 0 and item not in LEGACY:
                with tempfile.TemporaryDirectory() as tmp:
                    d = Path(tmp) / item
                    d.mkdir()
                    for f in files[item]:
                        body = _git("show", f"{ref}:work/{item}/{f}")
                        (d / f).write_text(body[0] if body else "", encoding="utf-8")
                    status, detail = classify(d, today)
                if status == "SKIPPED":
                    skipped.append((item, detail))
        # item 062: the branch is one unit; its RESEARCH ONLY items may not change code
        unit = changed(*RESEARCH_CODE_PATHS) + [f"work/{i}/{f}" for i in sorted(touched) for f in files[i]]
        for item, detail in _research_code(unit, requests.get):
            have = [k for k, (i, _) in enumerate(skipped) if i == item]
            if have:
                skipped[have[0]] = (item, f"{skipped[have[0]][1]}; {detail}")
            else:
                skipped.append((item, detail))
        when = _git("log", "-1", "--format=%cs", ref)
        last = dt.date.fromisoformat(when[0].strip()) if when and when[1] == 0 and when[0].strip() else None
        found.append({"ref": ref, "items": items, "conflicts": conflicts,
                      "recurring": recurring, "clashes": clashes,
                      "skipped": skipped, "last": last, "rules": rules})
    return found


def _open_at(parent, item):
    """Item 053: is work item `item` still going through the pipeline at commit `parent`?
    PRE_A1_LINE and LEGACY items are closed; otherwise open when its 07 is absent there, has no
    `A1 result:` line, or its last one is FAIL (as classify)."""
    if item in PRE_A1_LINE or item in LEGACY:
        return False
    audit = _git("show", f"{parent}:work/{item}/07-audit-task.md")
    if audit is None or audit[1] != 0:
        return True
    verdicts = re.findall(r"^A1 result:\s*(\w+)", audit[0], re.M)
    return not verdicts or verdicts[-1].upper() == "FAIL"


def _walk(cutoff):
    """Items 053/062: HEAD's first-parent commits after `cutoff`, each with the files it changes
    against its first parent: ([(sha, files or None if diff-tree failed)], None), or
    (None, (text, failed)) when the cutoff can't be used. Needs git."""
    note = f" (cutoff {cutoff[:7]} from --untracked-from)" if cutoff != UNTRACKED_FROM else ""
    known = _git("rev-parse", "--verify", "-q", f"{cutoff}^{{commit}}")
    if known[1] != 0 or _git("merge-base", "--is-ancestor", cutoff, "HEAD")[1] != 0:
        shallow = _git("rev-parse", "--is-shallow-repository")
        if shallow[1] == 0 and shallow[0].strip() == "true":
            return None, (f"not checked (cutoff {cutoff[:7]} not in this shallow clone; run git fetch --unshallow)"
                          + note, False)
        return None, (f"cutoff {cutoff[:7]} not in HEAD's history (squash/rebase or wrong SHA)" + note, True)
    walk = _git("rev-list", "--first-parent", "--reverse", f"{cutoff}..HEAD")
    if walk[1] != 0:
        return None, (f"cutoff {cutoff[:7]}: git rev-list failed" + note, True)
    units = []
    for c in walk[0].split():
        diff = _git("diff-tree", "-r", "--name-only", "--no-renames", f"{c}^1", c)
        units.append((c, diff[0].split("\n") if diff[1] == 0 else None))
    return units, None


def untracked_changes(cutoff=UNTRACKED_FROM, walked=None):
    """Item 053 (RI-007): None without git, else (text after `UNTRACKED CHANGE: `, failed).
    `walked` is _walk(cutoff) when main() already has it."""
    if _git("rev-parse", "HEAD") is None:
        return None
    note = f" (cutoff {cutoff[:7]} from --untracked-from)" if cutoff != UNTRACKED_FROM else ""
    units, error = walked or _walk(cutoff)
    if error:
        return error
    entries = []
    for c, files in units:
        if files is None:
            entries.append(f"{c[:7]} (git diff-tree failed)")
            continue
        code = [f for f in files if f.startswith(CODE_PATHS)]
        if not code:
            continue
        items = sorted({m[1] for m in map(STEP_FILE.match, files) if m})
        if not any(_open_at(f"{c}^1", i) for i in items):
            entries.append(f"{c[:7]} {' '.join(code)}")
    if not entries:
        return "none" + note, False
    return ("; ".join(entries) + " (item 053: code, config, tests or rules changed with no step file of an "
            "open work item; a follow-up to a completed item is a new item)" + note, True)


def research_code(cutoff=UNTRACKED_FROM, walked=None):
    """Item 062 (RI-007): None without git, else (text after `RESEARCH CODE: `, {ID: (sha7, detail)})
    for RESEARCH ONLY items whose HEAD commits after the cutoff change RESEARCH_CODE_PATHS. Scope
    and waiver are read from work/<ID>/request.md in the working tree. A cutoff problem is
    UNTRACKED CHANGE's (053) and is not reported twice; a diff-tree failure is 053's entry."""
    if _git("rev-parse", "HEAD") is None:
        return None
    units, error = walked or _walk(cutoff)
    if error:
        return "not checked (see UNTRACKED CHANGE)", {}

    def request_text_of(item):
        req = Path("work") / item / "request.md"
        return req.read_text(encoding="utf-8") if req.is_file() else None

    flagged = {}
    for c, files in units:
        for item, detail in _research_code(files or [], request_text_of):
            if item in flagged:
                sha, old = flagged[item]
                flagged[item] = (sha, f"{old}; {c[:7]} {detail}")
            else:
                flagged[item] = (c[:7], detail)
    return ", ".join(sorted(flagged)) or "none", flagged


MAIN = "origin/main"


def main_ahead():
    """Commits on origin/main that HEAD lacks (item 051); 0 when there is no origin/main."""
    ref = _git("rev-parse", "--verify", "-q", MAIN)
    if ref is None or ref[1] != 0:
        return 0
    n = _git("rev-list", "--count", f"HEAD..{MAIN}")
    return int(n[0].strip()) if n and n[1] == 0 and n[0].strip().isdigit() else 0


def next_id():
    """The next free work item ID over HEAD and every unmerged remote branch (item 037)."""
    ids = [int(p.name) for p in Path("work").iterdir() if p.name.isdigit()] if Path("work").is_dir() else []
    out = _git("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")
    for ref in (out[0].split() if out and out[1] == 0 else []):
        listing = _git("ls-tree", "-d", "--name-only", f"{ref}:work")
        ids += [int(n) for n in (listing[0].split() if listing and listing[1] == 0 else []) if n.isdigit()]
    return f"{max(ids, default=0) + 1:03d}"


def main(argv):
    today = dt.datetime.now(dt.timezone.utc).date()
    if argv[:1] == ["--next-id"]:
        print(next_id())
        return 0
    if argv[:1] == ["--log"]:
        if len(argv) != 4:
            sys.exit(__doc__)
        return write_log(*argv[1:])
    cutoff, rest = UNTRACKED_FROM, list(argv)
    while rest:
        if len(rest) < 2 or rest[0] not in ("--today", "--untracked-from"):
            sys.exit(__doc__)
        if rest[0] == "--today":
            today = dt.date.fromisoformat(rest[1])
        else:
            cutoff = rest[1]
        rest = rest[2:]
    work = Path("work")
    skipped, stuck, awaiting, in_pr, failed, unfinished = [], [], [], [], [], []
    branches = open_branches(today)
    walked = _walk(cutoff) if _git("rev-parse", "HEAD") is not None else None
    untracked = untracked_changes(cutoff, walked)
    research = research_code(cutoff, walked)
    flagged = research[1] if research else {}
    listed = sorted(p for p in work.iterdir() if (p / "request.md").exists())
    for d in listed:
        status, detail = classify(d, today)
        if d.name in LEGACY and status in ("SKIPPED", "in progress"):
            status, detail = "LEGACY", LEGACY[d.name]
        if d.name in flagged:                       # item 062: replaces the classify line
            status, detail = "SKIPPED", f"{flagged[d.name][0]} {flagged[d.name][1]}"
        if status in ("STUCK", "not started", "in progress"):
            here = {s for s, f in STEPS.items() if (d / f).exists()}
            best = max(((len(items.get(d.name, set()) - here), ref, items.get(d.name, set()))
                        for ref, items in ((b["ref"], b["items"]) for b in branches)), default=(0, "", set()))
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
        if status == "A1 FAIL":
            failed.append(d.name)
        gaps = incomplete(d)
        if gaps:
            unfinished.append(f"{d.name} ({'; '.join(gaps)})")
    for item in sorted(set(flagged) - {d.name for d in listed}):   # item 062: no request.md here
        print(f"{item}: SKIPPED ({flagged[item][0]} {flagged[item][1]})")
        skipped.append(item)
    print(f"STUCK: {', '.join(stuck) or 'none'}")
    print(f"AWAITING A1: {', '.join(awaiting) or 'none'}")
    print(f"IN PR: {', '.join(in_pr) or 'none'}")
    ahead = main_ahead()
    if ahead:
        print(f"MAIN AHEAD: {MAIN} has {ahead} commits not in HEAD; merge it before building (item 051)")
    if branches:
        print("OPEN BRANCHES (not merged into HEAD):")
        for b in branches:
            conflicts = b["conflicts"]
            merge = ("merge not checked" if conflicts is None else
                     f"CONFLICTS: {', '.join(conflicts)}" if conflicts else "merges cleanly")
            note = f"; edits {RECURRING} (item 036)" if b["recurring"] else ""
            age = f"; last commit {b['last']} ({(today - b['last']).days} days)" if b["last"] else ""
            print(f"  {b['ref']}: items {', '.join(sorted(b['items'])) or 'none'}; {merge}{note}{age}")
    if _git("rev-parse", "HEAD") is not None:
        ruling = [f"{b['ref']} changes {', '.join(b['rules'])}" for b in branches if b["rules"]]
        print(f"RULES BRANCH: {'; '.join(ruling) + '; build new items on top of it (item 049)' if ruling else 'none'}")
    clashes = [f"{i} ({b['ref']})" for b in branches for i in b["clashes"]]
    print(f"ID CLASH: {', '.join(clashes) or 'none'}")
    for b in branches:
        for item, detail in b["skipped"]:
            print(f"BRANCH SKIPPED: {item} ({b['ref']}: {detail})")
    print(f"A1 FAIL: {', '.join(failed) or 'none'}")
    print(f"INCOMPLETE: {', '.join(unfinished) or 'none'}")
    late = late_log_lines()
    excepted = "; ".join(f"{i}: {why}" for i, why in sorted(LOG_TIME_EXCEPT.items())
                         if (work / i / "request.md").exists())
    excepted = f" (not checked: {excepted})" if excepted and late is not None else ""
    print(f"LOG TIME: {'not checked (no git)' if late is None else (', '.join(late) or 'none') + excepted}")
    print(f"UNTRACKED CHANGE: {'not checked (no git)' if untracked is None else untracked[0]}")
    print(f"RESEARCH CODE: {'not checked (no git)' if research is None else research[0]}")
    orphans = orphan_log_lines()
    print(f"ORPHAN LOG: {', '.join(orphans) or 'none'}")
    print(f"SKIPPED: {', '.join(skipped) or 'none'}")
    return 1 if skipped or failed or unfinished or late or orphans or (untracked and untracked[1]) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
