# Work item 007
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 002 code (`ccbot/expiries.py::business_days`/`scan_calendar`, `ccbot/broker/webull_sandbox.py` L165). The Thursday fallback was first noted by I3 (06).

## What we want
Live/paper scans must use the exchange calendar, so that expiries moved by a holiday get the right date and OCC symbol.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `business_days` = `pd.bdate_range` (Mon–Fri, no holidays). A1: 2026-06-19 (Juneteenth, a market holiday) is in the calendar, and the June 2026 monthly comes out as 2026-06-19 instead of Thursday 06-18.
- Coming soon: 2026-12-25 and 2027-01-01 are Fridays and market holidays. Weekly (V2) expiries move to Thursday, but the scan computes Friday.
- OCC fallback `fridays(business_days(exp, exp))` on Thursday 2026-06-18 → `[]` (A1 ran it), so no symbols are built.
- The effect is fail-safe (no quotes → no trade) but gives wrong DTE and wrong symbols. The backtest is not affected, since it uses the CSV's own trading dates.

## Root cause and prevention guardrail (BUG only)
Root cause: the scan calendar is a weekday calendar, not the exchange calendar. Guardrail: a holiday list in config (NYSE closures through 2027, dated source) used by `scan_calendar`, and tests for 2026-12-24 (weekly), 2026-06-18 (monthly) and the Thursday OCC fallback.

## Recurring issue link (RI-#, if any)
RI-003 (new).

## Done looks like
The scan for 2026-12-21 picks the 2026-12-24 weekly. The fallback builds Thursday symbols. Tests cover all three dates.
