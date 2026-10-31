# 06 Verification - 002
Verdict: FAIL

Prepared by I3 on 2026-10-30. Input: `work/002/request.md`, `01`–`05`, `logs/recurring-issues.md` (no entries), `git status`/`git diff`, and every file under `ccbot/`, `tests/`, `config/`, `scripts/`. Research, not financial advice. Nothing connected to a brokerage and no order was placed. I did not change any code.

**One blocking defect: a look-ahead bias in the realised-vol input (section "Sent back", item 1).** Everything else checks out, including every safety rule. The fix is small. After the fix, only the RV path and its test need re-checking.

## I1 audit (plan vs research)

Mostly faithful to R3's hand-off. All nine "changes from the 03 map" are listed with reasons, and none weakens a safety rule. Checked one by one:

| 04 item | vs 03 | Result |
|---|---|---|
| Change 1 `ccbot/`, single CLI | 03 step 14 CLI name | OK, naming only |
| Change 2 calibration deferred | 03 step 15 | OK. Stated, and the snapshot log is still written |
| Change 3 tolerance [0.20, 0.35] | new rule | OK. Sourced by the BS delta-per-strike arithmetic (research 1). `in_band` is still logged |
| Change 4 BASIS_ABOVE_BAND | 001 step 5/9b | OK |
| Change 5 SYNTH_A etf + SYNTH_B stock | 03 step 5 | OK, needed for the shipped-config guardrail test |
| Change 6 stdlib RNG | 03 step 5 | OK |
| Change 7 `state/` instead of `logs/paper/` | 03 step 14 | OK |
| Change 8 SDK guard order | 03 step 13 | OK. I re-read the SDK 3.0.4 wheel: `TradeClient.__init__` calls `ClientInitializer.initializer` (network), and the logger flags work as described |
| Change 9 WF selection basis | 03 step 9 | OK, an approximation the report states |
| Calendar note (±7-day slack, scan only) | not in 03 | Addition with a reason (the 2026-10-30 gap is real) |

**Errors in the plan:**
1. **The look-ahead originates here.** 04 `data.py` row says: "first `rv_window` rows: forward-fill the first valid value". 03 step 4 only said "trailing realized vol". Filling rows 0..19 with the first valid value (row 20) is a **backfill from the future**. See defect 1.
2. The plan repeats 03 step 6's "30–45 DTE is always found for monthly (gap ≤ 35 days)". That is false. The window is 16 days wide and monthlies are 28 or 35 days apart, so strict coverage is about 53%. I2 caught it (deviation 2).
3. The plan says "Weekly picks 5–9 DTE on every Monday". That is false: Monday to Friday is 4 DTE and the next Friday is 11. I2 caught it (deviation 3).

Errors 2 and 3 are arithmetic mistakes, and I2 handled both openly. They don't block.

## I2 audit (build vs plan)

`git status`: 2 tracked files modified. `README.md` (+39 lines, the ccbot section) and `logs/research/2026-10-30.md` (R-team lines, which predate I2). Everything else is untracked and new: `ccbot/` (19 modules), `tests/` (13 + conftest + helpers), `config/default.json`, `data/sample/` (6), `scripts/make_synthetic.py`, `reports/backtest_SYNTH_A_2026-10-30.{md,csv}`, `pyproject.toml`, `.gitignore`, `.env.example`. Ignored: only caches. No `state/`, `conf/`, `.env` or `*.log` exists or is tracked.

I compared each module with its row in 04's file table and found it matches, apart from the deviations listed in 05. Those deviations are judged below.

