"""Daily scan: positions -> screen -> rules -> validated order -> broker (dry-run for Webull) -> logs -> report."""
import datetime as dt
import json
import math
from pathlib import Path

import pandas as pd

from . import expiries
from .broker.base import NoQuote, OptionOrder, chunk
from .data import SNAPSHOT_COLUMNS
from .report import daily_report, weekly_report
from .rules import Market, apply_fill, decide_entry, decide_exit, equity
from .screen import feasible_universe, pass_history, universe_banner
from .variants import BY_ID, REGISTRY

TRADE_COLUMNS = ["date", "variant", "ticker", "action", "reason", "contract", "qty", "limit", "tif", "fill",
                 "fees", "mid", "delta", "in_band", "in_window", "status", "dry_run", "detail"]


class BrokerMarket(Market):
    """Expiries from the business-day calendar; chains read through the Broker interface.
    Every quote read is appended to `log` (state/paper_snapshots.csv)."""

    def __init__(self, broker, ticker, asof, log):
        cal = broker.calendar(asof)
        super().__init__(expiries.third_fridays(cal), expiries.fridays(cal))
        self.broker, self.ticker, self.log, self._cache = broker, ticker, log, {}

    def chain(self, day, expiry, kind):
        if (expiry, kind) not in self._cache:
            lo, hi = day.close * 0.7, day.close * 1.3
            symbols = self.broker.list_option_contracts(self.ticker, expiry, expiry, lo, hi)
            quotes = [q for part in chunk(symbols, 20) for q in self.broker.get_option_snapshots(part)]
            for q in quotes:
                self.log.append(_snap_row(day, self.ticker, q, expiry))
            self._cache[(expiry, kind)] = sorted((q for q in quotes if q.kind == kind), key=lambda q: q.strike)
        return self._cache[(expiry, kind)]


def _snap_row(day, ticker, q=None, expiry=None):
    return {"ts": day.date, "underlying": ticker, "underlying_price": day.close,
            "symbol": q.symbol if q else None, "expiry": expiry, "strike": q.strike if q else None,
            "type": q.kind if q else None, "bid": q.bid if q else None, "ask": q.ask if q else None,
            "iv": q.iv if q else day.vol, "delta": q.delta if q else None, "oi": q.oi if q else None,
            "next_earnings": day.next_earnings, "ex_div_date": day.ex_div_date, "asset_type": day.asset_type}


def _row(date, variant, ticker, d=None, result=None, tif=None, contract=None, dry_run=True, **kw):
    row = dict.fromkeys(TRADE_COLUMNS)
    row.update(date=date.isoformat(), variant=variant, ticker=ticker, dry_run=dry_run, contract=contract, tif=tif)
    if d is not None:
        row.update(action=d.action, reason=d.reason, qty=d.qty, limit=d.limit, mid=d.mid, delta=d.delta,
                   in_band=d.in_band, in_window=d.in_window)
    if result is not None:
        row.update(status=result.status, fill=result.fill, fees=result.fees, detail=result.detail)
    row.update(kw)
    return row


def _append_csv(path, rows, columns):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=columns).to_csv(path, mode="a", header=not path.exists(), index=False)


def _send(broker, d, ticker, tif):
    side = "BUY_TO_CLOSE" if d.action == "BUY_TO_CLOSE" else "SELL_TO_OPEN"
    order = OptionOrder(ticker, d.expiry, d.strike, d.kind, side, d.qty, d.limit, tif)
    return order.symbol, broker.submit(order)


def _would_act(state, day, variant, cfg, market, allowed):
    """Decision a variant would make today, on a copy of the ledger (nothing is sent)."""
    if not allowed:
        return "NONE", "UNIVERSE_EMPTY"
    st = type(state).from_dict(state.to_dict())
    ex = decide_exit(st, day, variant, cfg, market)
    if ex.action == "BUY_TO_CLOSE":
        return ex.action, ex.reason
    d = decide_entry(st, day, variant, cfg, market)
    if d.action == "BUY_SHARES":
        apply_fill(st, "BUY_SHARES", d.limit, d.qty, day.date, cfg)
        d = decide_entry(st, day, variant, cfg, market)
    return d.action, d.reason


