# 04 Build plan - 061
Fit verdict: FIT WITH CHANGES

Recurring issues checked: RI-001 (ESCALATED), RI-002 (GUARDED, policy applied below), RI-007 (ESCALATED: this
plan is the 04 step that 061 skipped), RI-010 (log line written by the coordinator with `--log`), RI-011 (OPEN; not
touched: no branch-diff code here), RI-012 (OPEN; see DROPPED row for `fetch_real_data.sql`).

## Fit check
- Research and paper only. Nothing here is imported by `ccbot/bot.py`, `rules.py`, `screen.py`, a broker or a config
  (grep of `realtest` in ccbot/: only realtest.py itself). No bot or config change is planned. Fits a ~$3k account as
  research, with one gap: the simulator uses fractional shares, so its per-stock results don't say whether the
  account can hold that stock. At $3,000 the screen allows `price × 100 ≤ 0.5 × 3,000` (SINGLE_NAME_CAP, screen.py
  L26), so only names ≤ $15 qualify. Change 9 adds that column so 01 can say which results apply.
- Conflicts with existing code. The code reuses `pick_expiry`/`pick_strike` (b4ce90e), but it still differs from
  `rules._option_entry` and `costs.fees` in seven places (changes 1-7). The verdict is FIT WITH CHANGES because none of
  these needs new research. 03's Feasibility column is "–", but committed reports already hold non-zero counts for
  every window rule (Rule trace below), and the build pins them.

