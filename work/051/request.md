# Work item 051
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-09

## What we want
When `check_pipeline.py` runs on a fix branch that main has moved ahead of, it should not list main (or a branch already merged into main) as an OPEN BRANCH with the item-036 warning. It should print one plain line saying main is ahead and should be merged first.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- A1 on PR #15's branch (`origin/daily-fixes/2026-11-07`, scratch worktree), 2026-11-09 after `git fetch origin`:
  `origin/claude/project-thread-rx7mt7: items none; merges cleanly; edits logs/recurring-issues.md (item 036); last commit 2026-11-08 (1 days)`
  `origin/main: items none; merges cleanly; edits logs/recurring-issues.md (item 036); last commit 2026-11-08 (1 days)`
- Both refs point at 217f172, the 2026-11-08 daily audit commit on main. Editing logs/recurring-issues.md on main is exactly what item 036 asks for, so the `(item 036)` note is a false alarm, and run-item's "a file you will change is on an OPEN BRANCH: build on top of that branch" points at main itself.
- `open_branches()` takes every ref from `git branch -r --no-merged HEAD` (scripts/check_pipeline.py `def open_branches`), so any branch behind main sees main this way. It happens after every daily audit commit while a fix PR is open.

## Recurring issue link (RI-#, if any)
None (no error found; noise in RI-009's output).

## Done looks like
On a branch behind main, OPEN BRANCHES leaves out origin/main and every remote branch whose tip is already in origin/main, and a `MAIN AHEAD: origin/main has <n> commits not in HEAD; merge it before building (item 051)` line is printed. `--next-id` still counts main's IDs. A test pins both.
