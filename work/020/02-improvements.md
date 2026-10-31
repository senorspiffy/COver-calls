# 02 Improvements - 020
## What past logs say
First audit cycle; related entries: see logs/recurring-issues.md and logs/audit/2026-10-30.md.
## 3 ways FOR
1. Makes the field checkable.
2. Zero extra effort: same script R3 runs.
3. Lets A1 compare R1's log to the brief automatically.
## 3 ways AGAINST
1. Unique URLs ≠ sources actually read (a failed fetch still counts).
2. Old log line (27) is left as is; the definition only applies going forward.
3. Two URLs to the same page with/without 'www' count twice.
## Findings by language
Languages: N/A (no new external claims). This fix only changes arithmetic, counts, or wording inside this repo, so there is nothing an outside source in any language could confirm or contradict. (Applied under the exception proposed in item 022, which is pending the person's review in the same PR.)
## Holes to watch out for (summary)
See AGAINST list.
