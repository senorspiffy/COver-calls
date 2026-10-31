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
    p.write_text("date,close\n" + "".join(f"{d},{24 + 0.3 * (-1) ** i:.2f}\n" for i, d in enumerate(days)))
    s = load_prices(p, rv_window=cfg["rv_window"])
    first_valid = days[cfg["rv_window"]]
    for vid in ("V0", "V5"):
        res = run_backtest(s, BY_ID[vid], cfg)
        sells = res.trades[res.trades["action"].isin(["SELL_CALL", "SELL_PUT"])]
        assert len(sells) and (sells["date"].map(str) >= str(first_valid)).all()
        assert res.reasons["VOL_WARMUP"] >= cfg["rv_window"] - 1   # day 0 buys shares, then waits
