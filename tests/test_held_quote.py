"""Item 083: the held option's strike is always inside the strike window the bot reads."""
import datetime as dt

import pytest

from ccbot import expiries
from ccbot.bot import BrokerMarket, run_daily
from ccbot.broker.base import NoQuote
from ccbot.broker.sim import SimBroker
from ccbot.config import load_config
from ccbot.portfolio import Portfolio
from ccbot.rules import Day, Quote, Short, State

DATE = dt.date(2026, 11, 19)
EXP = dt.date(2026, 12, 18)
HELD_SYM = "VALE261218C00013000"   # occ_symbol("VALE", EXP, "C", 13.0)
HELD = Short("C", 13.0, EXP, 2, 0.16, dt.date(2026, 11, 2))


class StubBroker:
    def __init__(self):
        self.windows = []

    def calendar(self, asof):
        return expiries.scan_calendar(asof)

    def list_option_contracts(self, underlying, exp_from, exp_to, lo, hi):
        self.windows.append((lo, hi))
        return []

    def get_option_snapshots(self, symbols):
        return []


def test_window_widens_to_the_held_strike():
    """VALE at $9.83 with a $13 call: 0.7-1.3x is 6.88-12.78, which left 13 out (2026-11-19)."""
    b = StubBroker()
    m = BrokerMarket(b, "VALE", DATE, [], Short("C", 13.0, EXP, 2, 0.16, dt.date(2026, 11, 2)))
    m.chain(Day(DATE, 9.83), EXP, "C")
    lo, hi = b.windows[0]
    assert lo <= 13.0 <= hi and abs(lo - 6.881) < 1e-9


def test_window_unchanged_without_a_held_option_or_on_another_expiry():
    b = StubBroker()
    BrokerMarket(b, "VALE", DATE, []).chain(Day(DATE, 10.0), EXP, "C")
    other = BrokerMarket(b, "VALE", DATE, [], Short("C", 13.0, dt.date(2027, 1, 15), 2, 0.16, DATE))
    other.chain(Day(DATE, 10.0), EXP, "C")
    assert [(round(lo, 2), round(hi, 2)) for lo, hi in b.windows] == [(7.0, 13.0), (7.0, 13.0)]
    assert BrokerMarket(b, "VALE", DATE, [], Short("C", 15.0, EXP, 1, 0.1, DATE)).chain(Day(DATE, 10.0), EXP, "C") == []
    assert b.windows[-1][1] == 15.0


class HeldQuotes:
    """Market data for SimBroker(quotes=...) (item 085). Synthetic fixture values, not market data.
    The strike filter is a test choice, like a strike-range query, not a claim about Webull.
    Same vol (NaN) as the live Webull Day."""
    quotes_have_oi = True

    def __init__(self):
        self.windows = []

    def get_underlying_quote(self, t):
        if t == "VALE":
            return Day(DATE, 9.83)
        raise NoQuote(t)

    def list_option_contracts(self, u, f, t, lo, hi):
        self.windows.append((u, f, lo, hi))
        return [HELD_SYM] if u == "VALE" and f == EXP and lo <= 13.0 <= hi else []

    def get_option_snapshots(self, symbols):
        return [Quote(HELD_SYM, 13.0, "C", 0.01, 0.03, 0.02, 0.03, 500, None)] if HELD_SYM in symbols else []


def _held_run(tmp_path, universe):
    """run_daily on a fresh tmp_path ledger holding 200 VALE (synthetic cash 1000) with the 13C open."""
    cfg = load_config(None, {"universe": universe})
    b = SimBroker(cfg, quotes=HeldQuotes(), ledger_path=tmp_path / "state" / "ledger.json")
    b.state = Portfolio(cash=1000.0, positions={"VALE": State(cash=0.0, ticker="VALE", shares=200, option=HELD)})
    scan = run_daily(DATE, b, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports")
    return scan, b.quotes


def _widened(stub):
    return any(u == "VALE" and f == EXP and lo <= 13.0 <= hi for u, f, lo, hi in stub.windows)


def test_run_daily_passes_held_option_at_universe_site(tmp_path):
    """item 085: a reverted L221 leaves 13 outside 6.881-12.779; equity NaN."""
    scan, stub = _held_run(tmp_path, ["VALE"])
    assert _widened(stub)
    assert scan["equity"] == pytest.approx(2962.0)
    assert scan["rejects"].get("VALE") != "CAPITAL_UNKNOWN"


def test_run_daily_passes_held_option_at_held_only_site(tmp_path):
    """item 085: VALE held but not in the universe (bot.py L230); a reverted L230 leaves equity NaN."""
    scan, stub = _held_run(tmp_path, ["SYNTH_A"])
    assert _widened(stub)
    assert scan["equity"] == pytest.approx(2962.0)
