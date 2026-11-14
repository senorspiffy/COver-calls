"""Real-quote covered-call test (item 061). Research only; nothing here trades.

Question: has selling calls on our candidate stocks beaten simply holding them (and has BXM
beaten SPY) after real bid/ask fills and costs, tested walk-forward with no lookahead?

Inputs (scripts/fetch_real_data.py writes them; DoltHub post-no-preference + Cboe):
  data/real/prices/T.csv      date, close (unadjusted)       data/real/dividends/T.csv  ex_date, amount
  data/real/splits/T.csv      ex_date, to_factor, for_factor data/real/earnings/T.csv   date
  data/real/options/T.csv.gz  date, expiration, strike, bid, ask, vol (IV), delta (calls only)
  data/real/volhist/T.csv     date, iv_current, hv_current   data/real/BXM_History.csv
  config/default.json (fees, r, target delta, tolerance, slack, cash) and config/tickers.json
  (asset_type). What happens when each input is absent: REALTEST_MISSING.

Simulation (one ticker; both arms fully invested with fractional shares, see simulate()):
  * Entry follows the bot (rules._option_entry, 061/04): expiry from expiries.third_fridays on
    the trading calendar + pick_expiry (30-45 DTE, config slack), which must be quoted that day
    (NO_EXPIRY); strike from pricing.pick_strike with the config tolerance; the cost-basis floor;
    EARNINGS_UNKNOWN for a stock with no known next earnings date; no call held through an
    earnings date (a <= e <= expiry, like screen._reject).
  * A call is only ever sold on a day that has a real quote for it (a snapshot day), at the bid
    ("bid" fills) or at bid + 25% of the spread ("quarter" fills). Buy-backs pay the ask (or
    ask - 25% of spread). Mid fills are reported only to show what the spread costs.
    Fees: costs.fees with the config's fee table.
  * Expiry: close > strike -> shares called away at the strike and bought back at the close
    (+1 cent/share slippage), so both arms always hold the same shares; the gap is cash.
    The re-buy happens the same day (the bot waits for the next close: ASSIGNED_TODAY).
  * Day before an ex-dividend date: an in-the-money call whose remaining time value
    (Black-Scholes from the sold contract's IV, APPROXIMATE) is below the dividend is assumed
    exercised early, so the dividend is lost.
  * On days without a quote for the open contract its value is Black-Scholes from the last
    quoted IV of that contract (APPROXIMATE; affects the daily curve/drawdown, not cash P&L).
  * Grid-only variants (not bot rules): the 14-24 DTE window (any quoted expiry), +/-0.075
    tolerance around targets other than the config's, and rolling when delta > 0.70.
Nothing on day t uses data after day t: a config's choices use only that day's quotes,
and walk-forward picks each 6-month block's config from the 24 months before it.
Earnings dates are read as if known in advance (APPROXIMATE: no record of publication dates).
"""
import argparse
import collections
import itertools
import json
import math
import random
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import costs, expiries
from .config import load_config
from .expiries import pick_expiry
from .pricing import bs_price, pick_strike

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "default.json"
TICKERS_PATH = ROOT / "config" / "tickers.json"
STOCK_SLIP = 0.01           # $/share paid when re-buying shares after assignment
GRID_TOL = 0.075            # grid-only: tolerance half-width around a target that is not the config's
EARNINGS_GAP_WARN = 120     # days between consecutive earnings dates counted as a data-hole warning
SUB_3C = 0.03               # information only: sales below 3 cents are counted, not blocked (bot has no floor)

# One row per input (item 061/04, RI-002): what happens when it is absent. The code below
# uses these texts; tests/test_realtest.py::test_realtest_missing_lists_every_input checks that
# every `root / "<input>"` read in load_ticker/bxm_vs_spy has a row here and a drop test.
REALTEST_MISSING = {
    "prices": "ticker skipped: prices: not supplied",
    "options": "ticker skipped: options: not supplied",
    "dividends": "ticker skipped: DIVIDEND_UNKNOWN: not supplied",
    "splits": "ticker skipped: splits: not supplied",
    "earnings": "EARNINGS_UNKNOWN on every day for a stock (no call sold); ETF unaffected",
    "volhist": "atm_iv_minus_next30d_rv NaN, atm_na_reason 'volhist: not supplied'",
    "BXM_History.csv": "bxm_vs_spy.error 'BXM_History.csv: not supplied'",
    "asset_type": "not in config/tickers.json (SPY: etf) -> treated as a stock (earnings required), warning",
}


# ---------------------------------------------------------------- loading

def _read(path):
    """None when the file is absent; an empty frame when it is 0 bytes or has no columns."""
    p = Path(path)
    if not p.exists():
        return None
    if p.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(p, compression="gzip" if p.suffix == ".gz" else None)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    raise KeyError(f"none of {names} in {list(df.columns)}")


def _asset_type(tk, facts):
    """(asset_type, warning or None). Unknown -> 'stock', which needs earnings dates (fails closed)."""
    a = (facts.get(tk) or {}).get("asset_type")
    if a:
        return a, None
    if tk == "SPY":
        return "etf", None
    return "stock", f"asset_type: {REALTEST_MISSING['asset_type']}"


