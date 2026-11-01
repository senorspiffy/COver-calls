# 02 Improvements - 031
## What past logs say
See `logs/audit/2026-11-01.md` and `logs/recurring-issues.md` (RI-007, RI-008).
## 3 ways FOR
1. Matches the written rule exactly; no judgement needed.
2. One-line change in the waiver's who-field keeps 024 honest about who approved it.
3. A test pins it, so a later edit can't loosen it silently.
## 3 ways AGAINST
1. An agent could still type `person`; the PR review is where the person sees it (run-item already says so).
2. Breaks a pinned test that used an A1 waiver of 03 (test updated).
3. Adds one more rule to remember for waivers.
## Findings by language
Languages: N/A (no new external claims). This changes code, wording or process inside this repo only, so no outside source in any language could confirm or contradict it.
## Holes to watch out for (summary)
See AGAINST list.
