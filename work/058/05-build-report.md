# 05 Build report - 058
## Changed files
- ccbot/config.py: `monthly_dte_by_ticker`, `dip_entry` defaults and validation; `for_ticker()`.
- ccbot/screen.py: screen uses the ticker's own window.
- ccbot/bot.py: prefetch, `_manage`, `_would_act` use `for_ticker`; `_dip()` gate writes NO_DIP rows for new entries.
- ccbot/rules.py: NO_DIP reason.
- config/default.json: the two new defaults.
- config/stagger.json, dip_base.json, dip_reserve.json: accounts A and B.
- tests/test_budget_paper.py: 8 tests; tests/test_variants.py: NO_DIP listed as bot-only.
## Tests
`python3 -m pytest -q` → 218 passed, 1 skipped. Mutations: dip gate off → 3 failed; screen without for_ticker → 1 failed.
