# 02 Improvements - 047
## What past logs say
- 045 (RI-010) made `--log` the only way to write a log line and added format and time checks; it did not check the ID against `work/` (A1 2026-11-06).
- 039, 044 (EFFICIENCY): small `check_pipeline`/`check_handoff` output lines that replace an A1 hand cross-check worked well and were merged.
- RI-009 / 037: a wrong or reused ID is an earlier failure mode; `--next-id` guards new IDs, nothing guards IDs typed at log time.

## 3 ways FOR
1. Removes a daily hand check from A1 (a1-auditor.md job B, first bullet) and makes it repeatable: same answer every run.
2. Stops the error where it starts: `--log` exit 2 tells the agent at once that the ID is wrong, before a commit.
3. Cheap: reuses `LOG_LINE`; one directory test per line; no git needed for the read side, so it also runs outside a repo.

## 3 ways AGAINST
1. A log line written before `request.md` exists would be refused. Reasoning: run-item.md has request.md before R1, so this only hits an out-of-order step, which is itself an error (RI-007). Accept.
2. One more exit-1 line in the daily run can make the run red for a typo. That is the intent; the line names the file so it is quick to fix.
3. Working-tree read also flags an uncommitted line on a fix branch before its work folder is committed. Both live in the same tree, so this only fires if the folder is really missing. Accept.

## Findings by language
Languages: N/A (no new external claims). The fix is a check inside this repo's own scripts: no fee, rule or market fact changes.

## Holes to watch out for (summary)
- Keep the refusal exit code 2 (same as the format refusal) and write nothing.
- Fixture test for `--log` must now create `work/<ID>/request.md` (test_log_writes_utc_line writes for 150 with no folder).
- Answer to R1's open question: read the working tree; simpler, and it catches the typo before commit.
