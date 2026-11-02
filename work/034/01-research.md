# 01 Research brief - 034
## Question
Can `check_pipeline.py` and A1 see work that is done on an unmerged branch, and report merge conflicts, so an item in an open PR is never called stuck?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `check_pipeline.py` reads only `Path("work")` in the current tree [scripts/check_pipeline.py main()]
- PR #7 branch `daily-fixes/2026-10-31-stuck` has 01–07 for 009–016; main has request.md only [git ls-tree origin/daily-fixes/2026-10-31-stuck work/, A1 2026-11-02]
- `git branch -r --no-merged HEAD` lists exactly the two unmerged branches (claude/project-thread-xrug2s, daily-fixes/2026-10-31-stuck) [A1 run, 2026-11-02]
- `git merge-tree --write-tree --name-only` (git ≥ 2.38; here 2.43.0) exits 1 and lists conflicted files without touching the work tree [git-merge-tree(1)]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-007, RI-009).
## Numbers used (show the math)
Unmerged remote branches: 2. Items IN PR on main today: 8 (009–016). Conflicts: PR #7 vs HEAD 2 files, PR #5 vs HEAD 3 files.
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
