# 01 Research brief - 025
## Question
Does the 023 screen agree with 001 step 3 and the bot's missing-data rule, and how do we stop research from passing a ticker on an unknown input?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- 001 Correction step 3 (005): unknown next earnings → test fails, `EARNINGS_UNKNOWN` [work/001/03-handoff.md]
- `MISSING_POLICY['snapshot.next_earnings'] = ('block', 'EARNINGS_UNKNOWN')` [ccbot/missing.py]
- `_reject` returns `EARNINGS_UNKNOWN` for a stock with blank `next_earnings` [ccbot/screen.py]
- 023/01 L70: F/VALE/AAL/NOK next earnings is reasoning, not a published date; L79 'F passes every test with data' [work/023/01-research.md]
- Existing test `test_drop_each_input[snapshot.next_earnings]` already pins blank earnings → `EARNINGS_UNKNOWN` [tests/test_missing_inputs.py L84–92]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-002 occ 7).
## Numbers used (show the math)
F, VALE, AAL: next earnings unpublished → 3 of 3 shortlisted fail step 3; 0 of 8 checked pass all tests.
## Fit for a ~$3k account
Text and process only; it stops a trade the house rule would block.
## Open questions
None.
