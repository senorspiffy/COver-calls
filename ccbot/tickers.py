"""Per-ticker facts the broker feed lacks (item 040): asset type, earnings and dividend dates.

Read from the JSON file named by cfg["tickers_file"] (config/tickers.json). Every value there
is entered from a source; null means unknown and keeps the missing-data policy (a stock with
unknown earnings is blocked, ccbot/missing.py).

Earnings estimate [house rule, person-visible]: when `next_earnings` is null but
`last_earnings` is known, the next report is taken as no earlier than last + earnings_gap_days
(70 by default; US companies report quarterly, about 91 days apart). The Day is flagged
`earnings_estimated` and the report says so. Once that date has passed with no new date
entered, earnings are unknown again and the stock is blocked.
"""
import dataclasses
import datetime as dt
import json
from pathlib import Path

from .data import DataError
from .expiries import load_holidays

# Optional keys of a tickers.json entry. Each has a `tickers.<key>` row in MISSING_POLICY
# (item 041; tests/test_missing_inputs.py::test_policy_lists_every_optional_input).
TICKER_FIELDS = ("next_earnings", "ex_div_date", "dividend")


def _d(x):
    return dt.date.fromisoformat(x) if x else None


def load_facts(cfg):
    path = cfg.get("tickers_file")
    if not path:
        return {}
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataError(f"cannot read tickers file {path}: {exc}") from exc
    return {t: v for t, v in raw.items() if not t.startswith("_")}


def enrich(day, ticker, facts, cfg):
    """The broker's Day with the file's facts applied. A ticker not in the file is unchanged."""
    f = facts.get(ticker)
    if f is None:
        return day
    asset = f.get("asset_type") or day.asset_type
    nxt, estimated = _d(f.get("next_earnings")), False
    if nxt is None and f.get("last_earnings"):
        guess = _d(f["last_earnings"]) + dt.timedelta(days=cfg["earnings_gap_days"])
        if guess > day.date:
            nxt, estimated = guess, True
    if nxt is not None and nxt < day.date:
        nxt = None       # a stale date is unknown, never "no earnings"
    ex_div = _d(f.get("ex_div_date"))
    if ex_div is not None and ex_div < day.date:
        ex_div = None    # a past ex-date says nothing about the next one: unknown, never 0.0 (041)
    amount = f.get("dividend")
    dividend, div_next = day.dividend, day.div_next   # unknown (NaN) unless both date and amount are known
    if ex_div is not None and amount is not None:
        nxt_day = _next_trading_day(day.date)
        dividend = float(amount) if ex_div == day.date else 0.0
        div_next = float(amount) if ex_div == nxt_day else 0.0
    return dataclasses.replace(day, asset_type=asset, next_earnings=nxt,
                               earnings_known=asset == "etf" or nxt is not None,
                               earnings_estimated=estimated, ex_div_date=ex_div,
                               dividend=dividend, div_next=div_next)


def _next_trading_day(d):
    """Next NYSE trading day after d (weekends and config/holidays.json closures skipped)."""
    closed = set(load_holidays()["holidays"])
    d += dt.timedelta(days=1)
    while d.weekday() >= 5 or d.isoformat() in closed:
        d += dt.timedelta(days=1)
    return d
