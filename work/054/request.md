# Work item 054
Type: FEATURE
Scope: FULL
Opened by: person (Toastedbrown), project thread
Date: 2026-11-12

## Ask
"Are there any max 80 dollar stocks we can test out that do weekly or biweekly?" then "Yeah let's do it" (2026-11-12, after a 12-stock shortlist and an offer of a weekly practice run at $8,000 per stock).

## Done looks like
`config/weekly.json`: a separate paper account (webull-paper ledger) with the 12 weekly-option stocks, $8,000 each, run with `--variant V2` (weekly 5–9 DTE). Ticker facts for the 6 new names in `config/tickers.json`. Tests pass. A scratch scan runs on the VPS before it joins the daily task.
