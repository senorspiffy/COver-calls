# 02 Improvements - 038
## What past logs say
See `logs/audit/2026-11-03.md` and `logs/recurring-issues.md` (RI-007, RI-009). Item 034 made open branches visible; this item closes what it missed.
## 3 ways FOR
1. The check reports what is on open branches, not only main.
2. A test pins it, so a later edit can't loosen it silently.
3. The person sees an open PR's problem in the daily report instead of after merge.
## 3 ways AGAINST
1. Depends on fetched refs; a stale fetch shows stale branches (a1 says fetch first).
2. More output lines to read.
3. Reading branch files with `git show` is slower on many branches (one branch today).
## Findings by language
Languages: N/A (no new external claims). This changes code, wording or process inside this repo only.
## Holes to watch out for (summary)
See AGAINST list.
