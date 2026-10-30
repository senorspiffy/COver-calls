# Work item 002
Type: IDEA
Opened by: person
Date: 2026-10-30
Scope: FULL PIPELINE (Research -> Implementation -> Audit). Builds on work/001/03-handoff.md.

## What we want
A bot for Webull that helps the person get better at the covered-call strategy and gives some day-to-day or week-to-week "action".
Ideas from the person to evaluate:
- Selling calls on a green (up) day during the week ("sell into strength").
- Weekly cadence instead of monthly.
- A bot that "learns the US stock market" and sells at opportune times (ML/adaptive timing).

Build order (person-facing plan):
1. Backtester: test the 001 strategy and the ideas above on historical data, net of bid-ask spread and Webull fees.
2. Paper-trading bot: daily scan, pick trades by rules, log them as if real, produce a daily/weekly report. No real orders.
3. Live trading through Webull's official API: research only for now. Do NOT build live order placement. It needs the person's explicit go-ahead later.

## Evidence
n/a (new idea)

## Root cause and prevention guardrail (BUG only)
n/a

## Done looks like
A working, tested backtester and paper-trading bot in the repo, with a report comparing the strategy variants, and research on what Webull's API allows for options.
