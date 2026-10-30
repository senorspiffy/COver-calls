# 02 Improvements - 004
## What past logs say
First audit cycle; related entries: see logs/recurring-issues.md and logs/audit/2026-10-30.md.
## 3 ways FOR
1. A script makes counts reproducible by anyone (R3, I3, A1).
2. Definitions of fixed/removed end the ambiguity in the removed list.
3. Exit code lets a future CI or hook enforce it.
## 3 ways AGAINST
1. Script relies on table format (rows start with '|'); a format change needs a script update.
2. Adds a step for R3.
3. Doesn't judge whether each row's verdict is right, only that counts add up.
## Findings by language
Languages: N/A (no new external claims). This fix only changes arithmetic, counts, or wording inside this repo, so there is nothing an outside source in any language could confirm or contradict. (Applied under the exception proposed in item 007, which is pending the person's review in the same PR.)
## Holes to watch out for (summary)
See AGAINST list.
