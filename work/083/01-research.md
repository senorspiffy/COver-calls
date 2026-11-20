# 01 Research brief - 083
## Question
Why did the 2026-11-19 main scan have no quote for VALE 13C 12/18, and what is the smallest safe fix?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Internal item: sources are repo files and the recap.
- F1. `BrokerMarket.chain` requests strikes in [0.7, 1.3] x close only [ccbot/bot.py].
- F2. 0.7 x 9.83 = 6.881, 1.3 x 9.83 = 12.779; 13 is outside [journal/recaps/2026-11-19.md: "chain only had 7-12 strikes"].
- F3. `_capital` uses the quote when present, else `option_mark` (BS on day.vol); the Webull Day has vol NaN, so equity is NaN [ccbot/bot.py, ccbot/broker/webull_sandbox.py].
- F4. NaN capital fails the screen with CAPITAL_UNKNOWN for every ticker [ccbot/screen.py].
## Numbers used (show the math)
13 / 9.83 = 1.322 > 1.3.
## Fit for a ~$5k account
Fixes the main $5k account freeze; no trading rule change.
## Open questions
If Webull has no quote even when asked, equity stays NaN (by design, RI-002).
