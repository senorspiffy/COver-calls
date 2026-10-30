"""Webull OpenAPI adapter: SANDBOX ONLY, dry-run by default, no production code path.

Uses only the official webull-openapi-python-sdk==3.0.4, imported lazily. Response field
names below come from Webull's docs, not from a run against the sandbox (UNVERIFIED);
the manual sandbox smoke test runs on the person's machine. Positions and cash come from
our own paper ledger, because sandbox options support is UNVERIFIED (03, A/R2 AGAINST3)."""
import datetime as dt
import importlib
import logging
import os
import time
import uuid
from pathlib import Path
from types import SimpleNamespace

from .. import expiries
from ..pricing import grid_range
from ..rules import Day, Quote
from .base import Broker, LiveTradingDisabled, NoQuote, OrderRejected, OrderResult, chunk, occ_symbol, parse_occ, validate
from .sim import SimBroker

SANDBOX_HOST = "api.sandbox.webull.com"
SANDBOX_STREAM_HOST = "data-api.sandbox.webull.com"
_DENY = ("api.webull.com", "data-api.webull.com", "events-api.webull.com")  # production: never allowed

_SDK_MODULES = {
    "ApiClient": "webull.core.client",
    "TradeClient": "webull.trade.trade_client",
    "DataClient": "webull.data.data_client",
    "ResolveEndpointRequest": "webull.core.endpoint.resolver_endpoint_request",
}
log = logging.getLogger("ccbot.webull")   # never given headers, keys or secrets
log.setLevel(logging.WARNING)


def load_sdk():
    try:
        return SimpleNamespace(**{name: getattr(importlib.import_module(mod), name)
                                  for name, mod in _SDK_MODULES.items()})
    except ImportError as exc:
        raise ImportError("Webull SDK not installed: pip install ccbot[webull] "
                          "(webull-openapi-python-sdk==3.0.4)") from exc


class TokenBucket:
    """At most `rate` requests per second (far under Webull's 300/60 s and 600/60 s)."""

    def __init__(self, rate=1.0, clock=time.monotonic, sleep=time.sleep):
        self.interval, self.clock, self.sleep, self.next_at = 1.0 / rate, clock, sleep, 0.0

    def take(self):
        now = self.clock()
        if now < self.next_at:
            self.sleep(self.next_at - now)
            now = self.next_at
        self.next_at = now + self.interval


def to_sdk_payload(order):
    """Order dict in the shape of the SDK's samples/order/order_option_client.py."""
    side = "SELL" if order.side == "SELL_TO_OPEN" else "BUY"
    return {
        "client_order_id": uuid.uuid4().hex, "combo_type": "NORMAL", "order_type": order.order_type,
        "quantity": str(order.qty), "limit_price": f"{order.limit:.2f}", "option_strategy": "SINGLE",
        "side": side, "time_in_force": order.tif, "entrust_type": "QTY",
        "legs": [{"side": side, "quantity": str(order.qty), "symbol": order.underlying,
                  "strike_price": f"{order.strike:g}", "option_expire_date": order.expiry.isoformat(),
                  "instrument_type": "OPTION", "option_type": "CALL" if order.kind == "C" else "PUT",
                  "market": "US"}],
    }


def _items(body):
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        return body.get("data") or body.get("list") or []
    return []


def _num(item, *keys):
    for k in keys:
        if item.get(k) not in (None, ""):
            return float(item[k])
    return None


