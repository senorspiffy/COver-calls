"""Real-quote covered-call test (item 061). Research only; nothing here trades.

Question: has selling calls on our candidate stocks beaten simply holding them (and has BXM
beaten SPY) after real bid/ask fills and costs, tested walk-forward with no lookahead?

Inputs (scripts/fetch_real_data.py writes them; DoltHub post-no-preference + Cboe):
  data/real/prices/T.csv      date, close (unadjusted)       data/real/dividends/T.csv  ex_date, amount
  data/real/splits/T.csv      ex_date, to_factor, for_factor data/real/earnings/T.csv   date
  data/real/options/T.csv.gz  date, expiration, strike, bid, ask, vol (IV), delta (calls only)
  data/real/volhist/T.csv     date, iv_current, hv_current   data/real/BXM_History.csv

Simulation (one ticker; both arms fully invested with fractional shares, see simulate()):
  * A call is only ever sold on a day that has a real quote for it (a snapshot day), at the bid
    ("bid" fills) or at bid + 25% of the spread ("quarter" fills). Buy-backs pay the ask (or
    ask - 25% of spread). Mid fills are reported only to show what the spread costs.
  * Expiry: close > strike -> shares called away at the strike and bought back at the close
    (+1 cent/share slippage), so both arms always hold the same shares; the gap is cash.
  * Day before an ex-dividend date: an in-the-money call whose remaining time value
    (Black-Scholes from the sold contract's IV, APPROXIMATE) is below the dividend is assumed
    exercised early, so the dividend is lost.
  * On days without a quote for the open contract its value is Black-Scholes from the last
    quoted IV of that contract (APPROXIMATE; affects the daily curve/drawdown, not cash P&L).
Nothing on day t uses data after day t: a config's choices use only that day's quotes,
and walk-forward picks each 6-month block's config from the 24 months before it.
"""
import argparse
import gzip
import itertools
import json
import math
import random
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from .pricing import bs_price

R = 0.03                    # flat rate for Black-Scholes fills between snapshots (approximate)
REG_FEE = 0.10 + 0.02       # per contract: regulatory/ORF-style fees + CAT (UNVERIFIED, from config)
COMMISSION = 0.0            # Webull lists $0 options commission (UNVERIFIED for every account type)
SEC_RATE = 2.06e-05         # on sale notional
STOCK_SLIP = 0.01           # $/share paid when re-buying shares after assignment


# ---------------------------------------------------------------- loading

def _read(path):
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(p, compression="gzip" if p.suffix == ".gz" else None)


def _col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    raise KeyError(f"none of {names} in {list(df.columns)}")


@dataclass
class TickerData:
    ticker: str
    close: pd.Series                 # date-indexed unadjusted close
    divs: dict                       # ex_date -> $ per share
    splits: dict                     # ex_date -> share multiplier (2.0 for 2-for-1)
    earnings: list                   # sorted dates
    chain: dict                      # date -> DataFrame(expiration, strike, bid, ask, iv, delta)
    volhist: pd.DataFrame            # date-indexed iv, hv (may be empty)
    warnings: list = field(default_factory=list)
    quotes: dict = field(default_factory=dict)   # (date, expiration, strike) -> (bid, ask, iv, delta)


def load_ticker(root, tk):
    root = Path(root)
    px = _read(root / "prices" / f"{tk}.csv")
    if px.empty:
        raise FileNotFoundError(f"no prices for {tk}")
    px["date"] = pd.to_datetime(px[_col(px, "date")]).dt.date
    close = px.set_index("date")[_col(px, "close")].astype(float).sort_index()
    close = close[~close.index.duplicated()]

    dv = _read(root / "dividends" / f"{tk}.csv")
    divs = {}
    if not dv.empty:
        for d, a in zip(pd.to_datetime(dv[_col(dv, "ex_date", "date")]).dt.date, dv[_col(dv, "amount", "dividend")]):
            if pd.notna(a) and float(a) > 0:
                divs[d] = divs.get(d, 0.0) + float(a)

    sp = _read(root / "splits" / f"{tk}.csv")
    splits = {}
    if not sp.empty:
        to = _col(sp, "to_factor", "numerator")
        fr = _col(sp, "for_factor", "denominator")
        for d, t, f in zip(pd.to_datetime(sp[_col(sp, "ex_date", "date")]).dt.date, sp[to], sp[fr]):
            if f and float(f) > 0 and float(t) / float(f) != 1:
                splits[d] = float(t) / float(f)

    er = _read(root / "earnings" / f"{tk}.csv")
    earnings = sorted(set(pd.to_datetime(er[_col(er, "date")]).dt.date)) if not er.empty else []

    oc = _read(root / "options" / f"{tk}.csv.gz")
    chain, quotes = {}, {}
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
        oc = oc[(oc.ask > 0) & (oc.bid >= 0) & (oc.ask >= oc.bid)]
        chain = {d: g.reset_index(drop=True) for d, g in oc.groupby("date")}
        quotes = {(d, e, round(k, 3)): (b, a, v, dl) for d, e, k, b, a, v, dl in
                  zip(oc.date, oc.expiration, oc.strike, oc.bid, oc.ask, oc.iv, oc.delta)}

    vh = _read(root / "volhist" / f"{tk}.csv")
    if not vh.empty:
        vh = pd.DataFrame({"date": pd.to_datetime(vh[_col(vh, "date")]).dt.date,
                           "iv": vh[_col(vh, "iv_current")].astype(float),
                           "hv": vh[_col(vh, "hv_current")].astype(float)}).set_index("date").sort_index()
    td = TickerData(tk, close, divs, splits, earnings, chain, vh, quotes=quotes)
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


