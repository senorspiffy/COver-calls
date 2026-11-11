# 05 Build report - 048
## Changed files
- config/tickers.json: T, VZ, PFE, KMI, CMCSA, KEY, HBAN, PBR, ITUB, KGC added, each with sources.
- config/practice.json (new): 13 stocks, cash $65,200, max_positions 13, max_single_name_frac 1/13.
- config/paper.json: cash 5000.
- tests/test_practice.py (new, 4 tests).
## Tests
`python3 -m pytest -q` → 187 passed, 1 skipped.
## Run
`python -m ccbot scan --config config/practice.json --broker webull-paper --date YYYY-MM-DD --state-dir state_practice --out reports_practice`

## Follow-up 2026-11-11
PBR: `last_earnings` set to 2026-11-10 (the confirmed scheduled date, now past), `next_earnings` cleared, per 07's note. Estimate: Nov 10 + 70 = Jan 19, 2027, after the Dec 18 expiry. The report itself is not confirmed by the source snapshot (labelled in sources).
