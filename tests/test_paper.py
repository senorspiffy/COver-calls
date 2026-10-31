"""Item 025: webull-paper mode, per-ticker facts file, option marks for capital."""
import datetime as dt
import json
import math

import pytest

from test_webull_sandbox import ENV, FakeSDK, Resp
from ccbot.bot import _capital, run_daily
from ccbot.broker.webull_sandbox import TokenBucket, WebullSandboxBroker
from ccbot.config import load_config
from ccbot.portfolio import Portfolio
from ccbot.rules import Day, Market, Quote, Short, State
from ccbot.tickers import enrich

DATE = dt.date(2026, 10, 30)
EXP = dt.date(2026, 12, 18)


def _cfg(tmp_path, facts, **over):
    p = tmp_path / "tickers.json"
    p.write_text(json.dumps(facts), encoding="utf-8")
    return load_config(None, {"tickers_file": str(p), **over})


FORD = {"asset_type": "stock", "next_earnings": None, "last_earnings": "2026-10-28",
        "ex_div_date": "2026-11-10", "dividend": 0.15}


def test_enrich_estimates_earnings_from_last_report(tmp_path):
    cfg = _cfg(tmp_path, {})
    day = enrich(Day(DATE, 12.33), "F", {"F": FORD}, cfg)
    assert day.next_earnings == dt.date(2027, 1, 6) and day.earnings_known and day.earnings_estimated
    assert day.ex_div_date == dt.date(2026, 11, 10) and day.dividend == 0.0
    exday = enrich(Day(dt.date(2026, 11, 10), 12.33), "F", {"F": FORD}, cfg)
    assert exday.dividend == 0.15


def test_enrich_estimate_expires_and_blocks(tmp_path):
    cfg = _cfg(tmp_path, {})
    late = enrich(Day(dt.date(2027, 1, 7), 12.0), "F", {"F": FORD}, cfg)
    assert late.next_earnings is None and late.earnings_known is False   # unknown again: blocked


def test_enrich_unknown_ticker_and_given_date(tmp_path):
    cfg = _cfg(tmp_path, {})
    base = Day(DATE, 10.0)
    assert enrich(base, "ZZZ", {"F": FORD}, cfg) is base
    given = enrich(base, "F", {"F": {**FORD, "next_earnings": "2026-12-01"}}, cfg)
    assert given.next_earnings == dt.date(2026, 12, 1) and not given.earnings_estimated


class OneQuote(Market):
    def __init__(self, quotes):
        super().__init__([EXP], [])
        self.quotes = quotes

    def chain(self, day, expiry, kind):
        return self.quotes


def test_capital_marks_option_at_quote_else_nan(cfg):
    pf = Portfolio(cash=1600.0, positions={"F": State(cash=0.0, ticker="F", shares=100, basis=12.0,
                                                      option=Short("C", 13.5, EXP, 1, 0.24, DATE))})
    day = Day(DATE, 12.33)          # vol NaN, as from the Webull feed
    q = Quote("F261218C00013500", 13.5, "C", 0.22, 0.26, 0.24, 0.26)
    assert _capital(pf, {"F": day}, {"F": OneQuote([q])}, cfg) == pytest.approx(1600 + 1233 - 24)
    assert math.isnan(_capital(pf, {"F": day}, {"F": OneQuote([])}, cfg))   # never priced at 0


class PaperSDK(FakeSDK):
    """FakeSDK with a Ford quote and a Dec 18 chain."""

    def __init__(self):
        super().__init__()
        base_data = self.DataClient
        chain = {13.0: (0.34, 0.36, 0.36), 13.5: (0.22, 0.24, 0.26), 14.0: (0.12, 0.13, 0.17)}

        def DataClient(api):
            d = base_data(api)
            d.market_data.get_snapshot = lambda *a: Resp([{"price": "12.33"}])
            d.instrument.list_option_contracts = lambda **kw: Resp(
                {"data": [{"symbol": f"F261218C{round(k * 1000):08d}"} for k in chain]})

            def snap(symbols, category):
                out = []
                for s in symbols.split(","):
                    k = int(s[-8:]) / 1000
                    if k in chain:
                        b, a, dl = chain[k]
                        out.append({"symbol": s, "bid": b, "ask": a, "delta": dl, "open_interest": 5000})
                return Resp(out)
            d.option_market_data.get_option_snapshot = snap
            return d
        self.DataClient = DataClient


def test_webull_paper_fills_in_local_ledger(tmp_path):
    cfg = _cfg(tmp_path, {"F": FORD}, universe=["F"])
    sdk = PaperSDK()
    b = WebullSandboxBroker(cfg, env=ENV, sdk=sdk, ledger_path=tmp_path / "s" / "ledger.json",
                            token_dir=tmp_path / "tok", limiter=TokenBucket(1000, sleep=lambda s: None), paper=True)
    assert b.dry_run is False and b.name == "webull-paper"
    scan = run_daily(DATE, b, cfg, state_dir=tmp_path / "s", reports_dir=tmp_path / "r")
    acts = [(d["action"], d["status"], d["contract"]) for d in scan["decisions"]]
    assert acts == [("BUY_SHARES", "FILLED", "F"), ("SELL_CALL", "FILLED", "F261218C00013500")]
    assert sdk.calls["place_option"] == 0 and sdk.calls["preview_option"] == 0   # nothing sent to Webull
    pf = b.get_positions()
    assert pf.positions["F"].shares == 100 and pf.positions["F"].option.premium == 0.22
    assert scan["equity"] == pytest.approx(3000 - 1233 + 22 - 0.10 + 1233 - 23, abs=0.01)   # call marked at mid 0.23
    md = (tmp_path / "r" / f"daily_{DATE}.md").read_text(encoding="utf-8")
    assert "(estimated: last report + earnings_gap_days)" in md and "broker webull-paper" in md