# ---------------------------------------------------------------- simulation

@dataclass(frozen=True)
class Config:
    delta: float = 0.275             # target call delta (bot uses 0.25-0.30)
    dte: tuple = (30, 45)            # days to expiry window (bot monthly rule)
    skip_earnings: bool = True       # don't hold a call through an earnings date
    manage: str = "hold"             # hold | take50 (buy back at 50% profit) | roll (roll up/out when delta > 0.70)
    fill: str = "bid"                # bid | quarter | mid

    @property
    def name(self):
        e = "noE" if self.skip_earnings else "E"
        return f"d{self.delta:.3f}_dte{self.dte[0]}-{self.dte[1]}_{e}_{self.manage}_{self.fill}"


BOT_RULE = Config()
GRID = [Config(d, w, e, m, "bid") for d, w, e, m in itertools.product(
    (0.15, 0.20, 0.275, 0.35, 0.45), ((5, 9), (14, 24), (30, 45)), (True, False), ("hold", "take50", "roll"))]


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


def opt_fees(px, mult, sell):
    """Fees for options covering `mult` shares; fractional contracts at the per-contract rate."""
    c = mult / 100.0
    return (COMMISSION + REG_FEE) * c + (SEC_RATE * px * mult if sell else 0.0)


@dataclass
class Trade:
    open_date: date
    expiration: date
    strike: float
    premium: float           # per share, at the fill
    iv: float
    delta: float
    spot: float
    close_date: date = None
    close_cost: float = 0.0  # per share paid to close (buy-back or intrinsic at assignment)
    outcome: str = ""        # expired | assigned | early_assigned | bought_back | rolled
    rv_life: float = float("nan")   # realized vol from open to close (annualised)
    qty: float = 100.0       # shares covered

    @property
    def pnl(self):
        return self.premium - self.close_cost


def _pick(g, spot, today, cfg):
    lo, hi = cfg.dte
    dte = g.expiration.map(lambda e: (e - today).days)
    ok = g[(dte >= lo) & (dte <= hi) & (g.strike > spot) & (g.bid > 0.0)]
    if ok.empty:   # widen the window by a week each side, like the bot's slack
        ok = g[(dte >= max(1, lo - 7)) & (dte <= hi + 7) & (g.strike > spot) & (g.bid > 0.0)]
    if ok.empty:
        return None
    mid = (ok.bid + ok.ask) / 2
    ok = ok[(ok.ask - ok.bid) <= 0.5 * mid + 0.05]           # skip very wide quotes
    if ok.empty:
        return None
    exp = sorted(ok.expiration.unique(), key=lambda e: abs((e - today).days - (lo + hi) / 2))[0]
    ok = ok[ok.expiration == exp]
    i = (ok.delta - cfg.delta).abs().idxmin()
    r = ok.loc[i]
    if abs(r.delta - cfg.delta) > 0.12:
        return None
    return r


def _earnings_between(td, a, b):
    return any(a < e <= b for e in td.earnings)


def _realized_vol(close, a, b):
    s = close[(close.index >= a) & (close.index <= b)]
    if len(s) < 4:
        return float("nan")
    r = np.diff(np.log(s.values))
    return float(np.std(r, ddof=1) * math.sqrt(252))