## Extra research (with sources)
1. **Home-made monthly test misses a real monthly.** `_is_monthly` accepts a Thursday only on day 16-20. In April 2022
   the third Friday (04-15) was Good Friday, so the monthly expired **Thursday 2022-04-14**. That expiry is rejected,
   and no call can be opened for that month from mid-March 2022. Confirmed:
   [Advisor Perspectives 2022-04-14](https://www.advisorperspectives.com/articles/2022/04/14/skittish-stock-traders-are-bracing-for-2-trillion-option-expiration),
   [investingLive 2022-04-13](https://investinglive.com/news/us-stocks-heads-up-for-thursday-monthly-options-expiration-estimated-at-over-2-tln-20220413/amp),
   [MIAX Good Friday 2022 schedule](https://www.miaxglobal.com/alert/2022/04/04/miax-exchange-group-holiday-schedule-good-friday-2022).
   Simpler method: use the bot's own `expiries.third_fridays(calendar)` on the price dates, as `bot.py` L29 and
   `backtest.py` L61 do. It moves a holiday Friday back to the trading day. Then require the picked expiry to be quoted
   that day, which is what `screen._reject` L31 does (`NO_EXPIRY`).
2. **Fees don't match the config they cite.** `REG_FEE = 0.10 + 0.02` charges $0.02 per contract for CAT. The config
   has `cat_rate: 0.000003 × notional` (`costs.fees` L32), about $0.0002 per contract at $0.50. `R = 0.03` vs config
   `r: 0.04`. Fix: call `costs.fees` and `cfg["r"]`.
3. **Earnings data edge case R3 missed.** An empty or short `earnings/T.csv` gives `earnings = []`, so
   `_earnings_between` is always False and calls are sold through earnings without any notice. The bot blocks this
   case (`EARNINGS_UNKNOWN`, rules.py L296). Also, the DoltHub calendar is read as if each date were known in advance.
   That is APPROXIMATE (no record of when a date was published) and must be labelled.
4. **Data-hole hint.** In `grid_in_sample.csv`, d0.150_dte14-24 shows HBAN with 67 calls, against 101-152 for the
   other 16. The bot rule shows HBAN at 53, which is normal. I2 counts HBAN's snapshot days and its 14-24 `NO_EXPIRY`
   rejects, and 01 labels the cause.

## Files to create/change
1. `ccbot/realtest.py` (change):
   1. `_pick(g, today, cfg, calendar, basis) -> (row | None, code)`. Expiry comes from `expiries.third_fridays(calendar)`
      for the 30-45 window. `calendar = expiries.extend(td.close.index, last + 90 d)`. The picked expiry must be in that
      day's quoted expirations, else `NO_EXPIRY`. The 14-24 grid window keeps every quoted expiry (labelled "grid
      variant, not a bot rule"). Delete `_is_monthly`. Return codes: `NO_EXPIRY`, `NO_STRIKE_IN_TOLERANCE`,
      `BASIS_ABOVE_BAND`, `OK`.
   2. Cost-basis floor, copied from rules.py L308-312. `basis` = the price the covered-call arm last bought shares at
      (first close, then the re-buy close + slip after assignment). Track it in `simulate`.
   3. `tolerance` and `target_delta` for BOT_RULE come from `cfg`, not literals. Other grid targets keep ±0.075
      (labelled).
   4. Earnings: `_earnings_between` becomes `a <= e <= b`, to match `screen._reject` L48. If a stock has no earnings
      date ≥ d, the code is `EARNINGS_UNKNOWN` and no call is sold. An ETF (asset_type from `config/tickers.json`, SPY
      default etf) is exempt. Also count gaps of more than 120 days between consecutive earnings dates as a warning.
   5. `take50` buys back only within the first third of the call's life (`rules.decide_exit` L253-255).
   6. Remove the `px >= 0.03` floor, because the bot has none. Count sales under $0.03 as information.
   7. `opt_fees` calls `costs.fees(side, px, qty/100, cfg)`. `R` becomes `cfg["r"]`. `run()`/`simulate()` take `cfg`,
      loaded with `config.load_config("config/default.json")`.
   8. Missing data (RI-002). A module dict `REALTEST_MISSING` holds one row per input, kept local so `ccbot/missing.py`
      is untouched:
      - `_read(path)` returns `None` when the file is absent, and an empty frame when the file is 0 bytes or has no
        columns (EmptyDataError: the KGC case).
      - prices or options absent → skip, with reason "not supplied".
      - dividends or splits absent → skip ("DIVIDEND_UNKNOWN: not supplied" / "splits: not supplied"). Present with
        0 rows → none.
      - a NaN dividend amount → skip, with reason (fail closed).
      - quote rows with non-finite or non-positive `iv`, or non-finite `delta` → dropped, with the count in
        `td.warnings`.
      - `last_iv or open_t.iv` → `last_iv`. It is always set from a finite IV at open, so assert that.
      - volhist absent or empty → `atm_iv_minus_next30d_rv` = NaN plus `atm_na_reason`.
      - `premium_yield_per_yr`: NaN if years ≤ 0, replacing `max(years, 1e-9)`.
      - `monte_carlo`: joint `dropna` on cc+bh instead of `fillna(0)`. Report `paths_used`. Fewer than 2 eligible
        columns → `{"na": reason}`.
      - `walk_forward`: a block whose scores are all -inf records `picked: None, reason: "no training data"`, instead
        of silently taking `configs[0]`.
      - `bxm_vs_spy`: an `error` reason when SPY is not requested or fails to load.
      - `run`: narrow `except Exception` to data errors (FileNotFoundError, ValueError, KeyError), so a code bug can't
        show up as "skipped".
   9. Counts in `summarize` and `summary.json`: per-ticker reject codes, plus `in_window` and `slack` sales (add
      `in_window` to `Trade`). Also `snap_days`, `snap_days_no_close`, `quote_rows_dropped`, `lot_cost_first`/`_last`
      (100 × close) and `fits_3k`, meaning `price × 100 ≤ min(cash − buffer, 0.5 × cash)` at the default config.
   10. Walk-forward out-of-sample returns come from `pct_change` on the full curve, sliced afterwards, so each block
       keeps its first day.
2. `tests/test_realtest.py` (change): tests below. Keep the `_make` fixture style. Everything is offline; the
   real-data tests read only committed `data/real/`.
3. `work/061/01-research.md` (change): a dated revision 2026-11-14 (I2) with re-run numbers next to the old ones and
   the A1-A6 table re-scored. pass-criteria.md is unchanged. Limitations to add: earnings dates treated as known in
   advance (APPROXIMATE); 100-share lots not modelled, with the `fits_3k` list; re-entry after assignment happens the
   same day (the bot uses ASSIGNED_TODAY and buys at the next close); grid-only rules (14-24 window, ±0.075 off-target
   tolerance, roll at Δ > 0.70) are not bot rules. Remove "cost-basis floor not modelled".
4. `reports/real/` (regenerated by `python -m ccbot.realtest`).

## Tests and checks
| Test | Pins |
|---|---|
| `test_pick_thursday_monthly_2022_04_14` | today 2022-03-14, quotes 04-14 + 05-20, no 04-15 close → 04-14 (31 DTE); old `_is_monthly` → None |
| `test_pick_unquoted_bot_expiry_is_no_expiry` | calendar monthly not in quotes → `NO_EXPIRY`, not another expiry |
| `test_pick_uses_the_bots_pickers` (keep, adapt signature) | first monthly in 30-45; Δ 0.36 → `NO_STRIKE_IN_TOLERANCE` |
| `test_basis_floor[below,above_band_fail,at_or_above]` | moves to the first strike ≥ basis; `BASIS_ABOVE_BAND` when its Δ < 0.20; unchanged otherwise |
| `test_earnings_today_blocks` / `test_stock_without_earnings_sells_nothing` / `test_etf_without_earnings_sells` | `a <= e`; `EARNINGS_UNKNOWN` count > 0 and 0 trades; SPY trades |
| `test_take50_only_in_first_third` | ask ≤ 50% on day ≤ life/3 → bought_back; later → hold |
| `test_fees_match_costs_fees` | `opt_fees(px,100,True) == costs.fees("sell",px,1,cfg)["total"]` |
| `test_drop_input[prices,options,dividends,splits,earnings,volhist,bxm]` | each absent file → its `REALTEST_MISSING` code or reason, never a number |
| `test_realtest_missing_lists_every_input` | every `root / "<kind>"` in `load_ticker`/`bxm_vs_spy` source has a `REALTEST_MISSING` row and a `test_drop_input` case |
| `test_nan_iv_rows_dropped_and_counted`, `test_nan_dividend_amount_skips` | count in warnings; skip reason |
| `test_monte_carlo_no_fill`, `test_monte_carlo_too_few_names_na` | bh has no NaN after alignment; `{"na": ...}` |
| `test_walk_forward_empty_training_block_not_picked` | `picked` None with reason |
| `test_premium_yield_na_zero_years` | NaN |
| `test_simulate_no_lookahead_and_accounting`, `test_run_end_to_end` (keep) | still pass with `cfg` passed |
| Feasibility on committed data (below) | exact counts I2 measures, pinned with `==` |
Checks: `pytest -q` (full suite, offline); `python3.11 -m py_compile ccbot/realtest.py` (RI-008);
`git diff --stat` shows no bot or config file (`ccbot/{bot,rules,screen,costs,expiries,pricing,missing}.py`, `config/`).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map: "No bot or config change; rule ideas wait for the person" | Kept: no bot/config file changed; `git diff --stat` check |
| Missing inputs: option quotes absent → skipped | 1.8 `_read` None/empty; `test_drop_input[options]` |
| Missing inputs: BXM_History.csv absent → error | Kept; `test_drop_input[bxm]` |
| Missing inputs: volhist absent → "column absent" | Changed to NaN + `atm_na_reason` (1.8); `test_drop_input[volhist]`. Supersedes 03's row (I2 notes it in 05) |
| realtest: 30-45 DTE monthly, 7-day slack (bot) | 1.1 via `third_fridays` + `pick_expiry`; feasibility test |
| realtest: 14-24 DTE grid window | 1.1 labelled grid-only; feasibility test |
| realtest: Δ tolerance [0.20, 0.35] / ±0.075 | 1.3 from cfg / labelled; feasibility test |
| realtest: no call through earnings | 1.4; earnings tests |
| realtest: min 3 years of quotes, start 2020-01-01 | Kept; feasibility test |
| realtest: premium ≥ $0.03 | DROPPED: not a bot rule (rules.py has none); count reported (1.6) |
| realtest: take50 / roll Δ > 0.70 | take50 aligned to the bot (1.5); roll labelled grid-only |
| Bot: cost-basis floor | Built (1.2) |
| Bot: EARNINGS_UNKNOWN / DIVIDEND_UNKNOWN | Built (1.4, 1.8) |
| Bot: 100-share lots, ASSIGNED_TODAY re-entry | Labelled limitations in 01 (3) + `fits_3k` column (1.9): lots would change the question from per-share edge to account cash drag |
| fetch_real_data.sql retries on `"deadline exceeded"` substring (RI-012 shape) | DROPPED: a missed match raises loudly (ticker in `failed`, exit 1), the data is already committed, and nothing trades on it |
| Person-followed rules (001 slack, tolerance, cap) | Unchanged; the code reads them from config, so no rule text update needed |

## Guardrail tests
Dated counts available now (committed reports from the post-b4ce90e run, data fetched 2026-11-13, period
2020-01-06 to 2026-11-12):
- Feasibility: bot rule (30-45 + 7 d slack, Δ [0.20, 0.35], skip earnings) → 942 calls over 17 tickers, 51-62 each
  (03 fact check; BAC 55, HBAN 53). Slack is used: BAC's 2020-01-06 sale is at 46 DTE and its 2020-02-21 sale at 28
  DTE (trades_BAC.csv). → `test_real_counts_bac`: load `data/real` BAC with cfg and BOT_RULE from 2020-01-01. Assert
  `calls_sold`, `in_window`, `slack` and each reject-code count `==` the values I2 measures after the build, all > 0
  except the info counts.
- Feasibility: 14-24 window → d0.150 noE hold: 67 (HBAN) to 152 (BAC) calls per ticker (grid_in_sample.csv) →
  `test_real_counts_bac` second case, Config(0.15, (14, 24)).
- Feasibility: ±0.075 off-target tolerance → d0.150 rows above are > 0. I2 also pins d0.450 for BAC.
- Feasibility: min 3 years → 17 of 21 kept; ITUB, PBR, VALE quoted only 2020-01-06 to 2020-12-02; KGC has no quotes
  (summary.json) → `test_real_min_years_filter`: the skipped set == {ITUB, KGC, PBR, VALE}, using load only and no
  simulate.
- Feasibility: start 2020-01-01 → the first snapshot used is 2020-01-06 → asserted in `test_real_counts_bac`.
- Missing inputs: prices, options, dividends, splits, earnings, volhist, BXM → `test_drop_input[...]`; enumeration →
  `test_realtest_missing_lists_every_input`. Optional quote fields iv/delta → `test_nan_iv_rows_dropped_and_counted`.
  Dividend amount → `test_nan_dividend_amount_skips`.
If a real-data test takes more than 30 s, I2 marks it `@pytest.mark.slow`, and it still runs in the default suite.

## Expected result
- `pytest -q`: all existing tests pass plus about 20 new ones; offline; no file outside the 4 planned paths changes.
- Re-run numbers move because of: the April 2022 monthly, the basis floor, earnings-today and unknown blocks, the fee
  fix, and removing the $0.03 floor. The A1-A6 table is re-scored in 01 with old and new values side by side, and
  pass-criteria.md is unchanged. The plan does not predict the verdict. If it flips, 01 says so, and the person
  decides before any bot change.
- `summary.json` has reject-code counts, `paths_used`, `fits_3k` and n/a reasons. No silent default is left: each
  RI-002 point above either blocks or shows n/a.
