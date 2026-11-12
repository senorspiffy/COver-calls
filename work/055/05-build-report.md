# 05 Build report - 055
## Changed files
- config/tickers.json: BMY, USB, MO, MDLZ added with sources.
- config/quality.json (new): 14 names, cash $112,200, max 14, frac 1/14.
- config/weekly.json: trimmed to PFE, VZ, KGC, BAC, CSX, OXY, PYPL; cash $56,200, frac 1/7.
- tests/test_practice.py: quality test added; weekly test updated to 7.
## Tests
`python3 -m pytest -q` → 207 passed, 1 skipped.
## Run
`python -m ccbot scan --config config/quality.json --broker webull-paper --date YYYY-MM-DD --state-dir state_quality --out reports_quality`
