"""Item 048: practice account config (13 stocks, $5,000 each) and its ticker facts."""
import datetime as dt

from ccbot.config import load_config
from ccbot.rules import Day
from ccbot.tickers import enrich, load_facts

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def _cfg(name):
    return load_config(ROOT / "config" / name, {"tickers_file": str(ROOT / "config" / "tickers.json")})


def test_practice_gives_each_stock_5000():
    cfg = _cfg("practice.json")
    n = len(cfg["universe"])
    assert cfg["max_positions"] == n == 13
    per_stock = cfg["max_single_name_frac"] * cfg["cash"]
    assert 5000 <= per_stock < 5000 + 200      # 100 sh up to ~$50 fit, one sleeve each
    assert cfg["cash"] - n * 5000 == cfg["cash_buffer"]


def test_main_paper_account_is_5000_two_stocks():
    cfg = _cfg("paper.json")
    assert cfg["cash"] == 5000 and cfg["max_positions"] == 2 and cfg["max_single_name_frac"] == 0.5


def test_every_universe_ticker_has_sourced_facts():
    facts = load_facts(_cfg("practice.json"))
    for t in _cfg("practice.json")["universe"] + _cfg("paper.json")["universe"]:
        assert t in facts and facts[t]["sources"], t


def _blocked_for_dec_18(day_date):
    cfg = _cfg("practice.json")
    facts = load_facts(cfg)
    day = Day(day_date, 20.0, q=0.0)
    clear = {t for t in cfg["universe"]
             if (d := enrich(day, t, facts, cfg)).earnings_known and d.next_earnings > dt.date(2026, 12, 18)}
    return set(cfg["universe"]) - clear


def test_earnings_known_for_dec_18_on_2026_11_09():
    """PBR reports 2026-11-10, after this day (053): 12 of 13 clear the Dec 18 expiry."""
    assert _blocked_for_dec_18(dt.date(2026, 11, 9)) == {"PBR"}


def test_earnings_known_for_dec_18_on_2026_11_11():
    """053: after PBR's 2026-11-10 report every name clears Dec 18 (PBR estimate 2027-01-19)."""
    assert _blocked_for_dec_18(dt.date(2026, 11, 11)) == set()