@dataclass
class TickerData:
    ticker: str
    close: pd.Series                 # date-indexed unadjusted close
    divs: dict                       # ex_date -> $ per share
    splits: dict                     # ex_date -> share multiplier (2.0 for 2-for-1)
    earnings: list                   # sorted dates
    chain: dict                      # date -> DataFrame(expiration, strike, bid, ask, iv, delta)
    volhist: pd.DataFrame            # date-indexed iv, hv (may be empty: see volhist_na)
    asset_type: str                  # "etf" skips the earnings checks, like the bot
    volhist_na: str                  # why volhist is empty ("" when it has rows)
    quote_rows_dropped: int          # rows dropped for non-finite/non-positive iv or non-finite delta
    earnings_gaps: int               # consecutive earnings dates > EARNINGS_GAP_WARN days apart
    warnings: list = field(default_factory=list)
    quotes: dict = field(default_factory=dict)   # (date, expiration, strike) -> (bid, ask, iv, delta)


def _load_facts():
    if not TICKERS_PATH.exists():
        return {}
    return {t: v for t, v in json.loads(TICKERS_PATH.read_text(encoding="utf-8")).items() if not t.startswith("_")}


def load_ticker(root, tk, facts=None):
    """One ticker's data. Raises FileNotFoundError/ValueError (run() records it as skipped) for
    each REALTEST_MISSING 'ticker skipped' row. `facts`: config/tickers.json entries (None: read it)."""
    root = Path(root)
    facts = _load_facts() if facts is None else facts
    warnings = []
    px = _read(root / "prices" / f"{tk}.csv")
    if px is None:
        raise FileNotFoundError(REALTEST_MISSING["prices"].removeprefix("ticker skipped: "))
    if px.empty:
        raise ValueError(f"prices: empty file for {tk}")
    px["date"] = pd.to_datetime(px[_col(px, "date")]).dt.date
    close = px.set_index("date")[_col(px, "close")].astype(float).sort_index()
    close = close[~close.index.duplicated()]
    if not np.isfinite(close.values).all() or (close.values <= 0).any():
        raise ValueError(f"prices: non-finite or non-positive close for {tk}")

    dv = _read(root / "dividends" / f"{tk}.csv")
    if dv is None:
        raise FileNotFoundError(REALTEST_MISSING["dividends"].removeprefix("ticker skipped: "))
    divs = {}
    if not dv.empty:
        for d, a in zip(pd.to_datetime(dv[_col(dv, "ex_date", "date")]).dt.date, dv[_col(dv, "amount", "dividend")]):
            a = float(a)
            if not math.isfinite(a):
                raise ValueError(f"DIVIDEND_UNKNOWN: amount on {d} is not a number")
            if a > 0:
                divs[d] = divs.get(d, 0.0) + a

    sp = _read(root / "splits" / f"{tk}.csv")
    if sp is None:
        raise FileNotFoundError(REALTEST_MISSING["splits"].removeprefix("ticker skipped: "))
    splits = {}
    if not sp.empty:
        to = _col(sp, "to_factor", "numerator")
        fr = _col(sp, "for_factor", "denominator")
        for d, t, f in zip(pd.to_datetime(sp[_col(sp, "ex_date", "date")]).dt.date, sp[to], sp[fr]):
            t, f = float(t), float(f)
            if not (math.isfinite(t) and math.isfinite(f) and t > 0 and f > 0):
                raise ValueError(f"splits: factor on {d} is not a positive number")
            if t / f != 1:
                splits[d] = t / f

    er = _read(root / "earnings" / f"{tk}.csv")
    if er is None:
        warnings.append("earnings: not supplied (EARNINGS_UNKNOWN for a stock)")
        earnings = []
    else:
        earnings = sorted(set(pd.to_datetime(er[_col(er, "date")]).dt.date)) if not er.empty else []
    gaps = sum((b - a).days > EARNINGS_GAP_WARN for a, b in zip(earnings, earnings[1:]))
    if gaps:
        warnings.append(f"earnings: {gaps} gap(s) > {EARNINGS_GAP_WARN} days between dates")

    oc = _read(root / "options" / f"{tk}.csv.gz")
    if oc is None:
        raise FileNotFoundError(REALTEST_MISSING["options"].removeprefix("ticker skipped: "))
    chain, quotes, dropped = {}, {}, 0
    if not oc.empty:
        oc = pd.DataFrame({
            "date": pd.to_datetime(oc[_col(oc, "date")]).dt.date,
            "expiration": pd.to_datetime(oc[_col(oc, "expiration")]).dt.date,
            "strike": oc[_col(oc, "strike")].astype(float),
            "bid": oc[_col(oc, "bid")].astype(float),
            "ask": oc[_col(oc, "ask")].astype(float),
            "iv": oc[_col(oc, "vol", "iv", "implied_volatility")].astype(float),
            "delta": oc[_col(oc, "delta")].astype(float),
        })
        good = np.isfinite(oc.iv) & (oc.iv > 0) & np.isfinite(oc.delta)
        dropped = int((~good).sum())
        if dropped:
            warnings.append(f"options: {dropped} quote rows dropped (iv not finite/positive or delta not finite)")
        oc = oc[good]
        oc = oc[(oc.ask > 0) & (oc.bid >= 0) & (oc.ask >= oc.bid)]
        chain = {d: g.reset_index(drop=True) for d, g in oc.groupby("date")}
        quotes = {(d, e, round(k, 3)): (b, a, v, dl) for d, e, k, b, a, v, dl in
                  zip(oc.date, oc.expiration, oc.strike, oc.bid, oc.ask, oc.iv, oc.delta)}

    vh = _read(root / "volhist" / f"{tk}.csv")
    vh_na = ""
    if vh is None:
        vh, vh_na = pd.DataFrame(), "volhist: not supplied"
    elif vh.empty:
        vh_na = "volhist: empty file"
    else:
        vh = pd.DataFrame({"date": pd.to_datetime(vh[_col(vh, "date")]).dt.date,
                           "iv": vh[_col(vh, "iv_current")].astype(float),
                           "hv": vh[_col(vh, "hv_current")].astype(float)}).set_index("date").sort_index()
    asset, aw = _asset_type(tk, facts)
    if aw:
        warnings.append(aw)
    td = TickerData(tk, close, divs, splits, earnings, chain, vh, asset_type=asset, volhist_na=vh_na,
                    quote_rows_dropped=dropped, earnings_gaps=gaps, warnings=warnings, quotes=quotes)
    _check_units(td)
    return td


