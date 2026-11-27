# Work item 117
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-27
## What we want
"New caller on another branch" checks (113's step 0, C1) count only lines a branch added since its merge base with HEAD.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-27-113.md F-2, work/113/06 and 07 (PR #40): step 0 compared line text against HEAD, so origin/main's L760 `(waived, waived_line, who)` (pre-105 text, already in merge base 94a20a5) counted as a new caller and forced step 2-alt. Failed safe (kept `who`).
## Root cause and prevention guardrail (BUG only)
Root cause: the rule diffed whole-branch text against HEAD instead of the branch's own changes since `git merge-base` (RI-002 class: a stale view read as a fact).
Guardrail: the i1 plan template / agent file says such greps use `git diff <merge-base>..<branch>` added lines only; a test fixture with an old line on main that must count 0.
## Recurring issue link (RI-#, if any)
RI-002 class (near miss, safe side, not counted).
## Done looks like
Rule text names the merge-base diff; fixture shows old text counts 0 and an added line counts 1.
