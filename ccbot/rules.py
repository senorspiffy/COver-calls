"""Decision logic shared by the backtest and the bot, so the two cannot drift apart."""
import datetime as dt
import math
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from . import costs
from .expiries import pick_expiry
from .pricing import bs_delta, bs_price, pick_strike

CONTRACT = costs.CONTRACT

REASONS = (
    "OK", "HAS_POSITION", "NO_EXPIRY", "EARNINGS_BLACKOUT", "NOT_UP_DAY", "IV_FILTER",
    "NO_STRIKE_IN_TOLERANCE", "BASIS_ABOVE_BAND", "INSUFFICIENT_CASH", "UNIVERSE_EMPTY",
    "PROFIT_TARGET_HIT", "WINDOW_CLOSED_ROLL", "ASSIGNED_TODAY", "VOL_WARMUP",
)
ACTIONS = ("SELL_CALL", "SELL_PUT", "BUY_TO_CLOSE", "BUY_SHARES", "NONE")


def _d(x):
    return dt.date.fromisoformat(x) if isinstance(x, str) else x


@dataclass
class Short:
    kind: str            # 'C' or 'P'
    strike: float
    expiry: dt.date
    qty: int
    premium: float       # fill price per share
    sold_on: dt.date


@dataclass
class State:
    cash: float
    ticker: str = ""
    shares: int = 0
    basis: float = 0.0
    option: Short | None = None
    called_away: bool = False
    assigned_on: dt.date | None = None
    target_expiry: dt.date | None = None
    last_settled: dt.date | None = None

    def to_dict(self):
        d = asdict(self)
        for key in ("assigned_on", "target_expiry", "last_settled"):
            d[key] = d[key] and d[key].isoformat()
        if self.option:
            d["option"]["expiry"] = self.option.expiry.isoformat()
            d["option"]["sold_on"] = self.option.sold_on.isoformat()
        return d

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        for key in ("assigned_on", "target_expiry", "last_settled"):
            d[key] = d[key] and _d(d[key])
        if d["option"]:
            o = dict(d["option"])
            o["expiry"], o["sold_on"] = _d(o["expiry"]), _d(o["sold_on"])
            d["option"] = Short(**o)
        return cls(**d)


@dataclass(frozen=True)
class Day:
    date: dt.date
    close: float
    prev_close: float | None = None
    vol: float = float("nan")
    q: float = 0.0
    dividend: float = 0.0
    div_next: float = 0.0
    vol_pct: float = float("nan")
    next_earnings: dt.date | None = None
    ex_div_date: dt.date | None = None
    asset_type: str = "stock"
    vol_warmup: bool = False   # True while the trailing realised vol has too little history


@dataclass
class Quote:
    symbol: str
    strike: float
    kind: str
    bid: float
    ask: float
    mid: float
    delta: float
    oi: int | None = None
    iv: float | None = None


@dataclass
class Decision:
    action: str
    reason: str
    kind: str | None = None
    strike: float | None = None
    expiry: dt.date | None = None
    qty: int = 0
    limit: float | None = None
    mid: float | None = None
    delta: float | None = None
    in_band: bool | None = None
    in_window: bool | None = None

    def __post_init__(self):
        if self.action not in ACTIONS or self.reason not in REASONS:
            raise ValueError(f"unknown decision {self.action}/{self.reason}")  # closed lists


def none(reason):
    return Decision("NONE", reason)


def years_to(expiry, today):
    return (expiry - today).days / 365.0


def model_quote(symbol, day, strike, expiry, kind, cfg):
    """BS mid at the day's vol input, with bid/ask from the spread model."""
    T = years_to(expiry, day.date)
    mid = bs_price(day.close, strike, T, cfg["r"], day.q, day.vol, kind)
    return Quote(symbol, strike, kind, costs.fill_price(mid, "sell", cfg),
                 costs.fill_price(mid, "buy", cfg), mid,
                 bs_delta(day.close, strike, T, cfg["r"], day.q, day.vol, kind), iv=day.vol)


