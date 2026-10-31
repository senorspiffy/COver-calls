"""Expiry calendar built from trading dates (business days beyond the data)."""
import bisect
import datetime as dt
import functools
import json
from pathlib import Path

import pandas as pd

HOLIDAYS_PATH = Path(__file__).resolve().parents[1] / "config" / "holidays.json"


def _as_dates(dates):
    return [d.date() if hasattr(d, "date") and callable(d.date) else d for d in dates]


def business_days(start, end, holidays=None):
    """Mon-Fri dates; with `holidays` (iterable of dates), exchange holidays removed."""
    if holidays is None:
        return [d.date() for d in pd.bdate_range(start, end)]
    return [d.date() for d in pd.bdate_range(start, end, freq="C", holidays=list(holidays))]


@functools.cache
def load_holidays():
    """config/holidays.json (NYSE full-day closures and early closes), read once."""
    return json.loads(HOLIDAYS_PATH.read_text(encoding="utf-8"))


def extend(dates, until):
    """Trading dates plus business days after the last one, up to `until`."""
    dates = _as_dates(dates)
    return dates + business_days(dates[-1] + dt.timedelta(days=1), until)


def _move_back(target, dates, known):
    """`target` if it trades, else the prior trading day (same week). Looks back at most
    4 days, which covers one holiday (e.g. Good Friday -> Thursday)."""
    if target in known:
        return target
    prior = [d for d in dates if target - dt.timedelta(days=4) <= d < target]
    return prior[-1] if prior else None


def third_fridays(dates):
    dates = _as_dates(dates)
    known, out = set(dates), []
    y, m = dates[0].year, dates[0].month
    while (y, m) <= (dates[-1].year, dates[-1].month):
        first = dt.date(y, m, 1)
        fri = first + dt.timedelta(days=(4 - first.weekday()) % 7 + 14)
        if dates[0] <= fri <= dates[-1]:
            day = _move_back(fri, dates, known)
            if day:
                out.append(day)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def fridays(dates):
    dates = _as_dates(dates)
    known, out = set(dates), []
    fri = dates[0] + dt.timedelta(days=(4 - dates[0].weekday()) % 7)
    while fri <= dates[-1]:
        day = _move_back(fri, dates, known)
        if day:
            out.append(day)
        fri += dt.timedelta(days=7)
    return out


def pick_expiry(today, expiries, dte_range, slack=0):
    """(expiry, in_window) for the first expiry (sorted list) with DTE in dte_range.
    If none and slack > 0: the expiry nearest the window within `slack` days of its
    edges (ties go to the later one), with in_window=False. Otherwise None."""
    lo, hi = dte_range
    future = []
    for e in expiries[bisect.bisect_right(expiries, today):]:
        dte = (e - today).days
        if dte > hi + slack:
            break
        if lo <= dte <= hi:
            return e, True
        future.append((e, dte))
    near = [(lo - dte if dte < lo else dte - hi, -dte, e) for e, dte in future if dte >= lo - slack]
    if not near:
        return None
    return min(near)[2], False


def scan_calendar(today, days=120):
    """Calendar for a live/paper scan: NYSE trading days around `today`. Raises
    ValueError outside the holiday table; it never falls back to Mon-Fri."""
    table = load_holidays()
    lo, hi = (dt.date.fromisoformat(d) for d in table["covers"])
    start, end = today - dt.timedelta(days=35), today + dt.timedelta(days=days)
    if start < lo or end > hi:
        raise ValueError(f"holiday table covers {lo}..{hi}; add NYSE dates for {start.year if start < lo else end.year} "
                         f"to {HOLIDAYS_PATH.name} (source {table['source']})")
    return business_days(start, end, table["holidays"])
