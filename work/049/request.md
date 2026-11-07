# Work item 049
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-07

## What we want
Main is red: `python3 -m pytest -q` → `1 failed, 199 passed, 1 skipped` (`tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`). Item 048's six log lines break the 045 rules. Fix 048's lines from what its files show, and add a guardrail so a branch built under old rules can't turn main red unseen.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `python3 scripts/check_pipeline.py` on main 4e0e9e8 (after `git fetch origin`), exit 1:
  - `INCOMPLETE: 048 (log line for I1 I2 does not match its format (item 045))`
  - `LOG TIME: 048 R1 … I3 (2026-11-07 20:40 after commit 2026-11-07 20:20 UTC)`: all six lines.
- logs/implementation/2026-11-07.md: `20:40 | I1 | 048 | FIT | see 04` and `20:40 | I2 | 048 | see 05 | tests 187/188 (1 skipped)`. These are the same `see 04` / `see 05` fields as RI-010's third occurrence.
- Commit 65adf0c (2026-11-07 20:20:51 UTC) adds all six lines, each timed 20:40, twenty minutes after the commit. Its parent is 87c8573 (the 2026-11-06 audit), which does not have 045's `--log` or LOG TIME check. Those were on open PR #12 / #13, which the 11-06 audit listed under OPEN BRANCHES.
- PR #14 (048) merged 2026-11-07 20:21 UTC; PRs #12 and #13 merged 20:53 UTC. Nothing re-ran the check on the combined main. The repo has no CI (`.github/` does not exist).
- 048's 04 lists 4 files; its 05 lists 4 changed files and `187 passed, 1 skipped`.

## Root cause and prevention guardrail (BUG only)
Root cause: (1) 048 was built from a main that did not have the rules on an open branch (045's `--log`), so its agent typed the six lines at the end, with a guessed time. run-item.md (item 034) only says to build on an open branch that changes *a file you will change*; it says nothing about an open branch that changes the *rules* (`.claude/`, `scripts/check_pipeline.py`). (2) Two PRs that pass alone can fail together, and nothing runs the check on main after a merge, so main stays red until the next daily audit.
Proposed guardrail:
- Fix: 048's I1/I2 fields rewritten from 04/05 (`FIT | 4 files planned`, `4 files changed | tests 187/188`). Their times can't be recovered, so 048 goes on a closed, named list in `check_pipeline.py` (like LEGACY, "never add a new item here") that skips LOG TIME for it with the reason shown in the output. Its lines are not re-timed.
- Rule: run-item.md: if an open branch changes `.claude/`, `templates/` or `scripts/check_pipeline.py`, build on top of it (its rules apply to the new item).
- Check: a GitHub Actions workflow runs `pytest` and `check_pipeline.py` on every PR and on every push to main, so a red main shows on GitHub at the merge, not a day later. (If the push of a workflow file is refused, say so in 05 and leave it to the person.)

## Recurring issue link (RI-#, if any)
RI-010 (ESCALATED) → 4th occurrence. Also RI-009's root cause ("new branches are built without the rules open PRs add").

## Done looks like
On main after merge: `check_pipeline.py` → INCOMPLETE none, LOG TIME shows 048 only as the named exception (not an error), exit 0; `pytest -q` all pass; run-item.md has the rules-branch line; the CI workflow is in `.github/workflows/` (or 05 says why not). Every log line for 049 is written with `--log`.
