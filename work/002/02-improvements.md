# 02 Improvements - 002
## What past logs say
First audit cycle; related entries: see logs/recurring-issues.md and logs/audit/2026-10-30.md.
## 3 ways FOR
1. Fixes a rule the person will use when adding money (decides when single stocks are allowed).
2. Self-check table is cheap: one row per threshold.
3. Same section also catches example-vs-rule errors (003).
## 3 ways AGAINST
1. Adds a section to every hand-off (more text).
2. A table can be filled in mechanically without real re-derivation; A1 must spot-check it.
3. Doesn't catch thresholds that live outside the map (e.g. in prose); the R3 rule says 'every numeric threshold in the map'.
## Findings by language
Languages: N/A (no new external claims). This fix only changes arithmetic, counts, or wording inside this repo, so there is nothing an outside source in any language could confirm or contradict. (Applied under the exception proposed in item 007, which is pending the person's review in the same PR.)
## Holes to watch out for (summary)
See AGAINST list.
