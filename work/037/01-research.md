# 01 Research brief - 037
## Question
Can two work items get the same ID, and can `check_pipeline.py` report it and hand out IDs that no open branch already uses?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- main `work/025/request.md` is A1's BUG; `origin/claude/project-thread-xrug2s:work/025/request.md` is the person's IDEA [git show, A1 2026-11-03]
- neither file exists at merge base 8d5c9b8 [git cat-file -e 8d5c9b8:work/025/request.md → absent]
- `check_pipeline.py` joins branch items by ID, so 025 shows complete and `IN PR: none` [scripts/check_pipeline.py main(), run 2026-11-03]
- `git ls-tree -d --name-only <ref>:work` lists a branch's item folders without a checkout [git-ls-tree(1)]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-007, RI-009).
## Numbers used (show the math)
Clashing IDs today: 1 (025). Highest ID over main + open branches: 039 → next 040.
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