def _check_units(td):
    """Prices and strikes must be on the same (unadjusted) basis: the median distance from
    the close to the nearest quoted strike should be small. Flags split-adjusted prices."""
    gaps = []
    for d, g in list(td.chain.items())[::10]:
        c = td.close.get(d)
        if c:
            gaps.append(float((g.strike - c).abs().min() / c))
    if gaps and float(np.median(gaps)) > 0.15:
        td.warnings.append(f"strikes far from closes (median gap {np.median(gaps):.0%}): price basis mismatch?")


def eligible(td, start, min_years):
    """Raises ValueError when a ticker has no quotes from `start`, or under `min_years` of them."""
    ch = [d for d in td.chain if start is None or d >= start]
    if not ch:
        raise ValueError("no option quotes")
    if (max(ch) - min(ch)).days / 365.25 < min_years:
        raise ValueError(f"option quotes only {min(ch)} to {max(ch)} (< {min_years} years)")


# ---------------------------------------------------------------- simulation

@dataclass(frozen=True)
class Config:
    delta: float                     # target call delta
    dte: tuple                       # days-to-expiry window
    skip_earnings: bool = True       # don't hold a call through an earnings date
    manage: str = "hold"             # hold | take50 (buy back at 50% profit in the first third of life) | roll (grid only: roll when delta > 0.70)
    fill: str = "bid"                # bid | quarter | mid

    @property
    def name(self):
        e = "noE" if self.skip_earnings else "E"
        return f"d{self.delta:.3f}_dte{self.dte[0]}-{self.dte[1]}_{e}_{self.manage}_{self.fill}"


def bot_rule(cfg):
    """The bot's call rule from the config: target delta, monthly DTE window, skip earnings, hold, bid."""
    return Config(float(cfg["target_delta"]), tuple(cfg["monthly_dte"]))


DEFAULT_CFG = load_config(CONFIG_PATH)
BOT_RULE = bot_rule(DEFAULT_CFG)
GRID = [Config(d, w, e, m, "bid") for d, w, e, m in itertools.product(
    (0.15, 0.20, 0.275, 0.35, 0.45), ((14, 24), (30, 45)), (True, False), ("hold", "take50", "roll"))]
# No 5-9 day window: DoltHub keeps ~3 expiries per snapshot (e.g. 16/30/65 days) and has a 5-9 day
# expiry on 1 of 1,272 BAC snapshot days, so a weekly variant would never trade and would just
# copy buy-and-hold (it got picked 3 times in walk-forward before this was removed).

ENTRY_CODES = ("OK", "NO_EXPIRY", "EARNINGS_UNKNOWN", "EARNINGS_BLACKOUT", "NO_STRIKE_IN_TOLERANCE", "BASIS_ABOVE_BAND")


@dataclass
class Quote:
    bid: float
    ask: float
    iv: float
    delta: float


def sell_px(row, fill):
    sp = row.ask - row.bid
    return {"bid": row.bid, "quarter": row.bid + 0.25 * sp, "mid": row.bid + 0.5 * sp}[fill]


def buy_px(row, fill):
    sp = row.ask - row.bid
    return {"bid": row.ask, "quarter": row.ask - 0.25 * sp, "mid": row.ask - 0.5 * sp}[fill]


def opt_fees(px, mult, sell, cfg):
    """costs.fees for options covering `mult` shares (fractional contracts at the per-contract rate)."""
    return costs.fees("sell" if sell else "buy", px, mult / 100.0, cfg)["total"]


@dataclass
class Trade:
    open_date: date
    expiration: date
    strike: float
    premium: float           # per share, at the fill
    iv: float
    delta: float
    spot: float
    in_window: bool          # expiry inside the DTE window (False: picked with the slack days)
    qty: float               # shares covered
    close_date: date = None
    close_cost: float = float("nan")  # per share paid to close (buy-back or intrinsic at assignment; 0 when expired)
    outcome: str = ""        # expired | assigned | early_assigned | bought_back | rolled ("" = still open)
    rv_life: float = float("nan")   # realized vol from open to close (annualised)

    @property
    def pnl(self):
        return self.premium - self.close_cost


