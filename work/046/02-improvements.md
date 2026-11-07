# 02 Improvements - 046
## What past logs say
RI-002 (9, ESCALATED): 014 found Day defaults outside a hand-kept enumeration; 041 repeated the pattern with TICKER_FIELDS. The fix that held for Day (014) derives the field list from the dataclass itself (`test_every_day_default_is_listed`).
## 3 ways FOR
1. Same method as 014's Day check, which has held since 2026-11-02.
2. Both sources are covered: a key someone adds to the file, and a key someone adds to the code.
3. Gives the two unlisted keys a written policy, so the report text and the code agree.
## 3 ways AGAINST
1. Reading code with a regex can miss a key read another way (e.g. a loop over names). Mitigation: the test also reads the file's keys.
2. `sources` must be excluded by name; a new non-input key would need the same.
3. Adds two drop tests to maintain.
## Findings by language
Languages: N/A (no new external claims: test and policy text inside this repo).
## Holes to watch out for (summary)
Keep the regex simple and test it on the real file; the test must fail on the A1 probe (`foo_date`).
