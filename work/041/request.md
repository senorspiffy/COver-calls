# Work item 041
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-04

## What we want
Item 040 added a new input path, `config/tickers.json`, but its facts are not in `MISSING_POLICY`, and one of them turns "unknown" into 0.0. Once a ticker's ex-dividend date in the file has passed, `tickers.enrich` still treats it as known: `dividend` and `div_next` become 0.0 ("no dividend") although the next ex-date is unknown. The earnings date has a stale guard ("a stale date is unknown, never 'no earnings'"); the ex-dividend date has none.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- A1 probe 2026-11-04 on main 8032e0b, `enrich(Day(date, close=12.0), "F", load_facts(config/tickers.json), {"earnings_gap_days": 70})`:
  - 2026-11-09 → `ex_div_date 2026-11-10, dividend 0.0, div_next 0.15` (correct, ex-date is tomorrow)
  - 2026-11-20 → `ex_div_date 2026-11-10, dividend 0.0, div_next 0.0` (stale date; next ex-date unknown, yet "no dividend")
- `ccbot/tickers.py::enrich` L48–52: `dividend = float(amount) if ex_div == day.date else 0.0`; `div_next = ... else 0.0`, with no `ex_div < day.date` check. Compare L44–45 for earnings.
- `ccbot/missing.py` `broker.div_next`: "0.0 only when the ex-date is known and not the next trading day". With a past ex-date, the next one is not known.
- Effect: `rules.py` L209 (early assignment before ex-div) sees `div_next == 0.0`, and L214 `EARLY_ASSIGN_CHECK_NA` cannot fire. A call held across Ford's next (unpublished, ~Feb 2027) ex-date would get no warning, no credit and no `DIVIDEND_UNKNOWN`. The report also shows a negative "days to ex-dividend" (`report.py` L182 `_days_to`).
- `MISSING_POLICY` has no `tickers.*` rows, and `snapshot.next_earnings` still says ("block", "EARNINGS_UNKNOWN") with no mention of 040's estimate. `test_policy_lists_every_optional_input` enumerates only CSV and snapshot fields, so it cannot see the file's keys.

## Root cause and prevention guardrail (BUG only)
Root cause: a new input path (the ticker facts file) was added without policy rows, so the RI-002 enumeration test never covered its keys, and the stale-date rule written for earnings was not applied to the other date in the same file.
Guardrail: (1) in `enrich`, a past `ex_div_date` is unknown (date None, dividend/div_next NaN, as for VALE); (2) `MISSING_POLICY` rows `tickers.next_earnings`, `tickers.ex_div_date`, `tickers.dividend`, and `snapshot.next_earnings` text names the 040 estimate; (3) `tickers.TICKER_FIELDS` lists the file's optional keys and `test_policy_lists_every_optional_input` requires a `tickers.<key>` row for each; (4) drop tests for each new row, including a stale ex-date.

## Recurring issue link (RI-#, if any)
RI-002 (9th occurrence).

## Done looks like
The 2026-11-20 probe gives `ex_div_date None, dividend nan, div_next nan`; the suite has a failing test if the stale guard is removed or a new tickers.json key has no policy row.