### Safety: live trading is impossible (read in the code AND tried)
| Rule | Code | Tried |
|---|---|---|
| No SDK import at module load | `webull_sandbox.py` uses only `importlib.import_module` inside `load_sdk()`. `broker/__init__.py` imports the adapter lazily. A grep for `import webull` / `from webull` in `ccbot/` finds nothing | With the real SDK on `PYTHONPATH`, importing every ccbot module (`__main__`, `bot`, `broker`, `webull_sandbox`, `backtest`, `screen`) leaves `[]` webull modules in `sys.modules` |
| Sandbox host forced before any client | L105–116: `ApiClient` → logger flags → token dir → `add_endpoint("us", SANDBOX_HOST)` + `quotes-api` → `_assert_sandbox()` → only then `TradeClient`/`DataClient`. `_assert_sandbox` also runs before every call (`_call`, `advance`) | **I tested against the real SDK 3.0.4** (installed `--no-deps` into the scratchpad, network blocked): (1) normal path: the TradeClient saw `api.sandbox.webull.com`; (2) with `add_endpoint` sabotaged, the resolver gives `api.webull.com` → `LiveTradingDisabled: endpoint 'api' resolves to 'api.webull.com', not the sandbox`, with **0 clients built and 0 network attempts**. No `webull_*_sdk.log` was written to the CWD |
| The SDK resolves the way the guard assumes | I read the SDK: `ApiClient._resolve_endpoint` uses `ResolveEndpointRequest(self._region_id)` (api_type `"api"`). `UserCustomizedEndpointResolver` is checked first in the chain. `request.endpoint` is only set from that resolution. The SDK has no hard-coded hosts outside `endpoints.json` | – |
| dry-run is the default | `dry_run=True` in the signature. The CLI never passes `dry_run`, so `place_option` cannot be reached from the CLI | `inspect` → `dry_run default: True` |
| `--live` exits 3 | `cmd_scan` raises `LiveTradingDisabled` before loading config or broker. `live=True` in the adapter raises | Run, output below. Exit 3 for sim, for webull-sandbox, and for webull-sandbox with valid-looking env |
| `WEBULL_ENV != sandbox` refused | L96 | Exit 3 with it unset and with `production` |
| Production hosts only in `_DENY` | grep: `ccbot/` only L24. Tests only in the fake resolver and the safety test's list | – |
| `place_option` once | grep: `webull_sandbox.py:215` only, behind `dry_run` false + sandbox assert | – |
| Credentials | Read from env only. The error names the variables, not their values. `.env.example` values are empty | – |

