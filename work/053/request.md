# Work item 053
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-11

## What we want
Every commit on main that changes code, config, tests or rules (`ccbot/`, `config/`, `scripts/`, `tests/`, `.claude/`) must belong to a work item that is still going through the pipeline, and `check_pipeline.py` must say so when one does not. Also: settle PBR's earnings and dividend facts entered in 3ba835e.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- Commit 3ba835e (2026-11-11 21:50 UTC, merged as PR #18, de5406c): "PBR: enter Nov 10 report date so it is no longer blocked (048 follow-up)". Changes `config/tickers.json` (PBR `next_earnings` 2026-11-10 → null, `last_earnings` null → 2026-11-10, sources rewritten), `tests/test_practice.py` (expected blocked set `{"PBR"}` → `set()`), and appends "## Follow-up 2026-11-11" to `work/048/05-build-report.md`.
- 048 was already complete: `work/048/07-audit-task.md` line 7 `A1 result: PASS (2026-11-07, ...)`. No R1–I3 step and no A1 check covers the follow-up; no log line for it in logs/; no new work/<ID>/.
- The new PBR source line itself says the report is "not confirmed" ("snapshot Oct 27: the report itself not confirmed"). `ccbot/missing.py:20` gives `tickers.last_earnings` policy `block` ("no estimate"); a scheduled date entered as a past report fills that field with an unconfirmed value. A quick search (2026-11-11) found coverage of a Petrobras dividend increase (oilandgas360.com, "petrobras hikes dividend as production surge offsets lower oil prices"), so PBR's `ex_div_date`/`dividend` (both null) may also be out of date. R1 to confirm from primary sources (Petrobras IR).
- `python3 scripts/check_pipeline.py` on main de5406c: exit 0, INCOMPLETE/SKIPPED/LOG TIME/ORPHAN LOG all none: the check did not see it. `python3 -m pytest -q` → 205 passed, 1 skipped.

## Root cause and prevention guardrail (BUG only)
Root cause: the RI-007 guardrails (026, 031, 035, 038, 042) all check the step files of work items. A change written as a note inside an item that already has its A1 PASS has every step file, so it shows `complete`; nothing ties a code/config commit to an item that is still open. The rule "a fix made outside the pipeline gets a work item the same day" depends on the daily audit reading every diff by hand.
Guardrail: `check_pipeline.py` prints `UNTRACKED CHANGE: <sha> <files>` (an error, exit 1) for every commit on the checked branch after a cutoff (this item's merge) that touches `ccbot/`, `config/`, `scripts/`, `tests/` or `.claude/` and does not add or change a step file of a work item whose `A1 result:` line was not yet written at that commit. A test builds both cases (a commit with a new item's files passes; a commit that edits a completed item's 05 plus config fails). Add one line to run-item.md and a1-auditor.md: a follow-up to a completed item is a new item.

## Recurring issue link (RI-#, if any)
RI-007, occurrence 5 → ESCALATED.

## Done looks like
On this branch, a scratch copy of 3ba835e's shape (completed item's 05 + config change, after the cutoff) gives `UNTRACKED CHANGE:` and exit 1; main's history before the cutoff stays clean (exit 0). PBR's `last_earnings`, `ex_div_date` and `dividend` either cite a primary source confirming them or stay null/blocked as the policy says.
