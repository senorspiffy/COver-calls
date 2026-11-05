# 01 Research brief - 038
## Question
Can `check_pipeline.py` apply the Scope rules to items on open branches, so a branch built outside the pipeline (PR #5) is reported?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- PR #5 branch has `work/025/request.md` and `05-build-report.md` only [git ls-tree origin/claude/project-thread-xrug2s work/025/]
- PR #5 changes 18 files, +295/−18, including ccbot/tickers.py (new) [git diff --stat main...origin/claude/project-thread-xrug2s]
- PR #5 `tickers.enrich` estimates next earnings as last + 70 days when unpublished [ccbot/tickers.py on the branch]
- main: `MISSING_POLICY["snapshot.next_earnings"] = ("block", "EARNINGS_UNKNOWN")` [ccbot/missing.py]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-007, RI-009).
## Numbers used (show the math)
Open-branch items today: 1 (025 on PR #5). By classify: SKIPPED (missing 01 02 03 04 before 05).
## Fit for a ~$3k account
Process only; no trading, no cost.
## Open questions
None.
