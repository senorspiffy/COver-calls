# 02 Improvements - 018
## What past logs say
First audit cycle; related entries: see logs/recurring-issues.md and logs/audit/2026-10-30.md.
## 3 ways FOR
1. Rounding down guarantees the fill never breaks the ≤ 50% trigger.
2. Avoids an order ticket rejecting $0.235.
3. Example now matches what the person will actually type.
## 3 ways AGAINST
1. Rounding down gives up up to one tick of profit vs rounding to nearest.
2. Tick size differs by option; the rule says 'minimum tick' without listing values (no sourced tick table fetched today, so none is stated).
3. Changes a hypothetical example only; no outcome data exists for the 50% rule either way (001 D3).
## Findings by language
Languages: N/A (no new external claims). This fix only changes arithmetic, counts, or wording inside this repo, so there is nothing an outside source in any language could confirm or contradict. (Applied under the exception proposed in item 022, which is pending the person's review in the same PR.)
## Holes to watch out for (summary)
See AGAINST list.