def option_mark(state, day, cfg):
    """Liability of the open short option at BS mid (0 if none)."""
    o = state.option
    if o is None:
        return 0.0
    mid = bs_price(day.close, o.strike, years_to(o.expiry, day.date), cfg["r"], day.q, day.vol, o.kind)
    return mid * CONTRACT * o.qty


def equity(state, day, cfg):
    return state.cash + state.shares * day.close - option_mark(state, day, cfg)


class Market(ABC):
    """Expiries and option chains for one underlying (model or broker quotes)."""

    def __init__(self, monthly, weekly):
        self._expiries = {"monthly": monthly, "weekly": weekly}

    def pick(self, today, kind, dte_range, slack):
        return pick_expiry(today, self._expiries[kind], dte_range, slack)

    @abstractmethod
    def chain(self, day, expiry, kind):
        """List of Quote for one expiry and kind ('C' or 'P')."""


# ---- settlement ---------------------------------------------------------------

def _assign(state, day, cfg, label):
    o = state.option
    n = o.qty * CONTRACT
    fee = costs.assignment_cost(cfg) * o.qty
    if o.kind == "C":
        state.shares -= n
        state.cash += o.strike * n - fee
        state.called_away = state.shares == 0
        if state.shares == 0:
            state.basis = 0.0
    else:
        state.shares += n
        state.cash -= o.strike * n + fee
        state.basis = o.strike
        state.called_away = False
    state.option, state.assigned_on = None, day.date
    return {"action": label, "kind": o.kind, "strike": o.strike, "expiry": o.expiry,
            "qty": o.qty, "price": o.strike, "fees": fee}


def settle_day(state, day, cfg):
    """Dividend credit, ex-dividend early assignment (001 F3) and expiry, at the
    day's close. Idempotent per date. Returns a list of event dicts."""
    if state.last_settled is not None and day.date <= state.last_settled:
        return []
    events = []
    if day.dividend > 0 and state.shares > 0:
        amount = day.dividend * state.shares
        state.cash += amount
        events.append({"action": "DIVIDEND", "price": day.dividend, "qty": state.shares, "amount": amount})
    o = state.option
    if o is not None:
        itm = day.close > o.strike if o.kind == "C" else day.close < o.strike
        if day.date >= o.expiry:
            if itm:
                events.append(_assign(state, day, cfg, "ASSIGNED"))
            else:
                state.option = None
                events.append({"action": "EXPIRED", "kind": o.kind, "strike": o.strike,
                               "expiry": o.expiry, "qty": o.qty, "price": 0.0, "fees": 0.0})
        elif o.kind == "C" and itm and day.div_next > 0:
            T = years_to(o.expiry, day.date)
            time_value = bs_price(day.close, o.strike, T, cfg["r"], day.q, day.vol, "C") - (day.close - o.strike)
            if time_value < day.div_next:
                events.append(_assign(state, day, cfg, "EARLY_ASSIGNED"))
    state.last_settled = day.date
    return events


def apply_fill(state, action, price, qty, day_date, cfg, kind=None, strike=None, expiry=None):
    """Book a fill on the state. qty = contracts for options, shares for BUY_SHARES."""
    if action == "BUY_SHARES":
        state.cash -= price * qty
        state.shares += qty
        state.basis, state.called_away = price, False
        return {"commission": 0.0, "reg": 0.0, "sec": 0.0, "cat": 0.0, "total": 0.0}
    side = "buy" if action == "BUY_TO_CLOSE" else "sell"
    fee = costs.fees(side, price, qty, cfg)
    if side == "sell":
        state.cash += price * CONTRACT * qty - fee["total"]
        state.option = Short(kind, strike, expiry, qty, price, day_date)
        state.target_expiry = None
    else:
        state.cash -= price * CONTRACT * qty + fee["total"]
        state.option = None
    return fee


# ---- decisions ------------------------------------------------------------------

