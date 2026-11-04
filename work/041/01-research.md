# 01 Research brief - 041
## Question
Can `tickers.enrich` treat a past ex-dividend date as unknown, and can every `config/tickers.json` key get a MISSING_POLICY row that a test enumerates?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `enrich` sets `dividend`/`div_next` to 0.0 whenever ex_div_date and amount are present, including a past date [ccbot/tickers.py L48–52; A1 probe F 2026-11-20 → div_next 0.0]
- the earnings date already has a stale guard (`nxt < day.date → None`) [ccbot/tickers.py L44–45]
- MISSING_POLICY `broker.div_next`: 0.0 only when the ex-date is known and not the next trading day [ccbot/missing.py]
- Ford's Q3 release gives the Nov 10 record date and no later dividend date [https://www.businesswire.com/news/home/20261028111591/en/Ford-Reports-Third-Quarter-2026-Financial-Results/]
- `rules.settle_day` early-assignment branch reads `div_next > 0` and EARLY_ASSIGN_CHECK_NA needs a future ex_div_date [ccbot/rules.py L209–219]
- `test_policy_lists_every_optional_input` enumerates CSV and snapshot fields only [tests/test_missing_inputs.py L198–201]

Internal item: sources are files and commands in this repo. Read `logs/recurring-issues.md` first (RI-002, RI-007, RI-009, RI-010).
## Numbers used (show the math)
Probe dates: 2026-11-09 (ex-date tomorrow) → div_next 0.15 (kept); 2026-11-20 (10 days after) → after the fix NaN. tickers.json optional keys: next_earnings, last_earnings, ex_div_date, dividend (asset_type falls back to the broker's) → 3 policy rows (next_earnings with last_earnings as its estimate input, ex_div_date, dividend).
## Fit for a ~$3k account
Changes no caps; makes the paper bot fail safe on a stale date.
## Open questions
None.
