# 03 Research hand-off - 023
Status: READY (written after the screen was delivered; item 026)
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F passes every test we could check | 001 Correction step 3 (005); `screen._reject` | WRONG | Next earnings unpublished → `EARNINGS_UNKNOWN` (025) |
| VALE fits (two-name pick) | same | WRONG | `EARNINGS_UNKNOWN` (025) |
| 1 of 8 checked passes every visible test | same | WRONG | 0 pass today (025) |
| F model premium K13.5 $0.235 Δ0.259 | `ccbot.pricing`, T 49/365, r 0.04, σ 0.355, q 0.60/12.33 | VERIFIED | – |
| VALE model premium K13 $0.275 Δ0.290 | `ccbot.pricing`, σ 0.368; q ≈ 6% gives $0.276 Δ0.290 | VERIFIED | – |
| AAL model premium K14 $0.310 Δ0.264 | `ccbot.pricing`, σ 0.466, q 0 | VERIFIED | – |
| F yield 1.9%, VALE 2.3% per 49 days | 0.235/12.33; 0.275/12.00 | VERIFIED | – |
| F + VALE = $2,433 ≤ $2,800; each ≤ $1,500 | 1,233 + 1,200; 0.5 × 3,000 | VERIFIED | – |
| 17 of 39 priced tickers pass the price cap | 01-research.md table | VERIFIED | – |
| Ford ex-date = record date under T+1 | labelled reasoning in 01 | VERIFIED | – |
**Totals:** 10 rows checked → **7 VERIFIED as-is**, **3 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Correction section in screen-summary.md; 001 decision example notes `EARNINGS_UNKNOWN` | 025 | corrected text | grep "EARNINGS_UNKNOWN" in both | 0 of 8 checked pass all tests, 2026-10-30 quotes, 01-research.md + `screen._reject` rule |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Next earnings date (stock) | not published | `EARNINGS_UNKNOWN` (fails step 3) |
| Next ex-dividend date | not found (VALE) | n/a; check before selling near the money |
| Dec 18 chain spread/OI | unreadable (fetch cut off) | unconfirmed; person checks in Webull |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Single-stock cap | price × 100 ≤ 0.5 × 3,000 | 1,233 ≤ 1,500; 1,200 ≤ 1,500 | ✓ |
| Two-name cash rule | Σ price × 100 ≤ 3,000 − 200 | 2,433 ≤ 2,800 | ✓ |
| Earnings test | stock with no published date → fail | F, VALE, AAL unpublished → fail | ✓ (corrected) |
| Totals add up | 7 + 3 + 0 = 10 | 10 | ✓ |
`python3 scripts/check_handoff.py 023` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 10
fact-check rows: 10
totals line: 10 rows -> 7 as-is, 3 fixed, 0 removed
PASS
```