def simulate(td, cfg, start=None, end=None):
    """Returns (daily DataFrame[cc, bh] starting at 1.0, trades list).

    Both arms stay fully invested with fractional shares, like the BXM index: dividends are
    reinvested at the ex-date close in both; in the covered-call arm the premium, buy-back costs
    and assignment proceeds are also turned back into shares at that day's close, and each call
    covers every share held when it is sold. Real accounts trade 100-share lots (see caveats)."""
    days = [d for d in td.close.index if (start is None or d >= start) and (end is None or d <= end)]
    snap_days = sorted(d for d in td.chain if start is None or d >= start)
    if not snap_days:
        raise ValueError(f"{td.ticker}: no option quotes")
    days = [d for d in days if d >= snap_days[0]]
    c0 = float(td.close[days[0]])
    sh_cc = sh_bh = 1.0 / c0          # $1 in each arm
    open_t = None
    last_iv = None
    trades, rows = [], []
    for i, d in enumerate(days):
        c = float(td.close[d])
        cash = 0.0                       # covered-call cash flows today, reinvested at the close
        if d in td.splits:               # OCC-style adjustment keeps the position whole
            f = td.splits[d]
            sh_cc *= f
            sh_bh *= f
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
        if open_t and g is not None and cfg.manage != "hold" and d < open_t.expiration:
            q = td.quotes.get((d, open_t.expiration, round(open_t.strike, 3)))
            if q is not None:
                q = Quote(*q)
                last_iv = q.iv
                ask = buy_px(q, cfg.fill)
                if (cfg.manage == "take50" and ask <= 0.5 * open_t.premium) or \
                   (cfg.manage == "roll" and q.delta > 0.70 and (open_t.expiration - d).days <= 21):
                    open_t.close_cost = ask
                    open_t.close_date = d
                    open_t.outcome = "bought_back" if cfg.manage == "take50" else "rolled"
                    open_t.rv_life = _realized_vol(td.close, open_t.open_date, d)
                    cash -= ask * open_t.qty + opt_fees(ask, open_t.qty, False)
                    trades.append(open_t)
                    open_t = None

        # early exercise the day before ex-dividend (approximate): we lose tomorrow's dividend
        if open_t and nxt in td.divs and c > open_t.strike and nxt <= open_t.expiration:
            T = max((open_t.expiration - d).days, 1) / 365
            tv = bs_price(c, open_t.strike, T, R, 0.0, last_iv or open_t.iv, "C") - (c - open_t.strike)
            if tv < td.divs[nxt]:
                open_t.close_cost = c - open_t.strike
                open_t.close_date = d
                open_t.outcome = "early_assigned"
                open_t.rv_life = _realized_vol(td.close, open_t.open_date, d)
                cash += (open_t.strike - c - STOCK_SLIP) * open_t.qty   # sold at K, re-bought at close
                cash -= td.divs[nxt] * open_t.qty                       # dividend we no longer get
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
            else:
                open_t.outcome = "expired"
            trades.append(open_t)
            open_t = None

        # open a new call on a quote day
        if open_t is None and g is not None and nxt is not None:
            r = _pick(g, c, d, cfg)
            if r is not None and not (cfg.skip_earnings and _earnings_between(td, d, r.expiration)):
                px = sell_px(r, cfg.fill)
                if px >= 0.03:
                    qty = sh_cc + cash / c
                    open_t = Trade(d, r.expiration, float(r.strike), float(px), float(r.iv), float(r.delta), c, qty=qty)
                    last_iv = float(r.iv)
                    cash += px * qty - opt_fees(px, qty, True)

        sh_cc += cash / c
        # mark to market
        liab = 0.0
        if open_t:
            q = td.quotes.get((d, open_t.expiration, round(open_t.strike, 3)))
            if q is not None:
                last_iv = float(q[2])
                liab = float((q[0] + q[1]) / 2)
            else:
                T = max((open_t.expiration - d).days, 0) / 365
                liab = bs_price(c, open_t.strike, T, R, 0.0, last_iv or open_t.iv, "C")
            liab *= open_t.qty
        rows.append((d, sh_cc * c - liab, sh_bh * c))
    df = pd.DataFrame(rows, columns=["date", "cc", "bh"]).set_index("date")
    return df, trades


# ---------------------------------------------------------------- metrics

def cagr(eq):
    n = (eq.index[-1] - eq.index[0]).days / 365.25
    return float(eq.iloc[-1] ** (1 / n) - 1) if n > 0 and eq.iloc[-1] > 0 else float("nan")


