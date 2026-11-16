# 01 Research brief - 068
## Question
(1) What does `python3 -m ccbot.realtest --tickers <names>` reproduce of a full run, and which summary sections need the full
run? (2) Where are MDLZ's two warnings for one earnings gap made, and what is the smallest change that leaves one
line naming the gap dates, with no change to any number? Sources are repo files (no web claims; 0 http URLs).

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- A full run took 11m19s / 11m22s, and 065 ran it six times (I2 x2, I3 x2, A1 x2). [logs/audit/2026-11-15-065.md L54, L102-103]
- `--tickers` is a comma list; with no list, every `data/options/*.csv.gz` is used. SPY is appended whenever prices/SPY.csv exists. [ccbot/realtest.py L860, L864-866]
- `--out` defaults to `reports/real`, so a `--tickers` run without `--out <scratch>` overwrites the published reports with a partial set. [ccbot/realtest.py L859, L867]
- Per-ticker work runs on one ticker's data at a time, with the same `start`, `cfg` and rule. Nothing in `load_ticker`, `simulate` or `summarize` reads another ticker. [ccbot/realtest.py L798-812, L823-829, L140-233, L423, L638-657]
  - So these match a full run for each requested name: that name's `counts_bot_rule_bid[tk]` (incl. warnings, earnings_gap_days, calls_sold), `skipped[tk]`, its rows in bot_rule_by_ticker.csv and grid_in_sample.csv, and trades_<tk>.csv.
- These are portfolio-wide (they depend on which tickers are in the set) and need the full run:
  - `walkforward_picks`: each block's config is the best *mean* over all tickers. [L686-695]
  - walkforward_by_ticker.csv: it uses those pooled picks, so even a requested ticker's row can differ. [L702-705, L831-838]
  - `monte_carlo_2_stocks_1yr`: random pairs drawn from all columns; one non-SPY name gives `{"na": ...}`. [L711-718, L842-844]
  - `period`: min/max over the set. [L845-846]
  - `bxm_vs_spy`: computed over that period. [L847]
  - `tickers` and the `fits_3k` list. [L848-850]
- 065's unreported changes were in exactly these portfolio sections: walkforward_picks (2/10), walkforward_by_ticker (11/17), MC median. [logs/audit/2026-11-15-065.md L85-91]
- Item 067 adds a whole-summary diff (`scripts/diff_reports.py`) for the full before/after. [logs/recurring-issues.md L143-147; work/067/request.md]
- `--tickers` runtime for 1-5 names: UNVERIFIED (not measured here; I2 should time it and record it in 05).
- Warning 1: `load_ticker` appends `"earnings: {gaps} gap(s) > 120 days between dates"`. It has a count only, no dates, and it is added even for an ETF. [ccbot/realtest.py L189-191]
- Warning 2: `simulate` appends `"earnings: gap(s) > 120 days between listed dates (a→b, ...)"` plus "; no call sold inside them (EARNINGS_UNKNOWN)" or "; earnings not checked by this rule". It is skipped for an ETF. [L453-458]
- Both come from the same `_gap_pairs`, so they always agree. `summarize` joins `td.warnings + df.attrs["warnings"]` into one string, which is why MDLZ shows both. [L386-389, L656]
- The count stays available as its own field `earnings_gaps_gt120` (td.earnings_gaps), which is published in counts_bot_rule_bid and the CSV. [L189, L233, L653, L807]
- Tests:
  - None asserts warning 1's text. [tests/test_realtest.py grep "gap(s)": only L285, a simulate-only check]
  - The drop-input test checks the dates in the joined string, which warning 2 alone satisfies. [L399-407]
  - L278-279 already pins exactly one simulate warning holding the dates. [L278-279]
- ETF case: the only ETF earnings file in the data, SPY, is empty, so dropping warning 1 loses no ETF warning today. [data/real/earnings/SPY.csv]
  - An ETF never uses earnings anyway. [ccbot/realtest.py L126, L453]
- run-item.md, i2-builder.md and i3-verifier.md never mention realtest, `--tickers` or reports/real. [grep of .claude/ for "realtest|--tickers|reports/real|summary.json": no match]
  - i2 step 3 and i3 step 2 just say "run the tests and checks listed" / "re-run the tests". [.claude/agents/i2-builder.md L20; .claude/agents/i3-verifier.md L13]

## Numbers used (show the math)
- 6 runs x ~11.3 min ≈ 68 min for 065. [065 audit L54]
- Proposed plan: I2 one full run after the build, plus I3 one full run. Base numbers come from the last published run or from 067's diff base. That is 2 full runs (about 23 min), plus `--tickers` runs (time UNVERIFIED). A1 may reuse I3's output or run once.
- Whether the "before" full run can be reused from reports/real/ is UNVERIFIED: reports/real/ is only valid if it was made at the base commit.

## Fit for a ~$3k account
Research-only backtest tooling. It changes no rule or screen the person follows. No brokerage contact.

## Open questions
- Smallest change, code: delete L190-191 in `load_ticker`. Keep `gaps` / `earnings_gaps`, since `earnings_gaps_gt120` is a published number.
  - Add a test: a fixture with one gap has exactly one "gap" warning in `summarize(...)["warnings"]`, and it names a→b.
  - Expected effect: only the `warnings` strings change, for CMCSA, MO, T, VZ, MDLZ (and ITUB/VALE/PBR if not skipped). Every number should stay the same, which 067's diff can confirm.
- Smallest change, text: one sentence in run-item.md, and the same in i2 step 3 and i3 step 2. "When ccbot/realtest.py's decision path changes, iterate with `--tickers <affected>,SPY --out <scratch>`. Run the full backtest once per step that publishes numbers (I2's 05, I3's 06). walkforward_*, monte_carlo, period and bxm_vs_spy are portfolio-wide and come only from the full run (067 diff)."
- Should A1 reuse I3's scratch output instead of re-running? This is for R2/R3 to decide. It touches a1-auditor.md, which is outside this request's "Done looks like".
