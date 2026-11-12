# 05 Build report - 054
## Changed files
- config/tickers.json: SOFI, BAC (ex-div Dec 4 $0.32), CSX, OXY, PYPL, CCL (estimated Dec 18 earnings, labelled).
- config/weekly.json (new): 12 stocks, cash $96,200, max_positions 12, max_single_name_frac 1/12.
- tests/test_practice.py: test_weekly_account_gives_each_stock_8000_and_has_facts.
## Tests
`python3 -m pytest -q` → 206 passed, 1 skipped in 22.90s
## Run
`python -m ccbot scan --config config/weekly.json --broker webull-paper --variant V2 --date YYYY-MM-DD --state-dir state_weekly --out reports_weekly`