def max_dd(eq):
    return float((eq / eq.cummax() - 1).min())


def iv_vs_rv(td, trades):
    """Per sold call: the IV we sold at vs the vol that actually happened over its life."""
    t = [x for x in trades if not math.isnan(x.rv_life) and x.iv > 0]
    if not t:
        return {}
    gap = np.array([x.iv - x.rv_life for x in t])
    out = {"sold_iv": float(np.mean([x.iv for x in t])), "realized": float(np.mean([x.rv_life for x in t])),
           "iv_minus_rv": float(gap.mean()), "pct_iv_above_rv": float((gap > 0).mean())}
    if not td.volhist.empty:
        vh = td.volhist.dropna()
        fwd = []
        for d, iv in vh.iv.items():
            rv = _realized_vol(td.close, d, d + timedelta(days=30))
            if not math.isnan(rv) and d + timedelta(days=30) <= td.close.index[-1]:
                fwd.append(iv - rv)
        if fwd:
            out["atm_iv_minus_next30d_rv"] = float(np.mean(fwd))
            out["atm_pct_iv_above_rv"] = float(np.mean(np.array(fwd) > 0))
    return out


def summarize(td, cfg, df, trades):
    n = len(trades)
    called = sum(t.outcome in ("assigned", "early_assigned") for t in trades)
    years = (df.index[-1] - df.index[0]).days / 365.25
    return {
        "ticker": td.ticker, "config": cfg.name, "start": str(df.index[0]), "end": str(df.index[-1]),
        "years": round(years, 2), "cc_cagr": cagr(df.cc), "bh_cagr": cagr(df.bh),
        "excess_cagr": cagr(df.cc) - cagr(df.bh), "cc_maxdd": max_dd(df.cc), "bh_maxdd": max_dd(df.bh),
        "calls_sold": n, "called_away": called, "called_away_pct": called / n if n else float("nan"),
        "early_assigned": sum(t.outcome == "early_assigned" for t in trades),
        "premium_yield_per_yr": float(np.sum([t.premium / t.spot for t in trades]) / max(years, 1e-9)),
        "option_pnl_per_share": sum(t.pnl for t in trades),
        "option_win_rate": float(np.mean([t.pnl > 0 for t in trades])) if n else float("nan"),
        **iv_vs_rv(td, trades), "warnings": "; ".join(td.warnings),
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
    Returns (oos daily returns per ticker DataFrame, bh daily returns, picks list)."""
    any_cfg = next(iter(curves.values()))
    first = min(df.index[0] for df in any_cfg.values())
    last = max(df.index[-1] for df in any_cfg.values())
    picks, oos, bh = [], {}, {}
    for tr0, te0, te1 in six_month_blocks(first, last):
        def score(name):
            s = []
            for tk, df in curves[name].items():
                w = df[(df.index >= tr0) & (df.index < te0)]
                if len(w) > 200:
                    s.append(math.log(w.cc.iloc[-1] / w.cc.iloc[0]) - math.log(w.bh.iloc[-1] / w.bh.iloc[0]))
            return np.mean(s) if s else -np.inf
        best = max((c.name for c in configs), key=score)
        picks.append({"train_from": str(tr0), "test_from": str(te0), "test_to": str(te1), "picked": best,
                      "train_excess_logret": float(score(best))})
        for tk, df in curves[best].items():
            w = df[(df.index >= te0) & (df.index < te1)]
            oos.setdefault(tk, []).append(w.cc.pct_change().dropna())
            bh.setdefault(tk, []).append(w.bh.pct_change().dropna())
    oos = pd.DataFrame({k: pd.concat(v) for k, v in oos.items()})
    bh = pd.DataFrame({k: pd.concat(v) for k, v in bh.items()})
    return oos, bh, picks


def monte_carlo(ret_cc, ret_bh, n_paths=10000, names=2, horizon=252, block=21, seed=7):
    """Random 2-stock equal-weight portfolios, block-bootstrapped 1-year paths.
    Returns percentiles of 1-year return and max drawdown for both arms."""
    rng = random.Random(seed)
    cols = [c for c in ret_cc.columns if ret_cc[c].notna().sum() > 500]
    out = {"cc_ret": [], "bh_ret": [], "cc_dd": [], "bh_dd": []}
    for _ in range(n_paths):
        pick = rng.sample(cols, names)
        a = ret_cc[pick].dropna()
        b = ret_bh[pick].reindex(a.index).fillna(0)
        if len(a) < block * 2:
            continue
        idx = []
        while len(idx) < horizon:
            s = rng.randrange(0, len(a) - block)
            idx += range(s, s + block)
        idx = idx[:horizon]
        for arm, src in (("cc", a), ("bh", b)):
            eq = np.cumprod(1 + src.values[idx].mean(axis=1))
            out[f"{arm}_ret"].append(eq[-1] - 1)
            out[f"{arm}_dd"].append(float((eq / np.maximum.accumulate(eq) - 1).min()))
    return {k: {p: float(np.percentile(v, p)) for p in (5, 25, 50, 75, 95)} for k, v in out.items()}


def bxm_vs_spy(root, start, end):
    p = Path(root) / "BXM_History.csv"
    if not p.exists():
        return {"error": "BXM_History.csv missing"}
    raw = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    hdr = next(i for i, l in enumerate(raw) if l.upper().startswith("DATE"))
    bx = pd.read_csv(Path(root) / "BXM_History.csv", skiprows=hdr)
    bx = pd.Series(bx.iloc[:, -1].astype(float).values,
                   index=pd.to_datetime(bx.iloc[:, 0], format="mixed").dt.date).sort_index()
    bx = bx[(bx.index >= start) & (bx.index <= end)]
    spy = load_ticker(root, "SPY")
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

def run(root, out, tickers, grid=GRID, mc_paths=10000, start=None, min_years=3.0):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    data, skipped = {}, {}
    for tk in tickers:
        try:
            data[tk] = load_ticker(root, tk)
            ch = [d for d in data[tk].chain if start is None or d >= start]
            if not ch:
                raise ValueError("no option quotes")
            if (max(ch) - min(ch)).days / 365.25 < min_years:
                raise ValueError(f"option quotes only {min(ch)} to {max(ch)} (< {min_years} years)")
        except Exception as e:
            data.pop(tk, None)
            skipped[tk] = str(e)
    spy = data.pop("SPY", None) if len(data) > 1 else None
    # 1) pre-registered bot rule with three fill assumptions
    fixed = []
    for tk, td in data.items():
        for fill in ("bid", "quarter", "mid"):
            cfg = Config(fill=fill)
            df, tr = simulate(td, cfg, start=start)
            fixed.append(summarize(td, cfg, df, tr))
            if fill == "bid":
                pd.DataFrame([asdict(t) | {"pnl": t.pnl} for t in tr]).to_csv(out / f"trades_{tk}.csv", index=False)
    if spy is not None:   # SPY with the same rule: our own check against BXM (not in the pooled tests)
        for fill in ("bid", "quarter", "mid"):
            cfg = Config(fill=fill)
            df, tr = simulate(spy, cfg, start=start)
            fixed.append(summarize(spy, cfg, df, tr))
    pd.DataFrame(fixed).to_csv(out / "bot_rule_by_ticker.csv", index=False)
    # 2) full grid (bid fills) -> walk-forward
    curves, grid_rows = {}, []
    for cfg in grid:
        curves[cfg.name] = {}
        for tk, td in data.items():
            df, tr = simulate(td, cfg, start=start)
            curves[cfg.name][tk] = df
            s = summarize(td, cfg, df, tr)
            grid_rows.append({k: s[k] for k in ("ticker", "config", "cc_cagr", "bh_cagr", "excess_cagr",
                                                 "cc_maxdd", "bh_maxdd", "called_away_pct", "calls_sold")})
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
    bot = curves.get(BOT_RULE.name) or {tk: simulate(td, BOT_RULE, start=start)[0] for tk, td in data.items()}
    rc = pd.DataFrame({tk: df.cc.pct_change() for tk, df in bot.items()})
    rb = pd.DataFrame({tk: df.bh.pct_change() for tk, df in bot.items()})
    mc = monte_carlo(rc, rb, n_paths=mc_paths)
    first = min(df.index[0] for df in bot.values())
    last = max(df.index[-1] for df in bot.values())
    bench = bxm_vs_spy(root, first, last) if "SPY" in tickers else {}
    summary = {"tickers": sorted(data), "skipped": skipped, "period": [str(first), str(last)],
               "monte_carlo_2_stocks_1yr": mc, "bxm_vs_spy": bench, "grid_size": len(grid),
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
    s = run(a.data, a.out, tks, mc_paths=a.mc_paths, start=date.fromisoformat(a.start))
    print(json.dumps({k: s[k] for k in ("tickers", "skipped", "period", "bxm_vs_spy")}, indent=1, default=str))


if __name__ == "__main__":
    main()
