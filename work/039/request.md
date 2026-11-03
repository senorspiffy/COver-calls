# Work item 039
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-03

## What we want
Show each open branch's last commit date and age on its OPEN BRANCHES line, so a branch that has waited for days stands out.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `origin/claude/project-thread-xrug2s` (PR #5): last commit e64e22d, 2026-10-31 15:49 UTC, 3 days old. The OPEN BRANCHES line gives no date, and two daily audits passed it without comment (logs/audit/2026-11-01.md, 2026-11-02.md).

## Done looks like
`  <branch>: items ...; ...; last commit <YYYY-MM-DD> (<n> days)`, with n counted to --today. Test pins it.
