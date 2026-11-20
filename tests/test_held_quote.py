"""Item 083: the held option's strike is always inside the strike window the bot reads."""
import datetime as dt

from ccbot import expiries
from ccbot.bot import BrokerMarket
from ccbot.rules import Day, Short

DATE = dt.date(2026, 11, 19)
EXP = dt.date(2026, 12, 18)


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
