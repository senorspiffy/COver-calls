# 02 Improvements - 036
## What past logs say
See `logs/audit/2026-11-02.md` and `logs/recurring-issues.md` (RI-007, RI-009). Item 026 built the check; 031 and 033 tightened it; this item covers what they could not see.
## 3 ways FOR
1. The check says what is true (done but unmerged, or unaudited) instead of what is on main only.
2. A test pins it, so a later edit can't loosen it silently.
3. The person gets fewer wrong questions in the daily report.
## 3 ways AGAINST
1. The script now depends on git state (fetched refs); a stale fetch shows stale branches. a1 says to fetch first.
2. More lines in the output to read.
3. One more rule for agents to remember.
## Findings by language
Languages: N/A (no new external claims). This changes code, wording or process inside this repo only.
## Holes to watch out for (summary)
See AGAINST list.