def _tolerance(rule, cfg):
    """(target, tolerance): the config's for the bot target, +/-GRID_TOL otherwise (grid only)."""
    if abs(rule.delta - cfg["target_delta"]) < 1e-9:
        return cfg["target_delta"], tuple(cfg["tolerance"])
    return rule.delta, (rule.delta - GRID_TOL, rule.delta + GRID_TOL)


def _pick(g, today, rule, cfg, monthly, basis):
    """(row with an `in_window` field, "OK") or (None, code), following rules._option_entry.
    Expiry: for the config's monthly window, expiries.pick_expiry over `monthly` (third Fridays of
    the trading calendar, holiday Fridays moved back) with the config slack; that expiry must be
    quoted today, else NO_EXPIRY (screen._reject). Other windows (grid only): any quoted expiry.
    Strike: pricing.pick_strike among bid > 0, then the cost-basis floor (rules.py L308-312)."""
    if not math.isfinite(basis):
        raise ValueError(f"cost basis {basis} is not a number")
    quoted = sorted(g.expiration.unique())
    slack = cfg["monthly_slack_days"]
    if rule.dte == tuple(cfg["monthly_dte"]):
        picked = pick_expiry(today, monthly, rule.dte, slack)
        if picked is None or picked[0] not in set(quoted):
            return None, "NO_EXPIRY"
    else:
        picked = pick_expiry(today, quoted, rule.dte, slack)
        if picked is None:
            return None, "NO_EXPIRY"
    ok = g[(g.expiration == picked[0]) & (g.bid > 0.0)]
    target, tol = _tolerance(rule, cfg)
    s = pick_strike(list(zip(ok.strike, ok.delta)), target, tol)
    if s is None:
        return None, "NO_STRIKE_IN_TOLERANCE"
    row = ok[ok.strike == s[0]].iloc[0]
    if row.strike < basis:
        above = ok[ok.strike >= basis].sort_values("strike")
        if above.empty or not (above.iloc[0].delta >= tol[0]):
            return None, "BASIS_ABOVE_BAND"
        row = above.iloc[0]
    row = row.copy()
    row["in_window"] = bool(picked[1])
    return row, "OK"


def _earnings_between(td, a, b):
    return any(a <= e <= b for e in td.earnings)


def _earnings_known(td, d):
    """A next earnings date on or after d exists (the bot's earnings_known for a stock)."""
    return bool(td.earnings) and td.earnings[-1] >= d


def _realized_vol(close, a, b):
    s = close[(close.index >= a) & (close.index <= b)]
    if len(s) < 4:
        return float("nan")
    r = np.diff(np.log(s.values))
    return float(np.std(r, ddof=1) * math.sqrt(252))


