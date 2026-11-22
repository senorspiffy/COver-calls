# Work item 098
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-22
## What we want
Small hardening from the 088-091 audits, in one item:
1. commit_step.py `--trailer` option passed to commit-tree, so no `git commit --amend --only` is needed after each commit (091 A1 N2, I3 follow-up 1; every 091 commit needed an amend).
2. Three surviving mutants (091 A1 N1): ROUND_HEADING_FROM=93 (092 not pinned), cwd-is-repo-top check dropped (refused with wrong reason), symlink name resolved in repo_relative. Add tests; rule: one mutant per refusal condition and per `*_FROM` boundary.
3. Runs under a `## Round 2 build`-style heading are neither read nor flagged (091 A1 N5).
4. 088's `not checked (unborn HEAD)` label also printed for a corrupt/dangling HEAD; docstring says ls-tree exits 1, measured 128 (088 A1 finding 3; 091 I3 follow-up 4).
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-21-088.md finding 3; logs/audit/2026-11-22-091.md N1, N2, N5; work/091/06 follow-ups 1 and 4.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY).
## Recurring issue link (RI-#, if any)
RI-010 (commit_step), RI-014 (HEAD labels).
## Done looks like
Each sub-ask has a test and a mutation that fails it; commits need no amend.
