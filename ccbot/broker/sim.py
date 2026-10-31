"""Local paper broker. Quotes come from the BS model on a PriceSeries or from a snapshot CSV."""
import datetime as dt
import json
import os
from pathlib import Path

import pandas as pd

from .. import expiries
from ..backtest import build_days
from ..data import DataError
from ..pricing import grid_range
from ..portfolio import Portfolio
from ..rules import Day, Quote, apply_fill, model_quote, settle_day
from .base import Broker, NoQuote, OptionOrder, OrderRejected, OrderResult, occ_symbol, parse_occ, validate


class SimBroker(Broker):
    name = "sim"

    def __init__(self, cfg, series=None, snapshots=None, meta=None, ledger_path="state/sim_ledger.json"):
        self.cfg, self.series, self.snapshots = cfg, series, snapshots
        self.ledger_path = Path(ledger_path)
        self.synthetic = bool((series.meta if series is not None else meta or {}).get("synthetic"))
        self.modelled = series is not None or self.synthetic
        self.quotes_have_oi = series is None   # BS model quotes carry no OI
        if series is not None:
            self._days = {d.date: d for d in build_days(series)}
        self.date, self.state, self.orders, self.n_orders = None, Portfolio(cash=cfg["cash"]), [], 0
        if self.ledger_path.exists():
            saved = json.loads(self.ledger_path.read_text(encoding="utf-8"))
            self.date = saved["date"] and dt.date.fromisoformat(saved["date"])
            self.state = Portfolio.from_dict(saved["state"])
            self.orders = [_order_from(o) for o in saved["orders"]]

    # ---- persistence ----
    def _save(self):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.ledger_path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"date": self.date and self.date.isoformat(), "state": self.state.to_dict(),
                                   "orders": [_order_to(o) for o in self.orders]}, indent=2), encoding="utf-8")
        os.replace(tmp, self.ledger_path)

    def calendar(self, asof):
        """Series replay: the backtest's own calendar (ModelMarket), so bot and backtest agree."""
        if self.series is not None:
            dates = [d.date() for d in self.series.df.index]
            return expiries.extend(dates, dates[-1] + dt.timedelta(days=70))
        return super().calendar(asof)

    # ---- quotes ----
    def _snap_rows(self, ticker=None):
        df = self.snapshots[self.snapshots["ts"] == self.date]
        return df if ticker is None else df[df["underlying"] == ticker]

    def get_underlying_quote(self, ticker):
        if self.series is not None:
            if ticker != self.series.ticker or self.date not in self._days:
                raise NoQuote(f"no quote for {ticker} on {self.date}")
            return self._days[self.date]
        rows = self._snap_rows(ticker)
        if rows.empty:
            raise NoQuote(f"no snapshot for {ticker} on {self.date}")
        older = self.snapshots[(self.snapshots["underlying"] == ticker) & (self.snapshots["ts"] < self.date)]
        first = rows.iloc[0]
        opt = lambda x: x if pd.notna(x) else None  # noqa: E731
        next_earnings = opt(first["next_earnings"])
        ex = opt(first["ex_div_date"])
        nxt = next((d for d in self.calendar(self.date) if d > self.date), None)
        # Snapshots give the ex-date but no amount: a known "not today/tomorrow" is 0.0,
        # anything else is unknown (NaN), never 0.0 (014, missing.py broker.dividend/div_next).
        return Day(self.date, float(first["underlying_price"]),
                   float(older.iloc[-1]["underlying_price"]) if len(older) else None,
                   float(rows["iv"].median()), q=0.0,   # labelled fallback: missing.py broker.q
                   dividend=float("nan") if ex is None or ex == self.date else 0.0,
                   div_next=float("nan") if ex is None or ex == nxt else 0.0,
                   next_earnings=next_earnings, ex_div_date=ex, asset_type=first["asset_type"],
                   earnings_known=first["asset_type"] == "etf" or next_earnings is not None)

    def list_option_contracts(self, underlying, exp_from, exp_to, strike_lo, strike_hi):
        if self.series is not None:
            self.get_underlying_quote(underlying)
            exps = [e for e in expiries.fridays(self.calendar(self.date)) if exp_from <= e <= exp_to]
            return [occ_symbol(underlying, e, kind, k) for e in exps for kind in ("C", "P")
                    for k in grid_range(strike_lo, strike_hi)]
        rows = self._snap_rows(underlying)
        rows = rows[(rows["expiry"] >= exp_from) & (rows["expiry"] <= exp_to)
                    & (rows["strike"] >= strike_lo - 1e-9) & (rows["strike"] <= strike_hi + 1e-9)]
        return list(rows["symbol"].dropna())

    def get_option_snapshots(self, symbols):
        out = []
        if self.series is not None:
            for s in symbols:
                u, exp, kind, k = parse_occ(s)
                out.append(model_quote(s, self.get_underlying_quote(u), k, exp, kind, self.cfg))
            return out
        rows = self._snap_rows()
        for _, r in rows[rows["symbol"].isin(list(symbols))].iterrows():
            out.append(Quote(r["symbol"], float(r["strike"]), r["type"], float(r["bid"]), float(r["ask"]),
                             (r["bid"] + r["ask"]) / 2, float(r["delta"]),
                             int(r["oi"]) if pd.notna(r["oi"]) else None, float(r["iv"])))
        return out

    # ---- account ----
    def get_positions(self):
        return Portfolio.from_dict(self.state.to_dict())

    def get_cash(self):
        return self.state.cash

    def _quote(self, order):
        quotes = self.get_option_snapshots([order.symbol])
        return quotes[0] if quotes else None

    def preview(self, order):
        validate(order, self.state, self.state.cash)
        q = self._quote(order)
        return {"symbol": order.symbol, "bid": q and q.bid, "ask": q and q.ask, "limit": order.limit}

    def _try_fill(self, order):
        q = self._quote(order)
        if q is None:
            return None
        sell = order.side == "SELL_TO_OPEN"
        if (sell and order.limit <= q.bid + 1e-9) or (not sell and order.limit >= q.ask - 1e-9):
            action = "BUY_TO_CLOSE" if not sell else ("SELL_CALL" if order.kind == "C" else "SELL_PUT")
            with self.state.lend(order.underlying, self.state.cash) as sleeve:
                fee = apply_fill(sleeve, action, order.limit, order.qty, self.date, self.cfg,
                                 order.kind, order.strike, order.expiry)
            return OrderResult("FILLED", order.limit, fee["total"])
        return None

    def submit(self, order):
        self.n_orders += 1
        try:
            validate(order, self.state, self.state.cash)
        except OrderRejected as exc:
            return OrderResult("REJECTED", detail=exc.reason)
        result = self._try_fill(order)
        if result is None:
            self.orders.append((order, self.date))
            result = OrderResult("RESTING", detail=f"{order.tif} order resting")
        self._save()
        return result

    def buy_shares(self, ticker, qty, limit):
        self.n_orders += 1
        price = self.get_underlying_quote(ticker).close
        if limit < price or self.state.cash < price * qty:
            return OrderResult("REJECTED", detail="limit below close or insufficient cash")
        if ticker not in self.state.positions and len(self.state.held()) >= self.cfg["max_positions"]:
            return OrderResult("REJECTED", detail="max_positions reached")
        with self.state.lend(ticker, self.state.cash) as sleeve:
            apply_fill(sleeve, "BUY_SHARES", price, qty, self.date, self.cfg)
        self._save()
        return OrderResult("FILLED", price)

    def advance(self, date):
        """Cancel yesterday's DAY orders, settle the day (same helper as the backtest),
        re-check resting GTC buy-to-close orders. Idempotent for a date already reached."""
        if self.date is not None and date < self.date:
            raise ValueError(f"ledger is at {self.date}; cannot go back to {date}")
        if self.date == date:
            return []
        self.date, events = date, []
        for order, placed in list(self.orders):
            if order.tif == "DAY" and placed < date:
                self.orders.remove((order, placed))
                events.append({"action": "CANCELLED", "contract": order.symbol, "status": "CANCELLED",
                               "ticker": order.underlying})
        for ticker in self.state.held():
            try:
                day = self.get_underlying_quote(ticker)
            except NoQuote as exc:
                raise DataError(f"cannot settle the paper ledger: {exc}") from exc
            with self.state.lend(ticker, 0.0) as sleeve:
                events += [{**e, "ticker": ticker} for e in settle_day(sleeve, day, self.cfg)]
        for order, placed in list(self.orders):
            result = self._try_fill(order)
            if result is not None:
                self.orders.remove((order, placed))
                events.append({"action": "BUY_TO_CLOSE", "contract": order.symbol, "status": "FILLED",
                               "ticker": order.underlying,
                               "fill": result.fill, "fees": result.fees, "detail": "resting GTC filled"})
        self._save()
        return events


def _order_to(item):
    order, placed = item
    d = dict(vars(order))
    d["expiry"], d["placed"] = order.expiry.isoformat(), placed.isoformat()
    return d


def _order_from(d):
    d = dict(d)
    placed = dt.date.fromisoformat(d.pop("placed"))
    d["expiry"] = dt.date.fromisoformat(d["expiry"])
    return OptionOrder(**d), placed
