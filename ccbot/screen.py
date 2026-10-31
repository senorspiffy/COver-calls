"""Universe screen (001 step 3 + the 03 guardrail): run on every scan."""
import collections

import pandas as pd

from . import expiries
from .pricing import pick_strike
from .rules import CONTRACT

TESTS = ("NO_QUOTES", "PRICE_CAP", "SINGLE_NAME_CAP", "NO_EXPIRY", "NO_STRIKE_IN_TOLERANCE",
         "SPREAD", "OI", "EARNINGS")


def _reject(rows, cfg, capital, asof):
    """First failing test for one ticker's snapshot rows, or None if it passes."""
    if rows.empty:
        return "NO_QUOTES"
    first = rows.iloc[0]
    price = float(first["underlying_price"])
    if price * CONTRACT > capital - cfg["cash_buffer"]:
        return "PRICE_CAP"
    if first["asset_type"] != "etf" and price * CONTRACT > cfg["max_single_name_frac"] * capital:
        return "SINGLE_NAME_CAP"
    calls = rows[(rows["type"] == "C") & rows["symbol"].notna()]
    monthly = expiries.third_fridays(expiries.scan_calendar(asof))
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
    if pd.notna(q["oi"]) and q["oi"] < cfg["screen"]["min_oi"]:
        return "OI"  # model quotes carry no OI, so this test needs real/snapshot quotes
    earn = first["next_earnings"]
    if pd.notna(earn) and earn is not None and asof <= earn <= pick[0]:
        return "EARNINGS"
    return None


def feasible_universe(cfg, snapshots, cash, asof):
    """(passing tickers, {ticker: reject reason}) for cfg['universe'] on date `asof`.
    `cash` is the account's capital (cash + positions)."""
    snaps = snapshots[snapshots["ts"] == asof]
    passing, rejects = [], {}
    for t in cfg["universe"]:
        reason = _reject(snaps[snaps["underlying"] == t], cfg, cash, asof)
        if reason:
            rejects[t] = reason
        else:
            passing.append(t)
    return passing, rejects


def universe_banner(passing, rejects):
    if passing:
        return None
    counts = collections.Counter(rejects.values())
    top = max(counts, key=lambda r: (counts[r], -TESTS.index(r))) if counts else "NO_QUOTES"
    return f"UNIVERSE EMPTY: rule {top} has no passing ticker"
