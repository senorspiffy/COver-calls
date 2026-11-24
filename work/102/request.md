# Work item 102
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-24
## What we want
1. A test proves commit_step's `--trailer` refusals run before any git call.
2. FROM / FROM-1 boundary pins for CHECKLIST_FROM, LOG_CHECK_FROM, TESTS_FORMAT_FROM, SUITE_FROM, TIMED_FROM, WHOLE_DIFF_FROM and VERDICT_FROM.
3. Decide (person's OK needed, RULE_PATHS) whether i1's plan text gets the "one mutant per refusal condition and per *_FROM boundary" sentence.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-24-098.md (PR #37): moving the `_trailer_ok` loop to just before commit-tree passes all 40 commit_step tests (T-b checks only HEAD and .git/index; loose blobs are written). work/098/03 Residuals (b), (c).
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: T-b variant with a recording `run` asserting zero git calls on a bad trailer; a parametrized FROM-boundary test over the 7 constants.
## Recurring issue link (RI-#, if any)
RI-010 (commit_step), RI-001.
## Done looks like
The moved-loop mutation and a FROM-1 shift per constant each fail a named test.