def simulate(td, rule, cfg, start=None, end=None):
    """Returns (daily DataFrame[cc, bh] starting at 1.0, trades list). df.attrs["counts"] holds the
    entry codes per attempted day (ENTRY_CODES) and the data counts (snap_days, ...).

    Both arms stay fully invested with fractional shares, like the BXM index: dividends are
    reinvested at the ex-date close in both; in the covered-call arm the premium, buy-back costs
    and assignment proceeds are also turned back into shares at that day's close, and each call
    covers every share held when it is sold. Real accounts trade 100-share lots (see caveats).
    Cost basis (for the floor) = the close the arm last bought shares at: the first close, then the
    re-buy close + slip after each assignment; split-adjusted like the strikes."""
    r_rate = float(cfg["r"])
    days = [d for d in td.close.index if (start is None or d >= start) and (end is None or d <= end)]
    snaps = sorted(d for d in td.chain if (start is None or d >= start) and (end is None or d <= end))
    if not snaps:
        raise ValueError(f"{td.ticker}: no option quotes")
    days = [d for d in days if d >= snaps[0]]
    if not days:
        raise ValueError(f"{td.ticker}: no closes on or after the first quote day {snaps[0]}")
    calendar = expiries.extend(td.close.index, td.close.index[-1] + timedelta(days=90))
    monthly = expiries.third_fridays(calendar)
    c0 = float(td.close[days[0]])
    sh_cc = sh_bh = 1.0 / c0          # $1 in each arm
    basis = c0
    open_t = None
    last_iv = None
    trades, rows = [], []
    codes = collections.Counter({k: 0 for k in ENTRY_CODES})
    sub3c = 0
    for i, d in enumerate(days):
        c = float(td.close[d])
        cash = 0.0                       # covered-call cash flows today, reinvested at the close
        if d in td.splits:               # OCC-style adjustment keeps the position whole
            f = td.splits[d]
            sh_cc *= f
            sh_bh *= f
            basis /= f
            if open_t:
                open_t.strike /= f
                open_t.premium /= f
                open_t.qty *= f
        if d in td.divs:
            sh_bh += td.divs[d] * sh_bh / c
            cash += td.divs[d] * sh_cc
        g = td.chain.get(d)
        nxt = days[i + 1] if i + 1 < len(days) else None

        # manage an open call on a quote day
        if open_t and g is not None and rule.manage != "hold" and d < open_t.expiration:
            q = td.quotes.get((d, open_t.expiration, round(open_t.strike, 3)))
            if q is not None:
                q = Quote(*q)
                last_iv = q.iv
                ask = buy_px(q, rule.fill)
                life = (open_t.expiration - open_t.open_date).days
                early = (d - open_t.open_date).days * 3 <= life          # rules.decide_exit: first third
                if (rule.manage == "take50" and early and ask <= 0.5 * open_t.premium) or \
                   (rule.manage == "roll" and q.delta > 0.70 and (open_t.expiration - d).days <= 21):
                    open_t.close_cost = ask
                    open_t.close_date = d
                    open_t.outcome = "bought_back" if rule.manage == "take50" else "rolled"
                    open_t.rv_life = _realized_vol(td.close, open_t.open_date, d)
                    cash -= ask * open_t.qty + opt_fees(ask, open_t.qty, False, cfg)
                    trades.append(open_t)
                    open_t = None

        # early exercise the day before ex-dividend (approximate): we lose tomorrow's dividend
        if open_t and nxt in td.divs and c > open_t.strike and nxt <= open_t.expiration:
            assert last_iv is not None and math.isfinite(last_iv), "last_iv is set from a finite IV at open"
            T = max((open_t.expiration - d).days, 1) / 365
            tv = bs_price(c, open_t.strike, T, r_rate, 0.0, last_iv, "C") - (c - open_t.strike)
            if tv < td.divs[nxt]:
                open_t.close_cost = c - open_t.strike
                open_t.close_date = d
                open_t.outcome = "early_assigned"
                open_t.rv_life = _realized_vol(td.close, open_t.open_date, d)
                cash += (open_t.strike - c - STOCK_SLIP) * open_t.qty   # sold at K, re-bought at close
                cash -= td.divs[nxt] * open_t.qty                       # dividend we no longer get
                basis = c + STOCK_SLIP
                trades.append(open_t)
                open_t = None

        # expiry (or the last trading day on/before it)
        if open_t and (d >= open_t.expiration or (nxt is not None and nxt > open_t.expiration)):
            open_t.close_date = d
            open_t.rv_life = _realized_vol(td.close, open_t.open_date, d)
            if c > open_t.strike:
                open_t.close_cost = c - open_t.strike
                open_t.outcome = "assigned"
                cash += (open_t.strike - c - STOCK_SLIP) * open_t.qty
                basis = c + STOCK_SLIP
            else:
                open_t.close_cost = 0.0
                open_t.outcome = "expired"
            trades.append(open_t)
            open_t = None

        # open a new call on a quote day
        if open_t is None and g is not None and nxt is not None:
            if rule.skip_earnings and td.asset_type != "etf" and not _earnings_known(td, d):
                r, code = None, "EARNINGS_UNKNOWN"
            else:
                r, code = _pick(g, d, rule, cfg, monthly, basis)
                if code == "OK" and rule.skip_earnings and _earnings_between(td, d, r.expiration):
                    r, code = None, "EARNINGS_BLACKOUT"
            codes[code] += 1
            if code == "OK":
                px = float(sell_px(r, rule.fill))
                sub3c += px < SUB_3C
                qty = sh_cc + cash / c
                open_t = Trade(d, r.expiration, float(r.strike), px, float(r.iv), float(r.delta), c,
                               bool(r.in_window), qty)
                last_iv = float(r.iv)
                cash += px * qty - opt_fees(px, qty, True, cfg)

        sh_cc += cash / c
        # mark to market
        liab = 0.0
        if open_t:
            q = td.quotes.get((d, open_t.expiration, round(open_t.strike, 3)))
            if q is not None:
                last_iv = float(q[2])
                liab = float((q[0] + q[1]) / 2)
            else:
                assert last_iv is not None and math.isfinite(last_iv), "last_iv is set from a finite IV at open"
                T = max((open_t.expiration - d).days, 0) / 365
                liab = bs_price(c, open_t.strike, T, r_rate, 0.0, last_iv, "C")
            liab *= open_t.qty
        rows.append((d, sh_cc * c - liab, sh_bh * c))
    df = pd.DataFrame(rows, columns=["date", "cc", "bh"]).set_index("date")
    closes = set(td.close.index)
    df.attrs["counts"] = {
        **{f"rej_{k}": int(v) for k, v in codes.items()},
        "open_at_end": int(open_t is not None),          # rej_OK = calls_sold + open_at_end
        "in_window": sum(t.in_window for t in trades),   # closed calls, like calls_sold
        "slack": sum(not t.in_window for t in trades),
        "sub_3c_sales": int(sub3c),
        "snap_days": len(snaps),
        "snap_days_no_close": sum(d not in closes for d in snaps),
    }
    return df, trades


# ---------------------------------------------------------------- metrics

def cagr(eq):
    n = (eq.index[-1] - eq.index[0]).days / 365.25
    return float(eq.iloc[-1] ** (1 / n) - 1) if n > 0 and eq.iloc[-1] > 0 else float("nan")


def max_dd(eq):
    return float((eq / eq.cummax() - 1).min())


NAN = float("nan")