def decide_exit(state, day, variant, cfg, market):
    """V1 only: buy to close at <= 50% of the sale price within the first third of
    the option's life (001 step 6). Otherwise hold."""
    o = state.option
    if o is None:
        return none("OK")
    if not variant.profit_take:
        return none("HAS_POSITION")
    life = (o.expiry - o.sold_on).days
    if (day.date - o.sold_on).days * 3 > life:
        return none("HAS_POSITION")
    quote = next((q for q in market.chain(day, o.expiry, o.kind) if abs(q.strike - o.strike) < 1e-9), None)
    if quote is None or quote.ask > 0.5 * o.premium:
        return none("HAS_POSITION")
    return Decision("BUY_TO_CLOSE", "PROFIT_TARGET_HIT", o.kind, o.strike, o.expiry, o.qty,
                    quote.ask, quote.mid, quote.delta)


def decide_entry(state, day, variant, cfg, market):
    if state.option is not None:
        return none("HAS_POSITION")
    if state.assigned_on == day.date:
        return none("ASSIGNED_TODAY")  # re-enter at the next close
    if state.shares == 0:
        if variant.wheel and state.called_away:
            return _option_entry(state, day, variant, cfg, market, "P")
        lots = math.floor((state.cash - cfg["cash_buffer"]) / (day.close * CONTRACT))
        if lots < 1:
            return none("INSUFFICIENT_CASH")
        return Decision("BUY_SHARES", "OK", qty=lots * CONTRACT, limit=day.close, mid=day.close)
    return _option_entry(state, day, variant, cfg, market, "C")


def _option_entry(state, day, variant, cfg, market, kind):
    if day.vol_warmup:
        return none("VOL_WARMUP")  # no option is priced before a past-only vol exists
    if variant.iv_theta and not day.vol_pct > variant.iv_theta:
        return none("IV_FILTER")  # NaN (< 252 days of history) also lands here
    weekly = variant.expiry_kind == "weekly" and kind == "C"
    dte = cfg["weekly_dte"] if weekly else cfg["monthly_dte"]
    slack = 0 if weekly else cfg["monthly_slack_days"]
    pick = market.pick(day.date, "weekly" if weekly else "monthly", dte, slack)
    if pick is None:
        return none("NO_EXPIRY")
    expiry, in_window = pick
    if variant.up_day_only:
        up = day.prev_close is not None and day.close > day.prev_close
        if not up:
            rolled = state.target_expiry is not None and state.target_expiry != expiry
            state.target_expiry = expiry
            return none("WINDOW_CLOSED_ROLL" if rolled else "NOT_UP_DAY")
    if day.next_earnings is not None and day.next_earnings <= expiry:
        return none("EARNINGS_BLACKOUT")
    chain = [q for q in market.chain(day, expiry, kind) if q.bid > 0]
    target = cfg["target_delta"] if kind == "C" else -cfg["target_delta"]
    picked = pick_strike([(q.strike, q.delta) for q in chain], target, cfg["tolerance"])
    if picked is None:
        return none("NO_STRIKE_IN_TOLERANCE")
    quote = next(q for q in chain if q.strike == picked[0])
    if kind == "C" and quote.strike < state.basis:
        above = sorted((q for q in chain if q.strike >= state.basis), key=lambda q: q.strike)
        if not above or above[0].delta < cfg["tolerance"][0]:
            return none("BASIS_ABOVE_BAND")
        quote = above[0]
    if kind == "C":
        qty = state.shares // CONTRACT
    else:
        qty = math.floor(state.cash / (quote.strike * CONTRACT))
        if qty < 1:
            return none("INSUFFICIENT_CASH")
    lo, hi = cfg["band"]
    return Decision("SELL_CALL" if kind == "C" else "SELL_PUT", "OK", kind, quote.strike, expiry, qty,
                    quote.bid, quote.mid, quote.delta, lo <= abs(quote.delta) <= hi, in_window)
