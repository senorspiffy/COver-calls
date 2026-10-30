# 01 Research brief - 004
## Question
What expiry rule and strike rule always have a candidate, stay consistent with 001's evidence for monthly expiries around 30–45 DTE, and match what the 002 bot does?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. tastylive: "At tasty*live*, we like to target 25-50 DTE when opening positions, with 45 days being our sweet spot." It also says "This window allows us to maximize the theta decay in our position while also allowing ourselves enough time to be right about our assumption." [https://www.tastylive.com/definitions/days-to-expiration-dte] The underlying study data is still not seen (001 C7 UNVERIFIED stands).
- F2. Cboe BXM, the covered-call benchmark that 001 relies on, sells "a succession of one-month, at-the-money call options" held "to maturity, generally the third Friday of each month", and then rolls into the next month. So the benchmark sells the next monthly, whatever its exact DTE (about 28–35 days at the roll). [https://www.govinfo.gov/content/pkg/FR-2008-06-18/pdf/E8-13703.pdf]
- F3. 001 C1: theta decay speeds up near expiry, and the steepest is at 5–7 days. [https://tastylive.com/news-insights/time-decay-tick-tock] 001 also cites ORATS (best = 30 DTE) and BXM/BXMD as monthly (001/03 step 4).
- F4. Third-Friday monthlies are 28 or 35 days apart (4 or 5 weeks). Holiday moves (007) can make a gap 34 or 36 days. Calendar arithmetic, computed below.

## Numbers used (show the math)
I computed coverage myself on NYSE sessions 2016-01-01 to 2025-12-31 (2,514 days), using the `exchange_calendars` XNYS calendar and the repo's `expiries.third_fridays`/`pick_expiry`. The question: on what share of days is at least one monthly inside the window?

| Rule | Days with a candidate | Coverage |
|---|---|---|
| 30–45 DTE (001 step 4) | 1,410 / 2,514 | 56.1% |
| 28–49 DTE | 1,861 / 2,514 | 74.0% |
| 25–50 DTE (tastylive range, F1) | 2,080 / 2,514 | 82.7% |
| 21–49 DTE | 2,352 / 2,514 | 93.6% |
| **Monthly nearest 35 DTE, limited to 21–56 (ties → later)** | 2,514 / 2,514 | **100%**; chosen DTE ranged 21–56 |

- A1's 55.2% used a Mon–Fri calendar; my 56.1% uses NYSE sessions. Both are about 55%.
- Why 21–56 always works: the window is 35 days wide (56 − 21), which equals the largest normal gap between monthlies. That it held on every one of the 2,514 days, holiday-moved Thursdays included, is measured above. Beyond 2025 it is not proven.
- Today, 2026-10-30: the monthlies are 11-20 (21 DTE), 12-18 (49 DTE) and 2027-01-15 (77 DTE). |21 − 35| = |49 − 35| = 14, a tie, so the rule takes the later one: **2026-12-18, 49 DTE**. That is the expiry the bot traded today (`SYNTH_A261218C00026000`).
- The bot today uses 30–45 with ±7-day slack, so 23–52 DTE, and A1 measured 95.2% coverage (not 100%). The nearest-to-35 rule gives the same pick where both find one, and it has no "None" days.
- Strike band, Black–Scholes at 35 DTE, r = 4%, $0.50 grid (the grid is assumed; listings per ticker are UNVERIFIED):

| Case | Strike in 0.25–0.30Δ? |
|---|---|
| S = $24, σ 25% | none; adjacent strikes are 0.07–0.09Δ apart |
| S = $17, σ 35% | none |
| S = $12, σ 25% | none; gap 0.16Δ |
| S = $24, σ 50% | two |

  So a 0.05-wide band is often empty. The code's tolerance [0.20, 0.35] is 0.15 wide. It covered every case above except a 0.16Δ gap (S = $12, σ 25%), where the band could still miss.

## Fit for a ~$3k account
- **Proposed 001 step 4:** "Sell the monthly (third-Friday) expiry whose DTE is nearest to 35; never below 21 or above 56 DTE. Log DTE and whether it was inside 30–45 (`in_window`)." This is always feasible (measured), stays inside tastylive's 25–50 most of the time, and is monthly like BXM. Code change: replace `monthly_dte` + `monthly_slack_days` with `monthly_target_dte: 35` and `monthly_dte_limits: [21, 56]`, or keep the slack and write [30, 45] ± 7 = 23–52 into 001 (95.2%, with a "skip the scan" day when there is none). Either is defensible. The first has no empty days.
- **Proposed 001 step 5:** "Strike = listed call nearest 0.275Δ, accepted only if its delta is in [0.20, 0.35] and the strike is ≥ cost basis; otherwise no trade that day (`NO_STRIKE_IN_TOLERANCE`). Log delta and whether it was in 0.25–0.30 (`in_band`)." This is what the code does (04 change 3).
- Guardrail (RI-001): each window rule in 03 carries its coverage %, as above, with the computing command. Keep `tests/test_calendar.py` coverage asserts and add one for the new rule (100% on 2016–2025).

## Open questions
- tastylive's numbers behind 45 DTE (still UNVERIFIED).
- Real listed strike grids and delta spacing for the candidate tickers' monthlies (002 saw weeklies only).
