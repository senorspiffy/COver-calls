"""Broker interface and order rules (strictest reading of Webull's docs, 03 A4)."""
import datetime as dt
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..rules import CONTRACT

SIDES = ("SELL_TO_OPEN", "BUY_TO_CLOSE")


class LiveTradingDisabled(Exception):
    """Raised for any path that could reach a production host or live trading."""


class OrderRejected(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class NoQuote(LookupError):
    """The broker has no quote for this ticker/date."""


@dataclass
class OptionOrder:
    underlying: str
    expiry: dt.date
    strike: float
    kind: str                 # 'C' or 'P'
    side: str                 # SELL_TO_OPEN or BUY_TO_CLOSE
    qty: int
    limit: float
    tif: str = "DAY"
    order_type: str = "LIMIT"

    @property
    def symbol(self):
        return occ_symbol(self.underlying, self.expiry, self.kind, self.strike)


@dataclass
class OrderResult:
    status: str               # FILLED, RESTING, DRY_RUN, REJECTED, SANDBOX_REJECTED, SUBMITTED
    fill: float | None = None
    fees: float = 0.0
    detail: str = ""


def validate(order, positions, cash):
    """Raise OrderRejected(reason) unless the order is allowed. positions: rules.State."""
    if order.order_type == "MARKET":
        raise OrderRejected("MARKET_NOT_ALLOWED")
    if order.order_type.startswith("TRAILING"):
        raise OrderRejected("TRAILING_NOT_ALLOWED")
    if order.order_type != "LIMIT":
        raise OrderRejected("ORDER_TYPE_NOT_ALLOWED")
    if order.tif not in ("DAY", "GTC"):
        raise OrderRejected("TIF_NOT_ALLOWED")
    if order.side not in SIDES:
        raise OrderRejected("SIDE_NOT_ALLOWED")
    if order.side == "SELL_TO_OPEN" and order.tif != "DAY":
        raise OrderRejected("SELL_GTC_NOT_ALLOWED")
    if order.qty < 1:
        raise OrderRejected("BAD_QTY")
    if order.limit <= 0 or abs(order.limit * 100 - round(order.limit * 100)) > 1e-6:
        raise OrderRejected("LIMIT_OFF_TICK")
    held = positions.option
    if order.side == "BUY_TO_CLOSE":
        if held is None or (held.kind, held.strike, held.expiry) != (order.kind, order.strike, order.expiry) \
                or order.qty > held.qty:
            raise OrderRejected("NO_POSITION_TO_CLOSE")
    elif order.kind == "C":
        open_calls = held.qty if held is not None and held.kind == "C" else 0
        if order.qty > positions.shares // CONTRACT - open_calls:
            raise OrderRejected("NAKED_CALL")
    elif cash < order.strike * CONTRACT * order.qty:
        raise OrderRejected("CSP_CASH")
    return order


def occ_symbol(underlying, expiry, kind, strike):
    """OCC-style symbol, e.g. SOFI261106C00017500 (root not padded, as Webull shows it)."""
    return f"{underlying}{expiry:%y%m%d}{kind}{round(strike * 1000):08d}"


_OCC = re.compile(r"^(?P<u>[A-Z0-9_.]+?)(?P<d>\d{6})(?P<k>[CP])(?P<s>\d{8})$")


def parse_occ(symbol):
    m = _OCC.match(symbol)
    if not m:
        raise ValueError(f"not an OCC symbol: {symbol}")
    return (m["u"], dt.datetime.strptime(m["d"], "%y%m%d").date(), m["k"], int(m["s"]) / 1000)


def chunk(items, size=20):
    items = list(items)
    return [items[i:i + size] for i in range(0, len(items), size)]


class Broker(ABC):
    name = "base"
    modelled = False      # True when quotes come from the BS model or synthetic snapshots
    synthetic = False
    dry_run = False       # True when orders are only validated/previewed, never filled

    @abstractmethod
    def advance(self, date):
        """Move the broker to `date` (settle expiries, re-check resting orders); list of events."""

    @abstractmethod
    def get_underlying_quote(self, ticker):
        """rules.Day for the ticker on the current date; NoQuote if unavailable."""

    @abstractmethod
    def list_option_contracts(self, underlying, exp_from, exp_to, strike_lo, strike_hi):
        """OCC symbols."""

    @abstractmethod
    def get_option_snapshots(self, symbols):
        """List of rules.Quote; callers pass at most 20 symbols (see chunk)."""

    @abstractmethod
    def get_positions(self):
        """rules.State (paper ledger)."""

    @abstractmethod
    def get_cash(self):
        """Cash in $."""

    @abstractmethod
    def preview(self, order):
        """Validate and estimate an order without placing it."""

    @abstractmethod
    def submit(self, order):
        """OrderResult."""

    @abstractmethod
    def buy_shares(self, ticker, qty, limit):
        """OrderResult for a stock purchase at `limit`."""
