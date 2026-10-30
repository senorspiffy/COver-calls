# Work item 007
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Let R2 skip the 7-language search on BUG/EFFICIENCY items that make no new outside claims (math or process fixes), and say so in one line.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `.claude/agents/r2-improver.md` requires a 7-language search on every item. Items 002-006 opened today are internal arithmetic, counting and process fixes on files in this repo; there is no outside fact a foreign-language source could confirm or contradict, so the search would be pure repeated work.

## Done looks like
R2's instructions allow "Languages: N/A (no new external claims)" for BUG/EFFICIENCY items whose fix makes no new external factual claim, and require the full search otherwise. IDEA items always get the full search.
