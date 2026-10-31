"""Daily backtest at the close on a PriceSeries (MODELLED option prices)."""
import datetime as dt
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import expiries
from .broker.base import occ_symbol
from .rules import (CONTRACT, Day, Market, State, apply_fill, decide_entry, decide_exit,
                    equity, model_quote, settle_day)
from .pricing import strike_grid

OPTION_FILLS = ("SELL_CALL", "SELL_PUT", "BUY_TO_CLOSE")


@dataclass
class Result:
    trades: pd.DataFrame
    equity: pd.Series
    metrics: dict
    reasons: dict          # no-trade reason -> count of days


def _next_date(flags, dates):
    """For each row, the next date (>= today) where flags is true, else None."""
    out, nxt = [None] * len(dates), None
    for i in range(len(dates) - 1, -1, -1):
        if flags[i]:
            nxt = dates[i]
        out[i] = nxt
    return out


def build_days(series):
    df = series.df
    dates = [d.date() for d in df.index]
    close = df["close"]
    q = (df["dividend"].rolling(252, min_periods=1).sum() / close).to_numpy()
    vol = series.vol.to_numpy()
    pct = series.vol.rolling(252).apply(lambda w: (w <= w[-1]).mean() * 100, raw=True).to_numpy()
    div = df["dividend"].to_numpy()
    earn = _next_date(df["earnings"].to_numpy() == 1, dates)
    exdiv = _next_date(div > 0, dates)
    asset = series.meta.get("asset_type", "stock")
    days = []
    for i, d in enumerate(dates):
        days.append(Day(d, float(close.iloc[i]), float(close.iloc[i - 1]) if i else None, float(vol[i]),
                        float(q[i]), float(div[i]), float(div[i + 1]) if i + 1 < len(div) else 0.0,
                        float(pct[i]), earn[i], exdiv[i], asset, bool(math.isnan(vol[i]))))
    return days


class ModelMarket(Market):
    """BS quotes on the strike grid for every expiry on the series' calendar."""

    def __init__(self, ticker, dates, cfg):
        cal = expiries.extend(dates, dates[-1] + dt.timedelta(days=70))
        super().__init__(expiries.third_fridays(cal), expiries.fridays(cal))
        self.ticker, self.cfg = ticker, cfg

    def chain(self, day, expiry, kind):
        return [model_quote(occ_symbol(self.ticker, expiry, kind, k), day, k, expiry, kind, self.cfg)
                for k in strike_grid(day.close)]


def _check(state):
    if state.cash < -1e-6:
        raise AssertionError(f"cash < 0: {state.cash}")
    if state.shares % CONTRACT:
        raise AssertionError(f"shares not in lots of 100: {state.shares}")
    o = state.option
    if o and o.kind == "C" and o.qty * CONTRACT > state.shares:
        raise AssertionError("more than one short call per 100 shares")
    if o and o.kind == "P" and state.cash < o.strike * CONTRACT * o.qty - 1e-6:
        raise AssertionError("cash-secured put not covered by cash")


def _row(day, d, price, fee):
    return {"date": day.date, "action": d.action, "reason": d.reason, "kind": d.kind, "strike": d.strike, "expiry": d.expiry,
            "qty": d.qty, "price": price, "mid": d.mid, "fees": fee["total"], "delta": d.delta,
            "in_band": d.in_band, "in_window": d.in_window}


def execute(state, day, d, cfg):
    """Fill a decision at its limit price on the state (backtest only)."""
    fee = apply_fill(state, d.action, d.limit, d.qty, day.date, cfg, d.kind, d.strike, d.expiry)
    return _row(day, d, d.limit, fee)


def run_backtest(series, variant, cfg, days=None):
    days = days if days is not None else build_days(series)
    market = ModelMarket(series.ticker, [d.date for d in days], cfg)
    state = State(cash=cfg["cash"], ticker=series.ticker)
    trades, eq, reasons = [], [], {}
    for day in days:
        for ev in settle_day(state, day, cfg):
            trades.append({"date": day.date, **ev})
        ex = decide_exit(state, day, variant, cfg, market)
        if ex.action == "BUY_TO_CLOSE":
            trades.append(execute(state, day, ex, cfg))
        for _ in range(2):  # buy shares, then sell the call at the same close (buy-write)
            d = decide_entry(state, day, variant, cfg, market)
            if d.action == "NONE":
                reasons[d.reason] = reasons.get(d.reason, 0) + 1
                break
            trades.append(execute(state, day, d, cfg))
            if d.action != "BUY_SHARES":
                break
        _check(state)
        eq.append(equity(state, day, cfg))
    equity_s = pd.Series(eq, index=pd.DatetimeIndex([d.date for d in days]), name="equity")
    trades_df = pd.DataFrame(trades)
    return Result(trades_df, equity_s, metrics(equity_s, trades_df, cfg), reasons)


def buy_and_hold(series, cfg):
    """Same start, cash and dividends; shares never sold."""
    s0 = float(series.df["close"].iloc[0])
    shares = max(1, math.floor((cfg["cash"] - cfg["cash_buffer"]) / (s0 * CONTRACT))) * CONTRACT
    cash = cfg["cash"] - shares * s0 + (series.df["dividend"] * shares).cumsum()
    return (cash + shares * series.df["close"]).rename("equity")


def metrics(equity_s, trades, cfg, rf=None):
    rf = cfg["r"] if rf is None else rf
    e = equity_s.to_numpy()
    start = cfg["cash"]
    n = len(e)
    cagr = (e[-1] / start) ** (252 / n) - 1 if n and e[-1] > 0 else float("nan")
    rets = np.diff(np.concatenate([[start], e])) / np.concatenate([[start], e[:-1]])
    vol = float(rets.std(ddof=1) * math.sqrt(252)) if n > 1 else float("nan")
    peak = np.maximum.accumulate(np.concatenate([[start], e]))
    mdd = float(((np.concatenate([[start], e]) - peak) / peak).min())
    out = {"cagr": cagr, "vol": vol, "max_dd": mdd,
           "sharpe": (cagr - rf) / vol if vol and vol > 0 else float("nan"),
           "final_equity": float(e[-1]) if n else float("nan")}
    if trades is not None:
        fills = trades[trades["action"].isin(OPTION_FILLS)] if len(trades) else trades
        sells = fills[fills["action"] != "BUY_TO_CLOSE"] if len(fills) else fills
        out.update({
            "premium": float((sells["price"] * CONTRACT * sells["qty"]).sum()) if len(sells) else 0.0,
            "fills": int(len(fills)),
            "spread_paid": float(((fills["mid"] - fills["price"]).abs() * CONTRACT * fills["qty"]).sum())
            if len(fills) else 0.0,
            "fees_paid": float(fills["fees"].sum()) if len(fills) else 0.0,
        })
    return out
