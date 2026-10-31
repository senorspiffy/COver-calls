"""Paper account with up to `max_positions` underlyings sharing one cash balance (item 024).

Each held underlying is a rules.State "sleeve" whose own cash is kept at 0. To run a
rules helper (decide_entry, apply_fill, settle_day) on a sleeve, lend it a cash budget
with `lend`; whatever the helper adds or spends is booked back to the shared cash.
The backtest still runs one State on one series, so the two share every rule.
"""
from contextlib import contextmanager
from dataclasses import dataclass, field

from .rules import State, equity as sleeve_equity


@dataclass
class Portfolio:
    cash: float
    positions: dict = field(default_factory=dict)   # ticker -> State (cash always 0 at rest)

    def get(self, ticker):
        """The sleeve for `ticker`, or an empty one (not stored) if none is held."""
        return self.positions.get(ticker) or State(cash=0.0, ticker=ticker)

    def held(self, wheel=False):
        """Tickers that occupy a slot: shares or an open option; with `wheel`, also a ticker
        whose shares were called away and now waits to sell a put (variant V5)."""
        return sorted(t for t, s in self.positions.items() if s.shares or s.option or (wheel and s.called_away))

    def prune(self):
        for t in [t for t, s in self.positions.items() if not (s.shares or s.option or s.called_away)]:
            del self.positions[t]

    @contextmanager
    def lend(self, ticker, budget):
        """Yield the sleeve for `ticker` holding `budget` cash; book the change to self.cash."""
        sleeve = self.positions.setdefault(ticker, State(cash=0.0, ticker=ticker))
        sleeve.cash = budget
        try:
            yield sleeve
        finally:
            self.cash += sleeve.cash - budget
            sleeve.cash = 0.0
            self.prune()

    def to_dict(self):
        return {"cash": self.cash, "positions": {t: s.to_dict() for t, s in sorted(self.positions.items())}}

    @classmethod
    def from_dict(cls, d):
        if "positions" not in d:   # a ledger saved before item 024: one State
            st = State.from_dict(d)
            p = cls(cash=st.cash)
            if st.shares or st.option or st.called_away:
                st.cash = 0.0
                p.positions[st.ticker] = st
            return p
        return cls(d["cash"], {t: State.from_dict(s) for t, s in d["positions"].items()})


def portfolio_equity(portfolio, days, cfg):
    """Cash + each sleeve's shares at the day's close − its short option at BS mid.
    `days`: ticker -> rules.Day; a held ticker missing from `days` raises KeyError (never priced at 0)."""
    return portfolio.cash + sum(sleeve_equity(portfolio.positions[t], days[t], cfg) for t in portfolio.held())


def entry_budget(portfolio, capital, asset_type, cfg):
    """Cash a new position may use: all of it for an ETF; for a single stock at most
    max_single_name_frac × capital (plus the buffer decide_entry keeps back), so
    shares ≤ that cap and the account keeps ≥ cash_buffer (001 step 1 and 9(a))."""
    if asset_type == "etf":
        return portfolio.cash
    return min(portfolio.cash, cfg["max_single_name_frac"] * capital + cfg["cash_buffer"])