class WebullSandboxBroker(Broker):
    name = "webull-sandbox"

    def __init__(self, cfg, dry_run=True, preview=False, live=False, env=None, sdk=None,
                 ledger_path="state/sim_ledger.json", token_dir="state/webull_token", limiter=None):
        env = os.environ if env is None else env
        if live:
            raise LiveTradingDisabled("Live trading is not built.")
        if env.get("WEBULL_ENV") != "sandbox":
            raise LiveTradingDisabled("WEBULL_ENV must be 'sandbox'; no other environment is supported.")
        missing = [n for n in ("WEBULL_APP_KEY", "WEBULL_APP_SECRET") if not env.get(n)]
        if missing:
            raise ValueError(f"missing environment variables: {', '.join(missing)}")
        self.cfg, self.dry_run, self.do_preview = cfg, dry_run, preview
        self.account_id = env.get("WEBULL_ACCOUNT_ID", "")
        self.sdk = sdk if sdk is not None else load_sdk()
        self.limiter = limiter or TokenBucket(1.0)
        api = self.sdk.ApiClient(env["WEBULL_APP_KEY"], env["WEBULL_APP_SECRET"], "us")
        api.set_logger(log)
        # The SDK adds stdout + webull_*_sdk.log handlers unless these flags are set.
        api._stream_logger_set = api._file_logger_set = True
        Path(token_dir).mkdir(parents=True, exist_ok=True)
        api.set_token_dir(str(token_dir))
        api.add_endpoint("us", SANDBOX_HOST)
        api.add_endpoint("us", SANDBOX_STREAM_HOST, "quotes-api")
        self.api = api
        self._assert_sandbox()  # before any client is built: building one makes a network call
        self.trade = self.sdk.TradeClient(api)
        self.data = self.sdk.DataClient(api)
        self.ledger = SimBroker(cfg, ledger_path=ledger_path)
        self.date = dt.date.today()

    def _assert_sandbox(self):
        for api_type, want in (("api", SANDBOX_HOST), ("quotes-api", SANDBOX_STREAM_HOST)):
            host = self.api._endpoint_resolver.resolve(self.sdk.ResolveEndpointRequest("us", api_type))
            if host != want or host in _DENY:
                raise LiveTradingDisabled(f"endpoint '{api_type}' resolves to {host!r}, not the sandbox")

    def advance(self, date):
        self._assert_sandbox()
        self.date = date
        return []   # dry-run: nothing fills, so the paper ledger has nothing to settle

    def _call(self, fn, *args, **kw):
        self._assert_sandbox()
        self.limiter.take()
        resp = fn(*args, **kw)
        if getattr(resp, "status_code", 200) != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        return resp.json() if hasattr(resp, "json") else resp

    def get_underlying_quote(self, ticker):
        items = _items(self._call(self.data.market_data.get_snapshot, ticker, "US_STOCK"))
        price = _num(items[0], "price", "close", "last_price") if items else None
        if price is None:
            raise NoQuote(f"no sandbox quote for {ticker}")
        return Day(self.date, price)  # earnings unknown → blocked (ccbot/missing.py)

    def list_option_contracts(self, underlying, exp_from, exp_to, strike_lo, strike_hi):
        # SDK docs: start_date = exact expiration date, end_date = expiration lower bound.
        dates = {"start_date": exp_from.isoformat()} if exp_from == exp_to else {"end_date": exp_from.isoformat()}
        try:
            symbols, key = [], None
            while True:
                body = self._call(self.data.instrument.list_option_contracts, category="US_OPTION",
                                  underlying_symbols=underlying, **dates,
                                  strike_price_gte=str(strike_lo), strike_price_lte=str(strike_hi),
                                  pagination_key=key)
                symbols += [i["symbol"] for i in _items(body) if "symbol" in i
                            and exp_from <= parse_occ(i["symbol"])[1] <= exp_to]
                key = body.get("pagination_key") if isinstance(body, dict) else None
                if not key:
                    return symbols
        except LiveTradingDisabled:
            raise
        except Exception as exc:  # endpoint unsupported on the sandbox (UNVERIFIED): build symbols
            log.warning("list_option_contracts failed (%s); building OCC symbols", type(exc).__name__)
            # window runs past the Friday, so a holiday Friday moves back to its Thursday
            exps = [e for e in expiries.fridays(expiries.scan_calendar(exp_from, days=(exp_to - exp_from).days + 7))
                    if exp_from <= e <= exp_to]
            return [occ_symbol(underlying, e, kind, k) for e in exps for kind in ("C", "P")
                    for k in grid_range(strike_lo, strike_hi)]

    def get_option_snapshots(self, symbols):
        out = []
        for part in chunk(symbols, 20):
            for i in _items(self._call(self.data.option_market_data.get_option_snapshot, ",".join(part), "US_OPTION")):
                bid, ask, delta = _num(i, "bid", "bid_price"), _num(i, "ask", "ask_price"), _num(i, "delta")
                if None in (bid, ask, delta) or "symbol" not in i:
                    continue  # incomplete quote: skipped, so the strike is never chosen
                _, _, kind, strike = parse_occ(i["symbol"])
                oi = _num(i, "open_interest", "oi")
                out.append(Quote(i["symbol"], strike, kind, bid, ask, (bid + ask) / 2, delta,
                                 int(oi) if oi is not None else None, _num(i, "imp_vol", "iv")))
        return out

    def get_positions(self):
        return self.ledger.get_positions()

    def get_cash(self):
        return self.ledger.get_cash()

    def preview(self, order):
        validate(order, self.get_positions(), self.get_cash())
        if not self.account_id:
            raise ValueError("WEBULL_ACCOUNT_ID is required to preview an order")
        return self._call(self.trade.order_v2.preview_option, self.account_id, [to_sdk_payload(order)])

    def submit(self, order):
        try:
            validate(order, self.get_positions(), self.get_cash())
        except OrderRejected as exc:
            return OrderResult("REJECTED", detail=exc.reason)
        payload = to_sdk_payload(order)
        if self.dry_run:
            detail = "validated only"
            if self.do_preview:
                try:
                    self.preview(order)
                    detail = "previewed on sandbox"
                except LiveTradingDisabled:
                    raise
                except Exception as exc:
                    detail = f"SANDBOX_REJECTED preview: {type(exc).__name__}"
            log.warning("DRY_RUN %s %s x%s @ %s", payload["side"], order.symbol, order.qty, order.limit)
            return OrderResult("DRY_RUN", detail=detail)
        if not self.account_id:
            return OrderResult("SANDBOX_REJECTED", detail="WEBULL_ACCOUNT_ID not set")
        try:
            self._call(self.trade.order_v2.place_option, self.account_id, [payload])
        except LiveTradingDisabled:
            raise
        except Exception as exc:
            log.warning("SANDBOX_REJECTED %s: %s", order.symbol, type(exc).__name__)
            return OrderResult("SANDBOX_REJECTED", detail=type(exc).__name__)
        return OrderResult("SUBMITTED", detail="sandbox order placed; paper ledger stays in SimBroker")

    def buy_shares(self, ticker, qty, limit):
        return OrderResult("DRY_RUN", detail="stock orders are not sent by this adapter")
