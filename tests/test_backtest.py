import datetime as dt

import pytest

from helpers import bdays, write_path
from ccbot.backtest import buy_and_hold, run_backtest
from ccbot.data import load_prices
from ccbot.variants import BY_ID, REGISTRY

V0 = BY_ID["V0"]
START = dt.date(2026, 10, 19)
DAYS = bdays(START, 26)                 # 2026-10-19 .. 2026-11-23; monthly expiry 2026-11-20
EXPIRY = dt.date(2026, 11, 20)
EARN = {dt.date(2026, 11, 23): 1}       # blocks re-entry after expiry, so one cycle is measured


def _sale(res):
    t = res.trades
    return t[t["action"] == "SELL_CALL"].iloc[0]


def _pnl(res, cfg):
    return res.equity.iloc[-1] - cfg["cash"]


def test_flat_keeps_premium(tmp_path, cfg):
    res = run_backtest(write_path(tmp_path / "f.csv", [24] * 26, earnings=EARN), V0, cfg)
    assert res.reasons["EARNINGS_BLACKOUT"] > 0
    sale = _sale(res)
    assert sale["expiry"] == EXPIRY and len(res.trades[res.trades["action"] == "SELL_CALL"]) == 1
    assert "EXPIRED" in set(res.trades["action"])
    assert _pnl(res, cfg) == pytest.approx(sale["price"] * 100 - sale["fees"])
    assert sale["price"] == pytest.approx(round(sale["mid"] - 0.025, 2), abs=0.006)


def test_spike_is_capped_at_strike(tmp_path, cfg):
    closes = [24] * 10 + [30] * 16
    res = run_backtest(write_path(tmp_path / "s.csv", closes, earnings=EARN), V0, cfg)
    sale = _sale(res)
    assert "ASSIGNED" in set(res.trades["action"])
    assert _pnl(res, cfg) == pytest.approx((sale["strike"] - 24) * 100 + sale["price"] * 100 - sale["fees"])


def test_crash_matches_stock_loss_plus_premium(tmp_path, cfg):
    closes = [24] * 10 + [18] * 16
    res = run_backtest(write_path(tmp_path / "c.csv", closes, earnings=EARN), V0, cfg)
    sale = _sale(res)
    assert "EXPIRED" in set(res.trades["action"])
    assert _pnl(res, cfg) == pytest.approx((18 - 24) * 100 + sale["price"] * 100 - sale["fees"])


def test_ex_dividend_early_assignment(tmp_path, cfg):
    exdiv = dt.date(2026, 11, 13)
    closes = [24] * 10 + [30] * 16
    res = run_backtest(write_path(tmp_path / "d.csv", closes, dividends={exdiv: 0.50}, earnings=EARN), V0, cfg)
    early = res.trades[res.trades["action"] == "EARLY_ASSIGNED"]
    assert list(early["date"]) == [dt.date(2026, 11, 12)]
    assert "DIVIDEND" not in set(res.trades["action"])


def test_invariants_on_synth_a_every_variant(runs):
    # run_backtest raises AssertionError on any invariant breach (cash, lots, cover)
    assert set(runs) == {v.id for v in REGISTRY}
    for r in runs.values():
        assert len(r.equity) == 2520


def test_buy_and_hold_exact(synth_a, cfg):
    bh = buy_and_hold(synth_a, cfg)
    shares = 100
    divs = (synth_a.df["dividend"] * shares).sum()
    expected = shares * synth_a.df["close"].iloc[-1] + (cfg["cash"] - shares * 24.0) + divs
    assert bh.iloc[-1] == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize("vid", ["V0", "V2"])
def test_wider_spread_lowers_equity(synth_a, cfg, vid):
    def run(spread):
        c = {**cfg, "spread": {**cfg["spread"], "value": spread}}
        return run_backtest(synth_a, BY_ID[vid], c).equity.iloc[-1]
    assert run(0.01) > run(0.10)


def test_no_option_sold_during_vol_warmup(tmp_path, cfg):
    """No iv column: no option is sold before a past-only trailing vol exists."""
    days = bdays(dt.date(2026, 1, 5), 80)
    p = tmp_path / "noiv.csv"
    # dividend/earnings supplied as 0: an absent column would block every entry (005 policy)
    p.write_text("date,close,dividend,earnings\n" + "".join(f"{d},{24 + 0.3 * (-1) ** i:.2f},0,0\n"
                                                           for i, d in enumerate(days)))
    s = load_prices(p, rv_window=cfg["rv_window"])
    first_valid = days[cfg["rv_window"]]
    for vid in ("V0", "V5"):
        res = run_backtest(s, BY_ID[vid], cfg)
        sells = res.trades[res.trades["action"].isin(["SELL_CALL", "SELL_PUT"])]
        assert len(sells) and (sells["date"].map(str) >= str(first_valid)).all()
        assert res.reasons["VOL_WARMUP"] >= cfg["rv_window"] - 1   # day 0 buys shares, then waits


