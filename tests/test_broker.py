import datetime as dt

import pytest

from conftest import head
from helpers import write_path
from ccbot.backtest import run_backtest
from ccbot.bot import run_daily
from ccbot.broker.base import OptionOrder, OrderRejected, occ_symbol, parse_occ, validate
from ccbot.broker.sim import SimBroker
from ccbot.rules import Short, State
from ccbot.variants import BY_ID

EXP = dt.date(2026, 11, 20)


def _state(shares=100, option=None):
    return State(cash=600, ticker="X", shares=shares, option=option)


def _order(**kw):
    base = dict(underlying="X", expiry=EXP, strike=26.0, kind="C", side="SELL_TO_OPEN", qty=1, limit=0.30)
    return OptionOrder(**{**base, **kw})


@pytest.mark.parametrize("kw,reason", [
    ({"order_type": "MARKET"}, "MARKET_NOT_ALLOWED"),
    ({"order_type": "TRAILING_STOP_LOSS"}, "TRAILING_NOT_ALLOWED"),
    ({"tif": "GTC"}, "SELL_GTC_NOT_ALLOWED"),
    ({"limit": 0.475}, "LIMIT_OFF_TICK"),
    ({"qty": 2}, "NAKED_CALL"),
])
def test_order_rules_reject(kw, reason):
    with pytest.raises(OrderRejected) as e:
        validate(_order(**kw), _state(), 600)
    assert e.value.reason == reason


def test_naked_call_without_shares():
    with pytest.raises(OrderRejected, match="NAKED_CALL"):
        validate(_order(), _state(shares=0), 600)


def test_gtc_buy_to_close_accepted():
    held = Short("C", 26.0, EXP, 1, 0.30, dt.date(2026, 10, 19))
    assert validate(_order(side="BUY_TO_CLOSE", tif="GTC", limit=0.15), _state(option=held), 600)


def test_csp_needs_cash():
    with pytest.raises(OrderRejected, match="CSP_CASH"):
        validate(_order(kind="P", strike=22.0), _state(shares=0), 2199.99)
    assert validate(_order(kind="P", strike=22.0), _state(shares=0), 2200)


def test_occ_round_trip():
    assert occ_symbol("SOFI", dt.date(2026, 11, 6), "C", 17.5) == "SOFI261106C00017500"
    assert parse_occ("SOFI261106C00017500") == ("SOFI", dt.date(2026, 11, 6), "C", 17.5)


@pytest.fixture
def flat(tmp_path):
    return write_path(tmp_path / "X.csv", [24] * 40), tmp_path / "ledger.json"


def _buy_and_sell(b, series, cfg):
    d0 = series.df.index[0].date()
    b.advance(d0)
    assert b.buy_shares("X", 100, 24).status == "FILLED"
    syms = [s for s in b.list_option_contracts("X", EXP, EXP, 26, 26) if parse_occ(s)[2] == "C"]
    q = b.get_option_snapshots(syms)[0]
    return d0, q


def test_sim_limits_day_and_gtc(flat, cfg):
    series, ledger = flat
    b = SimBroker(cfg, series=series, ledger_path=ledger)
    d0, q = _buy_and_sell(b, series, cfg)
    assert b.preview(_order(limit=q.bid))["bid"] == q.bid
    assert b.submit(_order(limit=round(q.bid + 0.05, 2))).status == "RESTING"   # above the bid: no fill
    events = b.advance(series.df.index[1].date())
    assert [e["action"] for e in events] == ["CANCELLED"] and b.orders == []    # DAY order gone next day
    b.advance(series.df.index[2].date())
    q = b.get_option_snapshots([q.symbol])[0]
    assert b.submit(_order(limit=q.bid)).status == "FILLED"
    target = round(q.ask * 0.6, 2)
    assert b.submit(_order(side="BUY_TO_CLOSE", tif="GTC", limit=target)).status == "RESTING"
    filled = []
    for d in series.df.index[3:]:
        filled += [e for e in b.advance(d.date()) if e.get("status") == "FILLED"]
        if filled:
            break
    assert filled and b.get_positions().get("X").option is None and filled[0]["fill"] == target


def test_ledger_survives_restart(flat, cfg):
    series, ledger = flat
    b = SimBroker(cfg, series=series, ledger_path=ledger)
    _, q = _buy_and_sell(b, series, cfg)
    b.submit(_order(limit=q.bid))
    again = SimBroker(cfg, series=series, ledger_path=ledger)
    assert again.get_positions() == b.get_positions() and again.get_cash() == b.get_cash()
    assert again.date == b.date


def test_bot_on_simbroker_matches_backtest_v0(synth_a, cfg, tmp_path):
    series = head(synth_a, 300)
    bt = run_backtest(series, BY_ID["V0"], cfg).trades
    want = [(r["date"], r["action"], r["strike"] if r["action"] != "BUY_SHARES" else None,
             r["expiry"] if r["action"] != "BUY_SHARES" else None, round(r["price"], 4))
            for _, r in bt[bt["action"].isin(["SELL_CALL", "BUY_SHARES"])].iterrows()]
    broker = SimBroker(cfg, series=series, ledger_path=tmp_path / "state" / "sim_ledger.json")
    got = []
    for d in series.df.index:
        scan = run_daily(d.date(), broker, cfg, "V0", state_dir=tmp_path / "state", reports_dir=tmp_path / "r")
        for r in scan["decisions"]:
            if r["action"] in ("SELL_CALL", "BUY_SHARES") and r["status"] == "FILLED":
                strike = expiry = None
                if r["action"] == "SELL_CALL":
                    _, expiry, _, strike = parse_occ(r["contract"])
                got.append((d.date(), r["action"], strike, expiry, round(r["fill"], 4)))
    assert len(want) > 5 and got == want
