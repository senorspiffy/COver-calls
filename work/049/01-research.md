# 01 Research brief - 049
## Question
How do we (a) clear 048's log errors on main without hiding what happened, and (b) stop the next item from being built under rules that an open branch has already changed?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- No external facts are needed. The change is inside this repo's own scripts and agent text. Sources are repo files and commands (A1 evidence in work/049/request.md).
- `late_log_lines()` blames each log line and flags it when its stated time is after its commit's minute; it checks items from `LOG_CHECK_FROM = 45` on, with no way to name an exception [repo: scripts/check_pipeline.py `def late_log_lines`].
- `LEGACY` and `PRE_A1_LINE` are the existing pattern for an item that predates a rule: a closed dict/set in the script, with the reason printed, and the comment "Never add a new item here" [repo: scripts/check_pipeline.py L109–111, L80–82].
- 048's 04 lists 4 files (`config/tickers.json; config/practice.json; config/paper.json; tests/test_practice.py`); 05 lists the same 4 and `187 passed, 1 skipped` [repo: work/048/04-build-plan.md, 05-build-report.md]. So the I1/I2 fields in format are `FIT | 4 files planned` and `4 files changed | tests 187/188` (188 = 187 passed + 1 skipped; the line already says `187/188`).
- Commit 65adf0c's parent is 87c8573, which has no `--log` and no LOG TIME check; PR #12 (`daily-fixes/2026-11-05`) had them and was open [git log; logs/audit/2026-11-06.md § Open pull requests].
- `open_branches()` already lists every unmerged remote branch and what it changes under `work/`, but not whether it changes the rules (`.claude/`, `templates/`, `scripts/check_pipeline.py`, `scripts/check_handoff.py`) [repo: scripts/check_pipeline.py `def open_branches`].
- run-item.md: "if the item is IN PR, or a file you will change is on an OPEN BRANCH, build on top of that branch (item 034)". 048 changed none of PR #12's files, so this rule did not apply [repo: .claude/commands/run-item.md].
- Every agent runs `check_pipeline.py` at the end of the item (run-item.md) and A1 runs it daily, so a printed line reaches both.
- Rewriting a log line in a new commit moves its `git blame` to the new commit. So editing 048's I1/I2 fields would also clear their LOG TIME flag without fixing their time [git blame semantics; A1 note, to be shown in a test].

## Numbers used (show the math)
- 048 lines flagged today: 6 LOG TIME (R1–I3) and 2 INCOMPLETE (I1, I2) → 1 failing test on main (`test_repo_pipeline_has_no_skipped_items`).
- 048 I2 total: 187 passed + 1 skipped = 188.

## Fit for a ~$3k account
Process only; no trading rule or number changes.

## Open questions
- CI (GitHub Actions) on PRs and main would show a red main at merge. It adds an outside service and needs a token that may push workflow files; is an in-repo check enough? R2/R3 to weigh.