def _x15(series):
    """First 600 rows with closes x 1.5 (s0 = $36): 100 sh cost more than cash - buffer."""
    from dataclasses import replace
    s = replace(series, df=series.df.iloc[:600].copy(), vol=series.vol.iloc[:600])
    s.df["close"] *= 1.5
    return s


@pytest.mark.parametrize("case", ["feasible", "infeasible"])
def test_benchmark_cash_never_negative(synth_a, cfg, case):
    """RI-002 guardrail (006): B&H never borrows. If 100 shares do not fit, it is n/a (NaN)."""
    import warnings
    from ccbot.backtest import _bh_cash, bh_lots, bh_na_reason, metrics
    from ccbot.variants import run_grid
    s = synth_a if case == "feasible" else _x15(synth_a)
    assert (_bh_cash(s, cfg) >= 0).all() and (bh_lots(s, cfg) * 100) % 100 == 0
    bh = buy_and_hold(s, cfg)
    if case == "feasible":
        assert bh_lots(s, cfg) == 1 and bh_na_reason(s, cfg) is None and bh.notna().all()
        return
    assert bh_lots(s, cfg) == 0 and bh.isna().all() and len(bh) == len(s.df)
    assert bh_na_reason(s, cfg) == "100 shares cost more than cash − buffer"
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        m = metrics(bh, None, cfg)
        grid, _, _ = run_grid(s, cfg, quick=True)
    assert all(m[k] != m[k] for k in ("cagr", "vol", "max_dd", "final_equity"))   # NaN
    assert grid["excess_vs_bh"].isna().all()


def test_all_variants_pass_account_invariants_infeasible_bh(synth_a, cfg):
    # run_backtest runs _check (cash >= 0, 100-share lots, cover) every day
    s = _x15(synth_a)
    for v in REGISTRY:
        res = run_backtest(s, v, cfg)
        assert len(res.equity) == 600 and res.reasons.get("INSUFFICIENT_CASH", 0) > 0


def test_stock_csv_without_earnings_blocks_with_reason(tmp_path, cfg):
    """005: a stock CSV with no earnings column blocks every option entry (never 'no earnings')."""
    import shutil
    import pandas as pd
    from conftest import SAMPLE
    p = tmp_path / "SYNTH_B.csv"
    pd.read_csv(SAMPLE / "SYNTH_B.csv", dtype=str).drop(columns="earnings").to_csv(p, index=False)
    shutil.copy(SAMPLE / "SYNTH_B.meta.json", tmp_path / "SYNTH_B.meta.json")
    s = load_prices(p)
    assert s.meta["asset_type"] == "stock" and s.missing == ("earnings",)
    res = run_backtest(s, V0, cfg)
    assert res.reasons["EARNINGS_UNKNOWN"] > 0 and res.reasons.get("EARNINGS_BLACKOUT", 0) == 0
    assert not res.trades["action"].isin(["SELL_CALL", "SELL_PUT"]).any()
    assert run_backtest(load_prices(SAMPLE / "SYNTH_B.csv"), V0, cfg).reasons["EARNINGS_BLACKOUT"] > 0  # control


def test_worked_example_50pct_exit(cfg):
    """RI-004 guardrail (008): 001's worked example agrees with decide_exit. A call sold at $0.47
    with 35 days of life: the 50% limit is $0.23 (<= $0.235); the last allowed day is 11."""
    from ccbot.rules import Day, Market, Quote, Short, State, decide_exit
    sold, K = dt.date(2026, 11, 2), 26.0
    expiry = sold + dt.timedelta(days=35)

    class OneQuote(Market):
        def __init__(self, ask):
            super().__init__([expiry], [])
            self.ask = ask

        def chain(self, day, exp, kind):
            return [Quote("X", K, "C", round(self.ask - 0.02, 2), self.ask, self.ask - 0.01, 0.10)]

    def exit_on(day_n, ask):
        st = State(cash=600.0, ticker="X", shares=100, basis=24.0, option=Short("C", K, expiry, 1, 0.47, sold))
        return decide_exit(st, Day(sold + dt.timedelta(days=day_n), 24.0), BY_ID["V1"], cfg, OneQuote(ask))

    d = exit_on(9, 0.23)
    assert (d.action, d.reason, d.limit) == ("BUY_TO_CLOSE", "PROFIT_TARGET_HIT", 0.23)
    assert exit_on(9, 0.24).reason == "HAS_POSITION"
    assert exit_on(11, 0.23).action == "BUY_TO_CLOSE"
    assert exit_on(12, 0.23).reason == "HAS_POSITION"
    assert round((0.47 - 0.23) * 100 - 0.20, 2) == 23.80
