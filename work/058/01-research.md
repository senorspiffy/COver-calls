# 01 Research brief - 058
## Question
What must the bot do to run 057's B4 and B5 as live paper accounts, matching the backtest rules?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Internal item: rules come from the 057 replay script on the VPS (C:\Users\Administrator\cover-calls-research\057\run_057.py), as reported by the VPS session on 2026-11-12.
- F1. B4: each stock keeps a fixed monthly window: F, AAL, PFE, CMCSA [30,45]; VALE, T, HBAN [60,75]; otherwise V0. Each sleeve is $20,000/7. [run_057.py, 057-4]
- F2. B5 base: the 7 stocks at 80% of $2,857 each; V0. [run_057.py, 057-5]
- F3. B5 reserve: $4,000 in one separate sleeve; a dip is close <= 0.95 x the highest close of the last 20 days (min 5 days); the first stock to dip is bought fresh (own basis, V0 calls on those lots only). [run_057.py, 057-5]
- F4. The reserve is freed at the first call-away and waits for the next dip; it never refills from elsewhere. [run_057.py, 057-5]
- F5. The bot today has one monthly_dte window for all tickers and no dip gate (ccbot/config.py, ccbot/bot.py).
- F6. The Webull snapshot has no price history; the bot already logs each ticker's daily close to its state's paper_snapshots.csv (ccbot/bot.py `_snap_row`).
## Numbers used (show the math)
$20,000 / 7 = $2,857.14; 0.8 x 2,857.14 = $2,285.71 = $16,000 / 7. Reserve 20000 − 16000 = $4,000.
## Fit for a ~$5k account
Paper only; the main $5k account is unchanged.
## Open questions
The live dip rule uses the bot's own recorded closes, so the reserve can't enter until 5 scans are logged.