def _nan_to_none(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else x


def run_daily(date, broker, cfg, variant="V0", weekly=False, state_dir="state", reports_dir="reports"):
    state_dir, reports_dir = Path(state_dir), Path(reports_dir)
    trades_path = state_dir / "paper_trades.csv"
    scan_path = state_dir / "scans" / f"{date.isoformat()}.json"
    if trades_path.exists():
        done = pd.read_csv(trades_path, usecols=["date", "variant"])
        if ((done["date"] == date.isoformat()) & (done["variant"] == variant)).any() and scan_path.exists():
            scan = json.loads(scan_path.read_text())
            scan["skipped"] = True
            write_reports(scan, state_dir, reports_dir, cfg, weekly)
            return scan
    v = BY_ID[variant]
    dry = broker.dry_run
    calendar = broker.calendar(date)  # raises outside the holiday table before any state changes
    rows = [_row(date, variant, broker.get_positions().ticker, contract=e.get("contract"),
                 dry_run=dry, **{"action": e["action"], "reason": "OK", "status": e.get("status", "FILLED"),
                                 "fill": e.get("fill", e.get("price")), "fees": e.get("fees"),
                                 "qty": e.get("qty"), "detail": e.get("detail")})
            for e in broker.advance(date)]
    state = start = broker.get_positions()
    log, days, markets = [], {}, {}
    for t in cfg["universe"]:
        try:
            day = broker.get_underlying_quote(t)
        except NoQuote:
            continue
        days[t], markets[t] = day, BrokerMarket(broker, t, date, log)
        log.append(_snap_row(day, t))
        pick = markets[t].pick(date, "monthly", cfg["monthly_dte"], cfg["monthly_slack_days"])
        if pick:
            markets[t].chain(day, pick[0], "C")
    holding = bool(state.shares or state.option)
    if holding and state.ticker not in days:
        days[state.ticker] = broker.get_underlying_quote(state.ticker)  # NoQuote: no silent skip
        markets[state.ticker] = BrokerMarket(broker, state.ticker, date, log)
    capital = equity(state, days[state.ticker], cfg) if holding else state.cash
    snaps = pd.DataFrame(log, columns=SNAPSHOT_COLUMNS)
    passing, rejects = feasible_universe(cfg, snaps, capital, date, calendar, broker.quotes_have_oi)
    banner = universe_banner(passing, rejects)
    ticker = state.ticker if holding else (passing[0] if passing else None)
    allowed = ticker is not None and ticker in passing
    context, chosen_spread = None, None
    if ticker is None:
        rows.append(_row(date, variant, None, action="NONE", reason="UNIVERSE_EMPTY", status="NO_ORDER",
                         dry_run=dry, detail=banner))
    else:
        day, market = days[ticker], markets[ticker]
        ex = decide_exit(state, day, v, cfg, market)
        if ex.action == "BUY_TO_CLOSE":
            sym, res = _send(broker, ex, ticker, "GTC")
            rows.append(_row(date, variant, ticker, ex, res, "GTC", sym, dry))
            state = broker.get_positions()
        for _ in range(2):  # buy shares, then the call at the same close (buy-write)
            if not allowed:
                rows.append(_row(date, variant, ticker, action="NONE", reason="UNIVERSE_EMPTY", status="NO_ORDER",
                                 dry_run=dry, detail=f"{ticker} fails the screen: {rejects.get(ticker)}"))
                break
            d = decide_entry(state, day, v, cfg, market)
            if d.action == "NONE":
                rows.append(_row(date, variant, ticker, d, status="NO_ORDER", dry_run=dry))
                break
            if d.action == "BUY_SHARES":
                res = broker.buy_shares(ticker, d.qty, d.limit)
                rows.append(_row(date, variant, ticker, d, res, "DAY", ticker, dry))
                if res.status != "FILLED":
                    break
                state = broker.get_positions()
                continue
            sym, res = _send(broker, d, ticker, "DAY")
            rows.append(_row(date, variant, ticker, d, res, "DAY", sym, dry))
            q = next((q for q in market.chain(day, d.expiry, d.kind) if q.strike == d.strike), None)
            chosen_spread = q and round(q.ask - q.bid, 2)
            break
        context = {"ticker": ticker, "price": day.close, "vol_pct": _nan_to_none(day.vol_pct),
                   "spread": chosen_spread, "next_earnings": day.next_earnings and day.next_earnings.isoformat(),
                   "earnings_known": day.asset_type == "etf" or day.earnings_known,
                   "ex_div_date": day.ex_div_date and day.ex_div_date.isoformat()}
    state = broker.get_positions()
    would = {x.label: _would_act(start, days[ticker], x, cfg, markets[ticker], allowed) if ticker else
             ("NONE", "UNIVERSE_EMPTY") for x in REGISTRY}
    _append_csv(trades_path, rows, TRADE_COLUMNS)
    _append_csv(state_dir / "paper_snapshots.csv", log, SNAPSHOT_COLUMNS)
    final_eq = equity(state, days[state.ticker], cfg) if (state.shares or state.option) else state.cash
    prior = [json.loads(p.read_text()) for p in sorted((state_dir / "scans").glob("*.json")) if p.stem < date.isoformat()]
    history = {t: list(pass_history(prior + [{"passing": passing}], t)) for t in cfg["universe"]}
    scan = {"date": date.isoformat(), "variant": variant, "broker": broker.name, "skipped": False,
            "synthetic": broker.synthetic, "modelled": broker.modelled, "dry_run": dry, "banner": banner,
            "passing": passing, "rejects": rejects, "pass_history": history,
            "early_close": date.isoformat() in expiries.load_holidays()["early_closes"],
            "positions": state.to_dict(), "equity": final_eq,
            "decisions": [{k: _nan_to_none(r[k]) for k in ("action", "reason", "contract", "limit", "tif",
                                                           "delta", "in_band", "in_window", "status", "fill")}
                          for r in rows], "context": context, "would_act": would}
    scan_path.parent.mkdir(parents=True, exist_ok=True)
    scan_path.write_text(json.dumps(scan, indent=2, default=str))
    write_reports(scan, state_dir, reports_dir, cfg, weekly)
    return scan


def write_reports(scan, state_dir, reports_dir, cfg, weekly=False):
    """Daily report from the scan record; weekly report on Fridays (or when asked)."""
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    date = dt.date.fromisoformat(scan["date"])
    paths = [reports_dir / f"daily_{scan['date']}.md"]
    paths[0].write_text(daily_report(scan))
    if weekly or date.weekday() == 4:
        scans = [json.loads(p.read_text()) for p in sorted((Path(state_dir) / "scans").glob("*.json"))
                 if p.stem <= scan["date"]]
        trades = pd.read_csv(Path(state_dir) / "paper_trades.csv")
        start = (date - dt.timedelta(days=6)).isoformat()
        week = trades[(trades["date"] >= start) & (trades["date"] <= scan["date"])]
        paths.append(reports_dir / f"weekly_{scan['date']}.md")
        paths[1].write_text(weekly_report(scan["date"], week, scans, cfg))
    return paths


def regenerate(date, state_dir, reports_dir, cfg, weekly=False):
    """`report` command: rebuild the reports from state/ logs only."""
    path = Path(state_dir) / "scans" / f"{date.isoformat()}.json"
    if not path.exists():
        raise FileNotFoundError(f"no scan recorded for {date} in {path.parent}")
    return write_reports(json.loads(path.read_text()), state_dir, reports_dir, cfg, weekly)
