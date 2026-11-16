# 02 Improvements - 068
## What past logs say
- RI-013 (OPEN, 067): 065's before/after was hand-picked; the changes it missed were all portfolio-wide (walkforward_picks, walkforward_by_ticker, MC median). Any `--tickers` shortcut must never be the published before/after. [logs/recurring-issues.md L143-149]
- RI-002 (065): the interior-gap warning in `simulate` is the guardrail. The merge must keep it and drop only the count-only line. [logs/recurring-issues.md L25; ccbot/realtest.py L453-458]
- No earlier item tried to cut realtest runs. The agent files never name realtest. [01-research.md L33-34]

## 3 ways FOR
1. Put the count into the line that is kept, so it is a real merge with nothing lost: `earnings: {n} gap(s) > 120 days between listed dates (a→b, ...)` + the same EARNINGS_UNKNOWN / "not checked" suffix. Then delete L190-191. The count field `earnings_gaps_gt120` (L653, L807) stays the same, so no number moves. Reasoning: L191 and L455 both come from `_gap_pairs`, so `len(gap_pairs) == gaps` for a stock [01-research.md L25]. Add a one-line assert in the new test.
2. Write the `--tickers` rule as a copyable command with `--out` required: `python3 -m ccbot.realtest --tickers <affected>,SPY --out <scratch>`. Without `--out`, a partial run overwrites reports/real (L859, L867), and that would corrupt 067's diff base. Name the portfolio-only keys in the same sentence: walkforward_*, monte_carlo_2_stocks_1yr, period, bxm_vs_spy, tickers, fits_3k [01-research.md L13-19].
3. Saving, with the math: 065 made 6 full runs ≈ 68 min. The plan is 1 full run in I2 and 1 in I3, about 23 min, so ≈ 45 min saved per realtest item, plus the `--tickers` runs (time UNVERIFIED; I2 records it in 05). It also cuts the chance that reports/real/ is left partway between two runs.

## 3 ways AGAINST
1. "The real-data summary numbers do not change" is true, but the summary *does* change: `counts_bot_rule_bid[tk].warnings` is a string in summary.json (L808). 067's whole-summary diff will flag CMCSA, MO, T, VZ, MDLZ (plus ITUB/VALE/PBR if they are not skipped). If 05 says "no change", that repeats RI-013. 05/06 must paste the diff and list those warnings lines as the only expected change.
2. A `--tickers` "before" run made at a different commit, or a reports/real/ not made at the base commit, gives a false base [01-research.md L39]. The text must say: scratch runs are for iterating only. Published before/after numbers come only from full runs at known commits.
3. Dropping L190-191 removes the gap note for an ETF that has earnings rows. Today the only ETF earnings file (SPY) is empty, so nothing is lost now [01-research.md L31]. And an ETF never uses earnings (L126, L453), so the risk is low. Still, a future ETF file with gaps would be silent. Accept and note it in 05, or keep a short ETF-only line. I2 picks one and says which.

## Findings by language
Languages: N/A (no new external claims). This is internal tooling and wording: one removed warning string plus agent text. Every fact comes from repo files or logs (0 http URLs in 01), and no fee, rule or market statistic is added.

## Holes to watch out for (summary)
- Scope: only run-item.md, i2-builder.md step 3 and i3-verifier.md step 2, plus ccbot/realtest.py and tests/test_realtest.py. Do not edit a1-auditor.md; A1 reusing I3's output is a separate item if wanted. Do not touch 067's files (scripts/diff_reports.py and its test and template field). Point to 067 by name only.
- The test must check `summarize(...)["warnings"]` holds exactly one "gap" line that names a→b and the count, and that `earnings_gaps_gt120` is unchanged. Mutation: restore L191, and the test should fail.
- `--tickers` without SPY drops bxm/SPY checks. Without `--out`, it overwrites reports/real. Both need to be in the sentence.
- I2 must state in 05 that the warnings text is the only diff, using 067's diff output if 067 is merged first. If it is not, say the diff was done by hand and is UNVERIFIED.
