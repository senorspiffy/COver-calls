# Work item 085
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-20
## What we want
A test that `run_daily` passes each ticker's held option to `BrokerMarket`, so item 083's fix can't be undone at the call site without a test failing.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-20-083.md: both `run_daily` call sites reverted to `BrokerMarket(broker, t, date, log)` -> 344 passed, 1 skipped on main 6b652ff. tests/test_held_quote.py tests only `BrokerMarket.chain`.
## Recurring issue link (RI-#, if any)
RI-001 (083's guardrail), RI-002 (NaN equity path).
## Done looks like
A run_daily test with a held VALE 13C on a $9.83 close: the broker stub sees a window that includes 13 and equity is a number; the call-site mutation fails it.
