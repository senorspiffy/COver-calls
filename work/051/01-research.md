# 01 Research brief - 051
## Question
How should `check_pipeline.py` treat main (and branches already merged into main) when it runs on a branch that main has moved ahead of?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- No external facts are needed: the change is in this repo's own script. Sources are repo files and commands.
- `open_branches()` and `next_id()` both take refs from `git branch -r --no-merged HEAD` [repo: scripts/check_pipeline.py `def open_branches`, `def next_id`].
- On PR #15's branch on 2026-11-09, `origin/main` and `origin/claude/project-thread-rx7mt7` (both 217f172) were listed with `edits logs/recurring-issues.md (item 036)` [A1 run, logs/audit/2026-11-09.md].
- Item 036 says only A1's daily commit on main edits logs/recurring-issues.md [repo: .claude/commands/run-item.md; check_pipeline.py docstring].
- `git merge-base --is-ancestor <ref> origin/main` exits 0 when the ref's tip is in main [git docs: https://git-scm.com/docs/git-merge-base].
- `git rev-list --count HEAD..origin/main` gives the number of main commits not in HEAD [git docs: https://git-scm.com/docs/git-rev-list].

## Numbers used (show the math)
- 2 false OPEN BRANCHES lines today; 0 expected.

## Fit for a ~$3k account
Process only; no trading rule or number changes.

## Open questions
- Should `--next-id` also drop main? R2 to weigh (main can hold new IDs the branch lacks).
