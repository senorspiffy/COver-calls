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


def test_earnings_known_for_dec_18_on_2026_11_09():
    """Monday's first run: every name clears the Dec 18 expiry."""
    cfg = _cfg("practice.json")
    facts = load_facts(cfg)
    day = Day(dt.date(2026, 11, 9), 20.0, q=0.0)
    clear = {t for t in cfg["universe"]
             if (d := enrich(day, t, facts, cfg)).earnings_known and d.next_earnings > dt.date(2026, 12, 18)}
    assert set(cfg["universe"]) - clear == set()   # PBR: last report Nov 10 (2026-11-11 follow-up)


def test_weekly_account_gives_each_stock_8000_and_has_facts():
    """Item 054 (trimmed to 7 quality names in 055): $8,000 each, all with sourced facts."""
    cfg = _cfg("weekly.json")
    n = len(cfg["universe"])
    assert n == cfg["max_positions"] == 7
    assert 8000 <= cfg["max_single_name_frac"] * cfg["cash"] < 8000 + 200
    facts = load_facts(cfg)
    assert all(t in facts and facts[t]["sources"] for t in cfg["universe"])
    day = Day(dt.date(2026, 11, 13), 20.0, q=0.0)
    assert all(enrich(day, t, facts, cfg).earnings_known for t in cfg["universe"])


def test_quality_account_14_names_8000_each():
    """Item 055: the 14 names scoring 4/5 or 5/5, $8,000 each, monthly; all with facts."""
    cfg = _cfg("quality.json")
    n = len(cfg["universe"])
    assert n == cfg["max_positions"] == 14
    assert 8000 <= cfg["max_single_name_frac"] * cfg["cash"] < 8000 + 200
    assert set(_cfg("weekly.json")["universe"]) <= set(cfg["universe"])
    facts = load_facts(cfg)
    assert all(t in facts and facts[t]["sources"] for t in cfg["universe"])
    day = Day(dt.date(2026, 11, 13), 20.0, q=0.0)
    assert all(enrich(day, t, facts, cfg).earnings_known for t in cfg["universe"])