def iv_vs_rv(td, trades):
    """Per sold call: the IV we sold at vs the vol that actually happened over its life; and the
    ATM IV vs the next 30 days' realized vol (NaN with atm_na_reason when it can't be computed)."""
    t = [x for x in trades if not math.isnan(x.rv_life)]
    out = {"sold_iv": NAN, "realized": NAN, "iv_minus_rv": NAN, "pct_iv_above_rv": NAN,
           "atm_iv_minus_next30d_rv": NAN, "atm_pct_iv_above_rv": NAN, "atm_na_reason": ""}
    if t:
        gap = np.array([x.iv - x.rv_life for x in t])
        out.update({"sold_iv": float(np.mean([x.iv for x in t])), "realized": float(np.mean([x.rv_life for x in t])),
                    "iv_minus_rv": float(gap.mean()), "pct_iv_above_rv": float((gap > 0).mean())})
    if td.volhist.empty:
        out["atm_na_reason"] = td.volhist_na
        return out
    vh = td.volhist.dropna()
    fwd = []
    for d, iv in vh.iv.items():
        rv = _realized_vol(td.close, d, d + timedelta(days=30))
        if not math.isnan(rv) and d + timedelta(days=30) <= td.close.index[-1]:
            fwd.append(iv - rv)
    if fwd:
        out["atm_iv_minus_next30d_rv"] = float(np.mean(fwd))
        out["atm_pct_iv_above_rv"] = float(np.mean(np.array(fwd) > 0))
    else:
        out["atm_na_reason"] = "volhist: no day with 30 days of later closes"
    return out


def fits_account(td, price, cfg):
    """One 100-share lot fits the default account: price x 100 <= cash - buffer, and for a stock
    <= max_single_name_frac x cash (screen._reject PRICE_CAP / SINGLE_NAME_CAP). NaN never fits."""
    lot = price * costs.CONTRACT
    if not lot <= cfg["cash"] - cfg["cash_buffer"]:
        return False
    return td.asset_type == "etf" or lot <= cfg["max_single_name_frac"] * cfg["cash"]


def summarize(td, rule, df, trades, cfg):
    n = len(trades)
    called = sum(t.outcome in ("assigned", "early_assigned") for t in trades)
    years = (df.index[-1] - df.index[0]).days / 365.25
    first, last = float(td.close[df.index[0]]), float(td.close[df.index[-1]])
    return {
        "ticker": td.ticker, "config": rule.name, "start": str(df.index[0]), "end": str(df.index[-1]),
        "years": round(years, 2), "cc_cagr": cagr(df.cc), "bh_cagr": cagr(df.bh),
        "excess_cagr": cagr(df.cc) - cagr(df.bh), "cc_maxdd": max_dd(df.cc), "bh_maxdd": max_dd(df.bh),
        "calls_sold": n, "called_away": called, "called_away_pct": called / n if n else NAN,
        "early_assigned": sum(t.outcome == "early_assigned" for t in trades),
        "premium_yield_per_yr": float(np.sum([t.premium / t.spot for t in trades]) / years) if years > 0 else NAN,
        "option_pnl_per_share": sum(t.pnl for t in trades),
        "option_win_rate": float(np.mean([t.pnl > 0 for t in trades])) if n else NAN,
        **iv_vs_rv(td, trades), **df.attrs["counts"],
        "quote_rows_dropped": td.quote_rows_dropped, "earnings_gaps_gt120": td.earnings_gaps,
        "lot_cost_first": 100 * first, "lot_cost_last": 100 * last,
        "fits_3k": fits_account(td, last, cfg), "asset_type": td.asset_type,
        "warnings": "; ".join(td.warnings),
    }


# ---------------------------------------------------------------- walk-forward

def six_month_blocks(first, last, train_months=24, test_months=6):
    out = []
    t0 = pd.Timestamp(first) + pd.DateOffset(months=train_months)
    while t0.date() < last:
        t1 = t0 + pd.DateOffset(months=test_months)
        out.append(((t0 - pd.DateOffset(months=train_months)).date(), t0.date(), min(t1.date(), last)))
        t0 = t1
    return out


def walk_forward(curves, configs):
    """curves[cfg.name][ticker] = daily DataFrame(cc, bh). For each 6-month block pick the config
    with the best mean (cc - bh) log growth over the trailing 24 months across all tickers,
    then use that config's daily returns in the block. Pooled pick = fewer chances to overfit.
    A block with no ticker having > 200 training days gets picked None ("no training data") and
    no out-of-sample returns. Returns come from pct_change on the full curve, sliced afterwards,
    so each block keeps its first day.
    Returns (oos daily returns per ticker DataFrame, bh daily returns, picks list)."""
    any_cfg = next(iter(curves.values()))
    first = min(df.index[0] for df in any_cfg.values())
    last = max(df.index[-1] for df in any_cfg.values())
    rets = {name: {tk: (df.cc.pct_change(), df.bh.pct_change()) for tk, df in per.items()}
            for name, per in curves.items()}
    picks, oos, bh = [], {}, {}
    for tr0, te0, te1 in six_month_blocks(first, last):
        def score(name):
            s = []
            for tk, df in curves[name].items():
                w = df[(df.index >= tr0) & (df.index < te0)]
                if len(w) > 200:
                    s.append(math.log(w.cc.iloc[-1] / w.cc.iloc[0]) - math.log(w.bh.iloc[-1] / w.bh.iloc[0]))
            return np.mean(s) if s else -np.inf
        scores = {c.name: score(c.name) for c in configs}
        best = max(scores, key=scores.get)
        if scores[best] == -np.inf:
            picks.append({"train_from": str(tr0), "test_from": str(te0), "test_to": str(te1), "picked": None,
                          "train_excess_logret": NAN, "reason": "no training data"})
            continue
        picks.append({"train_from": str(tr0), "test_from": str(te0), "test_to": str(te1), "picked": best,
                      "train_excess_logret": float(scores[best]), "reason": ""})
        for tk, (rc, rb) in rets[best].items():
            m = (rc.index >= te0) & (rc.index < te1)
            oos.setdefault(tk, []).append(rc[m].dropna())
            bh.setdefault(tk, []).append(rb[m].dropna())
    oos = pd.DataFrame({k: pd.concat(v) for k, v in oos.items()})
    bh = pd.DataFrame({k: pd.concat(v) for k, v in bh.items()})
    return oos, bh, picks