### Look-ahead and off-by-one review of the backtest
- **`data.realized_vol` L51–55: LOOK-AHEAD (defect 1).** `rv.fillna(rv[first])` gives rows 0..`rv_window`−1 the vol computed from returns of rows 1..`rv_window`, which are future closes. This happens on every user CSV without an `iv` column, which is the README's main "use your own data" path. I reproduced it on an 80-row CSV where days 1–20 are volatile and later days are calm. The day-0 vol is 0.376, equal to the day-20 RV, and the backtest's first trade (2026-01-05 SELL_CALL K=26 @ 0.57) is priced with it. No test covers this: every backtest test uses `helpers.write_path`, which always writes an `iv` column.
- `build_days`: `prev_close` is from the prior row. `q` is a trailing 252-day sum. The vol percentile is trailing and includes today, which is known at the close. `div_next` (tomorrow's dividend, for the ex-div check) and `next_earnings`/`ex_div_date` use scheduled dates that are announced in advance. All acceptable and as 001 F3/ORATS intend.
- Settlement runs at the top of the day, before any decision, so a position closed today is settled before re-entry, and `ASSIGNED_TODAY` delays the re-buy to the next close. A dividend is credited only to shares held at the ex-date settle, and shares bought at that day's close don't get it. On an ITM expiry that falls on an ex-date, the dividend is credited before the assignment. All correct.
- `pick_expiry`: `bisect_right` excludes today's expiry (no 0DTE). DTE is in calendar days and inclusive at both ends. Slack candidates are limited to [lo−slack, hi+slack], and ties go to the later expiry. At expiry T = 0 gives intrinsic value, and the option is settled before equity is marked. `third_fridays` handles a month starting on a Friday (gives the 15th). No off-by-one found.
- Walk-forward: `folds` asserts that train, test and held-out years never overlap. `chosen_h` is selected only on non-held years, and the held-out years are dropped from the PBO matrix. Yearly returns cut from the full run depend only on the past (the run is causal). No leak found.

### Deviations (05 §Deviations)
| # | Verdict | Why |
|---|---|---|
| 1 k scales the `iv` column | **Justified** | 03 B10 says the skew risk "is handled as a sensitivity sweep on k". Without this the 03-mandated k sweep does nothing on SYNTH_A. `scaled()` divides by the old k first, so k is never applied twice, and `test_data` checks this. The percentile is scale-invariant, so V4 is unaffected. **Doc gap:** README says "Without an `iv` column the vol input is 20-day realised vol × k", which suggests k doesn't touch `iv`. The report line doesn't say it either. Fix the wording (item 2) |
| 2 ±7-day slack in the backtest too | **Justified, documented** | Strict 30–45 has a monthly on <70% of days (test). One shared rule keeps the bot/backtest parity test honest. The report states it, and every trade logs `in_window` |
| 3 Weekly Mon/Tue → NO_EXPIRY | **Justified** | The calendar arithmetic is correct, and the test asserts it exactly |
| 4 V2 fills bound 3–5× → 1.5–5× | **Justified, but post-hoc** | I re-ran V2 vs V0: 129 vs 69 fills (1.87×). Days by reason: NO_EXPIRY 680 (Mon/Tue), BASIS_ABOVE_BAND 750, NO_STRIKE_IN_TOLERANCE 142, INSUFFICIENT_CASH 175. The causes I2 gives are real. 03's "≈4×" was an expectation, not a rule (04: "not a target"). The bound was loosened after seeing the result, so Audit should know it now only checks "clearly more than V0" |
| 5–13 | OK | Interface changes keep the logic shared. Added codes are in the closed lists. Known limits are stated in 05 and in the report |

I also checked the V0 trade log on SYNTH_A. Re-buying 100 shares at up to $185 on a $3k start is consistent: equity grows with the stock, and when the gap exceeds the cash the strategy waits (`INSUFFICIENT_CASH` 39 days). Not a defect.

### Connectivity check (re-done)
- Every `def`/`class` in `ccbot/` is referenced inside `ccbot/` (only `__post_init__` is not, which is a dunder). `pyflakes ccbot tests scripts` is clean.
- All 13 reason codes appear in producer code outside the `REASONS` tuple. `test_every_reason_code_is_produced` passes.
- There are no TODO/FIXME/XXX in `ccbot tests scripts config README.md`.
- Inputs and outputs are wired as 05 says. I confirmed the scan → `paper_trades.csv` → idempotency check by running it (3 lines after 2 runs).

## Tests re-run (output)
```
$ python -m pytest -q
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 12.84s
$ python -m pytest --co -q | tail -1
87 tests collected in 0.35s
```
```
$ python -m ccbot make-sample --out <scratch>/sample      (then sha256 vs data/sample/*)
SAMPLES_IDENTICAL
$ time python -m ccbot backtest --asof 2026-10-30 --out <scratch>/reports
96 configs in 17.4 s -> .../backtest_SYNTH_A_2026-10-30.md, .../backtest_SYNTH_A_2026-10-30.csv
real	0m17.944s
$ diff <scratch>/reports/backtest_SYNTH_A_2026-10-30.md reports/...md   -> MD_IDENTICAL
$ diff <scratch>/reports/backtest_SYNTH_A_2026-10-30.csv reports/...csv -> CSV_IDENTICAL
```
CLI (all with `--state-dir`/`--out` in the scratchpad):
```
$ python -m ccbot scan --date 2026-10-30
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED
exit 0
$ python -m ccbot scan --date 2026-10-30            (2nd run)
already scanned 2026-10-30 for V0: no new orders; reports re-rendered
exit 0
$ wc -l state/paper_trades.csv state/paper_snapshots.csv
    3 paper_trades.csv
  128 paper_snapshots.csv
$ python -m ccbot report --date 2026-10-30 --weekly   -> daily_2026-10-30.md, weekly_2026-10-30.md; exit 0
$ python -m ccbot scan --date 2026-10-30 --live
refused: Live trading is not built.
exit 3
$ python -m ccbot scan --date 2026-10-30 --broker webull-sandbox             (WEBULL_ENV unset)
refused: WEBULL_ENV must be 'sandbox'; no other environment is supported.
exit 3
$ WEBULL_ENV=production WEBULL_APP_KEY=x WEBULL_APP_SECRET=y python -m ccbot scan ... --broker webull-sandbox
refused: WEBULL_ENV must be 'sandbox'; no other environment is supported.
exit 3
$ WEBULL_ENV=sandbox WEBULL_APP_KEY=x WEBULL_APP_SECRET=y python -m ccbot scan ... --broker webull-sandbox --live
refused: Live trading is not built.
exit 3
$ WEBULL_ENV=sandbox WEBULL_APP_KEY=x WEBULL_APP_SECRET=y python -m ccbot scan --date 2026-10-31 --broker webull-sandbox
error: Webull SDK not installed: pip install ccbot[webull] (webull-openapi-python-sdk==3.0.4)
exit 2
$ python -m ccbot scan --date 2026-11-02
error: cannot settle the paper ledger: no snapshot for SYNTH_A on 2026-11-02
exit 2
$ python -m ccbot backtest --data /nonexistent.csv --quick
error: cannot read /nonexistent.csv: [Errno 2] No such file or directory: '/nonexistent.csv'
exit 2
$ python -m ccbot scan --date 2026-10-29             (earlier than ledger)
error: ledger is at 2026-10-30; cannot go back to 2026-10-29
exit 2
```
Real-SDK guard check (SDK 3.0.4 in the scratchpad, sockets and DNS blocked):
```
1) built: [('TradeClient', 'api.sandbox.webull.com')] | then: RuntimeError dns blocked: 127.0.0.1
2) LiveTradingDisabled: endpoint 'api' resolves to 'api.webull.com', not the sandbox | clients built: [] | network: []
3) refused: {'live': True} -> Live trading is not built.
3) refused: production -> WEBULL_ENV must be 'sandbox'; no other environment is supported.
dry_run default: True
```
Look-ahead reproduction (80-row CSV, no `iv` column; days 1–20 volatile, then calm):
```
vol day0 = 0.376  vol day20 = 0.376  (day20 RV uses returns of days 1..20)
         date      action  strike  price        mid
0  2026-01-05  BUY_SHARES     NaN  24.00  24.000000
1  2026-01-05   SELL_CALL    26.0   0.57   0.595914
```

## Sent back / sent to Audit
**Sent back. Not sent to Audit.**

1. **BLOCKING: look-ahead bias in `ccbot/data.py::realized_vol` (I1 plan wording + I2 code). Goes back to I1 to correct the rule and to I2 to fix.** `rv.fillna(rv[first])` backfills the first `rv_window` rows with a vol built from future closes. So on any user CSV without `iv`, the first call (and any decision in the first ~20 rows) is priced with future data. Required:
   - (a) Never use a vol that depends on closes after the decision day. For example, leave those rows NaN and have `decide_entry` return a no-trade (a new closed-list reason such as `NO_VOL_HISTORY`, or reuse an existing code with the rule documented). An expanding window from ≥ 2 returns would also work, as long as it uses past data only.
   - (b) Add a test: for a CSV without `iv`, `vol[i]` changes when only closes after `i` are changed, for no `i`. Also a backtest test on such a CSV showing no option is sold before a valid trailing vol exists.
   - (c) Fix the 04 wording ("forward-fill the first valid value").
2. **Non-blocking, fix in the same pass (I2):** README "Use your own data" and the report's "Volatility multiplier k" line should say that k multiplies the `iv` column too, when there is one (deviation 1).
3. **Notes for later (no change required now):**
   - `buy_and_hold` uses `max(1, …)` lots, so it goes cash-negative if 100 shares cost more than the cash. The strategy waits in that case, so the benchmark is mismatched only on such inputs.
   - The Webull OCC-symbol fallback (`fridays(business_days(exp, exp))`) returns nothing for a holiday-moved Thursday expiry.
   - The V2 fills test is now a weak bound (see deviation 4).

On re-submission, I3 re-checks item 1 and its tests, item 2, and runs the full suite again.

## Re-verification - 2026-10-30 (after I1/I2 revision)
Verdict: **FAIL** (1 new blocking item; every item from the first FAIL is fixed)

Prepared by I3. Input: 04 and 05 "Revision (after I3 FAIL)", the changed files, a grep of all of `ccbot/`, and runs made in the scratchpad. No code changed and nothing committed. Nothing connected to a brokerage.

### Item 1 (look-ahead): FIXED, complete
- `data.realized_vol` is now `rets.rolling(window).std() * sqrt(252)`, with no fill. `vol[t]` uses closes t−20..t, and rows 0..19 are NaN. `grep -c fillna ccbot/data.py` → 0. The rule matches the 04 revision word for word. `build_days` sets `vol_warmup = isnan(vol)`, and `_option_entry` returns `VOL_WARMUP` before any pricing.
- **Whole-package grep** for `fillna|bfill|ffill|backfill|shift(-|center=|expanding|interpolate|method=|[i+1]|iloc[-1]` and for whole-series `.max()/.min()/.mean()` in `ccbot/`. Each hit, reviewed:
  - `backtest.py:42` V4 percentile, `rolling(252)` trailing. A window with a NaN gives NaN, which maps to `IV_FILTER`.
  - `backtest.py:41` dividend yield, trailing `rolling(252, min_periods=1)`.
  - `backtest.py:50` `div[i+1]` is tomorrow's dividend. `_next_date` gives the next earnings/ex-div date. Both are scheduled, pre-announced dates that the ex-div and earnings checks need (accepted in the first pass).
  - `backtest.py:135` max drawdown over the finished equity curve. Reporting only.
  - `sim.py:59` `older.iloc[-1]` is the latest snapshot *before* today. `rows["iv"].median()` uses today's rows only.
  - `walkforward.py` `shift(1)` is backward, and fold years are disjoint (asserted). `webull_sandbox.py` `next_at` is the rate limiter.
  - **No other future-data use found.**

### Item 1b: the guardrail catches the original bug (shown)
I copied `ccbot tests config data scripts pyproject.toml` to a scratch directory and, in the copy only, put the old backfill back (`rv.fillna(rv[rv.first_valid_index()])`). Then I ran the full suite there:
```
FAILED tests/test_backtest.py::test_no_option_sold_during_vol_warmup - Assert...
FAILED tests/test_data.py::test_realized_vol_of_constant_return_is_zero - ass...
FAILED tests/test_data.py::test_realized_vol_uses_only_past_closes - assert F...
3 failed, 86 passed in 12.64s
```
The copy was deleted (`rm -rf`) and the repo file was untouched (`fillna` count 0). The guardrail test is sound. It uses a no-`iv` CSV (asserted), so it exercises the path that had no coverage before. It perturbs every t, and it also asserts that the edit does change a later vol, so it can't pass vacuously.

### Item 1c: V2 fills test: principled
The fitted 1.5× lower bound is gone. The test now asserts what follows from the rules: V0 < V2 < 5×V0 (5× is the plan's ceiling), weekly expiries are unique, DTE is in 5–9, and sales fall only on Wed–Fri. A comment explains why there is no ratio band. The Wed–Fri and uniqueness checks would fail on a real rule break, which the old ratio band would not catch. Accepted.

### Item 2: README / report wording: FIXED
README L80: "The vol input is the `iv` column × k when there is one; without it, it is the trailing 20-day realised vol × k, built only from closes up to that day. k scales both. … the first 20 rows have no vol yet … (reason `VOL_WARMUP`)." The report line now says the same. `rv_window` is 20 in `config/default.json`, so "20" is right.

### Tests and CLI re-run (real output)
```
$ python -m pytest -q
89 passed in 13.68s
$ python -m ccbot make-sample --out <scratch>/sample      -> exit 0; all 6 files byte-identical to data/sample/
$ time python -m ccbot backtest --asof 2026-10-30 --out <scratch>/reports
96 configs in 16.3 s -> ...   real 0m16.855s   exit 0
md IDENTICAL / csv IDENTICAL  (vs reports/backtest_SYNTH_A_2026-10-30.*; headline numbers unchanged, as 05 says)
$ python -m ccbot scan --date 2026-10-30 --state-dir <s> --out <o>
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED
exit 0
$ (same again)  -> already scanned 2026-10-30 for V0: no new orders; reports re-rendered   exit 0
$ python -m ccbot report --date 2026-10-30 --weekly ...   -> daily_2026-10-30.md, weekly_2026-10-30.md   exit 0
$ python -m ccbot scan --date 2026-10-30 --live            -> refused: Live trading is not built.   exit 3
$ python -m ccbot scan ... --broker webull-sandbox (WEBULL_ENV unset)  -> refused: WEBULL_ENV must be 'sandbox'; ...  exit 3
$ WEBULL_ENV=production ... --broker webull-sandbox        -> same refusal   exit 3
$ python -m ccbot backtest --data /nonexistent.csv --quick -> error: cannot read /nonexistent.csv ...   exit 2
```

### NEW blocking item: the "Mean of empty slice" warning hides a wrong result
1-year, no-`iv` CSV (250 business days in 2025), `backtest --quick`, exit 0:
```
walkforward.py:98: RuntimeWarning: Mean of empty slice
walkforward.py:99: RuntimeWarning: Mean of empty slice
...
## Overfitting check
- PBO (CSCV, S=8, monthly returns, held-out years excluded) across 8 configs: 0.000
```
Cause: `holdout_years: 2` holds out every year of a 1–2-year CSV, so the PBO matrix has 0 rows. `pbo_cscv` cuts `T − T%S` rows into S=8 blocks. With **T < 8 months** every block is empty, the means are NaN, `rank()` gives NaN, `math.log(nan)` is NaN, and `np.mean(nan <= 0)` is **0.0**. Reproduced directly: `pbo_cscv(empty 0×8) = 0.0`, `pbo_cscv(7×8 noise) = 0.0` (12×8 noise = 0.64). **0.000 is the best possible PBO.** So on any user CSV with fewer than 8 non-held months (under about 2 years 8 months of data, which is the README's "use your own data" path), the report prints "no overfitting" when PBO cannot be computed at all. The stitched-OOS table already shows `n/a` correctly, but PBO doesn't. Minor, same root cause: the held-out "Config" for V4 shows `V4 θ50`, which was "selected" on zero training years (ties go to the first config) and is not labelled as such.

### Sent back / sent to Audit
**Sent back to I1 (rule) → I2 (fix). Not sent to Audit. 07 not written.**
1. **BLOCKING:** `pbo_cscv` must return NaN (not 0.0) when T < S, or when any block is empty. The report must print `PBO: n/a (needs ≥ 8 non-held-out months; have T)`, and the warnings must not appear. Guardrail test: `pbo_cscv` on 0×N and 7×N matrices returns NaN, and a 1-year `--quick` report contains "n/a" for PBO and no `0.000`. Also label a held-out config selected on zero train years as "not selected (no train years)".
2. On re-submission I3 re-checks only this item, plus the full suite and CLI. Items 1, 1b, 1c and 2 above stand.

**Carry into 07-audit-task.md on PASS** (recorded here so they are not lost):
- 001 error found by R3 (03 §Error, L114): "ETF ≤ $28" at $3k gives an empty universe. A1 should open it as a BUG, with its guardrail (`UNIVERSE EMPTY` banner + shipped-config ≥ 1 passing ticker test).
- The look-ahead bug (RV backfill, from the 04 plan wording) and its fix + guardrail, for `logs/recurring-issues.md`.
- This PBO/numpy-warning issue and its fix.
- First-pass notes: `buy_and_hold` `max(1, …)` lot mismatch, the holiday-Thursday OCC fallback, and V2 test history.

## Re-verification 2 - 2026-10-30 (after Revision 2)
Verdict: **PASS**

Prepared by I3, round 3. Input: 04 and 05 "Revision 2", `ccbot/walkforward.py`, `ccbot/report.py`, `tests/test_walkforward.py`, `tests/test_cli.py`. No code changed, nothing committed, nothing connected to a brokerage.

### The fix is correct
- `pbo_cscv` returns NaN **before** any mean is taken when `T < S`, `N < 2`, or R has a non-finite value. The warning is avoided, not filtered. With T ≥ 8 every CSCV block has at least one row, so the guard is exactly the right boundary.
- `walk_forward` returns `pbo_months`. If there are no non-held-out years, `chosen_h = None`, so the held-out config prints "not selected (no train years)" and CAGR/excess print n/a. Before, the tie-break gave `V4 θ50`.
- The report prints the n/a and its reason. It shows a number only when PBO is finite.
- Boundary runs (`-W error::RuntimeWarning`, no-`iv` CSVs, `--quick`; every run exited 0 with no warning):
```
ONEYEAR (2025 only)        PBO: n/a (needs >= 8 non-held-out months and >= 2 configs; have 0 months)
                           held-out: V0..V5 "not selected (no train years)" | n/a | -25.02% | n/a
SEVENM (Jun 2023-2025)     PBO: n/a (... have 7 months)
EIGHTM (May 2023-2025)     PBO: 0.086
SYNTH_A (full)             PBO: 0.357  (unchanged)
```
- I2's grep for places that turn NaN or missing data into a number is confirmed. `grep -E "fillna|nan_to_num|or 0\b" ccbot/` finds nothing. I agree with I2's review of `compound([])`/`annualise(…, 0)` (NaN) and of the true-zero counters.

### The new tests catch the bug (shown)
In a scratch copy only (its `ccbot.__file__` is in the scratchpad), I reverted all three Revision 2 guards in `walkforward.py`: the `pbo_cscv` guard became `if False:`, and `if pre else None` and `if chosen_h else nan` were removed. Full suite there:
```
FAILED tests/test_cli.py::test_short_csv_reports_pbo_na_without_warnings - Ru...
FAILED tests/test_walkforward.py::test_pbo_undefined_on_too_few_months[0] - A...
FAILED tests/test_walkforward.py::test_pbo_undefined_on_too_few_months[1] - A...
FAILED tests/test_walkforward.py::test_pbo_undefined_on_too_few_months[7] - A...
4 failed, 89 passed, 9 warnings in 14.05s
```
The copy was deleted. In the repo, `grep -c "if T < S" ccbot/walkforward.py` → 1.

### No regressions (real output)
```
$ python -m pytest -q                       -> 93 passed in 14.29s
$ python -m ccbot make-sample --out <s>     -> exit 0; all 6 files byte-identical to data/sample/
$ time python -m ccbot backtest --asof 2026-10-30 --out <s>
96 configs in 17.6 s ...  real 0m18.082s  exit 0
md IDENTICAL, csv IDENTICAL vs reports/backtest_SYNTH_A_2026-10-30.*
$ python -m ccbot scan --date 2026-10-30 --state-dir <s> --out <o>
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED      exit 0
$ (again)  -> already scanned 2026-10-30 for V0: no new orders; reports re-rendered   exit 0
$ python -m ccbot report --date 2026-10-30 --weekly ...  -> daily_ + weekly_2026-10-30.md   exit 0
$ python -m ccbot scan --date 2026-10-30 --live          -> refused: Live trading is not built.   exit 3
$ ... --broker webull-sandbox (WEBULL_ENV unset)         -> refused: WEBULL_ENV must be 'sandbox'; ...   exit 3
$ WEBULL_ENV=production ... --broker webull-sandbox      -> same refusal   exit 3
$ python -m ccbot backtest --data /nonexistent.csv --quick -> error: cannot read ...   exit 2
```
Items 1, 1b, 1c and 2 from "Re-verification" still hold. The look-ahead guardrail tests are still in the 93 and pass.

### Minor notes for Audit (non-blocking)
- The n/a reason always says "needs >= 8 months and >= 2 configs", even when the real cause is a non-finite value in R (T ≥ 8). Today that can't happen on validated data, but the message could name the actual cause.
- Fixed variants V0–V3 and V5 have only one config. With no train years they also show "not selected" and n/a, even though nothing needed selecting and a held-out CAGR could be reported. This is conservative, not wrong.

### Sent to Audit
**PASS. Sent to Audit:** `work/002/07-audit-task.md`.
