# Work item 036
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-02

## What we want
Stop fix branches from editing `logs/recurring-issues.md`, so daily fix PRs stop conflicting with A1's daily commit to main.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- A1 commits `logs/recurring-issues.md` to main every day (82da1c6, 4b996e2, and today).
- PR #7's 014 build report lists `logs/recurring-issues.md` among its changes. Trial merge of PR #7 into main (2026-11-02): the only conflict is `logs/recurring-issues.md`.
- Each conflict needs a hand merge by the person before they can merge the fixes.

## Done looks like
run-item.md and i2-builder say: on a fix branch, guardrail status for an RI entry goes in 05/06 ("RI-00x: guardrail now ..."), not in `logs/recurring-issues.md`. A1's daily review copies it into the file on main. `check_pipeline.py`'s OPEN BRANCHES line (034) flags any branch that touches the file, so A1 sees it.
