"""Item 024: up to max_positions underlyings share one cash balance."""
import datetime as dt

import pandas as pd
import pytest

from conftest import SAMPLE
from ccbot.bot import run_daily
from ccbot.broker.sim import SimBroker
from ccbot.config import ConfigError, load_config
from ccbot.data import load_snapshots
from ccbot.portfolio import Portfolio, entry_budget
from ccbot.report import weekly_report
from ccbot.rules import Short, State

DATE = dt.date(2026, 10, 30)


def _two_stocks(price=14.0):
    """SYNTH_B (stock) made to pass the screen, plus an identical copy named SYNTH_D."""
    df, meta = load_snapshots(SAMPLE / "SYNTH_SNAPSHOTS.csv")
    b = df[df["underlying"] == "SYNTH_B"].copy()
    b["ask"] = (b["bid"] + 0.05).round(2)
    scale = price / b["underlying_price"].iloc[0]
    b["underlying_price"] = price
    b["strike"] = (b["strike"] * scale).round(2)
    d = b.assign(underlying="SYNTH_D", symbol=b["symbol"].str.replace("SYNTH_B", "SYNTH_D"))
    return pd.concat([b, d], ignore_index=True), meta


def _run(tmp_path, cfg, df, meta, date=DATE):
    broker = SimBroker(cfg, snapshots=df, meta=meta, ledger_path=tmp_path / "state" / "sim_ledger.json")
    return run_daily(date, broker, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports"), broker


def _cfg(**over):
    return load_config(None, {"universe": ["SYNTH_B", "SYNTH_D"], **over})


def test_two_stocks_opened_within_caps(tmp_path):
    cfg = _cfg()
    df, meta = _two_stocks()
    scan, broker = _run(tmp_path, cfg, df, meta)
    acts = [(d["ticker"], d["action"], d["status"]) for d in scan["decisions"]]
    assert acts == [("SYNTH_B", "BUY_SHARES", "FILLED"), ("SYNTH_B", "SELL_CALL", "FILLED"),
                    ("SYNTH_D", "BUY_SHARES", "FILLED"), ("SYNTH_D", "SELL_CALL", "FILLED")]
    pf = broker.get_positions()
    assert pf.held() == ["SYNTH_B", "SYNTH_D"]
    for t in pf.held():   # each single stock <= 50% of starting capital
        assert pf.positions[t].shares * pf.positions[t].basis <= 0.5 * cfg["cash"]
    assert pf.cash >= cfg["cash_buffer"]
    report = (tmp_path / "reports" / f"daily_{DATE}.md").read_text(encoding="utf-8")
    assert "## Positions (up to 2 underlyings)" in report and "- SYNTH_D: shares 100" in report


def test_max_positions_one_opens_only_one(tmp_path):
    df, meta = _two_stocks()
    scan, broker = _run(tmp_path, _cfg(max_positions=1), df, meta)
    assert broker.get_positions().held() == ["SYNTH_B"]
    assert {d["ticker"] for d in scan["decisions"]} == {"SYNTH_B"}


def test_next_day_manages_held_and_opens_nothing_new(tmp_path):
    cfg = _cfg()
    df, meta = _two_stocks()
    _run(tmp_path, cfg, df, meta)
    nxt = dt.date(2026, 11, 2)
    scan, broker = _run(tmp_path, cfg, df.assign(ts=nxt), meta, nxt)
    assert [d["action"] for d in scan["decisions"]] == ["NONE", "NONE"]
    assert {d["reason"] for d in scan["decisions"]} == {"HAS_POSITION"} and broker.n_orders == 0


def test_cheap_stock_buys_only_up_to_half(tmp_path):
    """$5 stock: the old one-position rule bought floor(2800 / 500) = 5 lots ($2,500, 83%).
    Now a single stock gets at most 50% of capital: 3 lots = $1,500."""
    cfg = _cfg(max_positions=1)
    df, meta = _two_stocks(price=5.0)
    scan, broker = _run(tmp_path, cfg, df, meta)
    buy = next(d for d in scan["decisions"] if d["action"] == "BUY_SHARES")
    assert buy["status"] == "FILLED" and broker.get_positions().positions["SYNTH_B"].shares == 300


def test_entry_budget_rules(cfg):
    pf = Portfolio(cash=3000.0)
    assert entry_budget(pf, 3000, "etf", cfg) == 3000
    assert entry_budget(pf, 3000, "stock", cfg) == 1700      # 50% × 3000 + 200 buffer
    assert entry_budget(Portfolio(cash=900.0), 3000, "stock", cfg) == 900


def test_lend_books_cash_back_and_prunes():
    pf = Portfolio(cash=1000.0)
    with pf.lend("X", 1000.0) as s:
        s.cash -= 400.0
        s.shares = 100
    assert pf.cash == 600.0 and pf.positions["X"].cash == 0.0
    with pf.lend("Y", 600.0):
        pass
    assert "Y" not in pf.positions


def test_pre_024_ledger_loads():
    old = State(cash=600.0, ticker="X", shares=100, basis=24.0,
                option=Short("C", 26.0, dt.date(2026, 12, 18), 1, 0.47, DATE)).to_dict()
    pf = Portfolio.from_dict(old)
    assert pf.cash == 600.0 and pf.held() == ["X"] and pf.positions["X"].option.strike == 26.0
    assert Portfolio.from_dict(State(cash=3000.0).to_dict()) == Portfolio(cash=3000.0)
    assert Portfolio.from_dict(pf.to_dict()) == pf


def test_max_positions_validated():
    with pytest.raises(ConfigError):
        load_config(None, {"max_positions": 0})


def test_weekly_bh_two_stocks(cfg):
    ctx = lambda p: [{"ticker": "B", "price": p, "asset_type": "stock"},  # noqa: E731
                     {"ticker": "D", "price": p, "asset_type": "stock"}]
    scans = [{"date": "2026-10-26", "contexts": ctx(12.0), "equity": 3000.0, "synthetic": True, "modelled": True},
             {"date": "2026-10-30", "contexts": ctx(13.0), "equity": 3000.0, "synthetic": True, "modelled": True}]
    trades = pd.DataFrame(columns=["status", "action", "mid", "fill", "qty", "in_band", "date", "contract"])
    md = weekly_report("2026-10-30", trades, scans, cfg)
    # B: min(3000, 1700) → 1 lot ($1,200); D: min(1800, 1700) → 1 lot; +$1 × 200 sh
    assert "- Buy-and-hold P/L: $200.00 (100 sh B; 100 sh D, 2026-10-26 to 2026-10-30" in md