def monte_carlo(ret_cc, ret_bh, n_paths=10000, names=2, horizon=252, block=21, seed=7):
    """Random 2-stock equal-weight portfolios, block-bootstrapped 1-year paths, on the days both
    arms of both names have a return (joint dropna; nothing is filled). Returns percentiles of
    1-year return and max drawdown for both arms plus paths_used, or {"na": reason}."""
    rng = random.Random(seed)
    cols = [c for c in ret_cc.columns if ret_cc[c].notna().sum() > 500 and ret_bh[c].notna().sum() > 500]
    if len(cols) < names:
        return {"na": f"{len(cols)} name(s) with > 500 return days; need {names}"}
    out = {"cc_ret": [], "bh_ret": [], "cc_dd": [], "bh_dd": []}
    joint, used = {}, 0
    for _ in range(n_paths):
        pick = rng.sample(cols, names)
        key = tuple(pick)
        if key not in joint:
            j = pd.concat([ret_cc[pick].add_prefix("cc_"), ret_bh[pick].add_prefix("bh_")], axis=1).dropna()
            joint[key] = (j.iloc[:, :names].values, j.iloc[:, names:].values)
        a, b = joint[key]
        if len(a) < block * 2:
            continue
        idx = []
        while len(idx) < horizon:
            s = rng.randrange(0, len(a) - block)
            idx += range(s, s + block)
        idx = idx[:horizon]
        used += 1
        for arm, src in (("cc", a), ("bh", b)):
            eq = np.cumprod(1 + src[idx].mean(axis=1))
            out[f"{arm}_ret"].append(eq[-1] - 1)
            out[f"{arm}_dd"].append(float((eq / np.maximum.accumulate(eq) - 1).min()))
    if not used:
        return {"na": f"no pair has {block * 2} joint return days"}
    res = {k: {p: float(np.percentile(v, p)) for p in (5, 25, 50, 75, 95)} for k, v in out.items()}
    res["paths_used"] = used
    return res


def bxm_vs_spy(root, start, end, facts=None):
    p = Path(root) / "BXM_History.csv"
    if not p.exists():
        return {"error": "BXM_History.csv: not supplied"}
    raw = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    hdr = next((i for i, l in enumerate(raw) if l.upper().startswith("DATE")), None)
    if hdr is None:
        return {"error": "BXM_History.csv: no DATE header line"}
    bx = pd.read_csv(p, skiprows=hdr)
    bx = pd.Series(bx.iloc[:, -1].astype(float).values,
                   index=pd.to_datetime(bx.iloc[:, 0], format="mixed").dt.date).sort_index()
    bx = bx[(bx.index >= start) & (bx.index <= end)]
    if bx.empty:
        return {"error": f"BXM_History.csv: no rows {start} to {end}"}
    try:
        spy = load_ticker(root, "SPY", facts)
    except (FileNotFoundError, ValueError, KeyError) as e:
        return {"error": f"SPY: {e}"}
    s = spy.close[(spy.close.index >= start) & (spy.close.index <= end)]
    # SPY total return: dividends reinvested on the ex-date close
    units, tr = 1.0, []
    for d, c in s.items():
        if d in spy.divs:
            units *= 1 + spy.divs[d] / c
        tr.append(units * c)
    spy_tr = pd.Series(tr, index=s.index)
    return {"start": str(bx.index[0]), "end": str(bx.index[-1]),
            "bxm_cagr": cagr(bx / bx.iloc[0]), "bxm_maxdd": max_dd(bx),
            "spy_tr_cagr": cagr(spy_tr / spy_tr.iloc[0]), "spy_tr_maxdd": max_dd(spy_tr)}


# ---------------------------------------------------------------- driver

