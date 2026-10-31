"""Universe screen (001 step 3 + the 03 guardrail): run on every scan."""
import collections

import pandas as pd

from . import expiries
from .pricing import pick_strike
from .rules import CONTRACT

TESTS = ("NO_QUOTES", "CAPITAL_UNKNOWN", "PRICE_CAP", "SINGLE_NAME_CAP", "NO_EXPIRY", "NO_STRIKE_IN_TOLERANCE",
         "SPREAD", "OI_UNKNOWN", "OI", "EARNINGS_UNKNOWN", "EARNINGS")


def _reject(rows, cfg, capital, asof, calendar, require_oi):
    """First failing test for one ticker's snapshot rows, or None if it passes."""
    if rows.empty:
        return "NO_QUOTES"
    first = rows.iloc[0]
    price = float(first["underlying_price"])
    if capital != capital:   # NaN: equity can't be marked (missing.py derived.capital)
        return "CAPITAL_UNKNOWN"
    # written to fail closed: a NaN on either side never passes (014)
    if not price * CONTRACT <= capital - cfg["cash_buffer"]:
        return "PRICE_CAP"
    if first["asset_type"] != "etf" and not price * CONTRACT <= cfg["max_single_name_frac"] * capital:
        return "SINGLE_NAME_CAP"
    calls = rows[(rows["type"] == "C") & rows["symbol"].notna()]
    monthly = expiries.third_fridays(calendar)
    pick = expiries.pick_expiry(asof, monthly, cfg["monthly_dte"], cfg["monthly_slack_days"])
    if pick is None or pick[0] not in set(calls["expiry"]):
        return "NO_EXPIRY"
    chain = calls[(calls["expiry"] == pick[0]) & (calls["bid"] > 0)]
    picked = pick_strike(zip(chain["strike"], chain["delta"]), cfg["target_delta"], cfg["tolerance"])
    if picked is None:
        return "NO_STRIKE_IN_TOLERANCE"
    q = chain[chain["strike"] == picked[0]].iloc[0]
    if round(q["ask"] - q["bid"], 2) > cfg["screen"]["max_spread"] + 1e-9:
        return "SPREAD"
    if pd.isna(q["oi"]):
        if require_oi:
            return "OI_UNKNOWN"
    elif q["oi"] < cfg["screen"]["min_oi"]:
        return "OI"
    earn = first["next_earnings"]
    if first["asset_type"] != "etf" and pd.isna(earn):
        return "EARNINGS_UNKNOWN"
    if pd.notna(earn) and asof <= earn <= pick[0]:
        return "EARNINGS"
    return None


def feasible_universe(cfg, snapshots, cash, asof, calendar=None, require_oi=True):
    """(passing tickers, {ticker: reject reason}) for cfg['universe'] on date `asof`.
    `cash` is the account's capital (cash + positions). `calendar`: trading days for
    expiries (None: expiries.scan_calendar(asof)). Blank OI is OI_UNKNOWN unless
    require_oi is False (only a model-quote replay, whose quotes have no OI field)."""
    calendar = expiries.scan_calendar(asof) if calendar is None else calendar
    snaps = snapshots[snapshots["ts"] == asof]
    passing, rejects = [], {}
    for t in cfg["universe"]:
        reason = _reject(snaps[snaps["underlying"] == t], cfg, cash, asof, calendar, require_oi)
        if reason:
            rejects[t] = reason
        else:
            passing.append(t)
    return passing, rejects


def pass_history(scans, ticker, k=10):
    """(n_passed, n_seen) over the last <= k scan dicts (oldest -> newest). Information
    only: it never blocks an order. n_seen < k means the history is short."""
    last = scans[-k:]
    return sum(ticker in s.get("passing", []) for s in last), len(last)


def universe_banner(passing, rejects):
    if passing:
        return None
    counts = collections.Counter(rejects.values())
    top = max(counts, key=lambda r: (counts[r], -TESTS.index(r))) if counts else "NO_QUOTES"
    return f"UNIVERSE EMPTY: rule {top} has no passing ticker"
