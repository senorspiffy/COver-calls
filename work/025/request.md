# Work item 025
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-10-31

## What we want
The 023 screen tells the person that Ford (F) "passes every test" and Vale (VALE) "fits", and 001's 2026-10-31 decision uses F + VALE as its example. Under 001 step 3 (Correction, item 005) both fail today: their next earnings dates are not published, so the result is `EARNINGS_UNKNOWN`. Correct the person-facing texts, and stop research from passing a ticker on an inferred input.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `work/001/03-handoff.md` § Correction, Step 3 (005): "If OI or the next earnings date is unknown, the test fails (`OI_UNKNOWN`, `EARNINGS_UNKNOWN`); an ETF has no earnings."
- `ccbot/missing.py::MISSING_POLICY`: `"snapshot.next_earnings": ("block", "EARNINGS_UNKNOWN")`; `ccbot/screen.py::_reject` returns `EARNINGS_UNKNOWN` for a stock with no `next_earnings`.
- `work/023/01-research.md` L70: "'Next earnings after Dec 18' for F/VALE/AAL/NOK is reasoning from a quarterly cadence (just reported in late Oct), not a published date." L79: "F passes every test with data."
- `work/023/screen-summary.md` Bottom line: "Ford (F) ... passes every test we could check"; Ford: "The next date isn't published yet"; VALE: "next not published"; "Your decision" section: "Ford ($1,233) + Vale ($1,200)".
- `work/001/03-handoff.md` § Correction, "Step 1 and 9(a), person's decision 2026-10-31": "Each must pass today's step-3 screen on its own. Example from the 023 screen: F ($1,233) + VALE ($1,200)".
- So the paper bot, given the same inputs, would reject F and VALE with `EARNINGS_UNKNOWN`, while the research tells the person they pass. Contradiction between Research and the code.

## Root cause and prevention guardrail (BUG only)
Root cause: the missing-data rule (RI-002) is enforced only in code. Research text has no step that maps each screen test to the bot's reject code, so R1 filled an unknown input (next earnings date) with reasoning and reported a pass. R2/R3 never ran on 023 (see 026), so nobody compared it with 001 step 3.
Guardrail: (1) r1 and r3: any screen of tickers reports, per ticker, the bot's result from `ccbot/screen.TESTS` (first failing code, or PASS). A value that is not published is UNKNOWN and gets the `MISSING_POLICY` result; reasoning may be shown as a note but never turns UNKNOWN into a pass. (2) A test that pins the policy for inferred dates: a stock snapshot with blank `next_earnings` is rejected `EARNINGS_UNKNOWN` even when the last report was days ago.

## Recurring issue link (RI-#, if any)
RI-002 (occurrence 7)

## Done looks like
023 screen-summary and 001's decision example say F and VALE are `EARNINGS_UNKNOWN` today under the house rule (with the quarterly-cadence reasoning shown as a note, and what would change it); r1/r3 carry the reject-code rule; the test exists and passes.