def run(root, out, tickers, cfg, grid=GRID, mc_paths=10000, start=None, min_years=3.0, facts=None):
    """cfg: the bot config (config.load_config); its fees, r, target delta, tolerance and slack
    are used. Only data errors (FileNotFoundError, ValueError, KeyError) skip a ticker."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    facts = _load_facts() if facts is None else facts
    bot = bot_rule(cfg)
    data, skipped = {}, {}
    for tk in tickers:
        try:
            td = load_ticker(root, tk, facts)
            eligible(td, start, min_years)
            data[tk] = td
        except (FileNotFoundError, ValueError, KeyError) as e:
            skipped[tk] = str(e)
    spy = data.pop("SPY", None) if len(data) > 1 else None
    # 1) pre-registered bot rule with three fill assumptions
    fixed, counts = [], {}
    for tk, td in data.items():
        for fill in ("bid", "quarter", "mid"):
            rule = Config(bot.delta, bot.dte, bot.skip_earnings, bot.manage, fill)
            df, tr = simulate(td, rule, cfg, start=start)
            s = summarize(td, rule, df, tr, cfg)
            fixed.append(s)
            if fill == "bid":
                pd.DataFrame([asdict(t) | {"pnl": t.pnl} for t in tr]).to_csv(out / f"trades_{tk}.csv", index=False)
                counts[tk] = {k: s[k] for k in (*df.attrs["counts"], "calls_sold", "quote_rows_dropped",
                                                "earnings_gaps_gt120", "lot_cost_first", "lot_cost_last",
                                                "fits_3k", "atm_na_reason", "warnings")}
    if spy is not None:   # SPY with the same rule: our own check against BXM (not in the pooled tests)
        for fill in ("bid", "quarter", "mid"):
            rule = Config(bot.delta, bot.dte, bot.skip_earnings, bot.manage, fill)
            df, tr = simulate(spy, rule, cfg, start=start)
            fixed.append(summarize(spy, rule, df, tr, cfg))
    pd.DataFrame(fixed).to_csv(out / "bot_rule_by_ticker.csv", index=False)
    # 2) full grid (bid fills) -> walk-forward
    curves, grid_rows = {}, []
    for rule in grid:
        curves[rule.name] = {}
        for tk, td in data.items():
            df, tr = simulate(td, rule, cfg, start=start)
            curves[rule.name][tk] = df
            s = summarize(td, rule, df, tr, cfg)
            grid_rows.append({k: s[k] for k in ("ticker", "config", "cc_cagr", "bh_cagr", "excess_cagr",
                                                 "cc_maxdd", "bh_maxdd", "called_away_pct", "calls_sold",
                                                 *df.attrs["counts"])})
    pd.DataFrame(grid_rows).to_csv(out / "grid_in_sample.csv", index=False)
    oos, bh, picks = walk_forward(curves, grid)
    wf = []
    for tk in oos.columns:
        a, b = (1 + oos[tk].dropna()).cumprod(), (1 + bh[tk].dropna()).cumprod()
        wf.append({"ticker": tk, "oos_start": str(a.index[0]), "oos_end": str(a.index[-1]),
                   "wf_cc_cagr": cagr(a), "bh_cagr": cagr(b), "excess_cagr": cagr(a) - cagr(b),
                   "wf_cc_maxdd": max_dd(a), "bh_maxdd": max_dd(b)})
    pd.DataFrame(wf).to_csv(out / "walkforward_by_ticker.csv", index=False)
    pd.DataFrame(picks).to_csv(out / "walkforward_picks.csv", index=False)
    # 3) Monte Carlo on the bot rule (bid fills), random 2-stock portfolios like the $5k account
    bc = curves.get(bot.name) or {tk: simulate(td, bot, cfg, start=start)[0] for tk, td in data.items()}
    rc = pd.DataFrame({tk: df.cc.pct_change() for tk, df in bc.items()})
    rb = pd.DataFrame({tk: df.bh.pct_change() for tk, df in bc.items()})
    mc = monte_carlo(rc, rb, n_paths=mc_paths)
    first = min(df.index[0] for df in bc.values())
    last = max(df.index[-1] for df in bc.values())
    bench = bxm_vs_spy(root, first, last, facts) if "SPY" in tickers else {"error": "SPY not requested"}
    summary = {"tickers": sorted(data), "skipped": skipped, "period": [str(first), str(last)],
               "monte_carlo_2_stocks_1yr": mc, "bxm_vs_spy": bench, "grid_size": len(grid),
               "counts_bot_rule_bid": counts, "fits_3k": sorted(tk for tk, c in counts.items() if c["fits_3k"]),
               "walkforward_picks": picks}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data/real")
    ap.add_argument("--out", default="reports/real")
    ap.add_argument("--tickers", default=None)
    ap.add_argument("--mc-paths", type=int, default=10000)
    ap.add_argument("--start", default="2020-01-01", help="DoltHub has one 2019 snapshot, then daily/MWF from 2020-01-06")
    a = ap.parse_args(argv)
    tks = a.tickers.split(",") if a.tickers else sorted(p.name.split(".")[0] for p in (Path(a.data) / "options").glob("*.csv.gz"))
    if "SPY" not in tks and (Path(a.data) / "prices" / "SPY.csv").exists():
        tks.append("SPY")
    s = run(a.data, a.out, tks, load_config(CONFIG_PATH), mc_paths=a.mc_paths, start=date.fromisoformat(a.start))
    print(json.dumps({k: s[k] for k in ("tickers", "skipped", "period", "bxm_vs_spy")}, indent=1, default=str))


if __name__ == "__main__":
    main()
