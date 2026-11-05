# 02 Improvements - 045
## What past logs say
RI-010 (3, ESCALATED): 043's presence check was met by a batch of lines typed after I2's run (logs/audit/2026-11-05.md). RI-006 is the same lesson for counts: take numbers from a script, never by hand (019). RI-007/042: a check of presence, not content, was bypassed before (FAST line, A1 FAIL).
## 3 ways FOR
1. A writer that stamps the time removes the hand-typed field that went wrong; agents run one command instead of formatting a line (also an efficiency gain).
2. The format check makes `see 05` fail, so the counts the person reads in logs are real (same idea as RI-006's script counts).
3. The blame check catches a line typed after its commit even if someone bypasses `--log`, because it compares with git's own record.
## 3 ways AGAINST
1. A line written in the working tree and committed seconds later is fine; a line written a minute early on a slow clock is not caught (the check only catches lines timed after their commit). Accepted: it catches the 2026-11-04 case.
2. Commit times can be set by hand (`GIT_COMMITTER_DATE`); the check trusts git. Accepted: it stops mistakes, not forgery.
3. Older items' lines (before 045) are not checked, so 041–044 stay as they are. Accepted: history is recorded in RI-010, not rewritten.
## Findings by language
Languages: N/A (no new external claims: process change inside this repo; the one URL is git's own manual).
## Holes to watch out for (summary)
Timezone: log times are UTC; the writer and the check must both use UTC. A day's log file name is the UTC date.
