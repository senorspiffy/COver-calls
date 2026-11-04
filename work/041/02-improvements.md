# 02 Improvements - 041
## What past logs say
See `logs/audit/2026-11-04.md` and `logs/recurring-issues.md`. Read first: RI-002, RI-007, RI-009, RI-010.
## 3 ways FOR
1. Closes the gap A1 showed with a probe, not a guess.
2. A test pins it, so a later edit can't loosen it silently.
3. The person sees the problem in the daily report instead of after merge.
## 3 ways AGAINST
1. More rules for agents to follow; each adds output to read.
2. A strict check can flag older items; limited to the items named in 03.
3. Fixture tests can drift from real files; the repo run in 06 covers that.
## Findings by language
Languages: N/A (no new external claims beyond the Ford release already used in 040).
## Holes to watch out for (summary)
See AGAINST list.
