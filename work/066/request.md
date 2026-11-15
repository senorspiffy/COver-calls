# Work item 066
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-15

## What we want
A test run for one item is not broken by another item's uncommitted step files in the same working tree, and the suite's test output is not padded by asserts that never change between cases. Pick the smallest change.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/implementation/2026-11-15.md: `00:10 | I2 | 063 | 4 files changed | tests 297/299`. work/063/05-build-report.md L98-101: the one failure was `tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`, caused by item 064's uncommitted `work/064/04-build-plan.md` (no I1 log line yet) while both items were built in the same tree. I2 then had to explain a failure that was not its own.
- work/064/06-verification.md: `test_work_code_pattern` repeats three constant `_is_code` asserts in every parametrized case, so one mutation fails all 8 cases (I3: "harmless; A1 may ask for them to be split out").

## Done looks like
Either run-item.md says items run one at a time per working tree (or each in its own worktree), or `test_repo_pipeline_has_no_skipped_items` checks committed state only, whichever is smaller; plus the constant asserts moved to one test. Suite green, same pass count minus the merged cases.
