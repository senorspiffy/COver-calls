# Work item 052
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-10

## What we want
`check_pipeline.py`'s open-branch checks (items, RULES BRANCH, item-036 note, ID CLASH, BRANCH SKIPPED) must report only what merging the branch would change, even when the branch and HEAD have more than one merge base.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- A1 on main a30101c (PR #15 merged 2026-11-09 23:34 UTC), 2026-11-10 after `git fetch origin`:
  `origin/daily-fixes/2026-11-09: items 049, 050, 051; merges cleanly; ...`
  `RULES BRANCH: origin/daily-fixes/2026-11-09 changes .claude/agents/a1-auditor.md, .claude/commands/run-item.md, scripts/check_pipeline.py; build new items on top of it (item 049)`
- 049 and 050 are already on main (PR #15). `git diff --name-only main origin/daily-fixes/2026-11-09` lists only 051's files, scripts/check_pipeline.py and tests/test_pipeline_check.py: the branch does not touch a1-auditor.md or run-item.md.
- `git merge-base --all main origin/daily-fixes/2026-11-09` → bfb0cfe and f74949a (criss-cross: PR #16's branch was cut from PR #15's head and merged main's 11-09 audit; then main merged PR #15). `git diff HEAD...ref` uses one base (bfb0cfe), so PR #15's changes look like PR #16's.
- `git diff --name-only HEAD $(git merge-tree --write-tree HEAD origin/daily-fixes/2026-11-09 | head -1)` → only 051's files, check_pipeline.py, the test file and 2 log files: the right answer.

## Root cause and prevention guardrail (BUG only)
Root cause: `open_branches()` (scripts/check_pipeline.py) assumes one merge base: it takes changed files from `git diff HEAD...<ref>` and the clash base from `git merge-base HEAD <ref>`. The daily routine creates two merge bases whenever a fix branch is built on an open PR and merges main, and that PR is then merged. This happens every time 049's "build on top of the RULES BRANCH" rule is followed.
Guardrail: take the changed files from `git diff --name-only HEAD <merge-tree result>` (what a merge would change; merge-tree is already run for CONFLICTS) and check the clash base against every `merge-base --all` result. A test builds the criss-cross case (branch B built on PR branch A, A merged into main after B merged main) and asserts B lists only its own item and no RULES BRANCH file it did not change.

## Recurring issue link (RI-#, if any)
New RI-011 (count 1). Related to RI-009 (open-branch view), different root cause.

## Done looks like
On main today: `origin/daily-fixes/2026-11-09: items 051`, RULES BRANCH names only scripts/check_pipeline.py. The criss-cross test passes; with the old `HEAD...ref` diff it fails.
