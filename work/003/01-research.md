# 01 Research brief - 003
## Question
Which ≤ $28 underlyings realistically pass 001's step-3 screen (spread ≤ $0.05, OI ≥ 500, at the target-delta strike) and the 50% single-name cap at $3k, and what should step 1 say instead?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. No diversified US-equity ETF ≤ $28 with liquid options was found among 11 checked (Cboe delayed snapshots 2026-10-08 to 10-30). The ≤ $28 ETFs that come close (KWEB, BITO, UNG) are single-country, single-asset or commodity funds. (002/01 E2) [https://cdn-api.cboe.com/api/global/delayed_quotes/options/KWEB.json] [https://cdn-api.cboe.com/api/global/delayed_quotes/options/BITO.json] [https://cdn-api.cboe.com/api/global/delayed_quotes/options/UNG.json] [https://cdn-api.cboe.com/api/global/delayed_quotes/options/MSOS.json]
- F2. KWEB, BITO, UNG and MSOS pass only at Δ0.11–0.23 (none at 0.25–0.30). MSOS fails (OI 262, spread $0.06). (002/03 L74/L114; 002/01 L75–79)
- F3. Single stocks, Cboe snapshots of the **11-06 weekly**: SOFI ~$16.77 on 10-30, 17.5C Δ0.28, $0.01 wide, OI 12,667 (inside 0.25–0.30). F ~$11.94 on 10-29, 12.5C Δ0.33, $0.04, OI 4,056. T ~$21.09, 21.5C Δ0.37, $0.05. PFE ~$29.56 (> $28). [https://cdn-api.cboe.com/api/global/delayed_quotes/options/SOFI.json] [https://cdn-api.cboe.com/api/global/delayed_quotes/options/F.json] [https://cdn-api.cboe.com/api/global/delayed_quotes/options/T.json] [https://cdn-api.cboe.com/api/global/delayed_quotes/options/PFE.json] (002/02, verified 002/03 L70–76)
- F4. Monthly (30–45 DTE) spreads for all of these: UNVERIFIED. Only weeklies were read (002/02 holes 2). Today's quotes were not re-pulled (point-in-time data above is 2026-10-08 to 10-30).
- F5. Wheel sizing guide: "$5,000 is at the edge of where the system starts to function", with "names in the $15–$40 range". [https://wheelstrategy.substack.com/p/how-much-money-do-you-really-need] (newsletter, 2025-10-25)
- F6. Webull Level 1 covers covered calls and CSPs. [https://www.webull.com/help/faq/10980] (002/03 G4)
- F7. "5 of the last 10 logged scans": the bot already writes every quote it reads to `state/paper_snapshots.csv` (`ccbot/bot.py` L23, L172), so the input exists. `feasible_universe` reads only the snapshots for `asof` (`screen.py`). Nothing counts past scans (grep, 2026-10-30).

## Numbers used (show the math)
- Price cap: ($3,000 − $200) / 100 = $28. Single-name cap: 50% × $3,000 = $1,500, so a single stock needs ≤ $15.00 (100 sh) or a CSP strike ≤ $15.
- SOFI: $1,677 / $3,000 = 55.9%, which **fails** the 50% cap as 100 shares. A CSP at a ≤ $15 strike fits the cap ($1,500), but that is about 10.6% below $16.77 ((16.77 − 15) / 16.77), so its delta is likely far from −0.25 (UNVERIFIED, no put quote read).
- F: $1,194 / $3,000 = 39.8%, which **passes** the cap. Its tolerance strike 12.5C (Δ0.33, $0.04, OI 4,056) passes the screen under the code's [0.20, 0.35]. It fails 001's strict 0.25–0.30 band, and its one in-band candidate was not seen.
- KWEB (ETF, 100% cap): $2,370 ≤ $2,800, so it passes on price, but only at Δ ≤ 0.23 (F2). It is inside the code's tolerance only at Δ0.20–0.23.
- So at the bot's tolerance on the dated quotes: **F (stock, weekly quote) and maybe KWEB** pass. At 001's strict band: only SOFI 17.5C, and SOFI fails the cap.

## Fit for a ~$3k account
- Step 1 should be a **screen result**, not a ticker class. Proposed: "At $3,000, trade one underlying that, on at least 5 of the last 10 logged scans, passes step 3 at the step-5 strike (nearest 0.275Δ within [0.20, 0.35]) of the step-4 monthly, and fits the caps: 100 sh ≤ cash − $200, and for a single stock ≤ 50% of capital (≤ $15/share at $3k). Prefer a diversified ETF if one passes; on 2026-10-30 none did. If none passes: (a) sell a CSP within the caps on a passing ticker, (b) wait/add funds (two names from ~$5.3k, 002/02), or (c) hold a covered-call ETF."
- Based on 002's evidence, the honest $3k picture: one candidate (F, a single stock at ~40% of capital) is plausible, but its monthly liquidity is unchecked. **Waiting for the paper bot's logged monthly scans** before trading is the evidence-backed choice. A CSP is a bridge only if a passing put strike is ≤ $15. These are options to research, not advice.
- "5 of 10": build it. `feasible_universe(cfg, snapshot_log, cash, asof, lookback=10, min_pass=5)` counts the distinct past scan dates in `paper_snapshots.csv` where `_reject` returns None. With fewer than 10 logged scans the result is **"unknown (n scans)"** and the ticker is blocked, not passed (RI-002 policy, see 005). Test: 4 passes in 10 → blocked; 5 → allowed; 3 scans logged → blocked with reason `HISTORY_SHORT`.
- Shipped config: the universe is SYNTH_A/B/C. Real tickers (F, SOFI, KWEB, T) belong in a separate `config/paper.json`, so the shipped-config test stays offline.
- Guardrail (RI-001): every filter rule in `templates/research-handoff.md` gets a field `Feasibility: <n passing> of <n checked>, as of <date>, source/command`, and R3 marks the rule BLOCKED if it is 0 or missing.

## Open questions
- Monthly 30–45 DTE spreads/OI and in-band strikes for F, SOFI, KWEB, T (paper-bot logs).
- Current SOFI put quotes at ≤ $15 strikes.
- Whether the person accepts a single stock (F) or a concentrated ETF (KWEB) (002/01 open Q7).
