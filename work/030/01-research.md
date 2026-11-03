# 01 Research brief - 030
## Question
Why do test runs change tracked files?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- 36 tracked paths contain __pycache__ (git ls-files)
- `.gitignore` lists __pycache__/ [.gitignore]
- Added in 5e46bef (git log --diff-filter=A)

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (no linked entry).
## Numbers used (show the math)
36 files; 30 changed after one pytest run.
## Fit for a ~$3k account
Repo hygiene only.
## Open questions
None.
